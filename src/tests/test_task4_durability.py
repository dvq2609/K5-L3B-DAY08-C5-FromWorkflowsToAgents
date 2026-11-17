"""Task 4: real crash windows, cross-seed retries, atomicity, and concurrent calls."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from threading import Barrier
import time

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund, issue_refund
from lab8.schemas import make_run_id
from lab8.shapes import SHAPES
from tests.task4_helpers import (
    SAFETY_SEEDS, SHAPES_UNDER_TEST, assert_private, assert_trial,
    denial_reasons, expected_result, forbidden_for,
)


@pytest.fixture(autouse=True)
def isolated_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
@pytest.mark.parametrize("seed", SAFETY_SEEDS)
@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
@pytest.mark.parametrize("claim_id,proposal,effect", [
    ("C-001", 35000, 35000), ("C-008", 35000, 20000), ("C-014", 150000, 120000),
])
def test_task4_crash_resume_and_cross_seed_retries(public_db, capsys, shape, seed, point, claim_id, proposal, effect):
    with pytest.raises(InjectedCrash, match=f"^{point}$"):
        SHAPES[shape](claim_id, seed=seed, store_path=str(public_db), crash_at=point)
    # A pre-effect crash may precede the first trace write; scan anything that exists.
    run_id = make_run_id(shape, claim_id, seed)
    crash_payload = {"run_id": run_id, "trace_path": str(Path("traces") / f"{run_id}.json")}
    assert_private(crash_payload, capsys.readouterr(), forbidden_for(claim_id))
    with closing(connect(public_db)) as conn:
        stored = get_refund(conn, claim_id)
        assert (stored is not None) == (point != "before_effect")
        if stored:
            assert stored["amount_vnd"] == effect
        assert committed_audit_count(conn, claim_id) == int(point != "before_effect")
        checkpoint = conn.execute("SELECT result_json FROM checkpoints WHERE claim_id = ?", (claim_id,)).fetchone()
        assert (checkpoint is not None) == (point == "after_checkpoint")

    expected = expected_result("resolved", proposal, effect)
    for replay_seed in (seed, seed, 55 if seed == 11 else 11):
        started = time.time()
        result = SHAPES[shape](claim_id, seed=replay_seed, store_path=str(public_db))
        assert_trial(public_db, result, expected, started)
        assert_private(result.as_dict(), capsys.readouterr(), forbidden_for(claim_id))
    with closing(connect(public_db)) as conn:
        checkpoint = conn.execute("SELECT result_json FROM checkpoints WHERE claim_id = ?", (claim_id,)).fetchone()
        assert json.loads(checkpoint["result_json"])["amount_vnd"] == effect


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
@pytest.mark.parametrize("seed", SAFETY_SEEDS)
def test_task4_conflict_does_not_change_money_or_poison_replay(public_db, capsys, shape, seed):
    first = SHAPES[shape]("C-001", seed=seed, store_path=str(public_db))
    assert first.status == "resolved"
    with closing(connect(public_db)) as conn:
        conn.execute("UPDATE orders SET shipping_fee_vnd = 10000 WHERE order_id = 'O-107'")
        conn.commit()
    for _ in range(2):
        started = time.time()
        result = SHAPES[shape]("C-001", seed=seed, store_path=str(public_db))
        assert result.error_reason == "amount_conflict"
        assert result.refund_effects == first.refund_effects
        assert_trial(public_db, result, expected_result("failed", 10000, 35000), started)
        assert_private(result.as_dict(), capsys.readouterr(), forbidden_for("C-001"))
    with closing(connect(public_db)) as conn:
        conflicts = conn.execute(
            "SELECT details_json FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'amount_conflict'"
        ).fetchall()
        assert [json.loads(row["details_json"]) for row in conflicts] == [{"committed_vnd": 35000, "attempted_vnd": 10000}]
        conn.execute("UPDATE orders SET shipping_fee_vnd = 35000 WHERE order_id = 'O-107'")
        conn.commit()
    started = time.time()
    recovered = SHAPES[shape]("C-001", seed=seed, store_path=str(public_db))
    assert_trial(public_db, recovered, expected_result("resolved", 35000, 35000), started)
    assert_private(recovered.as_dict(), capsys.readouterr(), forbidden_for("C-001"))


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
@pytest.mark.parametrize("seed", SAFETY_SEEDS)
def test_task4_second_ticket_cannot_duplicate_payment(public_db, capsys, shape, seed):
    first = SHAPES[shape]("C-001", seed=seed, store_path=str(public_db))
    assert first.status == "resolved"
    assert [row["amount_vnd"] for row in first.refund_effects] == [35000]
    for _ in range(2):
        second = SHAPES[shape]("C-010", seed=seed, store_path=str(public_db))
        assert (second.status, second.proposal_amount, second.error_reason) == ("denied", 35000, "order_already_refunded")
        assert second.refund_effects == []
        assert second.committed_audit_count == 0
        assert_private(second.as_dict(), capsys.readouterr(), forbidden_for("C-010"))
    # This is a multi-claim sequence, not a fresh single-trial store for trial_pass.
    with closing(connect(public_db)) as conn:
        rows = conn.execute("SELECT claim_id, amount_vnd FROM refund_ledger WHERE order_id = 'O-107'").fetchall()
        assert [tuple(row) for row in rows] == [("C-001", 35000)]
        assert committed_audit_count(conn, "C-001") == 1
        assert denial_reasons(conn, "C-010") == ["order_already_refunded"]


def test_task4_audit_failure_rolls_back_effect_and_allows_recovery(public_db):
    with closing(connect(public_db)) as conn:
        conn.executescript("""
            CREATE TRIGGER task4_fail_audit BEFORE INSERT ON audit_events
            WHEN NEW.claim_id = 'C-001' AND NEW.event_type = 'refund_committed'
            BEGIN SELECT RAISE(ABORT, 'task4 injected audit failure'); END;
        """)
        with pytest.raises(sqlite3.IntegrityError, match="task4 injected audit failure"):
            issue_refund(conn, "C-001", 35000)
        assert get_refund(conn, "C-001") is None
        assert committed_audit_count(conn, "C-001") == 0
        assert conn.execute("SELECT COUNT(*) FROM checkpoints WHERE claim_id = 'C-001'").fetchone()[0] == 0
        conn.execute("DROP TRIGGER task4_fail_audit")
        conn.commit()
        assert issue_refund(conn, "C-001", 35000)["ok"] is True
        assert get_refund(conn, "C-001")["amount_vnd"] == 35000
        assert committed_audit_count(conn, "C-001") == 1


@pytest.mark.parametrize("claim_id,proposal,effect", [("C-001", 35000, 35000), ("C-014", 150000, 120000)])
def test_task4_concurrent_same_claim_has_one_effect(public_db, claim_id, proposal, effect):
    barrier = Barrier(2, timeout=5)

    def pay():
        # Independent SQLite connections, synchronized before the host call.
        with closing(connect(public_db)) as conn:
            barrier.wait()
            return issue_refund(conn, claim_id, proposal)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(pay) for _ in range(2)]
        outcomes = [future.result(timeout=15) for future in futures]
    assert all(row["ok"] and not row["conflict"] for row in outcomes)
    with closing(connect(public_db)) as conn:
        assert get_refund(conn, claim_id)["amount_vnd"] == effect
        assert committed_audit_count(conn, claim_id) == 1
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id = ?", (claim_id,)).fetchone()[0] == 1


def test_task4_concurrent_claims_share_one_order_cap(public_db):
    barrier = Barrier(2, timeout=5)

    def pay(claim_id):
        with closing(connect(public_db)) as conn:
            barrier.wait()
            return claim_id, issue_refund(conn, claim_id, 35000)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(pay, claim_id) for claim_id in ("C-001", "C-010")]
        outcomes = [future.result(timeout=15) for future in futures]
    winners = [claim_id for claim_id, outcome in outcomes if outcome["ok"]]
    losers = [claim_id for claim_id, outcome in outcomes if not outcome["ok"]]
    assert len(winners) == len(losers) == 1
    with closing(connect(public_db)) as conn:
        rows = conn.execute("SELECT claim_id, amount_vnd FROM refund_ledger WHERE order_id = 'O-107'").fetchall()
        assert [tuple(row) for row in rows] == [(winners[0], 35000)]
        assert committed_audit_count(conn, winners[0]) == 1
        assert committed_audit_count(conn, losers[0]) == 0
        assert denial_reasons(conn, losers[0]) == ["order_already_refunded"]
