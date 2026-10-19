# Agent profiles — AI-Augmented SDLC

Tổ chức theo tài liệu SDLC HIỆN ĐẠI.docx người dùng cung cấp ngày 21/09/2026. Đây là hồ sơ vai trò và giao việc; chưa có bộ điều phối thực thi tự động.

Mỗi thư mục requirement/design/coding/testing/critic/deployment gồm:
- prompt.md: mẫu giao nhiệm vụ cụ thể, điền đầu vào/phạm vi trước khi chạy.
- skill.md: mapping tới registry dùng chung, không sao chép SKILL.md.
- config.yaml: cấu hình khai báo v1, đường dẫn tương đối từ root repository.

Registry duy nhất là [.agents/skills](../.agents/skills). Reference chi tiết tiếp tục nằm cạnh skill. Context chung tại [context](../docs/ai-engineering/context.md), prompt chuyên biệt tại [thư viện](../docs/ai-engineering/prompts.md). Vai trò tài liệu/Word và UML dùng skill dùng chung khi nhiệm vụ cần, không bắt buộc tạo agent riêng.

## Cách thực hiện

Chọn profile phù hợp và điền đủ các trường trong `prompt.md`: skill bắt buộc, skill bổ trợ nếu cần, nhiệm vụ, đầu vào/phiên bản, chế độ, phạm vi đọc, phạm vi ghi/tác động, phần giữ nguyên và tiêu chí hoàn tất. Agent phải đọc đầy đủ `SKILL.md` được chỉ định trước khi thực hiện; không nạp mọi skill. Khi yêu cầu chỉ chẩn đoán, review hoặc lập kế hoạch, chế độ đó ưu tiên hơn tên vai trò. Có thể bỏ qua các giai đoạn không cần thiết. Critic rà soát artifact theo loại; không bắt requirements phải qua code-review.

Bàn giao input/version, quyết định, file đầu ra, checks và giới hạn. Critic REVISE trả về tác vụ cần sửa trong phạm vi đã giao; không có vòng retry tự động vô hạn. ACCEPT không thay human approval và không kích hoạt deploy. Việc chạy nhiều agent chỉ khi được giao rõ; các profile không tự cấp quyền spawn.

## Version và cấu hình thực tế

schema_version là phiên bản cấu trúc config; profile_version là phiên bản nội dung profile. Git quản lý prompt, skill, config và case evaluation cùng nhau. Chưa commit thì ghi dirty state và hash file thực tế khi chạy, không bịa commit/tag.

model.id, model.version và sampling.temperature mặc định null vì chưa chọn runtime. Không tự lấy model Gemini của ứng dụng làm model cho agent phát triển. Config không đổi model của phiên chat. Trước mỗi lần chạy, ghi model/settings/tools thực tế nếu biết; nếu không, ghi unknown. requested_model khác actual_model phải được thể hiện.

execution_mode=manual và tools.capabilities_required là mô tả nhu cầu, không phải tên API hay permission thực thi. Phiên bản tool thực tế lưu ở run record. Prompt/skill/input/output được nhận diện bằng path và Git revision hoặc SHA-256; config không giả định mọi skill có cùng version.

## Liên hệ cấu trúc dự án

| Cấu trúc tham khảo | Vị trí hiện có |
|---|---|
| requirements/ | docs/software/requirements/ |
| design/ | docs/software/design/ và docs/diagrams/ |
| src/ | app/ và frontend/src/ |
| tests/ | tests/ và frontend/src với các file test |
| deployment/ | deploy/, Dockerfile, compose*.yaml, docs/software/deployment/deployment.md |
| agents/ | Thư mục này |
| skills registry | .agents/skills/ |
| evaluations/ | [Ca và hồ sơ đánh giá](../evaluations/README.md) |

Giữ đường dẫn phần mềm để không phá import/build/deploy. Bản mapping này là cách áp dụng cấu trúc tài liệu cho repository hiện tại.
