# SPDX-License-Identifier: MIT
import os
import json
import base64
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Base58 Alphabet (Bitcoin)
ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(v):
    """Base58 encode bytes."""
    if isinstance(v, bytes):
        long_value = int.from_bytes(v, "big")

        # Handle leading zeros
        nPad = 0
        for c in v:
            if c == 0:
                nPad += 1
            else:
                break
    else:
        # If integer (fallback)
        long_value = v
        nPad = 0

    output = b""
    while long_value:
        long_value, idx = divmod(long_value, 58)
        output = ALPHABET[idx : idx + 1] + output

    return (ALPHABET[0:1] * nPad) + output


def upload(text, url="https://paste.blueml.eu"):
    """
    Upload text to PrivateBin (v2) with client-side encryption.
    """
    # 1. Generate Key (32 bytes)
    key = os.urandom(32)
    key_b58 = b58encode(key).decode("utf-8")

    # 2. Parameters
    iv = os.urandom(12)  # 12 bytes for GCM
    salt = os.urandom(8)
    iterations = 100000
    keysize = 256
    tagsize = 128

    # 3. Key Derivation (PBKDF2)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=keysize // 8,
        salt=salt,
        iterations=iterations,
    )
    # The key in URL fragment is used as the password
    derived_key = kdf.derive(key_b58.encode("utf-8"))

    # 4. Prepare ADATA (Authenticated Data)
    # [iv, salt, iter, ks, ts, algo, mode, compression]
    # All bytes base64 encoded
    adata = [
        base64.b64encode(iv).decode("utf-8"),
        base64.b64encode(salt).decode("utf-8"),
        iterations,
        keysize,
        tagsize,
        "aes",
        "gcm",
        "none",
    ]

    # 5. Prepare Payload Structure (used for AAD)
    # The full array is used as AAD: [[params], "plaintext", 0, 0]
    payload_adata = [adata, "plaintext", 0, 0]
    payload_adata_json = json.dumps(payload_adata, separators=(",", ":"))

    # 6. Encrypt
    aesgcm = AESGCM(derived_key)
    # cryptography AESGCM.encrypt appends the tag to the ciphertext
    # The AAD MUST be the full payload_adata structure
    ct_blob = aesgcm.encrypt(
        iv, text.encode("utf-8"), payload_adata_json.encode("utf-8")
    )
    ct_b64 = base64.b64encode(ct_blob).decode("utf-8")

    # 7. Payload
    payload = {
        "v": 2,
        "adata": payload_adata,
        "ct": ct_b64,
        "meta": {"expire": "1week"},
    }

    # 8. Post
    headers = {
        "X-Requested-With": "JSONHttpRequest",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == 0:
            # Construct URL
            # If server returns 'url' field, use it.
            # Otherwise construct from base url + '?' + id
            base_url = data.get("url")
            if not base_url:
                base_url = f"{url}?{data.get('id')}"

            return f"{base_url}#{key_b58}"
        else:
            raise Exception(f"PrivateBin Error: {data.get('message')}")
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")
