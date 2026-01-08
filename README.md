# IDM Metrics Collector

A comprehensive monitoring and control system for IDM Heat Pumps (Navigator 2.0) with InfluxDB metrics storage and Grafana visualization.

## Features

*   **Multiple Installation Options**: Bare Metal, Docker, or Docker Compose (with full stack)
*   **Automated Setup**: Interactive installer handles all dependencies
*   **Data Source**: Reads from IDM Heat Pump via Modbus TCP
*   **Data Sink**: Supports InfluxDB v1 and v2
*   **Web Interface**: Modern dashboard for live data, configuration, manual control, and scheduling
*   **Automation**: Built-in scheduler to write values (e.g., temperatures) at specific times
*   **Zero-Config Docker**: Complete stack with InfluxDB and Grafana pre-configured
*   **Production Ready**: Systemd service, health checks, automatic restarts

## Quick Start

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/install.sh | sudo bash
```

Or clone and run:

```bash
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
sudo chmod +x install.sh
sudo ./install.sh
```

The installer will:
1. Detect your OS and update system packages
2. Install required dependencies (git, curl, etc.)
3. Ask you to choose installation method:
   - **Bare Metal**: Installs as systemd service with Python virtual environment
   - **Docker**: Single container deployment
   - **Docker Compose**: Complete stack (App + InfluxDB + Grafana)
4. Configure and start all services

### Installation Methods

#### 1. Bare Metal (Systemd Service)

Best for: Direct system installation, maximum control

```bash
sudo ./install.sh
# Choose option 1: Bare Metal
```

After installation:
```bash
# Edit configuration
sudo nano /opt/idm-metrics-collector/data/config.yaml

# Restart service
sudo systemctl restart idm-metrics-collector

# View logs
sudo journalctl -u idm-metrics-collector -f
```

#### 2. Docker (Single Container)

Best for: Simple containerized deployment

```bash
sudo ./install.sh
# Choose option 2: Docker
```

After installation:
```bash
# View logs
docker logs -f idm-metrics-collector

# Restart
docker restart idm-metrics-collector
```

#### 3. Docker Compose (Full Stack)

Best for: Complete turnkey solution with monitoring

```bash
sudo ./install.sh
# Choose option 3: Docker Compose
```

This installs:
- IDM Metrics Collector (Web UI + API)
- InfluxDB 2 (Time-series database)
- Grafana (Visualization platform)

All services are pre-configured and ready to use!

## Accessing Services

### After Installation

**Web UI** (IDM Metrics Collector)
- URL: `http://your-server-ip:5000`
- Default Login: `admin` / `admin` (change after first login)
- Features: Live dashboard, control panel, scheduling, configuration

**Grafana** (Docker Compose only)
- URL: `http://your-server-ip:3000`
- Default Login: `admin` / `admin`
- Pre-configured with InfluxDB datasource and IDM dashboard

**InfluxDB** (Docker Compose only)
- URL: `http://your-server-ip:8086`
- Default Credentials:
  - User: `admin`
  - Password: `adminpassword123`
  - Organization: `my-org`
  - Bucket: `idm`
  - Token: `my-super-secret-token-change-me`

### Docker Image (GHCR)

Pre-built images are available from GitHub Container Registry:

```bash
docker pull ghcr.io/xerolux/idm-metrics-collector:latest
docker run --rm -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  ghcr.io/xerolux/idm-metrics-collector:latest
```

Images are automatically built on:
- Pushes to `main` branch (tagged as `latest`)
- Git tags starting with `v` (e.g., `v1.0.0`)

## Configuration

Configuration file locations:
- **Bare Metal**: `/opt/idm-metrics-collector/data/config.yaml`
- **Docker/Compose**: `./config.yaml` in installation directory

Example:

```yaml
idm:
  host: "192.168.1.100"  # IP of your IDM Heat Pump
  port: 502              # Modbus Port
  circuits: ["A"]        # Enabled heating circuits

influx:
  version: 2             # 1 or 2
  url: "http://localhost:8086"
  org: "my-org"          # v2 only
  bucket: "idm"          # v2 only
  token: "my-token"      # v2 only
  username: "user"       # v1 only
  password: "password"   # v1 only
  database: "idm"        # v1 only

web:
  enabled: true
  port: 5000
  admin_password: "admin" # Password for login
  write_enabled: false    # Enable writing to heat pump (Control/Schedule)

logging:
  interval: 60           # Seconds between reads
  level: "INFO"
```

## Web Interface

Access the web interface at `http://<your-server-ip>:5000`.

*   **Live Dashboard**: Shows categorized sensor values with auto-refresh.
*   **Control**: (If enabled) Write values to writable sensors.
*   **Schedule**: (If enabled) Automate setting values based on time and day.
*   **Configuration**: Update connection settings.
