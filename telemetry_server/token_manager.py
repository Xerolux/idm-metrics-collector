# Xerolux 2026
"""
Token Manager - Per-Installation Authentication Tokens

Manages unique authentication tokens for each installation.
Replaces the shared COMMUNITY-CONTRIBUTOR-TOKEN with per-installation tokens.

Features:
- Token generation and storage
- Token validation
- Token revocation
- Automatic migration for existing installations
"""

import os
import json
import secrets
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()

# Token storage location
TOKEN_STORAGE_DIR = os.environ.get("TOKEN_STORAGE_DIR", "/var/lib/telemetry/tokens")
TOKEN_FILE = os.path.join(TOKEN_STORAGE_DIR, "installation_tokens.json")

# Ensure storage directory exists
Path(TOKEN_STORAGE_DIR).mkdir(parents=True, exist_ok=True)


class TokenManager:
    """Manages per-installation authentication tokens."""

    def __init__(self):
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._dirty = False
        self._last_save = 0.0
        self._save_interval = 60.0
        self._load_tokens()

    def _load_tokens(self):
        """Load tokens from storage."""
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    self.tokens = json.load(f)
                logger.info("tokens_loaded", count=len(self.tokens))
            else:
                logger.info("no_token_file_found", initializing=True)
                self.tokens = {}
        except Exception as e:
            logger.error("token_load_failed", error=str(e))
            self.tokens = {}

    def _save_tokens(self, force=False):
        """Save tokens to storage (debounced for last_used updates)."""
        if not force and not self._dirty:
            return
        try:
            import time as _time

            now = _time.time()
            if not force and (now - self._last_save) < self._save_interval:
                return
            temp_file = TOKEN_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.tokens, f, indent=2)
            os.replace(temp_file, TOKEN_FILE)
            self._dirty = False
            self._last_save = now
            logger.debug("tokens_saved", count=len(self.tokens))
        except Exception as e:
            logger.error("token_save_failed", error=str(e))

    def generate_token(
        self,
        installation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        with_encryption_key: bool = True,
    ) -> tuple:
        """
        Generate a new authentication token (and optionally encryption key) for an installation.

        Args:
            installation_id: Unique installation identifier
            metadata: Optional metadata (heatpump_model, etc.)
            with_encryption_key: Generate encryption key alongside token (default: True)

        Returns:
            Tuple of (token, encryption_key) or just token if with_encryption_key=False
            Both are plain text - only time they're available!
        """
        # Generate a secure random token (32 bytes = 64 hex chars)
        token = secrets.token_urlsafe(32)

        # Hash the token for storage (SHA256)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Generate encryption key if requested (32 bytes for Fernet)
        encryption_key = None
        encryption_key_b64 = None
        if with_encryption_key:
            # Generate 32-byte key for Fernet (AES-128 in CBC mode)
            from cryptography.fernet import Fernet

            encryption_key = Fernet.generate_key()  # Returns base64-encoded 32-byte key
            encryption_key_b64 = encryption_key.decode("utf-8")  # Store as string

        # Store token info
        self.tokens[installation_id] = {
            "token_hash": token_hash,
            "encryption_key_b64": encryption_key_b64,  # Base64-encoded key
            "has_encryption_key": with_encryption_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
            "revoked": False,
            "metadata": metadata or {},
        }

        self._save_tokens(force=True)

        logger.info(
            "token_generated",
            token_hash_prefix=token_hash[:16],
            has_encryption_key=with_encryption_key,
        )

        if with_encryption_key:
            return (token, encryption_key.decode("utf-8"))  # Return as string
        else:
            return token

    def validate_token(self, installation_id: str, token: str) -> bool:
        """
        Validate a token for an installation.

        Args:
            installation_id: Installation ID
            token: Token to validate

        Returns:
            True if token is valid, False otherwise
        """
        if installation_id not in self.tokens:
            logger.debug(
                "token_validation_failed",
                reason="installation_not_found",
                installation_id=installation_id,
            )
            return False

        token_info = self.tokens[installation_id]

        # Check if token is revoked
        if token_info.get("revoked", False):
            logger.warning(
                "token_validation_failed",
                reason="token_revoked",
                installation_id=installation_id,
            )
            return False

        # Hash provided token and compare
        provided_hash = hashlib.sha256(token.encode()).hexdigest()
        stored_hash = token_info["token_hash"]

        # Constant-time comparison
        import hmac

        is_valid = hmac.compare_digest(provided_hash, stored_hash)

        if is_valid:
            self.tokens[installation_id]["last_used"] = datetime.now(
                timezone.utc
            ).isoformat()
            self._dirty = True
            self._save_tokens()
            logger.debug("token_validated", installation_id=installation_id)
        else:
            logger.warning(
                "token_validation_failed",
                reason="hash_mismatch",
                installation_id=installation_id,
            )

        return is_valid

    def revoke_token(self, installation_id: str) -> bool:
        """
        Revoke a token for an installation.

        Args:
            installation_id: Installation ID

        Returns:
            True if token was revoked, False if not found
        """
        if installation_id not in self.tokens:
            logger.warning(
                "token_revocation_failed",
                reason="not_found",
                installation_id=installation_id,
            )
            return False

        self.tokens[installation_id]["revoked"] = True
        self.tokens[installation_id]["revoked_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        self._save_tokens(force=True)

        logger.info("token_revoked", installation_id=installation_id)
        return True

    def token_exists(self, installation_id: str) -> bool:
        """Check if a token exists for an installation."""
        return installation_id in self.tokens and not self.tokens[installation_id].get(
            "revoked", False
        )

    def get_encryption_key(self, installation_id: str) -> Optional[bytes]:
        """
        Get the encryption key for an installation.

        INTERNAL USE ONLY - Never expose via API!

        Args:
            installation_id: Installation ID

        Returns:
            Encryption key as bytes, or None if not found/no key
        """
        if installation_id not in self.tokens:
            return None

        token_info = self.tokens[installation_id]

        if token_info.get("revoked", False):
            logger.warning(
                "encryption_key_access_denied",
                reason="token_revoked",
                installation_id=installation_id,
            )
            return None

        encryption_key_b64 = token_info.get("encryption_key_b64")
        if not encryption_key_b64:
            return None

        # Decode from base64 string to bytes
        return encryption_key_b64.encode("utf-8")

    def has_encryption_key(self, installation_id: str) -> bool:
        """Check if an installation has a personal encryption key."""
        if installation_id not in self.tokens:
            return False

        token_info = self.tokens[installation_id]
        return (
            token_info.get("has_encryption_key", False)
            and token_info.get("encryption_key_b64") is not None
        )

    def get_token_info(self, installation_id: str) -> Optional[Dict[str, Any]]:
        """Get token info (without the actual token or encryption key)."""
        if installation_id not in self.tokens:
            return None

        info = self.tokens[installation_id].copy()
        # Never return sensitive data in API responses
        info.pop("token_hash", None)
        info.pop("encryption_key_b64", None)  # NEVER expose encryption key!
        return info

    def list_tokens(self, include_revoked: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        List all tokens (for admin purposes).

        Args:
            include_revoked: Include revoked tokens

        Returns:
            Dict of installation_id -> token_info (without hashes)
        """
        result = {}
        for installation_id, token_info in self.tokens.items():
            if not include_revoked and token_info.get("revoked", False):
                continue

            info = token_info.copy()
            info.pop("token_hash", None)  # Never expose hash
            result[installation_id] = info

        return result


# Global token manager instance
token_manager = TokenManager()


# Convenience functions


def generate_token(
    installation_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    with_encryption_key: bool = True,
):
    """Generate a new token (and optionally encryption key) for an installation."""
    return token_manager.generate_token(installation_id, metadata, with_encryption_key)


def validate_token(installation_id: str, token: str) -> bool:
    """Validate a token for an installation."""
    return token_manager.validate_token(installation_id, token)


def revoke_token(installation_id: str) -> bool:
    """Revoke a token for an installation."""
    return token_manager.revoke_token(installation_id)


def token_exists(installation_id: str) -> bool:
    """Check if a token exists for an installation."""
    return token_manager.token_exists(installation_id)


def get_encryption_key(installation_id: str) -> Optional[bytes]:
    """Get encryption key for an installation (INTERNAL USE ONLY)."""
    return token_manager.get_encryption_key(installation_id)


def has_encryption_key(installation_id: str) -> bool:
    """Check if an installation has a personal encryption key."""
    return token_manager.has_encryption_key(installation_id)
