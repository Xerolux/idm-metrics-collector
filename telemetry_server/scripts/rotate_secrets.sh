#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SERVER_DIR}/.env"

ROTATE_AUTH=false
ROTATE_ADMIN=false
ROTATE_ENCRYPTION=false
RESTART_STACK=false
DRY_RUN=false

usage() {
  cat <<'EOF'
Rotate telemetry server secrets inside telemetry_server/.env

Usage:
  ./scripts/rotate_secrets.sh [options]

Options:
  --auth           Rotate AUTH_TOKEN
  --admin          Rotate ADMIN_AUTH_TOKEN
  --encryption     Rotate TELEMETRY_ENCRYPTION_KEY
  --all            Rotate all three secrets (default when no rotate option is set)
  --restart        Restart stack after update (docker compose up -d)
  --dry-run        Print generated values but do not write .env
  -h, --help       Show help
EOF
}

has_rotate_selection=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --auth)
      ROTATE_AUTH=true
      has_rotate_selection=true
      ;;
    --admin)
      ROTATE_ADMIN=true
      has_rotate_selection=true
      ;;
    --encryption)
      ROTATE_ENCRYPTION=true
      has_rotate_selection=true
      ;;
    --all)
      ROTATE_AUTH=true
      ROTATE_ADMIN=true
      ROTATE_ENCRYPTION=true
      has_rotate_selection=true
      ;;
    --restart)
      RESTART_STACK=true
      ;;
    --dry-run)
      DRY_RUN=true
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

if [[ "${has_rotate_selection}" == "false" ]]; then
  ROTATE_AUTH=true
  ROTATE_ADMIN=true
  ROTATE_ENCRYPTION=true
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Create it from .env.production.example first." >&2
  exit 1
fi

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl is required but not installed." >&2
  exit 1
fi

gen_token() {
  openssl rand -base64 48 | tr -d '\n'
}

gen_enc_key() {
  openssl rand -base64 32 | tr -d '\n'
}

set_kv() {
  local file="$1"
  local key="$2"
  local value="$3"
  local tmp
  tmp="$(mktemp)"
  if grep -qE "^${key}=" "${file}"; then
    awk -v k="${key}" -v v="${value}" '
      BEGIN { FS=OFS="=" }
      $1 == k { $0 = k "=" v; found=1 }
      { print }
      END { if (!found) print k "=" v }
    ' "${file}" > "${tmp}"
  else
    cat "${file}" > "${tmp}"
    printf "\n%s=%s\n" "${key}" "${value}" >> "${tmp}"
  fi
  mv "${tmp}" "${file}"
}

NEW_AUTH=""
NEW_ADMIN=""
NEW_ENC=""

if [[ "${ROTATE_AUTH}" == "true" ]]; then
  NEW_AUTH="$(gen_token)"
fi
if [[ "${ROTATE_ADMIN}" == "true" ]]; then
  NEW_ADMIN="$(gen_token)"
fi
if [[ "${ROTATE_ENCRYPTION}" == "true" ]]; then
  NEW_ENC="$(gen_enc_key)"
fi

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "[DRY-RUN] Would rotate in ${ENV_FILE}:"
  [[ -n "${NEW_AUTH}" ]] && echo "AUTH_TOKEN=${NEW_AUTH}"
  [[ -n "${NEW_ADMIN}" ]] && echo "ADMIN_AUTH_TOKEN=${NEW_ADMIN}"
  [[ -n "${NEW_ENC}" ]] && echo "TELEMETRY_ENCRYPTION_KEY=${NEW_ENC}"
  echo "[DRY-RUN] No file changes applied."
  exit 0
fi

backup="${ENV_FILE}.backup-$(date +%Y%m%d-%H%M%S)"
cp "${ENV_FILE}" "${backup}"
chmod 600 "${ENV_FILE}" "${backup}"

[[ -n "${NEW_AUTH}" ]] && set_kv "${ENV_FILE}" "AUTH_TOKEN" "${NEW_AUTH}"
[[ -n "${NEW_ADMIN}" ]] && set_kv "${ENV_FILE}" "ADMIN_AUTH_TOKEN" "${NEW_ADMIN}"
[[ -n "${NEW_ENC}" ]] && set_kv "${ENV_FILE}" "TELEMETRY_ENCRYPTION_KEY" "${NEW_ENC}"

chmod 600 "${ENV_FILE}"

echo "Secrets rotated."
echo "Backup written to: ${backup}"
[[ -n "${NEW_AUTH}" ]] && echo "AUTH_TOKEN updated."
[[ -n "${NEW_ADMIN}" ]] && echo "ADMIN_AUTH_TOKEN updated."
[[ -n "${NEW_ENC}" ]] && echo "TELEMETRY_ENCRYPTION_KEY updated."

if [[ "${RESTART_STACK}" == "true" ]]; then
  (
    cd "${SERVER_DIR}"
    docker compose --env-file .env up -d
  )
  echo "Docker stack restarted."
fi

echo "Remember to update clients that still use global AUTH_TOKEN."
