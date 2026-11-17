# Báo cáo cá nhân — 2A202603838_LeNguyenAnhNhan

## 1. Thông tin thành viên

- Họ tên theo thông tin cung cấp: LeNguyenAnhNhan (Anh Nhân).
- MSSV: 2A202603838.
- Email: nguyenanhnhan161@gmail.com.
- GitHub: chưa cung cấp.

## 2. Phần việc phụ trách

Task 5 — đánh giá và đối chiếu: test policy cũ/tương lai, ticket sai lệch và trần hoàn theo đơn; chạy benchmark bốn shape, phân tích và soạn bảng so sánh.

## 3. Đóng góp cụ thể

- Thêm `src/tests/test_task5_rules.py`: 20 test độc lập, đáp án tính từ luật.
- Thêm `src/tests/test_task5_shapes.py`: 440 test tích hợp (22 ca × bốn shape × năm seed).
- Thêm `src/tests/test_task5_comparison.py`: 5 test cho việc tạo bảng và bảo toàn JSON đầu vào.
- Thêm `src/scripts/task5_comparison.py`: tạo bảng Markdown, ghi hash nguồn và run id dẫn chứng.
- Chạy benchmark chính thức sau tích hợp task 1–3, đối chiếu lần chạy lại giống byte; phân tích và đề xuất workflow tại `task5_evaluation.md`.
- Quyết định kỹ thuật: không skip/xfail stub; tách hai negative control swarm khỏi kết quả đúng nghiệp vụ; giữ proposal đầy đủ và kiểm ledger/audit thật.
- Commit phần task 5: **chưa tạo**; thay bằng hash thật trước nộp. Commit nền được đánh giá là `340469524960230dc5857a4e8e2623ed84b635af` (đã đủ ba shape nhóm).

## 4. Bằng chứng

- [Báo cáo đánh giá và lệnh tái lập](task5_evaluation.md).
- [Bảng benchmark sinh tự động](task5_comparison.md), nguồn `src/reports/benchmark.json`.
- Host gate sau tích hợp: 100 pass; test luật/renderer mới: 25 pass.
- Toàn bộ student: 688 pass; riêng test tích hợp task 5 có 440 pass. Không có fail/skip/xfail. Test xanh bao gồm các negative control của swarm, không nghĩa swarm đúng trên mọi trial benchmark.
- Crash CLI chính thức: 20/20; file `src/reports/crash.json`.
- Lần rà cuối: `python -m pytest -q -o addopts= --basetemp=.venv/tmp/final-task5-review --tb=short` cho 788 pass. Benchmark và crash chạy lại khớp từng byte với JSON bằng chứng. Đã dọn log tạm/spec/checklist riêng; lệnh tái lập và kết quả được giữ trong báo cáo đánh giá.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc repo/phân công, viết spec/plan/tasks, đề xuất ca biên, tạo test và script báo cáo, chạy kiểm chứng. Kết quả được kiểm bằng pytest, evaluator chính thức đối chiếu ledger/audit/trace, benchmark CLI và chạy lại so byte/hash JSON. Không sửa thước đo hoặc nhập tay JSON để đạt ngưỡng.

Trước nộp, thành viên cần tự chạy lại và giải thích được: policy có hiệu lực, ticket không quyết định tiền, proposal khác effect, vì sao top-up không trừ hai lần, và vì sao test negative control xanh không phải swarm đúng. Chưa ghi nhận thành viên đã tự thực hiện bước này.

## 6. Tự đánh giá

**Chờ thành viên tự điền** sau khi đọc code, chạy lại kiểm chứng và tích hợp kết quả nhóm. Không dùng AI để bịa phần tự đánh giá.
