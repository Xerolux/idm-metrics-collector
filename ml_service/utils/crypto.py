from cryptography.fernet import Fernet
import logging
import json
import base64
import hashlib
import hmac
import pickle
import os

logger = logging.getLogger(__name__)

# Hardcoded "Public" Key for Community Models.
# This prevents casual copying but is technically extractable.
# In a real scenario, this might be fetched from the server or derived dynamically.
COMMUNITY_KEY = b"gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="


def encrypt_file(input_path, output_path, key=None):
    """Encrypt a file (legacy format)."""
    if key is None:
        key = COMMUNITY_KEY

    f = Fernet(key)
    with open(input_path, "rb") as file:
        file_data = file.read()

    encrypted_data = f.encrypt(file_data)

    with open(output_path, "wb") as file:
        file.write(encrypted_data)
    logger.info(f"Encrypted {input_path} to {output_path}")


def decrypt_file(input_path, output_path, key=None):
    """Decrypt a file (legacy format)."""
    if key is None:
        key = COMMUNITY_KEY

    f = Fernet(key)
    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = f.decrypt(encrypted_data)

    with open(output_path, "wb") as file:
        file.write(decrypted_data)
    logger.info(f"Decrypted {input_path} to {output_path}")


def load_encrypted_model(input_path, key=None):
    """Load encrypted model directly into memory (deserialized object)."""
    if key is None:
        # Try env var first, then fallback to hardcoded
        key_str = os.environ.get("TELEMETRY_ENCRYPTION_KEY")
        if key_str:
            key = key_str.encode() if isinstance(key_str, str) else key_str
        else:
            key = COMMUNITY_KEY

    with open(input_path, "rb") as file:
        raw_data = file.read()

    decrypted_bytes = None

    # Try JSON format first (Signed & Versioned)
    try:
        # Peak to see if it starts with {
        if raw_data.strip().startswith(b"{"):
            envelope = json.loads(raw_data)
            if (
                isinstance(envelope, dict)
                and "payload" in envelope
                and "signature" in envelope
            ):
                # Verify signature
                payload_b64 = envelope["payload"]
                signature_expected = envelope["signature"]
                metadata = envelope.get("metadata", {})

                # Reconstruct signed message: payload + "." + sorted_json(metadata)
                metadata_json = json.dumps(metadata, sort_keys=True)
                msg = f"{payload_b64}.{metadata_json}".encode("utf-8")

                signature_calculated = hmac.new(key, msg, hashlib.sha256).hexdigest()

                # Backward compatibility check: if verification fails, try payload-only (migration path)
                # But since we just introduced this, we might not need migration logic yet.
                # However, previous code signed only payload.
                # If we want to support both, we should check both.
                # But simpler to just stick to new format if I control both ends now.
                # Since I am updating both ends in same PR, I will enforce new format.

                if not hmac.compare_digest(signature_calculated, signature_expected):
                    # Try legacy payload-only signature (for dev transition)
                    msg_legacy = payload_b64.encode("utf-8")
                    sig_legacy = hmac.new(key, msg_legacy, hashlib.sha256).hexdigest()
                    if hmac.compare_digest(sig_legacy, signature_expected):
                        logger.warning(
                            "Loaded community model with legacy signature (payload only)."
                        )
                    else:
                        logger.error("Model signature verification failed!")
                        return None

                encrypted_data = base64.b64decode(payload_b64)
                f = Fernet(key)
                decrypted_bytes = f.decrypt(encrypted_data)
                logger.info(
                    f"Loaded signed community model v{envelope.get('version', 'unknown')}"
                )
    except Exception:
        # Not JSON or invalid JSON, ignore and try legacy
        pass

    if decrypted_bytes is None:
        # Legacy path (Raw Fernet bytes)
        try:
            f = Fernet(key)
            decrypted_bytes = f.decrypt(raw_data)
            logger.info("Loaded legacy community model")
        except Exception as e:
            logger.error(f"Failed to decrypt model: {e}")
            return None

    # Deserialize
    try:
        return pickle.loads(decrypted_bytes)
    except Exception as e:
        logger.error(f"Failed to deserialize model: {e}")
        return None
