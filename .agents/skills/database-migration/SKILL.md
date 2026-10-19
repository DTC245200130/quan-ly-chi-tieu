---
name: database-migration
description: Soạn và kiểm chứng Alembic migration Sổ Chi Tiêu từ thay đổi schema đã xác định; xử lý preflight, dữ liệu hiện hữu, upgrade và rollback/restore trong môi trường được giao.
---

# Thực hiện migration dữ liệu

Áp dụng [context và phạm vi nhiệm vụ](../../../docs/ai-engineering/context.md). Prompt: [AIP-MIGRATE-001](../../../docs/ai-engineering/prompts.md#aip-migrate-001). Đầu ra ghi file chỉ áp dụng khi nhiệm vụ yêu cầu/cho phép; tư vấn trả kết quả trong câu trả lời. Giữ quyền và quyết định đã được giao, không hỏi lại chỉ vì chuyển skill.

## Quy trình

1. Xác định yêu cầu, thiết kế schema, revision hiện tại/heads, dialect, tập dữ liệu và môi trường được giao. Tách quyền viết migration với quyền chạy trên database thật.
2. Đọc model và lịch sử migration; không sửa migration đã phát hành hoặc dùng create_all thay migration. Khi thiết kế còn thiếu, dùng database-design để xác định trước phần phụ thuộc.
3. Lập preflight cho null, duplicate, identity collision, ownership và giá trị không hợp lệ theo thay đổi. Xung đột dữ liệu phải dừng và báo; không tự xóa, gộp hay sửa.
4. Viết upgrade theo phụ thuộc constraint/index/data backfill; xét lock và transaction theo dialect. Với dữ liệu lớn, nêu nhu cầu chia đợt có căn cứ.
5. Viết downgrade chỉ khi đảo ngược được an toàn. Với mất thông tin, ghi giới hạn và kế hoạch restore; không gọi migration “reversible” chỉ vì có hàm downgrade.
6. Thử trên database cô lập: schema mới từ đầu, upgrade từ revision trước với dữ liệu giả đại diện, preflight thất bại không làm hỏng dữ liệu, constraint sau upgrade; downgrade/restore nếu thuộc phạm vi. Phân biệt SQLite với PostgreSQL, không dùng kết quả một bên để chứng minh bên kia.
7. So sánh model/schema, ghi lệnh/revision/kết quả. Chạy production chỉ khi được giao rõ môi trường và bước vận hành; chuyển deployment thực hiện nếu cần.

## Hoàn tất và bàn giao

Migration source, preflight, bằng chứng môi trường thử, giới hạn rollback và hướng vận hành. Không chạm database cá nhân/production để làm fixture.
