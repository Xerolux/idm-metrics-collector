from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

# Hardcoded "Public" Key for Community Models.
# This prevents casual copying but is technically extractable.
# In a real scenario, this might be fetched from the server or derived dynamically.
COMMUNITY_KEY = b"gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="


def encrypt_file(input_path, output_path, key=None):
    """Encrypt a file."""
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
    """Decrypt a file."""
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
    """Load encrypted model directly into memory (bytes)."""
    if key is None:
        key = COMMUNITY_KEY

    f = Fernet(key)
    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    return f.decrypt(encrypted_data)
