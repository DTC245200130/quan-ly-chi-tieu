# Thiết kế cơ sở dữ liệu và migration

> Database design v1.1 theo baseline requirements v1.1 và Database Gate do Đào Minh Tâm phê duyệt ngày 06/09/2026. Đây là **thiết kế migration**, chưa phải bằng chứng migration đã được viết hoặc chạy. Không sửa revision đã phát hành `20260901_0001`; implementation phải tạo revision Alembic mới.

## 1. Phạm vi và trạng thái

Schema hiện tại có đủ entity chính nhưng chưa thực thi normalized key, business check, ownership composite FK, cascade/restrict và phần lớn composite index dưới đây. Tiền hiện là `NUMERIC(14,2)`; ID là chuỗi UUID do ứng dụng sinh.

Thiết kế đích hỗ trợ PostgreSQL production và SQLite development. PostgreSQL là môi trường đại diện bắt buộc cho bằng chứng migration, concurrency và query plan; chỉ chạy SQLite không đủ để đánh dấu hoàn thành.

## 2. ERD dạng text

```text
users (PK id)
  |--< categories (PK id, FK user_id -> users.id CASCADE)
  |      AK (id, user_id)
  |      UQ (user_id, type, name_normalized)
  |       |--< transactions via (category_id, user_id) RESTRICT
  |       `--< budgets      via (category_id, user_id) RESTRICT
  |--< transactions (PK id, FK user_id -> users.id CASCADE)
  |--< budgets (PK id, FK user_id -> users.id CASCADE)
  |      UQ (user_id, category_id, month, year)
  |--< saving_goals (PK id, FK user_id -> users.id CASCADE)
  |       |--< goal_items (PK id, FK goal_id -> saving_goals.id CASCADE)
  |       `--< goal_transactions (PK id, FK goal_id -> saving_goals.id CASCADE)
  `--< ai_conversations (PK id, FK user_id -> users.id CASCADE)
          `--< ai_messages (PK id, FK conversation_id -> ai_conversations.id CASCADE)
```

`transactions.user_id` và `budgets.user_id` vừa là FK trực tiếp tới owner, vừa tham gia composite FK tới category. Database vì thế từ chối category của user khác ngay cả khi ứng dụng bỏ sót authorization predicate.

## 3. Chuẩn hóa và precision

Thêm `users.username_normalized`, `users.email_normalized` và `categories.name_normalized`, đều `VARCHAR NOT NULL`. Một hàm dùng chung ở application và backfill tạo giá trị theo đúng thứ tự: Unicode NFKC → trim hai đầu → Unicode case-fold. Không collapse khoảng trắng ở giữa. Cột gốc giữ nguyên để hiển thị.

Backfill chạy bằng cùng implementation Python, không dùng riêng `LOWER()`, collation hoặc PostgreSQL `CITEXT`, vì chúng không bảo đảm kết quả giống SQLite. Create/update phải ghi cột gốc và normalized trong cùng transaction; lookup dùng normalized column; lỗi unique được map thành conflict ổn định.

Giữ `NUMERIC(14,2)` cho mọi amount/limit/target/cost/completion để không mất precision lịch sử. VND và làm tròn một chữ số thập phân thuộc service/API/display. Không dùng binary float. Giá trị dương tối đa lưu được là `999999999999.99`.

## 4. PK, FK, UNIQUE, CHECK và ON DELETE

### PK/FK/ON DELETE

| Tên | Cột nguồn | Đích | ON DELETE |
|---|---|---|---|
| PK hiện có | `*.id` | — | — |
| `fk_categories_user_id_users` | `categories.user_id` | `users.id` | CASCADE |
| `fk_transactions_user_id_users` | `transactions.user_id` | `users.id` | CASCADE |
| `fk_transactions_category_owner` | `transactions(category_id,user_id)` | `categories(id,user_id)` | RESTRICT |
| `fk_budgets_user_id_users` | `budgets.user_id` | `users.id` | CASCADE |
| `fk_budgets_category_owner` | `budgets(category_id,user_id)` | `categories(id,user_id)` | RESTRICT |
| `fk_saving_goals_user_id_users` | `saving_goals.user_id` | `users.id` | CASCADE |
| `fk_goal_items_goal_id_saving_goals` | `goal_items.goal_id` | `saving_goals.id` | CASCADE |
| `fk_goal_transactions_goal_id_saving_goals` | `goal_transactions.goal_id` | `saving_goals.id` | CASCADE |
| `fk_ai_conversations_user_id_users` | `ai_conversations.user_id` | `users.id` | CASCADE |
| `fk_ai_messages_conversation_id_ai_conversations` | `ai_messages.conversation_id` | `ai_conversations.id` | CASCADE |

Hai FK đơn từ transaction/budget tới `categories.id` được **thay**, không giữ song song. Mọi cột FK tiếp tục `NOT NULL`.

### UNIQUE

| Tên | Cột |
|---|---|
| `uq_users_username_normalized` | `users(username_normalized)` |
| `uq_users_email_normalized` | `users(email_normalized)` |
| `uq_categories_id_user_id` | `categories(id,user_id)` |
| `uq_categories_owner_type_name_norm` | `categories(user_id,type,name_normalized)` |
| `uq_budgets_owner_category_period` | `budgets(user_id,category_id,month,year)` |

Sau khi normalized unique đã tạo thành công, bỏ `ix_users_username` và `ix_users_email`: uniqueness case-sensitive trên cột hiển thị là dư thừa và tạo semantics conflict không cần thiết.

### CHECK

| Tên | Biểu thức |
|---|---|
| `ck_categories_type` | `type IN ('income','expense')` |
| `ck_categories_name_not_blank` | `length(trim(name)) > 0` |
| `ck_categories_name_normalized_not_blank` | `length(name_normalized) > 0` |
| `ck_transactions_amount_positive` | `amount > 0` |
| `ck_transactions_type` | `type IN ('income','expense')` |
| `ck_budgets_limit_positive` | `limit_amount > 0` |
| `ck_budgets_month` | `month BETWEEN 1 AND 12` |
| `ck_budgets_year` | `year BETWEEN 2000 AND 2100` |
| `ck_saving_goals_target_positive` | `target_amount > 0` |
| `ck_saving_goals_status` | `status IN ('active','completed')` |
| `ck_saving_goals_completion_amount` | `completion_amount IS NULL OR completion_amount >= 0` |
| `ck_saving_goals_completion_mode` | `completion_mode IS NULL OR completion_mode IN ('keep','release','spend')` |
| `ck_goal_items_cost_positive` | `cost > 0` |
| `ck_goal_transactions_amount_positive` | `amount > 0` |
| `ck_goal_transactions_type` | `type IN ('deposit','withdraw')` |
| `ck_ai_messages_role` | `role IN ('user','assistant')` |
| `ck_ai_messages_context_month` | `context_month IS NULL OR context_month BETWEEN 1 AND 12` |
| `ck_ai_messages_context_period_pair` | `(context_month IS NULL) = (context_year IS NULL)` |

Không thêm check `transaction.type = category.type`: portable FK cho invariant này cần mở rộng candidate key và write path, trong khi Gate chỉ phê duyệt same-owner reference. Application vẫn phải kiểm tra type. Không áp miền `context_year` vì requirements chưa duyệt.

## 5. Index và query pattern

| Tên | Cột theo thứ tự | Query chính |
|---|---|---|
| `ix_transactions_user_date` | `(user_id, txn_date)` | list/range, dashboard/report |
| `ix_transactions_user_type_date` | `(user_id, type, txn_date)` | filter/aggregate type theo kỳ |
| `ix_transactions_user_category_date` | `(user_id, category_id, txn_date)` | budget spent/category report |
| `ix_budgets_user_year_month` | `(user_id, year, month)` | list/dashboard theo kỳ |
| `ix_saving_goals_user_status_deadline` | `(user_id, status, deadline)` | active goals/deadline |
| `ix_goal_items_goal_id` | `(goal_id)` | load/delete goal items |
| `ix_goal_transactions_goal_date` | `(goal_id, txn_date)` | balance/history |
| `ix_ai_conversations_user_updated` | `(user_id, updated_at)` | conversation mới nhất |
| `ix_ai_messages_conversation_created_id` | `(conversation_id, created_at, id)` | history có thứ tự ổn định |

UNIQUE cũng tạo index. Không thêm index FK khi đã là prefix của index khác. Thay index AI đơn hiện tại bằng composite tương ứng. `note ILIKE '%...%'` không được B-tree hỗ trợ và trigram không portable, nên chưa thêm khi chưa có workload/Gate. PostgreSQL kiểm tra bằng `EXPLAIN (ANALYZE, BUFFERS)` trên dataset đại diện; SQLite `EXPLAIN QUERY PLAN` chỉ là smoke check.

## 6. Audit/preflight bắt buộc

Audit read-only chỉ xuất count và ID đủ để xử lý; không log hash/token/message/note. Nếu bất kỳ nhóm nào có row, **dừng trước DDL/backfill**, rollback và báo cáo; không trim/update/rename/chọn winner/xóa tự động.

1. Identity collision: normalize username/email bằng hàm Python đích, group normalized value có `count > 1`.
2. Category: `trim(name) = ''`; hoặc duplicate `(user_id,type,normalize(name))`.
3. Budget: duplicate `(user_id,category_id,month,year)`.
4. Ownership/FK: orphan ở mọi FK; transaction/budget có `user_id <> category.user_id`.
5. CHECK: enum ngoài miền; tiền `<= 0`; completion âm; month/year ngoài miền; context period chỉ có một vế.
6. Backfill: source null, normalized result rỗng, ID legacy trùng/không hợp lệ.
7. Precision: giá trị vượt `NUMERIC(14,2)` hoặc có hơn hai chữ số thập phân do SQLite affinity không cưỡng chế như PostgreSQL.

Chạy preflight trước maintenance window và lặp lại ngay trong migration để đóng khoảng drift. PostgreSQL khóa ghi các bảng bị ảnh hưởng khi audit cuối/backfill/constraint creation. SQLite deployment phải độc quyền writer trong khi batch rebuild.

## 7. Backfill và upgrade

1. Tạo revision mới kế tiếp `20260901_0001`; xác nhận revision hiện tại, chạy preflight và dừng với loại lỗi/count/sample ID khi conflict.
2. Thêm ba normalized column nullable tạm thời; backfill theo batch bằng hàm chung, không đổi cột hiển thị; audit collision/blank lần nữa.
3. Chuyển normalized columns thành `NOT NULL`, rồi tạo normalized UNIQUE và category candidate key.
4. Tạo CHECK sau audit sạch. PostgreSQL có thể dùng `NOT VALID` rồi `VALIDATE CONSTRAINT` cho CHECK/FK; UNIQUE cần maintenance window hoặc chiến lược concurrent index riêng vì `CREATE INDEX CONCURRENTLY` không chạy trong transaction Alembic thông thường.
5. Thay FK cũ bằng FK có tên/`ON DELETE`; tạo ownership FK sau candidate key. Không bật cascade trước khi orphan/cross-user audit sạch.
6. Tạo composite index, xác minh, rồi bỏ index đơn bị supersede và unique index case-sensitive cũ.
7. Chạy post-upgrade verification. Phối hợp application bằng expand/contract hai release hoặc maintenance window; không cho application cũ ghi row thiếu normalized sau khi `NOT NULL` có hiệu lực.

SQLite dùng `op.batch_alter_table(..., recreate='always')`, bật và xác minh `PRAGMA foreign_keys=ON`, giữ đúng thứ tự tạo constraint/index. SQLite không chứng minh được lock/concurrency production.

## 8. Account deletion và delete order

Hard delete active data chạy trong một transaction sau re-authentication/confirmation. Vì category reference là `RESTRICT`, service không phụ thuộc thứ tự cascade của engine:

```text
transactions + budgets
    -> ai_messages (hoặc qua conversations)
    -> goal_items + goal_transactions (hoặc qua goals)
    -> ai_conversations + saving_goals
    -> categories
    -> users
```

Mọi explicit delete có owner predicate; không nhận authoritative `user_id` từ client. Cascade là defense-in-depth. Xóa category độc lập bị RESTRICT nếu còn transaction/budget và tuyệt đối không xóa lịch sử ngầm.

Avatar ngoài DB cần cleanup idempotent có retry/durable task sau commit; lỗi object storage không làm giả trạng thái DB. Backup DB/avatar dùng retention `<= 30 ngày`, có log expiry, inventory và restore drill. Commit hard delete không đồng nghĩa dữ liệu lập tức biến mất khỏi backup.

## 9. Rollback/downgrade

1. Xác nhận application cũ không phụ thuộc normalized columns.
2. Khôi phục FK/index cũ trước; bỏ FK/index/CHECK/UNIQUE mới theo thứ tự phụ thuộc; bỏ normalized columns cuối cùng.
3. SQLite batch rebuild chiều ngược và chạy `foreign_key_check` sau mỗi nhóm.
4. Downgrade không hoàn tác account hard delete, không khôi phục row và không thay backup retention.
5. Với concurrent index PostgreSQL ngoài transaction, implementation phải có checkpoint/cleanup idempotent.

Ưu tiên roll-forward. Chỉ tuyên bố downgrade supported sau round-trip `upgrade -> downgrade -> upgrade` trên DB mới và bản sao đại diện; nếu không đạt, revision phải chặn downgrade rõ ràng thay vì giả thành công.

## 10. Verification và điều kiện hoàn thành

- Introspection khớp tên/cột/thứ tự mọi PK/FK/UNIQUE/CHECK/INDEX/ON DELETE trên cả hai DB.
- Negative writes chứng minh collision identity/category, duplicate budget, category blank, year 1999/2101, month 0/13, enum sai và tiền `<= 0` bị từ chối.
- Cross-user transaction/budget bị composite FK từ chối; same-user reference hợp lệ.
- Category đang dùng bị RESTRICT; xóa conversation/goal xóa children; xóa account xóa toàn bộ active row đúng user và không ảnh hưởng user khác.
- Vector case/whitespace/Unicode cho kết quả normalization giống nhau ở backfill và write path.
- `Decimal` round-trip/SUM đúng ở 0.01, hai decimal và gần giới hạn; không có float conversion.
- Query plan cho transaction list, dashboard/report, budget spent, goal history và conversation history dùng index phù hợp trên cardinality đại diện.
- Fixture chứa từng collision/conflict làm migration dừng mà dữ liệu không đổi.
- Chạy fresh install; upgrade từ `20260901_0001`; upgrade bản sao production đã khử nhạy cảm; failure atomicity; downgrade round-trip nếu hỗ trợ.
- PostgreSQL có test cạnh tranh tạo cùng normalized identity/category/budget để chứng minh UNIQUE chống race.

Không đánh dấu migration hoàn thành vì file tồn tại hoặc SQLite pass. Evidence cần revision/checksum, version DB, dataset profile, audit sạch, upgrade/rollback, constraint tests, query plans, account-delete test và backup-retention evidence. Release Gate vẫn `PENDING`.

## 11. Traceability constraint/index → requirement

| Thiết kế | Requirement/quyết định |
|---|---|
| Identity normalized UNIQUE + backfill | FR-AUTH-003, BR-003 |
| Category normalized UNIQUE + blank/type checks | FR-CAT-001, BR-001, BR-003 |
| Budget period UNIQUE + month/year/positive checks | FR-BUD-001, BR-002, BR-003 |
| Composite category ownership FK | NFR-SEC-001 |
| CASCADE/RESTRICT + explicit delete order | FR-DATA-001, BR-004 |
| Backup retention/evidence `<=30 ngày` | BR-004, NFR-PRIV-003 |
| Positive checks + `NUMERIC(14,2)` | NFR-DATA-001, NFR-DATA-002 |
| Transaction indexes | FR-TXN-001, FR-DASH-001, FR-REP-001, FR-BUD-001, NFR-PERF-001 |
| Goal indexes/cascades | FR-GOAL-001, NFR-PERF-001 |
| Conversation/message indexes/cascades | FR-AI-001, FR-DATA-001, NFR-PERF-001 |
| Context checks | FR-AI-002, NFR-TIME-001 |
| Audit-stop policy | BR-003 |
| PostgreSQL representative + SQLite compatibility tests | NFR-DATA-001, NFR-TEST-001 |

## 12. Khoảng trống implementation quan sát được

- Models và initial migration chưa có normalized columns, các CHECK/UNIQUE/composite FK/ON DELETE và phần lớn index đích.
- Auth chưa nhất quán case-insensitive cho username; category đang so sánh exact, chưa trim/case-fold.
- Xóa category mới kiểm tra transaction, chưa kiểm tra budget; database chưa có RESTRICT/ownership FK.
- `app/core/schema_migrations.py` có runtime `ALTER TABLE`; production schema phải chuyển qua Alembic và không coi helper này là bằng chứng migration.
- Account deletion workflow và backup expiry evidence cần implementation/operations xác nhận riêng.

Các mục này là đầu vào cho Implementation phase; tài liệu không sửa code và không khẳng định chúng đã được giải quyết.
