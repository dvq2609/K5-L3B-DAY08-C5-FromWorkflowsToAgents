# Báo cáo cá nhân — Đinh Phúc Diên

**Lab 8 — From Workflows to Agents: LogiX-VN**

## 1. Thông tin thành viên

- Họ tên: Đinh Phúc Diên
- MSSV: 2A202603876
- Email: 26ai.diendp@vinuni.edu.vn
- GitHub: dinhphucdien179

## 2. Phần việc phụ trách

Tôi phụ trách kiến trúc C — orchestrator và investigator trong bài toán xử lý yêu cầu hoàn tiền của LogiX-VN. Phần việc gồm triển khai `run_claim` trong [orchestrator.py](../../src/lab8/shapes/orchestrator.py), thiết lập handoff cho investigator, kết nối với host để ghi refund và bổ sung kiểm thử trong [test_orchestrator_handoff.py](../../src/tests/test_orchestrator_handoff.py).

Mục tiêu của phần này là phân chia rõ trách nhiệm giữa bên thu thập dữ kiện và bên điều phối xử lý. Investigator được đọc đơn hàng, policy và lịch sử hoàn tiền. Orchestrator sử dụng kết quả đó để tính quote bằng code, sau đó gọi host kiểm tra approval và ghi nhận khoản hoàn. Cách phân chia này phải giữ đúng luật nghiệp vụ và contract chung để có thể so sánh với các kiến trúc còn lại.

## 3. Đóng góp cụ thể

### 3.1. Luồng xử lý của orchestrator

Hàm `run_claim` được giữ nguyên chữ ký của đề bài. Khi nhận một claim, chương trình đọc thông tin qua `get_claim_view`. Claim không tồn tại được trả về `failed`; thiếu `order_id` được trả về `needs_info`. Chương trình không tìm mã đơn trong nội dung ticket để thay cho trường dữ liệu bị thiếu.

Với claim có mã đơn, orchestrator tạo handoff và gọi investigator. Nếu đơn không tồn tại hoặc không thuộc principal của claim, kết quả là `escalated`. Khi đơn hợp lệ, orchestrator gọi `compute_compensation` trên dữ liệu đơn hàng đã được kiểm tra quyền truy cập. Quote bằng 0 dẫn đến `denied`; quote lớn hơn 0 được chuyển cho `durability.issue_refund` xử lý.

Các nhánh trả kết quả đều sử dụng `finish()`. Nhờ đó, `refund_effects` và số audit được lấy từ ledger thay vì tự khai báo trong shape. Connection SQLite được đóng trong `finally`, kể cả khi có crash.

### 3.2. Handoff và quyền của investigator

Handoff được tạo bằng `make_handoff`, theo contract `handoff.v1`. Investigator chỉ nhận ba tool: `lookup_order`, `lookup_policy` và `lookup_refund_history`. Danh sách này do code quy định; nội dung ticket và kết quả model không được dùng để cấp thêm quyền.

Tôi không đưa nguyên claim, ticket, secret hoặc header vào handoff. Trường `facts` được để trống vì investigator có thể lấy dữ kiện qua các tool đọc đã được giới hạn phạm vi. Orchestrator giữ quyền gọi host ghi refund; investigator không nhận `issue_refund` hay `append_audit`.

### 3.3. Tính tiền, approval và xử lý chạy lại

Số tiền được tính từ dữ liệu đơn hàng có cấu trúc và policy hiện hành. Ví dụ, ở T02, ticket nói đơn trễ 5 ngày nhưng dữ liệu đơn hàng ghi 2 ngày. Orchestrator sử dụng số 2 nên không đề xuất hoàn phí ship, kể cả với seed 55.

Một quyết định quan trọng là truyền **quote đầy đủ** vào host. Với T14, entitlement là 150.000 VND và đơn đã được hoàn 30.000 VND trước đó. Shape vẫn gửi quote 150.000 VND; host tự trừ khoản đã hoàn và ghi thêm 120.000 VND. Nếu shape trừ trước rồi mới gửi, host sẽ trừ lần nữa và khoản hoàn bị thiếu.

Khi quote lớn hơn 0, orchestrator gọi host ngay cả khi approval không hợp lệ. Host vừa ngăn ghi tiền, vừa tạo audit `policy_denied`. Shape ánh xạ kết quả từ chối sang `denied`; riêng xung đột số tiền khi retry được trả về `failed` và giữ nguyên khoản đã commit.

Tham số `crash_at` được chuyển nguyên vào `issue_refund`. Trước khi ngoại lệ truyền ra ngoài, trace được ghi bằng khối `finally`. Sau khi chạy lại, việc chống hoàn trùng dựa vào ledger của host.

### 3.4. Trace và kiểm thử bổ sung

Trace ghi các sự kiện `handoff`, `investigator`, `quote`, `refund_request` và `decision`, tùy nhánh xử lý. Phần investigator chỉ ghi tóm tắt nghiệp vụ như khả năng truy cập đơn, số policy và tổng tiền đã hoàn. Trace không chứa nguyên bản ghi đơn hàng hay nội dung ticket.

File test bổ sung có 13 trường hợp sau khi mở rộng các tham số:

| Nội dung kiểm thử | Số trường hợp |
| --- | ---: |
| Handoff đúng allowlist, investigator chỉ đọc và không ghi ledger | 1 |
| Ticket chứa chỉ dẫn giả và dữ liệu nhạy cảm không làm thay đổi quyền hoặc gây rò rỉ | 1 |
| Claim không tồn tại, thiếu mã đơn, sai principal vẫn có trace hợp lệ | 3 |
| Mã đơn không tồn tại được chuyển sang `escalated` | 1 |
| Thiếu approval, approval không tồn tại hoặc thuộc claim khác bị host từ chối và có audit | 3 |
| Crash tại ba thời điểm rồi resume và retry vẫn chỉ có một refund, một audit committed | 3 |
| Quote thay đổi khi retry không sửa khoản tiền đã commit | 1 |
| **Tổng** | **13** |

Các bài kiểm tra sử dụng database và thư mục trace tạm. Riêng kiểm thử rò rỉ đưa cả dữ liệu nhạy cảm giả lập vào ticket rồi kiểm tra kết quả, trace và stdout/stderr, thay vì chỉ kiểm tra các khóa trong handoff.

## 4. Bằng chứng

Commit triển khai chính: [`a27e3c9`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/a27e3c9a7792a8fb16cc57976746ba7beeb0bc21) — `Implement orchestrator with safe handoff and integration tests`. Commit gồm hai file `src/lab8/shapes/orchestrator.py` và `src/tests/test_orchestrator_handoff.py`.

Các lệnh dưới đây chạy trong thư mục `src/`:

```bash
python -m pytest -q -m student -o addopts= -k orchestrator
python -m pytest -q
```

| Bộ kiểm thử | Kết quả |
| --- | --- |
| Ma trận student của orchestrator, gồm T01–T14 | 62 passed, 253 deselected |
| Bộ test host mặc định, bao gồm 13 trường hợp bổ sung | 67 passed, 248 deselected |

Tôi đã trực tiếp chạy hai lệnh này và nhận được kết quả trên. Số `deselected` là những test được lọc ra theo marker và tên test, không phải test thất bại. Hai hàng trong bảng có phạm vi khác nhau; 13 trường hợp bổ sung đã nằm trong 67 test host.

Một số test thể hiện trực tiếp yêu cầu của phần việc:

- `test_orchestrator_handoff_gives_worker_only_read_tools`: kiểm tra payload được chuyển qua ranh giới và ledger trước, sau khi investigator chạy.
- `test_orchestrator_untrusted_ticket_cannot_leak_or_grant_write_tools`: kiểm tra ticket không thể cấp quyền ghi hoặc làm lộ dữ liệu nhạy cảm.
- `test_orchestrator_crash_propagates_and_resume_pays_once`: kiểm tra crash thực sự xảy ra và không phát sinh khoản hoàn thứ hai khi resume.
- `test_orchestrator_changed_quote_on_retry_keeps_committed_amount`: kiểm tra xung đột số tiền khi gọi lại.

## 5. Công cụ AI đã dùng

Tôi sử dụng Codex để hỗ trợ đọc cấu trúc project, đối chiếu luật nghiệp vụ và contract, viết phần triển khai orchestrator, xây dựng các test handoff và rà soát thay đổi sau khi tích hợp workflow của thành viên khác.

Kết quả do công cụ đề xuất được kiểm tra bằng pytest và đối chiếu với ledger trong các test. Tôi trực tiếp chạy lại bộ test student của orchestrator và bộ test host trên môi trường của mình. Phần mô phỏng model trong chương trình vẫn dùng MockLLM của lab; số tiền hoàn và quyền ghi do code kiểm soát. Các file policy, durability, metrics, config và dữ liệu public được giữ nguyên.

## 6. Tự đánh giá

Phần đóng góp của tôi đáp ứng các yêu cầu triển khai và kiểm thử của orchestrator trên bộ public. Điểm tôi chú trọng là ranh giới quyền của investigator và tính nhất quán giữa kết quả trả về với ledger. Việc tách hai trách nhiệm này giúp kiểm tra được bên nào thu thập dữ kiện, bên nào đề xuất khoản hoàn và bên nào thực sự ghi tiền.

Qua bài lab, tôi rút ra rằng chia hệ thống thành nhiều agent không tự giải quyết vấn đề độ tin cậy. Nếu chuyển nguyên context cho investigator hoặc tin số liệu trong ticket, hệ thống vẫn có thể sai dù có thêm bước điều phối. Trong trường hợp này, giới hạn tool, dùng dữ kiện có cấu trúc và giữ thao tác ghi trong host là những phần quyết định tính đúng của kết quả.

Giải pháp có giới hạn rõ ràng: trình tự điều phối được quy định bằng Python, lời gọi MockLLM cho bước `plan` chưa tạo ra kế hoạch động và kết quả model không quyết định tool hay số tiền. Vì vậy, bài làm cho thấy cách tổ chức luồng orchestrator–investigator trong môi trường mô phỏng, chưa đủ để đánh giá khả năng suy luận, độ trễ hoặc hiệu quả của một hệ thống dùng model thật. Khi mở rộng, cần giữ các ràng buộc về quyền truy cập và ghi tiền, đồng thời đo chi phí và độ chính xác trên cùng điều kiện với các kiến trúc còn lại.
