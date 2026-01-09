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

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get("logging.level", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        memory_handler
    ]
)
logger = logging.getLogger("idm_logger")

stop_event = threading.Event()

def signal_handler(sig, frame):
    logger.info("Stopping...")
    stop_event.set()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting IDM Heat Pump Logger")

    # Modbus Client
    modbus = ModbusClient(
        host=config.get("idm.host"),
        port=config.get("idm.port")
    )

    # Scheduler
    scheduler = Scheduler(modbus)
    if config.get("web.write_enabled"):
        scheduler.start()
    else:
        logger.info("Scheduler disabled (write_enabled is False)")

    # Start Web UI in background
    if config.get("web.enabled"):
        web_thread = threading.Thread(target=run_web, args=(modbus, scheduler), daemon=True)
        web_thread.start()

    # Influx Writer
    influx = InfluxWriter()
    set_influx_writer(influx)

    try:
        while not stop_event.is_set():
            start_time = time.time()

            # Get current settings (can be changed via web UI)
            interval = config.get("logging.interval", 60)
            realtime_mode = config.get("logging.realtime_mode", False)

            # In realtime mode, use minimum interval (1 second)
            effective_interval = 1 if realtime_mode else interval

            # Read
            logger.debug("Reading sensors...")
            data = modbus.read_sensors()

            if data:
                # Update Web UI
                update_current_data(data)

                # Write to Influx
                logger.debug(f"Writing {len(data)} points to InfluxDB")
                influx.write(data)
            else:
                logger.warning("No data read from Modbus")

            # Sleep
            elapsed = time.time() - start_time
            if elapsed > effective_interval:
                logger.warning(f"Loop took {elapsed:.2f}s, which is longer than interval {effective_interval}s")

            sleep_time = max(0, effective_interval - elapsed)
            stop_event.wait(sleep_time)

    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        if config.get("web.write_enabled"):
            scheduler.stop()
        modbus.close()
        logger.info("Stopped")

if __name__ == "__main__":
    main()
