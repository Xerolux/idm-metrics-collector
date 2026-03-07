import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os

# Add telemetry_server to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import get_data_pool_stats


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data


async def mock_get(*args, **kwargs):
    await asyncio.sleep(0.5)  # Simulate 500ms network latency

    if "count by (installation_id)" in kwargs.get("params", {}).get("query", ""):
        return MockResponse(
            200, {"status": "success", "data": {"result": [{"value": [0, "10"]}]}}
        )
    else:
        return MockResponse(
            200, {"status": "success", "data": {"result": [{"value": [0, "1000"]}]}}
        )


async def mock_run_sync(*args, **kwargs):
    await asyncio.sleep(0.5)  # Simulate 500ms disk IO latency
    return ["model1", "model2"]


async def main():
    mock_request = MagicMock()
    mock_client = AsyncMock()
    mock_client.get.side_effect = mock_get
    mock_request.app.state.http_client = mock_client

    # We must patch run_sync
    with patch("app.run_sync", new=mock_run_sync):
        start = time.time()
        stats = await get_data_pool_stats(mock_request)
        end = time.time()

        print(f"Stats: {stats}")
        print(f"Time taken: {end - start:.2f} seconds")
        # Sequential would take ~1.5s (0.5 + 0.5 + 0.5)
        # Parallel takes ~0.5s


if __name__ == "__main__":
    asyncio.run(main())
