from idm_logger.config import config

print(f"installation_id: {config.get('installation_id')}")
print(f"telemetry.enabled: {config.get('telemetry.enabled', True)}")
print(f"telemetry.server_url: {config.get('telemetry.server_url', 'default')}")
print(f"hp_model: {config.get('hp_model', 'Unknown')}")
