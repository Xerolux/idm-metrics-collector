#!/usr/bin/env bash
# Installer: writes /usr/local/bin/telemetry and makes it executable.
# Run as root or via sudo.
set -euo pipefail

sudo tee /usr/local/bin/telemetry >/dev/null <<'EOF'
#!/usr/bin/env bash
# telemetry – lädt immer die aktuelle Version von GitHub und führt sie aus.
set -euo pipefail

SELF_URL="https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/telemetry_server/telemetry_update.sh"

# ── Colours ───────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BLUE='\033[0;34m'; RESET='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BLUE=''; RESET=''
fi

info() { echo -e "${BLUE}ℹ️ ${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠️ ${RESET} $*" >&2; }
die()  { echo -e "${RED}❌${RESET} $*" >&2; exit 1; }

# curl verfügbar?
command -v curl &>/dev/null || die "curl nicht gefunden – bitte installieren: apt install curl"

# Installer von GitHub laden
tmp=$(mktemp /tmp/telemetry_remote.XXXXXX)
trap "rm -f '$tmp'" EXIT

if ! curl -fsSL --connect-timeout 10 --max-time 30 "$SELF_URL" -o "$tmp" 2>/dev/null; then
  die "GitHub nicht erreichbar – kein Internetzugang oder URL ungültig."
fi

# Inneres Script (zwischen <<'EOF' und ^EOF$) extrahieren
tmp_inner=$(mktemp /tmp/telemetry_inner.XXXXXX)
trap "rm -f '$tmp' '$tmp_inner'" EXIT

awk "/^'EOF'\$/{found=1;next} /^EOF\$/{exit} found{print}" "$tmp" > "$tmp_inner"

if [[ ! -s "$tmp_inner" ]]; then
  die "Extraktion des Scripts fehlgeschlagen – Installer-Format unerwartet."
fi

chmod +x "$tmp_inner"

# Aktuelles Script von GitHub direkt ausführen
export TELEMETRY_NO_SELFUPDATE=1
exec bash "$tmp_inner" "$@"
EOF

sudo chmod +x /usr/local/bin/telemetry
echo "✅ /usr/local/bin/telemetry installiert."
