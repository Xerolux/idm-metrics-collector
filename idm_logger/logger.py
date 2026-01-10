import time
import logging
import threading
import signal
import sys
from .config import config
from .modbus import ModbusClient
from .influx import InfluxWriter
from .web import run_web, update_current_data, set_influx_writer
from .scheduler import Scheduler
from .log_handler import memory_handler
from .mqtt import mqtt_publisher

# Get logger instance (configure in main())
logger = logging.getLogger("idm_logger")

stop_event = threading.Event()

def signal_handler(sig, frame):
    logger.info("Stopping...")
    stop_event.set()

def main():
    # Configure logging
    logger.setLevel(getattr(logging, config.get("logging.level", "INFO")))

    # Create formatters and handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler with forced flush
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.stream.reconfigure(line_buffering=True)  # Force line buffering

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(memory_handler)

    # Force flush after adding handlers
    sys.stdout.flush()
    sys.stderr.flush()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting IDM Heat Pump Logger")

    # Initialize these as None first
    modbus = None
    scheduler = None
    influx = None
    mqtt = None

    # Start Web UI FIRST in background, so it's available even if Modbus/InfluxDB fails
    logger.info("Checking if web is enabled...")
    web_enabled = config.get("web.enabled")
    logger.info(f"Web enabled: {web_enabled}")
    if web_enabled:
        logger.info("Creating web thread...")
        web_thread = threading.Thread(target=run_web, args=(None, None), daemon=True)
        logger.info("Starting web thread...")
        web_thread.start()
        logger.info("Web UI thread started")
        # Give the web server a moment to start
        logger.info("Sleeping for 1 second...")
        time.sleep(1)
        logger.info("Sleep complete")

    # Now initialize the backend components
    try:
        # Modbus Client
        modbus = ModbusClient(
            host=config.get("idm.host"),
            port=config.get("idm.port")
        )
        logger.info(f"Modbus client initialized for {config.get('idm.host')}:{config.get('idm.port')}")
    except Exception as e:
        logger.error(f"Failed to initialize Modbus client: {e}")

    # Influx Writer
    try:
        influx = InfluxWriter()
        set_influx_writer(influx)
        logger.info("InfluxDB writer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize InfluxDB writer: {e}")

    # MQTT Publisher
    try:
        if config.get("mqtt.enabled", False):
            mqtt_publisher.start()
            mqtt = mqtt_publisher
            logger.info("MQTT publisher initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MQTT publisher: {e}")

    # Scheduler (only if we have a working modbus client)
    if modbus:
        scheduler = Scheduler(modbus)
        if config.get("web.write_enabled"):
            scheduler.start()
            logger.info("Scheduler started")
        else:
            logger.info("Scheduler disabled (write_enabled is False)")
    else:
        logger.warning("Scheduler not started (Modbus client unavailable)")

    # Update web.py with the actual instances
    if config.get("web.enabled"):
        from .web import modbus_client_instance, scheduler_instance
        import idm_logger.web as web_module
        web_module.modbus_client_instance = modbus
        web_module.scheduler_instance = scheduler

    try:
        while not stop_event.is_set():
            start_time = time.time()

            # Get current settings (can be changed via web UI)
            interval = config.get("logging.interval", 60)
            realtime_mode = config.get("logging.realtime_mode", False)

            # In realtime mode, use minimum interval (1 second)
            effective_interval = 1 if realtime_mode else interval

            # Read only if modbus is available
            if modbus:
                logger.debug("Reading sensors...")
                data = modbus.read_sensors()

                if data:
                    # Update Web UI
                    update_current_data(data)

                    # Write to Influx
                    if influx:
                        logger.debug(f"Writing {len(data)} points to InfluxDB")
                        influx.write(data)

                    # Publish to MQTT
                    if mqtt and mqtt.connected:
                        logger.debug(f"Publishing {len(data)} points to MQTT")
                        mqtt.publish_data(data)
                else:
                    logger.warning("No data read from Modbus")
            else:
                logger.debug("Modbus client not available, skipping sensor read")

            # Sleep
            elapsed = time.time() - start_time
            if elapsed > effective_interval:
                logger.warning(f"Loop took {elapsed:.2f}s, which is longer than interval {effective_interval}s")

            sleep_time = max(0, effective_interval - elapsed)
            stop_event.wait(sleep_time)

    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        if scheduler and config.get("web.write_enabled"):
            scheduler.stop()
        if mqtt:
            mqtt.stop()
        if modbus:
            modbus.close()
        logger.info("Stopped")

if __name__ == "__main__":
    main()
