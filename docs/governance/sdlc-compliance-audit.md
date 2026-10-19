# Đánh giá tuân thủ AI-Augmented SDLC

Ngày đánh giá: 06/09/2026. Tài liệu nguồn được dùng như tiêu chí tham khảo; yêu cầu hiện tại của người dùng và dự án Sổ Chi Tiêu mới là phạm vi thực hiện.

## Kết luận

Trước đợt bổ sung này, dự án **bám tốt phần implementation, testing, Git và deployment**, nhưng **chưa bám quy trình SDLC có kiểm soát bằng skill và human gate**. Không thể chứng minh chuỗi Requirements → Approval → Architecture → Approval → Database → Implementation; phần lớn tài liệu đang là as-built.

| Tiêu chí trong hướng dẫn | Trước bổ sung | Sau bổ sung | Còn cần con người |
|---|---|---|---|
| Phân tích yêu cầu | Thiếu artifact chuẩn | Có baseline FR/NFR, story, AC, issue | Requirements Gate đã duyệt |
| Requirements Skill | Không có | Đã có project skill | Dùng trong vòng thay đổi tiếp theo |
| Kiến trúc | README/DESIGN có một phần | Có architecture + ADR + traceability | Architecture Gate đã duyệt |
| Database Skill + CSDL | Có models/migration, thiếu skill/design | Có skill + design/gap | Database Gate đã duyệt; chưa implementation |
| Coding Skill + implementation | Implementation mạnh, không có evidence skill | Có implementation skill | Dùng theo baseline được duyệt |
| Testing Skill + evidence | Test/report tốt nhưng lệnh pytest lỗi discovery | Có skill/plan/report; lệnh đã sửa, suite pass | Quyết định coverage/E2E target |
| Code review | Không có report riêng | Có review report | Triage findings |
| Security review | Có controls/test, không có report | Có security skill/report | Xử lý/accept findings; chạy scanner |
| Documentation Skill | README/deploy/design tốt, thiếu skill | Có skill, API, deployment, user guide và bộ SDLC docs | Human review tính chính xác |
| Tools/MCP | Tools/Git rõ; không có MCP evidence | Tool evidence được log | MCP chỉ khi có external issue/source |
| Prompt/task evidence | Không có transcript cũ | Có prompt register từ 06/09/2026 | Không thể phục hồi prompt của commit cũ |
| Human verification + AI report | Thiếu | Requirements/Architecture/Database đã duyệt; có process log | Release Gate còn chờ |
| Git history | 14 commit rõ theo tính năng | Giữ nguyên | Commit các artifact mới |

## Những điểm chúng ta chưa làm đúng trước đây

1. Đi thẳng từ yêu cầu hội thoại sang thiết kế/code mà không tạo và xin duyệt baseline requirements.
2. Không tạo/use project-level `SKILL.md`; `.gitignore` còn loại `.agents/`, trái yêu cầu quản lý skill cùng source.
3. Không lưu prompt, artifact, lỗi AI và human correction theo từng vòng.
4. Không có traceability FR → architecture → test.
5. Báo cáo test là snapshot nhưng thiếu cấu hình discovery ổn định; lệnh README đã thất bại trong workspace hiện tại.
6. Không có human gate nên không được phép tuyên bố quy trình đã hoàn toàn tuân thủ, dù code/test tốt.

## Việc không thể bổ sung hồi tố

Không được tự tạo chữ ký phê duyệt, prompt lịch sử, MCP usage hay “chỉnh sửa do con người” khi không có bằng chứng. Các prompt từ ngày 06/09/2026 đã được lưu tại `docs/ai-engineering/history/prompts.md`; prompt của các commit cũ vẫn được ghi nhận là thiếu evidence. Requirements, Architecture và Database Gate đã được người dùng phê duyệt; Release Gate vẫn `PENDING`.

## Bước để hoàn tất

1. Thực hiện implementation theo ba gate đã duyệt và ghi prompt/artifact trong prompt register/process log.
2. Chạy dependency scan, PostgreSQL migration test và E2E nếu tiêu chí môn học yêu cầu.
3. Cập nhật testing/code/security reports theo implementation mới.
4. Người dùng kiểm chứng và duyệt Release Gate.
