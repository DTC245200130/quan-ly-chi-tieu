---
name: debugging
description: Chẩn đoán lỗi Sổ Chi Tiêu qua tái hiện, kiểm tra giả thuyết và bằng chứng nguyên nhân; dùng khi hỏi vì sao hoặc tìm nguyên nhân, không tự sửa mã nếu chưa được giao.
---

# Chẩn đoán lỗi

Áp dụng [context và phạm vi nhiệm vụ](../../../docs/ai-engineering/context.md). Prompt: [AIP-DEBUG-001](../../../docs/ai-engineering/prompts.md#aip-debug-001). Đầu ra ghi file chỉ áp dụng khi nhiệm vụ yêu cầu/cho phép; tư vấn trả kết quả trong câu trả lời. Giữ quyền và quyết định đã được giao, không hỏi lại chỉ vì chuyển skill.

## Quy trình

1. Xác định triệu chứng, expected/actual, môi trường/phiên bản, bước tái hiện và phạm vi ảnh hưởng. Đọc log đã che dữ liệu nhạy cảm, test và mã liên quan; không yêu cầu người dùng cung cấp lại thông tin đã có.
2. Tái hiện bằng ca nhỏ nhất trên môi trường cô lập. Nếu không tái hiện được, ghi điều kiện đã thử và dữ kiện thiếu; không gán nguyên nhân chắc chắn.
3. Lần theo đường đi dữ liệu và lỗi qua UI/API/xử lý/persistence. Lập các giả thuyết cạnh tranh có dấu hiệu kiểm chứng, kiểm tra theo chi phí và khả năng giải thích triệu chứng.
4. Dùng kiểm tra chỉ đọc hoặc thử nghiệm cô lập để loại giả thuyết; không sửa mã sản phẩm chỉ để chẩn đoán. Phân biệt lỗi gốc với lỗi dây chuyền và vấn đề môi trường.
5. Kết luận confirmed khi có bằng chứng đủ; nếu chỉ suy luận, ghi hypothesis và phép thử tiếp theo. Nêu nơi phát sinh, trigger, cơ chế gây lỗi và tác động.
6. Nếu yêu cầu bao gồm sửa lỗi, chuyển sang implementation với nguyên nhân, phạm vi và regression case; tiếp tục công việc đã được giao, không xin lại quyền. Nếu chỉ hỏi nguyên nhân, dừng ở báo cáo.

## Hoàn tất và bàn giao

Báo cáo expected/actual, cách tái hiện, giả thuyết đã loại, bằng chứng file:dòng/lệnh, mức chắc chắn và hướng sửa. Không coi việc hết triệu chứng sau một thay đổi ngẫu nhiên là đã chứng minh nguyên nhân.
