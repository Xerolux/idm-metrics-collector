import pytest
import time
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app import app


@pytest.mark.asyncio
async def test_pool_status_performance_parallel():
    """
    Verify that get_data_pool_stats executes in parallel.
    We mock delays to measure execution time.
    """

    # Mock VM query response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {"result": [{"value": [123456, "20000"]}]},
    }

    # Define a slow async mock for client.get
    async def slow_get(*args, **kwargs):
        await asyncio.sleep(0.1)  # 100ms delay
        return mock_response

    # Define a slow mock for run_sync
    async def slow_run_sync(func, *args):
        await asyncio.sleep(0.1)  # 100ms delay
        return ["Model A", "Model B"]

    # Patch dependencies
    with patch("app.httpx.AsyncClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.get.side_effect = slow_get
        mock_instance.aclose = AsyncMock()

        with patch("app.run_sync", side_effect=slow_run_sync):
            with TestClient(app) as client:
                start_time = time.time()

                response = client.get("/api/v1/pool/status")

                duration = time.time() - start_time

                assert response.status_code == 200

                # Expected: max(0.1, 0.1) + overhead = ~0.1s
                print(f"\nExecution duration: {duration:.4f}s")

                # Should be significantly faster than 0.3s
                assert duration < 0.2, (
                    f"Execution too slow ({duration:.4f}s), expected parallel behavior < 0.2s"
                )
