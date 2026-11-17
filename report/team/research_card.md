# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang và cộng sự (2026), [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/), EMNLP 2026; nghiên cứu benchmark có kiểm soát. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Một số mức cải thiện hiệu quả MAS được báo cáo phụ thuộc vào prompt và topology ban đầu, nên không thể mặc định quy chênh lệch cho thay đổi cấu trúc. Trong các thiết lập tác giả đánh giá, lợi ích cũng có thể đến từ đường tool bị vô hiệu hoặc cấu trúc ban đầu đã dư thừa. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận của bài báo áp dụng cho các phương pháp và benchmark MAS mà tác giả khảo sát. Lab này dùng MockLLM, 14 claim public và chi phí mô phỏng; không thể coi kết quả của lab là xác nhận chung cho model thật hoặc môi trường sản xuất. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trước khi so sánh, giả thuyết là workflow và single sẽ đạt pass rate xấp xỉ nhau (chênh không quá 0.05), còn single có cost/success mô phỏng cao hơn khoảng 1–5 VND do có thêm lời gọi model. Đây là giả thuyết dùng để đối chiếu với số liệu hiện có, không phải dự đoán đã được ghi nhận trước lần chạy. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Mục tiêu ablation là chỉ thay topology và giữ cố định MockLLM, prompt tương đương, tool registry và cách dùng tool, seed, corpus, giá, evaluator. Benchmark hiện có giữ cùng corpus, seed, giá và evaluator, nhưng workflow không gọi model còn single có vòng ReAct; prompt và số lời gọi tool/model cũng khác. Vì vậy kết quả hiện có là so sánh shape, chưa phải ablation một biến. Cần thiết kế và chạy hai biến thể kiểm soát các yếu tố còn lại để kiểm tra quan hệ nhân quả. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Có thể kết luận nhầm topology làm tăng cost trong khi nguyên nhân là số lần gọi model hoặc tool. Đo pass rate, pass^5, seed variance, cost/success, số lời gọi model/tool và kiểm tra leak, approval bypass trên cùng bộ claim và seed. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11` là một trial ví dụ; số liệu tổng hợp nằm trong `src/reports/benchmark.json`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Kết quả quan sát phù hợp với giả thuyết mô tả: workflow và single đều đạt pass rate 1.000 và pass^5 1.000; cost/success tương ứng 27.86 và 29.86 VND, chênh 2.01 VND sau làm tròn. Workflow có trung bình 0 model call và 2.79 tool call/trial, single có 3.79 model call và 2.79 tool call/trial. **Không kết luận được tác động riêng của topology** vì benchmark thay đổi nhiều yếu tố cùng lúc; chưa có kết quả ablation một biến.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Giả thuyết trên được lập sau khi đã có kết quả và cần được kiểm tra lại trên thí nghiệm độc lập hoặc bộ dữ liệu mới. Không sửa JSON; không suy ra điểm hidden từ bộ public.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
