import sys
from unittest.mock import MagicMock
import pytest
import tempfile
import os
import time

# Mock prometheus_client to avoid registry errors during test collection/execution
# if the app is imported multiple times or if we want to isolate from metrics logic.
sys.modules["prometheus_client"] = MagicMock()

# Need to set env vars before importing app if not already set
# This ensures we don't try to create directories in /var/lib/telemetry during import
os.environ.setdefault("TOKEN_STORAGE_DIR", "/tmp/telemetry/tokens")
os.environ.setdefault("AUDIT_LOG_DIR", "/tmp/telemetry/audit")
os.environ.setdefault("PERMISSION_STORAGE_DIR", "/tmp/telemetry/permissions")
os.environ.setdefault("INSTALLATION_STORAGE_DIR", "/tmp/telemetry/installations")
os.environ.setdefault("TASK_STORAGE_DIR", "/tmp/telemetry/tasks")
os.environ.setdefault("MODEL_DIR", "/tmp/telemetry/models")

# Ensure directories exist
for d in [
    os.environ[k]
    for k in os.environ
    if k.endswith("_DIR")
    and k.startswith("TOKEN")
    or k.startswith("AUDIT")
    or k.startswith("PERMISSION")
    or k.startswith("INSTALLATION")
    or k.startswith("TASK")
    or k.startswith("MODEL")
]:
    os.makedirs(d, exist_ok=True)

from telemetry_server.app import get_file_hash, _file_hash_cache, HASH_CACHE_TTL  # noqa: E402


@pytest.mark.asyncio
async def test_hash_cache_optimization():
    """
    Verify that get_file_hash uses file metadata (mtime, size) to avoid re-hashing
    files that haven't changed, even if the internal cache TTL has expired.
    """
    # Create a dummy large file (10MB) to make hashing measurable
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"a" * 1024 * 1024 * 10)
        filepath = f.name

    try:
        # Clear cache to ensure clean state
        _file_hash_cache.clear()

        # First call - cold cache
        start = time.time()
        hash1 = await get_file_hash(filepath)
        duration1 = time.time() - start

        assert hash1 is not None
        assert filepath in _file_hash_cache
        assert duration1 > 0.001  # Should take some time to hash 10MB

        # Manually expire cache entry to force re-check logic
        # We simulate that the entry is old (older than HASH_CACHE_TTL)
        if len(_file_hash_cache[filepath]) == 4:
            # New structure: (hash, timestamp, mtime, size)
            cached_hash, _, mtime, size = _file_hash_cache[filepath]
            # Set timestamp to 10 seconds past expiration
            _file_hash_cache[filepath] = (
                cached_hash,
                time.time() - HASH_CACHE_TTL - 10,
                mtime,
                size,
            )
        else:
            pytest.fail(
                "Cache structure is not 4-tuple, optimization might not be applied correctly"
            )

        # Second call - expired TTL but file unchanged
        # Optimized implementation: Should check mtime/size, see match, return cached hash (fast)
        start = time.time()
        hash2 = await get_file_hash(filepath)
        duration2 = time.time() - start

        assert hash1 == hash2

        # Performance assertion: Second call should be significantly faster
        # Using a conservative threshold (e.g., 50x faster or < 5ms)
        assert duration2 < 0.005, (
            f"Cache optimization failed: duration {duration2}s is too slow"
        )
        assert duration2 < (duration1 / 10), (
            f"Cache optimization failed: not significantly faster than cold hash ({duration1}s)"
        )

        # Verify timestamp was updated in cache (to prevent immediate re-check next time)
        _, new_timestamp, _, _ = _file_hash_cache[filepath]
        assert time.time() - new_timestamp < 5, (
            "Cache timestamp should be updated after successful metadata check"
        )

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
