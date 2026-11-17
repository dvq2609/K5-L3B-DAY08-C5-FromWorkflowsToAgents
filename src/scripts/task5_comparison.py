"""Render official benchmark JSON as a reviewable Markdown table. Never edit JSON.

From src/: python -m scripts.task5_comparison --benchmark reports/benchmark.json
    --out ../report/team/task5_comparison.md --revision <hash> --stage baseline
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from lab8.console import utf8_stdio


def cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def number(value: float | None, places: int = 6) -> str:
    return "—" if value is None else f"{value:.{places}f}"


def render_comparison(report: dict[str, Any], *, source: str, digest: str, revision: str, stage: str) -> str:
    controlled = report["controlled_variables"]
    lines = [
        "# Task 5 — Bảng so sánh benchmark",
        "",
        "File sinh tự động bằng `scripts.task5_comparison`; không nhập số liệu bằng tay.",
        "",
        f"- Benchmark: `{cell(source)}`",
        f"- SHA-256 benchmark: `{digest}`",
        f"- Revision do người chạy cung cấp: `{cell(revision)}`",
        f"- Giai đoạn: `{stage}`",
        f"- Model: {cell(controlled['model_backend'])}; as_of: {cell(controlled['as_of'])}",
        f"- Corpus: {len(controlled['claim_ids'])} claim; seeds: {', '.join(map(str, controlled['seeds']))}",
        f"- Isolation: {cell(controlled['isolation'])}; latency: {cell(controlled['latency'])}",
        "- Giá kiểm soát: `" + cell(json.dumps(controlled["pricing"], sort_keys=True, ensure_ascii=False)) + "`",
        "",
    ]
    if stage == "baseline":
        lines += [
            "**Baseline trước tích hợp:** shape chưa triển khai có thể đạt 0%; chưa dùng bảng này để chốt ADR.",
            "",
        ]
    lines += [
        "| Shape | Pass / graded | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for shape, stats in report["by_shape"].items():
        successes = stats["successes"]
        count = "—" if successes is None else str(successes)
        lines.append(
            f"| {cell(shape)} | {count} / {stats['graded_trials']} | {number(stats['pass_rate'])} | "
            f"{number(stats['pass_5'])} | {number(stats['seed_min'])}–{number(stats['seed_max'])} | "
            f"{number(stats['seed_variance'])} | {number(stats['cost_per_success_vnd'], 4)} | "
            f"{number(stats['mean_steps'], 2)} / {number(stats['p95_steps'], 2)} |"
        )
    lines += [
        "",
        "`—` = không xác định/chưa có nhãn. Không có trial thành công thì cost/success không xác định; không được hiểu là miễn phí.",
        "",
        "## Tỷ lệ theo seed",
        "",
        "| Shape | Seed | Pass rate |",
        "| --- | ---: | ---: |",
    ]
    for shape, stats in report["by_shape"].items():
        for seed, rate in stats["seed_pass_rates"].items():
            lines.append(f"| {cell(shape)} | {cell(seed)} | {number(rate)} |")
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for trial in report["trials"]:
        if trial["passed"] is not True:
            groups[(trial["shape"], trial["reason"])].append(trial["run_id"])
    lines += [
        "",
        "## Trial không pass hoặc chưa được chấm",
        "",
        "| Shape | Lý do | Số trial | Run id dẫn chứng (tối đa 3 mỗi nhóm) |",
        "| --- | --- | ---: | --- |",
    ]
    for (shape, reason), run_ids in sorted(groups.items()):
        examples = ", ".join(f"`{cell(run_id)}`" for run_id in run_ids[:3])
        lines.append(f"| {cell(shape)} | {cell(reason)} | {len(run_ids)} | {examples} |")
    if not groups:
        lines.append("| — | Không có trong báo cáo này | 0 | — |")
    lines += [
        "",
        "## Giới hạn và bước tiếp theo",
        "",
        "- MockLLM và giá mô phỏng không đại diện model sản xuất hoặc hóa đơn API; latency unavailable.",
        "- Steps là số event trace; số event ít không chứng minh chạy nhanh hơn.",
        "- Pass^5 chỉ mang nghĩa qua cả 5 seed khi báo cáo thực sự dùng đủ năm seed khác nhau.",
        "- Public benchmark không chứng minh đạt hidden ≥ 0.75, không cung cấp riêng secret leak / approval bypass counts.",
        "- T11/T12 trong benchmark chỉ là single run; retry/crash thật phải xem ma trận student và bằng chứng task 4.",
        ("- Sau tích hợp task 1–4, chạy lại test/benchmark và tạo lại bảng với `--stage integrated`; cùng nhóm quyết định ADR."
         if stage == "baseline" else
         "- Đây là kết quả sau tích hợp code. Dùng cùng bằng chứng crash/safety và hidden (nếu có) để nhóm chốt ADR; không tự suy ra các gate chưa đo."),
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--revision", required=True, help="Revision of the evaluated code; mark uncommitted changes explicitly")
    parser.add_argument("--stage", choices=["baseline", "integrated"], default="baseline")
    args = parser.parse_args(argv)
    if args.benchmark.resolve() == args.out.resolve():
        parser.error("--out must differ from --benchmark; the input JSON is read-only")
    raw = args.benchmark.read_bytes()
    report = json.loads(raw)
    markdown = render_comparison(
        report, source=args.benchmark.as_posix(), digest=hashlib.sha256(raw).hexdigest(),
        revision=args.revision, stage=args.stage,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
