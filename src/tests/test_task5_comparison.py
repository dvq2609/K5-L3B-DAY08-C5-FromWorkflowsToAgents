"""Reporting must preserve unavailable metrics and evidence without touching JSON."""

import hashlib
import json

import pytest

from lab8.metrics import summarize
from scripts.task5_comparison import main, render_comparison


def report_for(passed):
    trials = [{
        "shape": "workflow", "claim_id": "C-T5", "seed": 11, "passed": passed,
        "reason": "ok" if passed else "unlabeled" if passed is None else "proposal_mismatch",
        "cost_estimate": 12.0, "steps": 3, "model_calls": 1, "tool_calls": 1,
        "run_id": "R-workflow-C-T5-s11", "status": "resolved",
    }]
    return {
        "controlled_variables": {"model_backend": "MockLLM", "as_of": "2026-11-15",
                                 "claim_ids": ["C-T5"], "seeds": [11],
                                 "isolation": "fresh_sqlite_per_trial", "latency": "unavailable",
                                 "pricing": {"simulated": True, "currency": "VND"}},
        "by_shape": summarize(trials), "trials": trials,
    }


@pytest.mark.parametrize("passed", [True, False, None])
def test_markdown_preserves_metrics_evidence_and_input(tmp_path, passed):
    report = report_for(passed)
    source = tmp_path / "benchmark.json"
    source.write_text(json.dumps(report), encoding="utf-8")
    before = source.read_bytes()
    out = tmp_path / "comparison.md"
    assert main(["--benchmark", str(source), "--out", str(out), "--revision", "abc123+working-tree"]) == 0
    markdown = out.read_text(encoding="utf-8")
    assert source.read_bytes() == before
    assert hashlib.sha256(before).hexdigest() in markdown
    assert "abc123+working-tree" in markdown
    assert "Baseline trước tích hợp" in markdown
    if passed is True:
        assert "1 / 1 | 1.000000 | 1.000000" in markdown
        assert "12.0000" in markdown
    else:
        assert "R-workflow-C-T5-s11" in markdown
        assert ("unlabeled" if passed is None else "proposal_mismatch") in markdown
        assert ("— / 0 | — | —" if passed is None else "0 / 1 | 0.000000 | 0.000000") in markdown
        assert "12.0000" not in markdown  # a failed trial's cost is not cost per success


def test_input_cannot_be_overwritten(tmp_path):
    source = tmp_path / "benchmark.json"
    source.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        main(["--benchmark", str(source), "--out", str(source), "--revision", "abc123"])
    assert exc.value.code == 2
    assert source.read_text(encoding="utf-8") == "{}"


def test_integrated_stage_does_not_claim_hidden_or_safety_success():
    markdown = render_comparison(report_for(True), source="benchmark.json", digest="abc", revision="abc123", stage="integrated")
    assert "Baseline trước tích hợp" not in markdown
    assert "Đây là kết quả sau tích hợp code" in markdown
    assert "Sau tích hợp task 1–4, chạy lại" not in markdown
    assert "không chứng minh đạt hidden" in markdown
    assert "không cung cấp riêng secret leak / approval bypass counts" in markdown
