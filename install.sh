#!/bin/bash
################################################################################
# IDM Metrics Collector - Installation Script
# Supports: Bare Metal, Docker, Docker Compose installations
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
SERVICE_NAME="${APP_NAME}"
USER="${APP_NAME}"
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

# Update system packages
update_system() {
    print_header "Updating System Packages"

    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get upgrade -y
            print_success "System updated successfully"
            ;;
        centos|rhel|fedora)
            yum update -y
            print_success "System updated successfully"
            ;;
        *)
            print_warning "Unknown OS. Skipping system update."
            ;;
    esac
}

# Install basic dependencies
install_basic_dependencies() {
    print_header "Installing Basic Dependencies"

    case $OS in
        ubuntu|debian)
            apt-get install -y \
                curl \
                wget \
                git \
                software-properties-common \
                apt-transport-https \
                ca-certificates \
                gnupg \
                lsb-release \
                net-tools
            ;;
        centos|rhel|fedora)
            yum install -y \
                curl \
                wget \
                git \
                ca-certificates \
                net-tools
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
            # Remove old versions
            apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

            # Install Docker
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

    if command -v docker-compose &> /dev/null; then
        print_info "Docker Compose is already installed ($(docker-compose --version))"
        return 0
    fi

    # Get latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

    # Download and install
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Create symlink
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose || true

    print_success "Docker Compose installed successfully ($(docker-compose --version))"
}

# Install Python and dependencies for bare metal
install_python_dependencies() {
    print_header "Installing Python 3.11 and Dependencies"

    case $OS in
        ubuntu|debian)
            apt-get install -y \
                python3.11 \
                python3.11-venv \
                python3-pip \
                build-essential \
                libssl-dev \
                libffi-dev \
                python3-dev
            ;;
        centos|rhel|fedora)
            yum install -y \
                python311 \
                python311-devel \
                python3-pip \
                gcc \
                openssl-devel \
                libffi-devel
            ;;
        *)
            print_error "Unsupported OS for Python installation"
            exit 1
            ;;
    esac

    # Update pip
    python3.11 -m pip install --upgrade pip

    print_success "Python and dependencies installed"
}

# Install application (Bare Metal)
install_bare_metal() {
    print_header "Installing ${APP_NAME} (Bare Metal)"

    # Install Python dependencies
    install_python_dependencies

    # Create user
    if ! id -u $USER &>/dev/null; then
        useradd -r -s /bin/false $USER
        print_info "Created user: $USER"
    fi

    # Create directory
    mkdir -p $INSTALL_DIR
    cd $INSTALL_DIR

    # Clone or update repository
    if [[ -d "${INSTALL_DIR}/.git" ]]; then
        print_info "Updating existing installation..."
        sudo -u $USER git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate

    # Install requirements
    pip install --no-cache-dir -r requirements.txt

    # Create data directory
    mkdir -p ${INSTALL_DIR}/data

    # Copy example config if not exists
    if [[ ! -f ${INSTALL_DIR}/data/config.yaml ]]; then
        cp config.yaml.example ${INSTALL_DIR}/data/config.yaml
        print_info "Created default config at ${INSTALL_DIR}/data/config.yaml"
    fi

    # Set permissions
    chown -R $USER:$USER $INSTALL_DIR
    chmod -R 755 $INSTALL_DIR

    # Create systemd service
    create_systemd_service

    # Enable and start service
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    systemctl start $SERVICE_NAME

    print_success "Bare metal installation complete"
    print_info "Service status: systemctl status $SERVICE_NAME"
    print_info "Configuration: ${INSTALL_DIR}/data/config.yaml"
}

# Create systemd service
create_systemd_service() {
    print_info "Creating systemd service..."

    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=IDM Metrics Collector
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=${INSTALL_DIR}/data
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/python -m idm_logger.logger
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    print_info "Systemd service created: /etc/systemd/system/${SERVICE_NAME}.service"
}

# Install with Docker
install_docker_only() {
    print_header "Installing ${APP_NAME} (Docker)"

    # Install Docker
    install_docker

    # Create working directory
    mkdir -p /opt/${APP_NAME}
    cd /opt/${APP_NAME}

    # Clone repository
    if [[ -d "/opt/${APP_NAME}/.git" ]]; then
        print_info "Updating existing installation..."
        git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Copy example config if not exists
    if [[ ! -f config.yaml ]]; then
        cp config.yaml.example config.yaml
        print_warning "Created default config. Please edit config.yaml before starting!"
    fi

    # Build image
    print_info "Building Docker image..."
    docker build -t ${APP_NAME}:latest .

    # Create and start container
    print_info "Starting container..."
    docker run -d \
        --name ${APP_NAME} \
        --restart unless-stopped \
        -p 5000:5000 \
        -v /opt/${APP_NAME}/data:/app/data \
        ${APP_NAME}:latest

    print_success "Docker installation complete"
    print_info "Container status: docker ps | grep ${APP_NAME}"
    print_info "Logs: docker logs ${APP_NAME}"
    print_info "Configuration: /opt/${APP_NAME}/config.yaml"
}

# Install with Docker Compose
install_docker_compose_stack() {
    print_header "Installing ${APP_NAME} (Docker Compose)"

    # Install Docker and Docker Compose
    install_docker
    install_docker_compose

    # Create working directory
    mkdir -p /opt/${APP_NAME}
    cd /opt/${APP_NAME}

    # Clone repository
    if [[ -d "/opt/${APP_NAME}/.git" ]]; then
        print_info "Updating existing installation..."
        git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/${GITHUB_REPO}.git .
    fi

    # Copy example config if not exists
    if [[ ! -f config.yaml ]]; then
        cp config.yaml.example config.yaml
        print_warning "Created default config. Please edit config.yaml before starting!"
    fi

    # Pull images
    print_info "Pulling Docker images..."
    docker-compose pull || true

    # Start stack
    print_info "Starting Docker Compose stack..."
    docker-compose up -d --build

    print_success "Docker Compose installation complete"
    print_info ""
    print_info "Services:"
    print_info "  - Web UI:     http://localhost:5000 (Default login: admin/admin)"
    print_info "  - Grafana:    http://localhost:3000 (Login: admin/admin)"
    print_info "  - InfluxDB:   http://localhost:8086 (User: admin, Pass: adminpassword123)"
    print_info ""
    print_info "Useful commands:"
    print_info "  - Status:     docker-compose ps"
    print_info "  - Logs:       docker-compose logs -f"
    print_info "  - Stop:       docker-compose down"
    print_info "  - Restart:    docker-compose restart"
}

# Show installation menu
show_menu() {
    print_header "IDM Metrics Collector - Installation"

    echo "Please select installation method:"
    echo ""
    echo "  1) Bare Metal       - Install directly on system (systemd service)"
    echo "  2) Docker           - Install as Docker container (single container)"
    echo "  3) Docker Compose   - Install complete stack (App + InfluxDB + Grafana)"
    echo "  4) Exit"
    echo ""
    read -p "Enter your choice [1-4]: " choice

    case $choice in
        1)
            INSTALL_TYPE="bare_metal"
            ;;
        2)
            INSTALL_TYPE="docker"
            ;;
        3)
            INSTALL_TYPE="docker_compose"
            ;;
        4)
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

    # Update system
    read -p "Update system packages? (recommended) [Y/n]: " update_choice
    if [[ ! $update_choice =~ ^[Nn]$ ]]; then
        update_system
    fi

    # Install basic dependencies
    install_basic_dependencies

    # Show menu
    show_menu

    # Install based on choice
    case $INSTALL_TYPE in
        bare_metal)
            install_bare_metal
            ;;
        docker)
            install_docker_only
            ;;
        docker_compose)
            install_docker_compose_stack
            ;;
    esac

    print_header "Installation Complete!"

    case $INSTALL_TYPE in
        bare_metal)
            echo -e "${GREEN}Next steps:${NC}"
            echo "  1. Edit configuration: nano ${INSTALL_DIR}/data/config.yaml"
            echo "  2. Restart service: systemctl restart ${SERVICE_NAME}"
            echo "  3. Check status: systemctl status ${SERVICE_NAME}"
            echo "  4. View logs: journalctl -u ${SERVICE_NAME} -f"
            echo ""
            echo "Web UI: http://$(hostname -I | awk '{print $1}'):5000"
            ;;
        docker)
            echo -e "${GREEN}Next steps:${NC}"
            echo "  1. Edit configuration: nano /opt/${APP_NAME}/config.yaml"
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
            ;;
    esac

    echo ""
}

# Run main
main
