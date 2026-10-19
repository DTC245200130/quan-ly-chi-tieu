# Skill — danh mục và truy vết

Skill thực thi tiếp tục ở `.agents/skills`; không sao chép thành một bộ SKILL.md thứ hai. Danh mục hiện tại gồm 17 skill với prompt tương ứng; các reference chuyên sâu được nạp theo nhiệm vụ.

| Prompt | Skill | Vai trò | Phần SDLC hỗ trợ |
|---|---|---|---|
| [AIP-REQ-001](prompts.md#aip-req-001) | [requirements-analysis](../../.agents/skills/requirements-analysis/SKILL.md) | Phân tích yêu cầu | Requirements |
| [AIP-ARCH-001](prompts.md#aip-arch-001) | [architecture-design](../../.agents/skills/architecture-design/SKILL.md) | Thiết kế kiến trúc | Design |
| [AIP-DB-001](prompts.md#aip-db-001) | [database-design](../../.agents/skills/database-design/SKILL.md) | Thiết kế dữ liệu | Design |
| [AIP-IMPL-001](prompts.md#aip-impl-001) | [implementation](../../.agents/skills/implementation/SKILL.md) | Triển khai | Coding |
| [AIP-TEST-001](prompts.md#aip-test-001) | [testing](../../.agents/skills/testing/SKILL.md) | Kiểm thử | Testing / quality |
| [AIP-REVIEW-001](prompts.md#aip-review-001) | [code-review](../../.agents/skills/code-review/SKILL.md) | Rà soát mã | Testing / quality |
| [AIP-SEC-001](prompts.md#aip-sec-001) | [security-review](../../.agents/skills/security-review/SKILL.md) | Rà soát bảo mật | Testing / quality |
| [AIP-DOC-001](prompts.md#aip-doc-001) | [documentation](../../.agents/skills/documentation/SKILL.md) | Tài liệu | Xuyên suốt vòng đời |
| [AIP-DEPLOY-001](prompts.md#aip-deploy-001) | [deployment](../../.agents/skills/deployment/SKILL.md) | Vận hành | Deployment |
| [AIP-EVAL-001](prompts.md#aip-eval-001) | [ai-evaluation](../../.agents/skills/ai-evaluation/SKILL.md) | Đánh giá AI | AI Engineering / Evaluation |
| [AIP-UML-001](prompts.md#aip-uml-001) | [uml-diagrams](../../.agents/skills/uml-diagrams/SKILL.md) | Mô hình hóa và xuất ảnh UML | Design / Documentation |
| [AIP-DEBUG-001](prompts.md#aip-debug-001) | [debugging](../../.agents/skills/debugging/SKILL.md) | Chẩn đoán lỗi | Tác vụ chuyên biệt |
| [AIP-IMPACT-001](prompts.md#aip-impact-001) | [change-impact-analysis](../../.agents/skills/change-impact-analysis/SKILL.md) | Phân tích ảnh hưởng | Tác vụ chuyên biệt |
| [AIP-API-001](prompts.md#aip-api-001) | [api-design](../../.agents/skills/api-design/SKILL.md) | Thiết kế API | Tác vụ chuyên biệt |
| [AIP-MIGRATE-001](prompts.md#aip-migrate-001) | [database-migration](../../.agents/skills/database-migration/SKILL.md) | Migration database | Tác vụ chuyên biệt |
| [AIP-DOCBUILD-001](prompts.md#aip-docbuild-001) | [document-production](../../.agents/skills/document-production/SKILL.md) | Tạo Word/PDF | Tác vụ chuyên biệt |
| [AIP-RELEASE-001](prompts.md#aip-release-001) | [release-readiness](../../.agents/skills/release-readiness/SKILL.md) | Đánh giá phát hành | Tác vụ chuyên biệt |

`implementation` là quy trình coding theo prompt: làm rõ hành vi → khảo sát → khoanh vùng → sửa → kiểm chứng. `uml-diagrams` chuyên mô hình/ký hiệu/render; `document-production` chuyên dàn trang và xuất Word/PDF; `documentation` chịu nội dung và tính nhất quán. `database-design` thiết kế schema, `database-migration` thực thi chuyển đổi, `deployment` vận hành. Không tự chạy cả chuỗi khi nhiệm vụ chỉ cần một phần.

## Chọn skill theo yêu cầu

| Yêu cầu | Phối hợp khi cần |
|---|---|
| Tìm nguyên nhân lỗi | debugging; chỉ dùng implementation nếu yêu cầu gồm sửa |
| Đổi tính năng qua nhiều tầng | change-impact-analysis → implementation + testing |
| Thiết kế endpoint | api-design; implementation khi được giao xây dựng |
| Chuyển schema | database-design → database-migration; deployment nếu chạy môi trường thật được giao |
| Báo cáo Word có UML | documentation + uml-diagrams + document-production |
| Kiểm tra trước phát hành | release-readiness; không tự chuyển sang deploy |
| Cải thiện frontend/UX | impeccable nếu có trong môi trường + implementation; không tạo skill UI trùng lặp |

Các skill requirements-analysis, testing, deployment, code-review và security-review có reference chuyên sâu được dẫn ngay trong SKILL.md. Chỉ đọc reference ứng với tác vụ.

Các prompt nằm trong mục tương ứng theo ID; đường dẫn prompt dùng các neo ID ổn định. Tiêu chí chung là E1–E5 trong [Evaluation](evaluation.md), cộng kiểm chứng riêng trong từng prompt. Skill quy định cách làm; prompt xác định lần làm cụ thể; vai trò không cấp thêm quyền tác động.
