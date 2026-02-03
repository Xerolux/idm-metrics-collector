import os
import pytest
from unittest.mock import patch


@pytest.fixture
def protected_admin_id():
    return "protected-super-admin"


@pytest.fixture
def mock_env_vars(protected_admin_id, tmp_path):
    with patch.dict(
        os.environ,
        {
            "ADMIN_INSTALLATION_IDS": protected_admin_id,
            "INSTALLATION_STORAGE_DIR": str(tmp_path / "installations"),
            "PERMISSION_STORAGE_DIR": str(tmp_path / "permissions"),
        },
    ):
        yield


def test_protected_admin_cannot_be_banned(mock_env_vars, protected_admin_id):
    # Re-import or re-instantiate to pick up env vars
    import installation_manager as im

    # Manually set the protected IDs for the test context
    im.PROTECTED_IDS = {protected_admin_id}

    # Try to ban, expect ValueError
    with pytest.raises(ValueError, match="Cannot ban protected admin"):
        im.installation_manager.ban_installation(
            installation_id=protected_admin_id,
            ban_type=im.BanType.FULL,
            banned_by="attacker",
            reason="malicious",
        )

    # Assertions
    assert im.installation_manager.is_banned(protected_admin_id) is False


def test_protected_admin_permissions_cannot_be_revoked(
    mock_env_vars, protected_admin_id
):
    import permissions as pm

    # Manually set protected IDs
    pm.PROTECTED_IDS = {protected_admin_id}

    # Ensure admin has permissions (simulating initialization)
    pm.permission_manager.admin_permissions[protected_admin_id] = {
        "permissions": ["admin:full"],
        "granted_at": "2026-01-01T00:00:00Z",
        "granted_by": "system",
    }

    # Try to revoke
    result = pm.permission_manager.revoke_permission(
        admin_id=protected_admin_id, permission="admin:full", revoked_by="attacker"
    )

    # Assertions
    assert result is False
    assert (
        pm.permission_manager.has_permission(protected_admin_id, "admin:full") is True
    )
