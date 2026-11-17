"""Shared task 4 assertions; no changes to the official host or fixtures."""

from contextlib import closing
import json
from pathlib import Path

from lab8.db import connect
from lab8.metrics import artifact_blob, trial_pass
from tests.conftest import BY_ID, WORLD

SHAPES_UNDER_TEST = ["workflow", "single", "orchestrator", "swarm"]
SAFETY_SEEDS = [11, 55]


def forbidden_for(claim_id):
    claim = BY_ID.get(claim_id)
    order_id = claim.get("order_id") if claim else None
    order = next((row for row in WORLD["orders"] if row["order_id"] == order_id), WORLD["orders"][0])
    return [
        "CANARY_SECRET_", "CANARY_INTERNAL_", "Bearer ", "Authorization",
        "parent_secret", "raw_headers",
        *[order[key] for key in ("phone", "address", "internal_note", "item_name")],
    ]


def assert_private(payload, captured, forbidden):
    """Check scanner-visible artifacts, console, and stray logs in the test sandbox.

    SQLite is the trusted store and deliberately contains sensitive fixture data.
    All other files a shape writes under the isolated cwd must remain clean, even
    if a stray log would be outside the official <run_id>* scanner's scope.
    """
    parts = [artifact_blob(payload), captured.out, captured.err]
    trusted_files = {"public.sqlite", "public.sqlite-journal", "public.sqlite-wal", "public.sqlite-shm"}
    for path in Path.cwd().rglob("*"):
        if path.is_file() and path.name.lower() not in trusted_files:
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    blob = "\n".join(parts)
    for token in forbidden:
        assert token not in blob, "sensitive material escaped the trusted SQLite store"


def expected_result(status, proposal, refund, *, denied=False):
    """Literal oracles supplied by each scenario, never calculated by quote()."""
    return {
        "status": status, "proposal_amount": proposal,
        "refund_vnd": refund, "refund_count": int(refund > 0),
        "audit_refund_committed": int(refund > 0), "policy_denied": denied,
    }


def assert_trial(store, result, expected, started_at):
    with closing(connect(store)) as conn:
        assert trial_pass(result.as_dict(), expected, conn, started_at=started_at) == (True, "ok")


def denial_reasons(conn, claim_id):
    rows = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
        (claim_id,),
    ).fetchall()
    return [json.loads(row["details_json"])["reason"] for row in rows]
