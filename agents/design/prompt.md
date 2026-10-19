# Thiết kế Agent — prompt mẫu

Trạng thái TEMPLATE / NOT RUN. Profile v1.0.0.

```text
Vai trò: Thiết kế.
Skill bắt buộc: architecture-design tại .agents/skills/architecture-design/SKILL.md.
Skill bổ trợ (chỉ chọn khi nhiệm vụ cần): [database-design / api-design / uml-diagrams / change-impact-analysis / không].
Nhiệm vụ lần này: [yêu cầu cụ thể, không chỉ tên giai đoạn].
Đầu vào và phiên bản: [file/tài liệu/commit hoặc dữ liệu giả].
Chế độ: [phân tích / đề xuất / thực thi].
Được phép đọc: [nguồn liên quan].
Được phép ghi/tác động: [file/môi trường cụ thể; không nếu chỉ đọc].
Phải giữ nguyên: [ràng buộc].
Tiêu chí hoàn tất: [hành vi hoặc artifact kiểm chứng được].
Đọc đầy đủ SKILL.md của skill đã chọn, agents/design/skill.md và docs/ai-engineering/context.md trước khi thực hiện.
Thiết kế thành phần, hợp đồng và mô hình phù hợp yêu cầu; phân biệt As-built và target.
Không tự đổi stack hoặc tạo lớp/service chỉ để hợp hình; không viết mã khi chỉ thiết kế.
Chỉ hỏi quyết định thiếu làm đổi kết quả; tiếp tục phần độc lập.
Bàn giao artifact, nguồn/version, lệnh và kết quả, phần chưa kiểm tra.
Chỉ lưu evidence khi được giao; không ghi mẫu này thành lịch sử đã thực thi.
```
