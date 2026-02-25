
import pytest
import time
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# Ensure telemetry_server is in path (same as conftest.py)
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import app modules
# We need to mock environment variables before importing app
with patch.dict(os.environ, {"MODEL_DIR": "/tmp/models", "HASH_CACHE_TTL": "3600"}):
    import app
    from app import get_file_hash, _file_hash_cache, HASH_CACHE_TTL

@pytest.mark.asyncio
async def test_get_file_hash_smart_caching():
    """
    Test that get_file_hash uses mtime and size to avoid re-hashing
    when TTL expires but file hasn't changed.
    """
    filepath = "/tmp/models/test_model.enc"

    # Reset cache
    _file_hash_cache.clear()

    # Mock os.stat results
    mock_stat_initial = MagicMock()
    mock_stat_initial.st_mtime = 1000.0
    mock_stat_initial.st_size = 500

    # Mock hashlib to return a hash
    mock_hash_obj = MagicMock()
    mock_hash_obj.hexdigest.return_value = "hash_v1"

    # Use a mock time starting at T0
    start_time = 10000.0

    # 1. First call: Should calculate hash (Cold Cache)
    with patch("os.path.exists", return_value=True), \
         patch("os.stat", return_value=mock_stat_initial), \
         patch("builtins.open", MagicMock()) as mock_open, \
         patch("hashlib.file_digest", return_value=mock_hash_obj) as mock_digest, \
         patch("time.time", return_value=start_time):

        hash1 = await get_file_hash(filepath)
        assert hash1 == "hash_v1"
        assert mock_digest.call_count == 1

        # Verify cache state
        assert filepath in _file_hash_cache
        # Verify cache content structure (might change with optimization, but currently tuple)
        assert _file_hash_cache[filepath][0] == "hash_v1"

    # 2. Second call: Within TTL (Warm Cache)
    # Should NOT check file (no open/digest), might check stat depending on implementation but ideally not even stat if TTL valid.
    with patch("os.path.exists", return_value=True), \
         patch("os.stat", return_value=mock_stat_initial) as mock_stat, \
         patch("builtins.open", MagicMock()) as mock_open, \
         patch("hashlib.file_digest", return_value=mock_hash_obj) as mock_digest, \
         patch("time.time", return_value=start_time + 10): # +10 seconds

        hash2 = await get_file_hash(filepath)
        assert hash2 == "hash_v1"
        assert mock_digest.call_count == 0 # Should use cache
        assert mock_open.call_count == 0

    # 3. Third call: AFTER TTL, but file UNCHANGED (Smart Cache Optimization)
    # This is where we verify the optimization.
    # The file hasn't changed (same stat), so it should NOT re-hash.

    mock_digest.reset_mock()
    mock_open.reset_mock()

    with patch("os.path.exists", return_value=True), \
         patch("os.stat", return_value=mock_stat_initial) as mock_stat, \
         patch("builtins.open", MagicMock()) as mock_open, \
         patch("hashlib.file_digest", return_value=mock_hash_obj) as mock_digest, \
         patch("time.time", return_value=start_time + HASH_CACHE_TTL + 10): # Expired TTL

        hash3 = await get_file_hash(filepath)
        assert hash3 == "hash_v1"

        # KEY ASSERTION:
        # If optimization works: call_count should be 0 (reused hash because stat match)
        # Without optimization: call_count would be 1 (re-hashed because TTL expired)
        assert mock_digest.call_count == 0, "Optimization failed: Re-hashed file even though mtime/size unchanged"
        assert mock_open.call_count == 0, "Optimization failed: Opened file even though mtime/size unchanged"

        # Also verify cache timestamp was updated (to avoid checking stat on every subsequent call for another TTL period)
        # This requires peeking into implementation detail slightly, or just checking next call within TTL behaves as expected.
        # Let's verify next call within NEW TTL doesn't even check stat

    # 4. Fourth call: Within NEW TTL (Warm Cache from Smart Update)
    mock_stat.reset_mock()
    with patch("os.path.exists", return_value=True), \
         patch("os.stat", return_value=mock_stat_initial) as mock_stat, \
         patch("time.time", return_value=start_time + HASH_CACHE_TTL + 20):

        hash4 = await get_file_hash(filepath)
        assert hash4 == "hash_v1"
        # If timestamp updated correctly, it shouldn't need to check stat again immediately
        # But even if it does check stat, it shouldn't re-hash.
        # Ideally, checking cache timestamp prevents stat call.

@pytest.mark.asyncio
async def test_get_file_hash_changed_file():
    """Test that if file actually changes, it IS re-hashed even with smart caching."""
    filepath = "/tmp/models/test_model.enc"

    # Initial setup
    _file_hash_cache.clear()
    start_time = 10000.0

    mock_stat_v1 = MagicMock()
    mock_stat_v1.st_mtime = 1000.0
    mock_stat_v1.st_size = 500

    mock_hash_v1 = MagicMock()
    mock_hash_v1.hexdigest.return_value = "hash_v1"

    # Populate cache (v1)
    with patch("os.path.exists", return_value=True), \
         patch("os.stat", return_value=mock_stat_v1), \
         patch("builtins.open", MagicMock()), \
         patch("hashlib.file_digest", return_value=mock_hash_v1), \
         patch("time.time", return_value=start_time):
        await get_file_hash(filepath)

    # Now simulate file change + TTL expiry
    mock_stat_v2 = MagicMock()
    mock_stat_v2.st_mtime = 2000.0 # Changed mtime
    mock_stat_v2.st_size = 500     # Same size (or diff, doesn't matter)

    mock_hash_v2 = MagicMock()
    mock_hash_v2.hexdigest.return_value = "hash_v2"

    with patch("os.path.exists", return_value=True), \
         patch("os.stat", return_value=mock_stat_v2), \
         patch("builtins.open", MagicMock()) as mock_open, \
         patch("hashlib.file_digest", return_value=mock_hash_v2) as mock_digest, \
         patch("time.time", return_value=start_time + HASH_CACHE_TTL + 10):

        hash_new = await get_file_hash(filepath)

        assert hash_new == "hash_v2"
        assert mock_digest.call_count == 1 # Must re-hash
