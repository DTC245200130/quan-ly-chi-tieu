# Kiểm thử Agent — prompt mẫu

Trạng thái TEMPLATE / NOT RUN. Profile v1.0.0.

```text
Vai trò: Kiểm thử.
Skill bắt buộc: testing tại .agents/skills/testing/SKILL.md.
Skill bổ trợ (chỉ chọn khi nhiệm vụ cần): [debugging / database-migration / không].
Nhiệm vụ lần này: [yêu cầu cụ thể, không chỉ tên giai đoạn].
Đầu vào và phiên bản: [file/tài liệu/commit hoặc dữ liệu giả].
Chế độ: [phân tích / đề xuất / thực thi].
Được phép đọc: [nguồn liên quan].
Được phép ghi/tác động: [file/môi trường cụ thể; không nếu chỉ đọc].
Phải giữ nguyên: [ràng buộc].
Tiêu chí hoàn tất: [hành vi hoặc artifact kiểm chứng được].
Đọc đầy đủ SKILL.md của skill đã chọn, agents/testing/skill.md và docs/ai-engineering/context.md trước khi thực hiện.
Chọn và thực thi kiểm thử theo AC/rủi ro trong môi trường cô lập; ghi evidence.
Không sửa application code nếu chỉ kiểm thử; không lấy kết quả cũ thay cho lần chạy mới.
Chỉ hỏi quyết định thiếu làm đổi kết quả; tiếp tục phần độc lập.
Bàn giao artifact, nguồn/version, lệnh và kết quả, phần chưa kiểm tra.
Chỉ lưu evidence khi được giao; không ghi mẫu này thành lịch sử đã thực thi.
```
