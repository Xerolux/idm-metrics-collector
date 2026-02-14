import pytest
from unittest.mock import patch

from app import get_file_hash, _file_hash_cache

@pytest.fixture(autouse=True)
def clean_cache():
    _file_hash_cache.clear()
    yield
    _file_hash_cache.clear()

@pytest.mark.asyncio
async def test_smart_caching_logic():
    """
    Verify that get_file_hash uses mtime/size for cache validation
    instead of just relying on TTL.
    """
    # Mock the sync hash function to count calls
    with patch("app._get_file_hash_sync") as mock_hash:
        mock_hash.return_value = "hash_123"

        filepath = "/tmp/dummy_model.enc"
        mtime = 1000.0
        size = 500

        # 1. First call - should calculate hash
        h1 = await get_file_hash(filepath, mtime=mtime, size=size)
        assert h1 == "hash_123"
        assert mock_hash.call_count == 1

        # 2. Simulate TTL Expiry
        # Instead of mocking time, we set TTL to a small value (or negative)
        # We need to patch app.HASH_CACHE_TTL

        with patch("app.HASH_CACHE_TTL", 0):
            # 3. Call again with SAME mtime/size
            # Even though TTL is 0 (expired), smart caching should save us
            h2 = await get_file_hash(filepath, mtime=mtime, size=size)

            assert h2 == "hash_123"
            assert mock_hash.call_count == 1, "Should use cache when mtime/size match, even if TTL expired"

            # 4. Call with DIFFERENT mtime
            # TTL is expired, AND mtime mismatch -> Re-hash
            h3 = await get_file_hash(filepath, mtime=mtime + 1, size=size)
            assert h3 == "hash_123"
            assert mock_hash.call_count == 2, "Should re-hash when mtime changes"

            # 5. Call with DIFFERENT size
            # TTL is expired, AND size mismatch -> Re-hash
            h4 = await get_file_hash(filepath, mtime=mtime + 1, size=size + 10)
            assert h4 == "hash_123"
            assert mock_hash.call_count == 3, "Should re-hash when size changes"
