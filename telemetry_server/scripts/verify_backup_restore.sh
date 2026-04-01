#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=""
REQUIRE_ENV=true
REQUIRE_VM=true
REQUIRE_MODELS=true

usage() {
  cat <<'EOF'
Verify telemetry backup artifacts and restore-readability.

Usage:
  ./scripts/verify_backup_restore.sh --backup-dir <path>

Expected files in backup dir:
  .env
  vmdata.tar.gz
  model-data.tar.gz

Checks:
  1) file exists and is non-empty
  2) tar archive integrity (tar -tzf)
  3) extraction sanity-check to temp dir
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup-dir)
      BACKUP_DIR="$2"
      shift
      ;;
    --skip-env)
      REQUIRE_ENV=false
      ;;
    --skip-vmdata)
      REQUIRE_VM=false
      ;;
    --skip-model-data)
      REQUIRE_MODELS=false
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ -z "${BACKUP_DIR}" ]]; then
  echo "--backup-dir is required" >&2
  usage
  exit 1
fi

if [[ ! -d "${BACKUP_DIR}" ]]; then
  echo "Backup directory does not exist: ${BACKUP_DIR}" >&2
  exit 1
fi

check_file() {
  local path="$1"
  if [[ ! -s "${path}" ]]; then
    echo "Missing or empty: ${path}" >&2
    exit 1
  fi
}

verify_tar() {
  local archive="$1"
  local temp_dir
  check_file "${archive}"
  tar -tzf "${archive}" >/dev/null
  temp_dir="$(mktemp -d)"
  trap 'rm -rf "${temp_dir}"' RETURN
  tar -xzf "${archive}" -C "${temp_dir}"
  if [[ -z "$(find "${temp_dir}" -mindepth 1 -print -quit)" ]]; then
    echo "Archive extracted but appears empty: ${archive}" >&2
    exit 1
  fi
  rm -rf "${temp_dir}"
  trap - RETURN
}

if [[ "${REQUIRE_ENV}" == "true" ]]; then
  check_file "${BACKUP_DIR}/.env"
  grep -q '^AUTH_TOKEN=' "${BACKUP_DIR}/.env" || {
    echo "Backup .env does not contain AUTH_TOKEN=" >&2
    exit 1
  }
fi

if [[ "${REQUIRE_VM}" == "true" ]]; then
  verify_tar "${BACKUP_DIR}/vmdata.tar.gz"
fi

if [[ "${REQUIRE_MODELS}" == "true" ]]; then
  verify_tar "${BACKUP_DIR}/model-data.tar.gz"
fi

echo "Backup verification successful for: ${BACKUP_DIR}"
