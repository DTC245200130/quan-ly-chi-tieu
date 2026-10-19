# Yêu cầu khách hàng — Sổ Chi Tiêu

> Trạng thái: đã được Đào Minh Tâm phê duyệt tại Requirements Gate ngày 06/09/2026.

Xây dựng ứng dụng quản lý tài chính cá nhân bằng tiếng Việt, chạy trên web/PWA và Windows. Người dùng có tài khoản riêng để quản lý danh mục thu/chi, giao dịch, ngân sách tháng và mục tiêu tiết kiệm; xem dashboard và báo cáo; nhận phân tích tham khảo từ trợ lý Gemini dựa trên dữ liệu tổng hợp, không gửi giao dịch thô hoặc danh tính cho AI.

Hệ thống cần bảo vệ dữ liệu giữa các tài khoản, lưu mật khẩu an toàn, hỗ trợ đặt lại mật khẩu, triển khai được với PostgreSQL và giữ SQLite cho phát triển. Web và ứng dụng cài đặt hiện đều yêu cầu kết nối Internet cho toàn bộ chức năng. Khả năng offline không thuộc phạm vi hiện tại và chỉ được xem xét sau dựa trên phản hồi sử dụng thực tế. Đây không phải ứng dụng thực hiện giao dịch ngân hàng hay cung cấp lời khuyên tài chính mang tính quyết định.
