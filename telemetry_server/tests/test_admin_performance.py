import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from app import app


@pytest.mark.asyncio
async def test_admin_list_installations_n_plus_1_repro(client):
    # Setup mock client
    mock_client = AsyncMock()
    # We need to set it on the app instance used by the client
    # The client fixture uses 'app' imported from 'app' module
    app.state.http_client = mock_client

    # Define behavior for get requests
    async def side_effect(url, params=None, **kwargs):
        query = params.get("query", "")
        mock_response = MagicMock()
        mock_response.status_code = 200

        data = {}
        if "group by" in query:
            # Query 1: Master List & Series Counts (Original Logic)
            results = []
            for i in range(10):
                results.append(
                    {
                        "metric": {"installation_id": f"inst-{i}"},
                        "value": [1234567890, "5"],  # 5 active series
                    }
                )
            data = {
                "status": "success",
                "data": {"result": results},
            }
        elif "tlast_over_time" in query:
            # Query 2: Last Seen Times
            results = []
            for i in range(10):
                results.append(
                    {
                        "metric": {"installation_id": f"inst-{i}"},
                        # Timestamp is in the value for tlast_over_time
                        "value": [1234567890, "1234567890"],
                    }
                )
            data = {
                "status": "success",
                "data": {"result": results},
            }
        else:
            data = {
                "status": "success",
                "data": {"result": []},
            }

        mock_response.json.return_value = data
        # Enable use of orjson.loads(response.content)
        mock_response.content = json.dumps(data).encode("utf-8")

        return mock_response

    mock_client.get.side_effect = side_effect

    # Make request
    headers = {"Authorization": "Bearer test-token"}

    # patch verify_admin to avoid complexity
    with patch("app.is_admin", return_value=True):
        response = client.get(
            "/api/v1/admin/installations?installation_id=admin-id", headers=headers
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["installations"]) == 10

    # Verify we only made 2 calls (Optimization Success)
    assert mock_client.get.call_count == 2

    # Verify data integrity
    inst = data["installations"][0]
    assert inst["data_points"] == 5  # Series count
    assert inst["last_seen"] == 1234567890
