# SPDX-License-Identifier: MIT
import json
import pytest
from unittest.mock import MagicMock, patch


import idm_logger.mqtt  # noqa: F401


# Patch where config is IMPORTED, not where it is defined
# idm_logger.mqtt imports config as 'config'
@pytest.fixture
def mock_config():
    with patch("idm_logger.mqtt.config") as mock:

        def config_get(key, default=None):
            if key == "mqtt.enabled":
                return True
            if key == "mqtt.topic_prefix":
                return "idm/heatpump"
            if key == "mqtt.broker":
                return "mock_broker"
            return default

        mock.get.side_effect = config_get
        yield mock


@pytest.fixture
def mock_mqtt_client():
    with patch("idm_logger.mqtt.mqtt.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        yield mock_client


@pytest.fixture
def publisher(mock_mqtt_client, mock_config):
    from idm_logger.mqtt import MQTTPublisher

    pub = MQTTPublisher()
    pub._setup_client()
    pub.client = mock_mqtt_client
    pub.connected = True
    return pub


def test_publish_data_flat_dict(publisher, mock_mqtt_client):
    """Test publishing data from a flat dictionary (ModbusClient format)."""

    # Test data representing what ModbusClient.read_sensors() returns
    data = {
        "temp_outside": 12.5,
        "op_mode": 1,
        "op_mode_str": "Heating",  # String variant
        "fault_active": False,
    }

    # Mock sensors to provide units
    publisher.sensors = {
        "temp_outside": MagicMock(unit="°C"),
        "op_mode": MagicMock(unit=""),
        "fault_active": MagicMock(unit=""),
    }

    publisher.publish_data(data)

    # Verification
    calls = mock_mqtt_client.publish.call_args_list

    # We expect 4 calls: 3 individual sensors + 1 state topic
    assert len(calls) == 4

    # Helper to find call by topic
    def get_payload(topic_suffix):
        topic = f"idm/heatpump/{topic_suffix}"
        for call in calls:
            if call.args[0] == topic:
                return json.loads(call.args[1])
        return None

    # Check temp_outside
    payload = get_payload("temp_outside")
    assert payload is not None
    assert payload["value"] == 12.5
    assert payload["unit"] == "°C"

    # Check op_mode (should include value_str)
    payload = get_payload("op_mode")
    assert payload is not None
    assert payload["value"] == 1
    assert payload["value_str"] == "Heating"

    # Check fault_active
    payload = get_payload("fault_active")
    assert payload is not None
    assert payload["value"] is False

    # Check that _str topic was NOT published separately
    assert get_payload("op_mode_str") is None

    # Check state topic
    payload = get_payload("state")
    assert payload is not None
    assert payload == data


def test_publish_data_legacy_nested_dict(publisher, mock_mqtt_client):
    """Test publishing data from a legacy nested dictionary format."""
    data = {
        "temp_outside": {"value": 15.0},
        "op_mode": {"value": 2},
    }

    publisher.sensors = {
        "temp_outside": MagicMock(unit="°C"),
        "op_mode": MagicMock(unit=""),
    }

    publisher.publish_data(data)

    calls = mock_mqtt_client.publish.call_args_list

    # Helper to find call by topic
    def get_payload(topic_suffix):
        topic = f"idm/heatpump/{topic_suffix}"
        for call in calls:
            if call.args[0] == topic:
                return json.loads(call.args[1])
        return None

    # Check temp_outside
    payload = get_payload("temp_outside")
    assert payload is not None
    assert payload["value"] == 15.0
    assert payload["unit"] == "°C"

    # Check op_mode
    payload = get_payload("op_mode")
    assert payload is not None
    assert payload["value"] == 2
