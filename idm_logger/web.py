from flask import (
    Flask,
    request,
    jsonify,
    session,
    abort,
    send_from_directory,
    send_file,
)
from waitress import serve
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .technician_auth import calculate_codes
from .config import config
from .sensor_addresses import SensorFeatures
from .log_handler import memory_handler
from .backup import backup_manager, BACKUP_DIR
from .mqtt import mqtt_publisher
from .signal_notifications import send_signal_message
from .update_manager import (
    check_for_update,
    perform_update as run_update,
    get_current_version,
    can_run_updates,
)
from .alerts import alert_manager
from .templates import get_alert_templates
from shutil import which
import threading
import logging
import requests
import functools
import os
import signal
import ipaddress
import time
from pathlib import Path

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.get_flask_secret_key()
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Swagger/OpenAPI Configuration
app.config["SWAGGER"] = {
    "title": "IDM Metrics Collector API",
    "uiversion": 3,
    "version": "0.6.0",
    "description": "API for IDM Heat Pump Monitoring & Control",
}
swagger = Swagger(app)

# Rate Limiter Configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# Shared state
current_data = {}
data_lock = threading.Lock()
modbus_client_instance = None
scheduler_instance = None
metrics_writer_instance = None

# Cache for network security objects to avoid re-parsing on every request
_net_sec_cache = {
    "whitelist_ref": None,
    "whitelist_nets": [],
    "blacklist_ref": None,
    "blacklist_nets": [],
}


def update_current_data(data):
    with data_lock:
        current_data.clear()
        current_data.update(data)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Nicht autorisiert"}), 401
            return jsonify({"error": "Nicht autorisiert"}), 401
        return view(**kwargs)

    return wrapped_view


@app.before_request
def check_setup():
    pass


@app.before_request
def check_ip_whitelist():
    """Check if the request IP is allowed based on whitelist/blacklist."""
    if not config.get("network_security.enabled", False):
        return

    client_ip = request.remote_addr
    if not client_ip:
        return

    try:
        ip = ipaddress.ip_address(client_ip)
    except ValueError:
        logger.warning(f"Invalid client IP: {client_ip}")
        abort(403)
        return

    whitelist = config.get("network_security.whitelist", [])
    blacklist = config.get("network_security.blacklist", [])

    # Update blacklist cache if needed
    if blacklist is not _net_sec_cache["blacklist_ref"]:
        new_blacklist_nets = []
        for block in blacklist:
            try:
                new_blacklist_nets.append(
                    (ipaddress.ip_network(block, strict=False), block)
                )
            except ValueError:
                logger.error(f"Invalid blacklist entry: {block}")

        _net_sec_cache["blacklist_nets"] = new_blacklist_nets
        _net_sec_cache["blacklist_ref"] = blacklist

    # Check blacklist first
    for net, original_block in _net_sec_cache["blacklist_nets"]:
        if ip in net:
            logger.warning(
                f"Blocked IP {client_ip} (matched blacklist {original_block})"
            )
            abort(403)

    # Update whitelist cache if needed
    if whitelist is not _net_sec_cache["whitelist_ref"]:
        new_whitelist_nets = []
        for allow in whitelist:
            try:
                new_whitelist_nets.append(ipaddress.ip_network(allow, strict=False))
            except ValueError:
                logger.error(f"Invalid whitelist entry: {allow}")

        _net_sec_cache["whitelist_nets"] = new_whitelist_nets
        _net_sec_cache["whitelist_ref"] = whitelist

    # Check whitelist if it exists and is not empty
    if whitelist:
        allowed = False
        for net in _net_sec_cache["whitelist_nets"]:
            if ip in net:
                allowed = True
                break

        if not allowed:
            logger.warning(f"Blocked IP {client_ip} (not in whitelist)")
            abort(403)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.context_processor
def inject_config():
    safe_config = config.data.copy()
    return dict(config=safe_config)


@app.route("/api/setup", methods=["POST"])
@limiter.limit("5 per minute")
def setup():
    """
    Setup the initial configuration.
    ---
    tags:
      - Setup
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            idm_host:
              type: string
            idm_port:
              type: integer
            password:
              type: string
    responses:
      200:
        description: Setup completed successfully
    """
    if config.is_setup():
        return jsonify({"error": "Bereits eingerichtet"}), 400

    data = request.get_json()
    try:
        config.data["idm"]["host"] = data.get("idm_host")
        config.data["idm"]["port"] = int(data.get("idm_port"))

        if "circuits" in data:
            config.data["idm"]["circuits"] = data["circuits"]
        if "zones" in data:
            config.data["idm"]["zones"] = data["zones"]

        if "metrics" not in config.data:
            config.data["metrics"] = {}
        config.data["metrics"]["url"] = data.get("metrics_url")

        password = data.get("password")
        if not password or len(password) < 6:
            return jsonify(
                {"error": "Passwort muss mindestens 6 Zeichen lang sein"}
            ), 400

        config.set_admin_password(password)
        config.data["web"]["write_enabled"] = True
        config.data["setup_completed"] = True
        config.save()

        return jsonify(
            {
                "success": True,
                "message": "Einrichtung abgeschlossen. Bitte Dienst neu starten.",
            }
        )
    except Exception as e:
        logger.error(f"Setup error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """
    Authenticate user.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            password:
              type: string
    responses:
      200:
        description: Authentication successful
      401:
        description: Invalid password
      429:
        description: Too many attempts
    """
    data = request.get_json()
    password = data.get("password")

    if config.check_admin_password(password):
        session["logged_in"] = True
        session.permanent = True
        return jsonify({"success": True})
    else:
        logger.warning(f"Failed login attempt from {request.remote_addr}")
        return jsonify({"success": False, "message": "Ungültiges Passwort"}), 401


@app.route("/api/auth/check")
def check_auth():
    return jsonify({"authenticated": session.get("logged_in", False)})


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return jsonify({"success": True})


@app.route("/api/data")
def get_data():
    """
    Get current sensor data.
    ---
    tags:
      - Data
    responses:
      200:
        description: Current sensor readings
    """
    with data_lock:
        return jsonify(current_data)


@app.route("/api/health")
def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return jsonify(
        {
            "status": "healthy",
            "setup_completed": config.is_setup(),
            "client_ip": request.remote_addr,
        }
    ), 200


@app.route("/api/status")
def status_check():
    """Detailed status endpoint."""
    metrics_status = None
    if metrics_writer_instance:
        metrics_status = metrics_writer_instance.get_status()

    mqtt_status = mqtt_publisher.get_status() if mqtt_publisher else None

    return jsonify(
        {
            "status": "running",
            "setup_completed": config.is_setup(),
            "metrics": metrics_status,
            "mqtt": mqtt_status,
            "modbus_connected": modbus_client_instance is not None,
            "scheduler_running": scheduler_instance is not None
            and config.get("web.write_enabled"),
        }
    )


@app.route("/api/logs")
@login_required
def logs_page():
    logs = memory_handler.get_logs()
    logs.reverse()
    return jsonify(logs)


@app.route("/api/tools/technician-code", methods=["GET"])
@login_required
def get_technician_code():
    try:
        codes = calculate_codes()
        codes["server_time"] = time.strftime("%H:%M:%S")
        return jsonify(codes)
    except Exception as e:
        logger.error(f"Error generating codes: {e}")
        return jsonify({"error": "Fehler beim Generieren der Codes"}), 500


@app.route("/api/config", methods=["GET", "POST"])
@login_required
def config_page():
    if request.method == "GET":
        safe_config = config.data.copy()
        response = safe_config
        response["_meta"] = {
            "token_synced": True,
            "token_source": "environment"
            if os.environ.get("METRICS_URL")
            else "database",
        }
        return jsonify(response)

    if request.method == "POST":
        data = request.get_json()
        try:
            # IDM Host
            if "idm_host" in data:
                config.data["idm"]["host"] = data["idm_host"]
            if "idm_port" in data:
                try:
                    port = int(data["idm_port"])
                    if 1 <= port <= 65535:
                        config.data["idm"]["port"] = port
                    else:
                        return jsonify(
                            {"error": "Port muss zwischen 1 und 65535 sein"}
                        ), 400
                except ValueError:
                    return jsonify({"error": "Ungültige Portnummer"}), 400

            if "circuits" in data:
                config.data["idm"]["circuits"] = data["circuits"]
            if "zones" in data:
                config.data["idm"]["zones"] = data["zones"]
            if "write_enabled" in data:
                config.data["web"]["write_enabled"] = bool(data["write_enabled"])
            if "logging_interval" in data:
                try:
                    interval = int(data["logging_interval"])
                    if 1 <= interval <= 3600:
                        config.data["logging"]["interval"] = interval
                    else:
                        return jsonify(
                            {
                                "error": "Intervall muss zwischen 1 und 3600 Sekunden sein"
                            }
                        ), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger Intervallwert"}), 400
            if "realtime_mode" in data:
                config.data["logging"]["realtime_mode"] = bool(data["realtime_mode"])
            if "metrics_url" in data:
                config.data["metrics"]["url"] = data["metrics_url"]

            # MQTT
            if "mqtt_enabled" in data:
                config.data["mqtt"]["enabled"] = bool(data["mqtt_enabled"])
            if "mqtt_broker" in data:
                config.data["mqtt"]["broker"] = data["mqtt_broker"]
            if "mqtt_port" in data:
                try:
                    port = int(data["mqtt_port"])
                    if 1 <= port <= 65535:
                        config.data["mqtt"]["port"] = port
                    else:
                        return jsonify(
                            {"error": "MQTT Port muss zwischen 1 und 65535 sein"}
                        ), 400
                except ValueError:
                    return jsonify({"error": "Ungültige MQTT Portnummer"}), 400
            if "mqtt_username" in data:
                config.data["mqtt"]["username"] = data["mqtt_username"]
            if "mqtt_password" in data and data["mqtt_password"]:
                config.data["mqtt"]["password"] = data["mqtt_password"]
            if "mqtt_use_tls" in data:
                config.data["mqtt"]["use_tls"] = bool(data["mqtt_use_tls"])
            if "mqtt_topic_prefix" in data:
                config.data["mqtt"]["topic_prefix"] = data["mqtt_topic_prefix"]
            if "mqtt_ha_discovery_enabled" in data:
                config.data["mqtt"]["ha_discovery_enabled"] = bool(
                    data["mqtt_ha_discovery_enabled"]
                )
            if "mqtt_ha_discovery_prefix" in data:
                config.data["mqtt"]["ha_discovery_prefix"] = data[
                    "mqtt_ha_discovery_prefix"
                ]
            if "mqtt_publish_interval" in data:
                try:
                    interval = int(data["mqtt_publish_interval"])
                    if 1 <= interval <= 3600:
                        config.data["mqtt"]["publish_interval"] = interval
                    else:
                        return jsonify(
                            {
                                "error": "MQTT Publish-Intervall muss zwischen 1 und 3600 Sekunden sein"
                            }
                        ), 400
                except ValueError:
                    return jsonify({"error": "Ungültiges MQTT Publish-Intervall"}), 400
            if "mqtt_qos" in data:
                try:
                    qos = int(data["mqtt_qos"])
                    if qos in [0, 1, 2]:
                        config.data["mqtt"]["qos"] = qos
                    else:
                        return jsonify(
                            {"error": "MQTT QoS muss 0, 1, oder 2 sein"}
                        ), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger MQTT QoS Wert"}), 400

            # Signal
            if "signal_enabled" in data:
                config.data["signal"]["enabled"] = bool(data["signal_enabled"])
            if "signal_sender" in data:
                config.data["signal"]["sender"] = data["signal_sender"]
            if "signal_cli_path" in data:
                config.data["signal"]["cli_path"] = data["signal_cli_path"]
            if "signal_recipients" in data:
                recipients = data["signal_recipients"]
                if isinstance(recipients, str):
                    recipients = [
                        x.strip() for x in recipients.split("\n") if x.strip()
                    ]
                config.data["signal"]["recipients"] = recipients

            # AI
            if "ai_enabled" in data:
                config.data["ai"]["enabled"] = bool(data["ai_enabled"])
            if "ai_sensitivity" in data:
                try:
                    sens = float(data["ai_sensitivity"])
                    if 1.0 <= sens <= 10.0:
                        config.data["ai"]["sensitivity"] = sens
                    else:
                        return jsonify(
                            {"error": "AI Sensitivität muss zwischen 1.0 und 10.0 sein"}
                        ), 400
                except ValueError:
                    return jsonify(
                        {"error": "Ungültiger Wert für AI Sensitivität"}
                    ), 400

            # Updates
            if "updates_enabled" in data:
                config.data["updates"]["enabled"] = bool(data["updates_enabled"])
            if "updates_interval_hours" in data:
                try:
                    interval = int(data["updates_interval_hours"])
                    if 1 <= interval <= 168:
                        config.data["updates"]["interval_hours"] = interval
                    else:
                        return jsonify(
                            {
                                "error": "Update-Intervall muss zwischen 1 und 168 Stunden sein"
                            }
                        ), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger Update-Intervallwert"}), 400
            if "updates_mode" in data:
                if data["updates_mode"] not in ["check", "apply"]:
                    return jsonify(
                        {"error": "Update-Modus muss 'check' oder 'apply' sein"}
                    ), 400
                config.data["updates"]["mode"] = data["updates_mode"]
            if "updates_target" in data:
                if data["updates_target"] not in ["all", "major", "minor", "patch"]:
                    return jsonify(
                        {"error": "Update-Ziel muss all, major, minor oder patch sein"}
                    ), 400
                config.data["updates"]["target"] = data["updates_target"]

            # Network Security
            if "network_security_enabled" in data:
                config.data["network_security"]["enabled"] = bool(
                    data["network_security_enabled"]
                )
            if "network_security_whitelist" in data:
                whitelist = data["network_security_whitelist"]
                if isinstance(whitelist, str):
                    whitelist = [x.strip() for x in whitelist.split("\n") if x.strip()]
                validated_whitelist = []
                for entry in whitelist:
                    try:
                        ipaddress.ip_network(entry, strict=False)
                        validated_whitelist.append(entry)
                    except ValueError:
                        return jsonify(
                            {"error": f"Ungültiger Whitelist-Eintrag: {entry}"}
                        ), 400
                config.data["network_security"]["whitelist"] = validated_whitelist

            if "network_security_blacklist" in data:
                blacklist = data["network_security_blacklist"]
                if isinstance(blacklist, str):
                    blacklist = [x.strip() for x in blacklist.split("\n") if x.strip()]
                validated_blacklist = []
                for entry in blacklist:
                    try:
                        ipaddress.ip_network(entry, strict=False)
                        validated_blacklist.append(entry)
                    except ValueError:
                        return jsonify(
                            {"error": f"Ungültiger Blacklist-Eintrag: {entry}"}
                        ), 400
                config.data["network_security"]["blacklist"] = validated_blacklist

            new_pass = data.get("new_password")
            if new_pass:
                if len(new_pass) < 6:
                    return jsonify({"error": "Neues Passwort zu kurz"}), 400
                config.set_admin_password(new_pass)

            config.save()
            return jsonify(
                {
                    "success": True,
                    "message": "Konfiguration gespeichert. Neustart erforderlich.",
                }
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/restart", methods=["POST"])
@login_required
def restart_service():
    logger.info("Service restart requested by user")

    def delayed_restart():
        import time

        time.sleep(1)
        logger.info("Initiating restart...")
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=delayed_restart, daemon=True).start()
    return jsonify({"success": True, "message": "Starte Dienst neu..."})


@app.route("/api/version", methods=["GET"])
def get_version():
    try:
        return jsonify({"version": get_current_version()})
    except Exception as e:
        logger.error(f"Error getting version: {e}")
        return jsonify({"version": "unknown"})


@app.route("/api/check-update", methods=["GET"])
@login_required
def check_update():
    try:
        return jsonify(check_for_update())
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/perform-update", methods=["POST"])
@login_required
def perform_update():
    try:
        logger.info("Update requested by user")

        def do_update():
            try:
                time.sleep(2)
                if not can_run_updates():
                    logger.warning("Update skipped: repo path not found.")
                    return
                run_update()
            except Exception as e:
                logger.error(f"Update failed: {e}")

        threading.Thread(target=do_update, daemon=True).start()
        return jsonify({"success": True, "message": "Update gestartet"})
    except Exception as e:
        logger.error(f"Error starting update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/signal/test", methods=["POST"])
@login_required
def signal_test():
    data = request.get_json() or {}
    message = data.get("message", "Testnachricht vom IDM Metrics Collector")
    try:
        send_signal_message(message)
        return jsonify({"success": True, "message": "Signal-Testnachricht gesendet"})
    except Exception as e:
        logger.error(f"Signal test failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/signal/status", methods=["GET"])
@login_required
def signal_status():
    signal_config = config.data.get("signal", {})
    recipients = signal_config.get("recipients", []) or []
    cli_path = signal_config.get("cli_path", "signal-cli")
    return jsonify(
        {
            "enabled": signal_config.get("enabled", False),
            "sender_set": bool(signal_config.get("sender")),
            "recipients_count": len(recipients),
            "cli_path": cli_path,
            "cli_available": which(cli_path) is not None,
        }
    )


def validate_write(sensor_name, value):
    if not modbus_client_instance:
        return False, "Modbus-Client nicht verfügbar"

    sensor = modbus_client_instance.sensors.get(
        sensor_name
    ) or modbus_client_instance.binary_sensors.get(sensor_name)
    if not sensor:
        return False, "Sensor nicht gefunden"

    if hasattr(sensor, "enum") and sensor.enum:
        try:
            if str(value).isdigit():
                val_int = int(value)
                try:
                    sensor.enum(val_int)
                except ValueError:
                    return False, f"Wert {value} ist keine gültige Option"
            else:
                if value not in sensor.enum.__members__:
                    return False, f"Option {value} nicht gefunden"
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            logger.debug(f"Enum validation failed for {sensor_name}: {e}")
            return False, "Ungültiger Enum-Wert"

    elif hasattr(sensor, "min_value") and hasattr(sensor, "max_value"):
        try:
            val_float = float(value)
            if sensor.min_value is not None and val_float < sensor.min_value:
                return False, f"Wert {value} unter Minimum ({sensor.min_value})"
            if sensor.max_value is not None and val_float > sensor.max_value:
                return False, f"Wert {value} über Maximum ({sensor.max_value})"
        except ValueError:
            return False, "Ungültige Zahl"

    return True, None


@app.route("/api/control", methods=["GET", "POST"])
@login_required
def control_page():
    """
    Control sensors.
    ---
    tags:
      - Control
    responses:
      200:
        description: List of writable sensors or success message
    """
    if not config.get("web.write_enabled"):
        return jsonify({"error": "Schreibzugriff deaktiviert"}), 403

    if request.method == "POST":
        data = request.get_json()
        sensor_name = data.get("sensor")
        value = data.get("value")

        valid, msg = validate_write(sensor_name, value)
        if not valid:
            return jsonify({"error": msg}), 400

        try:
            if modbus_client_instance:
                modbus_client_instance.write_sensor(sensor_name, value)
                return jsonify(
                    {
                        "success": True,
                        "message": f"{value} erfolgreich auf {sensor_name} geschrieben",
                    }
                )
            else:
                return jsonify({"error": "Modbus-Client nicht verfügbar"}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    writable_sensors = []
    if modbus_client_instance:
        all_sensors = {
            **modbus_client_instance.sensors,
            **modbus_client_instance.binary_sensors,
        }
        for name, sensor in all_sensors.items():
            if sensor.supported_features != SensorFeatures.NONE:
                s_info = {
                    "name": sensor.name,
                    "unit": getattr(sensor, "unit", ""),
                    "description": getattr(sensor, "description", ""),
                    "features": sensor.supported_features.name
                    if hasattr(sensor.supported_features, "name")
                    else sensor.supported_features,
                    "min": getattr(sensor, "min_value", None),
                    "max": getattr(sensor, "max_value", None),
                    "enum": [{"name": m.name, "value": m.value} for m in sensor.enum]
                    if hasattr(sensor, "enum") and sensor.enum
                    else None,
                    "eeprom_sensitive": getattr(sensor, "eeprom_sensitive", False),
                    "cyclic_change_required": getattr(
                        sensor, "cyclic_change_required", False
                    ),
                }
                writable_sensors.append(s_info)

    writable_sensors.sort(key=lambda s: s["name"])
    return jsonify(writable_sensors)


@app.route("/api/schedule", methods=["GET", "POST"])
@login_required
def schedule_page():
    if not config.get("web.write_enabled"):
        return jsonify({"error": "Schreibzugriff deaktiviert"}), 403

    if not scheduler_instance:
        return jsonify({"error": "Scheduler nicht verfügbar"}), 503

    if request.method == "POST":
        data = request.get_json()
        action = data.get("action")

        if action == "add":
            sensor = data.get("sensor")
            value = data.get("value")

            valid, msg = validate_write(sensor, value)
            if not valid:
                return jsonify({"error": msg}), 400
            else:
                job = {
                    "sensor": sensor,
                    "value": value,
                    "time": data.get("time"),
                    "days": data.get("days", []),
                }
                if scheduler_instance:
                    scheduler_instance.add_job(job)
                    return jsonify({"success": True, "message": "Zeitplan hinzugefügt"})

        elif action == "delete":
            job_id = data.get("job_id")
            if scheduler_instance:
                scheduler_instance.delete_job(job_id)
                return jsonify({"success": True, "message": "Zeitplan gelöscht"})

        elif action == "toggle":
            job_id = data.get("job_id")
            current_state = data.get("current_state")
            if scheduler_instance:
                scheduler_instance.update_job(job_id, {"enabled": not current_state})
                state_text = "pausiert" if current_state else "fortgesetzt"
                return jsonify({"success": True, "message": f"Zeitplan {state_text}"})

        elif action == "run_now":
            job_id = data.get("job_id")
            if scheduler_instance:
                job = next(
                    (j for j in scheduler_instance.jobs if j["id"] == job_id), None
                )
                if job and modbus_client_instance:
                    try:
                        modbus_client_instance.write_sensor(job["sensor"], job["value"])
                        return jsonify(
                            {
                                "success": True,
                                "message": f"Ausgeführt: {job['sensor']} = {job['value']}",
                            }
                        )
                    except Exception as e:
                        return jsonify({"error": str(e)}), 500
                else:
                    return jsonify(
                        {"error": "Job nicht gefunden oder System nicht verfügbar"}
                    ), 404

        return jsonify({"error": "Ungültige Aktion"}), 400

    jobs = scheduler_instance.jobs if scheduler_instance else []

    writable_sensors = []
    if modbus_client_instance:
        try:
            all_sensors = {
                **modbus_client_instance.sensors,
                **modbus_client_instance.binary_sensors,
            }
            for name, sensor in all_sensors.items():
                if sensor.supported_features != SensorFeatures.NONE:
                    s_info = {
                        "name": sensor.name,
                        "unit": getattr(sensor, "unit", ""),
                        "enum": [
                            {"name": m.name, "value": m.value} for m in sensor.enum
                        ]
                        if hasattr(sensor, "enum") and sensor.enum
                        else None,
                        "eeprom_sensitive": getattr(sensor, "eeprom_sensitive", False),
                        "cyclic_change_required": getattr(
                            sensor, "cyclic_change_required", False
                        ),
                    }
                    writable_sensors.append(s_info)
        except Exception as e:
            logger.error(f"Error loading sensors for schedule: {e}")

    writable_sensors.sort(key=lambda s: s["name"])
    return jsonify({"jobs": jobs, "sensors": writable_sensors})


@app.route("/api/alerts", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def alerts_api():
    if request.method == "GET":
        return jsonify(alert_manager.alerts)

    if request.method == "POST":
        data = request.get_json()

        if not data.get("name"):
            return jsonify({"error": "Name fehlt"}), 400
        if data.get("type") not in ["threshold", "status"]:
            return jsonify({"error": "Ungültiger Typ"}), 400
        if data["type"] == "threshold" and not data.get("sensor"):
            return jsonify({"error": "Sensor fehlt"}), 400

        try:
            alert = alert_manager.add_alert(data)
            return jsonify({"success": True, "alert": alert})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == "PUT":
        data = request.get_json()
        alert_id = data.get("id")
        if not alert_id:
            return jsonify({"error": "ID fehlt"}), 400

        try:
            alert_manager.update_alert(alert_id, data)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == "DELETE":
        alert_id = request.args.get("id")
        if not alert_id:
            return jsonify({"error": "ID fehlt"}), 400

        try:
            alert_manager.delete_alert(alert_id)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/alerts/templates", methods=["GET"])
@login_required
def get_templates():
    return jsonify(get_alert_templates())


@app.route("/<path:path>")
def catch_all(path):
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/backup/create", methods=["POST"])
@login_required
def create_backup():
    result = backup_manager.create_backup()
    if result.get("success"):
        backup_manager.cleanup_old_backups(keep_count=10)
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route("/api/backup/list", methods=["GET"])
@login_required
def list_backups():
    backups = backup_manager.list_backups()
    return jsonify({"backups": backups}), 200


@app.route("/api/backup/download/<filename>", methods=["GET"])
@login_required
def download_backup(filename):
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Ungültiger Dateiname"}), 400

    backup_path = Path(BACKUP_DIR) / filename

    if not backup_path.exists():
        return jsonify({"error": "Backup nicht gefunden"}), 404

    try:
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/zip",
        )
    except Exception as e:
        logger.error(f"Failed to send backup file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/backup/restore", methods=["POST"])
@login_required
def restore_backup():
    if "file" not in request.files:
        data = request.get_json() or {}
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "Keine Backup-Datei angegeben"}), 400
        if ".." in filename or "/" in filename or "\\" in filename:
            return jsonify({"error": "Ungültiger Dateiname"}), 400
        backup_path = Path(BACKUP_DIR) / filename
    else:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Keine Datei ausgewählt"}), 400
        safe_filename = file.filename
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            return jsonify({"error": "Ungültiger Dateiname"}), 400
        temp_path = Path(BACKUP_DIR) / f"temp_{safe_filename}"
        file.save(temp_path)
        backup_path = temp_path

    try:
        restore_secrets = request.form.get("restore_secrets", "false").lower() == "true"
        result = backup_manager.restore_backup(
            str(backup_path), restore_secrets=restore_secrets
        )
        if "file" in request.files and backup_path.exists():
            backup_path.unlink()
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Restore failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/backup/delete/<filename>", methods=["DELETE"])
@login_required
def delete_backup(filename):
    result = backup_manager.delete_backup(filename)
    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route("/api/database/delete", methods=["POST"])
@login_required
def delete_database():
    try:
        metrics_url = config.data.get("metrics", {}).get(
            "url", "http://victoriametrics:8428/write"
        )
        base_url = metrics_url.replace("/write", "")
        delete_url = f"{base_url}/api/v1/admin/tsdb/delete_series"
        response = requests.post(delete_url, params={"match[]": '{__name__!=""}'})
        if response.status_code == 204 or response.status_code == 200:
            return jsonify(
                {"success": True, "message": "Datenbank erfolgreich bereinigt"}
            )
        else:
            return jsonify({"error": f"Fehler beim Löschen: {response.text}"}), 500
    except Exception as e:
        logger.error(f"Failed to delete database: {e}")
        return jsonify({"error": str(e)}), 500


def set_metrics_writer(writer):
    global metrics_writer_instance
    metrics_writer_instance = writer


def run_web(modbus_client, scheduler):
    global modbus_client_instance, scheduler_instance
    modbus_client_instance = modbus_client
    scheduler_instance = scheduler

    if config.get("web.enabled"):
        host = config.get("web.host", "0.0.0.0")
        port = config.get("web.port", 5000)
        try:
            logger.info(f"Starting production web server (Waitress) on {host}:{port}")
            serve(
                app,
                host=host,
                port=port,
                threads=4,
                channel_timeout=60,
                url_scheme="http",
            )
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
