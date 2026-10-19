# Nhật ký AI-Augmented SDLC

## Phiên 20/09/2026 — Rà soát và chuẩn hóa cấu trúc

- **Yêu cầu:** rà soát toàn bộ hệ thống, đưa `.agents/skills` và `docs` về bộ khung SDLC đã cung cấp, không sửa app và bảo toàn tài nguyên.
- **Phạm vi thay đổi:** chỉ cập nhật evidence trong `docs/software/testing/code-review.md`, `docs/software/testing/security-review.md`, `docs/software/testing/test-report.md`, `docs/ai-engineering/history/ai-process-log.md`; giữ nguyên các tài liệu bổ sung ngoài 13 artifact lõi để tránh mất dữ liệu.
- **Kiểm tra cấu trúc:** đủ 8 skill và đủ 13 artifact lõi đúng tên; không đổi tên repository vì có thể làm hỏng đường dẫn/deployment.
- **Kiểm tra:** Python hệ thống collection fail do thiếu FastAPI; venv pytest 4 failed/71 passed/22 subtests/7 warnings; Vitest 50 passed; Vite/PWA build pass.
- **Integrity evidence:** trước thay đổi, 118 tệp trong `app`, `frontend/src`, `frontend/public`, `frontend/src-tauri`, `alembic`, `tests` có manifest SHA-256 tổng hợp `65A5AF9B438DB1947D0FE07622EB3B8B85CF10B7AB28B96A892361D86E7B119E`. Sau thay đổi phải trùng khớp.
- **Human gate:** không thay đổi approval; Release vẫn `PENDING`. Không sửa source app, migration, test hay tài nguyên runtime.

Tài liệu này bắt đầu ngày 06/09/2026; không tái tạo giả các prompt hoặc human correction trước đó.

Prompt nguyên văn và liên kết artifact được lưu tại `docs/ai-engineering/history/prompts.md`; tài liệu này chỉ giữ tóm tắt quá trình.

## Phiên 06/09/2026 — Đối chiếu hướng dẫn SDLC

- **Prompt người dùng:** đọc file hướng dẫn, đánh giá mức tuân thủ, chỉ ra và bổ sung phần thiếu.
- **Nguồn:** DOCX do người dùng cung cấp; repository; Git log; test/build local.
- **AI artifacts:** bộ project skills; requirements/stories/AC/issues; architecture/ADR/database; gates; test/review/security reports; audit.
- **Tool evidence:** đọc OOXML; `rg`; Git read-only; pytest; Vitest coverage; TypeScript/Vite/PWA build; `apply_patch`.
- **Lỗi AI/tool phát hiện:** pytest thu thập nhầm test trong ignored `deliverables/`.
- **Sửa bởi AI:** thêm `pytest.ini`; bỏ `.agents/` khỏi `.gitignore` để skill có thể quản lý bằng Git.
- **Human corrections:** Đào Minh Tâm phê duyệt Requirements Gate và quyết định RQ-001..RQ-008 ngày 06/09/2026. Baseline được cập nhật; yêu cầu app offline được ghi rõ là chưa được kiến trúc/implementation hiện tại đáp ứng.
- **MCP:** không dùng; dự án không đặt issue/external data source trong phạm vi yêu cầu này. MCP là tùy điều kiện, không nên dùng chỉ để đủ hình thức.

## Phiên 06/09/2026 — Đánh giá kiến trúc offline

- **Human input:** offline cho hầu hết tính năng trừ AI; đánh giá sync; yêu cầu mã hóa, ít nhất dữ liệu gửi AI; xóa toàn bộ tài khoản; phản hồi dưới 10 giây ở tải bình thường.
- **AI assessment:** khả thi nhưng là thay đổi trung bình-cao; implementation hiện chỉ online-first và không có local DB/sync engine.
- **Artifacts cập nhật:** requirements clarification, acceptance criteria, architecture target, ADR-007..010 và issue decisions.
- **Human Gate:** Architecture vẫn `PENDING`; chưa sửa source code.

## Phiên 06/09/2026 — Thu hẹp phạm vi kết nối

- **Human correction:** thay quyết định offline bằng online toàn bộ cho cả web và app; offline chỉ được cân nhắc sau nếu có số lượng lớn phản hồi người dùng.
- **Artifacts cập nhật:** requirements baseline v1.1, story/AC kết nối, RQ-008, architecture và ADR.
- **Scope removed:** local database, outbox, sync engine, conflict handling và mã hóa local không còn thuộc release hiện tại.
- **Human Gate:** Requirements vẫn `APPROVED` theo bản sửa của người duyệt; Architecture vẫn `PENDING`.

## Phiên 06/09/2026 — Architecture Gate

- **Human approval:** Đào Minh Tâm phê duyệt Architecture Gate.
- **Decisions:** online-only cho web/app; shared FastAPI/database; offline ngoài scope; Gemini payload tối thiểu hóa qua HTTPS; backup của tài khoản đã xóa giữ tối đa 30 ngày.
- **Artifacts cập nhật:** human gate, ADR status, privacy requirement/acceptance criterion và architecture note.
- **Next gate:** Database `PENDING`; chưa sửa implementation.

## Phiên 06/09/2026 — Chuẩn bị Database Gate

- **Scope:** review models và migration hiện tại đối chiếu requirements/architecture đã duyệt.
- **Artifact:** cập nhật `docs/software/design/database-design.md` với constraints, indexes, composite ownership FK, cascade/restrict, backup retention và migration plan.
- **Code status:** không sửa Python, TypeScript, SQL migration hoặc database.
- **Human Gate:** Database `PENDING`, chờ bốn quyết định được liệt kê trong database design.

## Phiên 06/09/2026 — Database Gate

- **Human approval:** Đào Minh Tâm phê duyệt Database Gate.
- **Decisions:** category unique theo owner/type/tên chuẩn hóa; năm ngân sách 2000–2100; migration dừng khi có collision; hard delete active data; backup retention tối đa 30 ngày.
- **Artifacts cập nhật:** gate status, database design, business rules và acceptance criteria.
- **Code status:** chưa tạo migration và chưa sửa source code/database.
- **Next gate:** Implementation/testing rồi Release Gate; Release hiện `PENDING`.

## Phiên 06/09/2026 — Bổ sung prompt evidence

- **Human prompt:** hỏi về phần prompt người dùng trong hồ sơ nộp bài.
- **Artifact:** tạo `docs/ai-engineering/history/prompts.md`, ghi nguyên văn các prompt có bằng chứng và liên kết với skill/artifact/gate.
- **Integrity rule:** không tái dựng prompt cho các commit cũ khi transcript không tồn tại.
- **Code status:** không sửa source code.

## Phiên 06/09/2026 — Tạo thư viện prompt mẫu

- **Human authorization:** cho phép bổ sung prompt đầy đủ để hoàn thiện số lượng và hình thức hồ sơ.
- **Artifact:** phần TP-* kế thừa trong `docs/ai-engineering/prompts.md` gồm bảy prompt SDLC có role, context, input, objective, scope, constraints, outputs, verification và stopping/human-gate conditions; nội dung này ban đầu nằm trong `prompt-library.md` trước khi được hợp nhất.
- **Evidence label:** prompt hồi tố/mẫu, chưa thực thi; không được trình bày như prompt tạo implementation cũ.
- **Code status:** không sửa source code.

## Phiên 20/09/2026 — Dọn artifact cục bộ

- **Human prompt:** dọn các file/folder thừa.
- **Phạm vi đã xóa:** cache Python/pytest, frontend coverage/build, và TypeScript build metadata; tất cả đều có thể tái tạo.
- **Phạm vi giữ lại:** dependency (`venv`, `frontend/node_modules`), dữ liệu/runtime (`.env`, `expense.db`, `uploads`), deliverables và file được Git theo dõi.
- **Kiểm chứng:** xem trước bằng `git clean -ndX`, xóa theo đường dẫn giới hạn bằng `git clean -fdX`, rồi kiểm tra lại `git status --short --ignored`.
- **Code status:** không sửa source code; không chạy test vì chỉ xóa artifact sinh tự động.

## Phiên 20/09/2026 — Chuẩn hóa vị trí tài liệu

- **Human prompt:** di chuyển các file Markdown chưa đúng vị trí và cập nhật tham chiếu.
- **Thay đổi:** chuyển báo cáo kiểm thử hộp trắng vào `docs/software/testing/white-box-test-report-2026-08-31.md`; chuẩn hóa hướng dẫn Azure thành `docs/software/deployment/azure-deploy.md`.
- **Đồng bộ:** cập nhật tham chiếu trong README, Compose và các tài liệu liên quan.
- **Kiểm chứng:** tìm tên file cũ trên toàn repository và kiểm tra toàn bộ liên kết Markdown tương đối.
- **Code status:** không sửa hành vi ứng dụng và không chạy test mã nguồn.
