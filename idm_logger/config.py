import json
import logging
import os
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db

logger = logging.getLogger(__name__)

# Use DATA_DIR environment variable or current directory
DATA_DIR = os.environ.get("DATA_DIR", ".")
KEY_FILE = os.path.join(DATA_DIR, ".secret.key")

# Default values synchronized with docker-compose.yml
DOCKER_DEFAULTS = {
    "influx": {
        "url": "http://idm-influxdb:8086",
        "org": "my-org",
        "bucket": "idm",
        "token": "my-super-secret-token-change-me"
    }
}


class Config:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
        self.data = self._load_data()
        # Apply environment variable overrides
        self._apply_env_overrides()

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
        if not value:
            return ""
        return self.cipher.encrypt(value.encode()).decode()

    def _decrypt(self, token):
        if not token:
            return ""
        try:
            return self.cipher.decrypt(token.encode()).decode()
        except Exception:
            return ""

    def _apply_env_overrides(self):
        """Apply environment variable overrides for Docker deployment."""
        # InfluxDB settings from environment
        if os.environ.get("INFLUX_URL"):
            self.data["influx"]["url"] = os.environ["INFLUX_URL"]
        if os.environ.get("INFLUX_ORG"):
            self.data["influx"]["org"] = os.environ["INFLUX_ORG"]
        if os.environ.get("INFLUX_BUCKET"):
            self.data["influx"]["bucket"] = os.environ["INFLUX_BUCKET"]
        if os.environ.get("INFLUX_TOKEN"):
            self.data["influx"]["token"] = os.environ["INFLUX_TOKEN"]

        # IDM settings from environment
        if os.environ.get("IDM_HOST"):
            self.data["idm"]["host"] = os.environ["IDM_HOST"]
        if os.environ.get("IDM_PORT"):
            self.data["idm"]["port"] = int(os.environ["IDM_PORT"])

        # Web settings from environment
        if os.environ.get("WEB_PORT"):
            self.data["web"]["port"] = int(os.environ["WEB_PORT"])
        if os.environ.get("WEB_WRITE_ENABLED"):
            self.data["web"]["write_enabled"] = os.environ["WEB_WRITE_ENABLED"].lower() in ("true", "1", "yes")

        # Network Security settings from environment
        if os.environ.get("NETWORK_SECURITY_ENABLED"):
            self.data["network_security"]["enabled"] = os.environ["NETWORK_SECURITY_ENABLED"].lower() in ("true", "1", "yes")
        if os.environ.get("NETWORK_SECURITY_WHITELIST"):
            self.data["network_security"]["whitelist"] = [x.strip() for x in os.environ["NETWORK_SECURITY_WHITELIST"].split(",") if x.strip()]
        if os.environ.get("NETWORK_SECURITY_BLACKLIST"):
            self.data["network_security"]["blacklist"] = [x.strip() for x in os.environ["NETWORK_SECURITY_BLACKLIST"].split(",") if x.strip()]

        # Logging settings
        if os.environ.get("LOG_LEVEL"):
            self.data["logging"]["level"] = os.environ["LOG_LEVEL"].upper()
        if os.environ.get("LOG_INTERVAL"):
            self.data["logging"]["interval"] = int(os.environ["LOG_INTERVAL"])

    def _load_data(self):
        # Load from DB, structure into dict like old yaml
        raw = db.get_setting("config")
        if raw:
            try:
                data = json.loads(raw)
                # Decrypt sensitive fields
                if "influx" in data:
                    data["influx"]["token"] = self._decrypt(data["influx"].get("encrypted_token", ""))
                    data["influx"]["password"] = self._decrypt(data["influx"].get("encrypted_password", ""))
                return data
            except json.JSONDecodeError:
                pass

        # Default structure with Docker-friendly defaults
        return {
            "idm": {
                "host": "",
                "port": 502,
                "circuits": ["A"],
                "zones": []
            },
            "influx": {
                "version": 2,
                "url": DOCKER_DEFAULTS["influx"]["url"],
                "org": DOCKER_DEFAULTS["influx"]["org"],
                "bucket": DOCKER_DEFAULTS["influx"]["bucket"],
                "token": DOCKER_DEFAULTS["influx"]["token"],
                "username": "",
                "password": "",
                "database": "idm"
            },
            "web": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 5000,
                "write_enabled": False
            },
            "network_security": {
                "enabled": False,
                "whitelist": [],
                "blacklist": []
            },
            "logging": {
                "interval": 60,
                "realtime_mode": False,
                "level": "INFO"
            },
            "setup_completed": False
        }

    def save(self):
        # Encrypt sensitive fields before saving
        to_save = json.loads(json.dumps(self.data))

        if "influx" in to_save:
            to_save["influx"]["encrypted_token"] = self._encrypt(to_save["influx"].get("token", ""))
            to_save["influx"]["encrypted_password"] = self._encrypt(to_save["influx"].get("password", ""))
            # Remove plain text from storage dict
            if "token" in to_save["influx"]:
                del to_save["influx"]["token"]
            if "password" in to_save["influx"]:
                del to_save["influx"]["password"]

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

    def set(self, path, value):
        """Set a configuration value by path."""
        keys = path.split('.')
        data = self.data
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[keys[-1]] = value

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

    def reload(self):
        """Reload configuration from database."""
        self.data = self._load_data()
        self._apply_env_overrides()

    def get_flask_secret_key(self):
        """Returns the stable secret key for Flask sessions."""
        # Use the persistent Fernet key as the Flask secret key
        return self.key


config = Config()
