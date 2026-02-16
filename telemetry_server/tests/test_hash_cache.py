import sys
from unittest.mock import MagicMock

# Mock prometheus_client to avoid "Duplicated timeseries" error
sys.modules["prometheus_client"] = MagicMock()

import pytest  # noqa: E402
import tempfile  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from telemetry_server.app import get_file_hash, _file_hash_cache, HASH_CACHE_TTL  # noqa: E402


@pytest.mark.asyncio
async def test_hash_cache_optimization():
    # Create a dummy large file (10MB) to make hashing measurable
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"a" * 1024 * 1024 * 10)
        filepath = f.name

    try:
        # Clear cache
        _file_hash_cache.clear()

        # First call - cold cache
        start = time.time()
        hash1 = await get_file_hash(filepath)
        duration1 = time.time() - start

        assert hash1 is not None
        assert filepath in _file_hash_cache

        # Verify new cache structure
        cache_entry = _file_hash_cache[filepath]
        assert len(cache_entry) == 4, (
            "Cache should store (hash, timestamp, mtime, size)"
        )

        # Manually expire cache entry to force re-check if logic was solely TTL-based
        old_hash, _, mtime, size = cache_entry
        _file_hash_cache[filepath] = (
            old_hash,
            time.time() - HASH_CACHE_TTL - 10,
            mtime,
            size,
        )

        # Second call - expired TTL but file unchanged
        # Optimized implementation: Should check mtime, see it's same, return cached hash (fast)
        start = time.time()
        hash2 = await get_file_hash(filepath)
        duration2 = time.time() - start

        assert hash1 == hash2

        print(f"First call (cold): {duration1:.4f}s")
        print(f"Second call (expired TTL, file unchanged): {duration2:.4f}s")

        # Verify optimization: second call should be significantly faster (avoiding 10MB read/hash)
        # 10MB read/hash takes > 0.01s typically. Stat takes < 0.001s.
        assert duration2 < duration1 * 0.5, (
            "Optimization failed: Second call was not significantly faster"
        )

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
