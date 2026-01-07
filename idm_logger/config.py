import yaml
import os
import logging

class Config:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.data = {
            "idm": {
                "host": "localhost",
                "port": 502,
                "circuits": ["A"]
            },
            "influx": {
                "version": 2,
                "url": "http://localhost:8086",
                "org": "my-org",
                "bucket": "idm",
                "token": "my-token",
                "username": "",
                "password": "",
                "database": "idm"
            },
            "web": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 5000,
                "admin_password": "admin", # Default password
                "write_enabled": False # Feature flag for writing
            },
            "logging": {
                "interval": 60,
                "level": "INFO"
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                try:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        self.update_dict(self.data, loaded)
                except yaml.YAMLError as exc:
                    print(f"Error loading config: {exc}")

    def update_dict(self, target, source):
        for key, value in source.items():
            if isinstance(value, dict) and key in target:
                self.update_dict(target[key], value)
            else:
                target[key] = value

    def save(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)

    def get(self, path, default=None):
        keys = path.split('.')
        val = self.data
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return default
        return val

# Global config instance
config = Config()
