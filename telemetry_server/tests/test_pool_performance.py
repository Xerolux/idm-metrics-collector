import pytest
import time
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from app import app

@pytest.mark.asyncio
async def test_pool_stats_parallel(client):
    """
    Test that get_data_pool_stats executes its 2 internal queries in parallel.
    """
    # Setup mock client
    mock_client = AsyncMock()
    app.state.http_client = mock_client

    # Ensure cache miss
    import app as app_module
    app_module._pool_stats_cache = (None, 0)

    # Define behavior with delay to simulate network latency
    async def side_effect(url, params=None, **kwargs):
        # Simulate network delay of 100ms
        await asyncio.sleep(0.1)

        mock_response = MagicMock()
        mock_response.status_code = 200

        # Data structure matching VM response
        data = {
            "status": "success",
            "data": {"result": [{"value": [1234567890, "100"]}]}
        }

        # We need both .json() (if old code used it) and .content (for orjson)
        mock_response.json.return_value = data
        mock_response.content = json.dumps(data).encode("utf-8")

        return mock_response

    mock_client.get.side_effect = side_effect

    # Measure time
    start_time = time.time()
    response = client.get("/api/v1/pool/status")
    end_time = time.time()

    assert response.status_code == 200
    duration = end_time - start_time

    # Assertions
    # If sequential: 2 calls * 0.1s = 0.2s + overhead
    # If parallel: 1 call duration (approx) = 0.1s + overhead
    print(f"Test duration: {duration:.4f}s")

    # It should be significantly faster than 0.2s
    # In practice with overhead it might be ~0.11s
    assert duration < 0.18, "Queries should run in parallel (expected < 0.18s)"

    # Verify both queries were actually made
    assert mock_client.get.call_count == 2
