# Task 5 — Bảng so sánh benchmark

File sinh tự động bằng `scripts.task5_comparison`; không nhập số liệu bằng tay.

- Benchmark: `reports/benchmark.json`
- SHA-256 benchmark: `09930c572cd5534d350a9ca1b7f40ccef8411380102e72d7dcd9717e700ae96e`
- Revision do người chạy cung cấp: `340469524960230dc5857a4e8e2623ed84b635af+task5-working-tree`
- Giai đoạn: `integrated`
- Model: MockLLM; as_of: 2026-11-15
- Corpus: 14 claim; seeds: 11, 22, 33, 44, 55
- Isolation: fresh_sqlite_per_trial; latency: unavailable
- Giá kiểm soát: `{"currency": "VND", "input_per_1k_tokens_vnd": 20, "output_per_1k_tokens_vnd": 80, "simulated": true, "tool_call_vnd": 10}`

| Shape | Pass / graded | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| workflow | 70 / 70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.000000 | 27.8571 | 1.86 / 2.00 |
| single | 70 / 70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.000000 | 29.8629 | 4.64 / 5.00 |
| orchestrator | 70 / 70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.000000 | 57.1229 | 4.36 / 5.00 |
| swarm | 69 / 70 | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.000816 | 49.5670 | 2.80 / 3.00 |

`—` = không xác định/chưa có nhãn. Không có trial thành công thì cost/success không xác định; không được hiểu là miễn phí.

## Tỷ lệ theo seed

| Shape | Seed | Pass rate |
| --- | ---: | ---: |
| workflow | 11 | 1.000000 |
| workflow | 22 | 1.000000 |
| workflow | 33 | 1.000000 |
| workflow | 44 | 1.000000 |
| workflow | 55 | 1.000000 |
| single | 11 | 1.000000 |
| single | 22 | 1.000000 |
| single | 33 | 1.000000 |
| single | 44 | 1.000000 |
| single | 55 | 1.000000 |
| orchestrator | 11 | 1.000000 |
| orchestrator | 22 | 1.000000 |
| orchestrator | 33 | 1.000000 |
| orchestrator | 44 | 1.000000 |
| orchestrator | 55 | 1.000000 |
| swarm | 11 | 1.000000 |
| swarm | 22 | 1.000000 |
| swarm | 33 | 1.000000 |
| swarm | 44 | 1.000000 |
| swarm | 55 | 0.928571 |

## Trial không pass hoặc chưa được chấm

| Shape | Lý do | Số trial | Run id dẫn chứng (tối đa 3 mỗi nhóm) |
| --- | --- | ---: | --- |
| swarm | status resolved != denied | 1 | `R-swarm-C-002-s55` |

## Giới hạn và bước tiếp theo

- MockLLM và giá mô phỏng không đại diện model sản xuất hoặc hóa đơn API; latency unavailable.
- Steps là số event trace; số event ít không chứng minh chạy nhanh hơn.
- Pass^5 chỉ mang nghĩa qua cả 5 seed khi báo cáo thực sự dùng đủ năm seed khác nhau.
- Public benchmark không chứng minh đạt hidden ≥ 0.75, không cung cấp riêng secret leak / approval bypass counts.
- T11/T12 trong benchmark chỉ là single run; retry/crash thật phải xem ma trận student và bằng chứng task 4.
- Đây là kết quả sau tích hợp code. Dùng cùng bằng chứng crash/safety và hidden (nếu có) để nhóm chốt ADR; không tự suy ra các gate chưa đo.
