"""Task 5: hand-calculated boundary oracles, independent of student shapes."""

from contextlib import closing
from copy import deepcopy
import json

import pytest

from lab8.compensation import quote
from lab8.db import connect, init_store
from lab8.durability import issue_refund
from lab8.tools import compute_compensation, lookup_policy
from tests.conftest import CLAIMS, WORLD

AS_OF = "2026-11-15"


@pytest.mark.parametrize(
    "current,effective,expected",
    [
        (False, "2025-01-01", 0),
        (True, "2026-11-14", 35000),
        (True, "2026-11-15", 35000),
        (True, "2026-11-16", 0),
        (False, "2026-11-16", 0),
    ],
    ids=["superseded", "before-cutoff", "on-cutoff", "future-current", "future-inactive"],
)
def test_policy_current_and_effective_date_are_independent(tmp_path, current, effective, expected):
    world = deepcopy(WORLD)
    policy = deepcopy(world["policies"][0])
    policy.update(is_current=current, effective_date=effective)
    world["policies"] = [policy]
    order = deepcopy(world["orders"][0])
    order["delay_days"] = 3
    store = tmp_path / "policy.sqlite"
    init_store(store, world, CLAIMS).close()
    with closing(connect(store)) as conn:
        assert len(lookup_policy(conn)["policies"]) == (1 if expected else 0)
        assert compute_compensation(conn, order)["amount_vnd"] == expected
    # Also exercise quote's own guards without lookup_policy prefiltering input.
    assert quote(order, [policy], as_of=AS_OF).amount_vnd == expected


@pytest.mark.parametrize(
    "changes,expected",
    [
        ({"delay_days": 2}, 0),
        ({"delay_days": 3}, 35000),
        ({"shipping_fee_vnd": 0}, 0),
        ({"status": "cancelled", "damage_verified": True}, 0),
        ({"status": "in_transit", "damage_verified": True}, 0),
        ({"delay_days": 0, "damage_verified": False}, 0),
        ({"delay_days": 0, "damage_verified": True, "paid_vnd": 40000}, 40000),
        ({"damage_verified": True}, 150000),
        ({"damage_verified": True, "shipping_fee_vnd": 170000}, 170000),
    ],
    ids=["two-days", "three-days", "zero-ship", "cancelled", "in-transit",
         "unverified", "damage-paid-cap", "damage-wins", "ship-wins"],
)
def test_entitlement_boundaries_and_max_not_sum(changes, expected):
    order = deepcopy(WORLD["orders"][0])
    order.update(changes)
    for policies in (WORLD["policies"], list(reversed(WORLD["policies"]))):
        result = quote(order, policies, as_of=AS_OF)
        assert result.amount_vnd == expected
        assert "SHIP-LATE-OLD" not in result.clause_ids
        assert "SHIP-LATE-FUTURE" not in result.clause_ids


@pytest.mark.parametrize(
    "entitlement,prior,approved,paid,effect,reason",
    [
        (150000, 30000, 150000, 200000, 120000, "committed"),
        (150000, 30000, 50000, 200000, 50000, "committed"),
        (35000, 5000, 35000, 20000, 15000, "committed"),
        (35000, 35000, 35000, 250000, 0, "order_already_refunded"),
        (35000, 40000, 35000, 250000, 0, "order_already_refunded"),
        (35000, 20000, 35000, 20000, 0, "capped_to_zero"),
    ],
    ids=["top-up", "top-up-approval-cap", "remaining-paid-cap", "fully-paid-entitlement",
         "prior-above-entitlement", "paid-exhausted"],
)
def test_order_history_approval_and_paid_caps_interact(
    tmp_path, entitlement, prior, approved, paid, effect, reason
):
    world = deepcopy(WORLD)
    order = next(row for row in world["orders"] if row["order_id"] == "O-515")
    order["paid_vnd"] = paid
    next(row for row in world["approvals"] if row["approval_id"] == "A-014")["approved_vnd"] = approved
    next(row for row in world["prior_refunds"] if row["order_id"] == "O-515")["amount_vnd"] = prior
    store = tmp_path / "cap.sqlite"
    init_store(store, world, CLAIMS).close()
    with closing(connect(store)) as conn:
        outcome = issue_refund(conn, "C-014", entitlement)
        assert outcome["reason"] == reason
        rows = conn.execute("SELECT amount_vnd FROM refund_ledger WHERE claim_id = 'C-014'").fetchall()
        assert [row["amount_vnd"] for row in rows] == ([effect] if effect else [])
        total = conn.execute(
            "SELECT SUM(amount_vnd) FROM refund_ledger WHERE order_id = 'O-515'"
        ).fetchone()[0]
        assert total == prior + effect
        audits = conn.execute(
            "SELECT event_type, details_json FROM audit_events WHERE claim_id = 'C-014'"
        ).fetchall()
        assert len(audits) == 1
        assert audits[0]["event_type"] == ("refund_committed" if effect else "policy_denied")
        if not effect:
            assert json.loads(audits[0]["details_json"])["reason"] == reason
