---
name: requirements-analysis
description: Phân tích yêu cầu cho Sổ Chi Tiêu và tạo yêu cầu, user story, tiêu chí chấp nhận cùng các vấn đề chưa giải quyết có khả năng truy vết trước khi thiết kế hoặc triển khai.
---

# Phân tích yêu cầu

## Phạm vi nhiệm vụ

Áp dụng [hợp đồng context](../../../docs/ai-engineering/context.md); prompt tương ứng: [AIP-REQ-001](../../../docs/ai-engineering/prompts.md#aip-req-001). Các bước ghi file bên dưới chỉ áp dụng khi nhiệm vụ cho phép cập nhật artifact đó. Với yêu cầu tư vấn, phân tích hoặc review không ghi file, trả kết quả trong câu trả lời; không tự chạy toàn quy trình hay chuyển sang triển khai. Quyết định đã được người dùng chốt là đầu vào, không hỏi lại cùng quyết định.

## Quy trình

Khi đặc tả use case, luồng ngoại lệ hoặc truy vết AC, đọc [Đặc tả use case và truy vết](references/use-case-specification.md). Chỉ nạp phần phù hợp nhiệm vụ.

1. Đọc `docs/software/requirements/customer-requirement.md`, tài liệu sản phẩm hiện có và trạng thái Requirements Gate trong `docs/governance/human-gates.md`.
2. Trích xuất và phân loại thông tin thành yêu cầu đã xác nhận, giả định, mâu thuẫn và câu hỏi chưa giải quyết. Không suy diễn quy tắc nghiệp vụ từ implementation hiện tại.
3. Gán ID ổn định: `FR-*` cho yêu cầu chức năng, `NFR-*` cho yêu cầu phi chức năng, `US-*` cho user story và `AC-*` cho tiêu chí chấp nhận. Không tái sử dụng ID đã có cho ý nghĩa khác.
4. Viết hoặc cập nhật `docs/software/requirements/requirements.md`; mỗi yêu cầu phải rõ chủ thể, hành vi, phạm vi và điều kiện quan trọng.
5. Viết hoặc cập nhật `docs/software/requirements/user-stories.md`; truy vết từng story về ít nhất một requirement ID.
6. Viết hoặc cập nhật `docs/software/requirements/acceptance-criteria.md`; mỗi tiêu chí phải kiểm chứng được và liên kết tới requirement/story tương ứng.
7. Ghi giả định, mâu thuẫn, quyết định và câu hỏi mở vào `docs/software/requirements/requirements-issues.md`.
8. Kiểm tra ma trận truy vết để phát hiện requirement không có story/AC hoặc AC không có nguồn yêu cầu.
9. Nếu câu hỏi mở làm thay đổi đáng kể hành vi, dừng trước kiến trúc hoặc triển khai và yêu cầu quyết định của con người trong `docs/governance/human-gates.md`.

## Điểm dừng và đầu ra

- Không viết mã trong skill này.
- Không tự đánh dấu Requirements Gate là `APPROVED`.
- Đầu ra tối thiểu: bốn tài liệu requirements được cập nhật, danh sách vấn đề mở và trạng thái gate chính xác.
