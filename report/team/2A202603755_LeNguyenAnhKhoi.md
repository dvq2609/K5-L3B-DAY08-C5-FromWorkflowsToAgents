# Báo cáo cá nhân — 2A202603755_LeNguyenAnhKhoi
## 1. Thông tin thành viên

- Họ tên: Lê Nguyễn Anh Khôi.
- MSSV: 2A202603755.
- Email: lnakhoi5a@gmail.com.
- GitHub: KN-16.
- Phần việc được phân công: task 4 — an toàn và độ bền.

## 2. Phần việc phụ trách

Kiểm tra hệ thống xử lý claim hoàn tiền LogiX-VN trên bốn kiến trúc workflow, single, orchestrator và swarm, tập trung vào bốn ranh giới: approval hợp lệ, chống hoàn tiền trùng, phục hồi sau crash và bảo vệ secret/PII.

Mục tiêu là xác nhận việc ghi tiền do host kiểm soát. Model hoặc ticket không được tự tạo quyền duyệt; một claim chỉ có một refund; refund và committed audit phải nhất quán; dữ liệu nhạy cảm không được đi vào kết quả, trace hoặc console.

## 3. Đóng góp kỹ thuật được chuẩn bị cho task 4

Bộ test được bổ sung bằng Codex theo yêu cầu Anh Nhân để hỗ trợ phần việc của Khôi. Khôi cần rà lại code và xác nhận đóng góp thực tế trước khi khai báo commit trong TEAM.md.

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

Commit task 4: **chưa tạo**.

## 4. Bằng chứng kiểm chứng

Môi trường đã chạy: Python 3.12.14, Windows AMD64, pytest 8.4.2 và PyYAML 6.0.3. Ngày kiểm chứng: 2026-11-17 (GMT+7).

| Kiểm tra | Kết quả đã ghi nhận |
| --- | --- |
| Test an toàn task 4 | 228/228 pass; `src/reports/task4_tests.json` |
| Cổng host mặc định | 334/334 pass; `src/reports/task4_host.json`; pytest deselect 688 student |
| Toàn bộ test host và student | 1.022/1.022 pass; `src/reports/task4_regression.json`; không fail/skip/xfail |
| Crash suite chính thức | 20/20 |
| Smoke | `lab8.smoke pass` |

Bằng chứng và mô tả chi tiết: [task4_safety.md](task4_safety.md). Kết quả từng test an toàn: [task4_tests.json](../../src/reports/task4_tests.json); cổng host: [task4_host.json](../../src/reports/task4_host.json); toàn project: [task4_regression.json](../../src/reports/task4_regression.json); crash chính thức: [crash.json](../../src/reports/crash.json). Các kiểm thử mới không phát hiện lỗi cần sửa trong ba shape hoặc host.

Run id dẫn chứng lần chạy này:

- `T4-task4-20261117T042816Z-54a47a5f` — 228 test an toàn.
- `T4-host-20261117T042923Z-633e37b4` — cổng host.
- `T4-all-20261117T042849Z-5ed20190` — toàn project.

Ba JSON có exit code 0, all_passed=true và failed/error/skipped bằng 0. Tổng mới 1.022 bao gồm 6 test exporter thêm sau lần kiểm 1.016 trước đó. Metadata giữ revision nền, trạng thái working tree chưa commit và hash source; không dùng thời gian test như latency model.

Lệnh tự kiểm, chạy trong `src/` sau khi cài `requirements.txt` vào venv:

```powershell
New-Item -ItemType Directory -Path .venv/tmp -Force | Out-Null
.\.venv\Scripts\python.exe -m scripts.task4_report --scope task4 --out reports/task4_tests.json
.\.venv\Scripts\python.exe -m scripts.task4_report --scope host --out reports/task4_host.json
.\.venv\Scripts\python.exe -m scripts.task4_report --scope all --out reports/task4_regression.json
.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
.\.venv\Scripts\python.exe -m lab8.smoke
```

## 5. Công cụ AI và cách kiểm tra kết quả

Codex hỗ trợ đọc luật/contract, thiết kế tình huống đối kháng, viết test/helper và script xuất JSON, chạy pytest/crash suite/smoke và soạn báo cáo từ kết quả thực tế. JSON được sinh bằng pytest JUnit rồi chuyển thành dữ liệu tổng hợp, không nhập tay. Không thay thước đo hoặc bịa commit/số liệu; không ghi traceback/console nhạy cảm vào JSON.

Các phép kiểm đã thực hiện trong workspace gồm đối chiếu kết quả với ledger/audit thật, đọc checkpoint sau crash, quét dữ liệu nhạy cảm trong artifact và console, inject lỗi bằng SQLite trigger và chạy hai writer độc lập. Các test mới cũng được chạy cùng toàn bộ test có sẵn để kiểm hồi quy.

Phần cần Khôi tự xác nhận trước nộp: chạy lại các lệnh, đọc từng nhóm test, giải thích được vì sao quote đầy đủ khác tiền thực trả, vì sao ledger/checkpoint khác vai trò, và vì sao approval valid của claim khác vẫn bị chặn. Chưa ghi nhận Khôi đã tự thực hiện các bước này.

## 6. Đánh giá kết quả và giới hạn

Về kết quả kỹ thuật, bộ kiểm đã bao phủ các tình huống approval, idempotency, crash và bảo mật được giao, với các trường hợp cap/top-up, lỗi audit và cạnh tranh ghi tiền. Không phát hiện hồi quy trong phạm vi test đã chạy.

Giới hạn là môi trường MockLLM và SQLite của lab, hai seed safety 11/55 và dữ liệu synthetic. Crash được inject tại các điểm định trước, không phải tắt máy hoặc kill process tùy thời điểm. Chưa có hidden pack nên không kết luận pass rate hoặc safety counts của hidden; cũng chưa kiểm payment provider bên ngoài. Crash suite 20 điểm chính thức kiểm chủ yếu host/swarm; test bổ sung mới kiểm cả bốn shape.
