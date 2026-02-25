import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure telemetry_server is in path (same as conftest.py)
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import app modules
# We need to mock environment variables before importing app
with patch.dict(os.environ, {"MODEL_DIR": "/tmp/models", "HASH_CACHE_TTL": "3600"}):
    from app import get_file_hash, _file_hash_cache, HASH_CACHE_TTL


@pytest.mark.asyncio
async def test_get_file_hash_smart_caching():
    """
    Test that get_file_hash uses mtime and size to avoid re-hashing
    when TTL expires but file hasn't changed.
    """
    # Need to patch MODEL_DIR in app to match our test path for the security check
    # But get_file_hash uses global MODEL_DIR which we can't easily change after import
    # except by patching os.environ or the module attribute.
    # The path MUST be inside MODEL_DIR to pass the new security check.

    # We'll use a temporary directory structure for the test
    model_dir = "/tmp/models"
    filepath = os.path.join(model_dir, "test_model.enc")

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

    # Ensure get_file_hash sees the correct MODEL_DIR for containment check
    # We patch os.path.abspath to make containment check pass easily
    # Real implementations of os.path.abspath would work if directories exist,
    # but we are mocking os.path.exists anyway.

    # We'll just patch app.MODEL_DIR directly if possible, or rely on the env var we set at import.
    # The env var set at import implies app.MODEL_DIR is "/tmp/models".

    # 1. First call: Should calculate hash (Cold Cache)
    with (
        patch("os.path.exists", return_value=True),
        patch("os.stat", return_value=mock_stat_initial),
        patch("builtins.open", MagicMock()),
        patch("hashlib.file_digest", return_value=mock_hash_obj) as mock_digest,
        patch("time.time", return_value=start_time),
    ):
        # We need to ensure os.path.abspath works as expected for the security check
        # Since we use /tmp/models which is absolute, it should work fine.

        # Patch app.MODEL_DIR to be sure (it's imported from env)
        with patch("app.MODEL_DIR", "/tmp/models"):
            hash1 = await get_file_hash(filepath)

        assert hash1 == "hash_v1"
        assert mock_digest.call_count == 1

        # Verify cache state
        assert filepath in _file_hash_cache
        # Verify cache content structure (new format: hash, timestamp, mtime, size)
        assert len(_file_hash_cache[filepath]) == 4
        assert _file_hash_cache[filepath][0] == "hash_v1"

    # 2. Second call: Within TTL (Warm Cache)
    with (
        patch("os.path.exists", return_value=True),
        patch("os.stat", return_value=mock_stat_initial),
        patch("builtins.open", MagicMock()) as mock_open,
        patch("hashlib.file_digest", return_value=mock_hash_obj) as mock_digest,
        patch("time.time", return_value=start_time + 10),
    ):  # +10 seconds
        with patch("app.MODEL_DIR", "/tmp/models"):
            hash2 = await get_file_hash(filepath)

        assert hash2 == "hash_v1"
        assert mock_digest.call_count == 0  # Should use cache
        assert mock_open.call_count == 0

    # 3. Third call: AFTER TTL, but file UNCHANGED (Smart Cache Optimization)

    mock_digest.reset_mock()

    with (
        patch("os.path.exists", return_value=True),
        patch("os.stat", return_value=mock_stat_initial),
        patch("builtins.open", MagicMock()) as mock_open,
        patch("hashlib.file_digest", return_value=mock_hash_obj) as mock_digest,
        patch("time.time", return_value=start_time + HASH_CACHE_TTL + 10),
    ):  # Expired TTL
        with patch("app.MODEL_DIR", "/tmp/models"):
            hash3 = await get_file_hash(filepath)

        assert hash3 == "hash_v1"

        # KEY ASSERTION:
        # If optimization works: call_count should be 0 (reused hash because stat match)
        assert mock_digest.call_count == 0, (
            "Optimization failed: Re-hashed file even though mtime/size unchanged"
        )
        assert mock_open.call_count == 0, (
            "Optimization failed: Opened file even though mtime/size unchanged"
        )

    # 4. Fourth call: Within NEW TTL (Warm Cache from Smart Update)
    # This verifies the timestamp was updated

    # Create a fresh mock to verify no calls
    mock_stat_check = MagicMock()
    mock_stat_check.st_mtime = 1000.0
    mock_stat_check.st_size = 500

    with (
        patch("os.path.exists", return_value=True),
        patch("os.stat", return_value=mock_stat_check) as mock_stat,
        patch("time.time", return_value=start_time + HASH_CACHE_TTL + 20),
    ):
        with patch("app.MODEL_DIR", "/tmp/models"):
            hash4 = await get_file_hash(filepath)

        assert hash4 == "hash_v1"
        # Since we are within the NEW TTL (updated in step 3), we shouldn't even need to stat
        # But implementation might stat anyway if logic is simple.
        # Actually, my implementation checks TTL first.
        # Step 3 updated the timestamp to (start_time + HASH_CACHE_TTL + 10).
        # Step 4 is at (start_time + HASH_CACHE_TTL + 20).
        # Diff is 10s < HASH_CACHE_TTL.
        # So it should return from cache WITHOUT stat (if implementation is optimal)
        # or WITH stat but WITHOUT hash.
        # Let's check logic:
        # if (now - timestamp < HASH_CACHE_TTL) ... return cached_hash
        # Yes, it should skip stat.

        # To verify it skipped stat, we can check mock_stat call count
        # BUT get_file_hash calls os.stat at the very beginning now!
        # So it ALWAYS calls stat. That's the design change I made.
        # "Get current file stats... except OSError... Check cache"
        assert mock_stat.call_count == 1


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
    with (
        patch("os.path.exists", return_value=True),
        patch("os.stat", return_value=mock_stat_v1),
        patch("builtins.open", MagicMock()),
        patch("hashlib.file_digest", return_value=mock_hash_v1),
        patch("time.time", return_value=start_time),
    ):
        with patch("app.MODEL_DIR", "/tmp/models"):
            await get_file_hash(filepath)

    # Now simulate file change + TTL expiry
    mock_stat_v2 = MagicMock()
    mock_stat_v2.st_mtime = 2000.0  # Changed mtime
    mock_stat_v2.st_size = 500  # Same size (or diff, doesn't matter)

    mock_hash_v2 = MagicMock()
    mock_hash_v2.hexdigest.return_value = "hash_v2"

    with (
        patch("os.path.exists", return_value=True),
        patch("os.stat", return_value=mock_stat_v2),
        patch("builtins.open", MagicMock()),
        patch("hashlib.file_digest", return_value=mock_hash_v2) as mock_digest,
        patch("time.time", return_value=start_time + HASH_CACHE_TTL + 10),
    ):
        with patch("app.MODEL_DIR", "/tmp/models"):
            hash_new = await get_file_hash(filepath)

        assert hash_new == "hash_v2"
        assert mock_digest.call_count == 1  # Must re-hash
