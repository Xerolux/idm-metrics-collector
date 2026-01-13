# InfluxDB v3 Migration Guide

## Overview

This project has been migrated from InfluxDB v2 to InfluxDB v3 Core. This document describes the changes and how to migrate existing installations.

## What Changed

### InfluxDB v3 Core Features

- **Docker Image**: Changed from `influxdb:2.7` to `influxdb:3-core`
- **Port**: Changed from `8086` to `8181`
- **Query Language**: SQL instead of Flux
- **Configuration**: Simplified - no more org/bucket, just database name
- **Authentication**: Token-based (consistent with v2)
- **Auto-creation**: Database is automatically created on first write

### Code Changes

1. **Python Client**: Migrated from `influxdb-client` to `influxdb3-python`
2. **Configuration**: Removed `org` and `bucket`, replaced with `database`
3. **Environment Variables**:
   - `INFLUX_ORG` → removed
   - `INFLUX_BUCKET` → `INFLUX_DATABASE`
4. **Grafana**: Updated datasource configuration to use SQL query language

## Migration Steps

### For New Installations

Simply deploy using the updated `docker-compose.yml`. Everything will be set up automatically.

### For Existing Installations

**⚠️ IMPORTANT: Backup your data first!**

1. **Stop the stack**:
   ```bash
   cd /opt/idm-metrics-collector
   docker compose down
   ```

2. **Backup your InfluxDB v2 data** (optional but recommended):
   ```bash
   docker run --rm -v idm-influxdb-data:/data -v $(pwd):/backup \
     alpine tar czf /backup/influxdb-v2-backup.tar.gz /data
   ```

3. **Remove old InfluxDB volumes** (⚠️ this will delete all data):
   ```bash
   docker volume rm idm-influxdb-data idm-influxdb-config
   ```

4. **Pull the latest changes**:
   ```bash
   git pull origin main
   ```

5. **Start the new stack**:
   ```bash
   docker compose up -d
   ```

6. **Verify services are running**:
   ```bash
   docker compose ps
   docker compose logs influxdb
   ```

### Configuration Changes

The configuration format has changed. Old format:

```yaml
influx:
  version: 2
  url: "http://localhost:8086"
  org: "my-org"
  bucket: "idm"
  token: "my-token"
```

New format:

```yaml
influx:
  url: "http://localhost:8181"
  database: "idm"
  token: "my-token"
```

The system will automatically migrate the configuration on first start.

## Accessing Services

### InfluxDB v3

- **URL**: `http://localhost:8181`
- **Database**: `idm` (auto-created on first write)
- **Token**: `my-super-secret-token-change-me` (change this!)
- **Query Language**: SQL

Example query:
```sql
SELECT * FROM idm_heatpump
WHERE time > now() - INTERVAL '1 hour'
ORDER BY time DESC
LIMIT 100
```

### Grafana

The Grafana datasource has been updated to use InfluxDB v3 with SQL queries. Existing dashboards may need to be updated if they use Flux queries.

To update a dashboard:
1. Open the dashboard in edit mode
2. Change queries from Flux to SQL format
3. Example SQL query:
   ```sql
   SELECT
     time,
     temperature_outdoor,
     temperature_flow
   FROM idm_heatpump
   WHERE time > $__timeFrom()
   ORDER BY time ASC
   ```

## Token Management

The token is configured via environment variables and persists across container restarts. The token is stored in:

1. `docker-compose.yml` - `INFLUXDB_TOKEN` environment variable
2. Application configuration - synced automatically
3. Grafana datasource configuration - `grafana/provisioning/datasources/influxdb.yaml`

**Important**: Keep the token consistent across all services:
- InfluxDB container
- IDM Logger container
- Grafana datasource configuration

### Automatic Token Generation

For new installations, the install script automatically generates a secure random token:

```bash
./scripts/generate-token.sh
```

This script will:
1. Generate a cryptographically secure random token (64 hex characters)
2. Update all configuration files automatically
3. Create backups of original files
4. Display the new token for your records

**Manual Token Generation:**

If you need to generate a new token manually:

```bash
cd /opt/idm-metrics-collector
./scripts/generate-token.sh
```

Then restart all services:

```bash
docker compose down
docker compose up -d
```

**Important Security Notes:**
- Each installation should use a unique token
- Never commit tokens to version control
- Store the token securely (password manager recommended)
- The token provides full read/write access to InfluxDB

## Troubleshooting

### Connection Issues

If you see connection errors, check:

1. Port is correct (8181 not 8086)
2. Token matches across all services
3. Database name is correct

```bash
# Check InfluxDB logs
docker compose logs influxdb

# Check application logs
docker compose logs idm-logger

# Test InfluxDB health
curl http://localhost:8181/health
```

### Query Migration

Flux queries need to be converted to SQL. Common patterns:

**Flux**:
```flux
from(bucket: "idm")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "idm_heatpump")
```

**SQL**:
```sql
SELECT * FROM idm_heatpump
WHERE time > now() - INTERVAL '1 hour'
```

## Benefits of v3

1. **Better Performance**: Improved query performance and data ingestion
2. **SQL Support**: Standard SQL queries instead of Flux
3. **Simplified Setup**: No more org/bucket complexity
4. **Modern Architecture**: Built on Apache Arrow and DataFusion
5. **Better Grafana Integration**: Native SQL support in Grafana

## Support

For issues or questions:
- GitHub Issues: https://github.com/Xerolux/idm-metrics-collector/issues
- Community: https://community.simon42.com

## Dashboard Migration

All Grafana dashboards have been converted from Flux to SQL queries. Use the conversion script to update custom dashboards:

```bash
python3 scripts/convert-dashboards-to-sql.py
```

The script will:
- Convert all Flux queries to SQL
- Create backups with `.flux-backup` extension
- Update dashboards in place

**Common SQL Query Patterns:**

```sql
-- Get latest values
SELECT time, temperature_outdoor
FROM idm_heatpump
WHERE time > now() - INTERVAL '1 hour'
ORDER BY time DESC
LIMIT 1

-- Time series data
SELECT time, temperature_flow, temperature_return
FROM idm_heatpump
WHERE time >= $__timeFrom() AND time <= $__timeTo()
ORDER BY time ASC

-- Aggregated data
SELECT
  time_bucket('5 minutes', time) AS time,
  AVG(power_current) AS avg_power
FROM idm_heatpump
WHERE time > now() - INTERVAL '24 hours'
GROUP BY time_bucket('5 minutes', time)
ORDER BY time ASC
```

## References

- [InfluxDB v3 Documentation](https://docs.influxdata.com/influxdb3/core/)
- [Python Client for InfluxDB v3](https://github.com/InfluxCommunity/influxdb3-python)
- [Grafana InfluxDB v3 Data Source](https://grafana.com/docs/grafana/latest/datasources/influxdb/)
- [InfluxDB v3 SQL Reference](https://docs.influxdata.com/influxdb3/core/reference/sql/)
