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
SELF="/usr/local/bin/telemetry"
SELF_URL="https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/telemetry_server/telemetry_update.sh"
SYSTEMD_SERVICE="telemetry.service"

# ── Colours (disabled when not a terminal) ───────────────────────────────────
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BLUE='\033[0;34m'; RESET='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BLUE=''; RESET=''
fi

# ── Helpers ───────────────────────────────────────────────────────────────────
log()  { echo -e "${CYAN}==>${RESET} $*"; }
ok()   { echo -e "${GREEN}✅${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠️ ${RESET} $*" >&2; }
die()  { echo -e "${RED}❌${RESET} $*" >&2; exit 1; }
info() { echo -e "${BLUE}ℹ️ ${RESET} $*"; }

need_cmds() {
  local missing=()
  for cmd in git docker curl sha256sum; do
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
  update      git pull (stash/pop bei lokalen Änderungen) + compose down/pull/up -d
  start       compose up -d
  stop        compose down
  restart     compose down + up -d  (kein Image-Pull)
  status      compose ps
  logs        compose logs -f --tail=200
  self-update Script manuell von GitHub aktualisieren
  install     systemd-Service einrichten (einmalig als root)
  help        diese Hilfe anzeigen

Hinweis: Bei jedem Aufruf wird automatisch geprüft ob dieses
Script auf GitHub aktualisiert wurde und ggf. selbst aktualisiert.
USAGE
}

# ── Self-Update ───────────────────────────────────────────────────────────────
# Vergleicht den SHA256 des installierten Scripts mit dem inneren Script
# (Heredoc-Inhalt) aus dem Installer auf GitHub. Nur bei Abweichung wird
# aktualisiert. Loop-Schutz via TELEMETRY_NO_SELFUPDATE=1.
cmd_self_update() {
  local silent="${1:-}"

  # Loop-Schutz: gesetzt von exec nach erfolgreichem Update
  [[ "${TELEMETRY_NO_SELFUPDATE:-}" == "1" ]] && return 0

  # curl verfügbar?
  command -v curl &>/dev/null || {
    [[ "$silent" == "silent" ]] || warn "curl nicht gefunden – Self-Update übersprungen."
    return 0
  }

  local tmp tmp_inner
  tmp=$(mktemp /tmp/telemetry_installer.XXXXXX)
  tmp_inner=$(mktemp /tmp/telemetry_inner.XXXXXX)
  trap "rm -f '$tmp' '$tmp_inner'" RETURN

  # Installer-Script von GitHub laden
  if ! curl -fsSL --connect-timeout 10 --max-time 30 "$SELF_URL" -o "$tmp" 2>/dev/null; then
    [[ "$silent" == "silent" ]] || warn "Self-Update: GitHub nicht erreichbar – übersprungen."
    return 0
  fi

  # Inneres Script aus dem Installer-Heredoc extrahieren
  # Alles zwischen "<<'EOF'" und abschließendem "^EOF$" am Zeilenende
  awk "/^sudo tee/,0 { next }
       /^'?EOF'?\$/ { found=!found; next }
       found { print }" "$tmp" > "$tmp_inner" 2>/dev/null || true

  # Fallback: ganzes Installer-Script vergleichen wenn Extraktion leer
  if [[ ! -s "$tmp_inner" ]]; then
    cp "$tmp" "$tmp_inner"
  fi

  local hash_local hash_remote
  hash_local=$(sha256sum "$SELF"       | awk '{print $1}')
  hash_remote=$(sha256sum "$tmp_inner" | awk '{print $1}')

  if [[ "$hash_local" == "$hash_remote" ]]; then
    [[ "$silent" == "silent" ]] || ok "Script ist bereits aktuell."
    return 0
  fi

  info "Neue Script-Version gefunden – aktualisiere $SELF ..."

  if [[ $EUID -ne 0 ]]; then
    if ! sudo install -m 0755 "$tmp_inner" "$SELF"; then
      warn "Self-Update fehlgeschlagen (kein sudo?). Manuell: sudo telemetry self-update"
      return 0
    fi
  else
    install -m 0755 "$tmp_inner" "$SELF"
  fi

  ok "Script aktualisiert."

  # systemd informieren falls Service aktiv
  if command -v systemctl &>/dev/null && systemctl is-active --quiet "$SYSTEMD_SERVICE" 2>/dev/null; then
    info "Lade systemd-Service neu..."
    if [[ $EUID -eq 0 ]]; then
      systemctl daemon-reload
    else
      sudo systemctl daemon-reload 2>/dev/null || true
    fi
    ok "systemd daemon-reload abgeschlossen."
  fi

  # Ursprünglichen Befehl mit neuem Script neu ausführen – kein Loop da
  # TELEMETRY_NO_SELFUPDATE=1 exportiert wird und vererbt bleibt
  info "Starte neu mit aktualisiertem Script..."
  export TELEMETRY_NO_SELFUPDATE=1
  exec "$SELF" "${@:2}"
}

# ── Git-Update ────────────────────────────────────────────────────────────────
cmd_update() {
  need_cmds
  need_dirs

  cd "$REPO_DIR"

  # CRLF-Warnungen unterdrücken – nur Whitespace, kein echter Konflikt
  git config core.autocrlf input

  local stashed=false

  # Dirty working tree → automatisch stashen
  if ! git diff --quiet || ! git diff --cached --quiet; then
    warn "Lokale Änderungen erkannt – wird automatisch gestasht."
    if git stash push --include-untracked -m "telemetry-auto-stash-$(date +%Y%m%d-%H%M%S)"; then
      stashed=true
      log "git stash: lokale Änderungen gesichert."
    else
      die "git stash fehlgeschlagen – bitte manuell prüfen: git status"
    fi
  fi

  log "git pull"
  if ! git pull; then
    if [[ "$stashed" == true ]]; then
      warn "git pull fehlgeschlagen – stelle lokale Änderungen wieder her..."
      git stash pop || warn "git stash pop fehlgeschlagen – bitte manuell prüfen: git stash list"
    fi
    die "git pull fehlgeschlagen."
  fi

  if [[ "$stashed" == true ]]; then
    log "git stash pop: lokale Änderungen werden wiederhergestellt."
    if ! git stash pop; then
      warn "Merge-Konflikt beim stash pop – bitte manuell auflösen: git stash list"
      warn "Stack wird trotzdem neu gestartet."
    fi
  fi

  cd "$COMPOSE_DIR"
  log "docker compose down"
  compose down
  log "docker compose pull"
  compose pull
  log "docker compose up -d"
  compose up -d
  ok "Telemetry aktualisiert & gestartet."
}

# ── Weitere Befehle ───────────────────────────────────────────────────────────
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
  [[ $EUID -eq 0 ]] || die "install muss als root ausgeführt werden (sudo telemetry install)"

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

# ── Dispatch ──────────────────────────────────────────────────────────────────

# self-update explizit: kein automatischer Check davor
if [[ "${1:-help}" == "self-update" ]]; then
  cmd_self_update verbose
  exit 0
fi

# Automatischer Check bei jedem anderen Befehl (still, ohne Output wenn aktuell)
# Alle Argumente werden weitergereicht damit exec nach Update korrekt neu startet
cmd_self_update silent "$@"

case "${1:-help}" in
  update)         cmd_update  ;;
  start)          cmd_start   ;;
  stop)           cmd_stop    ;;
  restart)        cmd_restart ;;
  status)         cmd_status  ;;
  logs)           cmd_logs    ;;
  install)        cmd_install ;;
  help|--help|-h) usage       ;;
  *)
    warn "Unbekannter Befehl: '${1}'"
    usage
    exit 1
    ;;
esac
EOF

sudo chmod +x /usr/local/bin/telemetry
echo "✅ /usr/local/bin/telemetry installiert."
