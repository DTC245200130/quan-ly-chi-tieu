# Sơ đồ Use Case cho tài liệu SRS chuẩn

- Nguồn nội dung: tài liệu `03_GenAI_SoftwareDevelopment_requirements-specification_updated (1).docx`, quyết định RQ-009 và mã hiện tại của luồng đăng nhập/đăng xuất.
- Tác nhân chính: **Người sử dụng**, đại diện cá nhân tương tác trước và sau xác thực.
- Tác nhân ngoài: **Google Gemini** cho UC012 và **Resend** cho UC004.
- Thay đổi định danh: UC002 chỉ còn Đăng nhập; UC003 là Đăng xuất; các use case cũ UC003–UC011 tăng một số thành UC004–UC012.
- Danh sách tổng quan giữ nguyên tên 11 use case ban đầu; thay đổi duy nhất về cấu trúc là tách UC002 thành Đăng nhập và UC003 Đăng xuất, tổng cộng 12 use case.
- Không đặt khối chú thích trong sơ đồ tổng quan; phần giải thích nằm trong nội dung SRS.
- UC003 phản ánh hiện trạng frontend: xóa token/thông tin phiên trên thiết bị và chuyển về màn hình đăng nhập; tài khoản cùng dữ liệu vẫn được giữ nguyên, không có endpoint logout phía máy chủ.
- Toàn bộ actor trong các sơ đồ SRS được chuẩn hóa thành **Người sử dụng**; không còn actor Khách. Các SVG chi tiết cũ được đồng bộ ID UC004–UC012 khi tạo DOCX. Văn bản soạn thảo dùng Times New Roman 13; chữ trong ảnh UML dùng Arial.
- Phần phân rã gồm 5 sơ đồ độc lập theo nhóm use case có liên quan: Tài khoản; Danh mục và giao dịch; Ngân sách và mục tiêu tiết kiệm; Dashboard và báo cáo; Trợ lý AI. Mỗi sơ đồ đặt tác nhân chính ngoài biên hệ thống và thể hiện các quan hệ nghiệp vụ trong nhóm. Quan hệ khái quát hóa nối chức năng chuyên biệt về use case cấp cao; `«include»` chỉ biểu diễn hành vi bắt buộc được tách dùng chung, còn `«extend»` chỉ biểu diễn luồng tùy chọn có điều kiện.
- Kiểm tra logic: activity/sequence Đăng nhập tách khỏi Đăng xuất; activity có swimlane Người sử dụng/Hệ thống; sequence Đăng xuất không trình bày `user = null` mà dùng khái niệm phiên đăng nhập và nêu rõ tài khoản/dữ liệu vẫn tồn tại.
- Quyết định RQ-010: UC004 Khôi phục mật khẩu dành cho trường hợp chưa đăng nhập và bao gồm bước đặt mật khẩu mới trong cùng luồng; Đổi mật khẩu khi đã đăng nhập là chức năng con của UC005 Quản lý hồ sơ, không tạo use case tổng quan riêng.
- Quyết định RQ-011: Xóa tài khoản là chức năng con `UC005e` của UC005, không tạo use case tổng quan thứ 13. Luồng mục tiêu yêu cầu mật khẩu hiện tại và chuỗi xác nhận chính xác, hard delete dữ liệu active trong một transaction, dọn avatar idempotent sau commit và xóa dữ liệu client sau khi thành công. Thiết kế này chưa được xem là đã triển khai.
- Sơ đồ phân rã Tài khoản, Activity UC005 và Sequence UC005 đã được cập nhật theo RQ-011. PNG/SVG được render bằng PlantUML 1.2026.8 với Graphviz 2.44.1; ảnh được kiểm tra trực quan trước khi chèn Word ở chiều rộng tối đa 16 cm.
