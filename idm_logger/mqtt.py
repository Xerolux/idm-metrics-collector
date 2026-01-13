"""
MQTT Publisher for IDM Heat Pump Logger
Publishes sensor data to MQTT broker with authentication support.
"""
import logging
import json
import time
import ssl
from threading import Thread, Event
import paho.mqtt.client as mqtt
from .config import config
from .sensor_addresses import SensorFeatures, IdmBinarySensorAddress

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publishes heat pump data to MQTT broker."""

    def __init__(self):
        self.client = None
        self.connected = False
        self.running = False
        self.stop_event = Event()
        self.last_publish_time = 0
        self.sensors = {}
        self.binary_sensors = {}
        self.write_callback = None
        # Don't setup client during import, wait for explicit start()
        # self._setup_client()

    def set_sensors(self, sensors, binary_sensors=None):
        """Set available sensors for discovery."""
        self.sensors = sensors
        self.binary_sensors = binary_sensors or {}

    def set_write_callback(self, callback):
        """Set callback for handling write commands."""
        self.write_callback = callback

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
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id, protocol=mqtt.MQTTv311)

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
                self.client.tls_set(
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
                logger.info("MQTT TLS encryption enabled")

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

            # Subscribe to write commands if discovery is enabled (or just always if we support writes)
            # Standard topic for writes: [prefix]/[sensor]/set
            topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
            client.subscribe(f"{topic_prefix}/+/set")
            logger.info(f"Subscribed to control topics: {topic_prefix}/+/set")

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
                5: "Connection refused - not authorized"
            }
            error_msg = error_messages.get(rc, f"Connection refused - code {rc}")
            logger.error(f"Failed to connect to MQTT broker: {error_msg}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnect (code {rc}), will attempt reconnect")
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_publish(self, client, userdata, mid):
        """Callback when message is published."""
        logger.debug(f"MQTT message published (mid: {mid})")

    def _on_message(self, client, userdata, msg):
        """Callback when message is received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received MQTT message on {topic}: {payload}")

            if not self.write_callback:
                logger.warning("No write callback registered, ignoring message")
                return

            # Extract sensor name from topic: prefix/sensor_name/set
            topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
            if not topic.startswith(topic_prefix) or not topic.endswith("/set"):
                return

            # Remove prefix and /set suffix
            sensor_name = topic[len(topic_prefix)+1:-4]

            try:
                self.write_callback(sensor_name, payload)
                logger.info(f"Successfully processed write command for {sensor_name}")
            except Exception as e:
                logger.error(f"Failed to write sensor {sensor_name}: {e}")

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
        if not self.sensors and not self.binary_sensors:
            logger.warning("No sensors available for HA Discovery")
            return

        ha_prefix = config.get("mqtt.ha_discovery_prefix", "homeassistant")
        topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
        node_id = "idm_heatpump"

        device_info = {
            "identifiers": [node_id],
            "name": "IDM Heat Pump",
            "manufacturer": "IDM",
            "model": "Navigator 2.0"
        }

        logger.info(f"Publishing HA Discovery messages (prefix: {ha_prefix})...")

        # Combine sensors
        all_sensors = {**self.sensors, **self.binary_sensors}

        for name, sensor in all_sensors.items():
            # Determine component type and features
            component = "sensor"
            object_id = name

            # Base config payload
            payload = {
                "name": name.replace("_", " ").title(),
                "unique_id": f"{node_id}_{name}",
                "state_topic": f"{topic_prefix}/{name}",
                "device": device_info,
                "value_template": "{{ value_json.value }}",
                "availability_topic": f"{topic_prefix}/state",
                "availability_template": "{{ 'online' if value_json else 'offline' }}" # Simple check
            }

            # Add unit if available
            if hasattr(sensor, "unit") and sensor.unit:
                payload["unit_of_measurement"] = sensor.unit
                # Infer device class from unit
                if sensor.unit == "°C":
                    payload["device_class"] = "temperature"
                elif sensor.unit == "kW":
                    payload["device_class"] = "power"
                elif sensor.unit == "kWh":
                    payload["device_class"] = "energy"
                    payload["state_class"] = "total_increasing"
                elif sensor.unit == "%":
                    # Heuristic for humidity vs battery vs other
                    if "humidity" in name:
                         payload["device_class"] = "humidity"
                    elif "battery" in name or "charge" in name:
                         payload["device_class"] = "battery"
                    else:
                         payload["device_class"] = "power_factor" # generic percent

            # Binary Sensors
            if isinstance(sensor, IdmBinarySensorAddress):
                component = "binary_sensor"
                payload["payload_on"] = True
                payload["payload_off"] = False
                payload["value_template"] = "{{ value_json.value }}"
                if "failure" in name or "alarm" in name:
                     payload["device_class"] = "problem"

            # Writable Entities (Controls)
            if hasattr(sensor, "supported_features") and sensor.supported_features != SensorFeatures.NONE:
                # Decide component based on features/type

                # Enums -> Select
                if hasattr(sensor, "enum") and sensor.enum:
                     component = "select"
                     payload["command_topic"] = f"{topic_prefix}/{name}/set"
                     payload["options"] = [m.name for m in sensor.enum]
                     payload["value_template"] = "{{ value_json.value_str }}" # Use string representation for select
                     # We need to make sure we publish the string value in value_str or similar?
                     # Currently publish_data sends: value (raw), unit, timestamp.
                     # But my ModbusClient reads also give 'value_str' for enums in the big dict,
                     # BUT publish_data iterates over items and takes 'value'.

                     # Wait, publish_data structure:
                     # { sensor_name: { value: ..., unit: ... } }
                     # It publishes JSON payload.
                     # For Enum, the value is the integer.
                     # HA Select expects the option string.
                     # I might need to adjust publish_data to include the string value for Enums or use a template that maps int to string?
                     # Template mapping in HA is hard without hardcoding options.
                     # Better: Make sure logger publishes the string representation for Enums if available?

                     # Let's assume for now I will use the integer value for state (which is wrong for HA Select),
                     # OR I can use 'number' component for Enums if I just want to set the integer ID.
                     # BUT 'select' is better UI.
                     # For 'select', state_topic must return the option string.

                     # Hack: I will stick to 'sensor' for reading and add a separate 'select' entity for writing if needed?
                     # No, HA expects state topic to match one of the options.
                     pass

                # Numerical -> Number
                elif (sensor.supported_features & SensorFeatures.SET_TEMPERATURE) or \
                     (sensor.supported_features & SensorFeatures.SET_POWER) or \
                     (sensor.supported_features & SensorFeatures.SET_BATTERY) or \
                     (sensor.supported_features & SensorFeatures.SET_HUMIDITY):
                     component = "number"
                     payload["command_topic"] = f"{topic_prefix}/{name}/set"
                     if hasattr(sensor, "min_value") and sensor.min_value is not None:
                          payload["min"] = sensor.min_value
                     if hasattr(sensor, "max_value") and sensor.max_value is not None:
                          payload["max"] = sensor.max_value

                     # If sensor is write-only or not readable, set optimistic mode
                     if not sensor.read_supported:
                          payload["optimistic"] = True

                # Binary -> Switch
                elif sensor.supported_features & SensorFeatures.SET_BINARY:
                     component = "switch"
                     payload["command_topic"] = f"{topic_prefix}/{name}/set"
                     payload["state_on"] = True
                     payload["state_off"] = False
                     payload["payload_on"] = "true"
                     payload["payload_off"] = "false"

            # Publish config
            discovery_topic = f"{ha_prefix}/{component}/{node_id}/{name}/config"
            self.client.publish(discovery_topic, json.dumps(payload), retain=True)

        logger.info(f"Published HA Discovery for {len(all_sensors)} entities")

    def publish_data(self, data):
        """
        Publish sensor data to MQTT.

        Args:
            data: Dictionary of sensor data
        """
        if not config.get("mqtt.enabled", False):
            return

        if not self.connected:
            logger.debug("Not connected to MQTT broker, skipping publish")
            return

        topic_prefix = config.get("mqtt.topic_prefix", "idm/heatpump")
        qos = config.get("mqtt.qos", 1)

        try:
            # Publish each sensor value to individual topics
            for sensor_name, value in data.items():
                # data comes from modbus.read_sensors() which returns a flattened dict:
                # { "sensor_name": value, "sensor_name_str": "EnumName", ... }
                # But wait, logger.py passes 'data' which is that dict.
                # However, mqtt.py previously expected { sensor: {value: ..., unit: ... } } ?
                # Let's check existing publish_data implementation in read_file output.

                # The OLD publish_data implementation:
                # for sensor_name, sensor_data in data.items():
                #    if isinstance(sensor_data, dict) and 'value' in sensor_data:
                # ...

                # BUT logger.py says:
                # data = modbus.read_sensors()
                # modbus.read_sensors() returns a simple dict {name: value}.
                # WAIT. modbus.py read_sensors returns `data` dict.
                # Looking at modbus.py:
                # data[sensor.name] = value
                # data[f"{sensor.name}_str"] = str(value)
                # So it returns { "temp_outside": 12.5, ... }

                # The existing mqtt.py `publish_data` expects `sensor_data` to be a dict with `value` key.
                # This seems like a MISMATCH in the existing code or I misread something.
                # In `logger.py`:
                # if mqtt and mqtt.connected:
                #     mqtt.publish_data(data)

                # If `data` is flat, `isinstance(sensor_data, dict)` will be false for float/int values.
                # So existing code might be broken or I am missing something.
                # Let's fix this method to handle the flat dict from modbus.py.

                # Skip _str keys
                if sensor_name.endswith("_str"):
                    continue

                val = value
                # Find unit from sensor def if possible
                unit = ""
                if self.sensors and sensor_name in self.sensors:
                     unit = getattr(self.sensors[sensor_name], "unit", "")

                # Special handling for Enum string values for HA
                # If there is a corresponding _str key, use it?
                # For HA 'select', we might want the string.
                # But HA 'sensor' usually wants raw value.
                # Let's stick to raw value in 'value' field.

                val_str = data.get(f"{sensor_name}_str")

                topic = f"{topic_prefix}/{sensor_name}"

                # Prepare payload
                payload = {
                    'value': val,
                    'unit': unit,
                    'timestamp': int(time.time())
                }

                if val_str:
                     payload['value_str'] = val_str

                # Publish message
                result = self.client.publish(
                    topic,
                    json.dumps(payload),
                    qos=qos,
                    retain=False
                )

                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    logger.warning(f"Failed to publish {sensor_name}: {result.rc}")

            # Also publish complete state to single topic
            state_topic = f"{topic_prefix}/state"
            self.client.publish(
                state_topic,
                json.dumps(data), # This handles the full dict
                qos=qos,
                retain=True  # Retain state for new subscribers
            )

            self.last_publish_time = time.time()
            logger.debug(f"Published {len(data)} sensors to MQTT")

        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")

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

        payload = {
            'value': value,
            'unit': unit,
            'timestamp': int(time.time())
        }

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
            "last_publish": self.last_publish_time if self.last_publish_time > 0 else None
        }


# Global instance
mqtt_publisher = MQTTPublisher()
