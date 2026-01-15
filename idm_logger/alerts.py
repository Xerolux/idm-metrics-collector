import threading
import time
import logging
import uuid
from typing import Dict, Any
from .db import db
from .notifications import notification_manager

logger = logging.getLogger(__name__)


class AlertManager:
    def __init__(self):
        self.alerts = []
        self.lock = threading.Lock()
        self.load()

    def load(self):
        with self.lock:
            self.alerts = db.get_alerts()
            logger.info(f"Loaded {len(self.alerts)} alerts")

    def add_alert(self, alert_data):
        with self.lock:
            alert_id = str(uuid.uuid4())
            alert = {
                "id": alert_id,
                "name": alert_data.get("name"),
                "type": alert_data.get("type"),  # 'threshold' or 'status'
                "sensor": alert_data.get("sensor"),
                "condition": alert_data.get("condition"),  # '>', '<', '=', '!='
                "threshold": alert_data.get("threshold"),
                "message": alert_data.get("message"),
                "enabled": alert_data.get("enabled", True),
                "interval_seconds": int(alert_data.get("interval_seconds", 0)),
                "last_triggered": 0,
            }
            db.add_alert(alert)
            self.alerts.append(alert)
            return alert

    def update_alert(self, alert_id, data):
        with self.lock:
            db.update_alert(alert_id, data)
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert.update(data)
                    break

    def delete_alert(self, alert_id):
        with self.lock:
            db.delete_alert(alert_id)
            self.alerts = [a for a in self.alerts if a["id"] != alert_id]

    def check_alerts(self, current_data: Dict[str, Any]):
        """
        Check all alerts against current data.
        Should be called periodically (e.g. every loop or every minute).
        """
        with self.lock:
            now = time.time()
            triggered_alerts_ids = []
            for alert in self.alerts:
                if not alert.get("enabled"):
                    continue

                try:
                    should_trigger = False
                    trigger_value = None

                    # Check cooldown / interval
                    last_triggered = alert.get("last_triggered", 0)
                    interval = alert.get("interval_seconds", 0)

                    if interval > 0 and (now - last_triggered) < interval:
                        continue

                    if alert["type"] == "status":
                        # Status reports trigger based on interval only
                        # If interval is 0, it would trigger every loop (bad), so force min interval
                        if interval <= 0:
                            logger.warning(
                                f"Status alert {alert['name']} has invalid interval 0, skipping"
                            )
                            continue
                        should_trigger = True

                    elif alert["type"] == "threshold":
                        sensor = alert.get("sensor")
                        condition = alert.get("condition")
                        threshold_str = str(alert.get("threshold"))

                        if sensor not in current_data:
                            continue

                        current_val = current_data[sensor]
                        trigger_value = current_val

                        # Helper to convert to float if possible
                        def to_float(v):
                            try:
                                return float(v)
                            except (ValueError, TypeError):
                                return None

                        val_f = to_float(current_val)
                        thresh_f = to_float(threshold_str)

                        if val_f is not None and thresh_f is not None:
                            # Numeric comparison
                            if condition == ">":
                                should_trigger = val_f > thresh_f
                            elif condition == "<":
                                should_trigger = val_f < thresh_f
                            elif condition == "=":
                                should_trigger = val_f == thresh_f
                            elif condition == "!=":
                                should_trigger = val_f != thresh_f
                        else:
                            # String comparison
                            val_s = str(current_val)
                            if condition == "=":
                                should_trigger = val_s == threshold_str
                            elif condition == "!=":
                                should_trigger = val_s != threshold_str

                    if should_trigger:
                        self._trigger_alert(alert, trigger_value)

                        # Update last_triggered in memory and batch update for db
                        alert["last_triggered"] = now
                        triggered_alerts_ids.append(alert["id"])

                except Exception as e:
                    logger.error(f"Error checking alert {alert.get('name')}: {e}")

            if triggered_alerts_ids:
                db.update_alerts_last_triggered(triggered_alerts_ids, now)

    def _trigger_alert(self, alert, value):
        logger.info(f"Triggering alert: {alert['name']}")

        message_template = alert.get("message", "")

        # Replace placeholders
        # Supported: {value}, {sensor}, {name}, {time}
        msg = message_template.replace("{name}", alert["name"])
        msg = msg.replace("{time}", time.strftime("%H:%M:%S"))

        if value is not None:
            msg = msg.replace("{value}", str(value))

        if alert.get("sensor"):
            msg = msg.replace("{sensor}", alert["sensor"])

        # Use notification manager instead of hardcoded Signal
        notification_manager.send_all(msg, subject=f"IDM Alert: {alert['name']}")


alert_manager = AlertManager()
