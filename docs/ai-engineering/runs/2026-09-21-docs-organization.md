# Sắp xếp docs — 21/09/2026

Yêu cầu: tối ưu docs sau khi phân biệt phần mềm truyền thống và AI Engineering.

Đã chuyển 26 tài liệu Markdown vào software/requirements, software/design, software/testing, software/deployment, governance và ai-engineering/history; user-guide ở software, thư viện prompt cũ ở ai-engineering. diagrams/outputs và toàn bộ artifact nhị phân giữ nguyên. Tạo docs/README.md làm mục lục và quy ước lưu.

Nội dung nghiệp vụ và trạng thái lịch sử được giữ, chỉ chuẩn hóa đường dẫn. Cập nhật tham chiếu trong README, skills, agent, context/prompt; compose.azure.yaml chỉ đổi đường dẫn tài liệu trong chú thích, tools/update_live_testing_word.py chỉ đổi chuỗi đường dẫn báo cáo trong evidence. Không thay hành vi ứng dụng, database hoặc pipeline thực thi.

Kiểm chứng: 212 liên kết Markdown nội bộ có đích tồn tại trước khi thêm bản ghi này; git diff --check PASS. Không chạy test/build sản phẩm vì thay đổi chỉ là tổ chức tài liệu và chuỗi tham chiếu. Việc chuyển tài liệu không xác nhận nội dung SRS, thiết kế hay kết quả test cũ đã được kiểm chứng lại.
