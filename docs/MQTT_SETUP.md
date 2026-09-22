# MQTT Setup Guide

This guide explains how to configure MQTT publishing for the IDM Heat Pump Logger.

## Overview

The MQTT feature allows you to publish sensor data from your heat pump to an MQTT broker. This enables integration with home automation systems like Home Assistant, OpenHAB, Node-RED, and others.

## Features

- **Secure Authentication**: Username and password authentication
- **TLS Encryption**: Optional TLS/SSL encryption for secure communication
- **Quality of Service**: Configurable QoS levels (0, 1, 2)
- **Individual Topics**: Each sensor publishes to its own topic
- **State Topic**: Complete state published to a single retained topic
- **Auto-Reconnect**: Automatic reconnection on network issues

## MQTT Broker

You need an MQTT broker to use this feature. Popular options include:

- **Mosquitto** - Popular open-source broker
- **Home Assistant** - Built-in MQTT broker
- **HiveMQ** - Cloud and self-hosted options
- **EMQX** - Scalable MQTT broker

### Installing Mosquitto (Example)

```bash
# Ubuntu/Debian
sudo apt install mosquitto mosquitto-clients

# Start service
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

## Configuration

### Via Web Interface

1. Log in to the web interface
2. Navigate to **Settings** → **Configuration**
3. Scroll to the **MQTT Settings** section
4. Configure the following:
   - **Enable MQTT**: Toggle to enable MQTT publishing
   - **Broker Address**: Hostname or IP of your MQTT broker
   - **Port**: MQTT port (default: 1883 for non-TLS, 8883 for TLS)
   - **Username**: MQTT username (optional)
   - **Password**: MQTT password (optional)
   - **Use TLS**: Enable TLS encryption
   - **Topic Prefix**: Base topic for all messages (default: `idm/heatpump`)
   - **Publish Interval**: How often to publish data (uses logging interval if not set)
   - **QoS**: Quality of Service level (0, 1, or 2)
5. Click **Save Configuration**
6. Click **Restart Service** to apply changes

### Via Environment Variables (Docker)

Edit your `docker-compose.yml`:

```yaml
environment:
  - MQTT_ENABLED=true
  - MQTT_BROKER=mqtt.example.com
  - MQTT_PORT=1883
  - MQTT_USERNAME=myuser
  - MQTT_PASSWORD=mypassword
  - MQTT_USE_TLS=false
  - MQTT_TOPIC_PREFIX=idm/heatpump
```

### Via Configuration File

Edit `config.yaml`:

```yaml
mqtt:
  enabled: true
  broker: "mqtt.example.com"
  port: 1883
  username: "myuser"
  password: "mypassword"
  use_tls: false
  topic_prefix: "idm/heatpump"
  publish_interval: 60
  qos: 1
```

## MQTT Topics

### Individual Sensor Topics

Each sensor value is published to its own topic:

```
<topic_prefix>/<sensor_name>
```

Example topics:
- `idm/heatpump/temperature_outdoor`
- `idm/heatpump/temperature_flow`
- `idm/heatpump/cop_heating`

Message payload (JSON):
```json
{
  "value": 15.5,
  "unit": "°C",
  "timestamp": 1704567890
}
```

### State Topic

The complete state is published to a single retained topic:

```
<topic_prefix>/state
```

This topic is retained, so new subscribers immediately receive the last known state.

## Quality of Service (QoS)

- **QoS 0**: At most once delivery (fire and forget)
- **QoS 1**: At least once delivery (default, recommended)
- **QoS 2**: Exactly once delivery (slowest, highest reliability)

## Security Best Practices

### Authentication

Always use username and password authentication:

```yaml
mqtt:
  username: "idm_logger"
  password: "strong-random-password"
```

### TLS Encryption

For production deployments, enable TLS:

```yaml
mqtt:
  port: 8883
  use_tls: true
```

**Note**: Ensure your MQTT broker has valid TLS certificates configured.

### Broker Access Control

Configure your MQTT broker to restrict access:

**Mosquitto ACL Example** (`/etc/mosquitto/acl`):
```
user idm_logger
topic write idm/heatpump/#
topic read idm/heatpump/#
```

## Testing MQTT Connection

Use the included test script:

```bash
# Edit test_mqtt.py to configure your broker
nano test_mqtt.py

# Run test
python test_mqtt.py
```

Or use mosquitto_sub to monitor messages:

```bash
# Subscribe to all heat pump topics
mosquitto_sub -h mqtt.example.com -t "idm/heatpump/#" -v

# With authentication
mosquitto_sub -h mqtt.example.com -u myuser -P mypassword -t "idm/heatpump/#" -v

# With TLS
mosquitto_sub -h mqtt.example.com -p 8883 --cafile /etc/ssl/certs/ca-certificates.crt \
  -u myuser -P mypassword -t "idm/heatpump/#" -v
```

## Home Assistant Integration

### MQTT Discovery

Add sensors to Home Assistant `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Heat Pump Outdoor Temperature"
      state_topic: "idm/heatpump/temperature_outdoor"
      value_template: "{{ value_json.value }}"
      unit_of_measurement: "°C"
      device_class: temperature

    - name: "Heat Pump Flow Temperature"
      state_topic: "idm/heatpump/temperature_flow"
      value_template: "{{ value_json.value }}"
      unit_of_measurement: "°C"
      device_class: temperature

    - name: "Heat Pump COP"
      state_topic: "idm/heatpump/cop_heating"
      value_template: "{{ value_json.value }}"
      unit_of_measurement: ""
```

### Using State Topic

Alternatively, use the state topic for all sensors:

```yaml
mqtt:
  sensor:
    - name: "Heat Pump State"
      state_topic: "idm/heatpump/state"
      value_template: "{{ value_json | tojson }}"
```

## Troubleshooting

### Connection Issues

1. **Check broker is running**:
   ```bash
   mosquitto_sub -h localhost -t "test" -v
   ```

2. **Verify credentials**:
   - Check username and password are correct
   - Verify user has publish permissions

3. **Check firewall**:
   ```bash
   # Allow MQTT port
   sudo ufw allow 1883/tcp
   sudo ufw allow 8883/tcp
   ```

### TLS Issues

1. **Certificate verification fails**:
   - Ensure broker has valid TLS certificate
   - Check system CA certificates are up to date
   - Verify hostname matches certificate

2. **Self-signed certificates**:
   - Configure broker to use proper certificates
   - Or disable certificate verification (not recommended)

### Debug Logging

Enable debug logging to see MQTT activity:

```yaml
logging:
  level: "DEBUG"
```

Check logs:
```bash
# Docker
docker logs idm-logger

# Systemd
journalctl -u idm-logger -f
```

## Performance Considerations

### Publish Interval

- **Default**: 60 seconds (matches logging interval)
- **Minimum**: 1 second (realtime mode)
- **Recommendation**: 30-60 seconds for most use cases

Frequent publishing increases:
- Network traffic
- Broker load
- Client CPU usage

### Topic Structure

The default topic structure is optimized for:
- Individual sensor subscriptions
- Easy filtering in automation
- Minimal payload size

## Examples

### Node-RED Flow

Import this flow to subscribe to MQTT data:

```json
[
  {
    "id": "mqtt-in",
    "type": "mqtt in",
    "topic": "idm/heatpump/#",
    "broker": "mqtt-broker",
    "name": "Heat Pump Data"
  }
]
```

### Python Subscriber

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"{msg.topic}: {data['value']} {data['unit']}")

client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt.example.com", 1883)
client.subscribe("idm/heatpump/#")
client.loop_forever()
```

## Additional Resources

- [MQTT Specification](https://mqtt.org/)
- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [Paho MQTT Python Client](https://github.com/eclipse/paho.mqtt.python)
- [Home Assistant MQTT Integration](https://www.home-assistant.io/integrations/mqtt/)
