# Báo cáo cá nhân — 2A202603769 Đồng Văn Quyến

**Lab 8 — From Workflows to Agents: LogiX-VN**

## 1. Thông tin thành viên

- Họ tên: Đồng Văn Quyến
- MSSV: 2A202603769
- Email: 26ai.quyendv2@vinuni.edu.vn
- GitHub: dvq2609

## 2. Phần việc phụ trách

Tôi phụ trách shape A — workflow trong bài toán xử lý yêu cầu hoàn tiền. Phần việc gồm triển khai `run_claim` trong [workflow.py](../../src/lab8/shapes/workflow.py), bổ sung kiểm thử trong [test_workflow_extra.py](../../src/tests/test_workflow_extra.py), và đối chiếu kết quả với luật nghiệp vụ và contract của lab.

## 3. Đóng góp cụ thể

Workflow xử lý claim theo trình tự cố định bằng Python. Chương trình đọc claim qua `get_claim_view`; claim không tồn tại trả về `failed`, còn thiếu mã đơn trả về `needs_info`. Sau đó, `lookup_order` kiểm tra đơn có tồn tại và thuộc principal hay không; nếu không, kết quả là `escalated`.

Khi truy cập đơn hợp lệ, `compute_compensation` tính quote từ dữ liệu đơn và policy hiện hành, không lấy số ngày trễ từ ticket. Quote bằng 0 dẫn đến `denied` mà không gọi ghi refund. Với quote lớn hơn 0, workflow gọi `issue_refund` và chuyển **quote đầy đủ** cho host. Host chịu trách nhiệm kiểm tra approval, trần hoàn theo đơn và idempotency. Nếu đơn đã được hoàn trước đó, host tự trừ khoản đã hoàn; shape không trừ trước để tránh trừ hai lần.

Workflow dùng `finish()` để trả kết quả và ghi trace. Trace ghi quyết định cùng số tiền và lý do của quote khi có; không ghi toàn bộ claim, ticket hoặc thông tin nhạy cảm. Tham số `crash_at` được chuyển cho host; kết nối database được đóng trong `finally` và `InjectedCrash` không bị bỏ qua.

Commit triển khai workflow: [`dda1beb`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/dda1beb). File test bổ sung hiện cần được commit cùng các thay đổi liên quan.

Tổng hợp và hoàn thiện group report

## 4. Bằng chứng

Các lệnh chạy trong `src/`:

```bash
python -m pytest -q tests/test_workflow_extra.py
python -m pytest -q -m student -o addopts= -k workflow
```

File test bổ sung có **4 test pass**. Chúng kiểm tra ticket chứa yêu cầu giả và secret, approval thuộc claim khác, retry khi đơn đã được hoàn một phần, và trace khi claim không tồn tại. Bộ student của workflow đã chạy **62 test pass**; số test bị deselect có thể thay đổi khi nhóm bổ sung test khác.

Trên benchmark public của nhóm, workflow đạt 70/70 trial, pass rate 1.000, pass^5 1.000 và cost/success mô phỏng 27.86 VND. Bằng chứng nằm trong `src/reports/benchmark.json`; ví dụ run ID `R-workflow-C-001-s11`. Kết quả này giới hạn ở 14 claim public và 5 seed, không phải kết quả chấm hidden.

## 5. Công cụ AI đã dùng

Tôi sử dụng Codex để tìm hiểu cấu trúc repo và contract, hỗ trợ viết workflow, bổ sung test và soạn báo cáo. Kết quả được đối chiếu với code, luật nghiệp vụ và các lệnh pytest: tôi chạy bộ student của workflow và bộ test mặc định; Codex chạy file test bổ sung. Code của lab sử dụng MockLLM theo đề, còn số tiền hoàn và thao tác ghi do code và host kiểm soát.

## 6. Tự đánh giá

Qua phần workflow, tôi hiểu vì sao dữ liệu có cấu trúc và policy phải quyết định khoản hoàn, trong khi ticket chỉ là dữ liệu người dùng. Tôi cũng hiểu vai trò của host trong kiểm tra approval, trần hoàn và chống ghi trùng; việc truyền quote đầy đủ giúp host tính đúng phần còn được hoàn.

Bộ test public và test bổ sung cho thấy các trường hợp đã kiểm tra hoạt động đúng, nhưng không chứng minh mọi trường hợp hidden hoặc môi trường sản xuất đều an toàn. Tôi cần tiếp tục rà soát trace, kết quả crash và test sau khi nhóm tích hợp các thay đổi cuối cùng.
