# Review bảo mật theo ranh giới

Chọn phần liên quan, không tự chạy mọi scan hoặc thử tấn công production.

- Auth/session: lần theo tạo, kiểm tra, hết hạn, vô hiệu hóa token và reset token; kiểm tra replay/one-time và luồng lỗi trong fixture. Không mặc định client logout đồng nghĩa server revoke.
- Object authorization/API: account A/B, ID tài nguyên của B qua request A; kiểm tra read/write/delete/aggregate và file upload. Kiểm tra owner ở server, không tin user_id từ body.
- Upload: tên/path server tạo, giới hạn kích thước, định dạng nội dung và nơi phục vụ; metadata ownership; không dùng file phá hoại để thử ngoài môi trường được giao.
- AI privacy: kiểm tra payload thực tế sau lọc, dữ liệu giả nhận diện để xác minh bị loại; không suy ra an toàn từ tên hàm “anonymize”. Nội dung model trả về không tự cấp quyền mutation.
- Secrets/dependency: kiểm tra config mẫu và cơ chế truyền, chỉ ghi vị trí secret nếu phát hiện, không chép giá trị. Nếu tra advisory hoặc khuyến nghị bảo mật cập nhật, dùng nguồn chính thức và ghi ngày; không đánh giá “an toàn” chỉ từ version pin.

Mỗi phép kiểm tra nêu môi trường/phạm vi, expected/actual và giới hạn. Finding confirmed cần bằng chứng; review static không giả làm pentest hoặc chứng nhận tuân thủ.
