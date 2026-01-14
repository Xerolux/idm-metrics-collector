from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort, send_from_directory, send_file
from waitress import serve
from datetime import datetime
from .technician_auth import calculate_codes
from .config import config
from .sensor_addresses import SensorFeatures
from .log_handler import memory_handler
from .backup import backup_manager, BACKUP_DIR
from .mqtt import mqtt_publisher
from .signal_notifications import send_signal_message
from .update_manager import check_for_update, perform_update as run_update, get_current_version, can_run_updates
from .alerts import alert_manager
from shutil import which
import threading
import logging
import functools
import os
import sys
import signal
import ipaddress
import time
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.get_flask_secret_key()
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Rate limiting storage
login_attempts = {}

# Shared state
current_data = {}
data_lock = threading.Lock()
modbus_client_instance = None
scheduler_instance = None
metrics_writer_instance = None

def update_current_data(data):
    with data_lock:
        current_data.clear()
        current_data.update(data)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                 return jsonify({"error": "Nicht autorisiert"}), 401
            # For non-API routes (if any left), we could redirect, but we are SPA now
            # so usually we just return 401 and let frontend handle it.
            return jsonify({"error": "Nicht autorisiert"}), 401
        return view(**kwargs)
    return wrapped_view

@app.before_request
def check_setup():
    # If not setup, only allow setup related calls or static files
    # Frontend will check /api/health to see if setup is needed
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

    # Check blacklist first
    for block in blacklist:
        try:
            if ip in ipaddress.ip_network(block, strict=False):
                logger.warning(f"Blocked IP {client_ip} (matched blacklist {block})")
                abort(403)
        except ValueError:
            logger.error(f"Invalid blacklist entry: {block}")

    # Check whitelist if it exists and is not empty
    if whitelist:
        allowed = False
        for allow in whitelist:
            try:
                if ip in ipaddress.ip_network(allow, strict=False):
                    allowed = True
                    break
            except ValueError:
                logger.error(f"Invalid whitelist entry: {allow}")

        if not allowed:
            logger.warning(f"Blocked IP {client_ip} (not in whitelist)")
            abort(403)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.context_processor
def inject_config():
    # Only inject safe config data
    safe_config = config.data.copy()
    return dict(config=safe_config)

@app.route('/api/setup', methods=['POST'])
def setup():
    if config.is_setup():
        return jsonify({"error": "Bereits eingerichtet"}), 400

    data = request.get_json()
    try:
        # Save IDM
        config.data['idm']['host'] = data.get('idm_host')
        config.data['idm']['port'] = int(data.get('idm_port'))

        # Save Circuits and Zones
        if 'circuits' in data:
            config.data['idm']['circuits'] = data['circuits']
        if 'zones' in data:
            config.data['idm']['zones'] = data['zones']

        # Save Metrics
        if 'metrics' not in config.data:
            config.data['metrics'] = {}
        config.data['metrics']['url'] = data.get('metrics_url')

        # Save Admin Password
        password = data.get('password')
        if not password or len(password) < 6:
            return jsonify({"error": "Passwort muss mindestens 6 Zeichen lang sein"}), 400

        config.set_admin_password(password)

        # Enable features
        config.data['web']['write_enabled'] = True
        config.data['setup_completed'] = True

        config.save()

        return jsonify({"success": True, "message": "Einrichtung abgeschlossen. Bitte Dienst neu starten."})

    except Exception as e:
        logger.error(f"Setup error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login', methods=['POST'])
def login():
    # Rate limiting
    ip = request.remote_addr
    now = time.time()

    # Clean old attempts (older than 5 minutes)
    if ip in login_attempts:
        login_attempts[ip] = [t for t in login_attempts[ip] if now - t < 300]
        if len(login_attempts[ip]) >= 5:
            logger.warning(f"Login rate limit exceeded for IP {ip}")
            return jsonify({"success": False, "message": "Zu viele Fehlversuche. Versuch es später noch einmal."}), 429

    data = request.get_json()
    password = data.get('password')

    if config.check_admin_password(password):
        # Reset attempts on success
        if ip in login_attempts:
            del login_attempts[ip]

        session['logged_in'] = True
        session.permanent = True # Use permanent session (defaults to 31 days)
        return jsonify({"success": True})
    else:
        # Record failed attempt
        if ip not in login_attempts:
            login_attempts[ip] = []
        login_attempts[ip].append(now)

        logger.warning(f"Failed login attempt from {ip}")
        return jsonify({"success": False, "message": "Ungültiges Passwort"}), 401

@app.route('/api/auth/check')
def check_auth():
    return jsonify({"authenticated": session.get('logged_in', False)})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return jsonify({"success": True})

@app.route('/api/data')
def get_data():
    with data_lock:
        return jsonify(current_data)


@app.route('/api/health')
def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return jsonify({
        "status": "healthy",
        "setup_completed": config.is_setup(),
        "client_ip": request.remote_addr
    }), 200


@app.route('/api/status')
def status_check():
    """Detailed status endpoint with Metrics connection info."""
    metrics_status = None
    if metrics_writer_instance:
        metrics_status = metrics_writer_instance.get_status()

    mqtt_status = mqtt_publisher.get_status() if mqtt_publisher else None

    return jsonify({
        "status": "running",
        "setup_completed": config.is_setup(),
        "metrics": metrics_status,
        "mqtt": mqtt_status,
        "modbus_connected": modbus_client_instance is not None,
        "scheduler_running": scheduler_instance is not None and config.get("web.write_enabled")
    })

@app.route('/api/logs')
@login_required
def logs_page():
    logs = memory_handler.get_logs()
    logs.reverse()
    return jsonify(logs)

@app.route('/api/tools/technician-code', methods=['GET'])
@login_required
def get_technician_code():
    try:
        codes = calculate_codes()
        return jsonify(codes)
    except Exception as e:
        logger.error(f"Error generating codes: {e}")
        return jsonify({"error": "Fehler beim Generieren der Codes"}), 500

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def config_page():
    if request.method == 'GET':
        # Return safe config
        safe_config = config.data.copy()

        # Add metadata about token synchronization (Not used for VM currently)
        response = safe_config
        response['_meta'] = {
            "token_synced": True,
            "token_source": "environment" if os.environ.get("METRICS_URL") else "database"
        }
        return jsonify(response)

    if request.method == 'POST':
        data = request.get_json()
        try:
            # IDM Host
            if 'idm_host' in data:
                config.data['idm']['host'] = data['idm_host']

            # IDM Modbus Port
            if 'idm_port' in data:
                try:
                    port = int(data['idm_port'])
                    if 1 <= port <= 65535:
                        config.data['idm']['port'] = port
                    else:
                        return jsonify({"error": "Port muss zwischen 1 und 65535 sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültige Portnummer"}), 400

            # Circuits and Zones
            if 'circuits' in data:
                 config.data['idm']['circuits'] = data['circuits']
            if 'zones' in data:
                 config.data['idm']['zones'] = data['zones']

            # Write Enabled
            if 'write_enabled' in data:
                config.data['web']['write_enabled'] = bool(data['write_enabled'])

            # Logging Interval
            if 'logging_interval' in data:
                try:
                    interval = int(data['logging_interval'])
                    if 1 <= interval <= 3600:  # 1 second to 1 hour
                        config.data['logging']['interval'] = interval
                    else:
                        return jsonify({"error": "Intervall muss zwischen 1 und 3600 Sekunden sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger Intervallwert"}), 400

            # Realtime Mode
            if 'realtime_mode' in data:
                config.data['logging']['realtime_mode'] = bool(data['realtime_mode'])

            # Metrics URL
            if 'metrics_url' in data:
                 config.data['metrics']['url'] = data['metrics_url']

            # MQTT Settings
            if 'mqtt_enabled' in data:
                config.data['mqtt']['enabled'] = bool(data['mqtt_enabled'])

            if 'mqtt_broker' in data:
                config.data['mqtt']['broker'] = data['mqtt_broker']

            if 'mqtt_port' in data:
                try:
                    port = int(data['mqtt_port'])
                    if 1 <= port <= 65535:
                        config.data['mqtt']['port'] = port
                    else:
                        return jsonify({"error": "MQTT Port muss zwischen 1 und 65535 sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültige MQTT Portnummer"}), 400

            if 'mqtt_username' in data:
                config.data['mqtt']['username'] = data['mqtt_username']

            if 'mqtt_password' in data and data['mqtt_password']:
                # Only update password if provided (not empty)
                config.data['mqtt']['password'] = data['mqtt_password']

            if 'mqtt_use_tls' in data:
                config.data['mqtt']['use_tls'] = bool(data['mqtt_use_tls'])

            if 'mqtt_topic_prefix' in data:
                config.data['mqtt']['topic_prefix'] = data['mqtt_topic_prefix']

            if 'mqtt_ha_discovery_enabled' in data:
                 config.data['mqtt']['ha_discovery_enabled'] = bool(data['mqtt_ha_discovery_enabled'])

            if 'mqtt_ha_discovery_prefix' in data:
                 config.data['mqtt']['ha_discovery_prefix'] = data['mqtt_ha_discovery_prefix']

            if 'mqtt_publish_interval' in data:
                try:
                    interval = int(data['mqtt_publish_interval'])
                    if 1 <= interval <= 3600:
                        config.data['mqtt']['publish_interval'] = interval
                    else:
                        return jsonify({"error": "MQTT Publish-Intervall muss zwischen 1 und 3600 Sekunden sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültiges MQTT Publish-Intervall"}), 400

            if 'mqtt_qos' in data:
                try:
                    qos = int(data['mqtt_qos'])
                    if qos in [0, 1, 2]:
                        config.data['mqtt']['qos'] = qos
                    else:
                        return jsonify({"error": "MQTT QoS muss 0, 1, oder 2 sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger MQTT QoS Wert"}), 400

            # Signal Settings
            if 'signal_enabled' in data:
                config.data['signal']['enabled'] = bool(data['signal_enabled'])

            if 'signal_sender' in data:
                config.data['signal']['sender'] = data['signal_sender']

            if 'signal_cli_path' in data:
                config.data['signal']['cli_path'] = data['signal_cli_path']

            if 'signal_recipients' in data:
                recipients = data['signal_recipients']
                if isinstance(recipients, str):
                    recipients = [x.strip() for x in recipients.split('\n') if x.strip()]
                config.data['signal']['recipients'] = recipients

            # AI Settings
            if 'ai_enabled' in data:
                config.data['ai']['enabled'] = bool(data['ai_enabled'])
            if 'ai_sensitivity' in data:
                try:
                    sens = float(data['ai_sensitivity'])
                    if 1.0 <= sens <= 10.0:
                         config.data['ai']['sensitivity'] = sens
                    else:
                         return jsonify({"error": "AI Sensitivität muss zwischen 1.0 und 10.0 sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger Wert für AI Sensitivität"}), 400

            # Auto Update Settings
            if 'updates_enabled' in data:
                config.data['updates']['enabled'] = bool(data['updates_enabled'])

            if 'updates_interval_hours' in data:
                try:
                    interval = int(data['updates_interval_hours'])
                    if 1 <= interval <= 168:
                        config.data['updates']['interval_hours'] = interval
                    else:
                        return jsonify({"error": "Update-Intervall muss zwischen 1 und 168 Stunden sein"}), 400
                except ValueError:
                    return jsonify({"error": "Ungültiger Update-Intervallwert"}), 400

            if 'updates_mode' in data:
                if data['updates_mode'] not in ['check', 'apply']:
                    return jsonify({"error": "Update-Modus muss 'check' oder 'apply' sein"}), 400
                config.data['updates']['mode'] = data['updates_mode']

            if 'updates_target' in data:
                if data['updates_target'] not in ['all', 'major', 'minor', 'patch']:
                    return jsonify({"error": "Update-Ziel muss all, major, minor oder patch sein"}), 400
                config.data['updates']['target'] = data['updates_target']

            # Network Security Settings
            if 'network_security_enabled' in data:
                config.data['network_security']['enabled'] = bool(data['network_security_enabled'])

            if 'network_security_whitelist' in data:
                # Validate IP addresses/networks
                whitelist = data['network_security_whitelist']
                if isinstance(whitelist, str):
                    whitelist = [x.strip() for x in whitelist.split('\n') if x.strip()]

                # Validate each entry
                validated_whitelist = []
                for entry in whitelist:
                    try:
                        ipaddress.ip_network(entry, strict=False)
                        validated_whitelist.append(entry)
                    except ValueError:
                        return jsonify({"error": f"Ungültiger Whitelist-Eintrag: {entry}"}), 400

                config.data['network_security']['whitelist'] = validated_whitelist

            if 'network_security_blacklist' in data:
                # Validate IP addresses/networks
                blacklist = data['network_security_blacklist']
                if isinstance(blacklist, str):
                    blacklist = [x.strip() for x in blacklist.split('\n') if x.strip()]

                # Validate each entry
                validated_whitelist = []
                for entry in blacklist:
                    try:
                        ipaddress.ip_network(entry, strict=False)
                        validated_blacklist.append(entry)
                    except ValueError:
                        return jsonify({"error": f"Ungültiger Blacklist-Eintrag: {entry}"}), 400

                config.data['network_security']['blacklist'] = validated_blacklist

            # Handle password change
            new_pass = data.get('new_password')
            if new_pass:
                if len(new_pass) < 6:
                    return jsonify({"error": "Neues Passwort zu kurz"}), 400
                config.set_admin_password(new_pass)

            # Save config
            config.save()
            return jsonify({"success": True, "message": "Konfiguration gespeichert. Neustart erforderlich."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/restart', methods=['POST'])
@login_required
def restart_service():
    """Restart the service by sending SIGTERM to the main process."""
    logger.info("Service restart requested by user")

    # Use threading to delay the restart so the response can be sent
    def delayed_restart():
        import time
        time.sleep(1)  # Give time for the response to be sent
        logger.info("Initiating restart...")
        # Send SIGTERM to main process (PID 1 in container)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=delayed_restart, daemon=True).start()

    return jsonify({"success": True, "message": "Starte Dienst neu..."})

@app.route('/api/version', methods=['GET'])
def get_version():
    """Get current application version from git or package."""
    try:
        return jsonify({"version": get_current_version()})
    except Exception as e:
        logger.error(f"Error getting version: {e}")
        return jsonify({"version": "unknown"})

@app.route('/api/check-update', methods=['GET'])
@login_required
def check_update():
    """Check for updates from GitHub."""
    try:
        return jsonify(check_for_update())
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/perform-update', methods=['POST'])
@login_required
def perform_update():
    """Perform system update via git pull and docker compose restart."""
    try:
        logger.info("Update requested by user")

        # Run update in background thread
        def do_update():
            try:
                time.sleep(2)  # Give time for response to be sent

                if not can_run_updates():
                    logger.warning("Update skipped: repo path not found.")
                    return
                run_update()

            except Exception as e:
                logger.error(f"Update failed: {e}")

        # Start update in background
        threading.Thread(target=do_update, daemon=True).start()

        return jsonify({"success": True, "message": "Update gestartet"})

    except Exception as e:
        logger.error(f"Error starting update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/signal/test', methods=['POST'])
@login_required
def signal_test():
    data = request.get_json() or {}
    message = data.get('message', 'Testnachricht vom IDM Metrics Collector')
    try:
        send_signal_message(message)
        return jsonify({"success": True, "message": "Signal-Testnachricht gesendet"})
    except Exception as e:
        logger.error(f"Signal test failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/signal/status', methods=['GET'])
@login_required
def signal_status():
    signal_config = config.data.get("signal", {})
    recipients = signal_config.get("recipients", []) or []
    cli_path = signal_config.get("cli_path", "signal-cli")
    return jsonify({
        "enabled": signal_config.get("enabled", False),
        "sender_set": bool(signal_config.get("sender")),
        "recipients_count": len(recipients),
        "cli_path": cli_path,
        "cli_available": which(cli_path) is not None
    })

def validate_write(sensor_name, value):
    """Validates the value against sensor constraints."""
    if not modbus_client_instance:
        return False, "Modbus-Client nicht verfügbar"

    sensor = modbus_client_instance.sensors.get(sensor_name) or modbus_client_instance.binary_sensors.get(sensor_name)
    if not sensor:
        return False, "Sensor nicht gefunden"

    # Enum validation
    if hasattr(sensor, "enum") and sensor.enum:
        try:
            if str(value).isdigit():
                val_int = int(value)
                if val_int not in [m.value for m in sensor.enum]:
                     return False, f"Wert {value} ist keine gültige Option"
            else:
                 # Try key lookup
                 if value not in sensor.enum.__members__:
                      return False, f"Option {value} nicht gefunden"
        except (ValueError, KeyError, AttributeError, TypeError) as e:
             logger.debug(f"Enum validation failed for {sensor_name}: {e}")
             return False, "Ungültiger Enum-Wert"

    # Range validation
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

@app.route('/api/control', methods=['GET', 'POST'])
@login_required
def control_page():
    if not config.get("web.write_enabled"):
        return jsonify({"error": "Schreibzugriff deaktiviert"}), 403

    if request.method == 'POST':
        data = request.get_json()
        sensor_name = data.get('sensor')
        value = data.get('value')

        valid, msg = validate_write(sensor_name, value)
        if not valid:
             return jsonify({"error": msg}), 400

        try:
            if modbus_client_instance:
                modbus_client_instance.write_sensor(sensor_name, value)
                return jsonify({"success": True, "message": f"{value} erfolgreich auf {sensor_name} geschrieben"})
            else:
                 return jsonify({"error": "Modbus-Client nicht verfügbar"}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Filter writable sensors
    writable_sensors = []
    if modbus_client_instance:
        all_sensors = {**modbus_client_instance.sensors, **modbus_client_instance.binary_sensors}
        for name, sensor in all_sensors.items():
            if sensor.supported_features != SensorFeatures.NONE:
                # Serialize sensor info for frontend
                s_info = {
                    "name": sensor.name,
                    "unit": getattr(sensor, "unit", ""),
                    "description": getattr(sensor, "description", ""),
                    "features": sensor.supported_features.name if hasattr(sensor.supported_features, "name") else sensor.supported_features,
                    "min": getattr(sensor, "min_value", None),
                    "max": getattr(sensor, "max_value", None),
                    "enum": [{"name": m.name, "value": m.value} for m in sensor.enum] if hasattr(sensor, "enum") and sensor.enum else None,
                    "eeprom_sensitive": getattr(sensor, "eeprom_sensitive", False),
                    "cyclic_change_required": getattr(sensor, "cyclic_change_required", False),
                }
                writable_sensors.append(s_info)

    # Sort by name
    writable_sensors.sort(key=lambda s: s['name'])

    return jsonify(writable_sensors)

@app.route('/api/schedule', methods=['GET', 'POST'])
@login_required
def schedule_page():
    if not config.get("web.write_enabled"):
         return jsonify({"error": "Schreibzugriff deaktiviert"}), 403

    if not scheduler_instance:
        return jsonify({"error": "Scheduler nicht verfügbar"}), 503

    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')

        if action == 'add':
            sensor = data.get('sensor')
            value = data.get('value')

            # Validate input for schedule too
            valid, msg = validate_write(sensor, value)
            if not valid:
                 return jsonify({"error": msg}), 400
            else:
                job = {
                    'sensor': sensor,
                    'value': value,
                    'time': data.get('time'),
                    'days': data.get('days', [])
                }
                if scheduler_instance:
                    scheduler_instance.add_job(job)
                    return jsonify({"success": True, "message": "Zeitplan hinzugefügt"})

        elif action == 'delete':
            job_id = data.get('job_id')
            if scheduler_instance:
                scheduler_instance.delete_job(job_id)
                return jsonify({"success": True, "message": "Zeitplan gelöscht"})

        elif action == 'toggle':
             job_id = data.get('job_id')
             current_state = data.get('current_state')
             if scheduler_instance:
                  scheduler_instance.update_job(job_id, {'enabled': not current_state})
                  state_text = "pausiert" if current_state else "fortgesetzt"
                  return jsonify({"success": True, "message": f"Zeitplan {state_text}"})

        elif action == 'run_now':
             job_id = data.get('job_id')
             if scheduler_instance:
                 job = next((j for j in scheduler_instance.jobs if j['id'] == job_id), None)
                 if job and modbus_client_instance:
                     try:
                         modbus_client_instance.write_sensor(job['sensor'], job['value'])
                         return jsonify({"success": True, "message": f"Ausgeführt: {job['sensor']} = {job['value']}"})
                     except Exception as e:
                         return jsonify({"error": str(e)}), 500
                 else:
                     return jsonify({"error": "Job nicht gefunden oder System nicht verfügbar"}), 404

        return jsonify({"error": "Ungültige Aktion"}), 400

    jobs = scheduler_instance.jobs if scheduler_instance else []

    # Get sensors for dropdown
    writable_sensors = []
    if modbus_client_instance:
        try:
            all_sensors = {**modbus_client_instance.sensors, **modbus_client_instance.binary_sensors}
            for name, sensor in all_sensors.items():
                if sensor.supported_features != SensorFeatures.NONE:
                    s_info = {
                        "name": sensor.name,
                        "unit": getattr(sensor, "unit", ""),
                        "enum": [{"name": m.name, "value": m.value} for m in sensor.enum] if hasattr(sensor, "enum") and sensor.enum else None,
                        "eeprom_sensitive": getattr(sensor, "eeprom_sensitive", False),
                        "cyclic_change_required": getattr(sensor, "cyclic_change_required", False),
                    }
                    writable_sensors.append(s_info)
        except Exception as e:
            logger.error(f"Error loading sensors for schedule: {e}")

    writable_sensors.sort(key=lambda s: s['name'])

    return jsonify({"jobs": jobs, "sensors": writable_sensors})

@app.route('/api/alerts', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def alerts_api():
    if request.method == 'GET':
        return jsonify(alert_manager.alerts)

    if request.method == 'POST':
        data = request.get_json()

        # Validation
        if not data.get('name'):
            return jsonify({"error": "Name fehlt"}), 400
        if not data.get('type') in ['threshold', 'status']:
            return jsonify({"error": "Ungültiger Typ"}), 400
        if data['type'] == 'threshold' and not data.get('sensor'):
            return jsonify({"error": "Sensor fehlt"}), 400

        try:
            alert = alert_manager.add_alert(data)
            return jsonify({"success": True, "alert": alert})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == 'PUT':
        data = request.get_json()
        alert_id = data.get('id')
        if not alert_id:
             return jsonify({"error": "ID fehlt"}), 400

        try:
            alert_manager.update_alert(alert_id, data)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == 'DELETE':
        alert_id = request.args.get('id')
        if not alert_id:
             return jsonify({"error": "ID fehlt"}), 400

        try:
            alert_manager.delete_alert(alert_id)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Catch-all route for Vue SPA client-side routing
# This must be the last route to avoid catching API routes
@app.route('/<path:path>')
def catch_all(path):
    # Serve index.html for all non-API routes to support Vue Router
    return send_from_directory(app.static_folder, 'index.html')


# ============================================================================
# BACKUP & RESTORE API
# ============================================================================

@app.route('/api/backup/create', methods=['POST'])
@login_required
def create_backup():
    """Create a new backup."""
    result = backup_manager.create_backup()

    if result.get('success'):
        # Clean up old backups (keep last 10)
        backup_manager.cleanup_old_backups(keep_count=10)
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/api/backup/list', methods=['GET'])
@login_required
def list_backups():
    """List all available backups."""
    backups = backup_manager.list_backups()
    return jsonify({"backups": backups}), 200


@app.route('/api/backup/download/<filename>', methods=['GET'])
@login_required
def download_backup(filename):
    """Download a backup file."""
    # Security check
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
            mimetype='application/zip'
        )
    except Exception as e:
        logger.error(f"Failed to send backup file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/backup/restore', methods=['POST'])
@login_required
def restore_backup():
    """Restore from a backup file."""
    # Check if file was uploaded
    if 'file' not in request.files:
        data = request.get_json() or {}
        filename = data.get('filename')

        if not filename:
            return jsonify({"error": "Keine Backup-Datei angegeben"}), 400

        if ".." in filename or "/" in filename or "\\" in filename:
            return jsonify({"error": "Ungültiger Dateiname"}), 400

        # Restore from existing backup
        backup_path = Path(BACKUP_DIR) / filename
    else:
        # Handle uploaded file
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Keine Datei ausgewählt"}), 400

        # Save uploaded file temporarily
        # Ensure filename is safe
        safe_filename = file.filename
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
             return jsonify({"error": "Ungültiger Dateiname"}), 400

        temp_path = Path(BACKUP_DIR) / f"temp_{safe_filename}"
        file.save(temp_path)
        backup_path = temp_path

    try:
        restore_secrets = request.form.get('restore_secrets', 'false').lower() == 'true'
        result = backup_manager.restore_backup(str(backup_path), restore_secrets=restore_secrets)

        # Clean up temp file if uploaded
        if 'file' in request.files and backup_path.exists():
            backup_path.unlink()

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Restore failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/backup/delete/<filename>', methods=['DELETE'])
@login_required
def delete_backup(filename):
    """Delete a backup file."""
    result = backup_manager.delete_backup(filename)

    if result.get('success'):
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/api/database/delete', methods=['POST'])
@login_required
def delete_database():
    """Delete all data from the database."""
    # Not implemented for VictoriaMetrics via this API yet
    # Could send a delete request to VM
    return jsonify({"error": "Nicht implementiert für VictoriaMetrics"}), 501


def set_metrics_writer(writer):
    """Set the Metrics writer instance for status reporting."""
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
                threads=4,  # Use 4 threads for better concurrency
                channel_timeout=60,  # Timeout for idle connections
                url_scheme='http'  # Explicitly set URL scheme
            )
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
