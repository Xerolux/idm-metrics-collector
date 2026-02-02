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
import time
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

    def _save_tokens(self):
        """Save tokens to storage."""
        try:
            # Atomic write with temp file
            temp_file = TOKEN_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.tokens, f, indent=2)
            os.replace(temp_file, TOKEN_FILE)
            logger.debug("tokens_saved", count=len(self.tokens))
        except Exception as e:
            logger.error("token_save_failed", error=str(e))

    def generate_token(self, installation_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a new authentication token for an installation.

        Args:
            installation_id: Unique installation identifier
            metadata: Optional metadata (heatpump_model, etc.)

        Returns:
            The generated token (plain text - only time it's available)
        """
        # Generate a secure random token (32 bytes = 64 hex chars)
        token = secrets.token_urlsafe(32)

        # Hash the token for storage (SHA256)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Store token info
        self.tokens[installation_id] = {
            "token_hash": token_hash,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
            "revoked": False,
            "metadata": metadata or {}
        }

        self._save_tokens()

        logger.info(
            "token_generated",
            installation_id=installation_id,
            token_hash_prefix=token_hash[:16]
        )

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
            logger.debug("token_validation_failed", reason="installation_not_found", installation_id=installation_id)
            return False

        token_info = self.tokens[installation_id]

        # Check if token is revoked
        if token_info.get("revoked", False):
            logger.warning("token_validation_failed", reason="token_revoked", installation_id=installation_id)
            return False

        # Hash provided token and compare
        provided_hash = hashlib.sha256(token.encode()).hexdigest()
        stored_hash = token_info["token_hash"]

        # Constant-time comparison
        import hmac
        is_valid = hmac.compare_digest(provided_hash, stored_hash)

        if is_valid:
            # Update last_used timestamp
            self.tokens[installation_id]["last_used"] = datetime.now(timezone.utc).isoformat()
            self._save_tokens()
            logger.debug("token_validated", installation_id=installation_id)
        else:
            logger.warning("token_validation_failed", reason="hash_mismatch", installation_id=installation_id)

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
            logger.warning("token_revocation_failed", reason="not_found", installation_id=installation_id)
            return False

        self.tokens[installation_id]["revoked"] = True
        self.tokens[installation_id]["revoked_at"] = datetime.now(timezone.utc).isoformat()
        self._save_tokens()

        logger.info("token_revoked", installation_id=installation_id)
        return True

    def token_exists(self, installation_id: str) -> bool:
        """Check if a token exists for an installation."""
        return installation_id in self.tokens and not self.tokens[installation_id].get("revoked", False)

    def get_token_info(self, installation_id: str) -> Optional[Dict[str, Any]]:
        """Get token info (without the actual token)."""
        if installation_id not in self.tokens:
            return None

        info = self.tokens[installation_id].copy()
        # Never return the actual token hash in API responses
        info.pop("token_hash", None)
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

def generate_token(installation_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Generate a new token for an installation."""
    return token_manager.generate_token(installation_id, metadata)


def validate_token(installation_id: str, token: str) -> bool:
    """Validate a token for an installation."""
    return token_manager.validate_token(installation_id, token)


def revoke_token(installation_id: str) -> bool:
    """Revoke a token for an installation."""
    return token_manager.revoke_token(installation_id)


def token_exists(installation_id: str) -> bool:
    """Check if a token exists for an installation."""
    return token_manager.token_exists(installation_id)
