import pytest
import os
import time
from unittest.mock import patch, MagicMock
import sys

# Ensure telemetry_server is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import app modules - mock prometheus to avoid issues
with patch.dict(sys.modules, {"prometheus_client": MagicMock()}):
    from app import get_file_hash, _file_hash_cache, HASH_CACHE_TTL


@pytest.mark.asyncio
async def test_hash_cache_optimization(tmp_path):
    """Test that file hashing is optimized (skipped if metadata unchanged)."""

    # Create a dummy file
    test_file = tmp_path / "test_model.enc"
    test_file.write_text("dummy content")
    filepath = str(test_file)

    # Clean cache
    _file_hash_cache.clear()

    # Mock _get_file_hash_sync to track calls
    with patch("app._get_file_hash_sync") as mock_hash:
        mock_hash.return_value = "dummy_hash"

        # 1. First call - should calculate hash
        hash1 = await get_file_hash(filepath)
        assert hash1 == "dummy_hash"
        assert mock_hash.call_count == 1

        # Verify cache structure (current implementation check)
        assert filepath in _file_hash_cache

        # 2. Second call within TTL - should use cache (no hash calculation)
        hash2 = await get_file_hash(filepath)
        assert hash2 == "dummy_hash"
        assert mock_hash.call_count == 1  # Still 1 call

        # 3. Simulate TTL expiry
        # We need to manually expire the cache entry by manipulating timestamp
        cache_entry = _file_hash_cache[filepath]
        old_timestamp = time.time() - (HASH_CACHE_TTL + 10)

        # Helper to update timestamp regardless of tuple size (handles both 2-tuple and 4-tuple)
        if len(cache_entry) == 2:
            _file_hash_cache[filepath] = (cache_entry[0], old_timestamp)
        else:
            _file_hash_cache[filepath] = (cache_entry[0], old_timestamp) + cache_entry[
                2:
            ]

        # 4. Third call (TTL expired, but file unchanged)
        # Currently: Should re-calculate hash (call_count -> 2)
        # After Optimization: Should NOT re-calculate hash (call_count -> 1)

        hash3 = await get_file_hash(filepath)
        assert hash3 == "dummy_hash"

        # This assertion defines the optimization goal.
        # It will FAIL on current codebase (count will be 2).
        # It will PASS on optimized codebase (count will be 1).
        assert mock_hash.call_count == 1, (
            "Hash should not be recalculated if file metadata is unchanged"
        )

        # 5. Modify file and check
        # Update file content
        test_file.write_text("new content")

        # Force mtime update (filesystems have resolution limits, ensure it's different)
        new_mtime = time.time() + 100
        os.utime(filepath, (new_mtime, new_mtime))

        # Expire cache again to force check
        cache_entry = _file_hash_cache[filepath]
        if len(cache_entry) == 2:
            _file_hash_cache[filepath] = (cache_entry[0], old_timestamp)
        else:
            _file_hash_cache[filepath] = (cache_entry[0], old_timestamp) + cache_entry[
                2:
            ]

        # Mock hash to return new value
        mock_hash.return_value = "new_hash"

        hash4 = await get_file_hash(filepath)
        assert hash4 == "new_hash"
        assert mock_hash.call_count == 2, "Hash must be recalculated if file changed"
