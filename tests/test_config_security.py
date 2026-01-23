
import pytest
from unittest.mock import MagicMock
import sys

# Mock db to avoid database connection
# We must mock it before importing idm_logger.config
if "idm_logger.db" not in sys.modules:
    sys.modules["idm_logger.db"] = MagicMock()
    sys.modules["idm_logger.db"].db = MagicMock()
    sys.modules["idm_logger.db"].db.get_setting.return_value = None

from idm_logger.config import config

def test_no_default_password():
    """Test that the default 'admin' password is NOT accepted when hash is missing."""
    # Setup: Remove admin_password_hash if it exists
    # We work on a copy or modify the singleton? Modifying singleton is fine for this test session.
    # Note: This test expects the security fix to be applied.
    # Before the fix, this assertion will fail.

    # Ensure we are in a state with no hash
    if "admin_password_hash" in config.data["web"]:
        del config.data["web"]["admin_password_hash"]

    # Verify fallback is disabled
    # If this fails, the vulnerability exists
    assert config.check_admin_password("admin") is False, "Vulnerability: Default password 'admin' is enabled!"

def test_missing_hash_fails_closed():
    """Test that authentication fails closed (returns False) when hash is missing."""
    if "admin_password_hash" in config.data["web"]:
        del config.data["web"]["admin_password_hash"]

    assert config.check_admin_password("anything") is False
