# Class Diagram — As-built

- Loại/trạng thái: UML Class Diagram phản ánh cấu trúc ORM và vị trí hàm xử lý trong mã hiện tại.
- Nguồn: `app/models/*.py`, `app/routers/auth.py`, `app/routers/categories.py`, `transactions.py`, `budgets.py`, `goals.py`, `dashboard.py`, `reports.py`, `assistant.py`; quyết định RQ-009.
- Phạm vi: 9 entity ORM và các module router liên quan. Các module được biểu diễn bằng stereotype để không biến hàm module thành phương thức entity.
- Quyết định RQ-009: `User` giữ dữ liệu tài khoản đã đăng ký và tồn tại sau đăng xuất; thao tác xác thực nằm tại `AuthRouter`. Không tạo service hoặc migration mới.
- Renderer: PlantUML 1.2026.8, OpenJDK 21.0.12.1, Graphviz 2.44.1. Render local bằng `scripts/render_uml.ps1`; bản đầy đủ 4096 × 3465 px, bản Word 3848 × 1602 px; PNG và SVG đều được tạo thành công.
- Kích thước chèn dự kiến: trang A4 ngang, tối đa 24.7 cm theo chiều rộng, giữ nguyên tỉ lệ.
- `class-as-built-word.*` là bản tổng quan ít chi tiết để chèn rộng 16 cm trong tài liệu A4 dọc; đặc tả thuộc tính/thao tác đầy đủ nằm trong các bảng của tài liệu.
- Kiểm tra trực quan: PASS — `User` không có hàm xác thực, dependency từ `AuthRouter` đúng hướng, multiplicity và nhãn không bị cắt. Bản Word đã được xuất PDF bằng Microsoft Word và kiểm tra trang chứa hình.
