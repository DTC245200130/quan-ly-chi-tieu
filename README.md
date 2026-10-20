# Sổ Chi Tiêu

Phiên bản web phục vụ đề tài hiện có bốn mục: **Tổng quan, Giao dịch, Danh mục
và Báo cáo**. Giao diện dùng thanh điều hướng ngang và màu indigo, hỗ trợ
desktop/điện thoại và chế độ tối. Xem
[mô tả phiên bản giao diện](docs/software/design/finance-web-edition.md).

> Tra cứu tài liệu theo nhóm tại [docs/README.md](docs/README.md).
>
> Hồ sơ AI-Augmented SDLC: xem [đánh giá tuân thủ](docs/governance/sdlc-compliance-audit.md),
> [prompt register](docs/ai-engineering/history/prompts.md), [thư viện prompt mẫu](docs/ai-engineering/prompts.md), [human gates](docs/governance/human-gates.md) và
> [nhật ký AI](docs/ai-engineering/history/ai-process-log.md).

Ứng dụng quản lý tài chính cá nhân gồm một backend FastAPI dùng chung cho hai kênh phát hành:

- Web responsive/PWA cho Windows, Android và iOS.
- Ứng dụng Windows đóng gói bằng Tauri, kết nối tới cùng API production.

## Kiến trúc

```text
Web/PWA ───────────┐
                   ├── FastAPI ── PostgreSQL
Windows/Tauri ─────┘          ├── persistent uploads
                              ├── Gemini
                              └── Resend
```

Bản Windows hiện yêu cầu kết nối Internet cho toàn bộ chức năng. Dữ liệu không được lưu thành một database nghiệp vụ riêng trên từng máy, nhờ đó tài khoản và số liệu dùng chung nguồn dữ liệu với web. Offline chỉ được xem xét trong tương lai nếu phản hồi người dùng cho thấy nhu cầu đủ lớn.

## Clone và chạy thử trên local

### 1. Yêu cầu môi trường

- Git.
- Python 3.13.
- Node.js 24, kèm npm.

Kiểm tra các công cụ trong PowerShell:

```powershell
git --version
python --version
node --version
npm.cmd --version
```

### 2. Clone repository

```powershell
git clone https://github.com/daominhtam2k6/Expense-Management-Ai-Integration.git
Set-Location Expense-Management-Ai-Integration
```

Nếu đã clone từ trước, cập nhật nhánh chính bằng `git pull origin main` và bảo đảm
không có thay đổi local cần giữ trước khi pull.

### 3. Tạo cấu hình local

Sao chép file môi trường mẫu:

```powershell
Copy-Item .env.example .env
```

Mở `.env` và thay `SECRET_KEY` bằng một giá trị riêng, dài và ngẫu nhiên. Có thể
tạo giá trị bằng Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cấu hình mặc định trong `.env.example` sử dụng SQLite tại `expense.db`, bật
`AUTO_CREATE_SCHEMA=true` và không yêu cầu PostgreSQL. Các chức năng Gemini và
gửi email là tùy chọn; để trống `AI_API_KEY` và `RESEND_API_KEY` nếu chỉ kiểm thử
các chức năng local cơ bản. Không commit file `.env`.

### 4. Cài dependency và build frontend

Từ thư mục gốc repository:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Set-Location frontend
npm.cmd ci
npm.cmd run build
Set-Location ..
```

Lệnh build tạo `frontend/dist`; FastAPI sẽ phục vụ frontend này cùng API trên
một cổng. Không cần chạy Vite riêng cho quy trình kiểm thử local cơ bản.

### 5. Khởi động ứng dụng

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Giữ cửa sổ PowerShell này đang chạy, sau đó truy cập:

- Ứng dụng: `http://127.0.0.1:8000`
- Kiểm tra API: `http://127.0.0.1:8000/api/health`
- Kiểm tra database: `http://127.0.0.1:8000/api/ready`
- Swagger UI: `http://127.0.0.1:8000/api/docs`

Kết quả mong đợi của hai endpoint kiểm tra lần lượt là `{"status":"ok"}` và
`{"status":"ready"}`. Ở lần chạy đầu, ứng dụng tự tạo schema SQLite vì cấu
hình local bật `AUTO_CREATE_SCHEMA=true`.

### 6. Chạy kiểm thử tự động

Dừng server bằng `Ctrl+C` hoặc mở một cửa sổ PowerShell khác tại thư mục gốc:

```powershell
.\venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm.cmd test
npm.cmd run build
Set-Location ..
```

Nếu cổng `8000` đang được chương trình khác sử dụng, có thể chạy thử ở cổng khác:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

Khi đó mở `http://127.0.0.1:8001`. Nếu frontend chưa được build, API sẽ trả lỗi
`503` ở trang chính; chạy lại `npm.cmd ci` và `npm.cmd run build` trong thư mục
`frontend`.

## Deploy web lên Azure for Students

Lộ trình hiện tại: triển khai web, kiểm tra với người dùng thử, rồi phát hành
Windows Tauri kết nối cùng backend. Xem [hướng dẫn Azure](docs/software/deployment/azure-deploy.md)
để chọn VM, cấu hình HTTPS, lưu dữ liệu, sao lưu và kiểm tra sau triển khai.

## Deploy web bằng Docker

Production mặc định dùng PostgreSQL và hai volume bền vững cho database và avatar.

1. Điền tối thiểu các biến sau trong `.env`:

   ```dotenv
   POSTGRES_PASSWORD=mat-khau-database-manh
   SECRET_KEY=chuoi-ngau-nhien-dai
   FRONTEND_URL=https://finance.example.com
   TRUSTED_HOSTS=finance.example.com
   CORS_ORIGINS=http://tauri.localhost,https://tauri.localhost
   ```

2. Build và khởi động:

   ```powershell
   docker compose up -d --build
   docker compose ps
   ```

3. Kiểm tra:

   ```text
   GET https://finance.example.com/api/health
   GET https://finance.example.com/api/ready
   ```

Container tự chạy `alembic upgrade head` trước khi khởi động API. Reverse proxy hoặc cloud load balancer phải cung cấp HTTPS và chuyển tiếp traffic tới cổng ứng dụng.

### Database đã tồn tại

Migration đầu tiên được thiết kế cho database production mới. Không chạy `alembic upgrade head` trực tiếp lên file `expense.db` cũ đã có bảng. Sau khi backup và xác nhận schema cũ đã có đủ các cột hiện tại, đánh dấu revision bằng:

```powershell
.\venv\Scripts\python.exe -m alembic stamp 20260901_0001
```

## Cài web như ứng dụng

Build web đã có manifest, service worker và icon PWA. Người dùng có thể cài từ Microsoft Edge/Chrome trên Windows hoặc thêm vào màn hình chính trên mobile.

Service worker chỉ cache app shell và static assets. Các đường dẫn `/api/*` và `/uploads/*` không được cache.

## Build ứng dụng Windows

Yêu cầu bổ sung:

- Rust stable qua `rustup`.
- Visual Studio Build Tools với workload Desktop development with C++ và Windows SDK.
- WebView2 Runtime; Windows 10/11 thường đã có sẵn.

Tạo cấu hình desktop:

```powershell
Set-Location frontend
Copy-Item .env.desktop.example .env.desktop
```

Sửa `.env.desktop` để trỏ tới API production:

```dotenv
VITE_API_BASE_URL=https://finance.example.com/api
```

Chạy development shell:

```powershell
npm.cmd run desktop:dev
```

Tạo installer:

```powershell
npm.cmd run desktop:build
```

Installer `.msi` và `-setup.exe` được tạo trong `frontend/src-tauri/target/release/bundle/`. Cấu hình production bắt buộc có `VITE_API_BASE_URL`; build sẽ dừng nếu biến này bị thiếu.

Trước khi phát hành công khai, cần cấu hình chứng thư code-signing để giảm cảnh báo Microsoft SmartScreen. Auto-update nên được bật sau khi quy trình ký số và nơi lưu release artifacts đã ổn định.

## Kiểm thử

```powershell
.\venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm.cmd test -- --coverage
npm.cmd run build
```

Kiểm tra migration độc lập:

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
.\venv\Scripts\python.exe -m alembic check
```

## Biến môi trường production

| Biến | Bắt buộc | Mục đích |
|---|---:|---|
| `DATABASE_URL` | Có | Chuỗi kết nối PostgreSQL dùng driver `psycopg` |
| `SECRET_KEY` | Có | Ký access token |
| `FRONTEND_URL` | Có | Tạo link đặt lại mật khẩu |
| `CORS_ORIGINS` | Có cho desktop | Origin được phép gọi API |
| `TRUSTED_HOSTS` | Khuyến nghị | Danh sách hostname public |
| `AI_API_KEY` | Cho AI | Gemini API key |
| `GEMINI_MODEL` | Không | Model Gemini |
| `RESEND_API_KEY` | Cho email | Gửi email đặt lại mật khẩu |
| `RESEND_FROM_EMAIL` | Cho email | Địa chỉ người gửi đã xác minh |

Không commit `.env`, `.env.desktop`, database, uploads hoặc chứng thư ký số.

## Chạy với Nginx và pgAdmin

Chuẩn bị `.env` theo `.env.example`, bổ sung:
PGADMIN_DEFAULT_EMAIL và PGADMIN_DEFAULT_PASSWORD bằng giá trị riêng.

Khởi động:

```bash
sudo docker compose -f compose.yaml -f compose.pgadmin.yaml -f compose.nginx.yaml up -d --build
```

Truy cập trong Ubuntu:

- Web qua Nginx: http://localhost:8088
- pgAdmin: http://localhost:5050

Nginx chuyển tiếp đến web:8000 và bổ sung security headers.
Phương án hiện tại dùng HTTP, chưa bật HTTPS.

## Giám sát bằng Prometheus và Grafana

Các thành phần:
- cAdvisor: CPU và RAM container.
- Nginx exporter: trạng thái và số request Nginx.
- PostgreSQL exporter: trạng thái và kết nối database.
- Prometheus: thu thập metrics.
- Grafana: hiển thị dashboard.

### Chuẩn bị khi triển khai mới

Trong PostgreSQL, tạo tài khoản giám sát:

```sql
CREATE ROLE expense_monitor LOGIN;
GRANT CONNECT ON DATABASE expense TO expense_monitor;
GRANT pg_monitor TO expense_monitor;
```

Dùng `\password expense_monitor` trong psql để đặt mật khẩu.
Điền đúng mật khẩu này vào POSTGRES_EXPORTER_PASSWORD trong .env.
Đặt GRAFANA_ADMIN_USER và GRAFANA_ADMIN_PASSWORD riêng.
Không commit .env.

### Khởi động

```bash
sudo docker compose \
  -f compose.yaml \
  -f compose.pgadmin.yaml \
  -f compose.nginx.yaml \
  -f compose.monitoring.yaml \
  up -d --build
```

### Truy cập trong Ubuntu

- Prometheus: http://localhost:9091
- Grafana: http://localhost:3001
- Web qua Nginx: http://localhost:8088

Kiểm tra Prometheus Targets có đủ bốn job UP:
prometheus, cadvisor, nginx, postgres.

Datasource Prometheus-Expense được tạo tự động từ file provisioning.
Dashboard được lưu tại:
deploy/grafana/dashboards/expense-monitoring.json

Khi triển khai Grafana mới, dùng chức năng Import dashboard để nhập
file JSON trên và sử dụng datasource Prometheus-Expense.
File dashboard hiện được lưu để nhập thủ công, chưa tự động provision.

Dashboard gồm sáu panel: RAM, CPU, trạng thái Nginx,
request Nginx, trạng thái PostgreSQL và số kết nối database expense.
Các truy vấn CPU/RAM lọc project Docker Compose là expense.

Prometheus lưu dữ liệu tối đa theo cấu hình retention 2 ngày/512 MB.
cAdvisor dùng privileged và các mount máy chủ phục vụ môi trường lab;
không công bố cổng cAdvisor hoặc exporter ra ngoài.

## Mốc 3: Log tập trung Loki + Promtail

Promtail thu thập log các service web, nginx và db thuộc project expense.
Loki lưu trữ log; Grafana truy vấn qua datasource Loki-Expense.
Loki được truy cập từ máy chủ tại http://localhost:3101.
Grafana được truy cập tại http://localhost:3001.

Khởi động toàn bộ hệ thống:

```bash
sudo docker compose \
  -f compose.yaml \
  -f compose.pgadmin.yaml \
  -f compose.nginx.yaml \
  -f compose.monitoring.yaml \
  -f compose.logging.yaml \
  up -d --pull never
```

Các image Loki 3.7.8 và Promtail 3.6.8 phải có sẵn nếu dùng --pull never.

Kiểm tra Loki:

```bash
curl -i http://127.0.0.1:3101/ready
```

Trong Grafana Explore, chọn Loki-Expense và chạy lần lượt:

```logql
{project="expense", service="nginx"}
```

```logql
{project="expense", service="web"}
```

```logql
{project="expense", service="db"} |= "division by zero"
```

Tạo log lỗi thử nghiệm PostgreSQL, không thay đổi dữ liệu:

```bash
sudo docker exec expense-db-1 \
  psql -U expense -d expense -c 'SELECT 1 / 0;'
```

Lưu ý: Promtail đã hết vòng đời hỗ trợ; sử dụng theo yêu cầu bài thực hành.

## Hardening hệ thống

- Web chạy UID/GID 1000:1000, cap_drop ALL và no-new-privileges.
- Web dùng tài khoản expense_app, không dùng tài khoản superuser.
- expense là bootstrap superuser, giữ riêng cho quản trị.
- expense_app được cấp CONNECT database, USAGE schema,
  SELECT/INSERT/UPDATE/DELETE trên bảng và USAGE/SELECT trên sequence.
- Tạo tài khoản và cấp quyền trước khi bật cấu hình hardening;
  đặt mật khẩu riêng bằng lệnh \password trong psql.
- APP_DATABASE_URL trong .env dùng mật khẩu expense_app đã URL-encode.
- Không commit .env, mật khẩu hoặc bản sao lưu database.

Tách bốn mạng: frontend, backend, monitoring và logging.
Backend dùng internal: true. Kiểm tra cho thấy container chỉ thuộc
frontend không kết nối trực tiếp được PostgreSQL, trong khi web
vẫn đọc được dữ liệu bằng expense_app.

Các cổng công bố chỉ bind 127.0.0.1; PostgreSQL không publish ra host.
Nginx có security headers. Uvicorn tin cậy proxy trong subnet frontend
172.29.0.0/16 thay cho "*"; kiểm tra và cập nhật nếu subnet thay đổi.

Khởi động hệ thống đã chuẩn bị database và tài khoản:

```bash
sudo docker compose \
  -f compose.yaml \
  -f compose.pgadmin.yaml \
  -f compose.nginx.yaml \
  -f compose.monitoring.yaml \
  -f compose.logging.yaml \
  -f compose.hardening.yaml \
  up -d --no-build --pull never
```

Lệnh trên yêu cầu image đã có sẵn.
Khi triển khai mới, cần tạo schema bằng migration trước,
sau đó tạo expense_app và cấp quyền trên các bảng/sequence.

Cấu hình hardening bỏ migration tự động khỏi entrypoint của web.
Migration tương lai phải chạy riêng bằng tài khoản có quyền phù hợp,
sau đó cập nhật quyền expense_app cho các đối tượng mới.

Giới hạn của lab:
- cAdvisor vẫn dùng privileged.
- Promtail vẫn chạy root và truy cập Docker socket;
  mount socket :ro không giới hạn Docker API thành chỉ đọc.
- Chưa triển khai HTTPS.
- Không coi toàn bộ container đã chạy non-root.
