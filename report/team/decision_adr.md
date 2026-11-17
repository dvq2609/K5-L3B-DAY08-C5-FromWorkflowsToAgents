# Decision record

- Shape chọn: workflow
- Commit hash: fc6128a2dca3dd628519a5b0bcc948eaa7d1099f (commit task 5 chứa code/test và JSON bằng chứng; benchmark được chạy trên code nền 3404695). Bản code/test task 5 tương ứng trong lịch sử nhóm: a18fcd61bebcaef0692cacc09b646d81d634a620.
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: Các test public đã chạy thành công; chưa có kết quả chấm hidden, không khẳng định an toàn ngoài phạm vi kiểm thử.

## Vì sao shape này

Nhóm chọn workflow vì trên cùng 14 claim public và 5 seed 11, 22, 33, 44, 55, shape này đạt 70/70 trial, pass rate 1.000 và pass^5 1.000. Single và orchestrator cũng đạt 70/70, nhưng cost/success mô phỏng lần lượt là 29.86 và 57.12 VND, so với 27.86 VND của workflow. Swarm đạt 69/70, pass^5 0.929 và cost/success 49.57 VND. Dữ liệu và số liệu tổng hợp nằm trong `src/reports/benchmark.json`; run ID trên là một trial dẫn chứng, không phải ID của toàn bộ benchmark.

## Có đáng đổi lấy multi-agent không

Với bộ public hiện tại, thêm agent chưa cải thiện tỷ lệ thành công so với workflow và làm tăng chi phí mô phỏng. Nhóm sẽ cân nhắc lại nếu có bộ dữ liệu đại diện hơn cho thấy công việc có thể chia song song hoặc cần điều tra phức tạp, và multi-agent cải thiện kết quả đủ để bù chi phí và độ dao động, đồng thời vẫn đáp ứng các điều kiện an toàn.

## Trace và bằng chứng

Workflow ghi sự kiện `quote` với số tiền và lý do khi đã tính quote, và sự kiện `decision` với trạng thái và lý do ở các nhánh trả về. Trace không ghi toàn bộ claim, ticket, `parent_secret`, header, số điện thoại, địa chỉ, tên hàng hoặc ghi chú nội bộ. Trace được `finish()` ghi và trả qua `trace_path`; scanner kiểm tra file đó và các file cùng thư mục có tiền tố run ID. File hoặc stdout nằm ngoài phạm vi scanner không được chứng minh là sạch chỉ nhờ kết quả quét; cần kiểm tra thêm các đầu ra đó.

## Giới hạn

Kết quả trên chỉ phản ánh 14 claim public, năm seed, bảng giá mô phỏng và dữ liệu giả. Bộ hidden chưa được chấm trong bằng chứng này. MockLLM không phải model sản xuất và latency là `unavailable`; số tiền cost không phải hóa đơn API thực. Báo cáo crash có 20/20, nhưng không thay thế việc kiểm tra mọi tình huống ngoài bộ thử.
