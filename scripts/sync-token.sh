#!/bin/bash
# Script to synchronize InfluxDB token across all configuration files

if [ -z "$1" ]; then
    echo "Usage: $0 <new-token>"
    echo "Example: $0 my-new-secure-token"
    exit 1
fi

NEW_TOKEN="$1"
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Synchronizing token to: $NEW_TOKEN"

# 1. Update docker-compose.yml
DOCKER_COMPOSE="$PROJECT_ROOT/docker-compose.yml"
if [ -f "$DOCKER_COMPOSE" ]; then
    echo "Updating $DOCKER_COMPOSE..."
    # Update INFLUX_TOKEN for idm-logger
    sed -i "s/INFLUX_TOKEN=.*/INFLUX_TOKEN=$NEW_TOKEN/" "$DOCKER_COMPOSE"
    # Update INFLUXDB_TOKEN for influxdb
    sed -i "s/INFLUXDB_TOKEN=.*/INFLUXDB_TOKEN=$NEW_TOKEN/" "$DOCKER_COMPOSE"
    # Update INFLUXDB3_AUTH_TOKEN for influxdb (v3 standard)
    sed -i "s/INFLUXDB3_AUTH_TOKEN=.*/INFLUXDB3_AUTH_TOKEN=$NEW_TOKEN/" "$DOCKER_COMPOSE"
else
    echo "Warning: $DOCKER_COMPOSE not found"
fi

# 2. Update Grafana Datasource Provisioning
GRAFANA_PROVISIONING="$PROJECT_ROOT/grafana/provisioning/datasources/influxdb.yaml"
if [ -f "$GRAFANA_PROVISIONING" ]; then
    echo "Updating $GRAFANA_PROVISIONING..."
    sed -i "s/token: .*/token: $NEW_TOKEN/" "$GRAFANA_PROVISIONING"
else
    echo "Warning: $GRAFANA_PROVISIONING not found"
fi

# 3. Update InfluxDB Admin Token File
INFLUX_TOKEN_FILE="$PROJECT_ROOT/influxdb-token/admin_token.txt"
if [ -f "$INFLUX_TOKEN_FILE" ]; then
    echo "Updating $INFLUX_TOKEN_FILE..."
    echo -n "$NEW_TOKEN" > "$INFLUX_TOKEN_FILE"
else
    echo "Warning: $INFLUX_TOKEN_FILE not found. Creating it."
    mkdir -p "$(dirname "$INFLUX_TOKEN_FILE")"
    echo -n "$NEW_TOKEN" > "$INFLUX_TOKEN_FILE"
fi

# 4. Update .env if it exists
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Updating $ENV_FILE..."
    if grep -q "INFLUX_TOKEN" "$ENV_FILE"; then
        sed -i "s/INFLUX_TOKEN=.*/INFLUX_TOKEN=$NEW_TOKEN/" "$ENV_FILE"
    fi
    if grep -q "INFLUXDB_TOKEN" "$ENV_FILE"; then
        sed -i "s/INFLUXDB_TOKEN=.*/INFLUXDB_TOKEN=$NEW_TOKEN/" "$ENV_FILE"
    fi
fi

echo "Token synchronization complete."
echo ""
echo "To apply changes, run:"
echo "  docker compose down"
echo "  docker compose up -d"
echo ""
echo "Note: If volumes are persisted, the database might still hold old tokens."
echo "However, idm-logger is configured to auto-sync from environment variables on startup."
