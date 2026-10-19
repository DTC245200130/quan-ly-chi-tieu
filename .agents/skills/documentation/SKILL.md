---
name: documentation
description: Duy trì tài liệu người dùng, API, kiến trúc, cơ sở dữ liệu, triển khai và bằng chứng SDLC của Sổ Chi Tiêu đồng bộ với implementation.
---

# Tài liệu hóa

## Phạm vi nhiệm vụ

Áp dụng [hợp đồng context](../../../docs/ai-engineering/context.md); prompt tương ứng: [AIP-DOC-001](../../../docs/ai-engineering/prompts.md#aip-doc-001). Các bước ghi file bên dưới chỉ áp dụng khi nhiệm vụ cho phép cập nhật artifact đó. Với yêu cầu tư vấn, phân tích hoặc review không ghi file, trả kết quả trong câu trả lời; không tự chạy toàn quy trình hay chuyển sang triển khai. Quyết định đã được người dùng chốt là đầu vào, không hỏi lại cùng quyết định.

## Quy trình

Khi cần artifact Word/PDF theo mẫu hoặc kiểm tra trang xuất, dùng thêm [document-production](../document-production/SKILL.md); không coi nội dung Markdown đúng là đã kiểm chứng bố cục tài liệu.

Nếu nhiệm vụ có tạo/sửa sơ đồ UML, dùng thêm [uml-diagrams](../uml-diagrams/SKILL.md) cho chọn loại, ký hiệu, render và kích thước ảnh. Skill documentation tiếp tục chịu trách nhiệm nội dung, caption, liên kết và trạng thái tài liệu; không thay thế kiểm tra UML bằng việc ảnh đã được chèn vào Word.

1. Xác định tài liệu bị ảnh hưởng và nguồn sự thật tương ứng trong requirements, mã, config, migration, test hoặc deployment.
2. Đọc implementation và phiên bản tài liệu hiện có trước khi chỉnh sửa; không suy đoán hành vi từ tên file hoặc kế hoạch.
3. Phân loại nội dung thành đã triển khai, thiết kế mục tiêu, đề xuất, giới hạn và bằng chứng lịch sử; gắn nhãn rõ ràng.
4. Cập nhật tài liệu phù hợp: `README.md`, `docs/software/design/api.md`, `docs/software/design/architecture.md`, `docs/software/design/database-design.md`, `docs/software/deployment/deployment.md`, `docs/software/user-guide.md` hoặc artifact SDLC liên quan.
5. Đồng bộ endpoint, request/response, biến môi trường, command, port, dependency và đường dẫn với mã/config hiện tại.
6. Với hướng dẫn setup/deploy, bảo đảm lệnh có thứ tự, prerequisite, môi trường chạy và kết quả mong đợi rõ ràng.
7. Với tài liệu API/user guide, mô tả cả validation, permission, lỗi và giới hạn quan trọng; không chỉ mô tả happy path.
8. Kiểm tra liên kết nội bộ, đường dẫn file, heading, thuật ngữ, ID truy vết và mâu thuẫn giữa các tài liệu.
9. Đối chiếu mọi tuyên bố test, coverage, scan, approval, MCP hoặc prompt lịch sử với bằng chứng thực tế và ngày thực hiện.
10. Rà soát diff để bảo đảm không ghi đè lịch sử hợp lệ hoặc biến kế hoạch thành tuyên bố đã hoàn thành.

## Quy tắc bằng chứng

- Không tuyên bố hành vi đã triển khai nếu chỉ tồn tại trong thiết kế.
- Không tự tạo kết quả test, security scan, human approval, MCP usage hoặc historical prompt.
- Giữ tài liệu ngắn gọn nhưng đủ để người khác thực thi hoặc kiểm chứng độc lập.
