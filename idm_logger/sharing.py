"""
Dashboard Sharing Module

Provides functionality for creating shareable links to dashboards
with optional authentication and view-only mode.
"""

import secrets
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)


class ShareToken:
    """Represents a share token for a dashboard."""

    def __init__(
        self,
        token_id: str,
        dashboard_id: str,
        created_by: str,
        expires_at: Optional[int] = None,
        password: Optional[str] = None,
        is_public: bool = False,
    ):
        """
        Initialize a share token.

        Args:
            token_id: Unique token ID
            dashboard_id: Dashboard ID to share
            created_by: User who created the token
            expires_at: Optional expiration timestamp
            password: Optional password for access
            is_public: Whether the dashboard is public (no auth required)
        """
        self.token_id = token_id
        self.dashboard_id = dashboard_id
        self.created_by = created_by
        self.created_at = int(datetime.now().timestamp())
        self.expires_at = expires_at
        self.password_hash = self._hash_password(password) if password else None
        self.is_public = is_public
        self.access_count = 0
        self.last_accessed = None

    def _hash_password(self, password: str) -> str:
        """Hash a password using secure bcrypt-based hashing."""
        return generate_password_hash(password, method='pbkdf2:sha256:600000')

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches."""
        if not self.password_hash:
            return True
        # Support legacy SHA256 hashes during migration
        if self.password_hash.startswith('pbkdf2:'):
            return check_password_hash(self.password_hash, password)
        # Legacy SHA256 fallback - will be upgraded on next password set
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if not self.expires_at:
            return False
        return datetime.now().timestamp() > self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "token_id": self.token_id,
            "dashboard_id": self.dashboard_id,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "has_password": self.password_hash is not None,
            "is_public": self.is_public,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }


class SharingManager:
    """Manager for dashboard share tokens."""

    def __init__(self, config):
        """
        Initialize the sharing manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.tokens: Dict[str, ShareToken] = {}
        self._load_tokens()

    def _load_tokens(self):
        """Load share tokens from configuration."""
        try:
            sharing_config = self.config.get("sharing", {})
            tokens_data = sharing_config.get("tokens", [])

            for token_data in tokens_data:
                token = ShareToken(
                    token_id=token_data["token_id"],
                    dashboard_id=token_data["dashboard_id"],
                    created_by=token_data["created_by"],
                    expires_at=token_data.get("expires_at"),
                    password=token_data.get("password"),
                    is_public=token_data.get("is_public", False),
                )
                token.access_count = token_data.get("access_count", 0)
                token.last_accessed = token_data.get("last_accessed")
                self.tokens[token.token_id] = token

            logger.info(f"Loaded {len(self.tokens)} share tokens")
        except Exception as e:
            logger.error(f"Failed to load share tokens: {e}")
            self.tokens = {}

    def _save_tokens(self):
        """Save share tokens to configuration."""
        try:
            sharing_config = self.config.get("sharing", {})
            tokens_data = []

            for token in self.tokens.values():
                token_data = token.to_dict()
                # Include password hash for persistence
                if token.password_hash:
                    token_data["password_hash"] = token.password_hash
                tokens_data.append(token_data)

            sharing_config["tokens"] = tokens_data
            self.config.data["sharing"] = sharing_config
            self.config.save()

            logger.debug(f"Saved {len(self.tokens)} share tokens")
        except Exception as e:
            logger.error(f"Failed to save share tokens: {e}")

    def create_share_token(
        self,
        dashboard_id: str,
        created_by: str,
        expires_in_days: Optional[int] = None,
        password: Optional[str] = None,
        is_public: bool = False,
    ) -> ShareToken:
        """
        Create a new share token for a dashboard.

        Args:
            dashboard_id: Dashboard ID to share
            created_by: User creating the token
            expires_in_days: Optional expiration in days
            password: Optional password for access
            is_public: Whether the dashboard is public

        Returns:
            Created ShareToken instance
        """
        # Generate unique token ID
        token_id = secrets.token_urlsafe(16)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = int(
                (datetime.now() + timedelta(days=expires_in_days)).timestamp()
            )

        token = ShareToken(
            token_id=token_id,
            dashboard_id=dashboard_id,
            created_by=created_by,
            expires_at=expires_at,
            password=password,
            is_public=is_public,
        )

        self.tokens[token_id] = token
        self._save_tokens()

        logger.info(
            f"Created share token {token_id} for dashboard {dashboard_id} by {created_by}"
        )

        return token

    def get_token(self, token_id: str) -> Optional[ShareToken]:
        """
        Get a share token by ID.

        Args:
            token_id: Token ID

        Returns:
            ShareToken instance or None
        """
        return self.tokens.get(token_id)

    def validate_token(self, token_id: str, password: Optional[str] = None) -> bool:
        """
        Validate a share token.

        Args:
            token_id: Token ID to validate
            password: Optional password to check

        Returns:
            True if token is valid
        """
        token = self.tokens.get(token_id)
        if not token:
            return False

        if token.is_expired():
            return False

        if not token.is_public and token.password_hash:
            if not password or not token.check_password(password):
                return False

        return True

    def record_access(self, token_id: str):
        """
        Record access to a shared dashboard.

        Args:
            token_id: Token ID
        """
        token = self.tokens.get(token_id)
        if token:
            token.access_count += 1
            token.last_accessed = int(datetime.now().timestamp())
            self._save_tokens()

    def delete_token(self, token_id: str) -> bool:
        """
        Delete a share token.

        Args:
            token_id: Token ID to delete

        Returns:
            True if deleted
        """
        if token_id in self.tokens:
            del self.tokens[token_id]
            self._save_tokens()
            logger.info(f"Deleted share token {token_id}")
            return True
        return False

    def get_tokens_for_dashboard(self, dashboard_id: str) -> List[ShareToken]:
        """
        Get all share tokens for a dashboard.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            List of ShareToken instances
        """
        return [
            token
            for token in self.tokens.values()
            if token.dashboard_id == dashboard_id
        ]

    def get_all_tokens(self) -> List[ShareToken]:
        """
        Get all share tokens.

        Returns:
            List of all ShareToken instances
        """
        return list(self.tokens.values())

    def cleanup_expired_tokens(self):
        """Remove all expired tokens."""
        expired_tokens = [
            token_id for token_id, token in self.tokens.items() if token.is_expired()
        ]

        for token_id in expired_tokens:
            del self.tokens[token_id]

        if expired_tokens:
            self._save_tokens()
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")

        return len(expired_tokens)
