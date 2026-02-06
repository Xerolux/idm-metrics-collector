import pytest
import os
import hashlib
import sys
import tempfile

# Ensure telemetry_server is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import _get_file_hash_sync, get_file_hash


def test_get_file_hash_sync_correctness():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        # Create a file larger than 4KB to test chunking/loop logic
        content = b"test content" * 1000
        tmp.write(content)
        tmp_path = tmp.name

    try:
        expected_hash = hashlib.sha256(content).hexdigest()
        calculated_hash = _get_file_hash_sync(tmp_path)
        assert calculated_hash == expected_hash, "Sync hash calculation failed"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_get_file_hash_async_correctness():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = b"async test content"
        tmp.write(content)
        tmp_path = tmp.name

    try:
        expected_hash = hashlib.sha256(content).hexdigest()
        calculated_hash = await get_file_hash(tmp_path)
        assert calculated_hash == expected_hash, "Async hash calculation failed"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_file_hash_missing_file():
    assert _get_file_hash_sync("non_existent_file.txt") is None
