import pytest
import os
import tempfile
import time
import shutil
from unittest.mock import patch


@pytest.fixture
def temp_model_dir():
    # Create temp dir
    tmp_dir = tempfile.mkdtemp()
    old_model_dir = os.environ.get("MODEL_DIR")
    os.environ["MODEL_DIR"] = tmp_dir

    # Reload app config (this is tricky since app is already imported, but app.py reads env at module level)
    # We might need to patch MODEL_DIR where it is used.
    # But app.py uses global MODEL_DIR.
    # So we patch 'app.MODEL_DIR'
    with patch("app.MODEL_DIR", tmp_dir):
        yield tmp_dir

    # Cleanup
    shutil.rmtree(tmp_dir)
    if old_model_dir:
        os.environ["MODEL_DIR"] = old_model_dir


@pytest.mark.asyncio
async def test_parallel_hashing(client, temp_model_dir):
    # Create dummy models
    count = 10
    size_mb = 10  # 10MB to ensure hashing takes noticeable time

    print(f"\nCreating {count} dummy models of {size_mb}MB...")
    for i in range(count):
        with open(os.path.join(temp_model_dir, f"model_{i}.enc"), "wb") as f:
            f.write(os.urandom(size_mb * 1024 * 1024))

    headers = {
        "Authorization": "Bearer change-me-to-something-secure"
    }  # Default token in tests usually
    # Check app.py for default token: "change-me-to-something-secure" if not set
    # But in test environment it might be different.
    # Let's check app.AUTH_TOKEN
    from app import AUTH_TOKEN

    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    print("Calling /api/v1/models...")
    start = time.time()
    response = client.get("/api/v1/models", headers=headers)
    end = time.time()

    duration = (end - start) * 1000
    print(f"Response time: {duration:.2f} ms")

    assert response.status_code == 200
    data = response.json()
    assert len(data["models"]) == count

    # Estimate sequential time:
    # 10MB hashing might take ~30ms. 10 files = 300ms.
    # Parallel should be closer to max(single_hash) + overhead ~ 40-50ms.
    # But we don't have a baseline here.
    # This test primarily verifies correctness and that it doesn't timeout/crash.
