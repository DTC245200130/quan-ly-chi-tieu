# Test plan

## Quy tắc danh mục và ngân sách — 26/09/2026

| Yêu cầu | Tầng kiểm thử | File / bằng chứng | Trạng thái |
|---|---|---|---|
| BR-001, AC-018 | Schema/router/model: NFKC, trim, casefold; create/update collision; khác owner/loại; lỗi race qua UNIQUE | `tests/test_baseline_requirements.py`, `tests/test_crud_routes.py` | PASS trên SQLite cô lập |
| BR-002, AC-019 | Schema chặn năm ngoài 2000–2100; database CHECK chặn ghi trực tiếp | `tests/test_baseline_requirements.py`, `tests/test_category_budget_migration.py` | PASS trên SQLite tạm |
| BR-003, AC-020 | Backfill `name_normalized`; migration dừng trước DDL khi category collision hoặc budget year sai; upgrade/downgrade | `tests/test_category_budget_migration.py` | PASS trên SQLite tạm |
| FR-CAT-001 | Không xóa category đang được transaction hoặc budget sử dụng | `tests/test_crud_routes.py` | PASS |
| NFR-DATA-001 | Migration/constraint và ghi cạnh tranh trên PostgreSQL đại diện | Compose/PostgreSQL thử nghiệm | NOT RUN — chưa có môi trường cung cấp `POSTGRES_PASSWORD` |

Frontend không đổi trong phạm vi Giai đoạn 3 nên component test/build được đánh dấu NOT RUN cho đợt này.

## Chuẩn hóa định danh — 26/09/2026

| Yêu cầu | Tầng kiểm thử | File / bằng chứng | Trạng thái |
|---|---|---|---|
| RQ-001, AC-010 | Unit/integration auth: NFKC, trim, casefold; đăng ký trùng; đăng nhập username/email; cập nhật hồ sơ collision | `tests/test_auth.py` | PASS trên SQLite cô lập |
| BR-003, AC-020 | Migration từ `20260901_0001`: backfill, normalized UNIQUE, downgrade; collision phải dừng trước DDL và giữ nguyên row | `tests/test_user_identity_migration.py` | PASS trên SQLite tạm |
| NFR-DATA-001 | Cùng migration trên PostgreSQL đại diện, gồm kiểm tra lock và UNIQUE cạnh tranh | Compose/PostgreSQL thử nghiệm | NOT RUN — môi trường chưa có `POSTGRES_PASSWORD` |

Frontend và hợp đồng API không đổi trong phạm vi này; không cần thêm test component. Không dùng `expense.db` làm fixture migration: file này chỉ được audit read-only và không có collision trong 3 user hiện hữu.

## Kiểm thử live bổ sung 19/09/2026

- FR-AI-001, NFR-REL-001: adapter gọi Gemini thật bằng aggregates giả, có phản hồi; chưa đánh giá đầy đủ chất lượng nội dung hoặc mọi lỗi provider.
- FR-AUTH-002: Resend từ chối khóa hiện tại (HTTP 400, invalid API key); cần khóa hợp lệ và địa chỉ nhận thử trước khi chứng minh gửi/nhận và reset end-to-end.
- FR-REL-001, NFR-PRIV-002: production URL không kết nối được; cần tên miền có DNS hoạt động để kiểm tra health/readiness/TLS.
- FR-AUTH-001, NFR-UX-001: Edge đăng ký, đăng nhập và mở 7 trang qua backend local thật đạt; chưa bao phủ mọi thao tác CRUD UI, responsive hoặc offline PWA.
- NFR-DATA-001: Docker daemon không khả dụng; PostgreSQL vẫn chưa được kiểm chứng.

## Bổ sung ngày 19/09/2026

| Yêu cầu | Bằng chứng / khoảng trống |
|---|---|
| BR-001, AC-018 | `tests/test_baseline_requirements.py`: 2 ca trùng tên khác hoa/thường hoặc khoảng trắng FAIL; cần bổ sung nhánh update và kiểm tra khác user/loại |
| BR-002, AC-019 | Cùng file: 1999/2101 FAIL vì schema vẫn nhận; 2000/2100 PASS |
| FR-DATA-001, BR-004, AC-012/021 | Chưa có bằng chứng end-to-end xóa tài khoản và retention backup 30 ngày |
| BR-003, AC-020, NFR-DATA-001 | Migration SQLite mới PASS; chưa kiểm tra PostgreSQL/collision dữ liệu cũ; Docker daemon không khả dụng |
| NFR-TIME-001, AC-014 | Cần test ranh giới tháng theo Asia/Ho_Chi_Minh |
| NFR-DATA-002, AC-016 | Cần test làm tròn VND một chữ số thập phân xuyên suốt API/UI |
| FR-CONN-001, AC-013 | Test lỗi/retry component hiện có; chưa E2E mất Internet khi đang nhập/lưu dữ liệu |
| NFR-PERF-001, AC-015 | Chưa chạy tải theo điều kiện vận hành được phê duyệt |
| NFR-PRIV-002, AC-017 | Chưa kiểm chứng TLS production/live provider |
| FR-REL-001, NFR-UX-001 | Web/PWA build PASS; chưa browser E2E/responsive thực tế và bộ cài Tauri |

Không đánh đồng suite PASS với nghiệm thu toàn bộ baseline. Đợt này giữ nguyên lỗi ứng dụng và bổ sung ca tái hiện để phục vụ bước sửa lỗi.

| Nhóm | Yêu cầu | Kỹ thuật |
|---|---|---|
| Auth/profile/reset | FR-AUTH, NFR-SEC | unit/integration, positive/negative, token expiry, rate limit, upload boundary |
| CRUD + ownership | FR-CAT/TXN/BUD/GOAL | integration, cross-user ID, duplicate/not-found/in-use, money boundaries, rollback |
| Aggregation | FR-DASH/REP | deterministic datasets, empty period, current/previous period, owner isolation |
| Assistant | FR-AI, NFR-PRIV/REL | prompt/context unit tests, conversation ownership, Gemini timeout/retry/error mapping |
| Frontend | all user stories | component/API tests for success/loading/error/retry and route guards |
| Release | FR-REL, NFR-TEST | backend suite, frontend coverage, TypeScript + Vite/PWA build |

Các khoảng trống ưu tiên: frontend Goals/Transactions/Assistant branches, database constraints/migration behavior, token revocation (sau khi RQ-002 được quyết định), và E2E browser trên production-like PostgreSQL.
