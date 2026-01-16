"""Backup and restore functionality for IDM Logger configuration and data."""

import json
import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .config import config, DATA_DIR
from .db import db
try:
    from webdav4.client import Client as WebDavClient
    WEBDAV_AVAILABLE = True
except ImportError:
    WEBDAV_AVAILABLE = False

logger = logging.getLogger(__name__)

# Backup directory
BACKUP_DIR = Path(DATA_DIR) / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


class BackupManager:
    """Manages backup and restore operations."""

    @staticmethod
    def create_backup() -> Dict[str, Any]:
        """
        Create a complete backup of the system configuration.

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
                },
                "config": {},
                "scheduler": {},
                "db_settings": {},
            }

            # 1. Backup configuration (from config.data)
            config_copy = config.data.copy()
            backup_data["config"] = config_copy

            # 2. Backup all database settings (including scheduler rules)
            try:
                # Get all settings from database
                all_settings = {}
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                for row in cursor.fetchall():
                    key, value = row

                    # Handle scheduler_rules specifically
                    if key == "scheduler_rules":
                        try:
                            if value:
                                backup_data["scheduler"] = json.loads(value)
                        except Exception as e:
                            logger.warning(f"Could not backup scheduler rules: {e}")
                        continue

                    # Skip config (already backed up from memory)
                    if key == "config":
                        continue

                    # All other settings
                    try:
                        all_settings[key] = json.loads(value) if value else None
                    except json.JSONDecodeError:
                        all_settings[key] = value

                backup_data["db_settings"] = all_settings
                conn.close()
            except Exception as e:
                logger.warning(f"Could not backup database settings: {e}")

            # 4. Create ZIP file
            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
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

                # Add AI anomaly state file
                ai_file = Path(DATA_DIR) / "anomaly_state.json"
                if ai_file.exists():
                    zipf.write(ai_file, "ai/anomaly_state.json")

            file_size = backup_path.stat().st_size
            logger.info(
                f"Backup created successfully: {backup_name} ({file_size} bytes)"
            )

            # Upload to WebDAV if enabled
            webdav_result = None
            if config.get("webdav.enabled", False):
                logger.info("Auto-uploading backup to WebDAV...")
                webdav_result = self.upload_to_webdav(str(backup_path))

            return {
                "success": True,
                "filename": backup_name,
                "path": str(backup_path),
                "size": file_size,
                "created_at": backup_data["metadata"]["created_at"],
                "webdav_upload": webdav_result
            }

        except Exception as e:
            logger.error(f"Backup creation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    @staticmethod
    def restore_backup(
        backup_file_path: str, restore_secrets: bool = False
    ) -> Dict[str, Any]:
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

            with zipfile.ZipFile(backup_path, "r") as zipf:
                # 1. Extract and load backup.json
                backup_json = zipf.read("backup.json").decode("utf-8")
                backup_data = json.loads(backup_json)

                metadata = backup_data.get("metadata", {})
                logger.info(
                    f"Restoring backup from {metadata.get('created_at', 'unknown date')}"
                )

                # 2. Restore configuration
                if "config" in backup_data:
                    config.data = backup_data["config"]
                    config.save()
                    restored_items.append("configuration")
                    logger.info("Configuration restored")

                # 3. Restore scheduler rules
                if "scheduler" in backup_data and backup_data["scheduler"]:
                    db.set_setting(
                        "scheduler_rules", json.dumps(backup_data["scheduler"])
                    )
                    restored_items.append("scheduler_rules")
                    logger.info("Scheduler rules restored")

                # 4. Restore other database settings
                if "db_settings" in backup_data:
                    for key, value in backup_data["db_settings"].items():
                        db.set_setting(
                            key,
                            json.dumps(value)
                            if isinstance(value, (dict, list))
                            else value,
                        )
                    restored_items.append("database_settings")
                    logger.info("Database settings restored")

                # 5. Optionally restore secret key (DANGEROUS!)
                if restore_secrets and "secrets/.secret.key" in zipf.namelist():
                    key_file = Path(DATA_DIR) / ".secret.key"
                    with open(key_file, "wb") as f:
                        f.write(zipf.read("secrets/.secret.key"))
                    os.chmod(key_file, 0o600)
                    restored_items.append("secret_key")
                    logger.warning(
                        "Secret key restored - this may cause encryption issues!"
                    )

                # 6. Restore AI state
                if "ai/anomaly_state.json" in zipf.namelist():
                    ai_file = Path(DATA_DIR) / "anomaly_state.json"
                    with open(ai_file, "wb") as f:
                        f.write(zipf.read("ai/anomaly_state.json"))
                    restored_items.append("ai_model")
                    logger.info("AI Model state restored")

            # Reload configuration
            config.reload()

            return {
                "success": True,
                "restored_items": restored_items,
                "metadata": metadata,
                "message": f"Successfully restored: {', '.join(restored_items)}",
            }

        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_backups() -> list:
        """List all available backups."""
        backups = []

        try:
            for backup_file in sorted(
                BACKUP_DIR.glob("idm_backup_*.zip"), reverse=True
            ):
                try:
                    stat = backup_file.stat()

                    # Try to read metadata from backup
                    metadata = None
                    try:
                        with zipfile.ZipFile(backup_file, "r") as zipf:
                            if "backup.json" in zipf.namelist():
                                backup_json = zipf.read("backup.json").decode("utf-8")
                                backup_data = json.loads(backup_json)
                                metadata = backup_data.get("metadata", {})
                    except (
                        zipfile.BadZipFile,
                        json.JSONDecodeError,
                        KeyError,
                        UnicodeDecodeError,
                    ) as e:
                        logger.debug(
                            f"Could not read metadata from {backup_file.name}: {e}"
                        )

                    backups.append(
                        {
                            "filename": backup_file.name,
                            "path": str(backup_file),
                            "size": stat.st_size,
                            "created_at": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "metadata": metadata,
                        }
                    )
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
            backups = sorted(
                BACKUP_DIR.glob("idm_backup_*.zip"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            deleted_count = 0
            if len(backups) > keep_count:
                for backup_file in backups[keep_count:]:
                    try:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Cleaned up old backup: {backup_file.name}")
                    except Exception as e:
                        logger.warning(
                            f"Could not delete old backup {backup_file}: {e}"
                        )

            return {
                "success": True,
                "kept": min(len(backups), keep_count),
                "deleted": deleted_count,
            }
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def upload_to_webdav(file_path: str) -> Dict[str, Any]:
        """Upload a file to WebDAV/Nextcloud."""
        if not WEBDAV_AVAILABLE:
            return {"success": False, "error": "WebDAV library not available"}

        try:
            url = config.get("webdav.url")
            username = config.get("webdav.username")
            password = config.get("webdav.password")

            if not url or not username:
                return {"success": False, "error": "WebDAV not configured"}

            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}

            client = WebDavClient(base_url=url, auth=(username, password))

            # Check connection
            try:
                client.exists("/")
            except Exception as e:
                 # Try adding /remote.php/dav/files/USER/ if it's Nextcloud and failed
                 # But we assume user provides full URL for now
                 return {"success": False, "error": f"Connection failed: {e}"}

            remote_path = f"/{path.name}"
            # Nextcloud/WebDAV often requires the directory to exist or precise path
            # We upload to root of WebDAV share

            client.upload_file(file_path, remote_path, overwrite=True)
            logger.info(f"Successfully uploaded {path.name} to WebDAV")

            return {"success": True, "message": "Upload successful"}

        except Exception as e:
            logger.error(f"WebDAV upload failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience instance
backup_manager = BackupManager()
