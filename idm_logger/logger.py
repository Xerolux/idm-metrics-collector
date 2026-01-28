# SPDX-License-Identifier: MIT
import time
import logging
import threading
import signal
import sys
import asyncio
from .config import config
from .heatpump_manager import heatpump_manager
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
from .backup import backup_manager
from .telemetry import telemetry_manager
from .model_updater import model_updater
from .migrations import get_default_heatpump_id, run_migration

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
    scheduler = None
    metrics = None
    mqtt = None

    # Start Web UI FIRST in background, so it's available even if Modbus/metrics fails
    try:
        web_enabled = config.get("web.enabled")
        if web_enabled:
            web_thread = threading.Thread(
                target=run_web, args=(heatpump_manager, None), daemon=True
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

    def backup_worker():
        last_backup_check = 0
        while not stop_event.is_set():
            now = time.time()
            # Check every hour if backup is due
            if now - last_backup_check > 3600:
                last_backup_check = now
                if config.get("backup.enabled", False):
                    try:
                        interval_hours = int(config.get("backup.interval", 24))
                        # Find last backup time
                        backups = backup_manager.list_backups()
                        should_run = True
                        if backups:
                            last_backup = backups[0]  # Sorted by date desc
                            # Parse ISO format from filename or metadata? list_backups returns sorted dicts
                            # last_backup['created_at'] is isoformat
                            from datetime import datetime

                            last_date = datetime.fromisoformat(
                                last_backup["created_at"]
                            )
                            # Convert to timestamp
                            last_ts = last_date.timestamp()

                            if (now - last_ts) < (interval_hours * 3600):
                                should_run = False

                        if should_run:
                            logger.info("Starting scheduled backup...")
                            backup_manager.create_backup()
                            # create_backup handles cleanup and auto-upload internally based on config
                    except Exception as e:
                        logger.error(f"Backup scheduler error: {e}")

            stop_event.wait(60)

    backup_thread = threading.Thread(target=backup_worker, daemon=True)
    backup_thread.start()

    # Run database migrations (single -> multi-heatpump)
    try:
        migrated_hp = run_migration()
        if migrated_hp:
            logger.info(
                f"Successfully migrated legacy configuration to heatpump {migrated_hp}"
            )
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}", exc_info=True)

    # Now initialize the backend components
    try:
        # Initialize HeatpumpManager
        asyncio.run(heatpump_manager.initialize())
    except Exception as e:
        logger.error(f"Failed to initialize HeatpumpManager: {e}", exc_info=True)

    # Metrics Writer
    try:
        metrics = MetricsWriter()
        set_metrics_writer(metrics)
        logger.info("Metrics writer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Metrics writer: {e}", exc_info=True)

    # MQTT Publisher
    try:
        mqtt_enabled = config.get("mqtt.enabled", False)
        mqtt_broker = config.get("mqtt.broker", "")

        if mqtt_enabled and mqtt_broker:
            mqtt_publisher.set_heatpump_manager(heatpump_manager)
            mqtt_publisher.start()
            mqtt = mqtt_publisher
            logger.info("MQTT publisher initialized")
        elif mqtt_enabled and not mqtt_broker:
            logger.warning(
                "MQTT is enabled but no broker configured - skipping MQTT initialization"
            )
    except Exception as e:
        logger.error(f"Failed to initialize MQTT publisher: {e}", exc_info=True)

    # Scheduler
    try:
        scheduler = Scheduler(heatpump_manager)
        if config.get("web.write_enabled"):
            scheduler.start()
            logger.info("Scheduler started")
        else:
            logger.info("Scheduler disabled (write_enabled is False)")
    except Exception as e:
        logger.error(f"Failed to initialize Scheduler: {e}", exc_info=True)

    # Update web.py with the actual instances
    if config.get("web.enabled"):
        import idm_logger.web as web_module

        web_module.heatpump_manager_instance = heatpump_manager
        web_module.scheduler_instance = scheduler

    # Start Telemetry Manager
    try:
        telemetry_manager.start()
    except Exception as e:
        logger.error(f"Failed to start Telemetry Manager: {e}")

    # Start Model Updater
    try:
        model_updater.start()
    except Exception as e:
        logger.error(f"Failed to start Model Updater: {e}")

    logger.info("Entering main loop...")

    try:
        while not stop_event.is_set():
            start_time = time.time()

            # Get current settings (can be changed via web UI)
            interval = config.get("logging.interval", 60)
            realtime_mode = config.get("logging.realtime_mode", False)

            # In realtime mode, use minimum interval (1 second)
            effective_interval = 1 if realtime_mode else interval

            # Read all heatpumps
            logger.debug("Reading sensors...")
            try:
                data = asyncio.run(heatpump_manager.read_all())

                if data:
                    # Flatten data for Web UI/WebSocket broadcasting
                    # Format: "hp_id.sensor_name": value
                    # Plus legacy support: "sensor_name": value (for default HP)
                    flat_data = {}
                    default_hp_id = get_default_heatpump_id()

                    for hp_id, measurements in data.items():
                        if not isinstance(measurements, dict):
                            logger.error(
                                f"Invalid measurements for {hp_id}: expected dict, got {type(measurements)} ({measurements})"
                            )
                            continue

                        for sensor, value in measurements.items():
                            # New format
                            flat_data[f"{hp_id}.{sensor}"] = value

                            # Legacy format (Default HP only)
                            if hp_id == default_hp_id:
                                flat_data[sensor] = value

                    # Update Web UI
                    update_current_data(flat_data)

                    # Send Telemetry
                    telemetry_manager.submit_data(data)

                    # Check Alerts
                    alert_manager.check_alerts(data)

                    # Write to Metrics
                    if metrics:
                        logger.debug(f"Writing metrics for {len(data)} heatpumps")
                        metrics.write_all_heatpumps(
                            data, heatpump_manager.get_all_configs()
                        )

                    # Publish to MQTT
                    if mqtt and mqtt.connected:
                        logger.debug("Publishing to MQTT")
                        mqtt.publish_data(data)
                else:
                    # Log only if we expected data but got none
                    if heatpump_manager.connected_count > 0:
                        logger.warning("No data read from any heatpump")
            except Exception as e:
                logger.error(f"Error reading sensors: {e}", exc_info=True)

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
        model_updater.stop()
        telemetry_manager.stop()
        if scheduler and config.get("web.write_enabled"):
            scheduler.stop()
        if mqtt:
            mqtt.stop()

        asyncio.run(heatpump_manager.close())
        logger.info("Stopped")


if __name__ == "__main__":
    main()
