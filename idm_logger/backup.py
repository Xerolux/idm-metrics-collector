"""Backup and restore functionality for IDM Logger configuration and data."""

import json
import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import config, DATA_DIR
from .db import db

logger = logging.getLogger(__name__)

# Backup directory
BACKUP_DIR = Path(DATA_DIR) / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


class BackupManager:
    """Manages backup and restore operations."""

    @staticmethod
    def create_backup(include_influx_config: bool = True) -> Dict[str, Any]:
        """
        Create a complete backup of the system configuration.

        Args:
            include_influx_config: Whether to include InfluxDB credentials (sensitive data)

        Returns:
            Dict containing backup metadata and file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"idm_backup_{timestamp}.zip"
        backup_path = BACKUP_DIR / backup_name

        try:
            # Collect all data to backup
            backup_data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "hostname": os.environ.get("HOSTNAME", "unknown"),
                    "include_influx_config": include_influx_config
                },
                "config": {},
                "scheduler": {},
                "db_settings": {}
            }

            # 1. Backup configuration (from config.data)
            config_copy = config.data.copy()

            # Optionally remove sensitive InfluxDB data
            if not include_influx_config and "influx" in config_copy:
                influx_copy = config_copy["influx"].copy()
                if "token" in influx_copy:
                    influx_copy["token"] = "***REMOVED***"
                if "password" in influx_copy:
                    influx_copy["password"] = "***REMOVED***"
                config_copy["influx"] = influx_copy

            backup_data["config"] = config_copy

            # 2. Backup scheduler rules (from database)
            try:
                scheduler_data = db.get_setting("scheduler_rules")
                if scheduler_data:
                    backup_data["scheduler"] = json.loads(scheduler_data)
            except Exception as e:
                logger.warning(f"Could not backup scheduler rules: {e}")

            # 3. Backup all other database settings
            try:
                # Get all settings from database
                all_settings = {}
                # Query all settings (implementation depends on your DB structure)
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                for row in cursor.fetchall():
                    key, value = row
                    # Skip config and scheduler (already backed up)
                    if key not in ["config", "scheduler_rules"]:
                        try:
                            all_settings[key] = json.loads(value) if value else None
                        except json.JSONDecodeError:
                            all_settings[key] = value

                backup_data["db_settings"] = all_settings
                conn.close()
            except Exception as e:
                logger.warning(f"Could not backup database settings: {e}")

            # 4. Create ZIP file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main backup data as JSON
                zipf.writestr("backup.json", json.dumps(backup_data, indent=2))

                # Add database file if it exists
                db_path = Path(DATA_DIR) / "idm_logger.db"
                if db_path.exists():
                    zipf.write(db_path, "database/idm_logger.db")

                # Add secret key file
                key_file = Path(DATA_DIR) / ".secret.key"
                if key_file.exists():
                    zipf.write(key_file, "secrets/.secret.key")

            file_size = backup_path.stat().st_size
            logger.info(f"Backup created successfully: {backup_name} ({file_size} bytes)")

            return {
                "success": True,
                "filename": backup_name,
                "path": str(backup_path),
                "size": file_size,
                "created_at": backup_data["metadata"]["created_at"]
            }

        except Exception as e:
            logger.error(f"Backup creation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def restore_backup(backup_file_path: str, restore_secrets: bool = False) -> Dict[str, Any]:
        """
        Restore configuration from a backup file.

        Args:
            backup_file_path: Path to the backup ZIP file
            restore_secrets: Whether to restore secret keys (dangerous!)

        Returns:
            Dict containing restore status and information
        """
        backup_path = Path(backup_file_path)

        if not backup_path.exists():
            return {"success": False, "error": "Backup file not found"}

        try:
            restored_items = []

            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # 1. Extract and load backup.json
                backup_json = zipf.read("backup.json").decode('utf-8')
                backup_data = json.loads(backup_json)

                metadata = backup_data.get("metadata", {})
                logger.info(f"Restoring backup from {metadata.get('created_at', 'unknown date')}")

                # 2. Restore configuration
                if "config" in backup_data:
                    config.data = backup_data["config"]
                    config.save()
                    restored_items.append("configuration")
                    logger.info("Configuration restored")

                # 3. Restore scheduler rules
                if "scheduler" in backup_data and backup_data["scheduler"]:
                    db.set_setting("scheduler_rules", json.dumps(backup_data["scheduler"]))
                    restored_items.append("scheduler_rules")
                    logger.info("Scheduler rules restored")

                # 4. Restore other database settings
                if "db_settings" in backup_data:
                    for key, value in backup_data["db_settings"].items():
                        db.set_setting(key, json.dumps(value) if isinstance(value, (dict, list)) else value)
                    restored_items.append("database_settings")
                    logger.info("Database settings restored")

                # 5. Optionally restore secret key (DANGEROUS!)
                if restore_secrets and "secrets/.secret.key" in zipf.namelist():
                    key_file = Path(DATA_DIR) / ".secret.key"
                    with open(key_file, 'wb') as f:
                        f.write(zipf.read("secrets/.secret.key"))
                    os.chmod(key_file, 0o600)
                    restored_items.append("secret_key")
                    logger.warning("Secret key restored - this may cause encryption issues!")

            # Reload configuration
            config.reload()

            return {
                "success": True,
                "restored_items": restored_items,
                "metadata": metadata,
                "message": f"Successfully restored: {', '.join(restored_items)}"
            }

        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def list_backups() -> list:
        """List all available backups."""
        backups = []

        try:
            for backup_file in sorted(BACKUP_DIR.glob("idm_backup_*.zip"), reverse=True):
                try:
                    stat = backup_file.stat()

                    # Try to read metadata from backup
                    metadata = None
                    try:
                        with zipfile.ZipFile(backup_file, 'r') as zipf:
                            if "backup.json" in zipf.namelist():
                                backup_json = zipf.read("backup.json").decode('utf-8')
                                backup_data = json.loads(backup_json)
                                metadata = backup_data.get("metadata", {})
                    except (zipfile.BadZipFile, json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
                        logger.debug(f"Could not read metadata from {backup_file.name}: {e}")

                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "metadata": metadata
                    })
                except Exception as e:
                    logger.warning(f"Could not read backup {backup_file}: {e}")

        except Exception as e:
            logger.error(f"Could not list backups: {e}")

        return backups

    @staticmethod
    def delete_backup(filename: str) -> Dict[str, Any]:
        """Delete a backup file."""
        backup_path = BACKUP_DIR / filename

        if not backup_path.exists():
            return {"success": False, "error": "Backup file not found"}

        # Security check: ensure filename is safe
        if ".." in filename or "/" in filename or "\\" in filename:
            return {"success": False, "error": "Invalid filename"}

        try:
            backup_path.unlink()
            logger.info(f"Backup deleted: {filename}")
            return {"success": True, "message": f"Backup {filename} deleted"}
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def cleanup_old_backups(keep_count: int = 10) -> Dict[str, Any]:
        """
        Keep only the most recent N backups, delete older ones.

        Args:
            keep_count: Number of backups to keep
        """
        try:
            backups = sorted(BACKUP_DIR.glob("idm_backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)

            deleted_count = 0
            if len(backups) > keep_count:
                for backup_file in backups[keep_count:]:
                    try:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Cleaned up old backup: {backup_file.name}")
                    except Exception as e:
                        logger.warning(f"Could not delete old backup {backup_file}: {e}")

            return {
                "success": True,
                "kept": min(len(backups), keep_count),
                "deleted": deleted_count
            }
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def export_influxdb_config() -> Dict[str, Any]:
        """Export InfluxDB configuration for manual backup."""
        try:
            influx_config = config.data.get("influx", {}).copy()

            # Create export data
            export_data = {
                "influxdb_config": influx_config,
                "exported_at": datetime.now().isoformat()
            }

            return {
                "success": True,
                "data": export_data
            }
        except Exception as e:
            logger.error(f"InfluxDB config export failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience instance
backup_manager = BackupManager()
