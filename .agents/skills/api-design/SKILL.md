---
name: api-design
description: Thiết kế hoặc điều chỉnh hợp đồng API Sổ Chi Tiêu gồm request/response, validation, quyền truy cập, lỗi và tương thích; chưa triển khai endpoint nếu nhiệm vụ chỉ thiết kế.
---

# Thiết kế hợp đồng API

Áp dụng [context và phạm vi nhiệm vụ](../../../docs/ai-engineering/context.md). Prompt: [AIP-API-001](../../../docs/ai-engineering/prompts.md#aip-api-001). Đầu ra ghi file chỉ áp dụng khi nhiệm vụ yêu cầu/cho phép; tư vấn trả kết quả trong câu trả lời. Giữ quyền và quyết định đã được giao, không hỏi lại chỉ vì chuyển skill.

## Quy trình

1. Đọc yêu cầu/AC, route/schema và caller hiện có; xác định API hiện trạng hay thiết kế mục tiêu. Giữ convention của repository, không tự chọn versioning hoặc đổi format toàn API.
2. Với mỗi operation, ghi mục tiêu, method/path, path/query/body, kiểu dữ liệu, trường bắt buộc/null/default và response; nêu dữ liệu không được trả.
3. Ghi điều kiện xác thực và ownership trên tài nguyên; ID từ client không phải bằng chứng sở hữu. Phân biệt endpoint công khai với endpoint chỉ dành phiên chưa đăng nhập.
4. Định nghĩa validation và lỗi theo contract hiện có; status/message không lộ secret hoặc tài khoản/dữ liệu khác. Nêu phân trang, filter, sort khi collection cần; không tự bổ sung cho mọi endpoint.
5. Xem transaction boundary, thao tác lặp/retry và cạnh tranh khi operation có side effect; chỉ đưa idempotency khi có nhu cầu, không tự thêm cơ chế phức tạp.
6. Kiểm tra caller và thay đổi breaking/non-breaking; có ví dụ request/response hợp lệ, sai dữ liệu, chưa xác thực và sai owner phù hợp.
7. Bàn giao contract, mapping requirement và câu hỏi còn mở. Nếu được giao lưu, dùng docs/software/design/api.md hoặc artifact được chỉ định; OpenAPI chỉ sinh khi được yêu cầu và phải validate bằng công cụ hiện có.

## Hoàn tất và bàn giao

Contract đủ để frontend/backend/test cùng sử dụng, phân biệt actual/target. Không sửa endpoint, dependency hoặc database từ nhiệm vụ chỉ thiết kế.
