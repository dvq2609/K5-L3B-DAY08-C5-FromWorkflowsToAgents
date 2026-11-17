# Báo cáo cá nhân — 2A202603755_LeNguyenAnhKhoi
## 1. Thông tin thành viên

- Họ tên: Lê Nguyễn Anh Khôi.
- MSSV: 2A202603755.
- Email: 26ai.khoilna@vinuni.edu.vn.
- GitHub: KN-16.
- Phần việc được phân công: task 4 — an toàn và độ bền.

## 2. Phần việc phụ trách

Kiểm tra hệ thống xử lý claim hoàn tiền LogiX-VN trên bốn kiến trúc workflow, single, orchestrator và swarm, tập trung vào bốn ranh giới: approval hợp lệ, chống hoàn tiền trùng, phục hồi sau crash và bảo vệ secret/PII.

Mục tiêu là xác nhận việc ghi tiền do host kiểm soát. Model hoặc ticket không được tự tạo quyền duyệt; một claim chỉ có một refund; refund và committed audit phải nhất quán; dữ liệu nhạy cảm không được đi vào kết quả, trace hoặc console.

## 3. Đóng góp cụ thể

| File | Nội dung | Số test |
| --- | --- | ---: |
| `src/tests/test_task4_authorization.py` | Approval thiếu, không tồn tại, hết hạn, revoked/pending, amount không dương, mượn approval, approval dự phòng; biên hết hạn và cap 1 VND | 88 |
| `src/tests/test_task4_durability.py` | Ba điểm crash trên bốn shape; retry/đổi seed; conflict; trùng đơn; rollback khi audit lỗi; hai caller ghi đồng thời | 92 |
| `src/tests/test_task4_privacy.py` | Ticket chứa chỉ dẫn độc hại và secret/PII trên sáu nhánh trả về, kiểm cả trace, file phát sinh và stdout/stderr | 48 |
| `src/tests/task4_helpers.py` | Assertion chung cho kết quả, ledger/audit và quét dữ liệu nhạy cảm | — |
| **Test an toàn task 4** | Không skip/xfail | **228** |
| `src/tests/test_task4_report_export.py` | Kiểm kết quả JUnit và bảo toàn trạng thái pass/fail/error/skip khi xuất JSON | 6 |
| `src/scripts/task4_report.py` | Chạy test thật, xuất JSON từng test/từng module và provenance | — |
| **Tổng test bổ sung gồm kiểm exporter** | Không skip/xfail | **234** |

Các quyết định kỹ thuật chính:

- Đáp án tiền/trạng thái được xác định từ luật nghiệp vụ, không dùng hàm quote đang kiểm để tạo nhãn.
- Mỗi test dùng DB tạm và cwd riêng, không sửa fixture public hoặc file thước đo.
- Approval được kiểm qua shape gọi host, có gọi lại để phát hiện bypass khi retry và audit nhân đôi.
- Crash phải thực sự phát sinh `InjectedCrash`; kiểm trạng thái trước resume rồi replay cùng seed và seed khác để xác nhận một effect, một committed audit.
- Kiểm transaction bằng trigger SQLite gây lỗi insert audit, xác nhận effect rollback trước khi cho retry.
- Kiểm race bằng hai thread với connection SQLite riêng; cùng claim không tạo hai effect, khác claim cùng đơn không vượt trần.
- Quét cả console và file phát sinh ngoài prefix chuẩn để không bỏ sót log đặt sai tên.

Commit task 4: [`7b717a2`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/7b717a28af5de404670e74378ec42289e04eb894) (`feat(task4): implement pytest report generation and export to JSON by LNAKhoi`).

Commit task 4 Last Update: c83911138173987ceedf6bcf45d18930b2403dfb (`test(task4): refresh safety evidence and personal report`)

## 4. Bằng chứng kiểm chứng

Môi trường chạy lại cuối: Python 3.13.12, Windows AMD64 và pytest 8.4.2. Ngày kiểm chứng: 2026-11-18 (GMT+7).

| Kiểm tra | Kết quả đã ghi nhận |
| --- | --- |
| Test an toàn task 4 | 228/228 pass; `src/reports/task4_tests.json` |
| Cổng host mặc định | 338/338 pass; `src/reports/task4_host.json`; pytest deselect 688 student |
| Toàn bộ test host và student | 1.026/1.026 pass; `src/reports/task4_regression.json`; không fail/skip/xfail |
| Crash suite chính thức | 20/20 |
| Smoke | `lab8.smoke pass` |

Bằng chứng và mô tả chi tiết: [task4_safety.md](task4_safety.md). Kết quả từng test an toàn: [task4_tests.json](../../src/reports/task4_tests.json); cổng host: [task4_host.json](../../src/reports/task4_host.json); toàn project: [task4_regression.json](../../src/reports/task4_regression.json); crash chính thức: [crash.json](../../src/reports/crash.json). Các kiểm thử mới không phát hiện lỗi cần sửa trong ba shape hoặc host.

Run id dẫn chứng lần chạy này:

- `T4-task4-20261117T171038Z-b992875c` — 228 test an toàn.
- `T4-host-20261117T171108Z-80296e8b` — cổng host.
- `T4-all-20261117T171145Z-f608a907` — toàn project.

Ba JSON có exit code 0, `all_passed=true` và failed/error/skipped bằng 0. Lần chạy mới có 1.026 test do nhánh nhóm đã tích hợp thêm bốn test sau bằng chứng 1.022 trước đó. Metadata ghi revision nền `74432f9`, trạng thái working tree tại lúc sinh báo cáo và hash source; không dùng thời gian test như latency model.

Lệnh tự kiểm, chạy trong `src/` sau khi cài `requirements.txt` vào venv:

```powershell
python -m scripts.task4_report --scope task4 --out reports/task4_tests.json
python -m scripts.task4_report --scope host --out reports/task4_host.json
python -m scripts.task4_report --scope all --out reports/task4_regression.json
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.smoke
python -m lab8.check_submission
```

## 5. Công cụ AI và cách kiểm tra kết quả

Tôi trực tiếp đọc luật nghiệp vụ và contract, thiết kế các tình huống kiểm thử, triển khai test/helper cùng script xuất báo cáo, sau đó chạy pytest, crash suite và smoke để kiểm chứng. Tôi dùng Codex như công cụ hỗ trợ ở phạm vi nhỏ để phản biện một số trường hợp biên, rà lại cách diễn đạt và gợi ý điểm cần kiểm tra thêm; mọi đề xuất đều được tôi đối chiếu lại với code, dữ liệu SQLite và kết quả chạy thật trước khi sử dụng.

JSON bằng chứng được sinh tự động từ kết quả pytest JUnit rồi chuyển thành dữ liệu tổng hợp, không nhập tay. Tôi không thay đổi các file thước đo và không tự tạo commit, run ID hoặc số liệu. Exporter chỉ lưu định danh test, trạng thái và thời gian chạy; traceback, console và dữ liệu nhạy cảm không được đưa vào JSON.

Các bước tôi dùng để tự kiểm gồm đối chiếu `RunResult` với ledger/audit thật, đọc checkpoint sau crash, quét artifact và stdout/stderr để tìm secret/PII, inject lỗi bằng SQLite trigger để kiểm rollback và chạy hai writer độc lập để kiểm cạnh tranh ghi tiền. Tôi cũng chạy các test mới cùng toàn bộ test có sẵn để phát hiện hồi quy. Qua quá trình này, tôi có thể giải thích sự khác nhau giữa quote đầy đủ và tiền thực trả, vai trò riêng của ledger và checkpoint, cũng như lý do approval hợp lệ nhưng thuộc claim khác vẫn phải bị chặn.

## 6. Đánh giá kết quả và giới hạn

Về kết quả kỹ thuật, tôi đã xây dựng bộ kiểm bao phủ bốn nhóm yêu cầu được giao: approval, idempotency, phục hồi sau crash và bảo vệ secret/PII. Các trường hợp kiểm tra gồm cap/top-up, retry khác seed, rollback khi audit lỗi và cạnh tranh ghi tiền. Kết quả chạy lại cho thấy toàn bộ test Task 4 và test hồi quy đều pass; không phát hiện lỗi cần sửa trong ba shape ở phạm vi đã kiểm.

Kết quả vẫn có giới hạn: bài lab dùng MockLLM, SQLite, hai seed an toàn 11/55 và dữ liệu synthetic. Crash được inject tại ba điểm định trước, không mô phỏng việc tắt máy hoặc kill process ở thời điểm bất kỳ. Tôi chưa có hidden pack nên không khẳng định pass rate hoặc safety count trên bộ chấm ẩn, đồng thời chưa kiểm thử với payment provider bên ngoài. Crash suite 20 điểm chính thức chủ yếu kiểm host/swarm; bộ test tôi bổ sung mở rộng kiểm tra crash và retry trên cả bốn shape.
