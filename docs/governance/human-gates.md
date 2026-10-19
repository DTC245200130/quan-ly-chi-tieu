# Human verification gates

AI không được tự đánh dấu `APPROVED`. Người duyệt điền tên, ngày, quyết định và ghi chú.

| Gate | Artifact cần kiểm | Trạng thái | Người duyệt | Ngày |
|---|---|---|---|---|
| Requirements | customer requirement, requirements, stories, AC, issues | APPROVED | Đào Minh Tâm | 06/09/2026 |
| Architecture | architecture, decisions, traceability | APPROVED | Đào Minh Tâm | 06/09/2026 |
| Database | database design, model/migration gaps | APPROVED | Đào Minh Tâm | 06/09/2026 |
| Release | test report, code review, security review | PENDING | — | — |

Quy tắc: chỉ đổi trạng thái thành `APPROVED` sau khi con người kiểm tra; nếu `CHANGES_REQUESTED`, ghi quyết định và artifact phải sửa bên dưới bảng.

## Requirements Gate — quyết định

Baseline v1.1 được phê duyệt với các quyết định RQ-001 đến RQ-008 ghi tại `docs/software/requirements/requirements-issues.md`. RQ-008 đã được sửa: web và ứng dụng cài đặt online toàn bộ; offline là backlog có điều kiện dựa trên phản hồi người dùng. Phê duyệt yêu cầu không đồng nghĩa xác nhận implementation hiện tại đã đáp ứng; xóa tài khoản, timezone/rounding và tiêu chí vận hành vẫn phải được xử lý ở các gate tiếp theo.

Đào Minh Tâm chốt bổ sung RQ-011 ngày 26/09/2026: xóa tài khoản là chức năng con `UC005e` của UC005; lệnh xóa yêu cầu mật khẩu hiện tại và xác nhận chính xác `XÓA TÀI KHOẢN` trong cùng request. Quyết định này cho phép cập nhật thiết kế và triển khai sau đó, nhưng không xác nhận endpoint, migration, retention automation hoặc kiểm thử đã hoàn thành.

## Architecture Gate — quyết định

Đào Minh Tâm phê duyệt ngày 06/09/2026: web và ứng dụng cài đặt online toàn bộ; offline ngoài phạm vi hiện tại; các client dùng chung FastAPI và database máy chủ; payload Gemini được tối thiểu hóa và truyền qua HTTPS; dữ liệu backup của tài khoản đã xóa được giữ tối đa 30 ngày. Database và Release Gate chưa được phê duyệt.

## Database Gate — quyết định

Đào Minh Tâm phê duyệt ngày 06/09/2026: cấm category trùng tên trong cùng loại của một người dùng, không phân biệt hoa thường; năm ngân sách 2000–2100; migration phải dừng và báo cáo khi gặp dữ liệu trùng/xung đột; xóa tài khoản bằng hard delete dữ liệu active và backup hết retention trong tối đa 30 ngày. Phê duyệt này cho phép bước implementation lập migration mới, nhưng không khẳng định migration/code đã tồn tại hoặc đã được kiểm thử.
