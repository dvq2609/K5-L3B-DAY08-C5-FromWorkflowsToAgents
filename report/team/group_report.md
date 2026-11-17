# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: C5
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md).
- Commit dẫn chứng trong [decision_adr.md](decision_adr.md): `fc6128a` chứa code/test task 5 và JSON benchmark/crash; bản task 5 tương ứng trong lịch sử nhóm là `a18fcd6`. Benchmark ban đầu chạy trên code nền `3404695`. Các hash này là bằng chứng cho kết quả, chưa thay cho commit chốt bài nộp cuối của nhóm.

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý yêu cầu hoàn phí vận chuyển hoặc bồi thường hàng hỏng trên cùng dữ liệu LogiX-VN bằng bốn shape: workflow, single agent, orchestrator và swarm tham chiếu. Mục tiêu là chọn mức tự chủ đủ đáp ứng bài toán, dựa trên tính đúng, độ ổn định và chi phí mô phỏng.

Nhóm chia phần triển khai workflow, single và orchestrator; các phần kiểm thử an toàn và đánh giá được thực hiện cùng quá trình tích hợp. Mỗi shape trả về cùng contract `RunResult` và gọi host khi cần ghi refund. Nhóm giữ dữ liệu, seed, bảng giá và evaluator chung khi chạy benchmark; swarm có sẵn được dùng làm đối chứng.

## 3. Giải pháp

- **Workflow:** đọc claim và kiểm tra quyền truy cập đơn; tính quote bằng `compute_compensation` từ dữ liệu đơn và policy hiện hành. Shape trả `needs_info` khi thiếu mã đơn, `escalated` khi đơn không hiển thị, `denied` khi quote bằng 0 hoặc host từ chối, và `resolved` khi host chấp nhận.
- **Single:** dùng vòng `run_react` tối đa 8 bước. Agent chọn các tool đọc để thu thập claim, đơn và quote; code sau vòng lặp gọi host nếu quote lớn hơn 0. Lời gọi MockLLM được tính vào budget.
- **Orchestrator:** tạo handoff qua `make_handoff` và giao investigator các tool chỉ đọc. Handoff dùng allowlist và không chứa toàn bộ claim, ticket, secret hay header. Orchestrator tính quote từ kết quả điều tra và gọi host.
- **Swarm:** dùng bản tham chiếu của đề để so sánh; bản này có điểm yếu cố ý khi tin số ngày trễ trong ticket ở một số seed.

Ở cả bốn shape, model không quyết định số tiền hay trực tiếp ghi ledger. Shape gửi **quote đầy đủ** đến `issue_refund`; host kiểm tra approval, quyền, trần hoàn theo đơn và idempotency. Host tự trừ khoản hoàn trước đó. `crash_at` được truyền đến host để kiểm thử khả năng chạy lại sau crash.

Trace ghi các sự kiện phù hợp với từng shape, như quyết định và quote của workflow, hoặc handoff đã sanitize và tóm tắt điều tra của orchestrator. Không ghi nguyên claim, ticket, secret, header, số điện thoại, địa chỉ, tên hàng hay ghi chú nội bộ vào trace. `finish()` tạo kết quả và ghi trace ở các nhánh trả về thông thường.

## 4. Kết quả

Benchmark dùng 14 claim public, seed `11,22,33,44,55`, MockLLM và bảng giá mô phỏng chung. Mỗi shape có 70 trial; kết quả được lấy từ [benchmark.json](../../src/reports/benchmark.json).

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 1.86 / 2 |
| Single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 29.86 | 4.64 / 5 |
| Orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.12 | 4.36 / 5 |
| Swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Swarm có một trial trả `resolved` thay vì `denied`: `R-swarm-C-002-s55`. Báo cáo [crash.json](../../src/reports/crash.json) ghi `20/20`; suite gồm các tình huống crash/resume cùng kiểm tra conflict, thiếu approval và crash của swarm.

Phần task 5 thêm 465 test, gồm 20 test luật, 440 test tích hợp và 5 test tạo bảng. Lần rà lại trên nhánh Anh Nhân ngày 17/11/2026 ghi nhận 465 test task 5 và 1.026 test toàn project pass. Có một cảnh báo quyền ghi pytest cache, không có test thất bại. [JSON hồi quy task 4](../../src/reports/task4_regression.json) lưu lần chạy trước đó với 1.022 test pass; số 788 trong báo cáo đánh giá task 5 là mốc trước khi bổ sung task 4. Các mốc này được phân biệt theo lần kiểm chứng, không gộp thành kết quả của cùng một revision.

Nhóm chọn **workflow**: trên bộ public, shape này đạt 70/70 trial và chi phí mô phỏng thấp nhất. Chi tiết xem [decision_adr.md](decision_adr.md). [Research card R4](research_card.md) nêu giới hạn của so sánh: các shape còn khác nhau về lời gọi model và cách xử lý, nên chưa thể quy chênh lệch riêng cho topology; ablation một biến vẫn cần thực hiện.

## 5. Khó khăn và cách xử lý

Ticket có thể đưa thông tin sai hoặc yêu cầu bỏ qua policy. Nhóm sử dụng dữ liệu order và policy có cấu trúc để tính tiền, giới hạn tool của investigator và không đưa ticket thô vào trace. Một trường hợp cần chú ý khác là đơn đã hoàn trước đó: shape vẫn gửi quote đầy đủ, để host tính phần còn được hoàn và ghi audit khi từ chối.

Các JSON task 4 đang lưu ghi Python 3.12.14, pytest 8.4.2. Lần rà lại task 5 và toàn project ngày 17/11/2026 cũng dùng Python 3.12.14, nằm trong khoảng 3.11–3.13 của đề. Khi chạy ở máy khác, cần ghi phiên bản và giữ riêng kết quả của từng lần chạy.

## 6. Tổng hợp đóng góp

Chi tiết vai trò, commit và test của từng thành viên được ghi trong [TEAM.md](../../TEAM.md); mỗi thành viên có báo cáo cá nhân trong `report/team/`.

Lê Nguyễn Anh Nhân (2A202603838) phụ trách đánh giá và đối chiếu: thêm 465 test task 5, script tạo bảng từ benchmark JSON, phân tích lỗi swarm ở seed 55 và đề xuất workflow. Commit gốc là `fc6128a`, bản task 5 trong lịch sử nhóm là `a18fcd6`; `d1faaa7` tích hợp main và `3e4522a` đồng bộ thông tin. Hai commit task 5 có cùng bốn file Python, không tính trùng số test. Chi tiết tại [báo cáo cá nhân của Nhân](2A202603838_LeNguyenAnhNhan.md).

## 7. Hạn chế và hướng cải thiện

Kết quả chỉ phản ánh dữ liệu giả, 14 claim public và năm seed; chưa có kết quả chấm hidden trong bằng chứng này. MockLLM không phải model sản xuất, cost là mô phỏng và latency là `unavailable`. Benchmark hiện tại không cô lập topology khỏi prompt và số lời gọi model/tool. Nhóm cần thực hiện ablation có kiểm soát và đánh giá trên dữ liệu đại diện hơn trước khi kết luận về tác động nhân quả hoặc áp dụng vào hệ thống thực.

## 8. Tài liệu tham khảo

- [Luật nghiệp vụ](../../docs/business_rules.md), [contract kết quả và trace](../../docs/contracts.md), [định nghĩa metric](../../docs/metrics.md) của lab.
- Zhang và cộng sự (2026), [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/), EMNLP 2026.
