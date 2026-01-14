import json
import logging
import os
from cryptography.fernet import Fernet, InvalidToken
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db

logger = logging.getLogger(__name__)

# Use DATA_DIR environment variable or current directory
DATA_DIR = os.environ.get("DATA_DIR", ".")
KEY_FILE = os.path.join(DATA_DIR, ".secret.key")

# Default values synchronized with docker-compose.yml
DOCKER_DEFAULTS = {
    "metrics": {
        "url": "http://victoriametrics:8428/write",
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
        except (InvalidToken, ValueError, AttributeError) as e:
            logger.warning(f"Failed to decrypt token: {e}")
            return ""

    def _apply_env_overrides(self):
        """Apply environment variable overrides for Docker deployment."""
        # Metrics settings from environment
        if os.environ.get("METRICS_URL"):
            self.data["metrics"]["url"] = os.environ["METRICS_URL"]

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

        # MQTT settings from environment
        if os.environ.get("MQTT_ENABLED"):
            self.data["mqtt"]["enabled"] = os.environ["MQTT_ENABLED"].lower() in ("true", "1", "yes")
        if os.environ.get("MQTT_BROKER"):
            self.data["mqtt"]["broker"] = os.environ["MQTT_BROKER"]
        if os.environ.get("MQTT_PORT"):
            self.data["mqtt"]["port"] = int(os.environ["MQTT_PORT"])
        if os.environ.get("MQTT_USERNAME"):
            self.data["mqtt"]["username"] = os.environ["MQTT_USERNAME"]
        if os.environ.get("MQTT_PASSWORD"):
            self.data["mqtt"]["password"] = os.environ["MQTT_PASSWORD"]
        if os.environ.get("MQTT_USE_TLS"):
            self.data["mqtt"]["use_tls"] = os.environ["MQTT_USE_TLS"].lower() in ("true", "1", "yes")
        if os.environ.get("MQTT_TOPIC_PREFIX"):
            self.data["mqtt"]["topic_prefix"] = os.environ["MQTT_TOPIC_PREFIX"]
        if os.environ.get("MQTT_HA_DISCOVERY_ENABLED"):
            self.data["mqtt"]["ha_discovery_enabled"] = os.environ["MQTT_HA_DISCOVERY_ENABLED"].lower() in ("true", "1", "yes")
        if os.environ.get("MQTT_HA_DISCOVERY_PREFIX"):
            self.data["mqtt"]["ha_discovery_prefix"] = os.environ["MQTT_HA_DISCOVERY_PREFIX"]

        # Signal settings from environment
        if os.environ.get("SIGNAL_ENABLED"):
            self.data["signal"]["enabled"] = os.environ["SIGNAL_ENABLED"].lower() in ("true", "1", "yes")
        if os.environ.get("SIGNAL_SENDER"):
            self.data["signal"]["sender"] = os.environ["SIGNAL_SENDER"]
        if os.environ.get("SIGNAL_RECIPIENTS"):
            self.data["signal"]["recipients"] = [x.strip() for x in os.environ["SIGNAL_RECIPIENTS"].split(",") if x.strip()]
        if os.environ.get("SIGNAL_CLI_PATH"):
            self.data["signal"]["cli_path"] = os.environ["SIGNAL_CLI_PATH"]

        # AI settings from environment
        if os.environ.get("AI_ENABLED"):
            self.data["ai"]["enabled"] = os.environ["AI_ENABLED"].lower() in ("true", "1", "yes")
        if os.environ.get("AI_SENSITIVITY"):
             try:
                 self.data["ai"]["sensitivity"] = float(os.environ["AI_SENSITIVITY"])
             except ValueError:
                 pass

        # Update settings from environment
        if os.environ.get("UPDATES_ENABLED"):
            self.data["updates"]["enabled"] = os.environ["UPDATES_ENABLED"].lower() in ("true", "1", "yes")
        if os.environ.get("UPDATES_INTERVAL_HOURS"):
            self.data["updates"]["interval_hours"] = int(os.environ["UPDATES_INTERVAL_HOURS"])
        if os.environ.get("UPDATES_MODE"):
            self.data["updates"]["mode"] = os.environ["UPDATES_MODE"]
        if os.environ.get("UPDATES_TARGET"):
            self.data["updates"]["target"] = os.environ["UPDATES_TARGET"]

    def _merge_dicts(self, default, override):
        """Recursively merge override dictionary into default."""
        new_dict = default.copy()
        for k, v in override.items():
            if k in new_dict and isinstance(new_dict[k], dict) and isinstance(v, dict):
                new_dict[k] = self._merge_dicts(new_dict[k], v)
            else:
                new_dict[k] = v
        return new_dict

    def _load_data(self):
        defaults = {
            "idm": {
                "host": "",
                "port": 502,
                "circuits": ["A"],
                "zones": []
            },
            "metrics": {
                "url": DOCKER_DEFAULTS["metrics"]["url"],
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
                "interval": 30,
                "realtime_mode": False,
                "level": "INFO"
            },
            "mqtt": {
                "enabled": False,
                "broker": "",
                "port": 1883,
                "username": "",
                "password": "",
                "use_tls": False,
                "topic_prefix": "idm/heatpump",
                "publish_interval": 60,
                "qos": 1,
                "ha_discovery_enabled": False,
                "ha_discovery_prefix": "homeassistant"
            },
            "signal": {
                "enabled": False,
                "cli_path": "signal-cli",
                "sender": "",
                "recipients": []
            },
            "ai": {
                "enabled": False,
                "sensitivity": 3.0
            },
            "updates": {
                "enabled": False,
                "interval_hours": 12,
                "mode": "apply",
                "target": "all"
            },
            "setup_completed": False
        }

        # Auto-complete setup in Docker environment
        # If METRICS_URL is provided, we assume environment setup
        if os.environ.get("METRICS_URL"):
            defaults["setup_completed"] = True
            defaults["web"]["write_enabled"] = True
            defaults["metrics"]["url"] = os.environ.get("METRICS_URL")

        # Load from DB, structure into dict like old yaml
        raw = db.get_setting("config")
        if raw:
            try:
                data = json.loads(raw)
                # Decrypt sensitive fields
                if "mqtt" in data:
                    data["mqtt"]["password"] = self._decrypt(data["mqtt"].get("encrypted_password", ""))

                # Merge loaded data into defaults
                return self._merge_dicts(defaults, data)
            except json.JSONDecodeError:
                pass

        # Default structure with Docker-friendly defaults
        return defaults

    def save(self):
        # Encrypt sensitive fields before saving
        to_save = json.loads(json.dumps(self.data))

        if "mqtt" in to_save:
            to_save["mqtt"]["encrypted_password"] = self._encrypt(to_save["mqtt"].get("password", ""))
            # Remove plain text from storage dict
            if "password" in to_save["mqtt"]:
                del to_save["mqtt"]["password"]

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
