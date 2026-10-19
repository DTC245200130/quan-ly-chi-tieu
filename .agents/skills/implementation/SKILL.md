---
name: implementation
description: Thực hiện tác vụ coding của Sổ Chi Tiêu từ prompt cụ thể bằng cách làm rõ hành vi mong muốn, khảo sát mã, xác định phạm vi sửa đổi, triển khai và kiểm chứng; không dùng cho yêu cầu chỉ review hoặc chẩn đoán.
---

# Coding theo yêu cầu và phạm vi thay đổi

## Phạm vi nhiệm vụ

Áp dụng [hợp đồng context](../../../docs/ai-engineering/context.md); prompt tương ứng: [AIP-IMPL-001](../../../docs/ai-engineering/prompts.md#aip-impl-001). Các bước ghi file bên dưới chỉ áp dụng khi nhiệm vụ cho phép cập nhật artifact đó. Với yêu cầu tư vấn, phân tích hoặc review không ghi file, trả kết quả trong câu trả lời; không tự chạy toàn quy trình hay chuyển sang triển khai. Quyết định đã được người dùng chốt là đầu vào, không hỏi lại cùng quyết định.

Yêu cầu nghiệp vụ lấy từ prompt hiện tại, quyết định người dùng và tài liệu liên quan. Skill này cung cấp quy trình làm việc, không chứa danh sách lời giải cho mọi tính năng/ngôn ngữ/framework và không tự tạo backlog.

## 1. Chuyển prompt thành hợp đồng thay đổi

Xác định vấn đề hoặc mục tiêu, hành vi hiện tại → mong muốn, người/luồng bị ảnh hưởng, ràng buộc, điều giữ nguyên và tiêu chí hoàn tất có thể kiểm chứng. Dùng FR/AC sẵn có khi liên quan; với lỗi nhỏ chưa có ID, có thể nêu tiêu chí trực tiếp từ prompt, không tự sửa SRS để tạo đủ giấy tờ.

Phân biệt điều đã biết, giả định ít rủi ro và câu hỏi làm thay đổi nghiệp vụ, quyền truy cập, dữ liệu hoặc tính tương thích. Khảo sát nguồn trước khi hỏi điều có thể tìm thấy. Chỉ hỏi phần còn thiếu ảnh hưởng thực sự đến kết quả; tiếp tục phần độc lập. Không yêu cầu người dùng duyệt lại quyết định hoặc quyền đã giao.

## 2. Khảo sát và khoanh vùng

Phối hợp theo nhu cầu: [debugging](../debugging/SKILL.md) khi nguyên nhân lỗi chưa rõ; [change-impact-analysis](../change-impact-analysis/SKILL.md) khi thay đổi lan qua nhiều tầng; [api-design](../api-design/SKILL.md) khi cần contract; [database-migration](../database-migration/SKILL.md) khi có migration. Không tự chạy tất cả skill. Với giao diện cần thiết kế/UX, dùng skill impeccable nếu có trong môi trường; nếu không, bám DESIGN.md và báo giới hạn.

Đọc hướng dẫn repository, kiểm tra trạng thái working tree và mã/test liên quan. Lần theo entrypoint → xử lý → dữ liệu/response và caller chịu ảnh hưởng; không suy đoán từ tên file. Với bug, xác định cách tái hiện hoặc bằng chứng nguyên nhân trước khi sửa.

Nêu ngắn gọn kế hoạch trước khi chỉnh: hành vi sẽ đổi; file/thành phần dự kiến và lý do; API/schema/dependency có bị tác động không; phần loại trừ; cách kiểm chứng. Quy mô kế hoạch tương xứng nhiệm vụ, không bắt buộc tạo file plan hoặc dừng xin duyệt cho sửa đổi thường lệ đã được giao.

Kiểm tra ảnh hưởng tới caller, contract, ownership, migration, config và test phù hợp. Giữ thay đổi người dùng; nếu có phần chồng chéo không thể bảo toàn thì báo cụ thể. Không kéo theo refactor, đổi stack, nâng dependency hoặc format toàn repository nếu không cần để hoàn thành nhiệm vụ.

## 3. Thực thi theo phạm vi

Chọn thay đổi nhất quán nhỏ nhất xử lý đúng nguyên nhân, theo convention hiện có. Không tạo service/abstraction mới chỉ để đúng mẫu. Nếu phát hiện cần mở rộng phạm vi đáng kể hoặc thay quyết định nghiệp vụ, nêu bằng chứng và lựa chọn; không tự đổi yêu cầu.

Bảo toàn invariant liên quan: dữ liệu tài chính theo owner, secret ngoài mã, Gemini chỉ nhận aggregate được cho phép, lỗi ngoài không lộ chi tiết nhạy cảm. Nếu cần schema change, dùng thiết kế và migration phù hợp; không sửa database thật trực tiếp. Với thay đổi không liên quan database, không tự tạo migration.

## 4. Kiểm chứng theo hành vi và rủi ro

Chọn kiểm tra từ tiêu chí hoàn tất: ca thành công, lỗi/biên và hồi quy tại thành phần ảnh hưởng; ưu tiên ownership/auth khi chạm dữ liệu hoặc quyền. Thêm test khi có giá trị bảo vệ hành vi, không kiểm thử chỉ để so khớp cấu trúc implementation.

Chạy kiểm tra tập trung trước, mở rộng suite/typecheck/build khi phạm vi và rủi ro cần. Đọc script/config thực tế để chọn lệnh. Không lặp toàn bộ suite khi không có thay đổi hoặc nghi vấn mới. Không hạ kỳ vọng để che lỗi; phân biệt lỗi có trước, regression và thiếu môi trường. Không ghi PASS khi chưa chạy.

## 5. Rà soát diff và bàn giao

Đối chiếu diff với hợp đồng ban đầu: từng file phải có lý do, không có secret/thay đổi ngoài phạm vi; kiểm tra hành vi mong muốn và tương thích. Cập nhật tài liệu trực tiếp chịu ảnh hưởng trong phạm vi được giao; không tự ghi mọi artifact SDLC.

Báo kết quả theo thứ tự: hành vi đã thay đổi, file chính, kiểm chứng thực tế, giới hạn còn lại. Lưu nhật ký nếu nhiệm vụ/quy trình yêu cầu, không bịa prompt lịch sử hoặc approval. Không commit/push/deploy chỉ vì đã coding xong.

## Điều kiện hoàn tất

- Tiêu chí hoàn tất từ prompt/AC liên quan có bằng chứng pass hoặc được ghi rõ là còn fail/block.
- Mã, test, migration (nếu có) và tài liệu trong phạm vi nhất quán.
- Không tuyên bố hoàn tất nếu test bắt buộc chưa chạy hoặc đang thất bại.
