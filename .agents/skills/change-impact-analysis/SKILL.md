---
name: change-impact-analysis
description: Phân tích tác động của thay đổi yêu cầu hoặc hành vi Sổ Chi Tiêu lên UI, API, xử lý, dữ liệu, test và tài liệu trước khi sửa.
---

# Phân tích ảnh hưởng thay đổi

Áp dụng [context và phạm vi nhiệm vụ](../../../docs/ai-engineering/context.md). Prompt: [AIP-IMPACT-001](../../../docs/ai-engineering/prompts.md#aip-impact-001). Đầu ra ghi file chỉ áp dụng khi nhiệm vụ yêu cầu/cho phép; tư vấn trả kết quả trong câu trả lời. Giữ quyền và quyết định đã được giao, không hỏi lại chỉ vì chuyển skill.

## Quy trình

1. Xác định baseline và thay đổi mong muốn từ prompt/quyết định; phân biệt đổi hành vi, đổi tên, sửa tài liệu và refactor giữ hành vi.
2. Tìm định nghĩa và caller thực tế; lần theo UI → API/schema → xử lý → dữ liệu và các consumer ngoài luồng chính. Gắn từng kết luận với nguồn.
3. Lập ma trận thành phần/file → tác động trực tiếp/gián tiếp/không đổi/chưa rõ → lý do → kiểm chứng cần làm.
4. Xem tương thích API, dữ liệu đã lưu, migration, phiên đăng nhập, cache và cấu hình khi liên quan; không đánh dấu tất cả tầng là bị ảnh hưởng chỉ để đủ bảng.
5. Nêu phương án tối thiểu, phương án thay thế nếu có và chi phí/rủi ro tương đối có căn cứ. Chỉ hỏi quyết định còn thiếu có thể làm đổi phạm vi.
6. Bàn giao tập sửa dự kiến, thứ tự phụ thuộc và kiểm chứng hồi quy. Đây là phân tích; không tự triển khai, đổi SRS hoặc tạo migration.

## Hoàn tất và bàn giao

Ma trận ảnh hưởng có nguồn và phần chưa biết; phạm vi đề nghị và tiêu chí kiểm chứng. RQ-009 chỉ thay mô hình hóa không tự suy ra thay database.
