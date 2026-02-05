import asyncio
import time
import json
from unittest.mock import MagicMock, AsyncMock, patch
import os
import sys

# Ensure app can be imported
sys.path.append(os.path.join(os.getcwd(), "telemetry_server"))

# Mock environment variables for app import
os.environ["TOKEN_STORAGE_DIR"] = "/tmp/tokens"
os.environ["AUDIT_LOG_DIR"] = "/tmp/audit"
os.environ["PERMISSION_STORAGE_DIR"] = "/tmp/permissions"
os.environ["TASK_STORAGE_DIR"] = "/tmp/tasks"
os.environ["INSTALLATION_STORAGE_DIR"] = "/tmp/installations"
os.environ["TRAINING_QUEUE_DIR"] = "/tmp/training"
os.environ["MODEL_DIR"] = "/tmp/models"

from app import app, admin_list_installations

# Configuration
N_INSTALLATIONS = 100
LATENCY_MS = 0.01  # 10ms


async def simulate_n_plus_1(client):
    # Simulate list query (1 call)
    await asyncio.sleep(LATENCY_MS)

    installations = [f"inst-{i}" for i in range(N_INSTALLATIONS)]

    results = []
    for inst_id in installations:
        # Simulate time query per installation (N calls)
        await asyncio.sleep(LATENCY_MS)
        results.append({"installation_id": inst_id, "last_seen": 1234567890})
    return results


async def run_benchmark():
    print(
        f"Benchmarking with N={N_INSTALLATIONS} installations, latency={LATENCY_MS * 1000}ms"
    )

    # Setup mock client
    mock_client = AsyncMock()
    app.state.http_client = mock_client

    # Define behavior for get requests
    async def side_effect(url, params=None, **kwargs):
        # Simulate network delay
        await asyncio.sleep(LATENCY_MS)

        query = params.get("query", "")
        mock_response = MagicMock()
        mock_response.status_code = 200

        results = []
        if "count by" in query:  # List query
            for i in range(N_INSTALLATIONS):
                results.append(
                    {
                        "metric": {"installation_id": f"inst-{i}"},
                        "value": [1234567890, "5"],
                    }
                )
        elif "tlast_over_time" in query:  # Time query
            for i in range(N_INSTALLATIONS):
                results.append(
                    {
                        "metric": {"installation_id": f"inst-{i}"},
                        "value": [1234567890, "1234567890"],
                    }
                )

        # Prepare valid JSON response
        json_data = {"status": "success", "data": {"result": results}}
        mock_response.json.return_value = json_data
        # Prepare content for orjson optimization
        mock_response.content = json.dumps(json_data).encode("utf-8")

        return mock_response

    mock_client.get.side_effect = side_effect

    # Benchmark Optimized
    print("\nRunning Optimized Implementation...")
    start_time = time.time()
    # Mock verify_admin and check_admin_rate_limit to avoid overhead
    with (
        patch("app.verify_admin", new=AsyncMock(return_value="admin")),
        patch("app.check_admin_rate_limit", new=AsyncMock()),
    ):
        # Create a mock request object
        mock_request = MagicMock()
        mock_request.app = app
        mock_request.headers = {}
        mock_request.client.host = "127.0.0.1"

        await admin_list_installations(mock_request, limit=N_INSTALLATIONS)
    end_time = time.time()
    optimized_duration = end_time - start_time
    print(f"Optimized Duration: {optimized_duration:.4f}s")

    # Benchmark N+1 Simulation
    print("\nRunning N+1 Simulation...")
    start_time = time.time()
    await simulate_n_plus_1(mock_client)
    end_time = time.time()
    n_plus_1_duration = end_time - start_time
    print(f"N+1 Duration:       {n_plus_1_duration:.4f}s")

    speedup = n_plus_1_duration / optimized_duration
    print(f"\nSpeedup: {speedup:.2f}x")


if __name__ == "__main__":
    # Setup directories
    for d in [
        "/tmp/tokens",
        "/tmp/audit",
        "/tmp/permissions",
        "/tmp/tasks",
        "/tmp/installations",
        "/tmp/training",
        "/tmp/models",
    ]:
        os.makedirs(d, exist_ok=True)

    asyncio.run(run_benchmark())
