import time
import logging
import threading
import signal
import sys
from .config import config
from .modbus import ModbusClient
from .metrics import MetricsWriter
from .web import run_web, update_current_data, set_metrics_writer
from .scheduler import Scheduler
from .log_handler import memory_handler
from .mqtt import mqtt_publisher
from .update_manager import (
    check_for_update,
    perform_update,
    can_run_updates,
    is_update_allowed,
)
from .alerts import alert_manager
from .ai.anomaly import anomaly_detector
from .signal_notifications import send_signal_message

# Get logger instance (configure in main())
logger = logging.getLogger("idm_logger")

stop_event = threading.Event()


def signal_handler(sig, frame):
    logger.info("Stopping...")
    stop_event.set()


def main():
    # Configure logging
    logger.setLevel(logging.INFO)

    # Create formatters and handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(memory_handler)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting IDM Heat Pump Logger")

    # Update log level from config
    try:
        log_level = config.get("logging.level", "INFO")
        logger.setLevel(getattr(logging, log_level))
        logger.info(f"Log level set to {log_level}")
    except Exception as e:
        logger.error(f"Failed to set log level from config: {e}")

    # Initialize these as None first
    modbus = None
    scheduler = None
    metrics = None
    mqtt = None

    # Start Web UI FIRST in background, so it's available even if Modbus/metrics fails
    try:
        web_enabled = config.get("web.enabled")
        if web_enabled:
            web_thread = threading.Thread(
                target=run_web, args=(None, None), daemon=True
            )
            web_thread.start()
            logger.info("Web UI started")
            # Give the web server a moment to start
            time.sleep(1)
    except Exception as e:
        logger.error(f"Failed to start web server: {e}", exc_info=True)

    def update_worker():
        while not stop_event.is_set():
            if config.get("updates.enabled", False):
                try:
                    if not can_run_updates():
                        logger.warning(
                            "Auto-Update deaktiviert: Repo-Pfad nicht gefunden."
                        )
                    else:
                        update_info = check_for_update()
                        if update_info.get("update_available"):
                            update_type = update_info.get("update_type", "unknown")
                            mode = config.get("updates.mode", "apply")
                            target = config.get("updates.target", "all")
                            if is_update_allowed(update_type, target):
                                if mode == "apply":
                                    logger.info(
                                        f"Update verfügbar ({update_type}). Starte automatisches Update..."
                                    )
                                    perform_update()
                                else:
                                    logger.info(
                                        f"Update verfügbar ({update_type}). Auto-Update auf 'check' gesetzt."
                                    )
                            else:
                                logger.info(
                                    f"Update verfügbar ({update_type}), aber Ziel '{target}' blockiert."
                                )
                except Exception as e:
                    logger.error(f"Auto-Update Fehler: {e}")
            interval_hours = config.get("updates.interval_hours", 12)
            stop_event.wait(max(3600, int(interval_hours) * 3600))

    update_thread = threading.Thread(target=update_worker, daemon=True)
    update_thread.start()

    # Now initialize the backend components
    try:
        # Modbus Client
        modbus = ModbusClient(host=config.get("idm.host"), port=config.get("idm.port"))
        logger.info(
            f"Modbus client initialized for {config.get('idm.host')}:{config.get('idm.port')}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize Modbus client: {e}", exc_info=True)

    # Metrics Writer
    try:
        metrics = MetricsWriter()
        set_metrics_writer(metrics)
        logger.info("Metrics writer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Metrics writer: {e}", exc_info=True)

    # MQTT Publisher
    try:
        if config.get("mqtt.enabled", False):
            # Pass sensors and write callback to MQTT publisher
            if modbus:
                mqtt_publisher.set_sensors(modbus.sensors, modbus.binary_sensors)
                if config.get("web.write_enabled"):
                    mqtt_publisher.set_write_callback(modbus.write_sensor)

            mqtt_publisher.start()
            mqtt = mqtt_publisher
            logger.info("MQTT publisher initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MQTT publisher: {e}", exc_info=True)

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
        import idm_logger.web as web_module

        web_module.modbus_client_instance = modbus
        web_module.scheduler_instance = scheduler

    logger.info("Entering main loop...")

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

                    # AI Anomaly Detection (Always learn)
                    anomaly_detector.update(data)

                    # Check AI Alerts if enabled
                    if config.get("ai.enabled", False):
                        # Configure model type if changed
                        model_type = config.get("ai.model", "rolling")
                        anomaly_detector.set_model_type(model_type)

                        sigma = float(config.get("ai.sensitivity", 3.0))
                        anomalies = anomaly_detector.detect(data, sigma)
                        if anomalies:
                            logger.info(f"AI Anomaly Detected: {anomalies}")
                            # Construct rich message
                            msg_lines = ["🤖 AI Anomalie erkannt!"]
                            msg_lines.append(f"Modus: {model_type}")

                            for sensor, det in anomalies.items():
                                z = det['z_score']
                                trend_icon = "↗️" if z > 0 else "↘️"
                                msg_lines.append(f"\n📍 {sensor}")
                                msg_lines.append(f"   Aktuell: {det['value']} {trend_icon}")
                                msg_lines.append(f"   Erwartet: ~{det['mean']:.2f}")
                                msg_lines.append(f"   Abweichung: {z:.1f}σ")

                            try:
                                # Simple rate limit prevention handled by user via cooldown?
                                # For AI, we hardcode a basic check or just send.
                                # Ideally we'd have a cooldown per sensor for AI too.
                                # For now, we trust the Z-score is significant.
                                send_signal_message("\n".join(msg_lines))
                            except Exception as e:
                                logger.error(f"Failed to send AI alert: {e}")

                    # Check Alerts
                    alert_manager.check_alerts(data)

                    # Write to Metrics
                    if metrics:
                        logger.debug(f"Writing {len(data)} points to Metrics")
                        metrics.write(data)

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
                logger.warning(
                    f"Loop took {elapsed:.2f}s, which is longer than interval {effective_interval}s"
                )

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
        anomaly_detector.save()  # Save learned model
        logger.info("Stopped")


if __name__ == "__main__":
    main()
