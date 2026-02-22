import pytest
import os
import time
from unittest.mock import patch

# Ensure we can import app
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import get_file_hash, _file_hash_cache

@pytest.mark.asyncio
async def test_smart_caching(tmp_path):
    """
    Test that get_file_hash uses file metadata (mtime/size) to avoid re-hashing
    files that haven't changed, even if the TTL has expired.
    """
    # Setup temp file
    test_file = tmp_path / "test_model.enc"
    test_file.write_text("initial content", encoding="utf-8")
    filepath = str(test_file)

    # Patch MODEL_DIR to ensure security check passes
    with patch("app.MODEL_DIR", str(tmp_path)):
        # Patch HASH_CACHE_TTL to a small value
        with patch("app.HASH_CACHE_TTL", 0.1):

            # 1. Initial Call - should calculate hash
            # Clear cache for this file just in case
            if filepath in _file_hash_cache:
                del _file_hash_cache[filepath]

            # Call original function to get real hash
            real_hash = await get_file_hash(filepath)
            assert real_hash is not None

            # Verify cache entry exists
            assert filepath in _file_hash_cache

            # 2. Wait for TTL expiry
            time.sleep(0.15)

            # 3. Call again - file unchanged
            # We wrap _get_file_hash_sync to see if it gets called.

            with patch("app._get_file_hash_sync", side_effect=lambda f: "recalculated_hash") as mock_hash:
                 hash2 = await get_file_hash(filepath)

                 # After optimization:
                 # TTL expired -> checks stat -> unchanged -> returns cached real_hash
                 assert hash2 == real_hash, "Should return cached hash if file unchanged"
                 assert mock_hash.call_count == 0, "Should not re-calculate hash if file unchanged"

        # 4. Modify file
        # Ensure timestamp changes
        time.sleep(0.1) # filesystem resolution
        test_file.write_text("new content", encoding="utf-8")

        # 5. Call again - should re-calculate
        # We assume TTL (0.1s) has expired since step 3 or we wait again.
        time.sleep(0.15)

        with patch("app.HASH_CACHE_TTL", 0.1):
            with patch("app._get_file_hash_sync", side_effect=lambda f: "new_hash_from_calc") as mock_hash_new:
                 hash3 = await get_file_hash(filepath)

                 # Should detect change and re-calculate
                 assert hash3 == "new_hash_from_calc"
                 assert mock_hash_new.call_count == 1
