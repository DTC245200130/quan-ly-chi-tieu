---
name: uml-diagrams
description: Tạo, sửa và kiểm tra sơ đồ UML từ yêu cầu hoặc mã nguồn, sinh mã PlantUML và render ảnh đọc rõ trong Word; áp dụng cho use case, class, sequence, activity, state, component và deployment.
---

# Sơ đồ UML

Skill này xử lý mô hình, ký hiệu, bố cục và artifact hình ảnh. Documentation xử lý nội dung tài liệu; architecture-design xử lý quyết định thiết kế. Không thay đổi kiến trúc hoặc mã sản phẩm chỉ để khớp hình.

## 1. Xác định bài toán và loại sơ đồ

Đọc yêu cầu hiện tại và [context dự án](../../../docs/ai-engineering/context.md). Xác định câu hỏi sơ đồ cần trả lời, nguồn, người đọc, mức tổng quan/chi tiết và trạng thái **As-built / thiết kế mục tiêu / đề xuất**. Tên loại người dùng đưa ra là đầu vào; nếu không phù hợp mục đích, giải thích khác biệt trước khi chọn.

Đọc [ký hiệu và cách chọn loại](references/notation.md), tập trung phần của loại được chọn. Không gọi ERD, flowchart hoặc hình kiến trúc tự do là UML nếu dùng ký hiệu khác. Với UML ngoài các loại được hướng dẫn, đọc đặc tả OMG và tài liệu renderer tương ứng trước khi sinh.

Nếu nguồn và yêu cầu mâu thuẫn, ghi rõ; không tự bịa actor, lớp, phương thức hay quan hệ. Thiếu thông tin chỉ hỏi khi làm thay đổi ý nghĩa mô hình; lựa chọn bố cục thông thường có thể tự quyết định.

## 2. Lập mô hình trước bố cục

Liệt kê phần tử, quan hệ/hướng, multiplicity hoặc guard/message liên quan, cùng nguồn chứng minh. Đối chiếu thuật ngữ và ID với tài liệu. Với As-built, phương thức phải nằm ở thành phần thực sự triển khai; hàm module không tự biến thành phương thức entity.

Áp dụng RQ-009 khi nhiệm vụ liên quan đến actor/USER, đọc quyết định tại nguồn. Không mặc định include Đăng nhập cho use case cần xác thực. Không tự tạo service hoặc migration.

## 3. Chọn khổ trang, sinh và chạy mã

Đọc [quy trình render và Word](references/render-word.md) trước khi tạo artifact. Xác định chiều rộng và chiều cao khả dụng trước khi tăng số phần tử. Tách hình tổng quan và chi tiết nếu nội dung không đọc rõ trong một trang; giữ mapping để không mất phần tử/quan hệ.

Dùng mã PlantUML UTF-8 làm nguồn chỉnh sửa. Không vẽ UML bằng mô hình sinh ảnh hoặc tô nhãn thủ công lên ảnh raster. Tái sử dụng nguồn hiện có nếu đúng loại/công cụ; Mermaid hiện hữu có thể giữ khi biểu đạt đủ ký hiệu, không ép đổi định dạng vô ích.

Kiểm tra renderer sẵn có, sinh mã, thực thi, kiểm tra exit code và file mới. Thiếu công cụ thì báo rõ phần chưa render, giữ mã nguồn; không dùng ảnh cũ hoặc ảnh báo lỗi như kết quả thành công. Không tự gửi mã dự án tới renderer công cộng.

## 4. Kiểm tra và lặp

- Ngữ nghĩa: đúng loại, đúng ký hiệu/hướng, truy vết nguồn, không trộn hiện trạng với đề xuất.
- Cú pháp: renderer thành công; ảnh không phải trang lỗi.
- Trực quan: mở ảnh; nhãn tiếng Việt đúng, không cắt/đè chữ, mũi tên và multiplicity đọc được, đường nối phân biệt được.
- Word: kiểm tra ở kích thước chèn dự kiến theo reference; nếu có DOCX được phép sửa, kiểm tra trang xuất thực tế. Không khẳng định đã kiểm tra Word chỉ từ PNG.
- Nếu chưa đạt, sửa nguồn rồi render lại. Không chỉ tăng DPI hoặc giảm toàn bộ chữ cho vừa trang.

## 5. Bàn giao

Mã nguồn, PNG và SVG khi renderer hỗ trợ; ghi loại sơ đồ, nguồn/phiên bản, As-built hay mục tiêu, lệnh/version renderer, kích thước pixel và kích thước chèn Word, kết quả kiểm tra và giới hạn. Theo quy ước lưu trong reference hoặc đường dẫn người dùng chỉ định. Không ghi đè sơ đồ khác hay tự chèn vào SRS khi nhiệm vụ chỉ yêu cầu xuất ảnh.

Prompt mẫu: [AIP-UML-001](../../../docs/ai-engineering/prompts.md#aip-uml-001).
