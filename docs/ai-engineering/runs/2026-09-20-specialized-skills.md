# Skill UML và quy trình coding — 20/09/2026

Yêu cầu: bổ sung skill UML từ nhận diện loại/ký hiệu đến mã và ảnh dùng trong Word; tổ chức coding theo yêu cầu từng prompt và phạm vi sửa đổi, không tạo bộ skill cho mọi tác vụ coding.

Kết quả: thêm uml-diagrams với references notation và render-word; nâng cấp implementation tại chỗ, giữ tên và liên kết; nối documentation/architecture-design với UML; thêm AIP-UML-001, cập nhật AIP-IMPL-001 và mapping vai trò. Không sửa SRS, sơ đồ sản phẩm, application code hoặc database.

Nguồn quy tắc UML: OMG UML 2.5.1 và tài liệu PlantUML được dẫn trong references. Kích thước Word, cỡ chữ và đường dẫn lưu là quy ước nội bộ có thể điều chỉnh theo mẫu người dùng, không phải tiêu chuẩn UML.

Kiểm chứng self-review: quick_validate.py PASS cho 4 skill mới/sửa; 33 đích liên kết local được kiểm tra tồn tại; git diff --check PASS. Chưa chạy AE-10 đến AE-14, chưa render ảnh, chưa kiểm tra Word. Kiểm tra PATH không tìm thấy java, plantuml, dot; chưa kết luận máy không có bản cài ở vị trí khác. Không cài renderer hoặc gọi dịch vụ render công cộng trong tác vụ xây dựng skill.

Giới hạn: kiểm tra cấu trúc không chứng minh skill đã đạt chất lượng hành vi; lần tạo sơ đồ thực tế cần chạy đủ render và kiểm tra đọc trong Word theo skill.
