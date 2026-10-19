#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

require_command docker
require_command openssl
require_command sha256sum
require_command tar
require_password_file
validate_backup_root "${BACKUP_ROOT}"

restore_id="$(date -u +%Y%m%dT%H%M%SZ)"
created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
expires_at="$(date -u -d "+${BACKUP_RETENTION_DAYS} days" +%Y-%m-%dT%H:%M:%SZ)"
partial_dir="${BACKUP_ROOT}/.partial-${restore_id}"
final_dir="${BACKUP_ROOT}/${restore_id}"
web_was_running=false
backup_complete=false

cleanup() {
  local exit_code=$?
  if [[ "${web_was_running}" == "true" ]]; then
    compose start web >/dev/null || echo "CẢNH BÁO: không thể khởi động lại web; cần xử lý ngay." >&2
  fi
  if [[ "${backup_complete}" != "true" && -d "${partial_dir}" ]]; then
    rm -rf -- "${partial_dir}"
  fi
  exit "${exit_code}"
}
trap cleanup EXIT

mkdir -p -- "${BACKUP_ROOT}"
if [[ -e "${final_dir}" || -e "${partial_dir}" ]]; then
  echo "Restore point ${restore_id} đã tồn tại." >&2
  exit 1
fi
mkdir -- "${partial_dir}"

if compose ps --status running --services | grep -qx web; then
  web_was_running=true
  echo "Tạm dừng web để tạo restore point nhất quán..."
  compose stop web >/dev/null
fi

echo "Đang backup PostgreSQL..."
compose exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc \
  | openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 \
      -pass "file:${BACKUP_ENCRYPTION_PASSWORD_FILE}" \
      -out "${partial_dir}/database.dump.enc"

echo "Đang backup avatar..."
compose run --rm --no-deps --entrypoint tar web -czf - -C /app uploads \
  | openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 \
      -pass "file:${BACKUP_ENCRYPTION_PASSWORD_FILE}" \
      -out "${partial_dir}/uploads.tar.gz.enc"

if [[ "${web_was_running}" == "true" ]]; then
  compose start web >/dev/null
  web_was_running=false
  echo "Web đã được khởi động lại sau khi chụp restore point."
fi

(
  cd -- "${partial_dir}"
  sha256sum database.dump.enc uploads.tar.gz.enc > checksums.sha256
)

cat > "${partial_dir}/manifest.json" <<EOF
{
  "restore_point_id": "${restore_id}",
  "created_at_utc": "${created_at}",
  "expires_at_utc": "${expires_at}",
  "retention_days": ${BACKUP_RETENTION_DAYS},
  "database": "${POSTGRES_DB}",
  "database_file": "database.dump.enc",
  "uploads_file": "uploads.tar.gz.enc",
  "encryption": "AES-256-CBC/PBKDF2",
  "status": "verified"
}
EOF

bash "${SCRIPT_DIR}/verify.sh" "${partial_dir}"
mv -- "${partial_dir}" "${final_dir}"
backup_complete=true

if [[ -n "${OFFSITE_BACKUP_ROOT:-}" ]]; then
  validate_backup_root "${OFFSITE_BACKUP_ROOT}"
  mkdir -p -- "${OFFSITE_BACKUP_ROOT}"
  cp -a -- "${final_dir}" "${OFFSITE_BACKUP_ROOT}/"
  bash "${SCRIPT_DIR}/verify.sh" "${OFFSITE_BACKUP_ROOT}/${restore_id}"
  echo "Đã xác minh bản sao ngoài VM tại ${OFFSITE_BACKUP_ROOT}/${restore_id}."
elif [[ "${REQUIRE_OFFSITE_COPY:-false}" == "true" ]]; then
  echo "Backup cục bộ đã tạo nhưng thiếu OFFSITE_BACKUP_ROOT bắt buộc." >&2
  exit 1
else
  echo "CẢNH BÁO: chưa cấu hình OFFSITE_BACKUP_ROOT; restore point hiện vẫn nằm trên VM." >&2
fi

bash "${SCRIPT_DIR}/prune.sh" --root "${BACKUP_ROOT}"
if [[ -n "${OFFSITE_BACKUP_ROOT:-}" ]]; then
  bash "${SCRIPT_DIR}/prune.sh" --root "${OFFSITE_BACKUP_ROOT}"
fi

echo "BACKUP_OK restore_point=${restore_id} created=${created_at} expires=${expires_at}"
