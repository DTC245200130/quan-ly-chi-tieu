---
name: document-production
description: Tạo hoặc chỉnh tài liệu Word/PDF theo mẫu Sổ Chi Tiêu, bảo toàn cấu trúc, styles, caption, mục lục và kiểm tra trang xuất; dùng khi cần artifact tài liệu hoàn chỉnh.
---

# Sản xuất tài liệu Word/PDF

Áp dụng [context và phạm vi nhiệm vụ](../../../docs/ai-engineering/context.md). Prompt: [AIP-DOCBUILD-001](../../../docs/ai-engineering/prompts.md#aip-docbuild-001). Đầu ra ghi file chỉ áp dụng khi nhiệm vụ yêu cầu/cho phép; tư vấn trả kết quả trong câu trả lời. Giữ quyền và quyết định đã được giao, không hỏi lại chỉ vì chuyển skill.

## Quy trình

1. Xác định file nguồn, mẫu, nội dung được duyệt, phần cần giữ, định dạng đầu ra và đường dẫn. Kiểm tra cấu trúc/template thực tế trước khi tạo; không ghi đè bản gốc nếu chỉ yêu cầu bản mới.
2. Lập mapping nội dung → heading/table/figure/appendix của mẫu, phân biệt thiếu nội dung với thiếu định dạng. Không tự thêm luận điểm, số liệu test hoặc lời phê duyệt.
3. Kiểm tra công cụ có sẵn cho DOCX và chuyển PDF; chọn công cụ bảo toàn các tính năng mẫu. Nếu thiếu renderer/converter, ghi rõ giới hạn, không giả file bằng cách đổi đuôi.
4. Dùng styles cho heading/body, numbering phù hợp; giữ section, margin, orientation, header/footer/page numbers. Bảng không tràn trang, hàng tiêu đề có thể lặp; caption và tham chiếu nhất quán.
5. Với UML, dùng uml-diagrams; chèn hình đúng vùng khả dụng và giữ tỉ lệ. Với ảnh khác, kiểm tra độ phân giải, chữ và nguồn. Không vẽ lại UML bằng công cụ sinh ảnh.
6. Tạo/cập nhật mục lục và field bằng công cụ có khả năng đó. Nếu thư viện chỉ chèn field nhưng chưa tính lại, ghi rõ cần cập nhật; không tuyên bố số trang/mục lục đã đúng.
7. Xuất preview/PDF bằng converter thực tế khi có, xem mọi trang chịu thay đổi và các trang kế cận; với tài liệu mới, kiểm tra toàn bộ trang. Xử lý blank page, orphan heading, cắt bảng, méo hình, font tiếng Việt và caption tách hình.
8. Bàn giao file cuối ở docs/outputs hoặc đường dẫn người dùng, nguồn và báo cáo kiểm tra ngắn. Giữ nguồn sửa được; không sửa nội dung SRS chỉ vì được giao dàn trang.

## Hoàn tất và bàn giao

DOCX/PDF đúng yêu cầu cùng trạng thái kiểm tra cấu trúc và trực quan riêng. Nếu chưa render trang, ghi NOT RUN cho kiểm tra bố cục; không lấy việc file mở được thay cho chất lượng trang.
