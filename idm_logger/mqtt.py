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

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publishes heat pump data to MQTT broker."""

    def __init__(self):
        self.client = None
        self.connected = False
        self.running = False
        self.stop_event = Event()
        self.last_publish_time = 0
        # Don't setup client during import, wait for explicit start()
        # self._setup_client()

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
            for sensor_name, sensor_data in data.items():
                if isinstance(sensor_data, dict) and 'value' in sensor_data:
                    topic = f"{topic_prefix}/{sensor_name}"

                    # Prepare payload
                    payload = {
                        'value': sensor_data['value'],
                        'unit': sensor_data.get('unit', ''),
                        'timestamp': sensor_data.get('timestamp', int(time.time()))
                    }

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
                json.dumps(data),
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
            "last_publish": self.last_publish_time if self.last_publish_time > 0 else None
        }


# Global instance
mqtt_publisher = MQTTPublisher()
