# Installation Guide - IDM Metrics Collector

Complete installation guide for the Docker Compose deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Linux distribution with Docker and Docker Compose support
- **Network**: Access to IDM Heat Pump via Modbus TCP

### Required Access

- Root or sudo privileges
- Internet connection (for pulling images)
- IDM Heat Pump accessible via network

## Installation

### Docker Compose Installation **[RECOMMENDED]**

**Best for**: Complete turnkey solution, includes monitoring stack, zero-config setup

#### What Gets Installed

- Docker engine (pre-requisite)
- IDM Metrics Collector container
- VictoriaMetrics container (time-series database)
- Grafana container (visualization platform)
- Pre-configured dashboards and datasources

#### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Xerolux/idm-metrics-collector.git
   cd idm-metrics-collector
   ```

2. **Start the stack:**
   ```bash
   docker compose up -d
   ```

#### Stack Management

```bash
# Navigate to installation directory
cd idm-metrics-collector

# View running services
docker compose ps

# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart all services
docker compose restart

# View logs from all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Pull latest images
docker compose pull
```

#### Service URLs

After installation, access:

- **Web UI**: http://your-server-ip:5008
  - Username: `admin`
  - Password: `admin`

- **Grafana**: http://your-server-ip:3001
  - Username: `admin`
  - Password: `admin`

- **VictoriaMetrics**: http://your-server-ip:8428

## Post-Installation

### Initial Configuration

1. **Edit configuration file (optional)**:
   You can map a custom configuration file, but typically environment variables in `docker-compose.yml` are sufficient for basic connectivity.

2. **Essential settings (in docker-compose.yml)**:
   ```yaml
    environment:
      # IDM Heat Pump connection
      - IDM_HOST=192.168.178.103  # Change to your heat pump IP
      - IDM_PORT=502
   ```

3. **Restart service** to apply changes
   ```bash
   docker compose restart idm-logger
   ```

### First Run Wizard

On first access to the Web UI (http://your-server-ip:5008):

1. Log in with default credentials (`admin` / `admin`)
2. Change admin password (important!)
3. Test heat pump connection

### Signal-CLI (Optional)

If enabled in configuration, allows Signal notifications.

### Security Recommendations

1. **Change default passwords**:
   - Web UI admin password
   - Grafana admin password (in docker-compose.yml)

2. **Configure firewall**:
   ```bash
   # Allow only necessary ports
   sudo ufw allow 5008/tcp   # Web UI
   sudo ufw allow 3001/tcp   # Grafana
   sudo ufw allow 8428/tcp   # VictoriaMetrics
   sudo ufw enable
   ```

## Troubleshooting

### Common Issues

#### 1. Cannot connect to heat pump

```bash
# Check logs
docker compose logs -f idm-logger
```

**Solution**: Verify IP address in `docker-compose.yml`, ensure heat pump allows Modbus TCP connections.

#### 2. Service won't start

```bash
# Check service status
docker compose ps
```

### Getting Help

If you encounter issues:

1. Check logs first
2. Review [GitHub Issues](https://github.com/Xerolux/idm-metrics-collector/issues)
