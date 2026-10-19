# Bản ghi xây dựng AI Engineering — 20/09/2026

## Yêu cầu và phạm vi

Người dùng yêu cầu bắt đầu từ skills và prompt theo nhánh AI Engineering trong ảnh: Prompt, Skill, Agent, Context, Evaluation; chưa sửa SRS hoặc hệ thống, không tái cấu trúc nhánh Traditional Software.

Nguồn: yêu cầu trực tiếp và ảnh trong hội thoại, 8 skill hiện hữu, phần TP-* kế thừa nay được hợp nhất trong docs/ai-engineering/prompts.md, docs/ai-engineering/history/prompts.md, docs/ai-engineering/history/ai-process-log.md và RQ-009. Skill dùng để xây dựng bộ này: skill-creator; nguyên tắc documentation dùng để phân biệt hiện trạng, mục tiêu và evidence. Các mẫu AIP-* mới chưa được chạy để sửa sản phẩm.

## Kết quả tạo artifact

- Giữ 8 skill hiện hữu, bổ sung hợp đồng phạm vi và liên kết prompt; thêm deployment và ai-evaluation.
- Tạo 10 prompt mẫu AIP-* có nhiệm vụ, context, phạm vi, đầu ra và kiểm chứng, mapping một-một với 10 skill dự án.
- Mô tả vai trò Agent và cách bàn giao; không cấu hình runtime hoặc khởi chạy nhiều agent.
- Tạo Context theo nguồn sự thật và Evaluation gồm rubric E1–E5, 9 ca hành vi.
- Không sửa SRS, sơ đồ, mã ứng dụng, database, migration, test sản phẩm hoặc human gate. RQ-009 đã được ghi từ lượt trước; các thư mục docs/diagrams, docs/outputs và scripts đã có ở working tree trước tác vụ này.

## Kiểm chứng

Evaluator: agent thực hiện, self-review; không phải đánh giá độc lập.
Môi trường: workspace Windows/PowerShell, Python với PYTHONUTF8=1.

| Kiểm tra | Kết quả | Bằng chứng/giới hạn |
|---|---|---|
| Frontmatter và tên 10 skill | PASS | Chạy quick_validate.py của skill-creator cho từng thư mục .agents/skills; 10/10 trả Skill is valid |
| Liên kết nội bộ | PASS | PowerShell kiểm tra 71 đích liên kết trong bộ AI Engineering và skills, cùng các neo AIP; lần đầu thiếu bản ghi này, kiểm tra lại đã đạt |
| Diff và phạm vi file | PASS | git diff --check không có lỗi whitespace; git status/diff xác nhận thay đổi mới thuộc skills, AI Engineering và liên kết trong thư viện prompt; thay đổi RQ-009 và artifact có sẵn được giữ nguyên |
| AE-01 đến AE-09 | NOT RUN | Đã thiết kế ca; chưa thực thi agent trên bộ ca |
| E1–E5 cho hành vi agent | NOT RUN | Không suy ra điểm từ việc instruction có đủ nội dung |
| Test/build sản phẩm | NOT RUN | Không thay đổi mã sản phẩm |

Kết quả hiện tại là bộ nền tảng có thể review và sử dụng, không phải bằng chứng AI đã đạt evaluation hoặc sản phẩm đã sẵn sàng production. Khi thay đổi skill/prompt dựa trên thực tế sử dụng, chạy các ca liên quan và lưu bản ghi riêng.
