# Test report

## Quy tắc danh mục và ngân sách — 26/09/2026

Phạm vi: BR-001/AC-018, BR-002/AC-019, phần category/budget của BR-003/AC-020 và kiểm tra xóa category đang được budget sử dụng.

| Lệnh / kiểm tra | Kết quả |
|---|---|
| Audit read-only `expense.db` | PASS — 10 category: 0 blank, 0 normalized collision; 4 budget: 0 năm ngoài miền. Không chạy migration trực tiếp. |
| `.\venv\Scripts\python.exe -m pytest -q tests/test_baseline_requirements.py tests/test_crud_routes.py tests/test_category_budget_migration.py` | **PASS — 13 passed, 3 warnings, 6.24s** |
| Migration SQLite tạm `20260925_0002` → `20260926_0003` → `20260925_0002` | PASS — backfill đúng, category normalized UNIQUE và budget year CHECK chặn ghi sai, downgrade bỏ schema mới. |
| Fixture có category collision và budget year 1999 | PASS — upgrade dừng trước DDL, báo ID xung đột và giữ nguyên row. |
| `.\venv\Scripts\python.exe -m pytest -q` | **PASS — 89 passed, 24 subtests passed, 7 warnings, 20.48s** |
| Frontend test/build | NOT RUN — không có file frontend hoặc hợp đồng API response thay đổi. |
| PostgreSQL migration/rehearsal | NOT RUN — Compose chưa được cung cấp `POSTGRES_PASSWORD`; không tự tạo secret hoặc chạm volume. |

Giới hạn: bằng chứng migration hiện tại là SQLite cô lập, không thay thế kiểm chứng lock, constraint và ghi cạnh tranh trên PostgreSQL production-like.

## Chuẩn hóa username/email — 26/09/2026

Phạm vi: RQ-001, AC-010 và phần identity của BR-003/AC-020. Thuật toán đích là Unicode NFKC → trim → casefold; không sửa dữ liệu hiển thị khi backfill và không tự xử lý collision.

| Lệnh / kiểm tra | Kết quả |
|---|---|
| Audit read-only `expense.db` bằng hàm Python đích | PASS — 3 user; username/email đều 0 blank, 0 collision. Database không có bảng `alembic_version`; không chạy migration trực tiếp. |
| `.\venv\Scripts\python.exe -m pytest -q tests/test_auth.py tests/test_auth_branches.py tests/test_user_identity_migration.py` | **PASS — 26 passed, 5 subtests passed, 1 warning, 17.18s** |
| Migration SQLite tạm từ `20260901_0001` → `20260925_0002` → `20260901_0001` | PASS — backfill đúng, normalized UNIQUE chặn duplicate, downgrade bỏ hai cột mới. |
| Fixture có `Minh` và `  ＭINH  ` | PASS — upgrade dừng trước DDL, báo ID xung đột, giữ nguyên 2 row. |
| `.\venv\Scripts\python.exe -m pytest -q` | **FAIL — 4 failed, 81 passed, 24 subtests passed, 7 warnings, 15.74s**. Bốn fail vẫn là DEF-018/DEF-019 thuộc category và budget, ngoài Giai đoạn 2. |
| `.\venv\Scripts\python.exe -m compileall -q app alembic tests` | PASS |
| `docker compose ps --format json` | BLOCKED/NOT RUN cho PostgreSQL — Compose yêu cầu `POSTGRES_PASSWORD`, không tự tạo secret hoặc chạm volume. |

Giới hạn: SQLite không chứng minh hành vi khóa/cạnh tranh hoặc migration trên PostgreSQL production-like. Cần rehearsal trên bản sao PostgreSQL đã khử nhạy cảm trước Release Gate.

## Tái kiểm tra cấu trúc — 20/09/2026

Không sửa source app, frontend, migration hoặc test. Kết quả quan sát:

| Lệnh | Kết quả |
|---|---|
| `python -m pytest -q` | FAIL tại collection: Python hệ thống (`D:\\Anaconda`) không có `fastapi`; 13 module collection error. Đây là lỗi môi trường, không phải kết quả test logic. |
| `.\\venv\\Scripts\\python.exe -m pytest -q` | **FAIL — 4 failed, 71 passed, 22 subtests passed, 7 warnings, 9.48s**. Bốn fail tại AC-018/AC-019, khớp DEF-018/DEF-019 đã ghi nhận. |
| `npm.cmd test -- --coverage` | **PASS — 5 files, 50 tests**; statements 62.86%, branches 46.55%, functions 57.68%, lines 67.90%. |
| `npm.cmd run build` | **PASS** — TypeScript/Vite/PWA; 35 precache entries, 785.87 KiB. |

Kết luận: frontend đạt bộ kiểm tra hiện có; backend suite chạy được trong venv nhưng baseline vẫn fail. Hệ thống chưa đủ điều kiện Release Gate cho đến khi AC-018/AC-019 được sửa theo quy trình implementation/database migration đã phê duyệt và test lại.

## Dịch vụ thực tế và trình duyệt — 19/09/2026

Đã cập nhật file Word trước đó tại Downloads, giữ 4 bảng của mẫu, sửa FT-06/FT-08 thành Fail và bổ sung LIVE-01..07. Bản sao phát hành: `deliverables/05_functional_testing_live_20260919.docx`. Bản trước cập nhật được giữ với hậu tố `_before_live_20260919` trong Downloads.

| Kiểm tra thực tế | Kết quả |
|---|---|
| Gemini qua `generate_financial_advice`, model cấu hình `gemini-3.7-flash` | PASS smoke: gọi provider thật, phản hồi 196 ký tự trong 12.22 giây; chỉ gửi số liệu giả lập, `store=false`. Không kiểm chứng toàn bộ độ đúng nội dung/SLA. |
| Resend `GET https://api.resend.com/domains` | HTTP 400. Lần chẩn đoán tiếp theo xác nhận `validation_error`, `API key is invalid`. FAIL xác thực với khóa hiện tại; chưa gửi email. |
| Web cấu hình `https://daominhtam2k6.dpdns.org` | BLOCKED: `/`, `/login`, `/api/health`, `/api/ready`, `/api/unknown-live-test` đều ConnectionError. Resolve-DnsName không trả IP, chỉ có SOA. Chưa chứng minh health/readiness hoặc TLS. |
| Edge headless, backend Uvicorn thật, SQLite tạm, không mock API | PASS đăng ký và đăng nhập; 7 trang nghiệp vụ hiển thị, không API HTTP >=400 hoặc JS pageerror trong từng lần mở. Tổng 9 smoke checks. |
| Docker/PostgreSQL | BLOCKED: Docker Desktop Linux Engine không khả dụng; không có PostgreSQL test được cấu hình. |

Bằng chứng: `deliverables/live-service-results-20260919.json` (Resend ban đầu được ghi INCONCLUSIVE theo HTTP, nguyên nhân invalid key được xác nhận ở lần chẩn đoán sau); `deliverables/live-browser-results-20260919.json`; `deliverables/live-browser-20260919.png`. Scripts tái hiện: `tools/live_service_checks.py`, `tools/live_browser_checks.py`. Chạy lại script dịch vụ sẽ gọi Gemini thật và có thể tiêu thụ quota.

Browser smoke dùng tài khoản mới, database tạm và chặn service worker; chưa kiểm thử mọi CRUD bằng UI hoặc offline/cache PWA. Đã dừng server thử và dọn database tạm. Không gửi email do khóa không hợp lệ và chưa có địa chỉ nhận thử được cung cấp. Tauri, tải vận hành, backup retention và luồng production xuyên suốt vẫn chưa thực thi. Những kết quả live bổ sung không khắc phục 2 lỗi nghiệp vụ AC-018/019 đã phát hiện.

## Đợt kiểm thử 18–19/09/2026

Kết luận: **chưa đạt đầy đủ baseline yêu cầu**. Bộ test cũ đạt nhưng 6 ca bổ sung theo AC-018/019 phát hiện 4 ca thất bại, tương ứng 2 lỗi nghiệp vụ. Không sửa code ứng dụng trong đợt kiểm thử này.

| Ngày | Kiểm tra | Kết quả quan sát |
|---|---|---|
| 18/09 | Backend trước khi bổ sung ca yêu cầu | 69 passed, 22 subtests passed, 7 warnings; 10.56s |
| 19/09 | `.\venv\Scripts\python.exe -m pytest -q` sau khi thêm `tests/test_baseline_requirements.py` | **4 failed, 71 passed, 22 subtests passed**, 7 warnings; 10.21s |
| 18/09 | `npm.cmd test -- --coverage` | 5 files, 50 tests passed; statements 62.86%, branches 46.55%, functions 57.68%, lines 67.90% |
| 18/09 | `npm.cmd run build` | PASS; TypeScript/Vite/PWA, 35 precache entries; cảnh báo plugin timing |
| 18/09 | `alembic upgrade head` + `alembic check` | PASS trên SQLite tạm mới; revision 20260901_0001; No new upgrade operations detected |
| 19/09 | `python -m pip check` trong venv | No broken requirements found; đây là kiểm tra tương thích dependency, không phải quét lỗ hổng Python |
| 19/09 | `npm.cmd audit --omit=dev --audit-level=high` | found 0 vulnerabilities; chỉ dependency production frontend tại thời điểm chạy |
| 19/09 | `docker info` | Không kết nối được Docker Desktop Linux Engine; chưa chạy PostgreSQL container |

### Lỗi được tái hiện

- **DEF-018 — AC-018 / BR-001 (mức vừa):** cùng người dùng/loại, tạo `Food` rồi `food` hoặc ` Food ` đều được chấp nhận. Kỳ vọng từ chối tên trùng sau trim và so sánh không phân biệt hoa thường. Hai ca route integration với SQLite in-memory thất bại vì không phát sinh HTTPException. Vị trí: `app/routers/categories.py`, `app/schemas/category.py`.
- **DEF-019 — AC-019 / BR-002 (mức vừa):** `BudgetCreate` chấp nhận năm 1999 và 2101. Kỳ vọng ValidationError trước khi ghi dữ liệu. Hai ca schema validation thất bại; hai giá trị biên hợp lệ 2000/2100 đạt. Vị trí: `app/schemas/budget.py`.

### Phạm vi và giới hạn

Đã chạy toàn bộ suite hiện có và bổ sung 6 ca theo baseline. Kết quả này không chứng minh mọi yêu cầu đã đạt. Migration SQLite sạch không chứng minh PostgreSQL, xử lý collision dữ liệu cũ (AC-020), hoặc retention backup. Database tạm đã được xóa sau kiểm tra; không dùng database nghiệp vụ cho migration.

Chưa thực thi E2E trình duyệt, bộ cài Tauri, tải thực tế (AC-015), TLS production (AC-017), Gemini/Resend live, quét lỗ hổng Python/dev dependencies và vòng đời backup (AC-012/021). Cargo không được tìm thấy trong PATH. Coverage nhánh frontend 46.55% còn thấp, đặc biệt Goals/Transactions/Assistant. Xem `docs/software/testing/test-plan.md` để truy vết các khoảng trống.

**Đính chính tài liệu Word ngày 14/09:** kết luận Pass toàn bộ FT-06 và FT-08 chưa đủ bằng chứng; các nhánh AC-018/019 nay đã được tái hiện là Fail. Các ca tổng hợp khác chỉ có bằng chứng cho phạm vi suite đã chạy, không được suy diễn thành nghiệm thu toàn bộ AC.

## Lịch sử ngày 06/09/2026

Ngày chạy: 06/09/2026. Môi trường: workspace local Windows.

| Lệnh | Kết quả |
|---|---|
| `.\venv\Scripts\python.exe -m pytest -q` | PASS — 69 passed, 22 subtests passed, 7 Pydantic deprecation warnings |
| `npm.cmd test -- --coverage` | PASS — 5 files, 50 tests; statements 62.86%, branches 46.55%, functions 57.68%, lines 67.90% |
| `npm.cmd run build` | PASS — TypeScript/Vite build; PWA generated 35 precache entries |

## Defect phát hiện và xử lý

Lần chạy đầu của `pytest -q` thu thập nhầm 15 module test trong `deliverables/browser_tools/greenlet` và lỗi thiếu `psutil`. Nguyên nhân là chưa giới hạn test discovery. Đã thêm `pytest.ini` với `testpaths = tests`; chạy lại thành công. Không xóa hay sửa test của thư viện.

## Cảnh báo và giới hạn

- 7 schema dùng class-based Pydantic config đã deprecated; chưa lỗi ở Pydantic 2 nhưng cần chuyển sang `ConfigDict` trước Pydantic 3.
- Coverage frontend hiện thấp hơn số ghi trong [white-box-test-report-2026-08-31.md](white-box-test-report-2026-08-31.md) ngày 31/08/2026 ở cả bốn chỉ số; báo cáo cũ là snapshot lịch sử, không phải bằng chứng chạy hiện tại.
- Chưa chạy E2E browser, test production PostgreSQL, migration trên database thật, dependency vulnerability scan hoặc external Gemini/Resend live test trong đợt này.
