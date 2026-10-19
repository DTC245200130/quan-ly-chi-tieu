# Triển khai web lên Azure for Students

Giai đoạn đầu: web React và API FastAPI dùng chung địa chỉ HTTPS, PostgreSQL
chạy cùng máy ảo Linux. Bản Windows Tauri sẽ kết nối API này sau khi web đã
được kiểm tra với người dùng thử. Chưa cần đổi kiến trúc sang ứng dụng offline.

## 1. Chọn máy chủ và kiểm tra ngân sách

Trong Azure Portal, chọn đúng subscription **Azure for Students** và tạo resource
group riêng, ví dụ `expense-demo`. Tạo VM Ubuntu 24.04 LTS, kiến trúc x64,
đăng nhập bằng SSH key. Với demo ít người dùng, bắt đầu từ 2 GiB RAM nếu ngân sách
cho phép; đây là đề xuất ban đầu, chưa phải kết quả kiểm tra tải.

Trước khi nhấn Create, kiểm tra region/SKU thực sự được subscription cho phép,
hạn mức Free services, giá máy, OS disk, public IPv4 và backup. Không mặc định
mọi VM đều miễn phí. $100 là tổng credit có hạn sử dụng, không phải $100/tháng.
Giữ spending limit và tạo budget/cảnh báo trong Cost Management; budget chỉ
cảnh báo, không tự dừng tài nguyên. Chưa thêm RDS/PostgreSQL managed, load balancer
hay dịch vụ trả phí khác cho demo này.

Network Security Group: mở TCP 80/443 cho người dùng; TCP 22 chỉ từ IP quản trị.
Không mở 8000 hoặc 5432. Dùng public IP tĩnh. Trong public IP > Configuration,
đặt DNS name label rồi sao chép **FQDN thực tế** Azure cung cấp. Có thể dùng
FQDN này trước khi mua tên miền; nếu dùng tên miền riêng, trỏ DNS tới public IP.

Tài liệu chính thức:
- https://azure.microsoft.com/en-us/free/students/
- https://learn.microsoft.com/en-us/azure/virtual-machines/create-fqdn
- https://docs.docker.com/engine/install/ubuntu/
- https://caddyserver.com/docs/automatic-https

## 2. Cài và cấu hình trên VM

Cài Docker Engine và Compose plugin theo hướng dẫn Ubuntu chính thức ở trên.
Các lệnh sau chạy bằng Bash trên VM, tại thư mục repo. Nếu tài khoản chưa có
quyền Docker, dùng `sudo docker` thay cho `docker`.

Chuyển source đã kiểm tra lên VM bằng Git hoặc SCP; không chuyển `.env` local,
`expense.db`, `uploads`, `venv` hay `frontend/node_modules`. Không sao chép token
hoặc API key vào Git. Repo private cần quyền đọc phù hợp.

```bash
cp .env.example .env
chmod 600 .env
openssl rand -hex 32
openssl rand -hex 32
```

Dùng hai chuỗi ngẫu nhiên khác nhau cho `SECRET_KEY` và `POSTGRES_PASSWORD`.
Mật khẩu database dạng hex tránh ký tự đặc biệt làm hỏng DATABASE_URL.
Sửa `.env` bằng trình soạn thảo trên VM:

```dotenv
APP_ENV=production
AUTO_CREATE_SCHEMA=false
APP_DOMAIN=YOUR_ACTUAL_AZURE_FQDN
APP_BIND_ADDRESS=127.0.0.1
SECRET_KEY=YOUR_RANDOM_SECRET
POSTGRES_PASSWORD=YOUR_RANDOM_DATABASE_PASSWORD
```

APP_DOMAIN chỉ chứa hostname, không có `https://`, cổng hoặc dấu `/`.
Compose Azure tự đặt FRONTEND_URL và TRUSTED_HOSTS, cho phép healthcheck nội bộ.
Nếu cần AI và email khôi phục mật khẩu, điền AI_API_KEY, GEMINI_MODEL,
RESEND_API_KEY và RESEND_FROM_EMAIL hợp lệ. Các tích hợp này tính phí riêng;
credit Azure không thanh toán Gemini/Resend. Không có key thì chưa nghiệm thu
hai chức năng đó.

```bash
docker compose -f compose.yaml -f compose.azure.yaml config --quiet
docker compose -f compose.yaml -f compose.azure.yaml up -d --build
docker compose -f compose.yaml -f compose.azure.yaml ps
docker compose -f compose.yaml -f compose.azure.yaml logs --tail=100 web proxy
```

Lần khởi động đầu tự chạy Alembic trên database PostgreSQL mới. Không đưa SQLite
cũ vào quy trình này; chuyển dữ liệu cũ cần bước xuất/nhập riêng có backup.
Caddy tự cấp và gia hạn chứng chỉ khi DNS trỏ đúng và 80/443 truy cập được.
Database, uploads và chứng chỉ được giữ bằng named volumes. Không chạy
`docker compose down -v` trên hệ thống có dữ liệu cần giữ.

## Backup hằng ngày và retention 30 ngày

Các volume giúp dữ liệu tồn tại sau khi container khởi động lại nhưng không phải
là backup. Bộ script tại `scripts/backup/` tạo một restore point nhất quán gồm
PostgreSQL và avatar, mã hóa AES-256, kiểm tra checksum, hỗ trợ bản sao ngoài VM,
restore test và tự xóa restore point quá 30 ngày.

Tạo tệp mật khẩu riêng ngoài repository và giới hạn quyền đọc:

```bash
sudo install -d -m 700 /etc/expense-management-ai
openssl rand -base64 48 | sudo tee /etc/expense-management-ai/backup-password >/dev/null
sudo chmod 600 /etc/expense-management-ai/backup-password
sudo install -d -m 700 /var/backups/expense-management-ai
```

Ổ hoặc storage ngoài VM cần được mount tại một đường dẫn riêng, ví dụ
`/mnt/expense-backups`. Chạy backup từ thư mục gốc repository:

```bash
sudo env \
  BACKUP_ENCRYPTION_PASSWORD_FILE=/etc/expense-management-ai/backup-password \
  BACKUP_ROOT=/var/backups/expense-management-ai \
  OFFSITE_BACKUP_ROOT=/mnt/expense-backups \
  REQUIRE_OFFSITE_COPY=true \
  bash scripts/backup/backup.sh
```

Kiểm tra restore point và phục hồi thử vào database cô lập:

```bash
sudo env BACKUP_ENCRYPTION_PASSWORD_FILE=/etc/expense-management-ai/backup-password \
  bash scripts/backup/verify.sh /var/backups/expense-management-ai/RESTORE_POINT_ID
sudo env BACKUP_ENCRYPTION_PASSWORD_FILE=/etc/expense-management-ai/backup-password \
  bash scripts/backup/restore-test.sh /var/backups/expense-management-ai/RESTORE_POINT_ID
```

Xem trước retention mà không xóa, kể cả khi cần giả lập ngày demo:

```bash
sudo env BACKUP_RETENTION_DAYS=30 bash scripts/backup/prune.sh \
  --root /var/backups/expense-management-ai --dry-run
sudo env BACKUP_RETENTION_DAYS=30 bash scripts/backup/prune.sh \
  --root /var/backups/expense-management-ai --dry-run --now 2026-11-15T00:00:00Z
```

Sau khi chạy và restore test thủ công thành công, thêm cron chạy lúc ít người dùng:

```cron
0 2 * * * cd /opt/Expense-Management-Ai-Integration && BACKUP_ENCRYPTION_PASSWORD_FILE=/etc/expense-management-ai/backup-password BACKUP_ROOT=/var/backups/expense-management-ai OFFSITE_BACKUP_ROOT=/mnt/expense-backups REQUIRE_OFFSITE_COPY=true bash scripts/backup/backup.sh >> /var/log/expense-backup.log 2>&1
```

Không lưu mật khẩu mã hóa trong Git, manifest hoặc log. Mất tệp mật khẩu đồng
nghĩa không thể phục hồi backup. Chỉ coi job thành công khi có `BACKUP_OK`, bản
sao ngoài VM qua checksum và restore test định kỳ cho kết quả `RESTORE_TEST_OK`.

## 3. Kiểm tra trước khi mời người dùng

```bash
curl --fail https://YOUR_ACTUAL_AZURE_FQDN/api/health
curl --fail https://YOUR_ACTUAL_AZURE_FQDN/api/ready
```

- Mở trang bằng HTTPS, tải lại một đường dẫn trong app để kiểm tra React routing.
- Tạo hai tài khoản thử riêng; kiểm tra mỗi tài khoản chỉ thấy dữ liệu của mình.
- Thêm/sửa/xóa giao dịch, danh mục, ngân sách, mục tiêu và kiểm tra báo cáo.
- Upload avatar; khởi động lại container và xác nhận dữ liệu, avatar còn nguyên.
- Kiểm tra AI và email đặt lại mật khẩu nếu đã cấu hình dịch vụ.
- Thử trên điện thoại; kiểm tra đăng xuất và đăng nhập lại.
- Xem Cost Management sau khi số liệu sử dụng được cập nhật.

## 4. Sao lưu và cập nhật

Named volumes không phải backup. Trước mỗi lần cập nhật, tạm dừng web để database
và uploads nhất quán, rồi sao lưu bằng các lệnh sau. Nếu lệnh backup lỗi, kiểm tra
và khởi động lại web; không tiếp tục cập nhật cho tới khi có backup hợp lệ.

```bash
umask 077
mkdir -p backups
backup_stamp=$(date -u +%Y%m%dT%H%M%SZ)
docker compose -f compose.yaml -f compose.azure.yaml stop web
docker compose -f compose.yaml -f compose.azure.yaml exec -T db pg_dump -U expense -d expense -Fc > "backups/db-$backup_stamp.dump"
docker compose -f compose.yaml -f compose.azure.yaml run --rm --no-deps --entrypoint tar web -czf - -C /app uploads > "backups/uploads-$backup_stamp.tar.gz"
docker compose -f compose.yaml -f compose.azure.yaml start web
```

Sao chép backup ra nơi khác ngoài VM và bảo vệ quyền truy cập vì có dữ liệu cá
nhân. Lập lịch backup định kỳ trước khi dùng thật. Thử khôi phục trên môi trường
riêng: dùng `pg_restore -U expense -d expense` vào database trống và giải nén
uploads vào volume của môi trường thử, sau đó kiểm tra đăng nhập và dữ liệu.
Không khôi phục đè lên production để thử nghiệm.

Đưa phiên bản source đã kiểm tra lên VM, sau đó chạy lại `up -d --build` với cả
hai Compose files. Migration tự chạy lúc khởi động. Nếu migration không tương
thích ngược, quay lại image cũ có thể chưa đủ: cần kế hoạch khôi phục database.

## 5. Sau khi web ổn định

Điền URL thật vào `frontend/.env.desktop` theo mẫu có sẵn, build Tauri Windows
và kiểm tra tài khoản/dữ liệu dùng chung với web. Chưa phát hành installer trước
khi backend HTTPS và các luồng ở bước 3 được nghiệm thu.
