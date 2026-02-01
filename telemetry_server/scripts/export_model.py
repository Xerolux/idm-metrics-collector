# Xerolux 2026
import argparse
import os
import json
import base64
import hashlib
import hmac
import time
from cryptography.fernet import Fernet


def export_model(input_file, output_dir=None, output_file=None):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    # Determine destination
    if output_file:
        dest = output_file
        dest_dir = os.path.dirname(dest)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
    elif output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        dest = os.path.join(output_dir, "model.enc")
    else:
        print("Error: Either output_dir or output_file must be provided")
        return

    # Get key from environment
    key_str = os.environ.get("TELEMETRY_ENCRYPTION_KEY")
    if not key_str:
        raise ValueError("TELEMETRY_ENCRYPTION_KEY environment variable is not set")

    key = key_str.encode() if isinstance(key_str, str) else key_str

    f = Fernet(key)

    with open(input_file, "rb") as file:
        file_data = file.read()

    # Encrypt
    encrypted_data = f.encrypt(file_data)

    # Prepare payload
    payload_b64 = base64.b64encode(encrypted_data).decode("utf-8")

    # Create metadata
    metadata = {
        "timestamp": time.time(),
        "filename": os.path.basename(input_file),
        "size_original": len(file_data),
    }

    # Create structure for signing
    envelope = {"version": "2.0", "metadata": metadata, "payload": payload_b64}

    # Sign payload AND metadata
    # Format: payload_b64 + "." + canonical_json(metadata)
    metadata_json = json.dumps(metadata, sort_keys=True)
    msg = f"{payload_b64}.{metadata_json}".encode("utf-8")

    signature = hmac.new(key, msg, hashlib.sha256).hexdigest()

    envelope["signature"] = signature

    with open(dest, "w") as file:
        json.dump(envelope, file, indent=2)

    print(f"Model encrypted, signed, and exported to {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input pickle file")
    parser.add_argument(
        "--output-dir", type=str, required=True, help="Output directory"
    )
    args = parser.parse_args()

    export_model(args.input, output_dir=args.output_dir)
