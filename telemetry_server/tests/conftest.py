import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ensure telemetry_server is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Set env vars for testing
os.environ["AUTH_TOKEN"] = "test-token"
os.environ["TELEMETRY_ENCRYPTION_KEY"] = "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="

from app import app


@pytest.fixture
def client():
    return TestClient(app)
