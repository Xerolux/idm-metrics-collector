# Solar / PV Integration

You can integrate your Photovoltaic (PV) system with the iDM Heat Pump to optimize energy usage (PV Surplus charging).

## Prerequisites

*   A working PV system (inverter) that provides data via Modbus TCP, MQTT, or another API.
*   `idm-logger` running and connected to your iDM Heat Pump.
*   MQTT Broker (optional but recommended for easy integration).

## Registers

The iDM Heat Pump (Navigator 2.0) exposes specific registers for PV integration:

| Register (Dec) | Name | Sensor Name | Unit | Type | Access | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **74** | Aktueller PV-Überschuss | `power_solar_surplus` | kW | Float32 | RW | Write the current PV surplus (feed-in) here. |
| 78 | Aktuelle PV Produktion | `power_solar_production` | kW | Float32 | RW | Write current PV production. |
| 82 | Hausverbrauch | `power_use_house` | kW | Float32 | RW | Write current house consumption. |

**Important:** The most critical register for optimizing heat pump operation is **74 (PV Surplus)**.

## How to use

### Via MQTT (Recommended)

1.  **Enable MQTT** in your `config.yaml` or via the Web UI.
2.  **Publish** the current PV surplus value (in kW) to the following topic:

    ```
    idm/heatpump/power_solar_surplus/set
    ```

    *   **Payload**: The value as a number (e.g., `2.5` for 2500 Watts).
    *   **Unit**: Kilowatts (kW). If your inverter provides Watts, divide by 1000.
    *   **Frequency**: You can update this every few seconds or minutes (e.g., every 10-60 seconds).

    **Example:**
    ```bash
    mosquitto_pub -h your_broker -t "idm/heatpump/power_solar_surplus/set" -m "3.2"
    ```

### Via Python Script (External)

If you prefer a direct Modbus connection or a custom script, you can write to register 74 directly.

*   **Address**: 74
*   **Type**: Float32 (2 registers)
*   **Byte Order**: Big Endian
*   **Word Order**: Little Endian

*Note: The `idm-logger` handles the connection to the heat pump. If you use an external script to write via Modbus, ensure it doesn't conflict with the logger's connection limit (Modbus TCP usually allows multiple connections, but limited).*

### Logic

*   **Surplus > 0**: The heat pump may increase its target temperature to store energy (if configured in Navigator settings).
*   **Surplus = 0**: Normal operation.

## Configuration in iDM Navigator

Ensure your iDM Heat Pump is configured to use the PV signal:
*   Go to **Photovoltaic** settings in the Navigator panel.
*   Enable **PV signal** source (often called "GLT" or "Modbus TCP").

## Troubleshooting

*   **Value not showing**: Check `idm-logger` logs. The sensor `power_solar_surplus` is write-only for reading purposes in some configurations (to avoid errors), so it might not appear in the standard read loop or InfluxDB unless you write to it.
*   **Scaling**: Ensure you are sending **kW** (Kilowatts), not Watts. Sending `2500` instead of `2.5` will be interpreted as 2.5 MegaWatts!
