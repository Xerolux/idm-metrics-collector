#!/bin/bash
set -e

#
# Token Generator for InfluxDB v3 Installation
# Generates a secure random token and updates all configuration files
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}InfluxDB v3 Token Generator${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Generate a secure random token (32 bytes = 64 hex characters)
echo -e "${YELLOW}Generating secure random token...${NC}"
NEW_TOKEN=$(openssl rand -hex 32)

if [ -z "$NEW_TOKEN" ]; then
    echo -e "${RED}ERROR: Failed to generate token${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Token generated successfully${NC}"
echo ""

# Function to update token in file
update_token_in_file() {
    local file="$1"
    local old_token="my-super-secret-token-change-me"

    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}  - Skipping (file not found): $file${NC}"
        return
    fi

    # Check if file contains the default token
    if grep -q "$old_token" "$file"; then
        # Create backup
        cp "$file" "$file.backup-$(date +%Y%m%d-%H%M%S)"

        # Replace token
        sed -i "s/${old_token}/${NEW_TOKEN}/g" "$file"
        echo -e "${GREEN}  ✓ Updated: $(basename $file)${NC}"
    else
        echo -e "${YELLOW}  - Skipping (no default token found): $(basename $file)${NC}"
    fi
}

echo -e "${YELLOW}Updating configuration files...${NC}"
echo ""

# Update docker-compose.yml
update_token_in_file "$PROJECT_ROOT/docker-compose.yml"

# Update docker-compose.dev.yml
update_token_in_file "$PROJECT_ROOT/docker-compose.dev.yml"

# Update Grafana datasource
update_token_in_file "$PROJECT_ROOT/grafana/provisioning/datasources/influxdb.yaml"

# Update README (just for display)
update_token_in_file "$PROJECT_ROOT/README.md"

# Update MIGRATION guide
update_token_in_file "$PROJECT_ROOT/MIGRATION_V3.md"

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Token update complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${YELLOW}Your new InfluxDB token:${NC}"
echo -e "${GREEN}${NEW_TOKEN}${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "1. Save this token securely - you'll need it to configure clients"
echo "2. All configuration files have been updated automatically"
echo "3. Backups of original files were created with timestamp"
echo "4. Use this same token across all deployments to maintain consistency"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the updated configuration files"
echo "2. Deploy using: docker compose up -d"
echo "3. Access InfluxDB at: http://localhost:8181"
echo ""
echo -e "${RED}WARNING: Keep this token secret!${NC}"
echo -e "${RED}Anyone with this token can read/write data to your InfluxDB instance.${NC}"
echo ""
