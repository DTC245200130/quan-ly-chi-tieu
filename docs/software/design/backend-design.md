# Thiết kế backend mục tiêu

> Phạm vi thiết kế chi tiết cho FastAPI/SQLAlchemy, lập từ baseline requirements v1.1 và các Requirements, Architecture, Database Gate đã `APPROVED` ngày 06/09/2026. Tài liệu này không sửa source code, schema, migration hay trạng thái Human Gate; không khẳng định implementation hiện tại đã đáp ứng target.

## 1. Trạng thái và giới hạn quyết định

Thiết kế dưới đây tuân theo `docs/software/requirements/requirements.md`, `docs/software/requirements/acceptance-criteria.md`, `docs/software/design/architecture.md` và `docs/software/design/database-design.md`. Các điểm `ARCH-HG-005`, `ARCH-HG-006`, `ARCH-HG-009` còn mở nên chỉ xác định boundary và hành vi an toàn tối thiểu, không tự đặt giá trị nghiệp vụ. `ARCH-HG-010` đã được RQ-011 chốt theo phương án mật khẩu hiện tại và chuỗi xác nhận trong cùng lệnh xóa:

| Điểm mở | Phần có thể thiết kế | Phần bị chặn đến Human Gate |
|---|---|---|
| Reset password | token ngẫu nhiên, chỉ lưu hash, có expiry, response chống enumeration, email adapter | lifetime cụ thể, single-use/invalidation policy đầy đủ |
| Avatar/upload | authenticated command, server-generated key, content validation, storage adapter, cleanup retry | MIME/size/quota/transform/malware/public-URL policy cụ thể |
| AI evidence/confidence | aggregate-only DTO, allow-list, period/evidence/confidence bắt buộc về mặt cấu trúc | thang đo, threshold và semantics confidence/evidence |
| Re-auth account deletion | `current_password` + xác nhận chính xác `XÓA TÀI KHOẢN` trong cùng `DELETE /auth/me` | Đã chốt tại RQ-011; không dùng proof trung gian hoặc recent-auth window trong baseline này |

Do đó, các endpoint trên có thể được mô tả ở mức contract nhưng chưa được coi là implementation-ready ở phần policy còn mở. Nếu việc triển khai đòi hỏi chọn các giá trị này, phải dừng và đưa lại Requirements/Security/Architecture Gate; không dùng giá trị as-built làm quyết định mặc định.

## 2. Nguyên tắc backend bắt buộc

1. Principal chỉ đến từ access token đã kiểm signature và expiry. Không request DTO nào nhận `user_id` có thẩm quyền.
2. Mọi lookup, list, aggregate, update và delete nghiệp vụ đều có predicate `current_user.id`; child table không có `user_id` phải join qua parent đã user-scope.
3. ID không thuộc current user được trả `404 resource_not_found`, giống ID không tồn tại, để không lộ sự tồn tại của dữ liệu người khác.
4. Router chỉ xử lý HTTP/auth/schema; service sở hữu use case, invariant và transaction; repository sở hữu query/persistence; model không chứa HTTP concern.
5. Service nhận một Unit of Work/session cho toàn use case. Router và repository không `commit()`.
6. Tiền luôn là `Decimal`; không chuyển qua binary float. Storage giữ `NUMERIC(14,2)` theo database design; output tiền authoritative quantize một chữ số thập phân bằng shared money policy trước serialization.
7. Ranh giới tháng dùng `Asia/Ho_Chi_Minh`, dạng nửa mở `[start, next_month_start)`. Không dùng timezone hoặc `date.today()` phụ thuộc máy chủ cho quyết định kỳ.
8. External adapter có timeout, redaction và stable error mapping. Không response/log stack trace, password/hash/token/API key, payload Gemini bị cấm hoặc dữ liệu của user khác.
9. Gemini không nhận session/repository/model và không truy cập database. Chỉ nhận `GeminiAggregateRequest` đã qua privacy allow-list.
10. Mutation chỉ báo thành công sau commit. Rollback toàn bộ khi validation sau đọc, authorization, conflict, persistence hoặc external step thuộc atomic boundary thất bại.

## 3. Module boundaries

Target package có thể giữ `app/routers`, `app/schemas`, `app/models`, đồng thời thêm application/persistence/adapters theo capability. Đây là logical boundary; tên file cụ thể có thể thay đổi miễn dependency rule không đổi.

```text
app/main.py
  -> routers/{auth,profile,categories,transactions,budgets,goals,
              dashboard,reports,assistant,system}.py
       -> schemas/* + core/deps.py + services/*
            -> repositories/* + policies/{money,time,identity,privacy}.py
                 -> SQLAlchemy models + UnitOfWork/session
            -> ports/{email,avatar,gemini}.py
                 -> adapters/{resend,avatar_store,gemini}.py

Allowed: router -> service -> repository/model
         service -> policy/port
         adapter -> external HTTPS/storage
Forbidden: router -> commit; adapter -> repository; Gemini -> database;
           repository -> HTTP; model -> current request/user
```

| Module | Trách nhiệm | Không được làm |
|---|---|---|
| Auth/Profile router | parse credential/bearer/upload, response/status | query nghiệp vụ, commit, tự xóa file |
| IdentityService | register/login/profile/reset/re-auth/delete orchestration | trả password hash, tin user ID từ client |
| CategoryService | normalize name, CRUD, referenced-category policy | query ngoài owner scope |
| TransactionService | CRUD/filter, derive type từ owned category | tin transaction type từ client |
| BudgetService | CRUD, expense-category invariant, spent/is_over | tự tính month boundary khác Analytics |
| GoalService | CRUD items, deposit/withdraw/history/complete atomic | ghi history nếu invariant thất bại |
| AnalyticsService | dashboard/report aggregate sau owner filter | trả aggregate chứa user khác |
| AssistantService | conversation ownership, context, call gateway, history | cho model phát command/mutation |
| Repositories | query có owner scope, locking, persistence primitives | commit, map HTTP error |
| MoneyPolicy | Decimal parse/quantize/serialize VND | dùng float cho tiền |
| TimePolicy | Hanoi today/month bounds | phụ thuộc timezone host |
| GeminiPrivacyGateway | allow-list DTO, serialize aggregate, call model | nhận entity/raw row/note/identity/custom category name |
| EmailPort/ResendAdapter | gửi reset notification, timeout/error classification | log reset token/key |
| AvatarPort/Adapter | stage/finalize/delete/reconcile object bằng server key | expose filesystem path hoặc nhận key từ client |
| ErrorMapper | domain/external/unexpected exception → stable envelope | trả `str(exc)` tùy ý hoặc traceback |

### Sơ đồ endpoint → service → repository/model

```text
/api/auth/*
  -> IdentityService
     -> UserRepository -> User
     -> ResetCredentialRepository -> approved reset persistence
     -> EmailPort -> ResendAdapter

/api/auth/me, /api/auth/me/avatar, /api/auth/me/delete
  -> ProfileService / AccountDeletionService
     -> UserScopedAccountRepository -> User + all owned models
     -> AvatarPort -> avatar storage

/api/categories/* -> CategoryService -> CategoryRepository -> Category
/api/transactions/* -> TransactionService
  -> TransactionRepository + CategoryRepository -> Transaction + Category
/api/budgets/* -> BudgetService
  -> BudgetRepository + TransactionAggregateRepository + CategoryRepository
/api/goals/* -> GoalService
  -> GoalRepository + GoalItemRepository + GoalTransactionRepository
  -> BalanceRepository; optional TransactionRepository on complete(spend)
/api/dashboard/*, /api/reports/* -> AnalyticsService
  -> user-scoped aggregate repositories over Transaction/Category/Budget/Goal
/api/assistant/* -> AssistantService
  -> ConversationRepository -> AIConversation/AIMessage
  -> AnalyticsService -> aggregate DTO -> GeminiPrivacyGateway -> Gemini HTTPS
/api/health, /api/ready -> SystemService -> process check / required DB probe
```

## 4. API conventions

### 4.1 Common contract

- Base path `/api`; protected endpoints require `Authorization: Bearer <access-token>`.
- JSON uses UTF-8. Dates are `YYYY-MM-DD`; timestamps are ISO 8601 with offset/UTC.
- IDs are opaque strings. Client must not infer ownership from them.
- Monetary request fields are JSON decimal numbers or decimal strings accepted by Pydantic without float arithmetic; monetary responses are serialized consistently to one decimal place. Currency is implicitly VND for this baseline.
- Create returns `201`; read/update returns `200`; successful delete without representation returns `204` (no body).
- Validation is `422`; unauthenticated/expired token `401`; owned resource absent or foreign `404`; invariant/uniqueness/state conflict `409`; unsupported media `415`; upload too large `413`.
- List endpoints use stable order. Pagination is not required by approved requirements; adding a mandatory pagination contract would require compatibility review.
- OpenAPI is the field-level authority after implementation; this document is the semantic authority for ownership, errors and transactions.

### 4.2 Endpoint contracts

`Idem.` below names the retry rule from section 7.

| Endpoint | Request / response intent | Service | Tx | Idem. |
|---|---|---|---|---|
| `POST /auth/register` | username, email, password → own public profile | `IdentityService.register` | T1 | K1 |
| `POST /auth/login` | identifier + password → expiring bearer token | `IdentityService.login` | read | none |
| `GET /auth/me` | current public profile | `ProfileService.get` | read | safe |
| `PUT /auth/me` | replace editable profile fields → public profile | `ProfileService.update` | T1 | K1 |
| `POST /auth/forgot-password` | email → generic accepted message regardless of account existence | `IdentityService.request_reset` | T2 | dedupe/rate policy pending |
| `POST /auth/reset-password` | reset token + new password → success message | `IdentityService.reset_password` | T1 | single consumption pending HG-005 |
| `DELETE /auth/me` | current password + confirmation `XÓA TÀI KHOẢN` → `204` | `AccountDeletionService.delete` | T3 | K2 |
| `POST /auth/me/avatar` | multipart file → public profile | `ProfileService.replace_avatar` | T4 | K1 |
| `DELETE /auth/me/avatar` | remove avatar reference → public profile or `204` | `ProfileService.remove_avatar` | T4 | naturally idempotent target |
| `GET /categories/` | own categories | `CategoryService.list` | read | safe |
| `POST /categories/` | name/type/color/icon → category | `CategoryService.create` | T1 | K1 |
| `PUT /categories/{id}` | replacement/update per published schema → category | `CategoryService.update` | T1 | K1 |
| `DELETE /categories/{id}` | delete unreferenced owned category | `CategoryService.delete` | T1 | K2 |
| `GET /transactions/` | own list; category/type/from/to/keyword filters | `TransactionService.list` | read | safe |
| `POST /transactions/` | owned category, amount, date, note → transaction; type derived | `TransactionService.create` | T1 | K1 |
| `PUT /transactions/{id}` | update owned transaction; category revalidated | `TransactionService.update` | T1 | K1 |
| `DELETE /transactions/{id}` | delete owned transaction | `TransactionService.delete` | T1 | K2 |
| `GET /budgets/` | own budgets, optional month/year, computed spent/is_over | `BudgetService.list` | read snapshot | safe |
| `POST /budgets/` | owned expense category, month, year 2000–2100, positive limit | `BudgetService.create` | T1 | K1 |
| `PUT /budgets/{id}` | update allowed fields; year remains 2000–2100 | `BudgetService.update` | T1 | K1 |
| `DELETE /budgets/{id}` | delete owned budget | `BudgetService.delete` | T1 | K2 |
| `GET /goals/` | own goals with items/current amount | `GoalService.list` | read snapshot | safe |
| `POST /goals/` | name, positive target, deadline → active goal | `GoalService.create` | T1 | K1 |
| `PATCH /goals/{id}` | partial update owned goal | `GoalService.update` | T1 | K1 |
| `DELETE /goals/{id}` | delete only when approved domain policy permits | `GoalService.delete` | T1 | K2 |
| `POST /goals/{id}/items` | item name/cost → updated goal | `GoalService.add_item` | T1 | K1 |
| `PATCH /goals/{id}/items/{item_id}` | update child owned through goal | `GoalService.update_item` | T1 | K1 |
| `DELETE /goals/{id}/items/{item_id}` | delete child owned through goal | `GoalService.delete_item` | T1 | K2 |
| `GET /goals/{id}/transactions` | owned goal funding history | `GoalService.history` | read | safe |
| `POST /goals/{id}/deposit` | positive amount/note; reject over available balance | `GoalService.deposit` | T5 | K3 required |
| `POST /goals/{id}/withdraw` | positive amount/note; reject over saved amount | `GoalService.withdraw` | T5 | K3 required |
| `POST /goals/{id}/complete` | mode keep/release/spend; optional owned expense category | `GoalService.complete` | T5 | K3 required |
| `GET /dashboard/` | month/year → own summary/categories/trend/budgets/goals/recent | `AnalyticsService.dashboard` | read snapshot | safe |
| `GET /reports/` | month/year → own current/previous comparison | `AnalyticsService.report` | read snapshot | safe |
| `GET /assistant/context` | month/year → sanitized aggregate evidence preview | `AssistantService.context` | read | safe |
| `GET /assistant/conversations` | own conversation summaries | `AssistantService.list` | read | safe |
| `GET /assistant/conversations/{id}` | own conversation/messages | `AssistantService.get` | read | safe |
| `DELETE /assistant/conversations/{id}` | hard-delete owned conversation/messages | `AssistantService.delete` | T1 | K2 |
| `POST /assistant/messages` | question, optional owned conversation, month/year → reply/history | `AssistantService.ask` | T6 | K3 recommended |
| `GET /health` | process liveness; no dependency/secret detail | `SystemService.live` | none | safe |
| `GET /ready` | `200` iff required DB dependency ready; otherwise stable `503` | `SystemService.ready` | probe | safe |

Compatibility note: current routes without a trailing-slash policy should be canonicalized consistently without changing semantics. `PUT` versus `PATCH` behavior must match the published request schema; do not silently reinterpret omitted fields.

## 5. Domain and authorization rules

### Identity/profile/deletion

- Normalize username/email with the approved shared algorithm before lookup/write and persist normalized fields per database design. Original casing remains display data.
- Register and profile update check normalized uniqueness in service for friendly feedback; DB unique constraint is authoritative against races and maps to `identity_conflict`.
- Login uses one normalized identifier lookup and one generic credential error. Password hash never leaves repository/domain boundary.
- Expired/invalid bearer token always maps to `401 authentication_required` with `WWW-Authenticate: Bearer`.
- Forgot-password always returns the same public message. Token generation/persistence and notification use T2; no reset token appears in logs or response.
- Account delete requires current authenticated user, an approved fresh re-auth proof and explicit confirmation. The deletion repository targets only current user; DB cascades hard-delete all active relational data. Any missing cascade/preflight aborts the transaction. Other users are never scanned/deleted.

### Categories/transactions/budgets

- Category name is trimmed and normalized case-insensitively. Uniqueness scope is `(current_user.id, type, name_normalized)`; same normalized name is allowed for another user or another type.
- Category delete with owned transactions or budgets returns `409 resource_in_use`; database `RESTRICT` is mapped to the same stable error.
- Transaction category lookup is `(category_id, current_user.id)`. Transaction `type` is copied from that owned category and is never accepted as authoritative input.
- Transaction filters start from `Transaction.user_id == current_user.id`; `category_id` filter does not bypass this base predicate.
- Budget category must be owned and `expense`. Unique scope is `(user, category, month, year)`. Year is validated 2000–2100 before DB access.
- `spent` sums only current user's expense transactions for the exact category and Hanoi month; `is_over = spent > limit`, after Decimal calculation.

### Saving goals

- Goal ownership is checked before every child/history query. Child query is constrained by both `goal_id` and the already-owned parent; aggregate repository should join parent/user explicitly for defense in depth.
- Deposit requires active goal, positive amount and `amount <= available_balance`. Withdraw requires active goal, positive amount and `amount <= saved_amount`.
- Failed deposit/withdraw writes no `goal_transactions` row. Concurrent funding commands lock the owned goal plus rows/state needed to make available/saved balance invariant stable, then re-read totals.
- Complete locks the goal, rejects already completed or underfunded goals, validates mode, and for `spend` validates an owned expense category. Goal status, completion snapshot, goal withdrawal and optional expense transaction commit together.
- Deleting a goal with monetary history remains a `409` preservation rule as-built unless a Human Gate approves different behavior; account deletion is the explicit exception and cascades all owned active data.

### Analytics and assistant

- Dashboard/report share one `Period` and money policy. Repository APIs require `user_id` as a non-optional argument and apply it before joins/grouping.
- Category names may be returned to the authenticated user's dashboard/report, but are forbidden in the Gemini payload when user-defined. Gemini receives only approved generic labels/icon-derived buckets.
- Conversation list/get/delete scopes `AIConversation.user_id`. Messages are reachable only through an owned conversation.
- `AssistantService` builds context from user-scoped aggregate repositories, maps it into a dedicated allow-listed DTO, validates the serialized payload for forbidden keys/content, and only then calls `GeminiPort`.
- Conversation history contains user text and model text and therefore is personal data. It is stored for user-visible history and hard-deleted with conversation/account. No additional retention is invented while `ARCH-HG-008` remains open.
- Gemini output is untrusted text: size-limited, stored/rendered as text, never interpreted as SQL/tool call/domain command.

## 6. Transaction boundaries and external consistency

| ID | Boundary | Commit/rollback rule |
|---|---|---|
| T1 standard DB mutation | one service call, one SQLAlchemy transaction | validate owned dependencies, mutate, flush, commit once; any exception rolls back; serialize after successful flush/commit |
| T2 reset request + email | DB token state and external email cannot share ACID | persist an idempotent notification intent/outbox in same DB transaction if approved persistence exists; worker sends via Resend and retries. Without that approved mechanism, external failure must be surfaced/observed and token state must not be represented as “email sent” |
| T3 account deletion | one relational transaction + post-commit external cleanup | lock current user; delete/cascade only owned active rows; commit; then idempotently delete avatar and record retry/evidence. Relational failure rolls back all. Avatar failure does not resurrect data and enters reconciliation; backup expires operationally ≤30 days |
| T4 avatar replacement | staged object + DB reference + compensating cleanup | validate, stage new server-key object, update DB and commit, finalize if needed, then delete old object. DB failure deletes staged object. Old/new cleanup failure is retried idempotently |
| T5 goal money command | serializable invariant boundary for owned goal/balances | lock/re-read, validate, write every ledger/state row, commit once. Conflict/deadlock rolls back and maps retryable conflict; no partial history |
| T6 assistant ask | external call outside long DB transaction | read sanitized context/history; call Gemini with timeout; only on valid response open short transaction to create/append conversation and both messages atomically. Gemini failure writes neither new conversation nor user-only orphan message |

Repositories may call `flush()` but never `commit()`. Unit of Work owns `begin/commit/rollback`. Read aggregates that must be mutually consistent (dashboard, report, budget list) execute in one read transaction/snapshot supported by PostgreSQL; SQLite behavior is development-only evidence.

External calls never hold row locks. A timeout is an unknown external outcome; adapters use provider idempotency key where supported and avoid blind duplicate sends. No distributed transaction is claimed.

## 7. Idempotency and retry

| Rule | Áp dụng | Contract |
|---|---|---|
| Safe read | all `GET`, health/readiness | repeat has no mutation |
| K1 optional create/update key | register/profile/category/transaction/budget/goal/item/avatar | accept `Idempotency-Key` when retry safety is needed; same `(user, operation, key, canonical request hash)` replays stored status/body; different payload gives `409 idempotency_key_reused` |
| K2 delete target state | deletes | repeated call may return `204`; foreign IDs still `404`. Account delete cannot authenticate after success, so client treats first committed success or subsequent `401` after an ambiguous disconnect as terminal only after session/profile check |
| K3 mandatory financial/AI command key | goal deposit/withdraw/complete; recommended for assistant ask | key required for clients that automatically retry. Reservation/result persists atomically with DB mutation; concurrent duplicate returns original result or `409 operation_in_progress` |

The approved database design does not currently define idempotency storage. Therefore K1/K3 are target API rules whose durable implementation requires a reviewed schema/migration; until then clients must not automatically retry non-idempotent `POST` after an ambiguous timeout. This is an as-built gap, not permission to use process memory as authoritative deduplication.

## 8. Error model

All JSON errors use one envelope; validation errors are normalized into the same shape:

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Không tìm thấy tài nguyên.",
    "fields": [],
    "request_id": "opaque-correlation-id",
    "retryable": false
  }
}
```

`fields` is optional and contains only safe field names/reasons, never submitted secrets. `request_id` correlates sanitized server logs. Public `message` is stable Vietnamese copy; clients branch on `code`, not message.

| HTTP | Code tiêu biểu | Khi dùng |
|---|---|---|
| 400 | `malformed_request` | syntactically unusable request not covered by schema |
| 401 | `authentication_required`, `invalid_credentials` | missing/invalid/expired token; login failure |
| 404 | `resource_not_found` | nonexistent or foreign-owned resource, identical outward behavior |
| 409 | `identity_conflict`, `duplicate_category`, `duplicate_budget`, `resource_in_use`, `insufficient_balance`, `insufficient_goal_funds`, `invalid_goal_state`, `concurrent_conflict`, `idempotency_key_reused` | business/uniqueness/state conflict; no write |
| 413 | `upload_too_large` | upload over approved limit (limit pending HG-006) |
| 415 | `unsupported_media_type` | upload format/content mismatch |
| 422 | `validation_failed` | field/type/range/year/date validation |
| 429 | `rate_limited`, `external_rate_limited` | local protection or Gemini throttle; safe `Retry-After` when known |
| 502 | `external_bad_response` | invalid/rejected upstream response |
| 503 | `dependency_unavailable`, `service_not_configured`, `not_ready` | Resend/Gemini/storage/required DB unavailable |
| 504 | `external_timeout` | external timeout |
| 500 | `internal_error` | unexpected failure; generic client text only |

Exception mapping is centralized: schema → 422; auth → 401; `NotFound` → 404; domain conflict → 409; SQL unique/FK/check errors → their safe domain code; adapter typed errors → 429/502/503/504; unknown exception → rollback + logged exception under request ID + generic 500. Raw database/vendor messages and `str(exc)` never enter responses.

## 9. Health, readiness, uploads and external email

- `/api/health` is liveness only: `200 {"status":"ok"}` if event loop/process can serve. It performs no Gemini/Resend call and reveals no versions/configuration.
- `/api/ready` performs a bounded, read-only DB probe. Database failure/timeout returns `503 not_ready`; body does not expose DSN/query/stack. Gemini and Resend are feature dependencies, not global readiness blockers unless an approved deployment policy makes them mandatory.
- API/probes/uploads/assets are matched before SPA fallback; every `/api/*` miss remains JSON/HTTP, never `index.html`.
- Upload bytes are untrusted. Enforce streaming size bound, declared type plus decoded/signature validation, server-generated opaque key, no executable serving, ownership-controlled read, and storage timeout. Exact allow-list/size/quota/scanning/access URL remain blocked by `ARCH-HG-006`.
- Resend is behind `EmailPort`; HTTPS, connect/read timeouts, no API key/token in URL/log. Forgot-password public response remains generic for existing/non-existing emails. Delivery failure is observable and retryable through T2; it is never silently reported internally as successful delivery.

## 10. Verification matrix

| Area | Positive path | Negative/validation | Authorization | Rollback/concurrency | External failure |
|---|---|---|---|---|---|
| Auth/profile | register/login/me/update with normalized identity | weak/invalid fields, duplicate case variant, expired reset/token | bearer required; no hash in response | unique race rolls back; reset consume atomic | Resend timeout/error gives generic public behavior plus retry/telemetry; no secret |
| Account deletion | re-auth + confirm deletes all own active rows | absent/expired proof or confirmation rejected | cannot delete by supplied user ID; other user unchanged | injected child-delete failure rolls back entire relational delete | avatar cleanup failure queues retry; backup evidence ≤30 days |
| Category | CRUD own; same name allowed other type/user | trim/case duplicate rejected | foreign ID indistinguishable 404 | DB uniqueness race maps 409; delete RESTRICT leaves rows | n/a |
| Transaction | CRUD/filter; type derived from category | nonpositive amount/bad date/category rejected | list/object/category all user-scoped | commit failure leaves no row/update | n/a |
| Budget | create/list/update/delete and correct spent/is_over | year outside 2000–2100, income category, duplicate rejected | foreign category/budget 404 | concurrent duplicate leaves one; snapshot consistent | n/a |
| Goal | CRUD/items/history; legal deposit/withdraw/complete | over-balance, over-withdraw, inactive/underfunded/invalid mode rejected | parent and child foreign IDs 404 | concurrent deposits cannot overspend; all completion rows commit or none | n/a |
| Dashboard/report | totals/net/comparison/category for Hanoi periods | invalid month/year rejected, empty data stable | seed two users and prove aggregate isolation | consistent read during concurrent mutation | n/a |
| Assistant | own conversation and sanitized advice/history | empty/oversize question, invalid period/output rejected | foreign conversation 404 | Gemini fail creates no orphan; DB fail after reply rolls back messages | not configured/rate limit/timeout/bad payload map stable codes; payload capture proves deny-list |
| Health/readiness | healthy process/DB return 200 | readiness DB failure 503 | no sensitive details | bounded probe; no writes | optional Gemini/Resend outage does not falsely mark DB unready |
| Upload | valid approved image replace/delete | empty/oversize/type-signature/path payload rejected | own reference/read only | DB failure removes staged; cleanup retry converges | storage timeout maps stable error, no partial profile reference |

Required evidence includes unit tests for services/policies, repository integration tests on PostgreSQL for constraints/locking/user scope, API tests for envelopes/statuses, adapter contract tests with failures/timeouts, and end-to-end boundary tests for Hanoi month and one-decimal VND. SQLite tests alone are insufficient for T3/T5, unique races and FK/cascade behavior.

## 11. Traceability endpoint/service → FR/AC

| Endpoint/service | Requirement | Acceptance/evidence |
|---|---|---|
| register/login/profile, `IdentityService` | FR-AUTH-001, FR-AUTH-003, NFR-SEC-001/003 | AC-001, AC-010, AC-011 |
| forgot/reset, `IdentityService` + `EmailPort` | FR-AUTH-002, NFR-REL-001 | AC-001; external-failure path (AC-007 pattern) |
| reauth/delete, `AccountDeletionService` | FR-DATA-001, BR-004, NFR-PRIV-003 | AC-012, AC-021 |
| category endpoints, `CategoryService` | FR-CAT-001, BR-001, NFR-SEC-001 | AC-002, AC-018 |
| transaction endpoints, `TransactionService` | FR-TXN-001, NFR-SEC-001, NFR-DATA-001/002 | AC-002, AC-016 |
| budget endpoints, `BudgetService` | FR-BUD-001, BR-002 | AC-002, AC-003, AC-019 |
| goal/item/funding/complete, `GoalService` | FR-GOAL-001, NFR-DATA-001/002 | AC-002, AC-004, AC-016 |
| dashboard, `AnalyticsService` | FR-DASH-001, NFR-TIME-001 | AC-005, AC-014, AC-016 |
| reports, `AnalyticsService` | FR-REP-001, NFR-TIME-001 | AC-005, AC-014, AC-016 |
| assistant context/conversation/message, `AssistantService` | FR-AI-001/002, NFR-PRIV-001/002, NFR-REL-001 | AC-002, AC-006, AC-007, AC-017 |
| health/readiness/host | FR-REL-001, NFR-REL-001/002 | AC-008, AC-015 |
| all protected services/repositories | NFR-SEC-001/002/003 | AC-002, AC-011, AC-017 |
| all money/time policies | NFR-DATA-001/002, NFR-TIME-001 | AC-014, AC-016 |
| service/repository/adapter test seams | NFR-TEST-001 | AC-009 plus matrix section 10 |

`BR-003`/`AC-020` belongs to the Alembic migration boundary already defined in database design and is intentionally not redesigned here.

## 12. Khác biệt as-built → target

| As-built quan sát được | Target / tác động |
|---|---|
| Routers trực tiếp query model, thực thi rule và `db.commit()` | tách service/UoW/repository; một commit tại use-case boundary |
| Chưa có endpoint account deletion | thêm `DELETE /auth/me` với mật khẩu hiện tại + chuỗi xác nhận theo RQ-011; hard-delete dữ liệu active trong transaction |
| `users` chưa có normalized identity columns; username lookup còn case-sensitive | dùng approved normalized fields/indexes và migration fail-fast |
| Category duplicate dùng `func.lower(name)` nhưng không trim/normalize persisted; model thiếu unique target | shared normalization + service check + approved DB uniqueness |
| Budget schema create không giới hạn year 2000–2100; model thiếu checks/unique/composite ownership FK | validate trước DB và áp dụng database design qua migration ở phase implementation |
| Models/FKs chưa thể hiện đầy đủ checks, cascades, restrict, composite ownership/indexes đã duyệt | target repositories dựa trên constraints đã duyệt; chưa được giả định chúng đang tồn tại |
| Goal aggregate child query dựa vào `goal_id` sau parent check; không lock khi kiểm balance | explicit owner join + PostgreSQL locking/re-read cho funding/complete |
| Goal dùng `date.today()` | dùng `TimePolicy` Asia/Ho_Chi_Minh |
| Dashboard/report/assistant lặp logic month/percentage và có chuyển Decimal → float cho tỷ lệ | shared time/money/ratio policy; tiền không qua float; quy tắc phần trăm tách khỏi money |
| Output Decimal chưa có central one-decimal serialization rule | quantize/serialize VND nhất quán tại business/API boundary; rounding mode vẫn cần Gate nếu ảnh hưởng result |
| Forgot-password commit token rồi gọi email; adapter trả `False` nhưng router bỏ qua; rate limit in-memory | durable intent/retry hoặc explicit failure observability; policy cụ thể chờ HG-005/schema review |
| Reset lifetime 15 phút/single-use đang là code choice trong khi architecture ghi chưa được Human Gate định lượng | không nâng as-built choice thành target approval; giữ blocked marker HG-005 |
| Avatar ghi file trực tiếp, URL `/uploads/...` public static, policy 2 MB/PNG-JPEG-WebP tự đặt | adapter/staging/ownership/cleanup; exact upload/access policy chờ HG-006 |
| Upload tạo thư mục lúc import và dùng blocking whole-file read/write | lifecycle tại adapter/startup, streaming bound, timeout và reconciliation |
| Assistant router giữ DB transaction mở quanh external Gemini call và map `str(exc)` | external call ngoài lock/transaction dài; typed stable errors; atomic history write sau valid reply |
| Gemini prompt gửi raw conversation question/history (personal content) cùng aggregate | requirements chỉ cấm identity/raw financial fields nhưng history privacy/retention còn mở; target giới hạn, classify và không gọi đó là anonymous; HG-008/009 cần quyết định |
| Gemini gateway là core function, chưa có structural DTO/deny-list enforcement độc lập | port + aggregate-only allow-list DTO + payload contract test; không DB dependency |
| Error body dùng FastAPI `detail` không thống nhất; một số response lấy `str(exc)` | central error envelope/code/request ID/redaction |
| Mutation POST không có durable idempotency | K1/K3 target; cần schema/migration review trước durable implementation |
| `/uploads` được mount trước ownership-aware route và có thể công khai avatar | protected/signed delivery theo approved policy; không public-by-path mặc định |
| Readiness chỉ cần được kiểm chứng thêm về timeout/error envelope/dependency policy | bounded DB-only required probe, stable 503, no secret |
| Runtime `schema_migrations.py` tự chỉnh schema | production schema authority phải là Alembic; conflict migration fail-fast theo BR-003/AC-020 |

## 13. Điều kiện chuyển sang implementation

Phần category/transaction/budget/goal/analytics, common errors, user-scoped repositories và DB-only probes có thể lập implementation plan dựa trên Gate đã duyệt. Trước khi triển khai đầy đủ reset, account deletion proof, avatar policy, AI confidence/evidence và durable idempotency, cần:

1. Human decision cho `ARCH-HG-005`, `006`, `009` (và `008` nếu đặt retention hội thoại). `ARCH-HG-010` đã được RQ-011 giải quyết.
2. Database/migration review cho reset artifact/outbox/idempotency nếu target cần bảng/cột mới; không sửa migration đã phát hành.
3. Security review cho upload delivery, reset/re-auth proof, error redaction và Gemini payload contract.
4. PostgreSQL integration/concurrency tests cho cascade, composite ownership, duplicate races, T3 và T5.

Không có thay đổi requirement/architecture nào được đề xuất trong tài liệu này. Các điểm chưa đủ quyết định được giữ nguyên là blocker, đúng yêu cầu phải dừng trước khi tự đặt policy.
