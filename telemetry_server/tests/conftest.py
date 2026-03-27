# Xerolux 2026
import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

os.environ["AUTH_TOKEN"] = "test-token"
os.environ["TELEMETRY_ENCRYPTION_KEY"] = "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="
os.environ["REDIS_URL"] = ""

from app import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
