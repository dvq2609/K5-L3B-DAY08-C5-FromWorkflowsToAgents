"""Run real pytest checks and export their built-in JUnit results to JSON.

python -m scripts.task4_report --scope task4 --out reports/task4_tests.json
python -m scripts.task4_report --scope all --out reports/task4_regression.json
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest

from lab8.config_loader import repo_path
from lab8.console import utf8_stdio

TASK4_TESTS = [
    "tests/test_task4_authorization.py",
    "tests/test_task4_durability.py",
    "tests/test_task4_privacy.py",
]
STATUSES = ("passed", "failed", "error", "skipped")


def parse_junit(path: Path) -> dict:
    """Keep outcomes/IDs/timing only. Never export traceback or captured secrets."""
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    if not suites:
        raise ValueError("missing testsuite")
    records = []
    declared = Counter()
    for suite in suites:
        for key in ("tests", "failures", "errors", "skipped"):
            declared[key] += int(suite.get(key, "0"))
        for case in suite.iter("testcase"):
            status = "passed"
            for tag, outcome in (("error", "error"), ("failure", "failed"), ("skipped", "skipped")):
                if case.find(tag) is not None:
                    status = outcome
                    break
            records.append({
                "class_name": case.get("classname", ""),
                "test_name": case.get("name", ""),
                "status": status,
                "duration_seconds": float(case.get("time", "0")),
            })
    counts = Counter(row["status"] for row in records)
    if (len(records) != declared["tests"] or counts["failed"] != declared["failures"]
            or counts["error"] != declared["errors"] or counts["skipped"] != declared["skipped"]):
        raise ValueError("JUnit counts disagree with test cases")
    by_module = defaultdict(Counter)
    for row in records:
        by_module[row["class_name"]][row["status"]] += 1
    return {
        "summary": {"total": len(records), **{key: counts[key] for key in STATUSES}},
        "by_module": {
            name: {"total": sum(stats.values()), **{key: stats[key] for key in STATUSES}}
            for name, stats in sorted(by_module.items())
        },
        "tests": records,
    }


def provenance(root: Path) -> dict:
    repo = root.parent
    git = ["git", "-c", f"safe.directory={repo.as_posix()}"]
    try:
        head = subprocess.run([*git, "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True)
        status = subprocess.run([*git, "status", "--porcelain"], cwd=repo, capture_output=True, text=True)
        revision = head.stdout.strip() if head.returncode == 0 else None
        dirty = bool(status.stdout.strip()) if status.returncode == 0 else None
    except OSError:
        revision, dirty = None, None
    paths = [*root.joinpath("lab8").rglob("*.py"), *root.joinpath("tests").glob("*.py"),
             *root.joinpath("config").glob("*.yaml"), *root.joinpath("data").glob("*.json"),
             *root.joinpath("data").glob("*.jsonl"), Path(__file__).resolve()]
    hashes = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(paths)}
    return {"base_revision": revision, "working_tree_dirty": dirty, "source_sha256": hashes}


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["task4", "host", "all"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    root = repo_path()
    out = args.out.resolve()
    if out.suffix.lower() != ".json":
        parser.error("--out must be a .json file")
    official = {root.joinpath("reports", name).resolve() for name in ("benchmark.json", "crash.json")}
    if out in official:
        parser.error("use the official benchmark/crash CLI to generate those files")
    started = datetime.now(timezone.utc)
    report = {
        "schema_version": "task4.pytest.v1", "scope": args.scope,
        "run_id": f"T4-{args.scope}-{started.strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}",
        "started_at_utc": started.isoformat(),
        "environment": {"python": platform.python_version(), "pytest": pytest.__version__,
                        "platform": platform.platform()},
        "provenance": provenance(root),
        "timing_note": "pytest wall time; not MockLLM or production latency",
        "privacy_note": "no tracebacks, captured console, raw claim/order data in this export",
    }
    temp_parent = root / ".venv" / "tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"task4-json-{args.scope}-", dir=temp_parent, ignore_cleanup_errors=True) as tmp:
        scratch = Path(tmp)
        command = [sys.executable, "-m", "pytest", "-q", "--tb=short", "-o", "xfail_strict=true",
                   f"--basetemp={scratch / 'work'}", f"--junitxml={scratch / 'results.xml'}"]
        if args.scope != "host":
            command += ["-o", "addopts="]
        if args.scope == "task4":
            command += TASK4_TESTS
        report["pytest_args"] = ["-q", "--tb=short", "-o", "xfail_strict=true"]
        if args.scope != "host":
            report["pytest_args"] += ["-o", "addopts="]
        if args.scope == "task4":
            report["pytest_args"] += TASK4_TESTS
        result = subprocess.run(command, cwd=root)
        report["pytest_exit_code"] = result.returncode
        try:
            report.update(parse_junit(scratch / "results.xml"))
            report["report_error"] = None
        except (OSError, ET.ParseError, ValueError):
            report.update(summary=None, by_module={}, tests=[], report_error="missing_or_invalid_junit")
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    stats = report["summary"]
    report["all_passed"] = bool(
        result.returncode == 0 and stats and stats["total"] > 0
        and stats["passed"] == stats["total"]
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}; all_passed={report['all_passed']}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
