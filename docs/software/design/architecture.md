# Kiến trúc tổng quan Sổ Chi Tiêu

> Thiết kế mục tiêu theo baseline requirements v1.1 đã được phê duyệt tại Requirements Gate ngày 06/09/2026. Tài liệu này không xác nhận implementation hiện tại đã đáp ứng thiết kế và không thay đổi trạng thái Human Gate.

Artifact UML liên quan:

- [Use Case tổng quan](../../diagrams/uml/use-case-overview/use-case-overview.png): giữ nguyên 11 use case ban đầu và chỉ tách “Đăng nhập và đăng xuất” thành hai use case, tạo thành đúng 12 use case; dùng một tác nhân **Người sử dụng** theo RQ-009.
- [Class Diagram — As-built](../../diagrams/uml/class-as-built/class-as-built.png): 9 entity ORM và các module router đang thực thi thao tác. `User` chỉ biểu diễn dữ liệu tài khoản đã đăng ký; các hàm xác thực thuộc `AuthRouter`, không phải phương thức của entity.

Các sơ đồ này đồng bộ cách mô tả với mã hiện tại và RQ-009; chúng không thay đổi kiến trúc, schema hoặc trạng thái Human Gate.

## 1. Phạm vi và nguyên tắc

Kiến trúc bao phủ React/PWA, Windows Tauri, FastAPI, SQLAlchemy/Alembic, PostgreSQL production, SQLite development, Gemini, Resend và avatar storage. Offline, ngân hàng, thanh toán, đầu tư tự động, AI sửa dữ liệu và quản trị nằm ngoài phạm vi.

- Backend là nguồn sự thật duy nhất; cả hai client online-only và dùng chung API/dữ liệu máy chủ.
- Mọi dữ liệu nghiệp vụ được lọc theo `user_id` của principal đã xác thực, không tin `user_id` từ client.
- Gemini chỉ nhận dữ liệu tổng hợp, tối thiểu hóa, loại định danh; không truy cập database hay mutation.
- Tiền dùng decimal, VND, làm tròn nhất quán đến một chữ số thập phân tại lớp nghiệp vụ.
- Kỳ nghiệp vụ dùng `Asia/Ho_Chi_Minh`; production schema chỉ đổi qua Alembic.

## 2. System context và trust boundaries

```text
[Browser/PWA] --TLS--\
                       [Reverse proxy/TLS] --> [FastAPI]
[Windows Tauri] -TLS--/                    /       |       \
                                     SQLAlchemy   HTTPS    HTTPS
                                         v         v        v
                                   [PostgreSQL] [Gemini] [Resend]
                                         |
                                  [Avatar storage]
                                         |
                                   [Backup system]
```

1. **Client → public edge:** thiết bị, input, bearer token và upload đều không đáng tin; validate schema/file và không trả stack trace.
2. **Proxy → FastAPI:** chỉ tin forwarded header từ proxy cấu hình; `/api/*` không được SPA fallback.
3. **FastAPI → persistence:** tài khoản DB có quyền tối thiểu; application bắt buộc user-scope, constraint DB chỉ là phòng vệ bổ sung.
4. **FastAPI → Gemini:** chỉ AI privacy gateway được gọi model; payload HTTPS và qua allow-list.
5. **FastAPI → Resend:** chỉ email adapter gửi reset mail; secret chỉ tồn tại phía server.
6. **FastAPI → avatar/backup:** server sinh storage key; storage và backup là vùng dữ liệu cá nhân có access control và retention.

## 3. Thành phần và trách nhiệm

| Thành phần | Trách nhiệm | Giới hạn/phụ thuộc |
|---|---|---|
| React presentation | Route/form, dashboard/report/assistant, loading/error/focus, định dạng VND | Không chứa business DB; không báo mutation thành công trước server response |
| PWA shell | Cài đặt và cache app shell/static assets | Không cache `/api/*`, `/uploads/*` hay dữ liệu nghiệp vụ; không phải offline mode |
| Tauri shell | Đóng gói React cho Windows, gọi HTTPS API | Không local DB/sync; native capability tối thiểu |
| Shared API/auth client | Bearer token, lỗi mạng, dọn phiên khi token hết hạn/account bị xóa | Không tự quyết authorization |
| FastAPI delivery | Router/schema/auth dependency/error mapping, SPA build, health/readiness | Không bỏ qua application service/user scope |
| Identity service | Register/login/profile/reset/re-auth/delete; case-insensitive identity; bcrypt/JWT | Không tự thêm revoke/đa thiết bị chưa được yêu cầu |
| Finance services | Category/transaction/budget/goal, invariant, decimal/time policy, transaction boundary | Mọi repository call nhận current user |
| Analytics service | Dashboard/report theo kỳ, income/expense/net/comparison | Lọc user trước aggregate |
| AI orchestration | Conversation history; aggregate/evidence/period/confidence; gọi gateway | Read-only với tài chính; model output không thành command |
| Gemini privacy gateway | Allow-list, loại identity/note/raw transaction/internal ID/custom category name, timeout/error | HTTPS; Gemini key chỉ server |
| Resend adapter | Gửi reset link có hạn, ổn định hóa lỗi vendor | Không lộ secret/stack trace |
| SQLAlchemy repositories | Persistence có tenant scope và atomic transaction | Production PostgreSQL |
| Alembic boundary | Version schema, preflight collision/duplicate | Dừng và báo cáo; không tự sửa/xóa conflict |
| Avatar adapter | Store/read/delete bằng server key; ownership metadata trong DB | Policy file/access URL cần Human Gate |
| Operations | Logs/metrics/probes/alert/correlation, backup/restore | Không log password/token/key/payload bị cấm |

## 4. API và quy tắc ứng dụng

API chia theo capability: auth/profile, categories, transactions, budgets, goals, dashboard, reports, assistant/conversations, health/readiness và avatar thuộc profile. Đây là ranh giới trách nhiệm, không ấn định URL.

Luồng chung: **route validation → authentication → application service → user-scoped repository → database transaction → response schema**. ID không thuộc user hiện tại trả 404/401 theo AC-002 và không tiết lộ tồn tại.

- Category: trim và so khớp case-insensitive trong `(user, type)`; application validation cộng database uniqueness chống race.
- Budget: năm 2000–2100, category chi cùng user; `spent/is_over` từ transaction cùng user/tháng Hà Nội.
- Goal deposit/withdraw/complete: một DB transaction; kiểm tra số dư khả dụng/số đã dành, chỉ ghi history khi toàn bộ invariant hợp lệ.
- Dashboard/report: user filter trước aggregate; dùng chung finance/time/rounding policy.
- Account deletion: re-authentication + confirmation; hard-delete active data thuộc user, dọn avatar/session/client token-cache; backup hết retention tối đa 30 ngày.

## 5. Data flows

### Authentication và password reset

Client gửi credential qua HTTPS. Identity service chuẩn hóa định danh case-insensitive, kiểm bcrypt và phát access token có expiry. Auth dependency kiểm signature/expiry trên endpoint bảo vệ; token hết hạn bị từ chối và client xóa phiên. Reset artifact có hạn được lưu ở dạng không thể khôi phục trực tiếp rồi gửi qua Resend. Lifetime/single-use chưa được định lượng nên cần Human Gate trước thiết kế chi tiết.

### Mutation tài chính

Client gửi command nhưng không gửi authoritative user ID. API lấy principal từ token, validate và gọi service. Service đọc mọi dependency trong cùng user scope, kiểm invariant và commit atomically. Chỉ response sau commit xác nhận thành công; khi mất mạng client có thể giữ input trong memory để retry thủ công, không tạo outbox/sync.

### Dashboard/report và Gemini

Analytics lọc user và kỳ Hà Nội rồi tạo aggregate decimal. Dashboard/report trả aggregate cho client. Với assistant, orchestration tạo context có kỳ, aggregate, evidence và confidence; privacy gateway kiểm allow-list và chặn trường bị cấm trước khi gửi Gemini qua HTTPS. Gemini trả text tư vấn; lịch sử thuộc user được lưu nhưng output không kích hoạt mutation. Lỗi/timeout/chưa cấu hình được ánh xạ thành thông báo ổn định.

### Avatar

API xác thực user và file, sinh storage key, lưu ownership/metadata rồi thay profile reference. Read/delete phải kiểm ownership hoặc dùng URL có kiểm soát. Thay avatar/xóa account dọn object; backup tuân thủ retention 30 ngày. MIME, size, quota, transform và URL policy chưa đủ requirement.

## 6. Dữ liệu và consistency

- PostgreSQL là production database; SQLite chỉ development và không là bằng chứng duy nhất cho migration/concurrency/constraint production.
- Mỗi bảng nghiệp vụ có ownership trực tiếp hoặc đường ownership không mơ hồ tới user; join/aggregate giữ predicate này.
- Multi-step goal funding và account deletion dùng transaction. Isolation/locking cụ thể do database design xác nhận từ race condition.
- Không dùng binary float cho tiền. Một shared policy thực hiện decimal/VND/rounding một chữ số; rounding mode cụ thể cần xác nhận nếu ảnh hưởng business result.
- Timestamp production lưu instant có timezone, chuyển `Asia/Ho_Chi_Minh` khi xác định kỳ và ngày cuối tháng.
- Migration preflight identity collision/category-budget duplicate/conflict; upgrade dừng với báo cáo có thể xử lý, không tự sửa/xóa.

## 7. Security và privacy

- Password chỉ lưu bcrypt hash; bearer JWT có hạn và được kiểm signature/expiry server-side.
- Authorization default-deny; principal lấy từ token và object lookup luôn kèm `user_id`.
- JWT/DB/Gemini/Resend/storage secret chỉ từ environment/secret injection và được redact.
- CORS, CSP, proxy trust và Tauri capability theo least privilege của môi trường.
- Gemini xử lý plaintext đã tối thiểu hóa tại endpoint, nên chỉ cam kết encryption in transit, không tuyên bố end-to-end encryption.
- Active account data hard-delete; immutable backup chứa dữ liệu đã xóa phải hết hạn trong tối đa 30 ngày và có evidence vận hành.

## 8. Deployment và observability

Production gồm TLS reverse proxy, FastAPI stateless, PostgreSQL, persistent avatar storage và backup lifecycle. FastAPI phục vụ React build; API/probe/upload được match trước và không fallback HTML. Tauri dùng cùng public HTTPS API.

- Liveness chứng minh process hoạt động; readiness phản ánh dependency bắt buộc (tối thiểu database).
- Structured logs gồm timestamp, severity, route/status/latency, correlation ID; không có payload/secret nhạy cảm.
- Metrics: request/error/latency, DB pool, Gemini/Resend latency-error và readiness.
- Backup gồm DB/avatar, restore drill và expiry ≤30 ngày. Frequency/RPO/RTO chưa được duyệt.
- `<10 giây` được đo end-to-end ở tải bình thường; dataset, concurrency và percentile chưa rõ nên chưa thể tạo release test đầy đủ.

## 9. Quyết định, rationale và trade-off

| Quyết định | Rationale | Trade-off |
|---|---|---|
| Hosted backend/source of truth | Nhất quán web/Windows, đúng online-only | Phụ thuộc Internet và server availability |
| Application service + user-scoped repository | Một nơi thực thi invariant/isolation | Thêm abstraction và discipline query |
| PostgreSQL prod, SQLite dev | Constraint/concurrency prod và dev nhanh | Phải test PostgreSQL riêng |
| Aggregate-only Gemini gateway | Giảm dữ liệu lộ, giữ AI read-only | Ít ngữ cảnh, cần contract evidence/confidence |
| Avatar ngoài relational DB | Tách binary khỏi transaction store | Lifecycle/backup/cleanup phức tạp hơn |
| Expiring JWT | Stateless và dùng chung clients | Không revoke sớm nếu không bổ sung state |
| Không offline persistence/sync | Đúng baseline, tránh conflict/security complexity | Mất mạng chỉ có báo lỗi/giữ input tạm |

Chi tiết tại `docs/software/design/architecture-decisions.md`; mọi ADR là `PROPOSED` chờ con người xem xét.

## 10. Traceability requirement → component

| Requirement | Component chính | Hỗ trợ/evidence kiến trúc |
|---|---|---|
| FR-AUTH-001 | Identity service, auth/profile API | React auth/profile, user repo, avatar adapter |
| FR-AUTH-002 | Identity service, Resend adapter | Reset artifact persistence, auth UI |
| FR-AUTH-003 | Identity service, user repo | Normalization, DB uniqueness, migration preflight |
| FR-CAT-001 | Category service/API | User-scoped repo, constraint, React page |
| FR-TXN-001 | Transaction service/API | User-scoped repo, filter UI |
| FR-BUD-001 | Budget service/API | Finance/time policy, transaction aggregate, constraints |
| FR-GOAL-001 | Goal service/API | Atomic transaction, history repo, React page |
| FR-DASH-001 | Analytics/dashboard API | Finance/time policy, dashboard UI |
| FR-REP-001 | Analytics/report API | Finance/time policy, report UI |
| FR-AI-001 | AI orchestration/API | Conversation repo, UI, Gemini gateway |
| FR-AI-002 | AI orchestration + privacy gateway | Aggregate/evidence/confidence schema, read-only boundary |
| FR-DATA-001 | Account deletion service | Cascades, avatar/client cleanup, backup lifecycle |
| FR-REL-001 | FastAPI host/deployment edge | SPA exclusions, probes, PWA/Tauri packaging |
| FR-CONN-001 | Shared API client/connection UI | Online-only shells, no local business persistence |

BR-001/002 thuộc service + DB constraint; BR-003 thuộc Alembic preflight; BR-004/NFR-PRIV-003 thuộc deletion/backup; NFR-SEC-001/003 thuộc auth + scoped repo; NFR-SEC-002 thuộc secret injection/redaction; NFR-PRIV-001/002 thuộc privacy gateway + TLS; NFR-DATA-001/002 thuộc persistence/finance policy; NFR-TIME-001 thuộc time policy; NFR-REL-001/002 và NFR-PERF-001 thuộc error mapping/operations; NFR-TEST-001 thuộc test boundaries backend/frontend/build; NFR-UX-001 thuộc React presentation.

## 11. Rủi ro và câu hỏi cần Human Gate

| ID | Rủi ro/câu hỏi chưa đủ requirement | Gate cần quyết định |
|---|---|---|
| ARCH-HG-001 | “Tải bình thường” thiếu concurrency, dataset, percentile và môi trường đo | Architecture/Release: workload cho AC-015 |
| ARCH-HG-002 | Gần 24/7 và incident 24h thiếu SLI/SLO, severity, on-call | Architecture/Release |
| ARCH-HG-003 | Backup thiếu frequency, RPO/RTO, restore test/evidence expiry | Architecture/Release |
| ARCH-HG-004 | Accessibility thiếu WCAG level/browser/device matrix | Architecture/Release |
| ARCH-HG-005 | Reset token thiếu lifetime, single-use/invalidation | Requirements/Security |
| ARCH-HG-006 | Avatar thiếu MIME, size, quota, transform, URL/malware policy | Requirements/Security/Architecture |
| ARCH-HG-007 | JWT thiếu revoke sớm/đa thiết bị và client storage policy | Requirements/Security |
| ARCH-HG-008 | Conversation history chưa có retention ngoài account deletion | Requirements/Privacy |
| ARCH-HG-009 | AI confidence/evidence chưa có scale/format/threshold | Requirements/Architecture |
| ARCH-HG-010 | Re-auth khi xóa account thiếu recent-auth window/phương thức | Requirements/Security |

Các điểm này chặn thiết kế chi tiết/kiểm thử tương ứng và không được triển khai bằng rule tự đặt. Chỉ người có thẩm quyền được cập nhật Architecture Gate trong `docs/governance/human-gates.md`.
