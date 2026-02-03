# Xerolux 2026
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from installation_manager import InstallationRole, BanType

@pytest.mark.asyncio
async def test_check_eligibility_roles_and_bans(client):
    """
    Test that check_eligibility returns correct role and ban status.
    """
    installation_id = "550e8400-e29b-41d4-a716-446655440000"

    # Mock dependencies
    with patch("app.get_data_pool_stats") as mock_pool_stats, \
         patch("app.installation_manager") as mock_inst_manager, \
         patch("app.ADMIN_IDS", set()):

        # Mock pool stats
        mock_pool_stats.return_value = {
            "total_installations": 10,
            "total_data_points": 20000,
            "data_sufficient": True,
            "models_available": [],
        }

        # Mock VM response (eligible)
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {"result": [{"value": [1234567890]}]},
        }
        mock_http_client.get.return_value = mock_response

        # Inject mock client into app state
        client.app.state.http_client = mock_http_client

        # Scenario 1: Sponsor Role, Not Banned
        mock_inst_manager.get_role.return_value = InstallationRole.SPONSOR
        mock_inst_manager.is_banned.return_value = False
        mock_inst_manager.get_active_bans.return_value = []
        mock_inst_manager.has_role_or_higher.return_value = False # Not admin

        response = client.get(f"/api/v1/model/check?installation_id={installation_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "sponsor"
        assert data["is_banned"] is False
        assert data.get("is_admin") is None  # False/None

        # Scenario 2: Admin Role (via DB)
        mock_inst_manager.get_role.return_value = InstallationRole.ADMIN
        mock_inst_manager.has_role_or_higher.return_value = True # Is admin

        response = client.get(f"/api/v1/model/check?installation_id={installation_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "admin"
        assert data["is_admin"] is True
        assert "server_stats" in data

        # Scenario 3: Banned
        mock_inst_manager.get_role.return_value = InstallationRole.GUEST
        mock_inst_manager.is_banned.return_value = True
        mock_inst_manager.has_role_or_higher.return_value = False
        mock_inst_manager.get_active_bans.return_value = [
            {"type": "full", "reason": "Bad behavior"}
        ]

        response = client.get(f"/api/v1/model/check?installation_id={installation_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["is_banned"] is True
        assert len(data["active_bans"]) == 1
        assert data["active_bans"][0]["reason"] == "Bad behavior"
