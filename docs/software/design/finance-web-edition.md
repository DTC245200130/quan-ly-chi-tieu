# Giao diện web phục vụ đề tài quản lý chi tiêu cá nhân

Phiên bản này giới hạn chức năng web ở bốn trang: Tổng quan, Giao dịch,
Danh mục và Báo cáo. Đăng nhập, đăng ký, khôi phục mật khẩu và hồ sơ cá nhân
vẫn phục vụ quản lý tài khoản.

## Thiết kế

- Điều hướng ngang, hiển thị cả bốn mục trên desktop và điện thoại.
- Nền xám sáng, bề mặt trắng, điểm nhấn indigo; hỗ trợ chế độ tối.
- Tổng quan gồm số liệu thu/chi, số dư, cơ cấu chi theo danh mục, xu hướng
  ba tháng, giao dịch gần đây và liên kết báo cáo.
- Các trang giao dịch, danh mục và báo cáo dùng chung bộ màu, bề mặt và
  điều khiển mới trong `frontend/src/finance.css`.
- Đường dẫn cũ /budgets, /goals và /assistant chuyển về /dashboard.

## Phạm vi dữ liệu

Thay đổi này giới hạn các màn hình web. Các bảng, migration và API ngân sách,
mục tiêu, AI vẫn giữ nguyên để bảo toàn dữ liệu hiện có và khả năng tương
thích. Không cần migration database khi triển khai phiên bản giao diện này.

## Kiểm tra và chạy trên Linux

```bash
cd frontend
npm ci
npm test
npm run build
cd ..
docker compose up -d --build
```

Dockerfile vẫn build frontend và để FastAPI phục vụ các tệp tĩnh.
Các kiểm thử route xác nhận bốn trang được giữ lại, các trang đã bỏ chuyển
về Tổng quan, hồ sơ cá nhân và đăng xuất vẫn hoạt động.

Tài liệu này mô tả phiên bản web hiện tại; các mô tả sidebar, ngân sách,
mục tiêu và trợ lý AI trong DESIGN.md là thiết kế của phiên bản đầy đủ trước đó.
