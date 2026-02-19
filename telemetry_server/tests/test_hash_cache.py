import pytest
from unittest.mock import patch, MagicMock
import time
import sys
from pathlib import Path

# Add telemetry_server to path if needed
if str(Path(__file__).parent.parent) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent))

try:
    import app
except ImportError:
    sys.path.append("telemetry_server")
    import app

@pytest.mark.asyncio
async def test_smart_caching_logic():
    filepath = "/tmp/test_smart_cache.enc"

    # Mock os.stat result
    mock_stat = MagicMock()
    mock_stat.st_mtime = 1000.0
    mock_stat.st_size = 1024

    with patch("os.stat", return_value=mock_stat), \
         patch("app._get_file_hash_sync") as mock_calc_hash:

        mock_calc_hash.return_value = "hash_v1"

        # Clear cache
        app._file_hash_cache.clear()

        # 1. First call: Cache Miss -> Calculate
        h1 = await app.get_file_hash(filepath)
        assert h1 == "hash_v1"
        assert mock_calc_hash.call_count == 1

        # 2. Second call: Cache Hit (Time Valid) -> No Calculate
        h2 = await app.get_file_hash(filepath)
        assert h2 == "hash_v1"
        assert mock_calc_hash.call_count == 1

        # 3. Third call: Time Expired but File Unchanged (mtime/size same) -> No Calculate (Smart Cache)
        # Manually expire the cache entry timestamp
        entry = app._file_hash_cache[filepath]
        expired_time = time.time() - app.HASH_CACHE_TTL - 100

        if len(entry) == 3: # New format (hash, timestamp, key)
            app._file_hash_cache[filepath] = (entry[0], expired_time, entry[2])
        else: # Old format (hash, timestamp)
            app._file_hash_cache[filepath] = (entry[0], expired_time)

        h3 = await app.get_file_hash(filepath)
        assert h3 == "hash_v1"

        # KEY ASSERTION:
        # In current code: this fails because it re-calculates (call_count becomes 2)
        # In new code: this passes because stat matches (call_count stays 1)
        assert mock_calc_hash.call_count == 1, "Should verify via stat and skip hash calculation"

        # 4. Fourth call: File Changed (mtime changed) -> Calculate
        mock_stat.st_mtime = 2000.0
        mock_calc_hash.return_value = "hash_v2"

        h4 = await app.get_file_hash(filepath)
        assert h4 == "hash_v2"
        assert mock_calc_hash.call_count == 2
