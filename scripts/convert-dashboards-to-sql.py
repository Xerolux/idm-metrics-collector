#!/usr/bin/env python3
"""
Convert Grafana dashboards from InfluxDB Flux queries to SQL queries for v3.
"""
import json
import re
import sys
from pathlib import Path


def flux_to_sql(flux_query, time_range="$__timeFrom()"):
    """
    Convert a Flux query to SQL for InfluxDB v3.

    Common patterns:
    - from(bucket: "idm") → FROM idm_heatpump
    - range(start: -1h) → WHERE time > now() - INTERVAL '1 hour'
    - filter(fn: (r) => r._field == "temp_outside") → SELECT temp_outside
    - last() → ORDER BY time DESC LIMIT 1
    """

    # Extract field name from filter
    field_match = re.search(r'r\._field == "([^"]+)"', flux_query)
    if not field_match:
        # Try without quotes
        field_match = re.search(r'r\._field == ([^\)]+)', flux_query)

    if not field_match:
        return None

    field_name = field_match.group(1)

    # Determine time range
    range_match = re.search(r'range\(start: -([^)]+)\)', flux_query)
    if range_match:
        duration = range_match.group(1)
        # Convert duration to SQL interval
        if duration == "1h":
            interval = "1 hour"
        elif duration == "24h" or duration == "1d":
            interval = "1 day"
        elif duration == "7d":
            interval = "7 days"
        elif duration == "14d":
            interval = "14 days"
        elif duration == "30d" or duration == "1mo":
            interval = "30 days"
        elif duration == "90d" or duration == "3mo":
            interval = "90 days"
        elif duration == "180d" or duration == "6mo":
            interval = "180 days"
        elif duration == "365d" or duration == "1y":
            interval = "365 days"
        else:
            interval = duration.replace("h", " hour").replace("d", " day")

        time_filter = f"time > now() - INTERVAL '{interval}'"
    else:
        # Use Grafana variables for time range
        time_filter = f"time >= $__timeFrom() AND time <= $__timeTo()"

    # Check if it's a last() query (single value)
    if "last()" in flux_query or "lastNotNull" in flux_query:
        sql = f"SELECT time, {field_name} FROM idm_heatpump WHERE {time_filter} ORDER BY time DESC LIMIT 1"
    else:
        # Time series query
        sql = f"SELECT time, {field_name} FROM idm_heatpump WHERE {time_filter} ORDER BY time ASC"

    return sql


def convert_panel(panel):
    """Convert a single panel's queries from Flux to SQL."""
    if "targets" not in panel:
        return False

    modified = False
    for target in panel["targets"]:
        if "query" in target and "from(bucket:" in target["query"]:
            flux_query = target["query"]
            sql_query = flux_to_sql(flux_query)

            if sql_query:
                target["query"] = sql_query
                # Update query language hint if present
                if "language" in target:
                    target["language"] = "sql"
                modified = True
                print(f"  Converted query: {field_name if (field_name := re.search(r'SELECT time, ([^ ]+)', sql_query)) else 'unknown'}")

    # Recursively handle nested panels
    if "panels" in panel:
        for nested_panel in panel["panels"]:
            if convert_panel(nested_panel):
                modified = True

    return modified


def convert_dashboard(dashboard_path):
    """Convert a dashboard file from Flux to SQL queries."""
    print(f"\nConverting: {dashboard_path.name}")

    with open(dashboard_path, 'r') as f:
        dashboard = json.load(f)

    # Convert all panels
    modified = False
    if "panels" in dashboard:
        for panel in dashboard["panels"]:
            if convert_panel(panel):
                modified = True

    if modified:
        # Backup original
        backup_path = dashboard_path.with_suffix('.json.flux-backup')
        if not backup_path.exists():
            print(f"  Creating backup: {backup_path.name}")
            with open(backup_path, 'w') as f:
                json.dump(dashboard, f, indent=2)

        # Write converted dashboard
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard, f, indent=2)

        print(f"  ✓ Converted successfully")
        return True
    else:
        print(f"  - No Flux queries found")
        return False


def main():
    """Convert all dashboards in the grafana/dashboards directory."""
    script_dir = Path(__file__).parent
    dashboards_dir = script_dir.parent / "grafana" / "dashboards"

    if not dashboards_dir.exists():
        print(f"Error: Dashboards directory not found: {dashboards_dir}")
        sys.exit(1)

    print("=" * 60)
    print("Grafana Dashboard Converter: Flux → SQL (InfluxDB v3)")
    print("=" * 60)

    dashboard_files = list(dashboards_dir.glob("*.json"))
    if not dashboard_files:
        print("No dashboard files found.")
        sys.exit(0)

    print(f"\nFound {len(dashboard_files)} dashboard(s)")

    converted = 0
    for dashboard_file in sorted(dashboard_files):
        if convert_dashboard(dashboard_file):
            converted += 1

    print("\n" + "=" * 60)
    print(f"Conversion complete: {converted}/{len(dashboard_files)} dashboard(s) converted")
    print("=" * 60)
    print("\nBackups saved with .flux-backup extension")
    print("Review changes and test dashboards in Grafana before deployment.")


if __name__ == "__main__":
    main()
