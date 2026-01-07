#!/bin/bash
set -e

INSTALL_DIR="/opt/idm-logger"
SERVICE_FILE="/etc/systemd/system/idm-logger.service"

echo "Installing IDM Logger..."

# Function to install InfluxDB (OSS)
install_influxdb() {
    echo "Installing InfluxDB v2..."
    # Add key
    wget -q https://repos.influxdata.com/influxdata-archive_compat.key
    echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
    echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | tee /etc/apt/sources.list.d/influxdata.list
    rm influxdata-archive_compat.key

    apt-get update
    apt-get install -y influxdb2
    systemctl enable --now influxdb
    echo "InfluxDB installed. Run 'influx setup' to configure it initially."
}

# Function to install Grafana (OSS)
install_grafana() {
    echo "Installing Grafana..."
    apt-get install -y apt-transport-https software-properties-common wget
    mkdir -p /etc/apt/keyrings/
    wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | tee /etc/apt/keyrings/grafana.gpg > /dev/null
    echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | tee /etc/apt/sources.list.d/grafana.list

    apt-get update
    apt-get install -y grafana
    systemctl enable --now grafana-server
    echo "Grafana installed. Access at http://localhost:3000 (admin/admin)"
}

# Install system dependencies for logger
echo "Installing Python dependencies..."
apt-get update
apt-get install -y python3-venv wget gpg

# Create install directory
mkdir -p "$INSTALL_DIR"
cp -r idm_logger requirements.txt "$INSTALL_DIR"

# Create config if not exists
if [ ! -f "$INSTALL_DIR/config.yaml" ]; then
    echo "Creating default config.yaml..."
    cat <<EOF > "$INSTALL_DIR/config.yaml"
idm:
  host: "192.168.1.100"
  port: 502
  circuits: ["A"] # Enable heating circuits (A, B, C, etc.)
influx:
  version: 2
  url: "http://localhost:8086"
  org: "my-org"
  bucket: "idm"
  token: "my-token"
web:
  enabled: true
  port: 5000
logging:
  interval: 60
  level: "INFO"
EOF
fi

# Create virtual environment and install deps
echo "Setting up virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Install service
cp idm-logger.service "$SERVICE_FILE"
systemctl daemon-reload
systemctl enable idm-logger.service

# Interactive installation of extras
read -p "Do you want to install InfluxDB (locally)? [y/N] " install_influx
if [[ "$install_influx" =~ ^[Yy]$ ]]; then
    install_influxdb
fi

read -p "Do you want to install Grafana (locally)? [y/N] " install_grafana
if [[ "$install_grafana" =~ ^[Yy]$ ]]; then
    install_grafana
fi

echo "Installation complete."
echo "Edit $INSTALL_DIR/config.yaml and run 'systemctl start idm-logger'"
