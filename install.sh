#!/bin/bash
################################################################################
# IDM Metrics Collector - Installationsskript
# Unterstützt: Docker und Docker Compose Installationen
################################################################################

# Hinweis: Kein 'set -e', um defekte apt-Repositories elegant zu behandeln

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Keine Farbe

# Variablen
APP_NAME="idm-metrics-collector"
INSTALL_DIR="/opt/${APP_NAME}"
GITHUB_REPO="Xerolux/idm-metrics-collector"

# Ausgabefunktionen
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ERFOLG]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

print_error() {
    echo -e "${RED}[FEHLER]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# Prüfe auf Root-Rechte
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Dieses Skript muss als Root ausgeführt werden (benutze sudo)"
        exit 1
    fi
}

# Betriebssystem erkennen
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        print_info "Erkanntes OS: $OS $VER"
    else
        print_error "Kann OS nicht erkennen. /etc/os-release nicht gefunden."
        exit 1
    fi
}

# Grundlegende Abhängigkeiten installieren
install_basic_dependencies() {
    print_header "Installiere grundlegende Abhängigkeiten"

    case $OS in
        ubuntu|debian)
            # Prüfen, ob erforderliche Befehle verfügbar sind, überspringen falls vorhanden
            local missing_packages=()

            for cmd in curl wget git; do
                if ! command -v $cmd &> /dev/null; then
                    missing_packages+=($cmd)
                fi
            done

            if [ ${#missing_packages[@]} -eq 0 ]; then
                print_info "Alle erforderlichen Pakete bereits installiert"
            else
                print_info "Installiere fehlende Pakete: ${missing_packages[*]}"
                # Versuch zu aktualisieren, aber nicht abbrechen bei defekten Repos
                apt-get update 2>&1 | head -n 1 || true

                # Fehlende Pakete einzeln installieren
                for pkg in "${missing_packages[@]}"; do
                    apt-get install -y $pkg 2>&1 | tail -n 5 || print_warning "Konnte $pkg nicht installieren (vielleicht schon vorhanden)"
                done
            fi
            ;;
        centos|rhel|fedora)
            yum install -y curl wget git ca-certificates 2>/dev/null || true
            ;;
        *)
            print_error "Nicht unterstütztes OS für automatische Installation"
            exit 1
            ;;
    esac

    print_success "Grundlegende Abhängigkeiten bereit"
}

# Docker installieren
install_docker() {
    print_header "Installiere Docker"

    if command -v docker &> /dev/null; then
        print_info "Docker ist bereits installiert ($(docker --version))"
        return 0
    fi

    case $OS in
        ubuntu|debian)
            # Docker mit offiziellem Skript installieren
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            rm get-docker.sh

            # Docker starten und aktivieren
            systemctl start docker
            systemctl enable docker
            ;;
        centos|rhel|fedora)
            yum install -y docker
            systemctl start docker
            systemctl enable docker
            ;;
        *)
            print_error "Nicht unterstütztes OS für Docker-Installation"
            exit 1
            ;;
    esac

    print_success "Docker erfolgreich installiert ($(docker --version))"
}

# Docker Compose installieren
install_docker_compose() {
    print_header "Installiere Docker Compose"

    # Prüfen ob docker compose plugin verfügbar ist
    if docker compose version &> /dev/null; then
        print_info "Docker Compose Plugin ist bereits installiert ($(docker compose version))"
        return 0
    fi

    # Prüfen ob standalone docker-compose verfügbar ist
    if command -v docker-compose &> /dev/null; then
        print_info "Docker Compose Standalone ist bereits installiert ($(docker-compose --version))"
        return 0
    fi

    # Docker Compose Plugin installieren (bevorzugte Methode)
    case $OS in
        ubuntu|debian)
            apt-get install -y docker-compose-plugin
            ;;
        centos|rhel|fedora)
            yum install -y docker-compose-plugin
            ;;
        *)
            # Fallback: Standalone docker-compose installieren
            print_info "Installiere Standalone Docker Compose..."
            DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
            curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
            ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose || true
            ;;
    esac

    # Installation verifizieren
    if docker compose version &> /dev/null; then
        print_success "Docker Compose Plugin erfolgreich installiert ($(docker compose version))"
    elif command -v docker-compose &> /dev/null; then
        print_success "Docker Compose Standalone erfolgreich installiert ($(docker-compose --version))"
    else
        print_error "Fehler bei der Installation von Docker Compose"
        exit 1
    fi
}

# Installation mit Docker (Einzel-Container)
install_docker_only() {
    print_header "Installiere ${APP_NAME} (Docker)"

    # Docker installieren
    install_docker

    # Arbeitsverzeichnis erstellen
    mkdir -p ${INSTALL_DIR}
    cd ${INSTALL_DIR}

    # Repository klonen
    if [[ -d "${INSTALL_DIR}/.git" ]]; then
        print_info "Aktualisiere bestehende Installation..."
        git pull
    else
        print_info "Klone Repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Beispiel-Konfiguration kopieren falls nicht vorhanden
    if [[ ! -f config.yaml ]]; then
        cp config.yaml.example config.yaml
        print_warning "Standard-Konfiguration erstellt unter ${INSTALL_DIR}/config.yaml"
    fi

    # Alten Container stoppen und entfernen falls vorhanden
    if docker ps -a | grep -q ${APP_NAME}; then
        print_info "Entferne alten Container..."
        docker stop ${APP_NAME} 2>/dev/null || true
        docker rm ${APP_NAME} 2>/dev/null || true
    fi

    # Image von GHCR pullen
    print_info "Lade Docker Image von GitHub Container Registry..."
    docker pull ghcr.io/xerolux/${APP_NAME}:latest

    # Datenverzeichnis erstellen
    mkdir -p ${INSTALL_DIR}/data

    # Container erstellen und starten
    print_info "Starte Container..."
    docker run -d \
        --name ${APP_NAME} \
        --restart unless-stopped \
        -p 5000:5000 \
        -v ${INSTALL_DIR}/config.yaml:/app/data/config.yaml:ro \
        -v ${INSTALL_DIR}/data:/app/data \
        ghcr.io/xerolux/${APP_NAME}:latest

    print_success "Docker Installation abgeschlossen"
    print_info ""
    print_info "Container Status: docker ps | grep ${APP_NAME}"
    print_info "Logs: docker logs -f ${APP_NAME}"
    print_info "Konfiguration: ${INSTALL_DIR}/config.yaml"
}

# Installation mit Docker Compose (Full Stack)
install_docker_compose_stack() {
    print_header "Installiere ${APP_NAME} (Docker Compose)"

    # Docker und Docker Compose installieren
    install_docker
    install_docker_compose

    # Arbeitsverzeichnis erstellen
    mkdir -p ${INSTALL_DIR}
    cd ${INSTALL_DIR}

    # Repository klonen
    if [[ -d "${INSTALL_DIR}/.git" ]]; then
        print_info "Aktualisiere bestehende Installation..."
        git pull
    else
        print_info "Klone Repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Beispiel-Konfiguration kopieren falls nicht vorhanden
    if [[ ! -f config.yaml ]]; then
        cp config.yaml.example config.yaml 2>/dev/null || true
        print_warning "Standard-Konfiguration erstellt unter ${INSTALL_DIR}/config.yaml"
    fi

    # Sicheren Token für neue Installationen generieren
    print_header "Generiere Sicheren Token"
    print_info "Generiere neuen InfluxDB Authentifizierungs-Token..."

    if [[ -f scripts/generate-token.sh ]]; then
        bash scripts/generate-token.sh
        print_success "Token generiert und auf alle Konfigurationsdateien angewendet"
    else
        print_warning "Token-Generator nicht gefunden, verwende Standard-Token"
        print_warning "SICHERHEITSWARNUNG: Bitte ändere das Standard-Token nach der Installation!"
    fi

    # Bestehenden Stack stoppen
    print_info "Stoppe existierende Dienste..."
    docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

    # Images von Registries pullen
    print_info "Lade Docker Images von Registries..."
    if docker compose version &> /dev/null; then
        docker compose pull
    else
        docker-compose pull
    fi

    # Stack starten
    print_info "Starte Docker Compose Stack..."
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    print_success "Docker Compose Installation abgeschlossen"
    print_info ""
    print_info "Dienste:"
    print_info "  - Web UI:     http://$(hostname -I | awk '{print $1}'):5008 (Login: admin/admin)"
    print_info "  - Grafana:    http://$(hostname -I | awk '{print $1}'):3001 (Login: admin/admin)"
    print_info "  - InfluxDB:   http://$(hostname -I | awk '{print $1}'):8181 (Datenbank: idm, Query: SQL)"
    print_info ""
    print_info "InfluxDB v3 Token:"
    # Token aus docker-compose.yml extrahieren
    TOKEN=$(grep "INFLUX_TOKEN=" docker-compose.yml | head -1 | cut -d'=' -f2)
    print_warning "  ${TOKEN}"
    print_info ""
    print_warning "WICHTIG: Speichere deinen InfluxDB Token sicher!"
    print_warning "Du wirst ihn benötigen, um weitere Clients zu konfigurieren oder den Zugriff wiederherzustellen."
    print_info ""
    print_info "Nützliche Befehle:"
    print_info "  - Status:     cd ${INSTALL_DIR} && docker compose ps"
    print_info "  - Logs:       cd ${INSTALL_DIR} && docker compose logs -f"
    print_info "  - Stop:       cd ${INSTALL_DIR} && docker compose down"
    print_info "  - Restart:    cd ${INSTALL_DIR} && docker compose restart"
    print_info ""
    print_info "Konfiguration: ${INSTALL_DIR}/config.yaml"
}

# Installationsmenü anzeigen
show_menu() {
    print_header "IDM Metrics Collector - Installation"

    echo "Bitte wähle eine Installationsmethode:"
    echo ""
    echo "  1) Docker           - Einzelner Container (Nur App)"
    echo "  2) Docker Compose   - Full Stack (App + InfluxDB + Grafana) [EMPFOHLEN]"
    echo "  3) Beenden"
    echo ""
    read -p "Gib deine Wahl ein [1-3]: " choice

    case $choice in
        1)
            INSTALL_TYPE="docker"
            ;;
        2)
            INSTALL_TYPE="docker_compose"
            ;;
        3)
            print_info "Installation abgebrochen"
            exit 0
            ;;
        *)
            print_error "Ungültige Wahl"
            exit 1
            ;;
    esac
}

# Hauptfunktion
main() {
    clear
    print_header "IDM Metrics Collector Installer"

    # Root prüfen
    check_root

    # OS erkennen
    detect_os

    # Grundlegende Abhängigkeiten installieren
    install_basic_dependencies

    # Menü anzeigen
    show_menu

    # Basierend auf Wahl installieren
    case $INSTALL_TYPE in
        docker)
            install_docker_only
            ;;
        docker_compose)
            install_docker_compose_stack
            ;;
    esac

    print_header "Installation Abgeschlossen!"

    case $INSTALL_TYPE in
        docker)
            echo -e "${GREEN}Nächste Schritte:${NC}"
            echo "  1. Konfiguration bearbeiten: nano ${INSTALL_DIR}/config.yaml"
            echo "  2. Container neustarten: docker restart ${APP_NAME}"
            echo "  3. Logs ansehen: docker logs -f ${APP_NAME}"
            echo ""
            echo "Web UI: http://$(hostname -I | awk '{print $1}'):5000"
            ;;
        docker_compose)
            echo -e "${GREEN}Zugriff auf deine Dienste:${NC}"
            echo "  - Web UI:   http://$(hostname -I | awk '{print $1}'):5008"
            echo "  - Grafana:  http://$(hostname -I | awk '{print $1}'):3001"
            echo "  - InfluxDB: http://$(hostname -I | awk '{print $1}'):8181"
            echo ""
            echo -e "${YELLOW}WICHTIG: Bearbeite ${INSTALL_DIR}/config.yaml und setze deine Wärmepumpen-IP!${NC}"
            echo "Dann neustarten: cd ${INSTALL_DIR} && docker compose restart"
            ;;
    esac

    echo ""
}

# Main ausführen
main
