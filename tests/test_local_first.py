"""Regression checks for the local-first AI architecture."""

from idm_logger.config import Config
from idm_logger.web import app


def test_telemetry_endpoints_are_not_registered():
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert not any(route.startswith("/api/telemetry") for route in routes)


def test_legacy_telemetry_config_is_removed(monkeypatch):
    legacy = {
        "telemetry": {
            "enabled": True,
            "server_url": "https://collector.invalid",
            "encrypted_auth_token": "secret",
        },
        "ai": {"enabled": True, "model": "community"},
    }
    monkeypatch.setattr(
        "idm_logger.config.db.get_setting",
        lambda _key: __import__("json").dumps(legacy),
    )

    migrated = Config().data

    assert "telemetry" not in migrated
    assert migrated["ai"]["enabled"] is True
    assert migrated["ai"]["model"] == "rolling"
