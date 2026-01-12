#!/bin/bash
set -e

echo "InfluxDB v3 initialization script"

# Wait for InfluxDB to be ready
echo "Waiting for InfluxDB to be ready..."
sleep 5

# InfluxDB v3 Core automatically creates databases on first write
# No explicit database creation needed

# The token is configured via environment variable INFLUXDB_TOKEN
# and is persistent across container restarts

echo "InfluxDB v3 initialization complete"
echo "Database: ${INFLUXDB_DATABASE:-idm}"
echo "Token is configured via environment variable"
