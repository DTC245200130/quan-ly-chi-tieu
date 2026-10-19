# Agent — vai trò và bàn giao

Profile khai báo tương ứng hiện có tại [agents/](../../agents/README.md): requirement, design, coding, testing, critic, deployment. Mỗi profile có prompt, skill mapping và config; case đánh giá tại [evaluations/](../../evaluations/README.md). Những vai trò chuyên biệt trong bảng có thể được profile chọn theo nhiệm vụ, không cần khởi chạy agent riêng.

Đây là mô tả vai trò làm việc của AI, không phải lớp trong ứng dụng, tài khoản hệ thống hay cấu hình khởi chạy agent. Một agent có thể chuyển vai trò theo nhiệm vụ. Không tự bật thực thi song song hoặc giao việc cho subagent chỉ vì có bảng này.

| Vai trò | Skill sử dụng | Trách nhiệm/đầu ra trong phạm vi giao việc |
|---|---|---|
| Phân tích yêu cầu | requirements-analysis | Tách yêu cầu, giả định, mâu thuẫn; FR/US/AC và traceability |
| Thiết kế | architecture-design, database-design | Trách nhiệm thành phần, luồng, schema mục tiêu và khác biệt hiện trạng |
| Triển khai | implementation | Thay đổi mã tối thiểu theo yêu cầu; bằng chứng kiểm chứng |
| Kiểm thử | testing | Ca kiểm thử và kết quả theo AC; không tự sửa sản phẩm khi chỉ được giao test |
| Rà soát | code-review, security-review | Finding có bằng chứng; phân biệt confirmed/risk/gap |
| Vận hành | deployment | Kế hoạch phát hành hoặc thực thi trên môi trường được chỉ định |
| Tài liệu | documentation | Đồng bộ artifact và trạng thái, không tái dựng lịch sử |
| Mô hình hóa UML | uml-diagrams | Chọn loại, kiểm tra ký hiệu/nguồn, sinh mã, render và kiểm tra ảnh cho Word |
| Đánh giá AI | ai-evaluation | Chấm prompt/skill/context/đầu ra theo rubric và ca kiểm tra |
| Chẩn đoán lỗi | debugging | Nguyên nhân confirmed hoặc hypothesis, bằng chứng, tác động và hướng sửa; không kết luận chắc chắn nếu chưa tái hiện/kiểm chứng đủ. |
| Phân tích ảnh hưởng | change-impact-analysis | Ma trận có nguồn, phần chưa rõ, tương thích và kế hoạch kiểm chứng; không tự triển khai. |
| Thiết kế API | api-design | Contract có ví dụ hợp lệ/lỗi và mapping yêu cầu; không viết endpoint nếu chỉ thiết kế. |
| Migration database | database-migration | Migration và bằng chứng theo dialect/revision; quyền viết migration không đồng nghĩa quyền chạy production. |
| Tạo Word/PDF | document-production | Artifact cuối và trạng thái kiểm tra cấu trúc/trực quan riêng; thiếu converter thì ghi NOT RUN, không tự sửa nội dung SRS. |
| Đánh giá phát hành | release-readiness | READY / NOT READY / UNDETERMINED có căn cứ, gap cần đóng; không đổi human gate hay deploy. |

## Cách chọn vai trò

Chọn vai trò đủ cho yêu cầu; không bắt mọi nhiệm vụ đi qua toàn bộ vòng đời. Review là đọc và báo cáo. Đề xuất là mô tả mục tiêu. Thực thi chỉ tác động file/môi trường trong phạm vi đã được giao. Gate cũ không cho phép một thay đổi mới không liên quan.

Khi chuyển vai trò, bàn giao [gói context](context.md) và những điểm chưa được kiểm chứng. Người nhận kiểm tra artifact thật thay vì chỉ tin nhận xét của người trước. Nếu cùng agent tự kiểm tra, ghi rõ self-review; không gọi là đánh giá độc lập.

## Điểm bàn giao sang production

Chỉ triển khai khi người dùng giao rõ việc đó và xác định môi trường. Kết quả Evaluation đạt không thay thế kiểm thử phần mềm, kế hoạch rollback hay quyết định release. Gặp điều kiện thiếu chỉ chặn bước phụ thuộc; tiếp tục phần phân tích/chuẩn bị còn trong phạm vi.
