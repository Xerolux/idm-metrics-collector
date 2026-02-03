# Xerolux 2026
"""
Installation Manager - Role and Ban Management for Installations

Manages installation roles and ban status for the telemetry system.

Roles (in order of privilege):
- guest     - Default role, basic functionality
- visitor   - Can view public data
- sponsor   - Extended features, priority support
- moderator - Can view installation data (no management)
- admin     - Full access (managed separately via permissions.py)

Ban Types:
- upload    - Cannot submit telemetry data
- download  - Cannot download models
- full      - Completely blocked from all services

Bans can be permanent or time-limited.
"""

import os
import json
import structlog
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone, timedelta
from enum import Enum

logger = structlog.get_logger()

# Storage location
INSTALLATION_STORAGE_DIR = os.environ.get(
    "INSTALLATION_STORAGE_DIR", "/var/lib/telemetry/installations"
)
INSTALLATION_FILE = os.path.join(INSTALLATION_STORAGE_DIR, "installations.json")

# Ensure storage directory exists
Path(INSTALLATION_STORAGE_DIR).mkdir(parents=True, exist_ok=True)


class InstallationRole(str, Enum):
    """Installation role levels."""

    GUEST = "guest"
    VISITOR = "visitor"
    SPONSOR = "sponsor"
    MODERATOR = "moderator"
    SUPPORT = "support"
    ADMIN = "admin"


class BanType(str, Enum):
    """Types of bans that can be applied."""

    UPLOAD = "upload"  # Cannot upload/submit data
    DOWNLOAD = "download"  # Cannot download models
    FULL = "full"  # Completely blocked


# Role hierarchy (higher index = more privileges)
ROLE_HIERARCHY = [
    InstallationRole.GUEST,
    InstallationRole.VISITOR,
    InstallationRole.SPONSOR,
    InstallationRole.MODERATOR,
    InstallationRole.SUPPORT,
    InstallationRole.ADMIN,
]

# Role descriptions for UI
ROLE_DESCRIPTIONS = {
    InstallationRole.GUEST: "Default role with basic telemetry functionality",
    InstallationRole.VISITOR: "Can view public statistics and community data",
    InstallationRole.SPONSOR: "Extended features, priority support, early access",
    InstallationRole.MODERATOR: "Can view installation data and assist with support",
    InstallationRole.SUPPORT: "Can view detailed diagnostics and assist users",
    InstallationRole.ADMIN: "Full administrative access (requires admin permissions)",
}

# Features enabled per role
ROLE_FEATURES = {
    InstallationRole.GUEST: ["upload", "download_community_model"],
    InstallationRole.VISITOR: ["upload", "download_community_model", "view_stats"],
    InstallationRole.SPONSOR: [
        "upload",
        "download_community_model",
        "view_stats",
        "priority_training",
        "early_access",
    ],
    InstallationRole.MODERATOR: [
        "upload",
        "download_community_model",
        "view_stats",
        "view_installations",
        "view_audit_log",
    ],
    InstallationRole.SUPPORT: [
        "upload",
        "download_community_model",
        "view_stats",
        "view_installations",
        "view_audit_log",
        "view_diagnostics",
    ],
    InstallationRole.ADMIN: ["*"],  # All features
}


class InstallationManager:
    """Manages installation roles and ban status."""

    def __init__(self):
        self.installations: Dict[str, Dict] = {}
        self._load_installations()

    def _load_installations(self):
        """Load installations from storage."""
        try:
            if os.path.exists(INSTALLATION_FILE):
                with open(INSTALLATION_FILE, "r", encoding="utf-8") as f:
                    self.installations = json.load(f)
                logger.info("installations_loaded", count=len(self.installations))
            else:
                logger.info("no_installation_file_found", initializing=True)
                self.installations = {}
        except Exception as e:
            logger.error("installation_load_failed", error=str(e))
            self.installations = {}

    def _save_installations(self):
        """Save installations to storage."""
        try:
            temp_file = INSTALLATION_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.installations, f, indent=2)
            os.replace(temp_file, INSTALLATION_FILE)
            logger.debug("installations_saved", count=len(self.installations))
        except Exception as e:
            logger.error("installation_save_failed", error=str(e))

    def _ensure_installation(self, installation_id: str) -> Dict:
        """Ensure installation record exists, create if not."""
        installation_id = installation_id.lower()
        if installation_id not in self.installations:
            self.installations[installation_id] = {
                "role": InstallationRole.GUEST.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "bans": {},
                "notes": "",
                "metadata": {},
            }
            self._save_installations()
            logger.info("installation_created", installation_id=installation_id)
        return self.installations[installation_id]

    # --- Role Management ---

    def set_role(
        self,
        installation_id: str,
        role: InstallationRole,
        set_by: str,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Set the role for an installation.

        Args:
            installation_id: Target installation ID
            role: New role to assign
            set_by: Who is setting this role (for audit)
            reason: Optional reason for the change

        Returns:
            True if role was changed
        """
        installation_id = installation_id.lower()
        record = self._ensure_installation(installation_id)

        old_role = record.get("role", InstallationRole.GUEST.value)
        if old_role == role.value:
            return False

        record["role"] = role.value
        record["role_changed_at"] = datetime.now(timezone.utc).isoformat()
        record["role_changed_by"] = set_by
        if reason:
            record["role_change_reason"] = reason

        # Add to history
        if "role_history" not in record:
            record["role_history"] = []
        record["role_history"].append(
            {
                "from": old_role,
                "to": role.value,
                "changed_at": datetime.now(timezone.utc).isoformat(),
                "changed_by": set_by,
                "reason": reason,
            }
        )

        self._save_installations()

        logger.info(
            "role_changed",
            installation_id=installation_id,
            old_role=old_role,
            new_role=role.value,
            changed_by=set_by,
        )
        return True

    def get_role(self, installation_id: str) -> InstallationRole:
        """Get the role for an installation."""
        installation_id = installation_id.lower()
        if installation_id not in self.installations:
            return InstallationRole.GUEST

        role_str = self.installations[installation_id].get("role", "guest")
        try:
            return InstallationRole(role_str)
        except ValueError:
            return InstallationRole.GUEST

    def has_role_or_higher(
        self, installation_id: str, min_role: InstallationRole
    ) -> bool:
        """Check if installation has at least the specified role."""
        current_role = self.get_role(installation_id)
        current_idx = ROLE_HIERARCHY.index(current_role)
        min_idx = ROLE_HIERARCHY.index(min_role)
        return current_idx >= min_idx

    def has_feature(self, installation_id: str, feature: str) -> bool:
        """Check if installation has access to a specific feature."""
        role = self.get_role(installation_id)
        features = ROLE_FEATURES.get(role, [])
        return "*" in features or feature in features

    # --- Ban Management ---

    def ban_installation(
        self,
        installation_id: str,
        ban_type: BanType,
        banned_by: str,
        reason: str,
        duration_hours: Optional[int] = None,
    ) -> Dict:
        """
        Ban an installation.

        Args:
            installation_id: Target installation ID
            ban_type: Type of ban (upload, download, full)
            banned_by: Who is issuing the ban (for audit)
            reason: Reason for the ban (required)
            duration_hours: Ban duration in hours (None = permanent)

        Returns:
            Ban record
        """
        installation_id = installation_id.lower()
        record = self._ensure_installation(installation_id)

        expires_at = None
        if duration_hours:
            expires_at = (
                datetime.now(timezone.utc) + timedelta(hours=duration_hours)
            ).isoformat()

        ban_record = {
            "type": ban_type.value,
            "reason": reason,
            "banned_at": datetime.now(timezone.utc).isoformat(),
            "banned_by": banned_by,
            "expires_at": expires_at,
            "duration_hours": duration_hours,
            "active": True,
        }

        record["bans"][ban_type.value] = ban_record

        # Add to ban history
        if "ban_history" not in record:
            record["ban_history"] = []
        record["ban_history"].append(
            {
                **ban_record,
                "action": "banned",
            }
        )

        self._save_installations()

        logger.warning(
            "installation_banned",
            installation_id=installation_id,
            ban_type=ban_type.value,
            reason=reason,
            duration_hours=duration_hours,
            banned_by=banned_by,
        )

        return ban_record

    def unban_installation(
        self,
        installation_id: str,
        ban_type: BanType,
        unbanned_by: str,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Remove a ban from an installation.

        Args:
            installation_id: Target installation ID
            ban_type: Type of ban to remove
            unbanned_by: Who is removing the ban
            reason: Optional reason for unban

        Returns:
            True if ban was removed
        """
        installation_id = installation_id.lower()

        if installation_id not in self.installations:
            return False

        record = self.installations[installation_id]

        if ban_type.value not in record.get("bans", {}):
            return False

        # Mark as inactive instead of deleting
        record["bans"][ban_type.value]["active"] = False
        record["bans"][ban_type.value]["unbanned_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        record["bans"][ban_type.value]["unbanned_by"] = unbanned_by

        # Add to ban history
        if "ban_history" not in record:
            record["ban_history"] = []
        record["ban_history"].append(
            {
                "type": ban_type.value,
                "action": "unbanned",
                "unbanned_at": datetime.now(timezone.utc).isoformat(),
                "unbanned_by": unbanned_by,
                "reason": reason,
            }
        )

        self._save_installations()

        logger.info(
            "installation_unbanned",
            installation_id=installation_id,
            ban_type=ban_type.value,
            unbanned_by=unbanned_by,
        )

        return True

    def is_banned(
        self, installation_id: str, ban_type: Optional[BanType] = None
    ) -> bool:
        """
        Check if installation is banned.

        Args:
            installation_id: Installation ID to check
            ban_type: Specific ban type to check, or None for any active ban

        Returns:
            True if installation has an active ban
        """
        installation_id = installation_id.lower()

        if installation_id not in self.installations:
            return False

        bans = self.installations[installation_id].get("bans", {})

        # Check for full ban first (blocks everything)
        if "full" in bans:
            full_ban = bans["full"]
            if self._is_ban_active(full_ban):
                return True

        # Check specific ban type
        if ban_type:
            if ban_type.value in bans:
                return self._is_ban_active(bans[ban_type.value])
            return False

        # Check any active ban
        for ban in bans.values():
            if self._is_ban_active(ban):
                return True

        return False

    def _is_ban_active(self, ban: Dict) -> bool:
        """Check if a specific ban record is currently active."""
        if not ban.get("active", False):
            return False

        expires_at = ban.get("expires_at")
        if expires_at:
            try:
                expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > expiry:
                    return False
            except (ValueError, TypeError):
                pass

        return True

    def get_active_bans(self, installation_id: str) -> List[Dict]:
        """Get all active bans for an installation."""
        installation_id = installation_id.lower()

        if installation_id not in self.installations:
            return []

        bans = self.installations[installation_id].get("bans", {})
        active_bans = []

        for ban_type, ban in bans.items():
            if self._is_ban_active(ban):
                active_bans.append(
                    {
                        "type": ban_type,
                        **ban,
                    }
                )

        return active_bans

    def get_ban_info(self, installation_id: str, ban_type: BanType) -> Optional[Dict]:
        """Get info about a specific ban."""
        installation_id = installation_id.lower()

        if installation_id not in self.installations:
            return None

        bans = self.installations[installation_id].get("bans", {})
        if ban_type.value not in bans:
            return None

        ban = bans[ban_type.value]
        return {
            "type": ban_type.value,
            "is_active": self._is_ban_active(ban),
            **ban,
        }

    # --- Installation Info ---

    def get_installation(self, installation_id: str) -> Optional[Dict]:
        """Get full installation record."""
        installation_id = installation_id.lower()

        if installation_id not in self.installations:
            return None

        record = self.installations[installation_id].copy()

        # Add computed fields
        record["active_bans"] = self.get_active_bans(installation_id)
        record["is_banned"] = len(record["active_bans"]) > 0
        record["effective_role"] = self.get_role(installation_id).value

        return record

    def update_metadata(
        self,
        installation_id: str,
        metadata: Dict[str, Any],
        updated_by: Optional[str] = None,
    ):
        """Update installation metadata (heatpump model, last seen, etc.)."""
        installation_id = installation_id.lower()
        record = self._ensure_installation(installation_id)

        if "metadata" not in record:
            record["metadata"] = {}

        record["metadata"].update(metadata)
        record["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        if updated_by:
            record["metadata"]["updated_by"] = updated_by

        self._save_installations()

    def set_notes(self, installation_id: str, notes: str, set_by: str):
        """Set admin notes for an installation."""
        installation_id = installation_id.lower()
        record = self._ensure_installation(installation_id)

        record["notes"] = notes
        record["notes_updated_at"] = datetime.now(timezone.utc).isoformat()
        record["notes_updated_by"] = set_by

        self._save_installations()

        logger.info("installation_notes_updated", installation_id=installation_id)

    def list_installations(
        self,
        role_filter: Optional[InstallationRole] = None,
        banned_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List installations with optional filters.

        Returns:
            Dict with 'items', 'total', 'limit', 'offset'
        """
        items = []

        for inst_id, record in self.installations.items():
            # Apply filters
            if role_filter:
                if record.get("role") != role_filter.value:
                    continue

            if banned_only:
                if not self.is_banned(inst_id):
                    continue

            items.append(
                {
                    "installation_id": inst_id,
                    "role": record.get("role", "guest"),
                    "is_banned": self.is_banned(inst_id),
                    "active_bans": self.get_active_bans(inst_id),
                    "created_at": record.get("created_at"),
                    "notes": record.get("notes", "")[:100],  # Truncate notes
                    "metadata": record.get("metadata", {}),
                }
            )

        # Sort by creation date (newest first)
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        total = len(items)
        items = items[offset : offset + limit]

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about installations."""
        role_counts = {role.value: 0 for role in InstallationRole}
        banned_count = 0
        total = len(self.installations)

        for inst_id, record in self.installations.items():
            role = record.get("role", "guest")
            if role in role_counts:
                role_counts[role] += 1

            if self.is_banned(inst_id):
                banned_count += 1

        return {
            "total_installations": total,
            "by_role": role_counts,
            "banned_count": banned_count,
        }


# Global instance
installation_manager = InstallationManager()


# Convenience functions
def get_role(installation_id: str) -> InstallationRole:
    """Get the role for an installation."""
    return installation_manager.get_role(installation_id)


def is_banned(installation_id: str, ban_type: Optional[BanType] = None) -> bool:
    """Check if installation is banned."""
    return installation_manager.is_banned(installation_id, ban_type)


def has_feature(installation_id: str, feature: str) -> bool:
    """Check if installation has access to a feature."""
    return installation_manager.has_feature(installation_id, feature)


def check_upload_allowed(installation_id: str) -> tuple[bool, Optional[str]]:
    """
    Check if an installation is allowed to upload data.

    Returns:
        Tuple of (allowed, reason)
    """
    if installation_manager.is_banned(installation_id, BanType.UPLOAD):
        ban_info = installation_manager.get_ban_info(installation_id, BanType.UPLOAD)
        reason = (
            ban_info.get("reason", "Upload banned") if ban_info else "Upload banned"
        )
        expires = ban_info.get("expires_at") if ban_info else None
        if expires:
            reason += f" (expires: {expires})"
        return False, reason

    if installation_manager.is_banned(installation_id, BanType.FULL):
        ban_info = installation_manager.get_ban_info(installation_id, BanType.FULL)
        reason = (
            ban_info.get("reason", "Installation banned")
            if ban_info
            else "Installation banned"
        )
        return False, reason

    return True, None


def check_download_allowed(installation_id: str) -> tuple[bool, Optional[str]]:
    """
    Check if an installation is allowed to download models.

    Returns:
        Tuple of (allowed, reason)
    """
    if installation_manager.is_banned(installation_id, BanType.DOWNLOAD):
        ban_info = installation_manager.get_ban_info(installation_id, BanType.DOWNLOAD)
        reason = (
            ban_info.get("reason", "Download banned") if ban_info else "Download banned"
        )
        expires = ban_info.get("expires_at") if ban_info else None
        if expires:
            reason += f" (expires: {expires})"
        return False, reason

    if installation_manager.is_banned(installation_id, BanType.FULL):
        ban_info = installation_manager.get_ban_info(installation_id, BanType.FULL)
        reason = (
            ban_info.get("reason", "Installation banned")
            if ban_info
            else "Installation banned"
        )
        return False, reason

    return True, None
