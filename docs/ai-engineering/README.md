# AI Engineering cho Modern SDLC

Bộ nền tảng v1 — 20/09/2026. Cấu trúc theo nhánh bên phải của ảnh người dùng cung cấp: **Prompt, Skill, Agent, Context, Evaluation**. Đây là quy trình AI hỗ trợ phát triển Sổ Chi Tiêu, không phải kiến trúc trợ lý Gemini trong sản phẩm.

Giữ nguyên nhánh Traditional Software: requirements, design, coding, testing, deployment hiện có; không di chuyển mã nguồn hoặc tái cấu trúc database. Đợt này chỉ xây dựng tài sản AI Engineering, chưa thực thi việc sửa SRS/hệ thống theo RQ-009.

## Năm thành phần

Áp dụng cấu trúc trong SDLC HIỆN ĐẠI.docx ngày 21/09/2026: [agents/](../../agents/README.md) chứa sáu profile với prompt.md, skill.md và config.yaml; [evaluations/](../../evaluations/README.md) chứa case JSON theo agent. Registry .agents/skills giữ nguyên làm nguồn dùng chung. Các thư mục phần mềm không di chuyển; mapping nằm trong agents/README.md.

| Thành phần | Nguồn chính | Công dụng |
|---|---|---|
| Prompt | [prompts.md](prompts.md) | Mẫu giao việc, phạm vi, đầu vào, đầu ra và kiểm chứng cho từng skill |
| Skill | [skills.md](skills.md), thư mục [.agents/skills](../../.agents/skills) | Quy trình tái sử dụng; giữ vị trí hiện có |
| Agent | [agents.md](agents.md) | Vai trò, quyền thao tác và thông tin bàn giao |
| Context | [context.md](context.md) | Chọn nguồn sự thật và quyết định áp dụng cho nhiệm vụ |
| Evaluation | [evaluation.md](evaluation.md) | Đánh giá hành vi của AI và chất lượng artifact, tách khỏi test sản phẩm |

## Cách sử dụng

Bản mở rộng ngày 21/09/2026 có 17 skill/prompt, gồm chẩn đoán lỗi, phân tích ảnh hưởng, API, migration, sản xuất Word/PDF và đánh giá phát hành. Xem [danh mục và cách chọn skill](skills.md). Đây là bộ quy trình để áp dụng theo từng prompt, không yêu cầu mọi tác vụ phải đi qua cả 17 skill.

1. Chọn prompt và vai trò tương ứng; điền đủ skill bắt buộc, nhiệm vụ, chế độ, phạm vi đọc/ghi, loại trừ và tiêu chí hoàn tất.
2. Agent đọc đầy đủ `SKILL.md` được chỉ định, context liên quan và chỉ nạp skill bổ trợ khi nhiệm vụ thật sự cần.
3. Thực hiện đúng chế độ: phân tích, đề xuất hoặc thực thi. Prompt mẫu không tự cấp quyền sửa file, triển khai hay chuyển sang bước kế tiếp.
4. Kiểm tra đầu ra bằng tiêu chí của prompt và rubric Evaluation; lưu bằng chứng thực tế.
5. Bàn giao kết quả cùng phần còn thiếu. Con người quyết định nghiệp vụ và release; ghi nhận quyết định đã có, không hỏi lại chỉ vì đổi vai trò.

Một agent có thể đảm nhiệm các vai trò tuần tự. Bộ này không cài đặt bộ điều phối, không khởi chạy subagent và không tự động triển khai production. Production trong ảnh là kết quả cần cả chất lượng phần mềm và chất lượng công việc AI; chỉ có đủ năm thư mục không chứng minh đã sẵn sàng phát hành.

## Quan hệ với hồ sơ cũ

- [Thư viện prompt hợp nhất](prompts.md) giữ cả ID TP-* kế thừa và ID AIP-* hiện hành trong một nguồn duy nhất.
- [Prompt register](history/prompts.md) và [nhật ký AI](history/ai-process-log.md) giữ lịch sử, không dùng mẫu mới để tái dựng các lần chạy cũ.
- [Bản ghi đợt xây dựng này](runs/2026-09-20-foundation.md) phân biệt việc tạo bộ nền tảng, kiểm tra cấu trúc và các ca đánh giá hành vi chưa chạy.
