import pytest
from collections import deque
from telemetry_server.app import check_rate_limit, _rate_limit_store, _rate_limit_lock, RATE_LIMITS, RATE_LIMIT_WINDOW
import time
from unittest.mock import patch

def test_check_rate_limit_deque_logic():
    # Reset store
    _rate_limit_store.clear()

    ip = "127.0.0.1"
    endpoint = "default"

    # Mock time
    start_time = 1000.0

    with patch("time.time", return_value=start_time):
        # 1. Fill up to limit - 1
        limit = RATE_LIMITS["default"]
        for _ in range(limit):
            allowed, headers = check_rate_limit(ip, endpoint)
            assert allowed is True

        # Verify deque length
        key = f"ratelimit:{ip}:{endpoint}"
        assert len(_rate_limit_store[key]) == limit
        assert isinstance(_rate_limit_store[key], deque)

        # 2. Exceed limit
        allowed, headers = check_rate_limit(ip, endpoint)
        assert allowed is False
        assert headers["X-RateLimit-Remaining"] == "0"

    # 3. Advance time to expire one entry
    # Oldest entry is at start_time.
    # New time = start_time + RATE_LIMIT_WINDOW + 1
    new_time = start_time + RATE_LIMIT_WINDOW + 1

    with patch("time.time", return_value=new_time):
        allowed, headers = check_rate_limit(ip, endpoint)
        assert allowed is True
        # Should have popped all old entries actually, since they were all at start_time
        assert len(_rate_limit_store[key]) == 1 # Just the new one

def test_check_rate_limit_sliding_window():
    _rate_limit_store.clear()
    ip = "10.0.0.1"
    endpoint = "default"
    limit = RATE_LIMITS["default"]

    start_time = 1000.0

    # Add 1 entry at T=0
    with patch("time.time", return_value=start_time):
        check_rate_limit(ip, endpoint)

    # Add limit-1 entries at T=window/2
    mid_time = start_time + (RATE_LIMIT_WINDOW / 2)
    with patch("time.time", return_value=mid_time):
        for _ in range(limit - 1):
            check_rate_limit(ip, endpoint)

    # At T=window/2, we should be at full capacity
    key = f"ratelimit:{ip}:{endpoint}"
    assert len(_rate_limit_store[key]) == limit

    # Try one more at T=window/2 -> Should fail
    with patch("time.time", return_value=mid_time):
        allowed, _ = check_rate_limit(ip, endpoint)
        assert allowed is False

    # Advance to T=window + 1
    # The first entry (at T=0) should expire.
    # The entries at T=window/2 should remain.
    end_time = start_time + RATE_LIMIT_WINDOW + 1
    with patch("time.time", return_value=end_time):
        allowed, _ = check_rate_limit(ip, endpoint)
        assert allowed is True

        # Remaining count should be (limit - 1) + 1 new one = limit
        assert len(_rate_limit_store[key]) == limit
