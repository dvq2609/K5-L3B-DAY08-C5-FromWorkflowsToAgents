# Báo cáo cá nhân — 2A202603789 Nguyễn Thành Công

**Lab 8 — From Workflows to Agents: LogiX-VN**

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thành Công
- MSSV: 2A202603789
- Email: 26ai.congnt3@vinuni.edu.vn
- GitHub: congnt180263

---

## 2. Phần việc phụ trách

Trong bài lab này, tôi đảm nhận vai trò **Người thứ 2 phụ trách Shape B — Single ReAct Agent**. Nhiệm vụ chính gồm:
- Triển khai kiến trúc Single Agent với vòng lặp ReAct (Reasoning + Acting) có giới hạn bước trong hàm `run_claim` tại [single.py](../../src/lab8/shapes/single.py).
- Thiết lập ranh giới an toàn nghiêm ngặt giữa ReAct Agent (chỉ đọc) và Host Runtime (ghi tiền duy nhất).
- Xây dựng bộ kiểm thử đơn vị chuyên sâu cho vòng lặp ReAct tại [test_single_react.py](../../src/tests/test_single_react.py).
- Chạy đối soát và đảm bảo Shape B vượt qua toàn bộ 62 test case trong ma trận kiểm thử public (`test_public_matrix.py`) cũng như kiểm tra định dạng bài nộp qua `lab8.check_submission`.

---

## 3. Đóng góp cụ thể

### 3.1. Thiết kế vòng lặp ReAct có chặn trên (Bounded ReAct Loop)
- Sử dụng hàm điều phối `lab8.runtime.run_react` với tham số `max_steps=8` và kích hoạt chế độ `worker=True`. 
- Cấu trúc hàm `decide(seen)` theo chu trình suy luận có kiểm soát:
  1. **Thought & Fetch Claim:** Nếu chưa có thông tin claim, gọi tool `get_claim_view(claim_id)`.
  2. **Early Stopping & Validation:** 
     - Claim không tồn tại (`not found`) $\rightarrow$ dừng ngay với `status="failed"`, `error_reason="unknown_claim"`.
     - Claim thiếu mã đơn hàng (`not order_id`) $\rightarrow$ dừng ngay với `status="needs_info"`, `error_reason="missing_order_id"`. Tuyệt đối không trích xuất mã đơn từ văn bản ticket.
  3. **Order Verification:** Gọi `lookup_order` với `order_id` và `principal_id`. Nếu đơn hàng không hiển thị hoặc không thuộc quyền sở hữu của khách hàng (`not visible`) $\rightarrow$ dừng ngay với `status="escalated"`.
  4. **Compensation Calculation:** Gọi `compute_compensation(order)`. Số tiền bồi thường được tính hoàn toàn bằng mã nguồn tất định dựa trên dữ liệu đơn hàng và chính sách còn hiệu lực (`is_current = 1 AND effective_date <= as_of`), loại bỏ hoàn toàn các thông tin sai lệch hoặc yêu cầu gian lận từ ticket (ví dụ khách nói trễ 5 ngày nhưng đơn hàng chỉ trễ 2 ngày như tại T02).
  5. **Final Evaluation:** Nếu số tiền quote $\le 0$, trả về `final` với `status="denied"`. Nếu quote $> 0$, trả về `final` với `status="ready_to_refund"`, nhường quyền ghi tiền cho Host.

### 3.2. Ranh giới Host-Writer và Xử lý Độ bền (Durability & Idempotency)
- **Host là bên ghi duy nhất:** ReAct worker tuyệt đối không được cấp phát công cụ ghi `issue_refund`. Chỉ khi vòng ReAct kết thúc thành công với trạng thái `ready_to_refund`, Host ngoài vòng lặp mới trực tiếp gọi `durability.issue_refund`.
- **Bảo toàn trần hoàn tiền theo đơn (Per-order Cap):** Luôn chuyển **toàn bộ số tiền quote (full quote)** vào `issue_refund`. Host chịu trách nhiệm tra cứu lịch sử và tự động cấn trừ phần tiền đã được hoàn trước đó (như các case T13, T14). Shape không tự ý trừ trước để tránh tình trạng trừ hai lần.
- **Xử lý sự cố (Crash Safety):** Truyền đầy đủ tham số `crash_at` vào `durability.issue_refund` và **không được nuốt `InjectedCrash`**, cho phép kiểm thử độ bền (T12) kích hoạt chính xác tại điểm checkpoint.
- **Đóng gói kết quả chuẩn hóa:** Sử dụng hàm `finish()` từ `lab8.shapes.common` để tự động đối chiếu ledger SQLite, trích xuất `refund_effects` và số lượng audit `refund_committed`, không tự bịa các trường này.

### 3.3. Tuân thủ Trace Contract v1 và Bảo mật Secret/PII
- Sử dụng `lab8.trace.Trace` để ghi lại tiến trình thực thi vào file JSON định danh theo `run_id`.
- Chỉ lưu trữ các trường an toàn đã qua allowlist (`thought`, `decision`, `quote`). Tuyệt đối không log toàn bộ claim row, order row hoặc ticket thô, đảm bảo 0 rò rỉ secret (`CANARY_SECRET_*`) hay thông tin cá nhân (SĐT, địa chỉ, internal note).

### 3.4. Xây dựng bộ test [test_single_react.py](../../src/tests/test_single_react.py)
Tôi đã tạo một bộ kiểm thử độc lập gồm 8 test case nhằm xác thực toàn diện các đặc tính kỹ thuật của Shape B:
1. `test_react_loop_enforces_step_cap`: Xác thực vòng lặp dừng chuẩn xác tại bước thứ 8 với lý do `step_cap` khi agent không chạm tới trạng thái `final`.
2. `test_react_loop_blocks_write_tools_for_worker`: Xác thực cơ chế phòng vệ của worker ngăn chặn việc gọi write tool `issue_refund` thông qua ngoại lệ `ToolRejected`.
3. `test_react_loop_rejects_unknown_tools`: Kiểm tra từ chối các tool không có trong danh mục.
4. `test_single_agent_resolves_valid_claim`: Kiểm tra luồng giải quyết hoàn tất cho đơn trễ hạn hợp lệ (T01).
5. `test_single_agent_ignores_misleading_ticket_delay`: Kiểm tra tính kiên định của agent trước ticket giả mạo số ngày trễ (T02).
6. `test_single_agent_stops_early_on_missing_order_id`: Kiểm tra nhánh dừng sớm `needs_info` khi thiếu `order_id` (T04).
7. `test_single_agent_stops_early_on_unknown_claim`: Kiểm tra dừng sớm `failed` khi claim không tồn tại.
8. `test_single_agent_escalates_unowned_order`: Kiểm tra chuyển cấp `escalated` khi người dùng khiếu nại đơn không thuộc sở hữu (T05).

---

## 4. Bằng chứng

- **Commit thực hiện:** [`d28abb772bdc3bba41fb103650cfe77cca3a6a8f`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/d28abb772bdc3bba41fb103650cfe77cca3a6a8f)  
  *Message:* `feat(single-agent): complete shape B react loop and add react unit tests`
- **Kết quả chạy bộ test ReAct tự viết:**
  ```powershell
  python -m pytest -q tests/test_single_react.py
  # Kết quả: 8 passed in 0.86s
  ```
- **Kết quả chạy ma trận 62 test của Shape Single (T01–T14 qua 5 seeds + T11 retry + T12 crash):**
  ```powershell
  python -m pytest -q -m student -o addopts= -k "single]"
  # Kết quả: 62 passed, 248 deselected in 4.89s
  ```
- **Kết quả chạy cổng Host mặc định:**
  ```powershell
  python -m pytest -q
  # Kết quả: 62 passed, 248 deselected in 7.61s
  ```
- **Kết quả công cụ kiểm định `check_submission`:**
  ```text
  == shapes ==
  [ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11
  [ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11
  ```
- **Dữ liệu Trace mẫu:** File trace phát sinh tại `src/traces/R-single-C-001-s11.json` tuân thủ nghiêm ngặt Trace Contract v1, vượt qua kiểm tra `check_trace`.

---

## 5. Công cụ AI đã dùng

Trong quá trình thực hiện, tôi đã sử dụng trợ lý **Antigravity (Gemini)** nhằm:
- Phân tích và tóm tắt nhanh tài liệu kiến trúc, luật nghiệp vụ và các hợp đồng ràng buộc trong repo.
- Hỗ trợ xây dựng khung vòng lặp ReAct trong `single.py` và gợi ý các kịch bản kiểm thử biên (boundary test cases) cho `test_single_react.py`.
- **Cách tự kiểm tra và kiểm chứng kết quả:** Tôi không chấp nhận mã nguồn một cách cảm tính mà trực tiếp đối chiếu logic với hợp đồng tại `docs/contracts.md`, tự chạy các lệnh kiểm thử `pytest`, xác minh kết quả trace và ledger SQLite để chắc chắn 100% không vi phạm các điều kiện must-pass (không bypass approval, không rò rỉ secret, không duplicate refund khi crash).

---

## 6. Tự đánh giá

- **Hiểu sâu sắc về kiến trúc ReAct Agent:** Việc triển khai Shape B giúp tôi nhận thức rõ sức mạnh linh hoạt của chu trình Thought-Action trong việc điều hướng đọc dữ liệu, nhưng đồng thời cũng thấy được tầm quan trọng sống còn của việc thiết lập các **lan can an toàn (guardrails)**:
  - Phải có giới hạn số bước lặp (`max_steps`) để ngăn chặn vòng lặp vô tận tiêu tốn ngân sách.
  - Phải cô lập quyền ghi tiền ở tầng Host thay vì giao quyền cho mô hình ngôn ngữ hoặc worker agent.
  - Không được tin tưởng vào dữ liệu không có cấu trúc do người dùng cung cấp (untrusted user prompt/ticket).
- **Giới hạn & Điểm cải thiện:** Mặc dù Shape B đã vượt qua toàn bộ 62 test public, nhưng trên thực tế chi phí gọi mô hình (model calls) và số bước (steps) vẫn cao hơn so với Shape A (Workflow). Khi mở rộng ra hệ thống thực tế lớn hơn, cần bổ sung cơ chế caching tool result và tinh gọn số lượt gọi model để tối ưu hóa chi phí vận hành.

