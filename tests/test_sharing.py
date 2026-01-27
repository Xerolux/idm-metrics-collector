import pytest
from unittest.mock import patch

# Mock config before importing web
with patch("idm_logger.config.Config") as MockConfig:
    mock_conf = MockConfig.return_value
    mock_conf.get.return_value = {}
    mock_conf.data = {"sharing": {"tokens": []}}

    from idm_logger.web import app, sharing_manager
    from idm_logger.dashboard_config import dashboard_manager


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_shared_dashboard_endpoint(client):
    # 1. Create a dummy dashboard
    with patch.object(dashboard_manager, "get_dashboard") as mock_get_dash:
        mock_get_dash.return_value = {"id": "dash1", "name": "Test Dash", "charts": []}

        # 2. Create a share token (public)
        token = sharing_manager.create_share_token(
            dashboard_id="dash1", created_by="test", is_public=True
        )

        # 3. Test access
        resp = client.get(f"/api/sharing/dashboard/{token.token_id}")
        assert resp.status_code == 200
        assert resp.json["id"] == "dash1"

        # 4. Create protected token
        token_protected = sharing_manager.create_share_token(
            dashboard_id="dash1", created_by="test", password="secret", is_public=False
        )

        # 5. Test access without password
        resp = client.get(f"/api/sharing/dashboard/{token_protected.token_id}")
        assert resp.status_code == 401
        assert resp.json["require_password"] is True

        # 6. Test access with wrong password
        resp = client.get(
            f"/api/sharing/dashboard/{token_protected.token_id}",
            headers={"X-Share-Password": "wrong"},
        )
        assert resp.status_code == 403

        # 7. Test access with correct password
        resp = client.get(
            f"/api/sharing/dashboard/{token_protected.token_id}",
            headers={"X-Share-Password": "secret"},
        )
        assert resp.status_code == 200
        assert resp.json["id"] == "dash1"


def test_query_metrics_with_share_token(client):
    # Mock sharing manager to validate token
    with patch.object(sharing_manager, "validate_token") as mock_validate:
        mock_validate.return_value = True

        # Mock requests.get to VictoriaMetrics
        with patch("requests.get") as mock_requests_get:
            mock_requests_get.return_value.status_code = 200
            mock_requests_get.return_value.json.return_value = {
                "status": "success",
                "data": {},
            }

            # Access protected endpoint with token
            resp = client.get(
                "/api/metrics/query_range?query=test",
                headers={"X-Share-Token": "valid_token"},
            )

            assert resp.status_code == 200
            mock_validate.assert_called_with("valid_token", None)


def test_query_metrics_unauthorized(client):
    # Access without login or token
    resp = client.get("/api/metrics/query_range?query=test")
    assert resp.status_code == 401
