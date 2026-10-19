---
name: deployment
description: Lập kế hoạch hoặc thực hiện triển khai Sổ Chi Tiêu theo môi trường và phạm vi được giao, với kiểm tra readiness, migration, rollback và bằng chứng vận hành.
---

# Triển khai và vận hành

Áp dụng [hợp đồng phạm vi và nguồn context](../../../docs/ai-engineering/context.md). Prompt tương ứng: AIP-DEPLOY-001 trong [bộ prompt](../../../docs/ai-engineering/prompts.md). Mặc định của yêu cầu lập kế hoạch là đề xuất; không tự thực thi release.

## Quy trình

Khi nhiệm vụ liên quan CI/CD, môi trường, backup/restore hoặc sự cố, đọc [CI/CD và vận hành](references/operations.md). Chỉ nạp phần phù hợp nhiệm vụ.

1. Xác định môi trường, phiên bản/artifact cần phát hành, quyền tác động, yêu cầu downtime và điều kiện rollback. Đọc docs/software/deployment/deployment.md, docs/software/deployment/azure-deploy.md, docs/governance/human-gates.md, config liên quan; không đọc .env thật để đưa vào context.
2. Đối chiếu requirements vận hành, kết quả test/review hiện có và phạm vi release. Phân biệt bằng chứng cũ với kiểm chứng của phiên bản đang phát hành.
3. Với nhiệm vụ lập kế hoạch, mô tả thứ tự build, backup/restore, migration preflight, readiness, smoke test, chuyển traffic và rollback. Chỉ sửa tài liệu nếu được giao.
4. Với nhiệm vụ thực thi, chỉ chạy trên môi trường và phiên bản được chỉ định. Dừng bước phát hành nếu thiếu điều kiện bắt buộc; không tự chọn production hoặc dùng database thật để thử.
5. Nếu migration phát hiện collision/xung đột, dừng và báo cáo; không tự sửa dữ liệu. Không giả định rollback mã có thể đảo ngược migration mất dữ liệu; cần phương án restore phù hợp.
6. Kiểm tra health/readiness và hành vi chính theo phạm vi release; ghi lệnh, kết quả và tình trạng traffic thực tế. Nếu thất bại, áp dụng rollback đã nằm trong phạm vi được giao hoặc báo bước cần quyết định.

## Đầu ra

Kế hoạch hoặc bản ghi triển khai có môi trường/phiên bản, checks, bằng chứng, rollback và vấn đề chưa giải quyết. Không tự đánh dấu Release Gate APPROVED, không tuyên bố SLA/backup đã đạt khi chưa đo hoặc thử restore.
