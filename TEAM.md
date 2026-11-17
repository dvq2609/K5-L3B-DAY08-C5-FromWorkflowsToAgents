# Team

## Thông tin nhóm

- Tên nhóm: C5
- Lớp: L3A
- Repo nhóm: K5-L3B-DAY08-C5-FromWorkflowsToAgents
- URL repo, nhánh nộp, commit chốt:
- URL: [https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents](https://github.com/dvq2609/K5-L3B-DAY08-C5-FromWorkflowsToAgents)
  Branch: Main
  Commit: Finish lab 08

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Quyến  | 2A202603769 |       |        |         |
|   2 |  Công  | 2A202603789 |       |        |         |
|   3 |        |      |       |        |         |
|   4 |        |      |       |        |         |
|   5 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

### Đóng góp cụ thể

### Bằng chứng

## 2A202603876_DinhPhucDien — Đinh Phúc Diên

### Phần việc phụ trách

Kiến trúc C — orchestrator và investigator; giới hạn quyền qua handoff, kết nối luồng xử lý claim với host, kiểm thử tích hợp và báo cáo cá nhân.

### Đóng góp cụ thể

- Hoàn thiện [src/lab8/shapes/orchestrator.py](src/lab8/shapes/orchestrator.py), giữ nguyên chữ ký `run_claim` và xử lý các trạng thái `failed`, `needs_info`, `escalated`, `denied`, `resolved` theo contract. Kết quả được tạo bằng `finish()` để phản ánh ledger và audit thực tế.
- Tạo handoff `handoff.v1` bằng `make_handoff`; investigator chỉ có `lookup_order`, `lookup_policy`, `lookup_refund_history`. Không chuyển nguyên claim, ticket, secret hay header qua handoff; nội dung ticket không được cấp thêm quyền cho investigator.
- Tính quote từ dữ liệu đơn hàng có cấu trúc bằng `compute_compensation`; gửi quote đầy đủ cho host kiểm tra approval và trần hoàn theo đơn. Giữ đúng `proposal_amount` khi host cap số tiền hoặc từ chối, và trả `failed` khi retry có xung đột số tiền.
- Truyền `crash_at` tới `issue_refund` và để `InjectedCrash` truyền ra ngoài. Ghi trace khi crash, đóng connection trong `finally` và dùng cơ chế idempotency có sẵn của host khi resume.
- Ghi trace gồm handoff đã sanitize, tóm tắt investigator, quote, yêu cầu refund và quyết định. Các nhánh trả về sớm vẫn có trace; không ghi nguyên bản ghi đơn hàng hoặc ticket vào trace.
- Bổ sung [src/tests/test_orchestrator_handoff.py](src/tests/test_orchestrator_handoff.py) với 13 trường hợp: giới hạn quyền và thao tác của investigator; ticket chứa chỉ dẫn giả và dữ liệu nhạy cảm; claim hoặc đơn không hợp lệ; approval thiếu hoặc sai claim; ba điểm crash; retry với quote thay đổi. Kiểm thử rò rỉ kiểm tra cả kết quả, trace và stdout/stderr.
- Kiểm tra orchestrator trên 62 test student của bộ public, gồm retry T11, crash T12 và trần hoàn theo đơn T13–T14. Đối chiếu khả năng tích hợp với workflow khi cập nhật nhánh từ `main`.
- Viết [báo cáo cá nhân](report/team/2A202603876_DinhPhucDien.md), trình bày cách triển khai, quyết định kỹ thuật, kết quả kiểm thử, việc sử dụng Codex và giới hạn của giải pháp; bổ sung thông tin thành viên trong `TEAM.md`.

### Bằng chứng

| Nội dung | Commit hoặc bằng chứng |
| --- | --- |
| Triển khai orchestrator và thêm 13 trường hợp kiểm thử | `a27e3c9` — `Implement orchestrator with safe handoff and integration tests` |
| Tích hợp workflow từ `main` vào nhánh cá nhân | `e545187` — merge `origin/main` vào `DinhPhucDien` |
| Báo cáo cá nhân | `31628d8` — thêm `report/team/2A202603876_DinhPhucDien.md` |
| Cập nhật thông tin thành viên | `a67e869` — bổ sung họ tên, MSSV và email trong `TEAM.md` |
| Tích hợp code, test và báo cáo vào `main` | PR #2, merge commit `3404695` |
| Tích hợp cập nhật thông tin thành viên vào `main` | PR #4, merge commit `bcf314c` |
| Kết quả riêng của orchestrator trong benchmark chung | [src/reports/benchmark.json](src/reports/benchmark.json): 70/70 trial public đạt, pass rate 1.000, pass^5 1.000, seed variance 0; số liệu do phần đánh giá của nhóm tổng hợp |

Lệnh kiểm tra phần việc của Diên, chạy trong `src/`:

```bash
python -m pytest -q tests/test_orchestrator_handoff.py
python -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k orchestrator
```

Hai bộ kiểm tra lần lượt có 13 và 62 trường hợp. Bộ 13 trường hợp do Diên bổ sung; 62 trường hợp public là bộ test có sẵn của đề được dùng để xác nhận shape.
