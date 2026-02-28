import time
from collections import deque
from unittest.mock import patch

import pytest

import app


@pytest.fixture(autouse=True)
def cleanup_rate_limit_store():
    # Clear store before each test
    app._rate_limit_store.clear()
    yield
    # Clear store after each test
    app._rate_limit_store.clear()


def test_rate_limit_deque_basic():
    # Setup simple limits
    app.RATE_LIMITS["test_endpoint"] = 3
    app.RATE_LIMIT_WINDOW = 60

    ip = "127.0.0.1"

    # 1. Allowed request
    allowed, headers = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is True
    assert headers["X-RateLimit-Remaining"] == "2"

    # 2. Allowed request
    allowed, headers = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is True
    assert headers["X-RateLimit-Remaining"] == "1"

    # 3. Allowed request
    allowed, headers = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is True
    assert headers["X-RateLimit-Remaining"] == "0"

    # 4. Blocked request
    allowed, headers = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is False
    assert headers["X-RateLimit-Remaining"] == "0"


@patch("time.time")
def test_rate_limit_deque_sliding_window(mock_time):
    # Setup limit 3 reqs per 60s
    app.RATE_LIMITS["test_endpoint"] = 3
    app.RATE_LIMIT_WINDOW = 60
    ip = "127.0.0.1"

    # Start at t=100
    mock_time.return_value = 100.0

    # Fill limit
    for _ in range(3):
        allowed, _ = app.check_rate_limit(ip, "test_endpoint")
        assert allowed is True

    # 4th blocked
    allowed, _ = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is False

    # Move to t=159 (59 seconds later, still blocked)
    mock_time.return_value = 159.0
    allowed, _ = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is False

    # Move to t=161 (61 seconds later, limit resets completely)
    mock_time.return_value = 166.0
    allowed, headers = app.check_rate_limit(ip, "test_endpoint")
    assert allowed is True
    assert headers["X-RateLimit-Remaining"] == "2"


@patch("time.time")
def test_cleanup_rate_limits_and_bans_deque(mock_time):
    app.RATE_LIMIT_WINDOW = 60

    compound_key = "ratelimit:127.0.0.1:test_endpoint"

    # Setup simulated old entries
    d = deque()
    d.append(100.0)
    d.append(105.0)
    d.append(150.0)
    app._rate_limit_store[compound_key] = d

    # Run cleanup at t=161
    # 100 is > 60 old, 105 is > 60 old, 150 is valid
    mock_time.return_value = 166.0

    # run the inner loop of the task
    now = time.time()
    keys_to_remove = []
    with app._rate_limit_lock:
        for ip, timestamps in list(app._rate_limit_store.items()):
            while timestamps and now - timestamps[0] >= app.RATE_LIMIT_WINDOW:
                timestamps.popleft()
            if not timestamps:
                keys_to_remove.append(ip)

        for k in keys_to_remove:
            if k in app._rate_limit_store:
                del app._rate_limit_store[k]

    # Check
    assert compound_key in app._rate_limit_store
    assert len(app._rate_limit_store[compound_key]) == 1
    assert app._rate_limit_store[compound_key][0] == 150.0

    # Run cleanup at t=211 (everything expired)
    mock_time.return_value = 211.0
    now = time.time()
    keys_to_remove = []
    with app._rate_limit_lock:
        for ip, timestamps in list(app._rate_limit_store.items()):
            while timestamps and now - timestamps[0] >= app.RATE_LIMIT_WINDOW:
                timestamps.popleft()
            if not timestamps:
                keys_to_remove.append(ip)

        for k in keys_to_remove:
            if k in app._rate_limit_store:
                del app._rate_limit_store[k]

    # Check
    assert compound_key not in app._rate_limit_store
