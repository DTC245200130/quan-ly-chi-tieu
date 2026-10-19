---
name: release-readiness
description: Đánh giá một phiên bản Sổ Chi Tiêu đã đủ bằng chứng để phát hành hay chưa qua yêu cầu, test, lỗi mở, migration và vận hành; không tự deploy hoặc phê duyệt release.
---

# Đánh giá sẵn sàng phát hành

Áp dụng [context và phạm vi nhiệm vụ](../../../docs/ai-engineering/context.md). Prompt: [AIP-RELEASE-001](../../../docs/ai-engineering/prompts.md#aip-release-001). Đầu ra ghi file chỉ áp dụng khi nhiệm vụ yêu cầu/cho phép; tư vấn trả kết quả trong câu trả lời. Giữ quyền và quyết định đã được giao, không hỏi lại chỉ vì chuyển skill.

## Quy trình

1. Chốt phiên bản/commit hoặc artifact và môi trường phát hành; nếu working tree có thay đổi, mô tả chính xác tập được đánh giá, không quy mọi evidence cho HEAD.
2. Đọc yêu cầu/AC trong phạm vi release, gate và danh sách lỗi/review. Lập bảng tiêu chí → evidence → phiên bản/môi trường → PASS/FAIL/BLOCKED/NOT RUN.
3. Đối chiếu test/build, security findings, migration trial, cấu hình và readiness/rollback cần cho phiên bản này. Chỉ yêu cầu bằng chứng theo thay đổi và rủi ro, không biến thành checklist vô hạn.
4. Kiểm tra bằng chứng cũ còn áp dụng không; nêu lý do nếu dùng lại. Thiếu evidence phải ghi rõ, không coi là PASS. Rủi ro đã được con người chấp nhận cần nguồn và phạm vi chấp nhận.
5. Kết luận READY khi tiêu chí bắt buộc có bằng chứng phù hợp và không còn blocker; NOT READY khi có fail/gap chặn; UNDETERMINED khi chưa xác định được phiên bản hoặc điều kiện cần đánh giá.
6. Nêu hành động tối thiểu để đóng gap và người/vai trò cần bàn giao. Có thể chạy kiểm tra chỉ đọc trong phạm vi, không tự sửa sản phẩm, đổi human gate hay deploy.

## Hoàn tất và bàn giao

Báo cáo cho phiên bản cụ thể với kết luận, evidence, blocker và giới hạn. READY là khuyến nghị kỹ thuật, không là human approval hay quyền đưa lên production.
