import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app import verify_admin


@pytest.mark.asyncio
async def test_verify_admin_strict_missing_header():
    admin_uuid = "12345678-1234-1234-1234-123456789abc"
    with (
        patch("app.STRICT_ADMIN_AUTH", True),
        patch("app.ADMIN_AUTH_TOKEN", "admin-token-abcdefghijklmnopqrstuvwxyz"),
        patch("app.ADMIN_IDS", {admin_uuid}),
    ):
        with pytest.raises(HTTPException) as exc:
            await verify_admin(None, admin_uuid)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_admin_strict_wrong_token():
    admin_uuid = "12345678-1234-1234-1234-123456789abc"
    with (
        patch("app.STRICT_ADMIN_AUTH", True),
        patch("app.ADMIN_AUTH_TOKEN", "admin-token-abcdefghijklmnopqrstuvwxyz"),
        patch("app.ADMIN_IDS", {admin_uuid}),
    ):
        with pytest.raises(HTTPException) as exc:
            await verify_admin("Bearer wrong-token", admin_uuid)
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_verify_admin_strict_non_admin_uuid():
    non_admin_uuid = "aaaaaaaa-1234-1234-1234-123456789abc"
    token = "admin-token-abcdefghijklmnopqrstuvwxyz"
    with (
        patch("app.STRICT_ADMIN_AUTH", True),
        patch("app.ADMIN_AUTH_TOKEN", token),
        patch("app.ADMIN_IDS", set()),
        patch("app.is_admin", return_value=False),
    ):
        with pytest.raises(HTTPException) as exc:
            await verify_admin(f"Bearer {token}", non_admin_uuid)
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_verify_admin_strict_success():
    admin_uuid = "12345678-1234-1234-1234-123456789abc"
    token = "admin-token-abcdefghijklmnopqrstuvwxyz"
    with (
        patch("app.STRICT_ADMIN_AUTH", True),
        patch("app.ADMIN_AUTH_TOKEN", token),
        patch("app.ADMIN_IDS", {admin_uuid}),
        patch("app.is_admin", return_value=False),
    ):
        result = await verify_admin(f"Bearer {token}", admin_uuid.upper())
        assert result == admin_uuid
