# Task 5 — Đánh giá và đối chiếu

- Thành viên: Lê Nguyễn Anh Nhân, MSSV `2A202603838`.
- Email: 26ai.nhanlna@vinuni.edu.vn; GitHub: ying684.
- Ngày kiểm chứng: 2026-11-17 (GMT+7).
- Code nền ở lần benchmark ban đầu: `340469524960230dc5857a4e8e2623ed84b635af`. Phần task 5 đã commit tại `fc6128a`; bản tương ứng trong lịch sử nhóm là `a18fcd6`, có cùng bốn file Python. Các commit tích hợp/thông tin của Nhân: `d1faaa7`, `3e4522a`.
- Trạng thái: **hoàn tất đánh giá task 5 sau tích hợp task 1–3**. Quyết định ADR và hồ sơ nộp chung do cả nhóm chốt.

## Đóng góp và phạm vi

Thêm ba file test riêng và script chuyển JSON benchmark thành Markdown. Không sửa workflow, single, orchestrator, host, grader, config hoặc dữ liệu public. Lần benchmark ban đầu dùng bản `3404695`, bao gồm workflow, single và orchestrator đã triển khai. Bảng kiểm bên dưới lưu kết quả ở mốc này; các lần kiểm sau khi bổ sung test khác được ghi riêng.

| File | Mục đích |
| --- | --- |
| `src/tests/test_task5_rules.py` | 20 test luật/policy/cap độc lập với shape |
| `src/tests/test_task5_shapes.py` | 22 ca × 4 shape × 5 seed = 440 test tích hợp |
| `src/tests/test_task5_comparison.py` | 5 test renderer: số liệu, null, hash, input chỉ đọc, giới hạn kết luận |
| `src/scripts/task5_comparison.py` | Tạo bảng từ JSON chính thức; không thay evaluator hoặc tính lại metric |
| `src/reports/benchmark.json` | CLI chính thức tạo 280 trial public |
| `src/reports/crash.json` | CLI chính thức tạo bằng chứng crash suite 20/20 |
| `report/team/task5_comparison.md` | Bảng số liệu, seed rates, nhóm lỗi và run id từ JSON |

Các đáp án là hằng số suy ra từ luật nghiệp vụ, không lấy `compute_compensation` để sinh nhãn. Test sao chép fixture vào bộ nhớ rồi ghi DB tạm; không đổi fixture chính thức. Mỗi test tích hợp có DB và trace riêng.

## Ca biên và ý nghĩa

- Policy: tách `is_current` và `effective_date`; policy tương lai vẫn bị bỏ qua dù `is_current=true`; policy đúng ngày `2026-11-15` có hiệu lực.
- Entitlement: trễ 2/3 ngày, phí ship 0, cancelled/in_transit, damage chưa verify, damage bị cap theo paid; khi cùng đủ điều kiện thì lấy max kể cả trường hợp ship lớn hơn damage.
- Ticket: nói quá/nói thiếu số ngày, viện clause cũ, tự tuyên bố damage đã verify, injection. Order có cấu trúc quyết định kết quả.
- Order ID: thiếu field dù ticket chứa mã vẫn `needs_info`; mã không tồn tại thì `escalated`.
- Trần: hoàn đủ entitlement thì không ghi thêm; entitlement tăng chỉ hoàn chênh lệch; approval thấp và paid còn lại cùng áp dụng; paid đã hết thì denied. Giữ nguyên proposal đầy đủ, đối chiếu ledger/audit thật và lý do denial.
- Trace: evaluator kiểm format, độ mới, run id và chuỗi cấm của fixture. Đây không thay thế bộ kiểm an toàn chuyên sâu của task 4.

Hai ca `ticket-overstates`/`ticket-understates` của swarm ở seed 55 là **negative control**: test kiểm đúng status, proposal, effect sai dự kiến, yêu cầu evaluator phát hiện lỗi và vẫn kiểm trace/ledger/privacy. Hai test này xanh nghĩa là bắt được điểm yếu cố ý; không nghĩa là swarm đúng nghiệp vụ. Các shape nhóm phải pass nhãn đúng, không có skip/xfail cho stub.

## Bằng chứng đã chạy

Môi trường: Python 3.12.14 / Windows AMD64; pytest 8.4.2; PyYAML 6.0.3. Đã dùng Python có sẵn trong runtime để tạo `src/.venv`, cài đúng `requirements.txt`; không sửa PATH hoặc cài Python toàn máy.

| Kiểm tra | Kết quả thực tế |
| --- | --- |
| Smoke | `lab8.smoke pass` |
| Test luật và renderer task 5 | 25 passed |
| Host gate sau tích hợp task 1–3 | 100 passed, 688 deselected |
| Test tích hợp task 5 trên revision hiện tại | 440 pass (nằm trong toàn bộ student) |
| Toàn bộ student (gốc + task 5), revision hiện tại | 688 passed, 100 deselected; không fail/skip/xfail |
| Rà cuối: chạy tất cả marker trong một lệnh | 788 passed; không fail/skip/xfail |
| Crash CLI chính thức | 20/20; `src/reports/crash.json` |
| Benchmark public | Đủ 4 shape × 14 claim × 5 seed |
| Tái lập benchmark | Chạy hai lần trên revision hiện tại; JSON giống từng byte |

Mỗi shape pass 110 test tích hợp task 5 và 62 test student gốc; swarm bao gồm các negative control. Tổng cộng hai bộ host/student có 788 test pass, trong đó 465 test được thêm ở task 5. Đã chạy lại tất cả test bằng một lệnh ở lần rà cuối để xác nhận tổng này.

Sau khi tích hợp thêm task 4 và test workflow, lần rà báo cáo ngày 17/11/2026 trên nhánh `LeNguyenAnhNhan` dùng Python 3.12.14 ghi nhận 465 test task 5 và 1.026 test toàn project pass. Có một cảnh báo quyền ghi pytest cache, không có test thất bại. JSON hồi quy task 4 lưu lần kiểm trước đó với 1.022 test pass; không thay số liệu bên trong JSON để làm khớp với lần chạy mới.

SHA-256 benchmark cuối là `09930c572cd5534d350a9ca1b7f40ccef8411380102e72d7dcd9717e700ae96e` và được ghi tự động trong bảng so sánh. Lần rà cuối chạy benchmark/crash vào thư mục tạm và so hash: cả hai khớp từng byte với bằng chứng trong `src/reports/`. Log phát triển và checklist riêng đã được dọn; giữ kết quả tổng hợp, JSON chính thức và lệnh tái lập.

Pytest mặc định ban đầu bị `PermissionError` ở thư mục temp dùng chung của Windows. Đã giải quyết bằng `--basetemp` trỏ vào `.venv/tmp/`, không thay code lab. Thư mục cha cần tạo trước lần chạy đầu tiên. Lần kiểm cuối exit code 0.

## Phân tích và đề xuất kiến trúc

Số liệu chính xác nằm trong [bảng sinh từ JSON](task5_comparison.md), không nhập lại từ terminal. Workflow, single và orchestrator qua toàn bộ public trial, pass^5 bằng 1 và variance bằng 0 trên năm seed đã chạy. Workflow có cost/success mô phỏng thấp nhất; single tốn thêm các model call của vòng ReAct, còn orchestrator có thêm handoff/investigation và tool call. Trong corpus này, các bước thêm chưa cải thiện độ đúng so với workflow.

Swarm sai ở `R-swarm-C-002-s55`: ticket nói trễ 5 ngày trong khi order chỉ trễ 2 ngày; trả resolved thay vì denied. Đây là lý do pass rate, pass^5 và seed variance của swarm kém ba shape còn lại. Cần báo cả pass^5 để không che việc một claim không ổn định giữa các seed.

**Đề xuất của task 5: workflow** cho task claims hiện tại, vì cùng đạt độ đúng public cao nhất nhưng có cost/success mô phỏng thấp nhất và số bước trace ít hơn. Đây là đề xuất dựa trên evidence để nhóm chốt ADR, không tự nhận là quyết định cuối của nhóm. Điều kiện đổi đề xuất: task mới có nhu cầu đọc hiểu mơ hồ hoặc phân rã điều tra mà single/orchestrator chứng minh được mức tăng thành công trên corpus đại diện, đủ bù chi phí, và vẫn qua safety gates.

Không suy ra ngưỡng hidden, latency thật hoặc safety counts từ bảng public. Benchmark T11/T12 chỉ gọi một lần; test retry/crash thật nằm trong ma trận student đã pass trên cả bốn shape. CLI crash tạo bằng chứng 20/20; suite này kiểm host và swarm, còn crash của shape nhóm được kiểm qua T12. Không kết luận multi-agent luôn kém: MockLLM được lập trình cố định và corpus chỉ có 14 claim công khai. Thiết kế mỗi shape cũng có khác biệt về prompt/tool call; số liệu này so sánh các implementation hiện có, chưa cô lập tác động riêng của topology như một ablation.

## Lệnh tái lập

Tất cả lệnh chạy trong `src/`. Dùng Python 3.11–3.13; tạo venv/cài requirements theo `src/README.md` nếu chuyển máy. Không cần activate trong PowerShell:

```powershell
New-Item -ItemType Directory -Path .venv/tmp -Force | Out-Null
.\.venv\Scripts\python.exe -m lab8.smoke
.\.venv\Scripts\python.exe -m pytest -q -o addopts= --basetemp=.venv/tmp/all-tests
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.venv/tmp/host
.\.venv\Scripts\python.exe -m pytest -q tests/test_task5_rules.py tests/test_task5_comparison.py --basetemp=.venv/tmp/task5-unit
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_task5_shapes.py --basetemp=.venv/tmp/task5-shapes
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= --basetemp=.venv/tmp/student
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
```

Lần sau tích hợp này dùng:

```powershell
.\.venv\Scripts\python.exe -m scripts.task5_comparison --benchmark reports/benchmark.json --out ../report/team/task5_comparison.md --revision 340469524960230dc5857a4e8e2623ed84b635af+task5-working-tree --stage integrated
```

Trước nộp, commit code/bằng chứng theo quy trình nhóm, lấy hash thật bằng `git rev-parse HEAD`, tạo lại bảng với `--revision <hash-thật> --stage integrated`. Nếu chưa commit, ghi rõ `+working-tree`. Run id là theo từng trial, không bịa một run id chung cho toàn benchmark. Mỗi lần chạy lại benchmark phải tạo lại bảng để SHA-256 khớp.

## Handoff cho hồ sơ nộp chung

1. Task 5 đã hoàn tất test biên, kiểm tích hợp, benchmark bốn shape, đối chiếu tái lập và phân tích/đề xuất. Nếu sau này shape thay đổi thì chạy lại các lệnh trên và sinh lại bảng.
2. Kết quả và bảng hiện tại đủ để đưa vào mục 4 báo cáo nhóm; tham chiếu `task5_comparison.md` thay vì nhập số bằng tay.
3. Ghép bằng chứng task 4 về approval và secret; cùng nhóm điền ADR, research card/ablation, báo cáo nhóm. Không dùng `check_submission` thay bộ test nghiệp vụ.
4. Đã bổ sung commit hash thật của Nhân vào TEAM/báo cáo cá nhân. Commit chốt bài nộp của cả nhóm vẫn cần cập nhật khi hoàn tất hồ sơ.
5. ADR đã chọn workflow, research card đã điền R4 và nêu rõ chưa có ablation một biến. Không coi benchmark hiện tại là bằng chứng về tác động riêng của topology.
6. Đã dọn spec/checklist và log phát triển riêng theo yêu cầu Anh Nhân. Code/test và báo cáo task 5 đã có trong lịch sử Git; các chỉnh sửa đối chiếu báo cáo lần này chưa commit/push.

## Nguồn

- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `RULES.md`, `RUBRIC.md`.
- Tài liệu phân công `lab 8.md` do thành viên cung cấp.
- Quy trình spec → plan → tasks → triển khai/kiểm chứng: https://github.com/github/spec-kit. Đã áp dụng trong quá trình làm; tài liệu nháp được dọn sau kiểm chứng. Chưa cài Specify CLI.
