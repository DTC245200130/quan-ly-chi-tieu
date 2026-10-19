# Tài liệu dự án

Tổ chức theo mục đích; nguồn chính của mỗi tài liệu chỉ có một bản. Việc sắp xếp thư mục không thay đổi yêu cầu nghiệp vụ, trạng thái phê duyệt hoặc bằng chứng kiểm thử.

| Nhóm | Nội dung và điểm bắt đầu |
|---|---|
| **Phần mềm — yêu cầu** | [Requirements](software/requirements/requirements.md), [quyết định/issue](software/requirements/requirements-issues.md), [user stories](software/requirements/user-stories.md), [AC](software/requirements/acceptance-criteria.md), [yêu cầu khách hàng](software/requirements/customer-requirement.md) |
| **Phần mềm — thiết kế** | [Kiến trúc](software/design/architecture.md), [ADR](software/design/architecture-decisions.md), [database](software/design/database-design.md), [API](software/design/api.md), [backend](software/design/backend-design.md), [frontend](software/design/frontend-design.md), [trợ lý Gemini](software/design/assistant-design.md), [stack](software/design/technology-stack.md) |
| **Phần mềm — kiểm thử/review** | [Kế hoạch test](software/testing/test-plan.md), [kết quả test](software/testing/test-report.md), [hộp trắng](software/testing/white-box-test-report-2026-08-31.md), [code review](software/testing/code-review.md), [security review](software/testing/security-review.md) |
| **Phần mềm — vận hành/sử dụng** | [Triển khai](software/deployment/deployment.md), [Azure](software/deployment/azure-deploy.md), [hướng dẫn người dùng](software/user-guide.md) |
| **Quản lý SDLC dùng chung** | [Human gates](governance/human-gates.md), [audit tuân thủ](governance/sdlc-compliance-audit.md) |
| **AI Engineering** | [Tổng quan](ai-engineering/README.md), [skill registry](ai-engineering/skills.md), [prompt mẫu](ai-engineering/prompts.md), [context](ai-engineering/context.md), [evaluation](ai-engineering/evaluation.md) |
| **Lịch sử AI** | [Prompt thực tế](ai-engineering/history/prompts.md), [nhật ký](ai-engineering/history/ai-process-log.md), [thư viện prompt hợp nhất](ai-engineering/prompts.md), [bản ghi xây dựng/kiểm chứng](ai-engineering/runs) |
| **Artifact xuất bản** | [Sơ đồ](diagrams), [Word và tài liệu xuất](outputs) |

## Quy ước lưu

- Yêu cầu/thiết kế/test/vận hành sản phẩm vào software theo nhóm tương ứng. Trợ lý Gemini là tính năng sản phẩm, nên tài liệu thiết kế của nó thuộc software/design.
- Prompt, context, hướng dẫn agent và bằng chứng xây dựng bộ AI vào ai-engineering. Run kiểm tra hành vi agent thực tế theo hướng dẫn tại [evaluations](../evaluations/README.md).
- Gate/audit quản lý cả hai nhánh vào governance. Không coi agent đánh giá đạt là con người đã phê duyệt.
- diagrams và outputs giữ nguyên vị trí để công cụ xuất tài liệu tiếp tục hoạt động. Chúng chứa kết quả sản phẩm; việc AI tạo ra không tự biến chúng thành AI Engineering.
- [Agent profiles](../agents/README.md), [.agents/skills](../.agents/skills), [evaluations](../evaluations/README.md) tiếp tục ở root; không sao chép vào docs.
- Giữ ngày và nội dung lịch sử. Khi sắp xếp lại, chỉ chuẩn hóa đường dẫn tham chiếu; không biến kết quả cũ thành kiểm chứng phiên bản mới.

Các đường dẫn docs/*.md cũ đã chuyển vào nhóm tương ứng; cập nhật bookmark theo bảng trên. Mã nguồn, database, config chạy và dữ liệu người dùng không di chuyển.
