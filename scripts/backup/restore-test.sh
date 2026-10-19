#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

if [[ $# -ne 1 ]]; then
  echo "Cách dùng: $0 RESTORE_POINT_DIRECTORY" >&2
  exit 2
fi

require_command docker
require_command openssl
require_command tar
require_password_file

restore_dir="$(cd -- "$1" && pwd)"
bash "${SCRIPT_DIR}/verify.sh" "${restore_dir}"
test_db="restore_verify_$(date -u +%H%M%S)_$$"
temp_dir="$(mktemp -d)"

cleanup() {
  compose exec -T db dropdb --if-exists -U "${POSTGRES_USER}" "${test_db}" >/dev/null 2>&1 || true
  rm -rf -- "${temp_dir}"
}
trap cleanup EXIT

openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -pass "file:${BACKUP_ENCRYPTION_PASSWORD_FILE}" \
  -in "${restore_dir}/database.dump.enc" -out "${temp_dir}/database.dump"
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -pass "file:${BACKUP_ENCRYPTION_PASSWORD_FILE}" \
  -in "${restore_dir}/uploads.tar.gz.enc" -out "${temp_dir}/uploads.tar.gz"

tar -tzf "${temp_dir}/uploads.tar.gz" >/dev/null
compose exec -T db createdb -U "${POSTGRES_USER}" "${test_db}"
compose exec -T db pg_restore -U "${POSTGRES_USER}" -d "${test_db}" --no-owner --no-privileges \
  < "${temp_dir}/database.dump"
table_count="$(compose exec -T db psql -U "${POSTGRES_USER}" -d "${test_db}" -Atc \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")"

if [[ ! "${table_count}" =~ ^[1-9][0-9]*$ ]]; then
  echo "Restore test không tìm thấy bảng ứng dụng." >&2
  exit 1
fi

echo "RESTORE_TEST_OK restore_point=$(basename -- "${restore_dir}") tables=${table_count}"
