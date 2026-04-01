#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SERVER_DIR}/.env"
DRY_RUN=false

usage() {
  cat <<'EOF'
Pin docker images in telemetry_server/.env to immutable digests.

Usage:
  ./scripts/pin_images.sh [--dry-run]

Reads:
  TELEMETRY_IMAGE
  VICTORIAMETRICS_IMAGE

Writes:
  TELEMETRY_IMAGE=<repo>@sha256:...
  VICTORIAMETRICS_IMAGE=<repo>@sha256:...
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
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

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Create it from .env.production.example first." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but not installed." >&2
  exit 1
fi

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

current_telemetry="$(grep -E '^TELEMETRY_IMAGE=' "${ENV_FILE}" | cut -d= -f2- || true)"
current_vm="$(grep -E '^VICTORIAMETRICS_IMAGE=' "${ENV_FILE}" | cut -d= -f2- || true)"

if [[ -z "${current_telemetry}" || -z "${current_vm}" ]]; then
  echo "Both TELEMETRY_IMAGE and VICTORIAMETRICS_IMAGE must be set in ${ENV_FILE}." >&2
  exit 1
fi

resolve_digest_ref() {
  local image_ref="$1"
  docker pull "${image_ref}" >/dev/null
  local digest_ref
  digest_ref="$(docker image inspect --format '{{index .RepoDigests 0}}' "${image_ref}")"
  if [[ -z "${digest_ref}" ]]; then
    echo "Unable to resolve digest for ${image_ref}" >&2
    exit 1
  fi
  echo "${digest_ref}"
}

new_telemetry="$(resolve_digest_ref "${current_telemetry}")"
new_vm="$(resolve_digest_ref "${current_vm}")"

echo "Resolved:"
echo "  TELEMETRY_IMAGE=${new_telemetry}"
echo "  VICTORIAMETRICS_IMAGE=${new_vm}"

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "[DRY-RUN] No file changes applied."
  exit 0
fi

backup="${ENV_FILE}.backup-image-pin-$(date +%Y%m%d-%H%M%S)"
cp "${ENV_FILE}" "${backup}"
chmod 600 "${ENV_FILE}" "${backup}"

set_kv "${ENV_FILE}" "TELEMETRY_IMAGE" "${new_telemetry}"
set_kv "${ENV_FILE}" "VICTORIAMETRICS_IMAGE" "${new_vm}"
chmod 600 "${ENV_FILE}"

echo "Pinned image references written to ${ENV_FILE}"
echo "Backup written to: ${backup}"
