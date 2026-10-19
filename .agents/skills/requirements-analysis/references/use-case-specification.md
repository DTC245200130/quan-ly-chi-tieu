# Đặc tả use case và truy vết

Mỗi use case dùng ID hiện hữu nếu có, tên mục tiêu, actor, trigger, tiền điều kiện, hậu điều kiện thành công và bảo đảm tối thiểu khi thất bại. Tiền điều kiện là trạng thái đã có, không phải bước người dùng phải lặp mỗi lần.

Luồng chính đánh số hành động actor và phản hồi hệ thống ở mức nghiệp vụ; không trộn chi tiết framework. Luồng thay thế/ngoại lệ chỉ rõ xuất phát từ bước nào, điều kiện và điểm quay lại/kết thúc. Phân biệt nhập sai, hết phiên, không có quyền, lỗi dịch vụ và hủy thao tác khi liên quan.

Include/extend chỉ dùng đúng ngữ nghĩa; sơ đồ gọi uml-diagrams. Không coi CRUD luôn phải include nhau. Với RQ-009, actor Người sử dụng bao gồm trước/sau đăng nhập; USER là tài khoản tồn tại độc lập phiên.

AC dùng Given/When/Then hoặc diễn đạt tương đương kiểm chứng được; tránh “nhanh”, “dễ dùng” không có thước đo. Mapping requirement → use case/story → AC → test phải giữ ID và chỉ ra mục thiếu. Không tự thêm rule để lấp khoảng trống; nêu câu hỏi còn ảnh hưởng hành vi.

Tư vấn không mặc định viết đủ bốn tài liệu. Khi sửa SRS được giao, cập nhật đúng artifact chịu ảnh hưởng và giữ lịch sử quyết định.
