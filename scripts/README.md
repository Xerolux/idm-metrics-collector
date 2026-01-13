# Scripts Directory

This directory contains utility scripts for managing the IDM Metrics Collector.

## Available Scripts

### 1. generate-token.sh

**Purpose:** Generate a secure random token for InfluxDB v3 authentication

**Usage:**
```bash
./scripts/generate-token.sh
```

**What it does:**
- Generates a cryptographically secure 64-character hex token
- Updates all configuration files automatically:
  - `docker-compose.yml`
  - `docker-compose.dev.yml`
  - `grafana/provisioning/datasources/influxdb.yaml`
  - `README.md`
  - `MIGRATION_V3.md`
- Creates timestamped backups of modified files
- Displays the new token for your records

**When to use:**
- During initial installation (automatically called by install.sh)
- When rotating tokens for security
- When setting up a new deployment

**Important:**
- Save the generated token securely
- The token provides full read/write access to InfluxDB
- All services must use the same token

---

### 2. convert-dashboards-to-sql.py

**Purpose:** Convert Grafana dashboards from Flux queries to SQL queries for InfluxDB v3

**Usage:**
```bash
python3 scripts/convert-dashboards-to-sql.py
```

**What it does:**
- Scans all JSON dashboard files in `grafana/dashboards/`
- Converts Flux queries to equivalent SQL queries
- Creates `.flux-backup` files before modifying
- Updates dashboards in place

**Conversion examples:**

**Flux:**
```flux
from(bucket: "idm")
  |> range(start: -1h)
  |> filter(fn: (r) => r._field == "temp_outside")
  |> last()
```

**SQL:**
```sql
SELECT time, temp_outside
FROM idm_heatpump
WHERE time > now() - INTERVAL '1 hour'
ORDER BY time DESC
LIMIT 1
```

**When to use:**
- During migration from InfluxDB v2 to v3
- When importing custom dashboards with Flux queries
- To update dashboards after Flux query changes

---

### 3. influxdb-init.sh

**Purpose:** InfluxDB v3 initialization script (currently minimal)

**Usage:** Automatically executed by Docker on container startup

**What it does:**
- Validates InfluxDB v3 environment
- Logs initialization status
- Database is auto-created on first write (no explicit creation needed)

**Note:** InfluxDB v3 Core automatically creates databases, so minimal initialization is required.

---

## Security Best Practices

1. **Token Management:**
   - Generate unique tokens for each installation
   - Never commit tokens to version control
   - Use `.gitignore` to exclude token files
   - Rotate tokens periodically for production systems

2. **Backup Strategy:**
   - All scripts create backups before modifying files
   - Backups are timestamped for easy identification
   - Review backups before deletion

3. **Environment Variables:**
   - Tokens are stored as environment variables in docker-compose
   - Override via `.env` file for local development
   - Use secrets management for production deployments

## Troubleshooting

### Token Generation Fails

**Problem:** `openssl rand -hex 32` fails

**Solution:**
```bash
# Check if openssl is installed
which openssl

# Install if missing (Debian/Ubuntu)
sudo apt-get install openssl

# Install if missing (RHEL/CentOS)
sudo yum install openssl
```

### Dashboard Conversion Issues

**Problem:** Queries not converting correctly

**Solution:**
1. Check the `.flux-backup` files for original queries
2. Manually review and adjust SQL queries
3. Test queries in Grafana query editor
4. Report issues with examples to GitHub

### Permission Denied

**Problem:** Scripts not executable

**Solution:**
```bash
chmod +x scripts/*.sh
```

## Development

### Adding New Scripts

1. Place script in `scripts/` directory
2. Make it executable: `chmod +x scripts/your-script.sh`
3. Add documentation to this README
4. Test in clean environment
5. Update `.gitignore` if needed

### Testing Scripts

```bash
# Dry-run mode (if supported)
./scripts/generate-token.sh --dry-run

# Test in Docker container
docker run --rm -v $(pwd):/app -w /app python:3.11-slim \
  python3 scripts/convert-dashboards-to-sql.py
```

## See Also

- [MIGRATION_V3.md](../MIGRATION_V3.md) - Complete migration guide
- [README.md](../README.md) - Main project documentation
- [docker-compose.yml](../docker-compose.yml) - Service configuration
