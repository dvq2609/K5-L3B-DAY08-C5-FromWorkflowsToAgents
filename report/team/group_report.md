# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: C5
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md).
- Commit code được ghi trong [decision_adr.md](decision_adr.md): `3404695`; nhóm cần cập nhật cả hai file sau khi commit code, test và bằng chứng cuối cùng.

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

Swarm có một trial trả `resolved` thay vì `denied`. Báo cáo [crash.json](../../src/reports/crash.json) ghi `20/20`; suite gồm các tình huống crash/resume cùng kiểm tra conflict, thiếu approval và crash của swarm. Nhóm cũng đã chạy 248 test student và 75 test mặc định thành công sau khi tích hợp; số test mặc định có thể thay đổi khi thêm test.

Nhóm chọn **workflow**: trên bộ public, shape này đạt 70/70 trial và chi phí mô phỏng thấp nhất. Chi tiết xem [decision_adr.md](decision_adr.md). [Research card R4](research_card.md) nêu giới hạn của so sánh: các shape còn khác nhau về lời gọi model và cách xử lý, nên chưa thể quy chênh lệch riêng cho topology; ablation một biến vẫn cần thực hiện.

## 5. Khó khăn và cách xử lý

Ticket có thể đưa thông tin sai hoặc yêu cầu bỏ qua policy. Nhóm sử dụng dữ liệu order và policy có cấu trúc để tính tiền, giới hạn tool của investigator và không đưa ticket thô vào trace. Một trường hợp cần chú ý khác là đơn đã hoàn trước đó: shape vẫn gửi quote đầy đủ, để host tính phần còn được hoàn và ghi audit khi từ chối.

Môi trường đã chạy các kết quả trên dùng Python 3.14.3, trong khi đề yêu cầu Python 3.11–3.13. Nhóm cần chạy lại bộ kiểm tra trên phiên bản được hỗ trợ trước khi nộp để xác nhận tính tương thích.

## 6. Tổng hợp đóng góp

Chi tiết vai trò, commit và test của từng thành viên được ghi trong [TEAM.md](../../TEAM.md); mỗi thành viên có báo cáo cá nhân trong `report/team/`.

**Đinh Phúc Diên (2A202603876)** phụ trách kiến trúc C. Triển khai `orchestrator.py`, thiết lập handoff chỉ cấp tool đọc cho investigator, tính quote từ dữ liệu đơn hàng và chuyển quote đầy đủ cho host kiểm tra approval, trần hoàn theo đơn và ghi refund. Phần triển khai cũng xử lý trace ở các nhánh trả về, ghi trace khi crash và giữ nguyên cơ chế idempotency của host khi chạy lại. Bổ sung `tests/test_orchestrator_handoff.py` với 13 trường hợp kiểm thử về handoff, rò rỉ dữ liệu, claim/đơn không hợp lệ, approval, ba điểm crash và xung đột số tiền khi retry. Shape được kiểm tra bằng 62 test student public; benchmark chung ghi nhận orchestrator đạt 70/70 trial. Code và test nằm trong commit `a27e3c9`; báo cáo cá nhân được thêm ở `31628d8`, thông tin thành viên được cập nhật ở `a67e869`. Phân tích chi tiết và khai báo sử dụng AI nằm trong [báo cáo cá nhân của Diên](2A202603876_DinhPhucDien.md).

## 7. Hạn chế và hướng cải thiện

Kết quả chỉ phản ánh dữ liệu giả, 14 claim public và năm seed; chưa có kết quả chấm hidden trong bằng chứng này. MockLLM không phải model sản xuất, cost là mô phỏng và latency là `unavailable`. Benchmark hiện tại không cô lập topology khỏi prompt và số lời gọi model/tool. Nhóm cần thực hiện ablation có kiểm soát và đánh giá trên dữ liệu đại diện hơn trước khi kết luận về tác động nhân quả hoặc áp dụng vào hệ thống thực.

## 8. Tài liệu tham khảo

- [Luật nghiệp vụ](../../docs/business_rules.md), [contract kết quả và trace](../../docs/contracts.md), [định nghĩa metric](../../docs/metrics.md) của lab.
- Zhang và cộng sự (2026), [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/), EMNLP 2026.
