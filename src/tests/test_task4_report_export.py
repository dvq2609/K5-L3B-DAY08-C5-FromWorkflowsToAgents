"""The evidence exporter must not turn failures/errors/skips into passed tests."""

import json

import pytest

from scripts.task4_report import parse_junit


@pytest.mark.parametrize("tag,status", [(None, "passed"), ("failure", "failed"), ("error", "error"), ("skipped", "skipped")])
def test_junit_outcomes_and_private_details(tmp_path, tag, status):
    attrs = {"tests": 1, "failures": int(tag == "failure"), "errors": int(tag == "error"), "skipped": int(tag == "skipped")}
    attributes = " ".join(f'{key}="{value}"' for key, value in attrs.items())
    detail = f'<{tag} message="CANARY_SECRET_REPORT">sensitive traceback</{tag}>' if tag else ""
    path = tmp_path / "results.xml"
    path.write_text(
        f'<testsuites><testsuite {attributes}><testcase classname="tests.sample" name="check" time="0.25">'
        f'{detail}<system-out>CANARY_SECRET_REPORT console</system-out></testcase></testsuite></testsuites>',
        encoding="utf-8",
    )
    report = parse_junit(path)
    assert report["summary"]["total"] == 1
    assert report["summary"][status] == 1
    assert report["tests"][0]["status"] == status
    assert report["tests"][0]["duration_seconds"] == 0.25
    assert report["by_module"]["tests.sample"][status] == 1
    assert "CANARY_SECRET_REPORT" not in json.dumps(report)
    assert "sensitive traceback" not in json.dumps(report)


def test_junit_count_mismatch_fails_closed(tmp_path):
    path = tmp_path / "results.xml"
    path.write_text('<testsuites><testsuite tests="2"><testcase name="only-one"/></testsuite></testsuites>', encoding="utf-8")
    with pytest.raises(ValueError, match="counts disagree"):
        parse_junit(path)


def test_junit_missing_suite_is_not_success(tmp_path):
    path = tmp_path / "results.xml"
    path.write_text("<testsuites/>", encoding="utf-8")
    with pytest.raises(ValueError, match="missing testsuite"):
        parse_junit(path)
