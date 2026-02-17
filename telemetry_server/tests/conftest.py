# Xerolux 2026
import pytest
from fastapi.testclient import TestClient
import os
import sys
import asyncio
import tempfile
import shutil

# Ensure telemetry_server is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Create temporary directories for testing
test_dir = tempfile.mkdtemp()
os.environ["TOKEN_STORAGE_DIR"] = os.path.join(test_dir, "tokens")
os.environ["AUDIT_LOG_DIR"] = os.path.join(test_dir, "audit")
os.environ["PERMISSION_STORAGE_DIR"] = os.path.join(test_dir, "permissions")
os.environ["INSTALLATION_STORAGE_DIR"] = os.path.join(test_dir, "installations")
os.environ["TASK_STORAGE_DIR"] = os.path.join(test_dir, "tasks")
os.environ["MODEL_DIR"] = os.path.join(test_dir, "models")
os.environ["AUTH_TOKEN"] = "test-token"
os.environ["TELEMETRY_ENCRYPTION_KEY"] = "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="

# Ensure directories exist
for var in [
    "TOKEN_STORAGE_DIR",
    "AUDIT_LOG_DIR",
    "PERMISSION_STORAGE_DIR",
    "INSTALLATION_STORAGE_DIR",
    "TASK_STORAGE_DIR",
    "MODEL_DIR",
]:
    os.makedirs(os.environ[var], exist_ok=True)

from app import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_env():
    yield
    # Cleanup after session
    try:
        shutil.rmtree(test_dir)
    except Exception:
        pass


@pytest.fixture
def client():
    """Create a test client with proper startup."""
    # Import httpx to create mock client
    import httpx

    # Setup startup event manually
    async def setup():
        app.state.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

    # Run setup in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup())

    # Create client
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    loop.run_until_complete(app.state.http_client.aclose())
    loop.close()
