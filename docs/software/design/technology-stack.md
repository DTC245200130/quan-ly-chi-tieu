# Đánh giá technology stack

> Trạng thái: **DRAFT FOR HUMAN REVIEW**. Đánh giá ngày 06/09/2026 dựa trên baseline requirements v1.1, Architecture Gate và Database Gate đã được phê duyệt trong `docs/governance/human-gates.md`. Tài liệu này không thay đổi trạng thái Human Gate hoặc ADR hiện có.

## 1. Kết luận

Stack hiện tại **phù hợp với phạm vi đã duyệt**: ứng dụng tài chính cá nhân online-only, tải vận hành bình thường, một backend dùng chung cho web/PWA và Windows. Không có bằng chứng về yêu cầu quy mô, hiệu năng hoặc chi phí đủ mạnh để thay FastAPI, SQLAlchemy, React, Tauri, PostgreSQL, Gemini, Resend, Caddy hay mô hình Azure VM hiện tại.

Quyết định mặc định là **GIỮ NGUYÊN**. Các việc bắt buộc trước Release Gate chủ yếu là làm build/deploy tái lập và tạo bằng chứng kiểm thử; đây không phải đề xuất thêm framework. Repository chưa có dependency vulnerability scan, nên tài liệu **không kết luận dependency hoặc image nào an toàn/không có lỗ hổng**.

## 2. Cách đọc version và mức quyết định

- **MUST:** cần hoàn thành trước khi coi release production là có thể tái lập hoặc đáp ứng baseline đã duyệt.
- **SHOULD:** lợi ích vận hành/kiểm thử đo được, nên làm nếu tiếp tục vận hành ngoài demo ngắn hạn.
- **OPTIONAL:** chỉ kích hoạt khi metric hoặc nhu cầu thực tế đạt điều kiện nêu rõ.
- Python lấy version pin trực tiếp từ `requirements.txt`. JavaScript lấy version resolved từ `frontend/package-lock.json`; khi khác, cột version cũng nêu range khai báo trong `package.json`.
- Rust lấy constraint từ `frontend/src-tauri/Cargo.toml`. Không có `Cargo.lock`, vì vậy không suy đoán version resolved của crate dùng range.
- Image/container dùng đúng tag trong Dockerfile/Compose. Tag như `17-alpine`, `2-alpine`, `24-alpine`, `3.13-slim` không phải digest bất biến.

## 3. Technology → purpose → version → quyết định

| Technology | Purpose trong Sổ Chi Tiêu | Version hiện tại từ repository | Quyết định | Rationale |
|---|---|---|---|---|
| FastAPI | HTTP API, auth dependency, validation integration, health/readiness và phục vụ SPA build | `0.141.1` | **GIỮ — MUST** | Phủ đủ API capability, OpenAPI và async-compatible delivery; tải mục tiêu dưới 10 giây không đòi framework khác. Boundary router/service/repository mới quyết định maintainability và tenant isolation. |
| Pydantic | Request/response schema và validation | `2.13.4` (`pydantic_core 2.46.4`) | **GIỮ — MUST** | Tích hợp tự nhiên với FastAPI và tăng testability. Bảy schema còn dùng cấu hình class-based deprecated phải được xử lý trước Pydantic 3, nhưng chưa tạo lý do đổi thư viện. |
| SQLAlchemy | ORM/repository, transaction và parameter binding cho SQLite/PostgreSQL | `2.0.52` | **GIỮ — MUST** | Một persistence abstraction cho hai DB, hỗ trợ transaction và user-scoped query. Không thay thế yêu cầu constraint DB và test PostgreSQL. |
| Alembic | Schema authority và migration production | `1.19.1` | **GIỮ — MUST** | Được yêu cầu trực tiếp bởi `NFR-DATA-001` và kiến trúc; phù hợp SQLAlchemy. Migration phải fail-fast khi gặp collision theo `BR-003`. |
| PostgreSQL | Database production, constraint/concurrency và persistence | Image `postgres:17-alpine`; driver `psycopg[binary] 3.3.5` | **GIỮ — MUST** | Đáp ứng integrity và concurrency production ở tải bình thường với chi phí vận hành hợp lý. Tag image chưa khóa patch/digest nên deployment chưa hoàn toàn tái lập. |
| SQLite | Database phát triển nhanh, không phải production evidence | SQLite đi cùng Python runtime; repository không pin version SQLite riêng | **GIỮ — MUST (dev only)** | Vòng lặp local rẻ và đơn giản, đúng requirement. Khác biệt dialect/locking/collation buộc phải có test PostgreSQL riêng; không dùng SQLite làm bằng chứng duy nhất. |
| React | Presentation và component UI dùng chung | `18.3.1` (range `^18.3.1`) | **GIỮ — MUST** | Đáp ứng UI responsive, route/form/state và tái sử dụng trong PWA/Tauri. Không có nhu cầu SSR hoặc native UI chứng minh lợi ích của việc đổi framework. |
| React Router | Client routing và deep link | `7.18.2` (range `^7.18.2`) | **GIỮ — MUST** | Có mục đích rõ cho auth/application routes; cần production-routing test cùng SPA fallback. |
| TypeScript | Static typing frontend và build-time checking | resolved `5.9.3` (range `^5.6.3`) | **GIỮ — MUST** | Giảm lỗi contract/refactor và hỗ trợ maintainability. Range khai báo rộng nhưng lockfile hiện tạo build npm tái lập. |
| Vite + React plugin | Dev/build pipeline cho web và desktop bundle | Vite `8.2.2`; plugin `6.1.0` | **GIỮ — MUST** | Build nhanh, cấu hình PWA/Tauri hiện dùng trực tiếp; không có bottleneck build được đo để đổi bundler. |
| Vitest + Testing Library/jsdom | Unit/component test và coverage frontend | Vitest `4.1.11`; coverage-v8 `4.1.11`; Testing Library React `16.3.0`, user-event `14.6.1`, jest-dom `6.8.0`; jsdom `26.1.0` | **GIỮ — MUST** | Cùng toolchain Vite, đáp ứng bằng chứng test lặp lại. Không thay thế E2E browser/production-routing test. |
| PWA (`vite-plugin-pwa`) | Installable web shell và cache static assets | `1.3.0` | **GIỮ — MUST** | Phù hợp `FR-REL-001`; cấu hình loại `/api/*` và `/uploads/*` khỏi navigation fallback, đúng online-only. Không mở rộng thành offline business data. |
| Tauri | Đóng gói React thành MSI/NSIS Windows, capability native tối thiểu | crate `tauri 2.11.3`; CLI resolved `2.11.4` (range `^2.11.4`); `tauri-build 2.6.3`; `tauri-plugin-log 2`; Rust minimum `1.77.2` | **GIỮ — MUST** | Tái sử dụng UI/API, footprint và capability nhỏ hơn một desktop stack đầy đủ; phù hợp năng lực web hiện có. Thiếu `Cargo.lock` nên version resolved của crate range chưa có bằng chứng. |
| Gemini REST | Trợ lý read-only nhận context tổng hợp/loại định danh | REST endpoint `v1beta/interactions`; model mặc định `gemini-3.7-flash`; HTTP client `requests 2.32.3`; không dùng Gemini SDK | **GIỮ — MUST cho FR-AI** | REST adapter nhỏ, timeout/retry/error mapping và `store: false` phù hợp boundary privacy. API `v1beta` và tên model là dependency bên ngoài biến động; cần contract/live smoke test có kiểm soát, không cần SDK nếu chưa phát sinh maintenance cost. |
| Resend REST | Gửi email reset mật khẩu | Endpoint `https://api.resend.com/emails`; HTTP client `requests 2.32.3`; không có SDK/version Resend trong repo | **GIỮ — MUST cho FR-AUTH-002** | Adapter trực tiếp ít dependency và dễ mock. Cần live test domain/sender/rate-limit ở môi trường release; Azure credit không bao gồm chi phí vendor. |
| Docker multi-stage image | Build React và chạy FastAPI bằng image nhất quán | `node:24-alpine`, `python:3.13-slim`; Docker Engine version không được pin trong repo | **GIỮ — MUST** | Đơn giản hóa deploy một artifact và phục vụ SPA/API cùng origin. Base tag trôi làm giảm reproducibility/supply-chain traceability. |
| Docker Compose | Orchestrate web, PostgreSQL, volume và proxy trên một VM | Compose schema không khai báo version; repository không pin Compose CLI | **GIỮ — MUST** | Đủ cho một VM/demo tải bình thường, chi phí và độ phức tạp thấp. Không cung cấp HA, scheduler hay backup tự động. |
| Caddy | TLS termination, certificate automation, compression, reverse proxy và redirect | Image `caddy:2-alpine`; patch/digest không pin | **GIỮ — MUST** | Cấu hình nhỏ và giảm chi phí vận hành TLS. Cần pin image và kiểm thử header/TLS/CSP ở deployment thật. |
| Azure VM | Production host cho Docker Compose, PostgreSQL và volumes | Ubuntu `24.04 LTS` được tài liệu chỉ định; VM SKU/region/Docker version không pin trong repo | **GIỮ — SHOULD cho giai đoạn hiện tại** | Phù hợp demo/nhóm nhỏ và Azure for Students, không thêm managed-service cost. Một VM là single point of failure; chưa đủ bằng chứng cho mục tiêu gần 24/7. |

Các dependency hỗ trợ có mục đích rõ: `uvicorn 0.52.3` chạy ASGI; `bcrypt 4.0.1`/`passlib 1.7.4` băm mật khẩu; `python-jose 3.5.0` xử lý JWT; `python-multipart 0.0.32` nhận form/upload; `email-validator 2.3.0` kiểm tra email; `python-dotenv 1.2.2` nạp cấu hình local; `cryptography 50.0.0` và các gói crypto liên quan hỗ trợ auth stack. Các transitive package còn lại trong `requirements.txt` không được xem là framework độc lập; vulnerability status của toàn bộ tập này chưa được xác nhận.

## 4. Đánh giá theo tiêu chí

| Tiêu chí | Kết quả | Điều kiện/giới hạn |
|---|---|---|
| Đáp ứng requirements | **Phù hợp** | Stack bao phủ API, auth, CRUD/analytics, AI/email, PostgreSQL migration, web/PWA và Windows. Offline đã withdrawn nên không cần local DB/sync. |
| Bảo mật & privacy | **Phù hợp có điều kiện** | Có TLS edge, server-side secrets, validation, JWT expiry, bcrypt, user scope và Gemini gateway. Chưa có vulnerability scan; CSP/proxy trust, image provenance và deployment thật chưa được xác minh đầy đủ. |
| Maintainability | **Phù hợp** | Một React codebase, một API, typed schemas và ORM/migration giảm phân mảnh. REST adapters tránh SDK không cần thiết. Cần xử lý Pydantic deprecation và lock Rust dependencies. |
| Testability | **Phù hợp có khoảng trống** | FastAPI/Pydantic/services và Vitest/Testing Library dễ unit/integration test. Còn thiếu PostgreSQL migration/concurrency test, E2E browser, Tauri installer smoke test và live-contract test có kiểm soát. |
| Hiệu năng tải bình thường | **Có khả năng phù hợp, chưa chứng minh định lượng** | Kiến trúc stateless + relational DB đủ hợp lý cho phạm vi; `NFR-PERF-001` chưa định nghĩa concurrency, dataset hoặc percentile nên không thể tuyên bố đạt chỉ từ stack. |
| Triển khai | **Phù hợp cho một VM** | Compose/Caddy/Alembic/healthcheck tạo đường deploy đơn giản. Tag trôi, thiếu rollout/rollback đã thử, backup automation và HA làm giảm readiness production. |
| Chi phí vận hành | **Thấp cho demo/nhóm nhỏ** | Một VM và open-source stack tránh managed-service cost; đổi lại nhóm tự chịu patching, DB, backup, monitoring và incident. Gemini/Resend tính phí ngoài Azure. |
| Năng lực nhóm | **Phù hợp theo bằng chứng repo** | Code, tests và CI hiện hữu cho Python/React/TypeScript/Docker/Tauri. Không có bằng chứng đội ngũ đã vận hành PostgreSQL/Caddy/Azure 24/7; không nên giả định năng lực này. |

## 5. Đề xuất thay đổi có lợi ích đo được

| Mức | Đề xuất | Lợi ích/điều kiện đo | Migration cost | Risk | Phương án giữ nguyên |
|---|---|---|---|---|---|
| **MUST** | Khóa base/runtime image và service image bằng patch version hoặc digest đã được CI kiểm tra; ghi nhận Docker/Compose minimum version | Cùng commit sinh cùng base bits; giảm thay đổi ngoài ý muốn và cho phép truy vết image trong release | Thấp: cập nhật tag/digest và quy trình refresh định kỳ; không đổi application framework | Pin quá lâu bỏ lỡ security fix; digest khác kiến trúc có thể làm build fail | Giữ moving tag nhưng chấp nhận build không hoàn toàn tái lập, lưu image digest của từng release và rebuild/test trước deploy |
| **MUST** | Commit `frontend/src-tauri/Cargo.lock` cho application và đồng bộ version CLI/crate trong release pipeline | Build Windows resolve cùng crate graph; sai lệch version có thể phát hiện bằng diff/CI thay vì lúc đóng gói | Thấp: tạo lockfile bằng toolchain đã duyệt, review rồi CI `--locked`; không nâng dependency có chủ ý | Lockfile ban đầu có thể ghi nhận transitive version chưa được scan; CLI/crate không nhất thiết có cùng patch | Giữ manifest range và chấp nhận mỗi build có thể resolve khác; lưu SBOM/build artifact để điều tra |
| **MUST** | Trước Release Gate, chạy vulnerability scan cho Python, npm, Rust và container image; lưu tool/version/date/result làm evidence | Có số finding theo severity và SLA xử lý; thay thế trạng thái “chưa biết” bằng bằng chứng lặp lại | Thấp–trung bình: cấu hình CI và triage; có thể cần exception có hạn | False positive, advisory thiếu hoặc fix gây breaking change; scan không chứng minh hệ thống an toàn | Không scan và giữ nguyên dependency, nhưng Release Gate phải ghi rõ rủi ro supply-chain chưa định lượng; không được tuyên bố an toàn |
| **MUST** | Chạy test production-like trên PostgreSQL 17, gồm Alembic upgrade, constraint/collision fail-fast, owner isolation và đường rollback/restore đã định nghĩa | Pass/fail tái lập cho `NFR-DATA-001`, `BR-003`; đo migration duration và phát hiện khác biệt SQLite | Trung bình: fixture/container CI, dataset collision và quy trình restore | Test data không đại diện hoặc migration test làm chậm CI | Giữ SQLite-only loop để phát triển nhưng không dùng làm release evidence; chạy checklist thủ công trên staging PostgreSQL |
| **SHOULD** | Thêm E2E browser, production routing/PWA và Windows installer smoke test ở release workflow | Đo được các critical journey pass, deep-link không trả sai HTML/API, MSI/NSIS cài/chạy/gọi HTTPS thành công | Trung bình: test harness, runner Windows và bảo trì selector/artifact | Flaky test và CI lâu hơn | Giữ unit/component tests, nhưng checklist release thủ công phải ghi người chạy, artifact và kết quả |
| **SHOULD** | Tự động hóa backup ngoài VM, expiry ≤30 ngày và restore drill; đặt RPO/RTO sau Human Gate | Đo tỷ lệ backup thành công, tuổi backup, thời gian restore và bằng chứng xóa đúng retention | Trung bình: storage, schedule, encryption, runbook và chi phí nhỏ | Backup sai cấu hình có thể lộ dữ liệu hoặc tạo cảm giác an toàn giả | Giữ lệnh backup thủ công, nhưng không thể tuyên bố gần 24/7/retention có hiệu lực nếu không có lịch và restore evidence |
| **SHOULD** | Thiết lập baseline tải sau khi con người duyệt concurrency/dataset/percentile; chỉ scale khi vi phạm | Chuyển `<10 giây` thành metric đo được; tránh trả tiền hoặc thêm hạ tầng trước nhu cầu | Thấp–trung bình: workload, môi trường và dashboard kết quả | Benchmark không đại diện hoặc làm ảnh hưởng môi trường thật | Giữ một VM và đo latency từ structured logs; không tuyên bố đạt NFR hiệu năng định lượng |
| **OPTIONAL** | Chuyển PostgreSQL sang Azure managed service/chạy nhiều app instance chỉ khi SLO, downtime, restore drill hoặc công sức vận hành vượt ngưỡng được duyệt | Giảm công việc patch/backup DB hoặc single-host downtime; lợi ích phải thể hiện bằng giờ vận hành/tháng, RTO và availability | Cao: network/TLS/secrets, data migration, backup, cost model và rollback | Chi phí tăng, egress/lock-in, cấu hình sai và downtime migration | Tiếp tục PostgreSQL container trên VM, tăng kỷ luật backup/monitoring và chấp nhận single point of failure |
| **OPTIONAL** | Chỉ cân nhắc Gemini/Resend SDK hoặc đổi vendor khi contract break/failure rate/cost/maintenance vượt ngưỡng đã duyệt | Giảm code adapter hoặc vendor incident nếu số liệu thực tế chứng minh; hiện chưa có lợi ích đo được | Trung bình–cao: adapter, privacy review, test contract, dữ liệu/cấu hình và rollout | Vendor lock-in mới, thay đổi privacy/cost và lỗi hành vi | Giữ REST adapter hiện tại, pin contract bằng tests, timeout/error mapping và cấu hình model/sender qua environment |

Không đề xuất Kubernetes, microservices, Redis/cache, message queue, SSR framework, local-first database hoặc offline sync. Baseline hiện tại không yêu cầu chúng và chưa có metric cho thấy chi phí phức tạp được hoàn vốn.

## 6. ADR cần con người duyệt

Các quyết định sau là **PROPOSED**; người có thẩm quyền cần chấp nhận/từ chối và cập nhật artifact ADR/Human Gate. Tài liệu này không tự chuyển trạng thái.

### ADR-TS-001 — Reproducible dependency và container policy

- **Status:** PROPOSED
- **Context:** npm có lockfile; Rust application thiếu `Cargo.lock`; Docker/PostgreSQL/Caddy dùng tag trôi.
- **Decision đề xuất:** commit Rust lockfile, build locked; pin production images bằng patch/digest; lưu digest/SBOM và chỉ refresh qua CI test + vulnerability review.
- **Rationale:** giảm drift giữa CI và production, tạo khả năng truy vết release.
- **Migration cost:** thấp; thay đổi manifest/release process, không đổi framework.
- **Risk:** pin cũ có thể giữ vulnerability; cần cadence refresh và exception có hạn.
- **Giữ nguyên:** cho phép resolve/tag trôi nhưng lưu digest từng artifact; chấp nhận reproducibility thấp hơn.

### ADR-TS-002 — Release evidence trên production-like stack

- **Status:** PROPOSED
- **Context:** test report ghi chưa chạy PostgreSQL thật, E2E browser, dependency scan hoặc live Gemini/Resend test.
- **Decision đề xuất:** Release Gate yêu cầu PostgreSQL 17 migration/integration suite, E2E critical journeys, Windows installer smoke test, vulnerability scan và contract smoke test cho integration khi có credential kiểm thử.
- **Rationale:** stack phù hợp về thiết kế không đồng nghĩa triển khai đã đạt requirements.
- **Migration cost:** trung bình; thêm CI/staging evidence và triage, không đổi runtime architecture.
- **Risk:** CI cost/flakiness và secret management.
- **Giữ nguyên:** kiểm thủ công có biên bản cho demo; Release Gate vẫn PENDING và không tuyên bố production-ready.

### ADR-TS-003 — Azure single-VM deployment horizon

- **Status:** PROPOSED
- **Context:** Compose trên một Azure VM tối ưu chi phí nhưng là single point of failure; `NFR-REL-002` chưa có SLI/SLO/RPO/RTO định lượng.
- **Decision đề xuất:** giữ một VM cho demo/khối lượng hiện tại; chỉ chuyển managed PostgreSQL hoặc multi-instance khi Human Gate đặt SLO/RPO/RTO và telemetry/giờ vận hành chứng minh ngưỡng bị vi phạm.
- **Rationale:** tránh thêm chi phí trước nhu cầu, đồng thời không nhầm cấu hình demo với HA.
- **Migration cost:** hiện tại thấp; migration managed/HA trong tương lai cao.
- **Risk:** outage VM ảnh hưởng toàn bộ dịch vụ cho tới khi có kiến trúc HA.
- **Giữ nguyên:** tiếp tục một VM với backup ngoài máy, restore drill, monitoring và tuyên bố availability giới hạn.

## 7. Kiểm chứng phạm vi đánh giá

- Tất cả framework/công cụ được yêu cầu đều có purpose trong bảng; các dependency hỗ trợ chính cũng được giải thích.
- Version chỉ lấy từ `requirements.txt`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/src-tauri/Cargo.toml`, Dockerfile, Compose và tài liệu triển khai trong repository. Mục không được pin được ghi rõ là **không pin**, không đoán.
- Không chạy upgrade, install, vulnerability scan, live Gemini/Resend call, load test hoặc thay đổi code.
- Kết luận “phù hợp” là đánh giá fit theo requirements/architecture; không phải chứng nhận bảo mật, hiệu năng, availability hay production readiness.
