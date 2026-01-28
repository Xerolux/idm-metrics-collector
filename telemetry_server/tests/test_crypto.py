import pytest
import os
import sys
import pickle
import json

# Add root to path to import ml_service
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from ml_service.utils.crypto import load_encrypted_model
from telemetry_server.scripts.export_model import export_model


@pytest.fixture
def temp_dir(tmp_path):
    d = tmp_path / "model_test"
    d.mkdir()
    return d


def test_roundtrip_encryption(temp_dir):
    # 1. Create a dummy model
    input_file = temp_dir / "test_model.pkl"
    original_data = {"a": 1, "b": [1, 2, 3]}

    with open(input_file, "wb") as f:
        pickle.dump(original_data, f)

    # 2. Export (Encrypt & Sign)
    output_dir = temp_dir / "output"
    export_model(str(input_file), str(output_dir))

    exported_file = output_dir / "model.enc"
    assert exported_file.exists()

    # 3. Verify it is JSON
    with open(exported_file, "rb") as f:
        content = f.read()
        envelope = json.loads(content)
        assert "signature" in envelope
        assert "payload" in envelope
        assert envelope["version"] == "2.0"

    # 4. Load (Decrypt & Verify)
    loaded_data = load_encrypted_model(str(exported_file))

    assert loaded_data is not None
    assert loaded_data == original_data


def test_tampered_signature(temp_dir):
    # 1. Create model
    input_file = temp_dir / "test_model.pkl"
    with open(input_file, "wb") as f:
        pickle.dump({"foo": "bar"}, f)

    # 2. Export
    output_dir = temp_dir / "output"
    export_model(str(input_file), str(output_dir))
    exported_file = output_dir / "model.enc"

    # 3. Tamper with signature
    with open(exported_file, "r") as f:
        envelope = json.load(f)

    envelope["signature"] = "deadbeef" * 8  # Invalid signature

    with open(exported_file, "w") as f:
        json.dump(envelope, f)

    # 4. Try to load
    loaded_data = load_encrypted_model(str(exported_file))
    assert loaded_data is None


def test_tampered_payload(temp_dir):
    # 1. Create model
    input_file = temp_dir / "test_model.pkl"
    with open(input_file, "wb") as f:
        pickle.dump({"foo": "bar"}, f)

    # 2. Export
    output_dir = temp_dir / "output"
    export_model(str(input_file), str(output_dir))
    exported_file = output_dir / "model.enc"

    # 3. Tamper with payload
    with open(exported_file, "r") as f:
        envelope = json.load(f)

    # Change first char of payload
    orig_payload = envelope["payload"]
    new_payload = "A" + orig_payload[1:]
    envelope["payload"] = new_payload

    with open(exported_file, "w") as f:
        json.dump(envelope, f)

    # 4. Try to load
    loaded_data = load_encrypted_model(str(exported_file))
    assert loaded_data is None


def test_tampered_metadata(temp_dir):
    # 1. Create model
    input_file = temp_dir / "test_model.pkl"
    with open(input_file, "wb") as f:
        pickle.dump({"foo": "bar"}, f)

    # 2. Export
    output_dir = temp_dir / "output"
    export_model(str(input_file), str(output_dir))
    exported_file = output_dir / "model.enc"

    # 3. Tamper with metadata
    with open(exported_file, "r") as f:
        envelope = json.load(f)

    # Change filename in metadata
    envelope["metadata"]["filename"] = "hacked.pkl"

    with open(exported_file, "w") as f:
        json.dump(envelope, f)

    # 4. Try to load (Should fail because signature covers metadata now)
    loaded_data = load_encrypted_model(str(exported_file))
    assert loaded_data is None
