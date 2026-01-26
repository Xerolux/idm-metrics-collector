# SPDX-License-Identifier: MIT
"""
MQTT Publisher for IDM Heat Pump Logger
Publishes sensor data to MQTT broker with authentication support.
"""

import logging
import json
import os
import time
import ssl
import asyncio
from threading import Event
import paho.mqtt.client as mqtt
from .config import config
from .sensor_addresses import SensorFeatures, IdmBinarySensorAddress
from .migrations import get_default_heatpump_id

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publishes heat pump data to MQTT broker."""

    def __init__(self):
        self.client = None
        self.connected = False
        self.running = False
        self.stop_event = Event()
        self.last_publish_time = 0
        self.heatpump_manager = None
        # Don't setup client during import, wait for explicit start()
        # self._setup_client()

    def set_heatpump_manager(self, manager):
        """Set heatpump manager for discovery and control."""
        self.heatpump_manager = manager

    def _setup_client(self):
        """Setup MQTT client with authentication and TLS."""
        if not config.get("mqtt.enabled", False):
            logger.info("MQTT is disabled in configuration")
            return

        broker = config.get("mqtt.broker", "")
        if not broker:
            logger.warning("MQTT broker address not configured")
            return

        try:
            # Create MQTT client
            client_id = f"idm_logger_{int(time.time())}"
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION1,
                client_id=client_id,
                protocol=mqtt.MQTTv311,
            )

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            self.client.on_message = self._on_message

            # Set username and password if provided
            username = config.get("mqtt.username", "")
            password = config.get("mqtt.password", "")
            if username:
                self.client.username_pw_set(username, password)
                logger.info(f"MQTT authentication configured for user: {username}")

            # Configure TLS if enabled
            if config.get("mqtt.use_tls", False):
                ca_cert = config.get("mqtt.tls_ca_cert", "")
                tls_params = {
                    "cert_reqs": ssl.CERT_REQUIRED,
                    "tls_version": ssl.PROTOCOL_TLSv1_2,
                }

                # Add CA certificate path if provided (for self-signed certs)
                if ca_cert and os.path.exists(ca_cert):
                    tls_params["ca_certs"] = ca_cert
                    logger.info(f"MQTT TLS encryption enabled with CA cert: {ca_cert}")
                else:
                    logger.info("MQTT TLS encryption enabled with system CA certs")

                self.client.tls_set(**tls_params)

            logger.info(f"MQTT client configured for broker: {broker}")

        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
            self.client = None

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            self.connected = True
            broker = config.get("mqtt.broker", "")
            logger.info(f"Connected to MQTT broker: {broker}")

            # Subscribe to write commands
            # Topics:
            # - Legacy: [prefix]/[sensor]/set
            # - Multi:  [prefix]/[hp_id]/[sensor]/set
            topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
            client.subscribe(f"{topic_prefix}/+/set")
            client.subscribe(f"{topic_prefix}/+/+/set")
            logger.info(
                f"Subscribed to control topics: {topic_prefix}/+/set, {topic_prefix}/+/+/set"
            )

            # Publish HA Discovery if enabled
            if config.get("mqtt.ha_discovery_enabled", False):
                self._publish_ha_discovery()

        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized",
            }
            error_msg = error_messages.get(rc, f"Connection refused - code {rc}")
            logger.error(f"Failed to connect to MQTT broker: {error_msg}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        if rc != 0:
            logger.warning(
                f"Unexpected MQTT disconnect (code {rc}), will attempt reconnect"
            )
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_publish(self, client, userdata, mid):
        """Callback when message is published."""
        logger.debug(f"MQTT message published (mid: {mid})")

    def _on_message(self, client, userdata, msg):
        """Callback when message is received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            logger.info(f"Received MQTT message on {topic}: {payload}")

            if not self.heatpump_manager:
                logger.warning("Heatpump manager not set, ignoring message")
                return

            topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
            if not topic.startswith(topic_prefix) or not topic.endswith("/set"):
                return

            # Strip prefix and suffix
            # Path: [prefix]/.../set
            path = topic[len(topic_prefix) : -4].strip("/")
            parts = path.split("/")

            hp_id = None
            sensor_name = None

            if len(parts) == 1:
                # Legacy: idm/heatpump/sensor/set
                sensor_name = parts[0]
                hp_id = get_default_heatpump_id()
            elif len(parts) == 2:
                # Multi: idm/heatpump/hp_id/sensor/set
                hp_id = parts[0]
                sensor_name = parts[1]
            else:
                logger.warning(f"Invalid topic structure: {topic}")
                return

            if not hp_id or not sensor_name:
                return

            try:
                asyncio.run(
                    self.heatpump_manager.write_value(hp_id, sensor_name, payload)
                )
                logger.info(
                    f"Successfully processed write command for {hp_id}/{sensor_name}"
                )
            except Exception as e:
                logger.error(f"Failed to write sensor {hp_id}/{sensor_name}: {e}")

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def connect(self):
        """Connect to MQTT broker."""
        if not self.client:
            self._setup_client()

        if not self.client:
            logger.error("Cannot connect - MQTT client not initialized")
            return False

        broker = config.get("mqtt.broker", "")
        port = config.get("mqtt.port", 1883)

        try:
            logger.info(f"Connecting to MQTT broker {broker}:{port}")
            self.client.connect(broker, port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("MQTT client disconnected")

    def _publish_ha_discovery(self):
        """Publish Home Assistant Auto Discovery configs."""
        if not self.heatpump_manager:
            logger.warning("No HeatpumpManager available for HA Discovery")
            return

        ha_prefix = config.get("mqtt.ha_discovery_prefix", "homeassistant")
        base_topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")

        status_list = self.heatpump_manager.get_status()

        logger.info(f"Publishing HA Discovery messages (prefix: {ha_prefix})...")

        for hp_status in status_list:
            hp_id = hp_status["id"]
            conn = self.heatpump_manager.get_connection(hp_id)
            if not conn or not conn.enabled:
                continue

            node_id = f"idm_heatpump_{hp_id.replace('-', '_')}"
            topic_prefix = f"{base_topic_prefix}/{hp_id}"

            device_info = {
                "identifiers": [node_id],
                "name": conn.name,
                "manufacturer": conn.manufacturer,
                "model": conn.model,
            }

            for sensor in conn.sensors:
                name = sensor.id
                component = "sensor"

                # Base config payload
                payload = {
                    "name": sensor.name,
                    "unique_id": f"{node_id}_{name}",
                    "state_topic": f"{topic_prefix}/{name}",
                    "device": device_info,
                    "value_template": "{{ value_json.value }}",
                    "availability_topic": f"{topic_prefix}/state",
                    "availability_template": "{{ 'online' if value_json else 'offline' }}",
                }

                # Add unit if available
                if hasattr(sensor, "unit") and sensor.unit:
                    payload["unit_of_measurement"] = sensor.unit
                    # Infer device class
                    if sensor.unit == "°C":
                        payload["device_class"] = "temperature"
                    elif sensor.unit == "kW":
                        payload["device_class"] = "power"
                    elif sensor.unit == "kWh":
                        payload["device_class"] = "energy"
                        payload["state_class"] = "total_increasing"

                # Binary Sensors
                if sensor.category.value == "binary" or sensor.datatype == "BOOL":
                    component = "binary_sensor"
                    payload["payload_on"] = True
                    payload["payload_off"] = False

                # Writable Entities
                if sensor.is_writable:
                    # Enums -> Select
                    if hasattr(sensor, "enum_values") and sensor.enum_values:
                        component = "select"
                        payload["command_topic"] = f"{topic_prefix}/{name}/set"
                        payload["options"] = list(sensor.enum_values.values())
                        payload["value_template"] = "{{ value_json.value_str }}"

                    # Numerical -> Number
                    elif sensor.datatype in ("FLOAT", "INT16", "UINT16"):
                        component = "number"
                        payload["command_topic"] = f"{topic_prefix}/{name}/set"
                        if sensor.min_value is not None:
                            payload["min"] = sensor.min_value
                        if sensor.max_value is not None:
                            payload["max"] = sensor.max_value

                    # Binary -> Switch
                    elif sensor.datatype == "BOOL":
                        component = "switch"
                        payload["command_topic"] = f"{topic_prefix}/{name}/set"
                        payload["state_on"] = True
                        payload["state_off"] = False
                        payload["payload_on"] = "true"
                        payload["payload_off"] = "false"

                # Publish config
                discovery_topic = f"{ha_prefix}/{component}/{node_id}/{name}/config"
                self.client.publish(discovery_topic, json.dumps(payload), retain=True)

    def publish_data(self, all_data):
        """
        Publish sensor data to MQTT.

        Args:
            all_data: Nested dictionary { hp_id: { sensor: value } }
        """
        if not config.get("mqtt.enabled", False):
            return

        if not self.connected:
            return

        base_topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
        qos = config.get("mqtt.qos", 1)
        now = int(time.time())

        try:
            default_hp_id = get_default_heatpump_id()

            for hp_id, data in all_data.items():
                topic_prefix = f"{base_topic_prefix}/{hp_id}"

                # If this is the default HP, also publish to base prefix (legacy)
                is_default = hp_id == default_hp_id

                # Get connection for unit info
                conn = (
                    self.heatpump_manager.get_connection(hp_id)
                    if self.heatpump_manager
                    else None
                )

                for sensor_name, value in data.items():
                    if sensor_name.endswith("_str"):
                        continue

                    unit = ""
                    if conn:
                        sensor_def = next(
                            (s for s in conn.sensors if s.id == sensor_name), None
                        )
                        if sensor_def:
                            unit = sensor_def.unit or ""

                    payload = {"value": value, "unit": unit, "timestamp": now}

                    if f"{sensor_name}_str" in data:
                        payload["value_str"] = data[f"{sensor_name}_str"]

                    # Publish to idm/heatpump/hp_id/sensor
                    self.client.publish(
                        f"{topic_prefix}/{sensor_name}",
                        json.dumps(payload),
                        qos=qos,
                        retain=False,
                    )

                    # Publish to idm/heatpump/sensor (legacy)
                    if is_default:
                        self.client.publish(
                            f"{base_topic_prefix}/{sensor_name}",
                            json.dumps(payload),
                            qos=qos,
                            retain=False,
                        )

                # Publish state
                self.client.publish(
                    f"{topic_prefix}/state", json.dumps(data), qos=qos, retain=True
                )
                if is_default:
                    self.client.publish(
                        f"{base_topic_prefix}/state",
                        json.dumps(data),
                        qos=qos,
                        retain=True,
                    )

            self.last_publish_time = now

        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}", exc_info=True)

    def publish_sensor(self, sensor_name, value, unit=""):
        """
        Publish a single sensor value.

        Args:
            sensor_name: Name of the sensor
            value: Sensor value
            unit: Unit of measurement
        """
        if not config.get("mqtt.enabled", False) or not self.connected:
            return

        topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
        topic = f"{topic_prefix}/{sensor_name}"
        qos = config.get("mqtt.qos", 1)

        payload = {"value": value, "unit": unit, "timestamp": int(time.time())}

        try:
            result = self.client.publish(topic, json.dumps(payload), qos=qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published {sensor_name}={value} to MQTT")
            else:
                logger.warning(f"Failed to publish {sensor_name}: {result.rc}")
        except Exception as e:
            logger.error(f"Error publishing sensor to MQTT: {e}")

    def start(self):
        """Start MQTT publisher."""
        if not config.get("mqtt.enabled", False):
            logger.info("MQTT publishing disabled")
            return

        # Setup client if not already done
        if not self.client:
            self._setup_client()

        self.running = True
        self.stop_event.clear()

        # Connect to broker
        if self.connect():
            logger.info("MQTT publisher started")
        else:
            logger.error("Failed to start MQTT publisher")

    def stop(self):
        """Stop MQTT publisher."""
        self.running = False
        self.stop_event.set()
        self.disconnect()
        logger.info("MQTT publisher stopped")

    def get_status(self):
        """Get MQTT connection status."""
        return {
            "enabled": config.get("mqtt.enabled", False),
            "connected": self.connected,
            "broker": config.get("mqtt.broker", ""),
            "port": config.get("mqtt.port", 1883),
            "use_tls": config.get("mqtt.use_tls", False),
            "topic_prefix": config.get("mqtt.topic_prefix", "idm/heatpump"),
            "ha_discovery_enabled": config.get("mqtt.ha_discovery_enabled", False),
            "last_publish": self.last_publish_time
            if self.last_publish_time > 0
            else None,
        }


# Global instance
mqtt_publisher = MQTTPublisher()
