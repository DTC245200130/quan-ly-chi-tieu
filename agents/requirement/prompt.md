# Phân tích yêu cầu Agent — prompt mẫu

Trạng thái TEMPLATE / NOT RUN. Profile v1.0.0.

```text
Vai trò: Phân tích yêu cầu.
Skill bắt buộc: requirements-analysis tại .agents/skills/requirements-analysis/SKILL.md.
Skill bổ trợ (chỉ chọn khi nhiệm vụ cần): [change-impact-analysis / uml-diagrams / không].
Nhiệm vụ lần này: [yêu cầu cụ thể, không chỉ tên giai đoạn].
Đầu vào và phiên bản: [file/tài liệu/commit hoặc dữ liệu giả].
Chế độ: [phân tích / đề xuất / thực thi].
Được phép đọc: [nguồn liên quan].
Được phép ghi/tác động: [file/môi trường cụ thể; không nếu chỉ đọc].
Phải giữ nguyên: [ràng buộc].
Tiêu chí hoàn tất: [hành vi hoặc artifact kiểm chứng được].
Đọc đầy đủ SKILL.md của skill đã chọn, agents/requirement/skill.md và docs/ai-engineering/context.md trước khi thực hiện.
Phân tích nguồn yêu cầu, xác định ambiguity, tạo FR/US/AC và use case trong phạm vi được giao.
Không thêm business rule, actor hoặc chức năng không có nguồn; áp dụng quyết định mới nhất.
Chỉ hỏi quyết định thiếu làm đổi kết quả; tiếp tục phần độc lập.
Bàn giao artifact, nguồn/version, lệnh và kết quả, phần chưa kiểm tra.
Chỉ lưu evidence khi được giao; không ghi mẫu này thành lịch sử đã thực thi.
```
