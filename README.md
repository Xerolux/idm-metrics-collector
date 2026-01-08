# IDM Heat Pump Logger

A Debian tool to log data from IDM Heat Pumps (Navigator 2.0) to InfluxDB (v1 or v2).

## Features

*   **Automatic Startup**: Runs as a systemd service.
*   **Data Source**: Reads from IDM Heat Pump via Modbus TCP.
*   **Data Sink**: Supports InfluxDB v1 and v2.
*   **Web Interface**: Modern dashboard for live data, configuration, manual control, and scheduling.
*   **Automation**: Built-in scheduler to write values (e.g., temperatures) at specific times.
*   **Docker Support**: Ready-to-use Docker Compose stack.
*   **Easy Installation**: Interactive installer script for Debian.

## Installation (Debian/Ubuntu)

1.  Clone this repository:
    ```bash
    git clone https://github.com/yourusername/idm-logger.git
    cd idm-logger
    ```

2.  Run the installation script (as root):
    ```bash
    sudo ./install.sh
    ```
    The script will ask if you want to install InfluxDB and Grafana locally on your system.

3.  Edit the configuration file:
    ```bash
    sudo nano /opt/idm-logger/config.yaml
    ```
    *Tip: Set `web.write_enabled: true` to enable control and scheduling features.*

4.  Start the service:
    ```bash
    sudo systemctl start idm-logger
    ```

## Installation (Docker)

### Docker Image (GHCR)

The repository publishes a ready-to-use image to GitHub Container Registry (GHCR).

```bash
docker pull ghcr.io/<github-org-or-user>/idm-logger:latest
docker run --rm -p 5000:5000 \
  -v $(pwd)/config.yaml:/app/data/config.yaml \
  ghcr.io/<github-org-or-user>/idm-logger:latest
```

> Replace `<github-org-or-user>` with your GitHub org/user. The image is built automatically on pushes to `main` and tags starting with `v`.

This project includes a `docker-compose.yml` file to run the Logger, InfluxDB v2, and Grafana in containers.

1.  Clone the repository and cd into it.
2.  **Create the configuration file:**
    ```bash
    cp config.yaml.example config.yaml
    nano config.yaml
    ```
    *You MUST verify the settings, especially `idm.host`.*

3.  Start the stack:
    ```bash
    docker-compose up -d
    ```
4.  Access the services:
    *   **Logger Web UI**: `http://localhost:5000` (Default Login: `admin`)
    *   **Grafana**: `http://localhost:3000` (Login: `admin` / `admin`)
    *   **InfluxDB**: `http://localhost:8086` (User: `admin`, Pass: `adminpassword`, Org: `my-org`, Token: `my-token`)

## Configuration

The configuration file is located at `/opt/idm-logger/config.yaml` (native install) or `./config.yaml` (Docker).

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
