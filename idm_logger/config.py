import json
import logging
import os
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db

logger = logging.getLogger(__name__)

KEY_FILE = ".secret.key"

class Config:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
        self.data = self._load_data()

    def _load_or_create_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            # Ensure restricted permissions
            os.chmod(KEY_FILE, 0o600)
            return key

    def _encrypt(self, value):
        if not value: return ""
        return self.cipher.encrypt(value.encode()).decode()

    def _decrypt(self, token):
        if not token: return ""
        try:
            return self.cipher.decrypt(token.encode()).decode()
        except Exception:
            return ""

    def _load_data(self):
        # Load from DB, structure into dict like old yaml
        # We flat store in DB, but app expects nested dict for some parts?
        # Let's rebuild the structure.

        raw = db.get_setting("config")
        if raw:
            try:
                data = json.loads(raw)
                # Decrypt sensitive fields
                if "influx" in data:
                    data["influx"]["token"] = self._decrypt(data["influx"].get("encrypted_token", ""))
                    data["influx"]["password"] = self._decrypt(data["influx"].get("encrypted_password", ""))

                # Check for admin password hash (stored separately or in config?)
                # Let's keep admin_password_hash in config dict for simplicity of loading
                return data
            except json.JSONDecodeError:
                pass

        # Default structure if not found
        return {
            "idm": {"host": "", "port": 502, "circuits": ["A"]},
            "influx": {"version": 2, "url": "http://localhost:8086", "org": "", "bucket": "", "token": "", "username": "", "password": "", "database": ""},
            "web": {"enabled": True, "host": "0.0.0.0", "port": 5000, "write_enabled": False},
            "logging": {"interval": 60, "level": "INFO"},
            "setup_completed": False
        }

    def save(self):
        # Encrypt sensitive fields before saving
        to_save = self.data.copy()

        # Helper to avoid modifying self.data in place with encrypted values
        # Deep copy needed? Yes.
        to_save = json.loads(json.dumps(self.data))

        if "influx" in to_save:
            to_save["influx"]["encrypted_token"] = self._encrypt(to_save["influx"].get("token", ""))
            to_save["influx"]["encrypted_password"] = self._encrypt(to_save["influx"].get("password", ""))
            # Remove plain text from storage dict
            if "token" in to_save["influx"]: del to_save["influx"]["token"]
            if "password" in to_save["influx"]: del to_save["influx"]["password"]

        db.set_setting("config", json.dumps(to_save))

    def get(self, path, default=None):
        keys = path.split('.')
        val = self.data
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return default
        return val

    def set_admin_password(self, password):
        self.data["web"]["admin_password_hash"] = generate_password_hash(password)
        self.save()

    def check_admin_password(self, password):
        # Allow default "admin" if no hash set (legacy/migration)
        if "admin_password_hash" not in self.data["web"]:
             # Fallback
             return password == "admin"
        return check_password_hash(self.data["web"]["admin_password_hash"], password)

    def is_setup(self):
        return self.data.get("setup_completed", False)

config = Config()
