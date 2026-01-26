# SPDX-License-Identifier: MIT
"""
Database and configuration migrations for multi-heatpump support.

This module handles the migration from single-device to multi-device
configuration. It should be called during application startup.

Migration flow:
1. Check if migration is needed (no heatpumps in DB but config.idm.host exists)
2. Create a legacy heatpump entry from the existing config
3. Associate existing jobs/alerts with the legacy heatpump
4. Mark migration as complete
"""

import json
import logging
import time
from typing import Optional

from .db import db

logger = logging.getLogger(__name__)

# Migration flag key in settings
MIGRATION_KEY = "multi_heatpump_migrated"
LEGACY_HEATPUMP_ID = "hp-legacy"


def needs_migration() -> bool:
    """
    Check if migration from single to multi-heatpump is needed.

    Returns:
        True if migration should be performed
    """
    # Check if already migrated
    migrated = db.get_setting(MIGRATION_KEY)
    if migrated == "true":
        return False

    # Check if there are any heatpumps configured
    heatpumps = db.get_heatpumps()
    if heatpumps:
        # Already have heatpumps, mark as migrated
        db.set_setting(MIGRATION_KEY, "true")
        return False

    # Check if there's existing config to migrate
    config_raw = db.get_setting("config")
    if not config_raw:
        # No config at all, nothing to migrate
        db.set_setting(MIGRATION_KEY, "true")
        return False

    try:
        config = json.loads(config_raw)
        idm_config = config.get("idm", {})
        if idm_config.get("host"):
            # Has IDM config with host - needs migration
            return True
    except json.JSONDecodeError:
        pass

    # No valid config to migrate
    db.set_setting(MIGRATION_KEY, "true")
    return False


def migrate_single_to_multi() -> Optional[str]:
    """
    Migrate existing single-device configuration to multi-device.

    This creates a new heatpump entry from the existing idm config
    and associates existing jobs/alerts with it.

    Returns:
        The ID of the created heatpump, or None if nothing to migrate
    """
    logger.info("Starting migration from single to multi-heatpump configuration")

    # Load existing config
    config_raw = db.get_setting("config")
    if not config_raw:
        logger.warning("No config found to migrate")
        db.set_setting(MIGRATION_KEY, "true")
        return None

    try:
        config = json.loads(config_raw)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config: {e}")
        return None

    idm_config = config.get("idm", {})
    host = idm_config.get("host")

    if not host:
        logger.info("No IDM host configured, skipping migration")
        db.set_setting(MIGRATION_KEY, "true")
        return None

    # Create legacy heatpump entry
    heatpump_name = config.get("heatpump_model", "IDM Wärmepumpe")
    if not heatpump_name:
        heatpump_name = "IDM Wärmepumpe (Migriert)"

    hp_data = {
        "id": LEGACY_HEATPUMP_ID,
        "name": heatpump_name,
        "manufacturer": "idm",
        "model": "navigator_2_0",
        "connection_config": {
            "host": host,
            "port": idm_config.get("port", 502),
            "unit_id": 1,
            "timeout": 10,
        },
        "device_config": {
            "circuits": idm_config.get("circuits", ["A"]),
            "zones": idm_config.get("zones", []),
        },
        "enabled": True,
    }

    try:
        hp_id = db.add_heatpump(hp_data)
        logger.info(f"Created legacy heatpump {hp_id} from existing config")
    except Exception as e:
        logger.error(f"Failed to create legacy heatpump: {e}")
        return None

    # Update existing jobs to use the legacy heatpump
    try:
        jobs = db.get_jobs()
        for job in jobs:
            job_id = job["id"] if isinstance(job, dict) else job[0]
            db.update_job(job_id, {"heatpump_id": hp_id})
        logger.info(f"Associated {len(jobs)} jobs with legacy heatpump")
    except Exception as e:
        logger.warning(f"Failed to update jobs: {e}")

    # Update existing alerts to use the legacy heatpump
    try:
        alerts = db.get_alerts()
        for alert in alerts:
            alert_id = alert.get("id") if isinstance(alert, dict) else alert[0]
            db.update_alert(alert_id, {"heatpump_id": hp_id})
        logger.info(f"Associated {len(alerts)} alerts with legacy heatpump")
    except Exception as e:
        logger.warning(f"Failed to update alerts: {e}")

    # Create default dashboard for the legacy heatpump
    try:
        from .manufacturers import ManufacturerRegistry

        driver = ManufacturerRegistry.get_driver("idm", "navigator_2_0")
        if driver:
            template = driver.get_dashboard_template()
            dashboard = {
                "name": template.get("name", "IDM Wärmepumpe Dashboard"),
                "heatpump_id": hp_id,
                "config": template,
                "position": 0,
            }
            db.add_dashboard(dashboard)
            logger.info("Created default dashboard for legacy heatpump")
    except Exception as e:
        logger.warning(f"Failed to create dashboard: {e}")

    # Mark migration as complete
    db.set_setting(MIGRATION_KEY, "true")
    logger.info("Migration to multi-heatpump completed successfully")

    return hp_id


def run_migration():
    """
    Run migration if needed.

    This is the main entry point that should be called at startup.
    """
    if needs_migration():
        return migrate_single_to_multi()
    return None


def get_legacy_heatpump_id() -> Optional[str]:
    """
    Get the ID of the legacy heatpump if it exists.

    This is useful for backwards compatibility in APIs.
    """
    hp = db.get_heatpump(LEGACY_HEATPUMP_ID)
    if hp:
        return LEGACY_HEATPUMP_ID

    # If no legacy, return the first heatpump
    heatpumps = db.get_heatpumps()
    if heatpumps:
        return heatpumps[0]["id"]

    return None


def get_default_heatpump_id() -> Optional[str]:
    """
    Get the default heatpump ID for APIs that don't specify one.

    Priority:
    1. Legacy heatpump if exists
    2. First enabled heatpump
    3. First heatpump
    4. None
    """
    # Try legacy first
    if db.get_heatpump(LEGACY_HEATPUMP_ID):
        return LEGACY_HEATPUMP_ID

    # Try first enabled
    enabled = db.get_enabled_heatpumps()
    if enabled:
        return enabled[0]["id"]

    # Try any heatpump
    all_hp = db.get_heatpumps()
    if all_hp:
        return all_hp[0]["id"]

    return None
