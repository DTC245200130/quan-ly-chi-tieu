# Architecture Decision Records

> Các ADR là đề xuất theo baseline v1.1. `PROPOSED` yêu cầu con người xem xét; tài liệu này không thay đổi Architecture Gate.

## ADR-001 — Một hosted backend cho mọi client

- **Status:** PROPOSED
- **Context:** Web/PWA và Tauri online-only, dùng chung dữ liệu (`FR-REL-001`, `FR-CONN-001`).
- **Decision:** Cùng FastAPI HTTPS API/source of truth; không local business DB, outbox, sync/conflict engine. PWA chỉ cache shell/static.
- **Rationale:** Nhất quán dữ liệu và đúng phạm vi.
- **Trade-off:** Phụ thuộc Internet/backend.

## ADR-002 — React dùng chung, PWA và Tauri là hai shell

- **Status:** PROPOSED
- **Context:** Cần responsive web/PWA và Windows app.
- **Decision:** Một React client; PWA phân phối web, Tauri đóng gói Windows với native capability tối thiểu và HTTPS API.
- **Rationale:** Tránh phân kỳ UX/API.
- **Trade-off:** Desktop không có offline/native data riêng.

## ADR-003 — FastAPI capability modules và application services

- **Status:** PROPOSED
- **Decision:** Router chịu HTTP/schema; service chịu rule/transaction; repository chịu persistence có user scope.
- **Rationale:** Tập trung invariant, tăng testability/isolation.
- **Trade-off:** Thêm boundary và dependency discipline.

## ADR-004 — User isolation ở application và persistence

- **Status:** PROPOSED
- **Context:** `NFR-SEC-001`, `AC-002`.
- **Decision:** Principal chỉ từ token; mọi repo lookup/aggregate kèm user ID; ownership/FK/unique constraint là defense-in-depth; cross-user ID trả 404/401.
- **Rationale:** Chống horizontal authorization bypass.
- **Trade-off:** Query/test phức tạp hơn; shared schema không là physical isolation.

## ADR-005 — Expiring JWT và bcrypt

- **Status:** PROPOSED
- **Decision:** Server kiểm signature/expiry của bearer access token; client xóa phiên khi token hết hạn. Password chỉ lưu bcrypt hash; secrets chỉ server environment.
- **Rationale:** Stateless, dùng chung clients.
- **Trade-off:** Không tự thêm revoke sớm/refresh/đa thiết bị khi requirement chưa có.

## ADR-006 — PostgreSQL production, SQLite development

- **Status:** PROPOSED
- **Decision:** Alembic là schema authority production, tiền là decimal; SQLite không là evidence duy nhất cho migration/locking/constraint.
- **Rationale:** Production integrity và local loop nhanh.
- **Trade-off:** Cần test PostgreSQL riêng.

## ADR-007 — Shared money/time policy

- **Status:** PROPOSED
- **Decision:** Application dùng một decimal/VND/rounding-one-decimal policy và một `Asia/Ho_Chi_Minh` month-boundary policy.
- **Rationale:** Tránh lệch giữa endpoint/client.
- **Trade-off:** Client không tính authoritative result; rounding mode cần Human Gate nếu ảnh hưởng business result.

## ADR-008 — Gemini privacy gateway aggregate-only/read-only

- **Status:** PROPOSED
- **Decision:** Aggregate sau user filter; allow-list loại identity, note, raw transaction, internal ID, custom category name; HTTPS; output chỉ là advice, không command.
- **Rationale:** Data minimization và AI không sửa dữ liệu.
- **Trade-off:** Ít ngữ cảnh; evidence/confidence contract còn mở.

## ADR-009 — Resend sau email adapter

- **Status:** PROPOSED
- **Decision:** Identity service tạo reset artifact; adapter gọi Resend HTTPS và map timeout/error; key chỉ server.
- **Rationale:** Cô lập vendor và dễ test.
- **Trade-off:** Vendor availability; reset lifetime/single-use còn cần Human Gate.

## ADR-010 — Avatar ngoài relational database

- **Status:** PROPOSED
- **Decision:** Server sinh object key; DB giữ ownership/metadata; adapter store/read/delete, kiểm user và tham gia deletion/backup lifecycle.
- **Rationale:** Tách binary khỏi PostgreSQL.
- **Trade-off:** Orphan/reconciliation; file/access policy còn mở.

## ADR-011 — Account deletion hard-delete lifecycle

- **Status:** PROPOSED
- **Decision:** Online, re-auth + confirmation; xóa/cascade active relational data, conversations/avatar, kết thúc phiên, client dọn token/cache; backup expiry tối đa 30 ngày có evidence.
- **Rationale:** Đáp ứng `FR-DATA-001`, `BR-004` và bảo vệ user khác.
- **Trade-off:** Không phục hồi; immutable backup không xóa chọn lọc tức thì; re-auth/RPO/RTO còn mở.

## ADR-012 — TLS edge, stable errors và secret redaction

- **Status:** PROPOSED
- **Decision:** Public HTTPS; external adapter có timeout/error mapping; logs redact credential/token/key/payload cấm. Không tuyên bố E2E encryption với Gemini.
- **Rationale:** Boundary rõ, không lộ stack trace/secret.
- **Trade-off:** Proxy/internal network cần hardening theo môi trường.

## ADR-013 — Health/readiness và observability

- **Status:** PROPOSED
- **Decision:** Tách liveness/readiness; readiness phản ánh dependency bắt buộc. Thu request/error/latency, DB pool, external-call metrics; alert/runbook không chứa dữ liệu nhạy cảm.
- **Rationale:** Routing và chẩn đoán cho mục tiêu reliability.
- **Trade-off:** Probe sâu có thể tạo cascading failure; SLI/SLO/threshold còn mở.

## ADR-014 — SPA fallback loại trừ API

- **Status:** PROPOSED
- **Decision:** API, probes và asset/upload match trước; chỉ navigation route khác mới trả app shell.
- **Rationale:** Deep link hoạt động và giữ API semantics (`AC-008`).
- **Trade-off:** Cần production-routing test.

## ADR-015 — Migration fail-fast khi conflict

- **Status:** PROPOSED
- **Decision:** Preflight báo identity/category/budget collision và dừng trước destructive change; chỉ tiếp tục sau human-approved remediation.
- **Rationale:** Không âm thầm đổi/xóa user data (`BR-003`).
- **Trade-off:** Có thể chặn deployment.

Các mục `ARCH-HG-001`–`ARCH-HG-010` trong `docs/software/design/architecture.md` vẫn mở. Không ADR nào được chuyển khỏi `PROPOSED` nếu chưa có quyết định của người có thẩm quyền.

## ADR-016 — Mức trừu tượng của Class và Sequence Diagram trong ORD

- **Status:** ACCEPTED cho tài liệu ORD ngày 25/09/2026 theo quyết định trực tiếp của người dùng; không phải phê duyệt tái cấu trúc mã.
- **Context:** ORD cần thể hiện thiết kế hướng đối tượng có lớp, thuộc tính và phương thức, trong khi implementation hiện tại phân tán hành vi ở Router/Core. Sequence Diagram liệt kê mọi module/hàm làm hình quá rối.
- **Decision:** Class Diagram ORD là mô hình thiết kế mục tiêu gồm entity có trạng thái/hành vi và các lớp `«control»` cho hành vi liên đối tượng; phải ghi rõ không đồng nhất với Model/Schema/Router hiện tại. Sequence Diagram thao tác dùng đúng bốn lifeline: Người sử dụng, giao diện cụ thể, Backend (Router + Core) và CSDL. Không dùng thành phần `Helper`; tích hợp ngoài được mô tả trong thông điệp Backend khi cần.
- **Rationale:** Giữ đúng mục tiêu thiết kế hướng đối tượng, đồng thời duy trì khả năng đọc và giải thích trong tài liệu học thuật.
- **Trade-off:** Sequence Diagram không truy vết đến từng hàm/module; Class Diagram có thể chứa lớp/phương thức thiết kế chưa tồn tại nguyên dạng trong implementation nên luôn phải mang nhãn thiết kế mục tiêu.
