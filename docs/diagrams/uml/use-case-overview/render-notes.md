# Use Case tổng quan

- Loại/trạng thái: UML Use Case, baseline yêu cầu đã chốt theo RQ-009; không tuyên bố toàn bộ use case đã được implementation đáp ứng.
- Nguồn: `FR-AUTH-001..003`, `FR-CAT-001`, `FR-TXN-001`, `FR-BUD-001`, `FR-GOAL-001`, `FR-DASH-001`, `FR-REP-001`, `FR-AI-001..002`, `FR-DATA-001` và `RQ-009`.
- Tác nhân chính: **Người sử dụng** cho tương tác trước và sau đăng nhập; không tách lại thành Khách/Người dùng.
- Tác nhân ngoài hệ thống: **Google Gemini** tham gia use case hỏi trợ lý tài chính; **Resend** tham gia use case khôi phục mật khẩu. Hai actor này có bằng chứng trực tiếp tại `app/core/gemini.py`, `app/core/email.py` và các router gọi tương ứng. PostgreSQL/avatar storage/backup là hạ tầng lưu trữ, không phải vai trò tương tác trong use case diagram này.
- Quyết định mô hình: không dùng quan hệ `«include» Đăng nhập` cho mọi use case bảo vệ. Các giải thích được để ngoài sơ đồ tổng quan để hình gọn hơn.
- Phạm vi chỉnh sửa: giữ nguyên 11 use case ban đầu; chỉ tách use case “Đăng nhập và đăng xuất” thành `Đăng nhập` và `Đăng xuất`, nên sơ đồ sau chỉnh sửa có đúng 12 use case. Không bổ sung `Xóa tài khoản và dữ liệu cá nhân` hoặc `Quản lý lịch sử hội thoại` thành use case độc lập trong sơ đồ tổng quan.
- Renderer: PlantUML 1.2026.8, OpenJDK 21.0.12.1, Graphviz 2.44.1. Render local bằng `scripts/render_uml.ps1`; PNG 2300 × 4096 px và SVG được tạo thành công.
- Kích thước chèn dự kiến: tối đa 16 cm theo chiều rộng trong Word, giữ nguyên tỉ lệ; nên đặt trên trang riêng vì sơ đồ có hướng dọc.
- Kiểm tra trực quan: PASS — actor chính và hai actor ngoài đều nằm ngoài system boundary, association nối đúng use case, không có `«include» Đăng nhập`, nhãn tiếng Việt và đường liên kết không bị cắt.
