import unittest
from unittest.mock import patch, MagicMock
import json
import base64
from idm_logger.privatebin import upload, b58encode


class TestPrivateBin(unittest.TestCase):
    def test_b58encode(self):
        # 'hello' in hex is 68656c6c6f = 448378203247
        # 448378203247 in base58 is Cn8eVZg
        self.assertEqual(b58encode(b"hello"), b"Cn8eVZg")
        self.assertEqual(b58encode(b"\x00\x00hello"), b"11Cn8eVZg")

    @patch("requests.post")
    def test_upload(self, mock_post):
        # Setup mock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": 0,
            "id": "123456",
            "url": "https://paste.blueml.eu?123456",
            "deletetoken": "abc",
        }
        mock_post.return_value = mock_resp

        # Call upload
        link = upload("This is a test log")

        # Verify Link
        self.assertTrue(link.startswith("https://paste.blueml.eu?123456#"))
        key_part = link.split("#")[1]
        self.assertTrue(len(key_part) > 0)

        # Verify Payload
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        self.assertEqual(payload["v"], 2)
        self.assertIn("adata", payload)
        self.assertIn("ct", payload)

        # Verify ADATA structure
        adata = payload["adata"]
        self.assertIsInstance(adata, list)
        self.assertEqual(len(adata), 4)  # [params, format, open, burn]
        params = adata[0]
        self.assertEqual(
            len(params), 8
        )  # [iv, salt, iter, ks, ts, algo, mode, compression]

        # Verify Encryption is reproducible (can decrypt)
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes

        iv_b64 = params[0]
        salt_b64 = params[1]
        iter_count = params[2]

        iv = base64.b64decode(iv_b64)
        salt = base64.b64decode(salt_b64)
        ct_blob = base64.b64decode(payload["ct"])

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iter_count,
        )
        derived_key = kdf.derive(key_part.encode("utf-8"))

        aesgcm = AESGCM(derived_key)

        # Verify using correct AAD structure (full adata array)
        payload_adata = [params, "plaintext", 0, 0]
        payload_adata_json = json.dumps(payload_adata, separators=(",", ":"))

        plaintext = aesgcm.decrypt(iv, ct_blob, payload_adata_json.encode("utf-8"))
        self.assertEqual(plaintext.decode("utf-8"), "This is a test log")
