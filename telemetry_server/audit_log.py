"""
Audit Logging System for Admin Actions

Tracks all admin operations for security and compliance.
Logs are stored in JSON format with structured data.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger()

# Audit log directory
AUDIT_LOG_DIR = Path(os.environ.get("AUDIT_LOG_DIR", "/var/log/telemetry"))
AUDIT_LOG_FILE = AUDIT_LOG_DIR / "audit.log"
AUDIT_LOG_RETENTION_DAYS = int(os.environ.get("AUDIT_LOG_RETENTION_DAYS", "90"))


class AuditLogger:
    """
    Audit logger for tracking admin actions.

    Events are logged with:
    - Timestamp (ISO 8601 UTC)
    - Action type
    - Admin ID
    - IP address
    - Resource affected
    - Result (success/failure)
    - Additional metadata
    """

    def __init__(self):
        """Initialize audit logger and ensure log directory exists."""
        self.log_file = AUDIT_LOG_FILE
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """Create audit log directory if it doesn't exist."""
        try:
            AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("audit_log_dir_created", path=str(AUDIT_LOG_DIR))
        except Exception as e:
            logger.error(
                "audit_log_dir_creation_failed", error=str(e), path=str(AUDIT_LOG_DIR)
            )

    def log(
        self,
        action: str,
        admin_id: str,
        ip_address: str,
        resource: Optional[str] = None,
        result: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log an audit event.

        Args:
            action: Type of action (e.g., "model_delete", "training_trigger")
            admin_id: Installation ID of the admin
            ip_address: IP address of the request
            resource: Resource affected (e.g., model name, installation ID)
            result: "success" or "failure"
            metadata: Additional structured data
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "admin_id": admin_id,
            "ip_address": ip_address,
            "resource": resource,
            "result": result,
            "metadata": metadata or {},
        }

        try:
            # Write to audit log file
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")

            # Prepare safe event for structured logger (mask sensitive IDs)
            safe_event = event.copy()
            if safe_event.get("admin_id"):
                aid = safe_event["admin_id"]
                if len(aid) >= 8:
                    safe_event["admin_id"] = f"{aid[:8]}..."
                else:
                    safe_event["admin_id"] = "***"

            # Also log to structured logger
            logger.info("audit_event", **safe_event)
        except Exception as e:
            # Never fail on audit log errors, but log the error
            logger.error("audit_log_write_failed", error=str(e))

    def _read_last_lines(self, limit: int) -> list[str]:
        """
        Read the last N lines from the log file efficiently.
        Returns lines in reverse order (newest first).
        """
        if not self.log_file.exists():
            return []

        lines = []
        chunk_size = 8192

        try:
            with open(self.log_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                position = f.tell()
                buffer = b""

                while position > 0 and len(lines) < limit:
                    read_size = min(chunk_size, position)
                    position -= read_size
                    f.seek(position)
                    chunk = f.read(read_size)

                    # Combine chunk with buffer (chunk is the prefix)
                    data = chunk + buffer
                    parts = data.split(b"\n")

                    # The first part is incomplete (continued from previous chunk)
                    buffer = parts[0]

                    # The rest are complete lines. Iterate in reverse.
                    for line_bytes in reversed(parts[1:]):
                        if len(lines) >= limit:
                            break
                        if line_bytes.strip():
                            try:
                                lines.append(line_bytes.decode("utf-8"))
                            except UnicodeDecodeError:
                                # Skip lines with decoding errors
                                continue

                # Process remaining buffer if needed
                if len(lines) < limit and buffer.strip():
                    try:
                        lines.append(buffer.decode("utf-8"))
                    except UnicodeDecodeError:
                        pass

        except Exception as e:
            logger.error("audit_log_read_failed", error=str(e))

        return lines

    def get_recent_events(self, limit: int = 100) -> list[Dict[str, Any]]:
        """
        Get recent audit events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of audit events (most recent first)
        """
        events = []

        try:
            # Get last N lines (already reversed: newest first)
            lines = self._read_last_lines(limit)

            for line in lines:
                try:
                    event = json.loads(line.strip())
                    events.append(event)
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            logger.error("audit_log_process_failed", error=str(e))

        return events

    def get_events_by_admin(
        self, admin_id: str, limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Get audit events for a specific admin.

        Args:
            admin_id: Installation ID of the admin
            limit: Maximum number of events to return

        Returns:
            List of audit events for this admin (most recent first)
        """
        all_events = self.get_recent_events(limit=1000)
        admin_events = [e for e in all_events if e.get("admin_id") == admin_id]
        return admin_events[:limit]

    def get_events_by_action(
        self, action: str, limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Get audit events for a specific action type.

        Args:
            action: Action type (e.g., "model_delete")
            limit: Maximum number of events to return

        Returns:
            List of audit events for this action (most recent first)
        """
        all_events = self.get_recent_events(limit=1000)
        action_events = [e for e in all_events if e.get("action") == action]
        return action_events[:limit]

    def cleanup_old_logs(self):
        """
        Clean up audit logs older than retention period.

        This should be called periodically (e.g., daily).
        """
        try:
            if not self.log_file.exists():
                return

            # Read all events
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Filter events within retention period
            cutoff_time = datetime.now(timezone.utc).timestamp() - (
                AUDIT_LOG_RETENTION_DAYS * 86400
            )
            kept_events = []
            removed_count = 0

            for line in lines:
                try:
                    event = json.loads(line.strip())
                    event_time = datetime.fromisoformat(event["timestamp"]).timestamp()

                    if event_time >= cutoff_time:
                        kept_events.append(line)
                    else:
                        removed_count += 1
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Keep malformed lines for now
                    kept_events.append(line)

            # Write back filtered events
            if removed_count > 0:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.writelines(kept_events)

                logger.info(
                    "audit_log_cleanup",
                    removed=removed_count,
                    retained=len(kept_events),
                )

        except Exception as e:
            logger.error("audit_log_cleanup_failed", error=str(e))


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions for common audit events


def log_model_delete(
    admin_id: str, ip_address: str, model_name: str, success: bool = True
):
    """Log model deletion event."""
    audit_logger.log(
        action="model_delete",
        admin_id=admin_id,
        ip_address=ip_address,
        resource=model_name,
        result="success" if success else "failure",
    )


def log_training_trigger(
    admin_id: str,
    ip_address: str,
    success: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Log training trigger event."""
    audit_logger.log(
        action="training_trigger",
        admin_id=admin_id,
        ip_address=ip_address,
        result="success" if success else "failure",
        metadata=metadata,
    )


def log_model_download(
    installation_id: str, ip_address: str, model_name: str, success: bool = True
):
    """Log model download event."""
    audit_logger.log(
        action="model_download",
        admin_id=installation_id,  # For downloads, use installation_id as the user
        ip_address=ip_address,
        resource=model_name,
        result="success" if success else "failure",
        metadata={"model": model_name},
    )


def log_installation_delete(
    admin_id: str, ip_address: str, installation_id: str, success: bool = True
):
    """Log installation deletion event."""
    audit_logger.log(
        action="installation_delete",
        admin_id=admin_id,
        ip_address=ip_address,
        resource=installation_id,
        result="success" if success else "failure",
    )


def log_config_change(
    admin_id: str,
    ip_address: str,
    config_key: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Log configuration change event."""
    audit_logger.log(
        action="config_change",
        admin_id=admin_id,
        ip_address=ip_address,
        resource=config_key,
        result="success",
        metadata=metadata,
    )


def log_failed_auth(installation_id: str, ip_address: str, reason: str):
    """Log failed authentication attempt."""
    audit_logger.log(
        action="failed_auth",
        admin_id=installation_id,
        ip_address=ip_address,
        result="failure",
        metadata={"reason": reason},
    )


def log_admin_access(admin_id: str, ip_address: str, endpoint: str):
    """Log admin endpoint access."""
    audit_logger.log(
        action="admin_access",
        admin_id=admin_id,
        ip_address=ip_address,
        resource=endpoint,
        result="success",
    )
