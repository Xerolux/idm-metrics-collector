#!/usr/bin/env python3
"""
Test script for MQTT functionality
Tests connection, authentication, and message publishing
"""
import sys
import time
import json
import paho.mqtt.client as mqtt

# Test configuration
MQTT_BROKER = "localhost"  # Change this to your MQTT broker
MQTT_PORT = 1883
MQTT_USERNAME = ""  # Optional
MQTT_PASSWORD = ""  # Optional
MQTT_USE_TLS = False
MQTT_TOPIC_PREFIX = "idm/heatpump"

def on_connect(client, userdata, flags, rc):
    """Callback for connection events."""
    if rc == 0:
        print(f"✓ Connected to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
    else:
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized"
        }
        error_msg = error_messages.get(rc, f"Connection refused - code {rc}")
        print(f"✗ Failed to connect: {error_msg}")

def on_disconnect(client, userdata, rc):
    """Callback for disconnection events."""
    if rc != 0:
        print(f"⚠ Unexpected disconnect (code {rc})")
    else:
        print("✓ Disconnected cleanly")

def on_publish(client, userdata, mid):
    """Callback for publish events."""
    print(f"✓ Message published (mid: {mid})")

def test_mqtt():
    """Test MQTT connection and publishing."""
    print("=" * 50)
    print("MQTT Connection Test")
    print("=" * 50)
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Username: {MQTT_USERNAME if MQTT_USERNAME else '(none)'}")
    print(f"TLS: {'Enabled' if MQTT_USE_TLS else 'Disabled'}")
    print(f"Topic Prefix: {MQTT_TOPIC_PREFIX}")
    print("=" * 50)

    try:
        # Create MQTT client
        client_id = f"idm_test_{int(time.time())}"
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        # Set callbacks
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish

        # Set authentication if provided
        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            print(f"✓ Authentication configured")

        # Configure TLS if enabled
        if MQTT_USE_TLS:
            import ssl
            client.tls_set(
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            print(f"✓ TLS configured")

        # Connect to broker
        print(f"\nConnecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()

        # Wait for connection
        time.sleep(2)

        # Test publishing sensor data
        print("\nTesting sensor data publishing...")

        test_data = {
            "temperature_outdoor": {
                "value": 15.5,
                "unit": "°C",
                "timestamp": int(time.time())
            },
            "temperature_flow": {
                "value": 35.2,
                "unit": "°C",
                "timestamp": int(time.time())
            },
            "cop_heating": {
                "value": 3.8,
                "unit": "",
                "timestamp": int(time.time())
            }
        }

        # Publish individual sensor values
        for sensor_name, sensor_data in test_data.items():
            topic = f"{MQTT_TOPIC_PREFIX}/{sensor_name}"
            payload = json.dumps(sensor_data)

            result = client.publish(topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"  → Published: {topic}")
            else:
                print(f"  ✗ Failed to publish: {topic} (rc={result.rc})")

            time.sleep(0.1)

        # Publish complete state
        state_topic = f"{MQTT_TOPIC_PREFIX}/state"
        result = client.publish(state_topic, json.dumps(test_data), qos=1, retain=True)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"  → Published state: {state_topic}")
        else:
            print(f"  ✗ Failed to publish state (rc={result.rc})")

        # Wait for messages to be sent
        time.sleep(2)

        # Disconnect
        print("\nDisconnecting...")
        client.loop_stop()
        client.disconnect()

        print("\n" + "=" * 50)
        print("✓ MQTT test completed successfully!")
        print("=" * 50)

        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    print("\n📡 IDM Heat Pump Logger - MQTT Test\n")

    # Check if broker is configured
    if MQTT_BROKER == "localhost":
        print("⚠ Warning: Using default broker 'localhost'")
        print("   Edit this script to configure your MQTT broker\n")

    exit_code = test_mqtt()
    sys.exit(exit_code)
