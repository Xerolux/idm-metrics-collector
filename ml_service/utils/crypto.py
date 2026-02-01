import os
import json
import base64
import hmac
import hashlib
import pickle
import io
from cryptography.fernet import Fernet


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Only allow safe modules and classes
        # This list should be updated as needed for the ML model components
        safe_modules = {
            "river",
            "numpy",
            "collections",
            "datetime",
            "math",
        }

        # Allow submodules of safe modules (simple prefix check)
        is_safe_module = any(
            module == m or module.startswith(m + ".") for m in safe_modules
        )

        if is_safe_module:
            return super().find_class(module, name)

        # Handle builtins safely
        if module == "builtins":
            if name in {
                "dict",
                "list",
                "set",
                "tuple",
                "str",
                "int",
                "float",
                "bool",
                "bytes",
                "NoneType",
            }:
                return super().find_class(module, name)

        raise pickle.UnpicklingError(f"Global '{module}.{name}' is forbidden")


def load_encrypted_model(filepath):
    """
    Load, verify, and decrypt a model file.
    Returns the unpickled object or None on failure.
    Requires TELEMETRY_ENCRYPTION_KEY environment variable to be set.
    """
    # Security: Require environment variable, do not use hardcoded default.
    key_val = os.environ.get("TELEMETRY_ENCRYPTION_KEY")
    if not key_val:
        return None

    if isinstance(key_val, str):
        key = key_val.encode("utf-8")
    else:
        key = key_val

    try:
        with open(filepath, "rb") as f:
            envelope = json.load(f)

        # 1. Extract fields
        if (
            "payload" not in envelope
            or "signature" not in envelope
            or "metadata" not in envelope
        ):
            return None

        payload_b64 = envelope["payload"]
        metadata = envelope["metadata"]
        signature = envelope["signature"]

        # 2. Verify signature
        # Reconstruct message to sign: payload + "." + canonical_json(metadata)
        metadata_json = json.dumps(metadata, sort_keys=True)
        msg = f"{payload_b64}.{metadata_json}".encode("utf-8")

        expected_sig = hmac.new(key, msg, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, signature):
            return None

        # 3. Decrypt
        f = Fernet(key)
        encrypted_data = base64.b64decode(payload_b64)
        decrypted_data = f.decrypt(encrypted_data)

        # 4. Unpickle
        return RestrictedUnpickler(io.BytesIO(decrypted_data)).load()

    except Exception:
        return None
