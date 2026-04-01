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
SCRIPTS_DIR="/home/idm-metrics-collector/telemetry_server/scripts"
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
  [[ -d "$SCRIPTS_DIR" ]] || die "Scripts dir not found: $SCRIPTS_DIR"
}

require_script() {
  local script="$1"
  [[ -x "${SCRIPTS_DIR}/${script}" ]] || die "Script missing or not executable: ${SCRIPTS_DIR}/${script}"
}

compose() { docker compose "$@"; }

usage() {
  cat <<USAGE
Usage: telemetry <command>

Commands:
  menu        interaktives Menü öffnen
  update      sicheres Update (git pull --rebase --autostash + compose up -d)
  update-force hartes Update (git reset --hard origin/main + clean)
  start       compose up -d
  stop        compose down
  restart     compose down + up -d
  status      compose ps
  logs        compose logs -f --tail=200
  pin-images  TELEMETRY_IMAGE/VICTORIAMETRICS_IMAGE auf Digest pinnen
  rotate-secrets  AUTH/ADMIN/Encryption-Secret rotieren (siehe --help im Script)
  verify-backup   Backup-Artefakte prüfen (setzt --backup-dir voraus)
  harden      sicheres Basis-Hardening (pin-images + restart + Hinweise)
  install     systemd-Service einrichten (als root)
  reinstall   dieses Script von GitHub neu installieren
  help        diese Hilfe anzeigen
USAGE
}

ensure_whiptail() {
  if command -v whiptail >/dev/null 2>&1; then
    return 0
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    warn "whiptail fehlt und apt-get ist nicht verfügbar. Nutze Text-Menü-Fallback."
    return 1
  fi

  log "whiptail nicht gefunden. Installiere Paket..."
  if [[ $EUID -eq 0 ]]; then
    apt-get update && apt-get install -y whiptail
  elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y whiptail
  else
    warn "sudo nicht verfügbar. Nutze Text-Menü-Fallback."
    return 1
  fi

  if command -v whiptail >/dev/null 2>&1; then
    ok "whiptail installiert."
    return 0
  fi

  warn "whiptail Installation fehlgeschlagen. Nutze Text-Menü-Fallback."
  return 1
}

run_menu() {
  local choice=""

  if ensure_whiptail && [[ -t 1 ]]; then
    choice="$(whiptail --title "Telemetry Control" --menu "Aktion wählen" 22 78 12 \
      "status" "[SAFE] Container-Status anzeigen" \
      "start" "[SAFE] Stack starten" \
      "stop" "[RISK] Stack stoppen" \
      "restart" "[RISK] Stack neu starten" \
      "update" "[RISK] Repo + Images sicher aktualisieren" \
      "update-force" "[HIGH] Repo hart zurücksetzen + aktualisieren" \
      "logs" "[SAFE] Logs folgen" \
      "pin-images" "[SAFE] Images auf Digests pinnen" \
      "rotate-secrets" "[HIGH] Secrets rotieren" \
      "verify-backup" "[SAFE] Backup verifizieren" \
      "harden" "[SAFE] Basis-Hardening ausführen" \
      "help" "[SAFE] Hilfe anzeigen" \
      3>&1 1>&2 2>&3)" || return 0
  else
    echo
    echo -e "${BLUE}Telemetry Menü${RESET}"
    echo -e "1) ${GREEN}status${RESET} [SAFE]"
    echo -e "2) ${GREEN}start${RESET} [SAFE]"
    echo -e "3) ${YELLOW}stop${RESET} [RISK]"
    echo -e "4) ${YELLOW}restart${RESET} [RISK]"
    echo -e "5) ${YELLOW}update${RESET} [RISK]"
    echo -e "6) ${RED}update-force${RESET} [HIGH]"
    echo -e "7) ${GREEN}logs${RESET} [SAFE]"
    echo -e "8) ${GREEN}pin-images${RESET} [SAFE]"
    echo -e "9) ${RED}rotate-secrets${RESET} [HIGH]"
    echo -e "10) ${GREEN}verify-backup${RESET} [SAFE]"
    echo -e "11) ${GREEN}harden${RESET} [SAFE]"
    echo -e "12) ${GREEN}help${RESET} [SAFE]"
    read -r -p "Auswahl [1-12, Enter=abbrechen]: " sel
    case "${sel:-}" in
      1) choice="status" ;;
      2) choice="start" ;;
      3) choice="stop" ;;
      4) choice="restart" ;;
      5) choice="update" ;;
      6) choice="update-force" ;;
      7) choice="logs" ;;
      8) choice="pin-images" ;;
      9) choice="rotate-secrets" ;;
      10) choice="verify-backup" ;;
      11) choice="harden" ;;
      12) choice="help" ;;
      *) return 0 ;;
    esac
  fi

  case "$choice" in
    update)         cmd_update ;;
    update-force)
      confirm_action "HIGH-RISK: Repo wirklich hart zurücksetzen?" || return 0
      cmd_update_force
      ;;
    start)          cmd_start ;;
    stop)           cmd_stop ;;
    restart)        cmd_restart ;;
    status)         cmd_status ;;
    logs)           cmd_logs ;;
    pin-images)     cmd_pin_images ;;
    rotate-secrets)
      confirm_action "HIGH-RISK: Secrets wirklich rotieren?" || return 0
      echo "Beispiel: --all --restart (leer = Standard)"
      read -r -p "Argumente für rotate-secrets: " args
      # shellcheck disable=SC2086
      cmd_rotate_secrets --yes $args
      ;;
    verify-backup)
      read -r -p "Backup-Verzeichnis (Pflicht): " backup_dir
      [[ -n "${backup_dir}" ]] || die "Backup-Verzeichnis ist erforderlich."
      cmd_verify_backup --backup-dir "${backup_dir}"
      ;;
    harden)         cmd_harden ;;
    help)           usage ;;
  esac
}

confirm_action() {
  local prompt="$1"
  if command -v whiptail >/dev/null 2>&1 && [[ -t 1 ]]; then
    if whiptail --title "Sicherheitsabfrage" --yesno "$prompt" 10 70; then
      return 0
    fi
    return 1
  fi

  if [[ -t 0 && -t 1 ]]; then
    local answer=""
    read -r -p "${prompt} [yes/NO]: " answer
    [[ "${answer}" == "yes" ]]
    return
  fi

  return 1
}

SELF_UPDATE_URL="https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/telemetry_server/telemetry_update.sh"

_self_update() {
  if [[ "${_TELEMETRY_SELF_UPDATED:-}" == "1" ]]; then return; fi
  log "Prüfe auf Script-Update..."
  local tmp
  tmp=$(mktemp) || return
  if curl -fsSL "$SELF_UPDATE_URL" -o "$tmp" 2>/dev/null; then
    bash "$tmp"
    rm -f "$tmp"
    export _TELEMETRY_SELF_UPDATED=1
    exec /usr/local/bin/telemetry update
  fi
  rm -f "$tmp"
}

cmd_update() {
  _self_update
  need_cmds; need_dirs
  cd "$REPO_DIR"
  git config core.autocrlf input
  log "git fetch origin"
  git fetch origin
  log "git pull --rebase --autostash origin main"
  git pull --rebase --autostash origin main
  cd "$COMPOSE_DIR"
  log "docker compose pull"
  compose pull
  log "docker compose up -d"
  compose up -d
  ok "Telemetry sicher aktualisiert & gestartet."
}

cmd_update_force() {
  _self_update
  need_cmds; need_dirs
  confirm_action "RISK: Wirklich lokales Repo verwerfen (reset --hard + clean)?" || die "Abgebrochen."
  cd "$REPO_DIR"
  git config core.autocrlf input
  git checkout main 2>/dev/null || true
  log "git fetch origin"
  git fetch origin
  log "git reset --hard origin/main"
  git reset --hard origin/main
  log "git clean -fd"
  git clean -fd
  cd "$COMPOSE_DIR"
  log "docker compose pull"
  compose pull
  log "docker compose up -d"
  compose up -d
  ok "Telemetry hart aktualisiert & gestartet."
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

cmd_pin_images() {
  need_cmds; need_dirs
  require_script "pin_images.sh"
  cd "$COMPOSE_DIR"
  log "Pinne Container-Images auf Digests..."
  "${SCRIPTS_DIR}/pin_images.sh"
  ok "Images gepinnt. Starte Stack neu..."
  compose --env-file .env up -d
  ok "Pinning abgeschlossen."
}

cmd_rotate_secrets() {
  need_cmds; need_dirs
  require_script "rotate_secrets.sh"
  cd "$COMPOSE_DIR"
  if [[ "${1:-}" == "--yes" ]]; then
    shift
  elif ! confirm_action "HIGH-RISK: Secrets wirklich rotieren?"; then
    die "Abgebrochen. Für Non-Interactive nutze: telemetry rotate-secrets --yes <args>"
  fi
  log "Starte Secret-Rotation..."
  "${SCRIPTS_DIR}/rotate_secrets.sh" "$@"
}

cmd_verify_backup() {
  need_cmds; need_dirs
  require_script "verify_backup_restore.sh"
  cd "$COMPOSE_DIR"
  "${SCRIPTS_DIR}/verify_backup_restore.sh" "$@"
}

cmd_harden() {
  need_cmds; need_dirs
  require_script "pin_images.sh"
  cd "$COMPOSE_DIR"
  [[ -f .env ]] || die "Missing ${COMPOSE_DIR}/.env. Create it first."
  log "Hardening: pin-images + compose restart"
  "${SCRIPTS_DIR}/pin_images.sh"
  compose --env-file .env up -d
  ok "Basis-Hardening abgeschlossen."
  warn "Token-Rotation wird NICHT automatisch ausgeführt."
  warn "Wenn gewünscht: telemetry rotate-secrets --all --restart"
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
  menu)           run_menu ;;
  update)         cmd_update    ;;
  update-force)   cmd_update_force ;;
  start)          cmd_start     ;;
  stop)           cmd_stop      ;;
  restart)        cmd_restart   ;;
  status)         cmd_status    ;;
  logs)           cmd_logs      ;;
  pin-images)     cmd_pin_images ;;
  rotate-secrets) shift; cmd_rotate_secrets "$@" ;;
  verify-backup)  shift; cmd_verify_backup "$@" ;;
  harden)         cmd_harden ;;
  install)        cmd_install   ;;
  reinstall)      cmd_reinstall ;;
  help|--help|-h) usage         ;;
  "")
    if [[ -t 0 && -t 1 ]]; then
      run_menu
    else
      usage
    fi
    ;;
  *)
    warn "Unbekannter Befehl: '${1}'"
    usage
    exit 1
    ;;
esac
EOF

sudo chmod +x /usr/local/bin/telemetry
echo "✅ /usr/local/bin/telemetry installiert."
