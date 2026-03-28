#!/usr/bin/env bash
# Installer: writes /usr/local/bin/telemetry and makes it executable.
# Run as root or via sudo.
set -euo pipefail

sudo tee /usr/local/bin/telemetry >/dev/null <<'EOF'
#!/usr/bin/env bash
# telemetry – wrapper for idm-metrics-collector docker compose stack
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
REPO_DIR="/home/idm-metrics-collector"
COMPOSE_DIR="/home/idm-metrics-collector/telemetry_server"
SYSTEMD_SERVICE="telemetry.service"

# ── Colours (disabled when not a terminal) ───────────────────────────────────
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BLUE='\033[0;34m'; RESET='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BLUE=''; RESET=''
fi

log()  { echo -e "${CYAN}==>${RESET} $*"; }
ok()   { echo -e "${GREEN}✅${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠️ ${RESET} $*" >&2; }
die()  { echo -e "${RED}❌${RESET} $*" >&2; exit 1; }

need_cmds() {
  local missing=()
  for cmd in git docker; do
    command -v "$cmd" &>/dev/null || missing+=("$cmd")
  done
  [[ ${#missing[@]} -eq 0 ]] || die "Required commands not found: ${missing[*]}"
}

need_dirs() {
  [[ -d "$REPO_DIR" ]]    || die "Repo dir not found: $REPO_DIR"
  [[ -d "$COMPOSE_DIR" ]] || die "Compose dir not found: $COMPOSE_DIR"
}

compose() { docker compose "$@"; }

usage() {
  cat <<USAGE
Usage: telemetry <command>

Commands:
  update      git pull + compose down/pull/up -d
  start       compose up -d
  stop        compose down
  restart     compose down + up -d
  status      compose ps
  logs        compose logs -f --tail=200
  install     systemd-Service einrichten (als root)
  reinstall   dieses Script von GitHub neu installieren
  help        diese Hilfe anzeigen
USAGE
}

cmd_update() {
  need_cmds; need_dirs
  cd "$REPO_DIR"
  git config core.autocrlf input
  git checkout main 2>/dev/null || true
  log "git fetch origin"
  git fetch origin
  log "git reset --hard origin/main"
  git reset --hard origin/main
  git clean -fd --quiet 2>/dev/null || true
  cd "$COMPOSE_DIR"
  log "docker compose down"
  compose down
  log "docker compose pull"
  compose pull
  log "docker compose up -d"
  compose up -d
  ok "Telemetry aktualisiert & gestartet."
}

cmd_start() {
  need_cmds; need_dirs
  cd "$COMPOSE_DIR"
  log "docker compose up -d"
  compose up -d
  ok "Telemetry gestartet."
}

cmd_stop() {
  need_cmds; need_dirs
  cd "$COMPOSE_DIR"
  log "docker compose down"
  compose down
  ok "Telemetry gestoppt."
}

cmd_restart() {
  need_cmds; need_dirs
  cd "$COMPOSE_DIR"
  log "docker compose down"
  compose down
  log "docker compose up -d"
  compose up -d
  ok "Telemetry neugestartet."
}

cmd_status() {
  need_cmds; need_dirs
  cd "$COMPOSE_DIR"
  compose ps
}

cmd_logs() {
  need_cmds; need_dirs
  cd "$COMPOSE_DIR"
  compose logs -f --tail=200 || true
}

cmd_install() {
  [[ $EUID -eq 0 ]] || die "install muss als root ausgeführt werden."
  local service_file="/etc/systemd/system/${SYSTEMD_SERVICE}"
  log "Erstelle systemd-Service: $service_file"
  cat > "$service_file" <<SERVICE
[Unit]
Description=IDM Metrics Collector (Telemetry Stack)
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/telemetry start
ExecStop=/usr/local/bin/telemetry stop
WorkingDirectory=${COMPOSE_DIR}

[Install]
WantedBy=multi-user.target
SERVICE
  systemctl daemon-reload
  systemctl enable "$SYSTEMD_SERVICE"
  ok "systemd-Service installiert & aktiviert."
  log "Starten mit: systemctl start telemetry"
  log "Status:      systemctl status telemetry"
}

cmd_reinstall() {
  log "Lade Installer von GitHub..."
  command -v curl &>/dev/null || die "curl nicht gefunden: apt install curl"
  if [[ $EUID -ne 0 ]]; then
    curl -fsSL https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/telemetry_server/telemetry_update.sh | sudo bash
  else
    curl -fsSL https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/telemetry_server/telemetry_update.sh | bash
  fi
}

# ── Dispatch ──────────────────────────────────────────────────────────────────
case "${1:-help}" in
  update)         cmd_update    ;;
  start)          cmd_start     ;;
  stop)           cmd_stop      ;;
  restart)        cmd_restart   ;;
  status)         cmd_status    ;;
  logs)           cmd_logs      ;;
  install)        cmd_install   ;;
  reinstall)      cmd_reinstall ;;
  help|--help|-h) usage         ;;
  *)
    warn "Unbekannter Befehl: '${1}'"
    usage
    exit 1
    ;;
esac
EOF

sudo chmod +x /usr/local/bin/telemetry
echo "✅ /usr/local/bin/telemetry installiert."
