# Task 4 — An toàn và độ bền

- Phần việc theo phân công: Khôi — approval, hoàn tiền trùng, crash và rò secret.
- Bộ kiểm tra được phát triển, được rà lại trên nhánh nhóm và commit tại `7b717a28af5de404670e74378ec42289e04eb894`.
- Ngày kiểm chứng lại: 2026-11-18, GMT+7.
- Revision nền của bằng chứng mới: `74432f9bc81f9604607e98d1da39c4120163a125`.
- Kết quả cuối: 228/228 test an toàn task 4 pass; thêm 6 test xuất JSON pass; toàn bộ project 1.026 test pass; cổng host 338 pass; smoke pass; crash suite chính thức 20/20.

## Yêu cầu và phương pháp kiểm

| Yêu cầu | Test và bằng chứng |
| --- | --- |
| Approval hợp lệ phải đúng approval_id mà claim trỏ đến và thuộc đúng claim | `test_task4_authorization.py`; kiểm cả hai lần gọi lại |
| Thiếu/hỏng/hết hạn/thu hồi approval hoặc amount không dương không tạo refund | Kiểm status denied, proposal đầy đủ, ledger rỗng, không có committed audit/checkpoint, có đúng lý do policy_denied |
| Biên hết hạn và cap không bị từ chối sai | Approval hết hạn đúng ngày as_of vẫn hợp lệ; approval 1 VND chỉ ghi effect 1 VND dù quote 35.000 |
| Một claim chỉ được trả một lần, kể cả crash/retry/đổi seed | `test_task4_durability.py`; kiểm tiền, số dòng ledger, committed audit và checkpoint bằng connection mới |
| Refund và audit phải cùng transaction | Trigger SQLite gây lỗi khi ghi committed audit; effect phải rollback; bỏ trigger thì retry thành công |
| Hai caller không vượt idempotency/trần theo đơn | Hai thread dùng connection SQLite riêng, đồng bộ trước khi gọi host; kiểm cùng claim và khác claim cùng đơn |
| Secret/PII trong ticket không được đi vào output | `test_task4_privacy.py`; quét result, trace/side files, stdout/stderr và file khác trong cwd cô lập |

Đáp án tiền và trạng thái là hằng số suy ra từ `docs/business_rules.md`/`docs/contracts.md`, không dùng chính hàm quote để tạo nhãn. Mỗi test có SQLite và cwd riêng; fixture chính thức không bị sửa. Không tạo thêm file spec/checklist riêng; yêu cầu, thiết kế và kết quả được giữ trong báo cáo bàn giao này.

## Code bàn giao

| File | Số test | Nội dung |
| --- | ---: | --- |
| `src/tests/test_task4_authorization.py` | 88 | 11 tình huống × bốn shape × hai seed; mỗi tình huống gọi lại hai lần |
| `src/tests/test_task4_durability.py` | 92 | 72 crash/resume, 8 conflict/recovery, 8 ticket trùng đơn, 1 rollback audit và 3 race bằng SQLite thật |
| `src/tests/test_task4_privacy.py` | 48 | Sáu nhánh trả về × bốn shape × hai seed, có ticket chứa chỉ dẫn độc hại và secret/PII |
| `src/tests/task4_helpers.py` | — | Assertion chung cho evaluator, ledger/audit, privacy và thu thập console/artifact |
| **Test an toàn task 4** | **228** | Không skip hoặc xfail |
| `src/tests/test_task4_report_export.py` | 6 | Kiểm trạng thái JUnit, số lượng nhất quán, fail-closed và loại nội dung nhạy cảm |
| `src/scripts/task4_report.py` | — | Chạy pytest thật, chuyển JUnit thành JSON theo scope task4/host/all |
| **Tổng test bổ sung, gồm kiểm xuất báo cáo** | **234** | Không skip hoặc xfail |

Các shape được kiểm là workflow, single, orchestrator và swarm; hai seed safety là 11 và 55. Các test task 4 nằm trong cổng pytest mặc định để tiếp tục bắt hồi quy an toàn.

## Approval

Chín tình huống phải chặn: claim không có approval_id, approval_id không tồn tại, approval hết hạn, revoked, pending, amount bằng 0, amount âm, mượn approval của claim khác, và claim trỏ approval revoked dù có một approval valid dự phòng cho cùng claim. Ticket tự xưng được duyệt hoặc yêu cầu bỏ policy không làm thay đổi quyền.

Mỗi ca được chạy hai lần để kiểm retry không vượt gate và audit denial không nhân đôi. Hai ca phải được chấp nhận là approval hết hạn đúng ngày `2026-11-15` và approval chỉ 1 VND. Ngày xét của lab là `2026-11-15`, không lấy ngày hệ điều hành.

## Crash, retry và transaction

Mỗi shape được inject crash thật tại `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`. `InjectedCrash` bắt buộc phải truyền ra; test fail nếu shape nuốt lỗi hoặc bỏ qua crash_at.

Ba claim được kiểm gồm refund thường, refund bị cap bởi approval và top-up do đã nhận một phần trước đó. Trước resume, test kiểm đúng trạng thái ledger/audit/checkpoint tại từng điểm crash. Sau đó resume, replay cùng seed và replay seed khác vẫn chỉ có một effect và một committed audit; checkpoint phải ghi số tiền thực trả.

Conflict được kiểm bằng cách đổi phí ship sau lần commit đầu: lần gọi tiếp phải failed/amount_conflict và giữ tiền cũ, audit conflict chỉ có một dòng dù retry. Khôi phục quote ban đầu phải cho phép idempotent replay thành công.

Kiểm transaction không dùng mock: một trigger trong DB tạm làm insert committed audit thất bại. Test xác nhận effect và checkpoint chưa tồn tại sau rollback; gỡ trigger rồi retry trả đúng một lần.

Ba ca race dùng hai thread, hai connection SQLite độc lập và barrier trước host call. Hai ca cùng claim (refund thường và top-up) đều trả cùng effect; ca khác claim cùng đơn chỉ cho một bên thắng, bên còn lại bị order_already_refunded. Đây là kiểm cạnh tranh ghi tiền trong SQLite của lab, chưa mô phỏng provider thanh toán bên ngoài.

## Secret, PII và trace

Ticket đối kháng yêu cầu in header/secret, cấp tool ghi và bỏ policy; đồng thời mang canary, dữ liệu riêng của order và tên field nhạy cảm. Kiểm trên các nhánh resolved, denied do quote bằng 0, needs_info, escalated, denied do approval và unknown claim.

Với mỗi kết quả hoàn tất, evaluator kiểm trace đúng contract, mới được ghi trong lần chạy, run_id đúng và ledger/audit khớp. Assertion bổ sung kiểm stdout/stderr và mọi file trong cwd tạm, kể cả log đặt sai prefix mà scanner chính thức có thể bỏ sót. Chỉ DB SQLite fixture và ba sidecar journal/wal/shm được coi là trusted storage, không quét nội dung DB như log.

Sau crash, kiểm các artifact thực sự được tạo và console; không ép workflow phải có trace hoàn tất ở trước-effect crash. Trace contract đầy đủ được kiểm lại khi resume hoàn tất. Đây không là miễn trừ cho việc log secret khi crash.

## Bằng chứng JSON và kết quả cuối

Môi trường chạy lại: Python 3.13.12, Windows AMD64; pytest 8.4.2. Các số dưới đây lấy từ JSON do lần chạy thực tế sinh ra, không sửa tay file kết quả.

| Phạm vi | File bằng chứng | Kết quả |
| --- | --- | --- |
| Approval | [task4_tests.json](../../src/reports/task4_tests.json), module `tests.test_task4_authorization` | 88/88 pass |
| Durability | Cùng JSON, module `tests.test_task4_durability` | 92/92 pass |
| Privacy | Cùng JSON, module `tests.test_task4_privacy` | 48/48 pass |
| Tổng test an toàn task 4 | [task4_tests.json](../../src/reports/task4_tests.json) | 228/228 pass |
| Cổng host mặc định | [task4_host.json](../../src/reports/task4_host.json) | 338/338 pass; pytest deselect 688 student |
| Toàn bộ host và student | [task4_regression.json](../../src/reports/task4_regression.json) | 1.026/1.026 pass |
| Crash suite chính thức | [crash.json](../../src/reports/crash.json) | 20/20 |

Cả ba JSON pytest có `all_passed=true`, `pytest_exit_code=0`, `report_error=null`, số failed/error/skipped đều bằng 0. Cổng host hiện gồm 104 test khác + 228 test an toàn + 6 test exporter. Tổng project tăng từ bằng chứng cũ 1.022 lên 1.026 do bốn test đã được tích hợp thêm trên nhánh nhóm, không phải sửa số liệu cũ bằng tay.

Run id của lần kiểm chứng 2026-11-17:

- Task 4: `T4-task4-20261117T171038Z-b992875c`.
- Host: `T4-host-20261117T171108Z-80296e8b`.
- Toàn bộ project: `T4-all-20261117T171145Z-f608a907`.

JSON giữ kết quả từng test, tổng hợp theo module, phiên bản môi trường, thời điểm UTC, revision nền và SHA-256 source được kiểm. Provenance ghi `working_tree_dirty=true` vì các report được tái sinh trong working tree; commit kỹ thuật task 4 đã chốt là `7b717a2`. Timing là thời gian chạy pytest, không là latency của MockLLM hoặc production.

Script dùng JUnit tích hợp sẵn của pytest, không cài thêm plugin. Traceback, system-out/system-err và dữ liệu claim/order không được chép vào JSON. Các trạng thái failed/error/skipped được giữ riêng; thiếu XML, lệch số lượng hoặc không có test không thể được báo thành all_passed. XML và DB phục vụ xuất báo cáo nằm trong thư mục tạm và được dọn sau khi đọc.

Crash JSON chỉ do `lab8.crash_test` tạo; exporter từ chối ghi đè `crash.json`/`benchmark.json`. Smoke chạy lại cho `lab8.smoke pass`. Không cần sửa ba shape, host, evaluator, config hoặc dữ liệu public để đạt các kết quả trên.

## Lệnh tái lập

Chạy từ `src/`, dùng venv đã cài `requirements.txt`. Thư mục tạm nằm trong `.venv` để tránh lỗi quyền thư mục temp dùng chung của Windows:

```powershell
python -m scripts.task4_report --scope task4 --out reports/task4_tests.json
python -m scripts.task4_report --scope host --out reports/task4_host.json
python -m scripts.task4_report --scope all --out reports/task4_regression.json
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.smoke
python -m lab8.check_submission
```

Mỗi lần chạy có run id và timestamp mới. Khi chạy lại để nộp, cập nhật run id dẫn chứng trong báo cáo theo JSON mới; không tự đổi run id bên trong JSON.

## Giới hạn và hồ sơ cá nhân

Không có pack hidden nên chưa có safety counts hoặc pass rate của hidden grader. Không suy ra bảo đảm cho mọi dữ liệu hoặc hệ thống production từ các test trên. Crash suite 20 điểm chính thức chủ yếu kiểm host và swarm; test mới bổ sung crash/resume cho cả bốn shape.

[Báo cáo cá nhân Lê Nguyễn Anh Khôi — 2A202603755](2A202603755_LeNguyenAnhKhoi.md) ghi rõ phần hỗ trợ bằng Codex, commit kỹ thuật và bằng chứng chạy lại. `TEAM.md` đã liên kết commit thật của task 4; việc push commit cập nhật bằng chứng cuối vẫn do nhóm thực hiện.

## Nguồn

 `docs/business_rules.md`, `docs/contracts.md`, `RULES.md`, `src/lab8/durability.py`, `src/lab8/policy.py` và các test host có sẵn. Quy trình yêu cầu → thiết kế → triển khai → kiểm chứng được giữ trong báo cáo này để bàn giao.
