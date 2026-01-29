# SPDX-License-Identifier: MIT
"""Backup and restore functionality for IDM Logger configuration and data."""

import json
import logging
import os
import re
import zipfile
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import requests
import threading

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

# Track if default credentials warning was shown
_default_creds_warned = False

# Pattern for safe filenames (alphanumeric, dash, underscore only)
_SAFE_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")


def _sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    Prevents path traversal attacks and invalid characters.
    """
    if not name:
        return "unnamed"

    # Remove any path separators and dangerous characters
    sanitized = name.replace("/", "_").replace("\\", "_").replace("..", "_")

    # Keep only safe characters
    sanitized = "".join(c if c.isalnum() or c in "-_" else "_" for c in sanitized)

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Ensure it's not empty after sanitization
    return sanitized if sanitized else "unnamed"


def _is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """
    Check if target_path is safely within base_dir (no path traversal).
    """
    try:
        # Resolve both paths to absolute paths
        base_resolved = base_dir.resolve()
        target_resolved = target_path.resolve()

        # Check if target is within base
        return str(target_resolved).startswith(str(base_resolved))
    except (OSError, ValueError):
        return False


def _get_grafana_credentials():
    """
    Get Grafana credentials from environment variables.
    Warns once if default credentials are being used.
    """
    global _default_creds_warned
    user = os.environ.get("GF_SECURITY_ADMIN_USER", "admin")
    password = os.environ.get("GF_SECURITY_ADMIN_PASSWORD")

    if not password:
        if not _default_creds_warned:
            logger.warning(
                "GF_SECURITY_ADMIN_PASSWORD not set, using default. "
                "Set this environment variable for production!"
            )
            _default_creds_warned = True
        password = "admin"

    return user, password


class BackupManager:
    """Manages backup and restore operations."""

    @staticmethod
    def _backup_victoriametrics(backup_dir: Path) -> bool:
        """
        Create VictoriaMetrics snapshot and copy to backup directory.

        Returns:
            True if successful, False otherwise
        """
        try:
            vm_url = os.environ.get("METRICS_URL", "http://victoriametrics:8428")

            # Create snapshot via API
            logger.info("Creating VictoriaMetrics snapshot...")
            response = requests.post(f"{vm_url}/snapshot/create", timeout=60)

            if response.status_code != 200:
                logger.error(f"Failed to create VM snapshot: {response.status_code}")
                return False

            result = response.json()
            snapshot_name = result.get("snapshot", "")

            if not snapshot_name:
                logger.error("No snapshot name returned from VictoriaMetrics")
                return False

            logger.info(f"VictoriaMetrics snapshot created: {snapshot_name}")

            # Copy snapshot data using docker exec
            # The snapshot is stored in /storage/snapshots/<snapshot_name>
            vm_backup_dir = backup_dir / "victoriametrics"
            vm_backup_dir.mkdir(exist_ok=True)

            # Use docker cp to copy snapshot from container
            container_name = "idm-victoriametrics"
            snapshot_path = f"/storage/snapshots/{snapshot_name}"

            cmd = [
                "docker",
                "cp",
                f"{container_name}:{snapshot_path}",
                str(vm_backup_dir / snapshot_name),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                logger.error(f"Failed to copy VM snapshot: {result.stderr}")
                return False

            logger.info("VictoriaMetrics snapshot copied successfully")

            # Clean up snapshot in container (optional, to save space)
            delete_response = requests.post(
                f"{vm_url}/snapshot/delete",
                params={"snapshot": snapshot_name},
                timeout=30,
            )

            if delete_response.status_code == 200:
                logger.info("Cleaned up VM snapshot in container")

            return True

        except Exception as e:
            logger.error(f"VictoriaMetrics backup failed: {e}", exc_info=True)
            return False

    @staticmethod
    def _backup_grafana(backup_dir: Path) -> bool:
        """
        Backup Grafana dashboards and settings via API and volume.

        Returns:
            True if successful, False otherwise
        """
        try:
            grafana_backup_dir = backup_dir / "grafana"
            grafana_backup_dir.mkdir(exist_ok=True)

            # Grafana API settings (uses secure credential helper)
            grafana_url = "http://grafana:3000"
            grafana_user, grafana_password = _get_grafana_credentials()

            # 1. Export all dashboards via API
            logger.info("Exporting Grafana dashboards...")

            try:
                # Get all dashboards
                search_response = requests.get(
                    f"{grafana_url}/api/search",
                    auth=(grafana_user, grafana_password),
                    timeout=10,
                )

                if search_response.status_code == 200:
                    dashboards = search_response.json()

                    dashboards_dir = grafana_backup_dir / "dashboards"
                    dashboards_dir.mkdir(exist_ok=True)

                    for dashboard in dashboards:
                        if dashboard.get("type") == "dash-db":
                            uid = dashboard.get("uid")
                            if uid:
                                # Sanitize uid to prevent path traversal
                                safe_uid = _sanitize_filename(uid)

                                # Get full dashboard
                                dash_response = requests.get(
                                    f"{grafana_url}/api/dashboards/uid/{uid}",
                                    auth=(grafana_user, grafana_password),
                                    timeout=10,
                                )

                                if dash_response.status_code == 200:
                                    dash_data = dash_response.json()
                                    dash_file = dashboards_dir / f"{safe_uid}.json"

                                    # Verify path is safe before writing
                                    if not _is_safe_path(dashboards_dir, dash_file):
                                        logger.warning(
                                            f"Skipping unsafe path: {dash_file}"
                                        )
                                        continue

                                    with open(dash_file, "w") as f:
                                        json.dump(dash_data, f, indent=2)
                                    logger.info(
                                        f"Exported dashboard: {dashboard.get('title')}"
                                    )

                    logger.info(f"Exported {len(dashboards)} Grafana dashboards")
                else:
                    logger.warning(
                        f"Could not export Grafana dashboards: {search_response.status_code}"
                    )

            except Exception as e:
                logger.warning(f"Grafana API backup failed (may be unavailable): {e}")

            # 2. Copy Grafana data volume using docker cp
            logger.info("Copying Grafana volume data...")

            container_name = "idm-grafana"
            grafana_data_paths = [
                "/var/lib/grafana/grafana.db",  # SQLite database
                "/var/lib/grafana/alerting",  # Alerting rules
                "/var/lib/grafana/plugins",  # Plugins
            ]

            volume_dir = grafana_backup_dir / "volume"
            volume_dir.mkdir(exist_ok=True)

            for path in grafana_data_paths:
                try:
                    dest = volume_dir / Path(path).name
                    cmd = ["docker", "cp", f"{container_name}:{path}", str(dest)]

                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=30
                    )

                    if result.returncode == 0:
                        logger.info(f"Copied Grafana data: {path}")
                    else:
                        logger.debug(f"Could not copy {path}: {result.stderr}")

                except Exception as e:
                    logger.debug(f"Could not copy Grafana path {path}: {e}")

            # 3. Copy static provisioning files from host
            logger.info("Copying Grafana provisioning files...")

            project_root = Path(__file__).parent.parent
            grafana_host_dir = project_root / "grafana"

            if grafana_host_dir.exists():
                provisioning_dir = grafana_backup_dir / "provisioning"

                # Copy provisioning directory
                if (grafana_host_dir / "provisioning").exists():
                    shutil.copytree(
                        grafana_host_dir / "provisioning",
                        provisioning_dir,
                        dirs_exist_ok=True,
                    )

                # Copy dashboards directory
                if (grafana_host_dir / "dashboards").exists():
                    shutil.copytree(
                        grafana_host_dir / "dashboards",
                        grafana_backup_dir / "host_dashboards",
                        dirs_exist_ok=True,
                    )

                logger.info("Grafana provisioning files copied")

            return True

        except Exception as e:
            logger.error(f"Grafana backup failed: {e}", exc_info=True)
            return False

    @staticmethod
    def _secure_extract(zipf: zipfile.ZipFile, target_dir: Path) -> None:
        """
        Extract files from zip archive securely, preventing path traversal.
        """
        target_dir = target_dir.resolve()
        for member in zipf.infolist():
            # Resolve destination path
            member_path = (target_dir / member.filename).resolve()

            # Check if the path is within the target directory
            if os.path.commonpath([target_dir, member_path]) != str(target_dir):
                logger.warning(f"Blocked path traversal attempt: {member.filename}")
                continue

            # Check if file is a symlink (security risk)
            if (
                member.create_system == 3
                and (member.external_attr >> 16) & 0xA000 == 0xA000
            ):
                logger.warning(f"Blocked symlink extraction: {member.filename}")
                continue

            zipf.extract(member, target_dir)

    @staticmethod
    def _backup_ml_service(backup_dir: Path) -> bool:
        """
        Backup ML service model state if available.

        Returns:
            True if successful, False otherwise
        """
        try:
            ml_backup_dir = backup_dir / "ml_service"
            ml_backup_dir.mkdir(exist_ok=True)

            # Copy ML service source code and config for reference
            project_root = Path(__file__).parent.parent
            ml_service_dir = project_root / "ml_service"

            if ml_service_dir.exists():
                # Copy main.py and requirements.txt
                for file in ["main.py", "requirements.txt", "Dockerfile"]:
                    src = ml_service_dir / file
                    if src.exists():
                        shutil.copy2(src, ml_backup_dir / file)

                logger.info("ML service configuration backed up")

            # Copy ML model data from container
            container_name = "idm-ml-service"
            try:
                # Copy model_state.pkl
                cmd = [
                    "docker",
                    "cp",
                    f"{container_name}:/app/data/model_state.pkl",
                    str(ml_backup_dir / "model_state.pkl"),
                ]
                subprocess.run(cmd, capture_output=True, check=True)
                logger.info("ML model state copied from container")
            except Exception as e:
                logger.debug(f"Could not copy ML model state: {e}")

            return True

        except Exception as e:
            logger.error(f"ML service backup failed: {e}", exc_info=True)
            return False

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

            # 4. Backup VictoriaMetrics, Grafana, and ML Service
            temp_backup_dir = BACKUP_DIR / f"temp_{timestamp}"
            temp_backup_dir.mkdir(exist_ok=True)

            try:
                # Backup VictoriaMetrics
                vm_success = BackupManager._backup_victoriametrics(temp_backup_dir)
                if vm_success:
                    backup_data["metadata"]["victoriametrics_backed_up"] = True
                    logger.info("VictoriaMetrics backup completed")
                else:
                    backup_data["metadata"]["victoriametrics_backed_up"] = False
                    logger.warning("VictoriaMetrics backup failed or skipped")

                # Backup Grafana
                grafana_success = BackupManager._backup_grafana(temp_backup_dir)
                if grafana_success:
                    backup_data["metadata"]["grafana_backed_up"] = True
                    logger.info("Grafana backup completed")
                else:
                    backup_data["metadata"]["grafana_backed_up"] = False
                    logger.warning("Grafana backup failed or skipped")

                # Backup ML Service
                ml_success = BackupManager._backup_ml_service(temp_backup_dir)
                if ml_success:
                    backup_data["metadata"]["ml_service_backed_up"] = True
                    logger.info("ML service backup completed")
                else:
                    backup_data["metadata"]["ml_service_backed_up"] = False
                    logger.warning("ML service backup failed or skipped")

                # 5. Create ZIP file
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

                    # Add AI anomaly state file (legacy/if present)
                    ai_file = Path(DATA_DIR) / "anomaly_state.json"
                    if ai_file.exists():
                        zipf.write(ai_file, "ai/anomaly_state.json")

                    # Add VictoriaMetrics backup if exists
                    vm_dir = temp_backup_dir / "victoriametrics"
                    if vm_dir.exists():
                        for root, dirs, files in os.walk(vm_dir):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(temp_backup_dir)
                                zipf.write(file_path, arcname)

                    # Add Grafana backup if exists
                    grafana_dir = temp_backup_dir / "grafana"
                    if grafana_dir.exists():
                        for root, dirs, files in os.walk(grafana_dir):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(temp_backup_dir)
                                zipf.write(file_path, arcname)

                    # Add ML service backup if exists
                    ml_dir = temp_backup_dir / "ml_service"
                    if ml_dir.exists():
                        for root, dirs, files in os.walk(ml_dir):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(temp_backup_dir)
                                zipf.write(file_path, arcname)

            finally:
                # Clean up temporary backup directory
                if temp_backup_dir.exists():
                    shutil.rmtree(temp_backup_dir, ignore_errors=True)

            file_size = backup_path.stat().st_size
            logger.info(
                f"Backup created successfully: {backup_name} ({file_size} bytes)"
            )

            # Upload to WebDAV if enabled
            webdav_result = None
            if config.get("webdav.enabled", False) and config.get(
                "backup.auto_upload", False
            ):
                logger.info("Auto-uploading backup to WebDAV...")
                webdav_result = BackupManager.upload_to_webdav(str(backup_path))

            return {
                "success": True,
                "filename": backup_name,
                "path": str(backup_path),
                "size": file_size,
                "created_at": backup_data["metadata"]["created_at"],
                "webdav_upload": webdav_result,
            }

        except Exception as e:
            logger.error(f"Backup creation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    @staticmethod
    def _restore_victoriametrics(extract_dir: Path) -> bool:
        """
        Restore VictoriaMetrics snapshot from backup.

        Returns:
            True if successful, False otherwise
        """
        try:
            vm_backup_dir = extract_dir / "victoriametrics"
            if not vm_backup_dir.exists():
                logger.info("No VictoriaMetrics backup found in archive")
                return False

            # Find snapshot directory
            snapshots = list(vm_backup_dir.iterdir())
            if not snapshots:
                logger.warning("VictoriaMetrics backup directory is empty")
                return False

            snapshot_dir = snapshots[0]  # Take first snapshot
            logger.info(f"Restoring VictoriaMetrics snapshot: {snapshot_dir.name}")

            # Copy snapshot to container
            container_name = "idm-victoriametrics"

            # First, copy to container's snapshots directory
            cmd = [
                "docker",
                "cp",
                str(snapshot_dir),
                f"{container_name}:/storage/snapshots/",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                logger.error(f"Failed to copy snapshot to container: {result.stderr}")
                return False

            # Restore snapshot via API
            vm_url = os.environ.get("METRICS_URL", "http://victoriametrics:8428")

            response = requests.post(
                f"{vm_url}/snapshot/restore",
                params={"snapshot": snapshot_dir.name},
                timeout=120,
            )

            if response.status_code == 200:
                logger.info("VictoriaMetrics snapshot restored successfully")
                return True
            else:
                logger.error(
                    f"Failed to restore VM snapshot via API: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"VictoriaMetrics restore failed: {e}", exc_info=True)
            return False

    @staticmethod
    def _restore_grafana(extract_dir: Path) -> bool:
        """
        Restore Grafana dashboards and settings from backup.

        Returns:
            True if successful, False otherwise
        """
        try:
            grafana_backup_dir = extract_dir / "grafana"
            if not grafana_backup_dir.exists():
                logger.info("No Grafana backup found in archive")
                return False

            # Grafana API settings (uses secure credential helper)
            grafana_url = "http://grafana:3000"
            grafana_user, grafana_password = _get_grafana_credentials()

            # 1. Restore dashboards via API
            dashboards_dir = grafana_backup_dir / "dashboards"
            if dashboards_dir.exists():
                logger.info("Restoring Grafana dashboards...")

                for dashboard_file in dashboards_dir.glob("*.json"):
                    try:
                        with open(dashboard_file, "r") as f:
                            dashboard_data = json.load(f)

                        # Import dashboard
                        import_data = {
                            "dashboard": dashboard_data.get(
                                "dashboard", dashboard_data
                            ),
                            "overwrite": True,
                            "message": "Restored from backup",
                        }

                        response = requests.post(
                            f"{grafana_url}/api/dashboards/db",
                            auth=(grafana_user, grafana_password),
                            json=import_data,
                            timeout=10,
                        )

                        if response.status_code in (200, 201):
                            logger.info(f"Restored dashboard: {dashboard_file.name}")
                        else:
                            logger.warning(
                                f"Failed to restore dashboard {dashboard_file.name}: {response.status_code}"
                            )

                    except Exception as e:
                        logger.warning(
                            f"Could not restore dashboard {dashboard_file.name}: {e}"
                        )

            # 2. Restore Grafana volume data
            volume_dir = grafana_backup_dir / "volume"
            if volume_dir.exists():
                logger.info("Restoring Grafana volume data...")

                container_name = "idm-grafana"

                for item in volume_dir.iterdir():
                    try:
                        # Copy back to container
                        cmd = [
                            "docker",
                            "cp",
                            str(item),
                            f"{container_name}:/var/lib/grafana/",
                        ]

                        result = subprocess.run(
                            cmd, capture_output=True, text=True, timeout=30
                        )

                        if result.returncode == 0:
                            logger.info(f"Restored Grafana data: {item.name}")
                        else:
                            logger.warning(
                                f"Could not restore {item.name}: {result.stderr}"
                            )

                    except Exception as e:
                        logger.warning(
                            f"Could not restore Grafana item {item.name}: {e}"
                        )

                # Restart Grafana to apply changes
                try:
                    subprocess.run(
                        ["docker", "restart", container_name],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    logger.info("Grafana restarted to apply restored data")
                except Exception as e:
                    logger.warning(f"Could not restart Grafana: {e}")

            # 3. Restore provisioning files to host
            provisioning_dir = grafana_backup_dir / "provisioning"
            if provisioning_dir.exists():
                logger.info("Restoring Grafana provisioning files...")

                project_root = Path(__file__).parent.parent
                grafana_host_dir = project_root / "grafana"
                grafana_host_dir.mkdir(exist_ok=True)

                # Copy provisioning directory
                dest_provisioning = grafana_host_dir / "provisioning"
                if dest_provisioning.exists():
                    shutil.rmtree(dest_provisioning)

                shutil.copytree(provisioning_dir, dest_provisioning)
                logger.info("Grafana provisioning files restored")

            # Restore host dashboards
            host_dashboards_dir = grafana_backup_dir / "host_dashboards"
            if host_dashboards_dir.exists():
                logger.info("Restoring host dashboard files...")

                project_root = Path(__file__).parent.parent
                dest_dashboards = project_root / "grafana" / "dashboards"

                if dest_dashboards.exists():
                    shutil.rmtree(dest_dashboards)

                shutil.copytree(host_dashboards_dir, dest_dashboards)
                logger.info("Host dashboard files restored")

            return True

        except Exception as e:
            logger.error(f"Grafana restore failed: {e}", exc_info=True)
            return False

    @staticmethod
    def _restore_ml_service(extract_dir: Path) -> bool:
        """
        Restore ML service data (model state).
        """
        try:
            ml_backup_dir = extract_dir / "ml_service"
            if not ml_backup_dir.exists():
                return False

            # Check for model state
            model_file = ml_backup_dir / "model_state.pkl"
            if model_file.exists():
                logger.info("Restoring ML model state...")
                container_name = "idm-ml-service"
                # Copy to container
                cmd = [
                    "docker",
                    "cp",
                    str(model_file),
                    f"{container_name}:/app/data/model_state.pkl",
                ]
                subprocess.run(cmd, capture_output=True, check=True)

                # Restart ML service
                subprocess.run(
                    ["docker", "restart", container_name],
                    capture_output=True,
                    check=False,
                )
                logger.info("ML service restored and restarted")
                return True
            return False
        except Exception as e:
            logger.error(f"ML restore failed: {e}")
            return False

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

        # Create temporary extraction directory
        temp_extract_dir = (
            BACKUP_DIR / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        temp_extract_dir.mkdir(exist_ok=True)

        try:
            restored_items = []

            with zipfile.ZipFile(backup_path, "r") as zipf:
                # Extract all files to temp directory securely
                BackupManager._secure_extract(zipf, temp_extract_dir)

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

                # 6. Restore AI state (legacy / simple file)
                if "ai/anomaly_state.json" in zipf.namelist():
                    ai_file = Path(DATA_DIR) / "anomaly_state.json"
                    with open(ai_file, "wb") as f:
                        f.write(zipf.read("ai/anomaly_state.json"))
                    restored_items.append("ai_model_legacy")
                    logger.info("AI Model state (legacy) restored")

            # 7. Restore VictoriaMetrics
            vm_success = BackupManager._restore_victoriametrics(temp_extract_dir)
            if vm_success:
                restored_items.append("victoriametrics")
                logger.info("VictoriaMetrics data restored")

            # 8. Restore Grafana
            grafana_success = BackupManager._restore_grafana(temp_extract_dir)
            if grafana_success:
                restored_items.append("grafana")
                logger.info("Grafana data restored")

            # 9. Restore ML Service Data (River model)
            ml_success = BackupManager._restore_ml_service(temp_extract_dir)
            if ml_success:
                restored_items.append("ml_service_model")
                logger.info("ML Service data restored")

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
        finally:
            # Clean up temporary extraction directory
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir, ignore_errors=True)

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
            # Refresh config just in case
            keep_count = int(config.get("backup.retention", keep_count))

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
        """
        Upload a file to WebDAV/Nextcloud in the background.
        Returns immediately with 'success': True to avoid blocking.
        """
        if not WEBDAV_AVAILABLE:
            return {"success": False, "error": "WebDAV library not available"}

        url = config.get("webdav.url")
        username = config.get("webdav.username")
        password = config.get("webdav.password")

        if not url or not username:
            return {"success": False, "error": "WebDAV not configured"}

        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": "File not found"}

        def _do_upload():
            try:
                client = WebDavClient(base_url=url, auth=(username, password))

                # Check connection
                try:
                    client.exists("/")
                except Exception as e:
                    # Try adding /remote.php/dav/files/USER/ if it's Nextcloud and failed
                    # But we assume user provides full URL for now
                    logger.error(f"WebDAV connection failed: {e}")
                    return

                remote_path = f"/{path.name}"
                # Nextcloud/WebDAV often requires the directory to exist or precise path
                # We upload to root of WebDAV share

                client.upload_file(file_path, remote_path, overwrite=True)
                logger.info(f"Successfully uploaded {path.name} to WebDAV")

            except Exception as e:
                logger.error(f"WebDAV upload failed: {e}")

        # Start upload in background
        thread = threading.Thread(target=_do_upload, daemon=True)
        thread.start()

        return {"success": True, "message": "Upload started in background"}


# Convenience instance
backup_manager = BackupManager()
