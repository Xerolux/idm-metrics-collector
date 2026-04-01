# Xerolux 2026
import pytest
from fastapi.testclient import TestClient
import os
import sys
from contextlib import asynccontextmanager

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

os.environ["AUTH_TOKEN"] = "test-token"
os.environ["ADMIN_AUTH_TOKEN"] = "test-admin-token-1234567890-1234567890"
os.environ["STRICT_ADMIN_AUTH"] = "true"
os.environ["TELEMETRY_ENCRYPTION_KEY"] = "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="
os.environ["REDIS_URL"] = ""

from app import app


@asynccontextmanager
async def _no_lifespan(_app):
    # Disable startup/shutdown background tasks in tests to avoid teardown hangs.
    yield


@pytest.fixture
def client():
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _no_lifespan
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.router.lifespan_context = original_lifespan
