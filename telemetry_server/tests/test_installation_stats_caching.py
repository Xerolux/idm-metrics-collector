import pytest
import time
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from app import app

@pytest.mark.asyncio
async def test_installation_stats_caching(client):
    """Verify that installation stats are cached."""
    mock_client = AsyncMock()
    app.state.http_client = mock_client

    # Reset cache before test
    import app as app_module
    app_module._installation_stats_cache = (None, 0)

    # Mock response for list query and time query
    async def side_effect(url, params=None, **kwargs):
        query = params.get("query", "")
        mock_response = MagicMock()
        mock_response.status_code = 200
        data = {"status": "success", "data": {"result": []}}

        if "count by" in query:
            # List query
            data["data"]["result"] = [
                {"metric": {"installation_id": "inst-1"}, "value": [1, "10"]},
                {"metric": {"installation_id": "inst-2"}, "value": [1, "5"]},
            ]
        elif "tlast_over_time" in query:
            # Time query
            data["data"]["result"] = [
                {"metric": {"installation_id": "inst-1"}, "value": [1, "1000"]},
                {"metric": {"installation_id": "inst-2"}, "value": [1, "2000"]},
            ]

        # Enable orjson.loads
        import json
        mock_response.content = json.dumps(data).encode("utf-8")
        mock_response.json.return_value = data
        return mock_response

    mock_client.get.side_effect = side_effect

    headers = {"Authorization": "Bearer test-token"}

    # patch verify_admin
    with patch("app.verify_admin", return_value="admin-id"), \
         patch("app.has_permission", return_value=True):

        # First call: Should trigger fetches
        client.get("/api/v1/admin/installations", headers=headers)

        # Count calls to list query
        list_calls_1 = len([
            c for c in mock_client.get.mock_calls
            if "params" in c.kwargs and "count by" in c.kwargs["params"]["query"]
        ])
        assert list_calls_1 == 1

        # Second call: Should use cache
        client.get("/api/v1/admin/installations", headers=headers)

        list_calls_2 = len([
            c for c in mock_client.get.mock_calls
            if "params" in c.kwargs and "count by" in c.kwargs["params"]["query"]
        ])
        # Should still be 1
        assert list_calls_2 == 1
