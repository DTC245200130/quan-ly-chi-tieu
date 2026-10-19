#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILES=(-f "${PROJECT_ROOT}/compose.yaml" -f "${PROJECT_ROOT}/compose.azure.yaml")

BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/expense-management-ai}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
POSTGRES_USER="${POSTGRES_USER:-expense}"
POSTGRES_DB="${POSTGRES_DB:-expense}"

compose() {
  docker compose "${COMPOSE_FILES[@]}" "$@"
}
require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Thiếu lệnh bắt buộc: $1" >&2
    exit 1
  fi
}
validate_backup_root() {
  local root="$1"
  if [[ -z "${root}" || "${root}" == "/" ]]; then
    echo "BACKUP_ROOT không được để trống hoặc là thư mục gốc /." >&2
    exit 1
  fi
}

require_password_file() {
  if [[ -z "${BACKUP_ENCRYPTION_PASSWORD_FILE:-}" ]]; then
    echo "Phải đặt BACKUP_ENCRYPTION_PASSWORD_FILE tới tệp mật khẩu chỉ chủ sở hữu được đọc." >&2
    exit 1
  fi
  if [[ ! -f "${BACKUP_ENCRYPTION_PASSWORD_FILE}" || ! -s "${BACKUP_ENCRYPTION_PASSWORD_FILE}" ]]; then
    echo "Tệp mật khẩu backup không tồn tại hoặc đang trống." >&2
    exit 1
  fi
}
