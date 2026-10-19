#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

root="${BACKUP_ROOT}"
dry_run=false
now="$(date -u +%s)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) root="$2"; shift 2 ;;
    --dry-run) dry_run=true; shift ;;
    --now) now="$(date -u -d "$2" +%s)"; shift 2 ;;
    *) echo "Tham số không hợp lệ: $1" >&2; exit 2 ;;
  esac
done

validate_backup_root "${root}"
[[ -d "${root}" ]] || { echo "Không có thư mục backup: ${root}"; exit 0; }
cutoff="$((now - BACKUP_RETENTION_DAYS * 86400))"

while IFS= read -r -d '' candidate; do
  name="$(basename -- "${candidate}")"
  [[ "${name}" =~ ^[0-9]{8}T[0-9]{6}Z$ ]] || continue
  created="$(date -u -d "${name:0:4}-${name:4:2}-${name:6:2} ${name:9:2}:${name:11:2}:${name:13:2} UTC" +%s)"
  if (( created < cutoff )); then
    if [[ "${dry_run}" == "true" ]]; then
      echo "WOULD_DELETE restore_point=${name}"
    else
      rm -rf -- "${candidate}"
      echo "DELETED restore_point=${name}"
    fi
  fi
done < <(find "${root}" -mindepth 1 -maxdepth 1 -type d -print0)
