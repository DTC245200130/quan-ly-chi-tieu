#!/usr/bin/env bash

set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
  echo "Cách dùng: $0 RESTORE_POINT_DIRECTORY" >&2
  exit 2
fi

restore_dir="$(cd -- "$1" && pwd)"
for required in manifest.json checksums.sha256 database.dump.enc uploads.tar.gz.enc; do
  if [[ ! -s "${restore_dir}/${required}" ]]; then
    echo "Restore point thiếu hoặc rỗng: ${required}" >&2
    exit 1
  fi
done

(
  cd -- "${restore_dir}"
  sha256sum --check --strict checksums.sha256
)
echo "VERIFY_OK restore_point=$(basename -- "${restore_dir}")"
