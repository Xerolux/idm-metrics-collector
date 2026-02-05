import pytest
import json
import time
import asyncio
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

@pytest.mark.asyncio
async def test_admin_installation_details_parallel(client):
    # Setup mock client
    mock_client = AsyncMock()
    app.state.http_client = mock_client

    # Define behavior with delay to simulate network latency
    async def side_effect(url, params=None, **kwargs):
        # Simulate network delay
        await asyncio.sleep(0.1)

        query = params.get("query", "")
        mock_response = MagicMock()
        mock_response.status_code = 200

        data = {"status": "success", "data": {"result": []}}

        if 'metrics' in query and 'heatpump_metrics' in query and 'count_over_time' not in query:
             # Metrics query
             data["data"]["result"] = [
                 {"metric": {"__name__": "heatpump_metrics_temp", "heatpump_model": "TestModel"}, "value": [123, "10"]}
             ]
        elif 'count_over_time' in query:
            # Count query
            data["data"]["result"] = [{"value": [123, "100"]}]
        elif 'min_over_time' in query:
            # First seen
            data["data"]["result"] = [{"value": [1000000000]}]
        elif 'last_over_time' in query:
            # Last seen
            data["data"]["result"] = [{"value": [1000000100]}]
        elif 'group by' in query:
             # Rank query
             data["data"]["result"] = [
                 {"metric": {"installation_id": "550e8400-e29b-41d4-a716-446655440000"}, "value": [123, "100"]},
                 {"metric": {"installation_id": "other-id"}, "value": [123, "50"]}
             ]

        mock_response.json.return_value = data
        return mock_response

    mock_client.get.side_effect = side_effect

    headers = {"Authorization": "Bearer test-token"}
    target_id = "550e8400-e29b-41d4-a716-446655440000"

    # We patch verify_admin to bypass auth checks for this perf test
    with patch("app.verify_admin", return_value="admin-id"):
        start_time = time.time()
        response = client.get(
            f"/api/v1/admin/installations/{target_id}/details",
            headers=headers
        )
        end_time = time.time()

    assert response.status_code == 200
    duration = end_time - start_time

    # If sequential: 5 calls * 0.1s = 0.5s + overhead
    # If parallel: 1 call duration (approx) = 0.1s + overhead
    # We assert it's faster than sequential sum (allow some buffer)
    assert duration < 0.25 # Should be well under 0.25s (typically ~0.12s)
