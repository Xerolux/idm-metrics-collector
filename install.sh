#!/bin/bash
################################################################################
# IDM Metrics Collector - Installation Script
# Supports: Docker and Docker Compose installations
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
APP_NAME="idm-metrics-collector"
INSTALL_DIR="/opt/${APP_NAME}"
GITHUB_REPO="Xerolux/idm-metrics-collector"

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        print_info "Detected OS: $OS $VER"
    else
        print_error "Cannot detect OS. /etc/os-release not found."
        exit 1
    fi
}

# Install basic dependencies
install_basic_dependencies() {
    print_header "Installing Basic Dependencies"

    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get install -y curl wget git ca-certificates gnupg
            ;;
        centos|rhel|fedora)
            yum update -y
            yum install -y curl wget git ca-certificates
            ;;
        *)
            print_error "Unsupported OS for automatic installation"
            exit 1
            ;;
    esac

    print_success "Basic dependencies installed"
}

# Install Docker
install_docker() {
    print_header "Installing Docker"

    if command -v docker &> /dev/null; then
        print_info "Docker is already installed ($(docker --version))"
        return 0
    fi

    case $OS in
        ubuntu|debian)
            # Install Docker using official script
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            rm get-docker.sh

            # Start and enable Docker
            systemctl start docker
            systemctl enable docker
            ;;
        centos|rhel|fedora)
            yum install -y docker
            systemctl start docker
            systemctl enable docker
            ;;
        *)
            print_error "Unsupported OS for Docker installation"
            exit 1
            ;;
    esac

    print_success "Docker installed successfully ($(docker --version))"
}

# Install Docker Compose
install_docker_compose() {
    print_header "Installing Docker Compose"

    # Check if docker compose plugin is available
    if docker compose version &> /dev/null; then
        print_info "Docker Compose plugin is already installed ($(docker compose version))"
        return 0
    fi

    # Check if standalone docker-compose is available
    if command -v docker-compose &> /dev/null; then
        print_info "Docker Compose standalone is already installed ($(docker-compose --version))"
        return 0
    fi

    # Install Docker Compose plugin (preferred method)
    case $OS in
        ubuntu|debian)
            apt-get install -y docker-compose-plugin
            ;;
        centos|rhel|fedora)
            yum install -y docker-compose-plugin
            ;;
        *)
            # Fallback: Install standalone docker-compose
            print_info "Installing standalone Docker Compose..."
            DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
            curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
            ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose || true
            ;;
    esac

    # Verify installation
    if docker compose version &> /dev/null; then
        print_success "Docker Compose plugin installed successfully ($(docker compose version))"
    elif command -v docker-compose &> /dev/null; then
        print_success "Docker Compose standalone installed successfully ($(docker-compose --version))"
    else
        print_error "Failed to install Docker Compose"
        exit 1
    fi
}

# Install with Docker (single container)
install_docker_only() {
    print_header "Installing ${APP_NAME} (Docker)"

    # Install Docker
    install_docker

    # Create working directory
    mkdir -p ${INSTALL_DIR}
    cd ${INSTALL_DIR}

    # Clone repository
    if [[ -d "${INSTALL_DIR}/.git" ]]; then
        print_info "Updating existing installation..."
        git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Copy example config if not exists
    if [[ ! -f config.yaml ]]; then
        cp config.yaml.example config.yaml
        print_warning "Created default config at ${INSTALL_DIR}/config.yaml"
    fi

    # Stop and remove old container if exists
    if docker ps -a | grep -q ${APP_NAME}; then
        print_info "Removing old container..."
        docker stop ${APP_NAME} 2>/dev/null || true
        docker rm ${APP_NAME} 2>/dev/null || true
    fi

    # Build image
    print_info "Building Docker image..."
    docker build -t ${APP_NAME}:latest .

    # Create data directory
    mkdir -p ${INSTALL_DIR}/data

    # Create and start container
    print_info "Starting container..."
    docker run -d \
        --name ${APP_NAME} \
        --restart unless-stopped \
        -p 5000:5000 \
        -v ${INSTALL_DIR}/config.yaml:/app/data/config.yaml:ro \
        -v ${INSTALL_DIR}/data:/app/data \
        ${APP_NAME}:latest

    print_success "Docker installation complete"
    print_info ""
    print_info "Container status: docker ps | grep ${APP_NAME}"
    print_info "Logs: docker logs -f ${APP_NAME}"
    print_info "Configuration: ${INSTALL_DIR}/config.yaml"
}

# Install with Docker Compose (full stack)
install_docker_compose_stack() {
    print_header "Installing ${APP_NAME} (Docker Compose)"

    # Install Docker and Docker Compose
    install_docker
    install_docker_compose

    # Create working directory
    mkdir -p ${INSTALL_DIR}
    cd ${INSTALL_DIR}

    # Clone repository
    if [[ -d "${INSTALL_DIR}/.git" ]]; then
        print_info "Updating existing installation..."
        git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Copy example config if not exists
    if [[ ! -f config.yaml ]]; then
        cp config.yaml.example config.yaml
        print_warning "Created default config at ${INSTALL_DIR}/config.yaml"
    fi

    # Stop existing stack
    print_info "Stopping existing services..."
    docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

    # Pull images
    print_info "Pulling Docker images..."
    docker compose pull 2>/dev/null || docker-compose pull 2>/dev/null || true

    # Start stack
    print_info "Starting Docker Compose stack..."
    if docker compose version &> /dev/null; then
        docker compose up -d --build
    else
        docker-compose up -d --build
    fi

    print_success "Docker Compose installation complete"
    print_info ""
    print_info "Services:"
    print_info "  - Web UI:     http://$(hostname -I | awk '{print $1}'):5000 (Login: admin/admin)"
    print_info "  - Grafana:    http://$(hostname -I | awk '{print $1}'):3000 (Login: admin/admin)"
    print_info "  - InfluxDB:   http://$(hostname -I | awk '{print $1}'):8086 (User: admin, Pass: adminpassword123)"
    print_info ""
    print_info "Useful commands:"
    print_info "  - Status:     cd ${INSTALL_DIR} && docker compose ps"
    print_info "  - Logs:       cd ${INSTALL_DIR} && docker compose logs -f"
    print_info "  - Stop:       cd ${INSTALL_DIR} && docker compose down"
    print_info "  - Restart:    cd ${INSTALL_DIR} && docker compose restart"
    print_info ""
    print_info "Configuration: ${INSTALL_DIR}/config.yaml"
}

# Show installation menu
show_menu() {
    print_header "IDM Metrics Collector - Installation"

    echo "Please select installation method:"
    echo ""
    echo "  1) Docker           - Single container (App only)"
    echo "  2) Docker Compose   - Full stack (App + InfluxDB + Grafana) [RECOMMENDED]"
    echo "  3) Exit"
    echo ""
    read -p "Enter your choice [1-3]: " choice

    case $choice in
        1)
            INSTALL_TYPE="docker"
            ;;
        2)
            INSTALL_TYPE="docker_compose"
            ;;
        3)
            print_info "Installation cancelled"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Main installation
main() {
    clear
    print_header "IDM Metrics Collector Installer"

    # Check root
    check_root

    # Detect OS
    detect_os

    # Install basic dependencies
    install_basic_dependencies

    # Show menu
    show_menu

    # Install based on choice
    case $INSTALL_TYPE in
        docker)
            install_docker_only
            ;;
        docker_compose)
            install_docker_compose_stack
            ;;
    esac

    print_header "Installation Complete!"

    case $INSTALL_TYPE in
        docker)
            echo -e "${GREEN}Next steps:${NC}"
            echo "  1. Edit configuration: nano ${INSTALL_DIR}/config.yaml"
            echo "  2. Restart container: docker restart ${APP_NAME}"
            echo "  3. View logs: docker logs -f ${APP_NAME}"
            echo ""
            echo "Web UI: http://$(hostname -I | awk '{print $1}'):5000"
            ;;
        docker_compose)
            echo -e "${GREEN}Access your services:${NC}"
            echo "  - Web UI:   http://$(hostname -I | awk '{print $1}'):5000"
            echo "  - Grafana:  http://$(hostname -I | awk '{print $1}'):3000"
            echo "  - InfluxDB: http://$(hostname -I | awk '{print $1}'):8086"
            echo ""
            echo -e "${YELLOW}IMPORTANT: Edit ${INSTALL_DIR}/config.yaml and set your heat pump IP address!${NC}"
            echo "Then restart: cd ${INSTALL_DIR} && docker compose restart"
            ;;
    esac

    echo ""
}

# Run main
main
