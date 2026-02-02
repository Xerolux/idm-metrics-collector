# Xerolux 2026
"""
Permission System - Role-Based Access Control (RBAC)

Manages granular admin permissions to prevent full-access admin accounts.
Implements principle of least privilege.

Permission Roles:
- admin:view      - Read-only access to admin data
- admin:models    - Model management (delete, download)
- admin:training  - Trigger model training
- admin:users     - Installation management (revoke tokens, etc.)
- admin:full      - All permissions (super admin)
"""

import os
import json
import structlog
from pathlib import Path
from typing import Set, Dict, Optional, List
from datetime import datetime, timezone
from fastapi import HTTPException

logger = structlog.get_logger()

# Permission storage location
PERMISSION_STORAGE_DIR = os.environ.get("PERMISSION_STORAGE_DIR", "/var/lib/telemetry/permissions")
PERMISSION_FILE = os.path.join(PERMISSION_STORAGE_DIR, "admin_permissions.json")

# Ensure storage directory exists
Path(PERMISSION_STORAGE_DIR).mkdir(parents=True, exist_ok=True)

# Permission definitions
PERMISSIONS = {
    "admin:view": "Read-only access to admin data and dashboards",
    "admin:models": "Model management (delete, download, view analytics)",
    "admin:training": "Trigger model training and manage training queue",
    "admin:users": "Installation management (token revocation, user info)",
    "admin:full": "Full admin access (all permissions)",
}

# Permission hierarchies (which permissions grant others)
PERMISSION_HIERARCHY = {
    "admin:full": ["admin:view", "admin:models", "admin:training", "admin:users"],
}


class PermissionManager:
    """Manages admin permissions with role-based access control."""

    def __init__(self):
        self.admin_permissions: Dict[str, Dict] = {}
        self._load_permissions()

    def _load_permissions(self):
        """Load permissions from storage."""
        try:
            if os.path.exists(PERMISSION_FILE):
                with open(PERMISSION_FILE, "r", encoding="utf-8") as f:
                    self.admin_permissions = json.load(f)
                logger.info("permissions_loaded", count=len(self.admin_permissions))
            else:
                logger.info("no_permission_file_found", initializing=True)
                self.admin_permissions = {}
                # Initialize with default full-access admins from env
                self._initialize_default_admins()
        except Exception as e:
            logger.error("permission_load_failed", error=str(e))
            self.admin_permissions = {}
            self._initialize_default_admins()

    def _initialize_default_admins(self):
        """Initialize existing ADMIN_INSTALLATION_IDS with full access."""
        raw_admin_ids = os.environ.get("ADMIN_INSTALLATION_IDS", "")
        admin_ids = {x.strip().lower() for x in raw_admin_ids.split(",") if x.strip()}

        for admin_id in admin_ids:
            if admin_id and admin_id not in self.admin_permissions:
                self.admin_permissions[admin_id] = {
                    "permissions": ["admin:full"],
                    "granted_at": datetime.now(timezone.utc).isoformat(),
                    "granted_by": "system",
                    "migrated": True,
                }
                logger.info("default_admin_initialized", admin_id=admin_id)

        if admin_ids:
            self._save_permissions()

    def _save_permissions(self):
        """Save permissions to storage."""
        try:
            # Atomic write with temp file
            temp_file = PERMISSION_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.admin_permissions, f, indent=2)
            os.replace(temp_file, PERMISSION_FILE)
            logger.debug("permissions_saved", count=len(self.admin_permissions))
        except Exception as e:
            logger.error("permission_save_failed", error=str(e))

    def grant_permission(
        self,
        admin_id: str,
        permission: str,
        granted_by: str
    ) -> bool:
        """
        Grant a permission to an admin.

        Args:
            admin_id: Admin installation ID
            permission: Permission to grant (e.g., "admin:models")
            granted_by: Who granted this permission (for audit trail)

        Returns:
            True if permission was granted, False if already exists
        """
        if permission not in PERMISSIONS:
            raise ValueError(f"Invalid permission: {permission}")

        admin_id = admin_id.lower()

        if admin_id not in self.admin_permissions:
            self.admin_permissions[admin_id] = {
                "permissions": [],
                "granted_at": datetime.now(timezone.utc).isoformat(),
                "granted_by": granted_by,
            }

        if permission not in self.admin_permissions[admin_id]["permissions"]:
            self.admin_permissions[admin_id]["permissions"].append(permission)
            self.admin_permissions[admin_id]["last_modified"] = datetime.now(timezone.utc).isoformat()
            self.admin_permissions[admin_id]["last_modified_by"] = granted_by
            self._save_permissions()

            logger.info(
                "permission_granted",
                admin_id=admin_id,
                permission=permission,
                granted_by=granted_by
            )
            return True
        else:
            logger.debug("permission_already_exists", admin_id=admin_id, permission=permission)
            return False

    def revoke_permission(
        self,
        admin_id: str,
        permission: str,
        revoked_by: str
    ) -> bool:
        """
        Revoke a permission from an admin.

        Args:
            admin_id: Admin installation ID
            permission: Permission to revoke
            revoked_by: Who revoked this permission (for audit trail)

        Returns:
            True if permission was revoked, False if didn't exist
        """
        admin_id = admin_id.lower()

        if admin_id not in self.admin_permissions:
            logger.warning("revoke_permission_failed", reason="admin_not_found", admin_id=admin_id)
            return False

        if permission in self.admin_permissions[admin_id]["permissions"]:
            self.admin_permissions[admin_id]["permissions"].remove(permission)
            self.admin_permissions[admin_id]["last_modified"] = datetime.now(timezone.utc).isoformat()
            self.admin_permissions[admin_id]["last_modified_by"] = revoked_by
            self._save_permissions()

            logger.info(
                "permission_revoked",
                admin_id=admin_id,
                permission=permission,
                revoked_by=revoked_by
            )
            return True
        else:
            logger.debug("permission_not_found", admin_id=admin_id, permission=permission)
            return False

    def has_permission(self, admin_id: str, permission: str) -> bool:
        """
        Check if an admin has a specific permission.

        Args:
            admin_id: Admin installation ID
            permission: Permission to check

        Returns:
            True if admin has the permission (directly or via hierarchy)
        """
        admin_id = admin_id.lower()

        if admin_id not in self.admin_permissions:
            logger.debug("permission_check_failed", reason="admin_not_found", admin_id=admin_id)
            return False

        admin_perms = set(self.admin_permissions[admin_id]["permissions"])

        # Check direct permission
        if permission in admin_perms:
            return True

        # Check permission hierarchy (e.g., admin:full grants all permissions)
        for granted_perm in admin_perms:
            if granted_perm in PERMISSION_HIERARCHY:
                if permission in PERMISSION_HIERARCHY[granted_perm]:
                    return True

        return False

    def get_permissions(self, admin_id: str) -> Set[str]:
        """
        Get all effective permissions for an admin (including hierarchy).

        Args:
            admin_id: Admin installation ID

        Returns:
            Set of all permissions (direct + inherited)
        """
        admin_id = admin_id.lower()

        if admin_id not in self.admin_permissions:
            return set()

        permissions = set(self.admin_permissions[admin_id]["permissions"])

        # Expand hierarchical permissions
        expanded = set(permissions)
        for perm in permissions:
            if perm in PERMISSION_HIERARCHY:
                expanded.update(PERMISSION_HIERARCHY[perm])

        return expanded

    def is_admin(self, admin_id: str) -> bool:
        """Check if an installation_id is an admin (has any permissions)."""
        admin_id = admin_id.lower()
        return admin_id in self.admin_permissions and len(self.admin_permissions[admin_id]["permissions"]) > 0

    def list_admins(self) -> Dict[str, Dict]:
        """List all admins with their permissions (for admin UI)."""
        result = {}
        for admin_id, info in self.admin_permissions.items():
            result[admin_id] = {
                "permissions": info["permissions"],
                "effective_permissions": list(self.get_permissions(admin_id)),
                "granted_at": info.get("granted_at"),
                "granted_by": info.get("granted_by"),
                "last_modified": info.get("last_modified"),
                "last_modified_by": info.get("last_modified_by"),
                "migrated": info.get("migrated", False),
            }
        return result

    def get_admin_info(self, admin_id: str) -> Optional[Dict]:
        """Get permission info for a specific admin."""
        admin_id = admin_id.lower()

        if admin_id not in self.admin_permissions:
            return None

        info = self.admin_permissions[admin_id].copy()
        info["effective_permissions"] = list(self.get_permissions(admin_id))
        return info


# Global permission manager instance
permission_manager = PermissionManager()


# Convenience functions

def has_permission(admin_id: str, permission: str) -> bool:
    """Check if an admin has a specific permission."""
    return permission_manager.has_permission(admin_id, permission)


def is_admin(admin_id: str) -> bool:
    """Check if an installation is an admin."""
    return permission_manager.is_admin(admin_id)


def require_permission(permission: str):
    """
    Decorator to require a specific permission for an endpoint.

    Usage:
        @app.get("/api/v1/admin/models")
        @require_permission("admin:models")
        async def list_models(admin_id: str):
            ...
    """
    from functools import wraps
    from fastapi import HTTPException

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract admin_id from kwargs (should be set by verify_admin)
            admin_id = kwargs.get("admin_id")

            if not admin_id:
                raise HTTPException(
                    status_code=500,
                    detail="Internal error: admin_id not provided"
                )

            if not has_permission(admin_id, permission):
                logger.warning(
                    "permission_denied",
                    admin_id=admin_id,
                    permission=permission,
                    has_permissions=list(permission_manager.get_permissions(admin_id))
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {permission}"
                )

            logger.debug("permission_granted", admin_id=admin_id, permission=permission)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
