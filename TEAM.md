# Team

## Thông tin nhóm

- Tên nhóm: C5
- Lớp: L3B
- Repo nhóm: K5-L3B-DAY08-C5-FromWorkflowsToAgents
- URL repo, nhánh nộp, commit chốt:
- URL: [https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents)
  Branch: Main
  Commit: Last Update Lab 8 - L3B - C5

## Thành viên

| STT | Họ tên              | MSSV        | Email                                                            | GitHub       | Vai trò                               |
| --: | --------------------- | ----------- | ---------------------------------------------------------------- | ------------ | -------------------------------------- |
|   1 | Quyến                | 2A202603769 | [26ai.quyendv2@vinuni.edu.vn](mailto:26ai.quyendv2@vinuni.edu.vn) | dvq2609      | workflow                               |
|   2 | Công                 | 2A202603789 | [26ai.congnt3@vinuni.edu.vn](mailto:26ai.quyendv2@vinuni.edu.vn)  | congnt180263 | single agent                           |
|   3 | Đinh Phúc Diên     | 2A202603876 | 26ai.diendp@vinuni.edu.vn                                        | dinhphucdien179             | Task 3 — Orchestrator, handoff và kiểm thử tích hợp |
|   4 | Lê Nguyễn Anh Khôi |  2A202603755 |  26ai.khoilna@vinuni.edu.vn                                                                |    KN-16          | Task 4 — An toàn và độ bền       |
|   5 | Lê Nguyễn Anh Nhân       | 2A202603838 | 26ai.nhanlna@vinuni.edu.vn | ying684 | Task 5 — Đánh giá và đối chiếu |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người               | Vai                                           | Commit                                                                                                                                                                                                                                                                        | Test đã thêm hoặc sửa                                                                                                                                        |
| --------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Đồng Văn Quyến    | workflow                                      | dda1beb                                                                                                                                                                                                                                                                       | tests/test\_workflow\_extra.py                                                                                                                                    |
| Nguyễn Thành Công  | Single agent                                  | [**feat(single-agent): complete shape B react loop and add react unit tests**](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/d28abb772bdc3bba41fb103650cfe77cca3a6a8f "feat(single-agent): complete shape B react loop and add react unit tests") | test/test\_single\_react.py                                                                                                                                       |
| Đinh Phúc Diên | Task 3: triển khai orchestrator; handoff chỉ đọc; trace; xử lý approval, crash và retry qua host; báo cáo cá nhân và tích hợp | [`a27e3c9`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/a27e3c9a7792a8fb16cc57976746ba7beeb0bc21) (code và test); `31628d8` (báo cáo cá nhân); `a67e869` (thông tin thành viên) | [src/tests/test_orchestrator_handoff.py](src/tests/test_orchestrator_handoff.py) — 13 trường hợp; kiểm tra shape bằng 62 test public có sẵn trong `src/tests/test_public_matrix.py` |
| Lê Nguyễn Anh Khôi | Task 4: approval, idempotency, crash, privacy | [`7b717a2`](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents/commit/7b717a28af5de404670e74378ec42289e04eb894) — triển khai test và exporter; `c839111` — cập nhật bằng chứng an toàn và báo cáo cá nhân | `src/tests/test_task4_authorization.py`, `src/tests/test_task4_durability.py`, `src/tests/test_task4_privacy.py`, `src/tests/test_task4_report_export.py` — tổng 234 test |
| Lê Nguyễn Anh Nhân | Task 5: test biên, benchmark, đối chiếu | `fc6128a` (code/test và bằng chứng ban đầu); `a18fcd6` (bản task 5 trong lịch sử nhóm, cùng code); `d1faaa7` (tích hợp main); `3e4522a` (đồng bộ thông tin) | `src/tests/test_task5_rules.py`, `src/tests/test_task5_shapes.py`, `src/tests/test_task5_comparison.py` — tổng 465 test |
