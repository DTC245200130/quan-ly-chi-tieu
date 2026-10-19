# Đặc tả yêu cầu

> Baseline v1.1 được Đào Minh Tâm điều chỉnh và phê duyệt tại Requirements Gate ngày 06/09/2026. Một số yêu cầu chưa được implementation hiện tại đáp ứng; xem `docs/software/requirements/requirements-issues.md`.

## Yêu cầu chức năng

- **FR-AUTH-001:** Người dùng đăng ký, đăng nhập và xem/cập nhật hồ sơ của chính mình.
- **FR-AUTH-002:** Người dùng yêu cầu và sử dụng liên kết đặt lại mật khẩu có thời hạn.
- **FR-AUTH-003:** Username và email được so khớp không phân biệt chữ hoa/chữ thường.
- **FR-CAT-001:** Người dùng CRUD danh mục thu/chi của chính mình.
- **FR-TXN-001:** Người dùng CRUD và lọc giao dịch của chính mình.
- **FR-BUD-001:** Người dùng CRUD ngân sách theo danh mục chi và tháng; hệ thống tính số đã chi/vượt mức.
- **FR-GOAL-001:** Người dùng CRUD mục tiêu và hạng mục, nạp/rút tiền, xem lịch sử và hoàn thành mục tiêu.
- **FR-DASH-001:** Hệ thống tổng hợp dashboard theo kỳ từ dữ liệu của người dùng hiện tại.
- **FR-REP-001:** Hệ thống tạo báo cáo so sánh thu/chi theo kỳ và danh mục.
- **FR-AI-001:** Người dùng hỏi trợ lý về tài chính cá nhân và quản lý lịch sử hội thoại của chính mình.
- **FR-AI-002:** Trợ lý chỉ nhận dữ liệu tổng hợp/ẩn danh, kèm kỳ, bằng chứng và mức tin cậy; không sửa dữ liệu.
- **FR-DATA-001:** Lịch sử hội thoại được giữ lại; người dùng có thể chủ động xóa toàn bộ tài khoản và dữ liệu cá nhân của chính mình.
- **FR-REL-001:** Backend cung cấp health/readiness và phục vụ web build; sản phẩm hỗ trợ kênh web/PWA và ứng dụng cài đặt.
- **FR-CONN-001:** Phiên bản web và ứng dụng cài đặt yêu cầu kết nối Internet cho toàn bộ chức năng trong phạm vi phát hành hiện tại.

## Quy tắc nghiệp vụ

- **BR-001:** Trong cùng một tài khoản và cùng loại thu/chi, tên category sau khi trim không được trùng nhau khi so khớp không phân biệt hoa thường.
- **BR-002:** Năm ngân sách hợp lệ nằm trong khoảng 2000–2100.
- **BR-003:** Khi migration phát hiện identity collision, category/budget trùng hoặc dữ liệu xung đột, migration phải dừng và báo cáo; không tự sửa hay xóa dữ liệu người dùng.
- **BR-004:** Xóa tài khoản dùng hard delete cho dữ liệu active; dữ liệu trong backup hết retention trong tối đa 30 ngày.

## Yêu cầu phi chức năng

- **NFR-SEC-001:** Mọi dữ liệu nghiệp vụ phải được lọc theo người dùng đã xác thực; mật khẩu băm bằng bcrypt và token có hạn dùng.
- **NFR-SEC-003:** Khi access token hết hạn, phiên đăng nhập bị kết thúc và token không còn được chấp nhận.
- **NFR-SEC-002:** Secrets chỉ đến từ biến môi trường; không đưa khóa Gemini vào frontend/log/response.
- **NFR-PRIV-001:** Gemini không nhận danh tính, ghi chú, giao dịch thô, ID nội bộ hoặc tên danh mục do người dùng nhập.
- **NFR-PRIV-002:** Dữ liệu truyền giữa client, máy chủ và Gemini phải được mã hóa khi truyền. Dữ liệu gửi Gemini phải được tối thiểu hóa và loại bỏ định danh; Gemini vẫn phải giải mã nội dung tại đầu xử lý để tạo câu trả lời.
- **NFR-PRIV-003:** Sau khi xóa tài khoản, bản sao lưu chứa dữ liệu của tài khoản được giữ không quá 30 ngày rồi phải bị xóa theo vòng đời backup.
- **NFR-DATA-001:** Tiền dùng kiểu decimal; production dùng migration và PostgreSQL; SQLite được phép khi phát triển.
- **NFR-DATA-002:** Tiền tệ là Việt Nam đồng; giá trị hiển thị/tính toán theo quyết định nghiệp vụ được làm tròn đến một chữ số thập phân.
- **NFR-TIME-001:** Hệ thống dùng múi giờ Hà Nội (`Asia/Ho_Chi_Minh`); kỳ tháng kết thúc vào ngày cuối cùng của tháng theo múi giờ này.
- **NFR-REL-001:** Lỗi dịch vụ ngoài được chuyển thành thông báo ổn định, không lộ stack trace cho client.
- **NFR-REL-002:** Mục tiêu vận hành là gần 24/7; sự cố được xử lý trong vòng 24 giờ.
- **NFR-PERF-001:** Thao tác thông thường phản hồi trong dưới 10 giây ở tải vận hành bình thường; hệ thống hiện không đặt mục tiêu cho quy mô người dùng lớn.
- **NFR-TEST-001:** Backend, frontend và production build phải có bằng chứng chạy lại được.
- **NFR-UX-001:** Giao diện responsive, hỗ trợ bàn phím/focus và trạng thái loading/error.

## Ngoài phạm vi hiện được chứng minh

Kết nối ngân hàng, thanh toán, đầu tư tự động, thao tác dữ liệu bằng AI, hoạt động offline và phân quyền quản trị.

## Yêu cầu đã rút khỏi baseline

- **FR-OFF-001 (WITHDRAWN):** Hỗ trợ hầu hết thao tác app khi offline. Quyết định ngày 06/09/2026: chưa phát triển; chỉ đưa lại vào requirements khi dữ liệu phản hồi cho thấy có số lượng lớn người dùng yêu cầu.
