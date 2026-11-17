# Báo cáo cá nhân — 2A202603838_LeNguyenAnhNhan

**Lab 8 — From Workflows to Agents: LogiX-VN**

## 1. Thông tin thành viên

- Họ tên: Lê Nguyễn Anh Nhân.
- MSSV: 2A202603838.
- Email: 26ai.nhanlna@vinuni.edu.vn.
- GitHub: ying684.

## 2. Phần việc phụ trách

Tôi phụ trách task 5: viết test cho các trường hợp biên, chạy benchmark bốn shape và tổng hợp số liệu để nhóm chọn kiến trúc. Phần kiểm tra tập trung vào policy cũ hoặc chưa có hiệu lực, thông tin sai trong ticket và trần hoàn tiền theo đơn. Phân công này thống nhất với [TEAM.md](../../TEAM.md).

## 3. Đóng góp cụ thể

Phần code task 5 gồm bốn file:

| File | Nội dung |
| --- | --- |
| `src/tests/test_task5_rules.py` | 20 test luật nghiệp vụ, hiệu lực policy và giới hạn số tiền |
| `src/tests/test_task5_shapes.py` | 440 test tích hợp: 22 tình huống × bốn shape × năm seed |
| `src/tests/test_task5_comparison.py` | 5 test kiểm bảng báo cáo và việc giữ nguyên JSON đầu vào |
| `src/scripts/task5_comparison.py` | Đọc JSON benchmark, tạo bảng Markdown kèm hash và run id dẫn chứng |

Đáp án test được viết từ luật nghiệp vụ, không lấy kết quả của hàm đang kiểm để làm đáp án. Các ca hoàn tiền kiểm cả `proposal_amount`, tiền thực ghi trong ledger và audit. Ví dụ, quote 150.000 VND với khoản hoàn trước đó 30.000 VND phải giữ proposal 150.000 và chỉ ghi thêm 120.000.

Hai ca ticket nói quá/nói thiếu số ngày ở seed 55 được dùng để chỉ ra điểm yếu cố ý của swarm. Test xanh ở hai ca đối chứng này nghĩa là đã phát hiện đúng lỗi dự kiến, không phải swarm xử lý đúng nghiệp vụ. Các shape nhóm viết vẫn phải đáp ứng đáp án đúng; không dùng skip/xfail để bỏ qua lỗi.

Các commit liên quan, đều có author `ying684`:

| Commit | Nội dung |
| --- | --- |
| [`fc6128a`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/fc6128a2dca3dd628519a5b0bcc948eaa7d1099f) | Commit task 5 ban đầu: code, 465 test, báo cáo và JSON benchmark/crash |
| [`a18fcd6`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/a18fcd61bebcaef0692cacc09b646d81d634a620) | Bản đưa phần code/test/báo cáo task 5 vào lịch sử nhóm; author là Nhân, committer là Khôi. Bốn file Python giống bản `fc6128a`, không tính thành đóng góp mới lần hai |
| [`d1faaa7`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/d1faaa71fb9ecfb9a9713feb70313f92b56289f6) | Tích hợp `main` vào nhánh cá nhân, nhận thay đổi của các thành viên |
| [`3e4522a`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/3e4522ae50a0e4faea6709ca62708cd5d4bfced0) | Đồng bộ `TEAM.md` và cập nhật thông tin trong báo cáo cá nhân |

Commit `3404695` là bản code nền được dùng khi chạy benchmark sau tích hợp task 1–3, không phải commit đóng góp của tôi.

## 4. Bằng chứng

Benchmark dùng cùng 14 claim public và năm seed `11,22,33,44,55`, tổng cộng 280 trial. Số liệu từ [benchmark.json](../../src/reports/benchmark.json), được tổng hợp trong [bảng so sánh](task5_comparison.md):

| Shape | Trial pass | Pass^5 | Cost/success mô phỏng (VND) |
| --- | ---: | ---: | ---: |
| Workflow | 70/70 | 1.000 | 27.86 |
| Single | 70/70 | 1.000 | 29.86 |
| Orchestrator | 70/70 | 1.000 | 57.12 |
| Swarm | 69/70 | 0.929 | 49.57 |

Trial swarm sai là `R-swarm-C-002-s55`: ticket nói trễ 5 ngày trong khi order chỉ trễ 2 ngày. Workflow đạt cùng độ đúng với single/orchestrator nhưng chi phí mô phỏng thấp hơn. Từ kết quả này, phần task 5 đề xuất workflow; [ADR](decision_adr.md) và [báo cáo nhóm](group_report.md) cũng đã chọn workflow. Run id dẫn chứng trong ADR là `R-workflow-C-001-s11`.

Ngày 17/11/2026, lần rà lại trong workspace dùng Python 3.12.14 cho **465 test riêng task 5 pass** và **1.026 test toàn project pass**. Có một cảnh báo không ghi được pytest cache do quyền thư mục; không có test thất bại. Con số 788 trong báo cáo đánh giá task 5 là lần kiểm ban đầu, trước khi bổ sung task 4 và test khác; JSON hồi quy task 4 lưu lần chạy 1.022 test. Đây là các mốc khác nhau, không phải ba số của cùng một lần chạy.

[Crash suite](../../src/reports/crash.json) đạt 20/20. Đây là bằng chứng an toàn chung, không tính thành test riêng task 5. Lệnh tái lập và lần đối chiếu benchmark/crash giống từng byte được ghi trong [task5_evaluation.md](task5_evaluation.md).

## 5. Công cụ AI đã dùng

Tôi sử dụng Codex để hỗ trợ tìm hiểu code, gợi ý các trường hợp biên, viết test và script tổng hợp kết quả. Các ca kiểm thử bám theo luật nghiệp vụ và contract của lab; kết quả được kiểm chứng bằng pytest, đối chiếu với ledger, audit và trace.

Số liệu trong báo cáo lấy từ JSON do công cụ của lab tạo ra, không sửa thước đo hoặc nhập tay kết quả. AI là công cụ hỗ trợ trong quá trình làm bài; tôi chịu trách nhiệm về nội dung và kết quả của phần task 5.

## 6. Tự đánh giá

Về phần việc được giao, task 5 đã có test biên, benchmark đủ bốn shape, bảng so sánh và phân tích để nhóm ra quyết định. Điểm cần giữ rõ là proposal khác số tiền thực trả, và test đối chứng xanh không đồng nghĩa swarm đúng trên mọi trial.

Hạn chế chính là bộ public chỉ có 14 claim, MockLLM và giá đều mô phỏng. Kết quả 100% trên public chưa chứng minh đạt ngưỡng hidden. Benchmark cũng thay đổi cả cách gọi model/tool giữa các shape, nên chưa thể kết luận riêng tác động của topology. Như research card của nhóm đã nêu, cần thêm ablation có kiểm soát và dữ liệu độc lập nếu muốn kết luận rộng hơn.
