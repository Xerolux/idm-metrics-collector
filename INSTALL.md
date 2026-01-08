# Installation Guide - IDM Metrics Collector

Complete installation guide for all deployment methods.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Installation Methods](#installation-methods)
  - [Bare Metal Installation](#1-bare-metal-installation)
  - [Docker Installation](#2-docker-installation)
  - [Docker Compose Installation](#3-docker-compose-installation)
- [Manual Installation](#manual-installation)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Debian 11+, Ubuntu 20.04+, or compatible Linux distribution
- **CPU**: 1 core minimum, 2+ cores recommended
- **RAM**: 512 MB minimum, 1 GB+ recommended
- **Disk**: 1 GB minimum, 10 GB+ recommended for long-term data storage
- **Network**: Access to IDM Heat Pump via Modbus TCP

### Required Access

- Root or sudo privileges
- Internet connection (for installation only)
- IDM Heat Pump accessible via network

## Quick Installation

### One-Command Install

```bash
curl -fsSL https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/install.sh | sudo bash
```

Or download and run:

```bash
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
sudo chmod +x install.sh
sudo ./install.sh
```

The installer will guide you through:
1. OS detection and system updates
2. Dependency installation
3. Method selection (Bare Metal / Docker / Docker Compose)
4. Service configuration and startup

## Installation Methods

### 1. Bare Metal Installation

**Best for**: Production deployments, maximum performance, direct system integration

#### What Gets Installed

- Python 3.11 with virtual environment
- System dependencies (build tools, libraries)
- Systemd service for automatic startup
- Application in `/opt/idm-metrics-collector`

#### Installation Steps

```bash
sudo ./install.sh
# Select option 1: Bare Metal
```

#### Post-Install Configuration

```bash
# Edit configuration
sudo nano /opt/idm-metrics-collector/data/config.yaml

# Configure your IDM Heat Pump IP address
idm:
  host: "192.168.1.100"  # Change to your heat pump IP
  port: 502
  circuits: ["A"]

# Restart service
sudo systemctl restart idm-metrics-collector

# Check status
sudo systemctl status idm-metrics-collector

# View logs
sudo journalctl -u idm-metrics-collector -f
```

#### Service Management

```bash
# Start service
sudo systemctl start idm-metrics-collector

# Stop service
sudo systemctl stop idm-metrics-collector

# Restart service
sudo systemctl restart idm-metrics-collector

# Enable auto-start on boot
sudo systemctl enable idm-metrics-collector

# Disable auto-start
sudo systemctl disable idm-metrics-collector

# View service status
sudo systemctl status idm-metrics-collector

# View recent logs
sudo journalctl -u idm-metrics-collector -n 100

# Follow logs in real-time
sudo journalctl -u idm-metrics-collector -f
```

### 2. Docker Installation

**Best for**: Simple containerized deployment, easy updates, isolated environment

#### What Gets Installed

- Docker engine
- IDM Metrics Collector container
- Persistent data volume

#### Installation Steps

```bash
sudo ./install.sh
# Select option 2: Docker
```

#### Post-Install Configuration

```bash
# Stop container
docker stop idm-metrics-collector

# Edit configuration
cd /opt/idm-metrics-collector
nano config.yaml

# Configure your IDM Heat Pump IP
idm:
  host: "192.168.1.100"  # Change to your heat pump IP
  port: 502
  circuits: ["A"]

# Start container
docker start idm-metrics-collector
```

#### Container Management

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Start container
docker start idm-metrics-collector

# Stop container
docker stop idm-metrics-collector

# Restart container
docker restart idm-metrics-collector

# View logs
docker logs idm-metrics-collector

# Follow logs in real-time
docker logs -f idm-metrics-collector

# View last 100 lines
docker logs --tail 100 idm-metrics-collector

# Remove container (keeps data)
docker rm idm-metrics-collector

# Rebuild and start container
cd /opt/idm-metrics-collector
docker build -t idm-metrics-collector:latest .
docker run -d \
  --name idm-metrics-collector \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /opt/idm-metrics-collector/data:/app/data \
  idm-metrics-collector:latest
```

### 3. Docker Compose Installation

**Best for**: Complete turnkey solution, includes monitoring stack, zero-config setup

#### What Gets Installed

- Docker engine
- Docker Compose
- IDM Metrics Collector container
- InfluxDB 2 container (time-series database)
- Grafana container (visualization platform)
- Pre-configured dashboards and datasources

#### Installation Steps

```bash
sudo ./install.sh
# Select option 3: Docker Compose
```

#### Post-Install Configuration

```bash
# Stop stack
cd /opt/idm-metrics-collector
docker-compose down

# Edit configuration
nano config.yaml

# Configure your IDM Heat Pump IP
idm:
  host: "192.168.1.100"  # Change to your heat pump IP
  port: 502
  circuits: ["A"]

# Start stack
docker-compose up -d
```

#### Stack Management

```bash
# Navigate to installation directory
cd /opt/idm-metrics-collector

# View running services
docker-compose ps

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart idm-logger
docker-compose restart influxdb
docker-compose restart grafana

# View logs from all services
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs from specific service
docker-compose logs idm-logger
docker-compose logs influxdb
docker-compose logs grafana

# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build

# Remove all containers (keeps data in volumes)
docker-compose down

# Remove containers and volumes (DELETES ALL DATA!)
docker-compose down -v
```

#### Service URLs

After installation, access:

- **Web UI**: http://your-server-ip:5000
  - Username: `admin`
  - Password: `admin`

- **Grafana**: http://your-server-ip:3000
  - Username: `admin`
  - Password: `admin`

- **InfluxDB**: http://your-server-ip:8086
  - Username: `admin`
  - Password: `adminpassword123`
  - Organization: `my-org`
  - Bucket: `idm`

## Manual Installation

If you prefer manual installation without the script:

### Bare Metal Manual

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip git

# Clone repository
sudo mkdir -p /opt/idm-metrics-collector
cd /opt/idm-metrics-collector
sudo git clone https://github.com/Xerolux/idm-metrics-collector.git .

# Create virtual environment
sudo python3.11 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# Create user
sudo useradd -r -s /bin/false idm-metrics-collector

# Create data directory and config
sudo mkdir -p /opt/idm-metrics-collector/data
sudo cp config.yaml.example /opt/idm-metrics-collector/data/config.yaml

# Set permissions
sudo chown -R idm-metrics-collector:idm-metrics-collector /opt/idm-metrics-collector

# Create systemd service
sudo nano /etc/systemd/system/idm-metrics-collector.service
```

Add this content:

```ini
[Unit]
Description=IDM Metrics Collector
After=network.target

[Service]
Type=simple
User=idm-metrics-collector
Group=idm-metrics-collector
WorkingDirectory=/opt/idm-metrics-collector/data
Environment="PATH=/opt/idm-metrics-collector/venv/bin"
ExecStart=/opt/idm-metrics-collector/venv/bin/python -m idm_logger.logger
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable idm-metrics-collector
sudo systemctl start idm-metrics-collector
```

### Docker Compose Manual

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector

# Create config
cp config.yaml.example config.yaml
nano config.yaml  # Edit your settings

# Start stack
docker-compose up -d
```

## Post-Installation

### Initial Configuration

1. **Edit configuration file**:
   ```bash
   # Bare Metal
   sudo nano /opt/idm-metrics-collector/data/config.yaml

   # Docker/Compose
   nano /opt/idm-metrics-collector/config.yaml
   ```

2. **Essential settings**:
   ```yaml
   idm:
     host: "192.168.1.100"  # Your heat pump IP
     port: 502              # Modbus TCP port (usually 502)
     circuits: ["A"]        # Heating circuits to monitor

   influx:
     version: 2
     url: "http://localhost:8086"  # Or your InfluxDB server
     org: "my-org"
     bucket: "idm"
     token: "my-super-secret-token-change-me"

   web:
     enabled: true
     port: 5000
     write_enabled: false   # Set to true to enable control features

   logging:
     interval: 60          # Data collection interval in seconds
     level: "INFO"
   ```

3. **Restart service** to apply changes

### First Run Wizard

On first access to the Web UI (http://your-server-ip:5000):

1. Log in with default credentials (`admin` / `admin`)
2. Complete the First Run Wizard
3. Change admin password (important!)
4. Configure InfluxDB connection
5. Test heat pump connection

### Security Recommendations

1. **Change default passwords**:
   - Web UI admin password (via UI or config)
   - InfluxDB admin password (in docker-compose.yml)
   - Grafana admin password (in docker-compose.yml)

2. **Configure firewall**:
   ```bash
   # Allow only necessary ports
   sudo ufw allow 5000/tcp   # Web UI
   sudo ufw allow 3000/tcp   # Grafana (if using Docker Compose)
   sudo ufw allow 8086/tcp   # InfluxDB (if using Docker Compose)
   sudo ufw enable
   ```

3. **Use reverse proxy** for HTTPS (optional but recommended):
   - Nginx or Apache with Let's Encrypt SSL certificate

## Troubleshooting

### Common Issues

#### 1. Cannot connect to heat pump

```bash
# Test connectivity
ping 192.168.1.100  # Your heat pump IP

# Test Modbus TCP port
telnet 192.168.1.100 502

# Check logs
# Bare Metal:
sudo journalctl -u idm-metrics-collector -f

# Docker:
docker logs -f idm-metrics-collector
```

**Solution**: Verify IP address, ensure heat pump allows Modbus TCP connections

#### 2. Service won't start (Bare Metal)

```bash
# Check service status
sudo systemctl status idm-metrics-collector

# Check for errors
sudo journalctl -u idm-metrics-collector -n 50

# Test manually
cd /opt/idm-metrics-collector/data
sudo -u idm-metrics-collector /opt/idm-metrics-collector/venv/bin/python -m idm_logger.logger
```

**Solution**: Check permissions, verify config syntax, ensure dependencies installed

#### 3. Docker build fails with DNS error

```bash
# Check Docker DNS
docker run --rm alpine ping -c 1 google.com

# Configure Docker DNS
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

```bash
sudo systemctl restart docker
```

#### 4. InfluxDB connection fails

```bash
# Check InfluxDB is running
# Docker Compose:
docker-compose ps

# Test InfluxDB API
curl http://localhost:8086/health
```

**Solution**: Verify InfluxDB is running, check token and credentials in config

#### 5. Web UI not accessible

```bash
# Check if service is running
# Bare Metal:
sudo systemctl status idm-metrics-collector

# Docker:
docker ps | grep idm-metrics-collector

# Check if port is listening
sudo netstat -tlnp | grep 5000
```

**Solution**: Check firewall rules, verify port binding, ensure service started successfully

### Getting Help

If you encounter issues:

1. Check logs first (see commands above)
2. Verify configuration file syntax
3. Review [GitHub Issues](https://github.com/Xerolux/idm-metrics-collector/issues)
4. Create new issue with:
   - Installation method used
   - OS version
   - Error messages from logs
   - Configuration file (remove sensitive data)

### Uninstallation

#### Bare Metal

```bash
# Stop and disable service
sudo systemctl stop idm-metrics-collector
sudo systemctl disable idm-metrics-collector

# Remove service file
sudo rm /etc/systemd/system/idm-metrics-collector.service
sudo systemctl daemon-reload

# Remove installation
sudo rm -rf /opt/idm-metrics-collector

# Remove user
sudo userdel idm-metrics-collector
```

#### Docker

```bash
# Stop and remove container
docker stop idm-metrics-collector
docker rm idm-metrics-collector

# Remove image
docker rmi idm-metrics-collector:latest

# Remove data (optional)
sudo rm -rf /opt/idm-metrics-collector
```

#### Docker Compose

```bash
# Stop and remove containers
cd /opt/idm-metrics-collector
docker-compose down

# Remove volumes (DELETES ALL DATA!)
docker-compose down -v

# Remove installation
cd ..
sudo rm -rf /opt/idm-metrics-collector
```

## Updates

### Bare Metal

```bash
cd /opt/idm-metrics-collector
sudo git pull
sudo venv/bin/pip install -r requirements.txt
sudo systemctl restart idm-metrics-collector
```

### Docker

```bash
cd /opt/idm-metrics-collector
git pull
docker build -t idm-metrics-collector:latest .
docker stop idm-metrics-collector
docker rm idm-metrics-collector
docker run -d \
  --name idm-metrics-collector \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /opt/idm-metrics-collector/data:/app/data \
  idm-metrics-collector:latest
```

### Docker Compose

```bash
cd /opt/idm-metrics-collector
git pull
docker-compose pull
docker-compose up -d --build
```

## Additional Resources

- [Main README](README.md)
- [Configuration Guide](README.md#configuration)
- [Web Interface Guide](README.md#web-interface)
- [GitHub Repository](https://github.com/Xerolux/idm-metrics-collector)
