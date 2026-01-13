from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort, send_from_directory, send_file
from waitress import serve
from datetime import datetime
from .technician_auth import calculate_codes
from .config import config
from .sensor_addresses import SensorFeatures
from .log_handler import memory_handler
from .backup import backup_manager
from .mqtt import mqtt_publisher
import threading
import logging
import functools
import os
import sys
import signal
import ipaddress
import time
import subprocess
import requests
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
influx_writer_instance = None

def update_current_data(data):
    with data_lock:
        current_data.clear()
        current_data.update(data)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                 return jsonify({"error": "Unauthorized"}), 401
            # For non-API routes (if any left), we could redirect, but we are SPA now
            # so usually we just return 401 and let frontend handle it.
            return jsonify({"error": "Unauthorized"}), 401
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
    if 'influx' in safe_config:
        safe_config['influx'] = safe_config['influx'].copy()
        if 'token' in safe_config['influx']:
            del safe_config['influx']['token']
        if 'password' in safe_config['influx']:
            del safe_config['influx']['password']
    return dict(config=safe_config)

@app.route('/api/setup', methods=['POST'])
def setup():
    if config.is_setup():
        return jsonify({"error": "Already setup"}), 400

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

        # Save Influx
        config.data['influx']['url'] = data.get('influx_url')
        config.data['influx']['database'] = data.get('influx_database')
        if data.get('influx_token'):
            config.data['influx']['token'] = data.get('influx_token')

        # Save Admin Password
        password = data.get('password')
        if not password or len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        config.set_admin_password(password)

        # Enable features
        config.data['web']['write_enabled'] = True
        config.data['setup_completed'] = True

        config.save()

        return jsonify({"success": True, "message": "Setup complete. Please restart service."})

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
            return jsonify({"success": False, "message": "Too many failed attempts. Try again later."}), 429

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
        return jsonify({"success": False, "message": "Invalid password"}), 401

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
    """Detailed status endpoint with InfluxDB connection info."""
    influx_status = None
    if influx_writer_instance:
        influx_status = influx_writer_instance.get_status()

    mqtt_status = mqtt_publisher.get_status() if mqtt_publisher else None

    return jsonify({
        "status": "running",
        "setup_completed": config.is_setup(),
        "influx": influx_status,
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
        return jsonify({"error": "Failed to generate codes"}), 500

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def config_page():
    if request.method == 'GET':
        # Return safe config
        safe_config = config.data.copy()
        token_synced = True
        token_source = "database"

        if 'influx' in safe_config:
            safe_config['influx'] = safe_config['influx'].copy()

            # Check for token synchronization
            env_token = os.environ.get("INFLUX_TOKEN") or os.environ.get("INFLUXDB_TOKEN")
            current_token = config.data.get("influx", {}).get("token")

            if env_token:
                token_source = "environment"
                if env_token != current_token:
                    token_synced = False

            if 'token' in safe_config['influx']:
                 safe_config['influx']['token'] = '******' # Don't send token
            if 'password' in safe_config['influx']:
                 safe_config['influx']['password'] = '******'

        # Add metadata about token synchronization
        response = safe_config
        response['_meta'] = {
            "token_synced": token_synced,
            "token_source": token_source
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
                        return jsonify({"error": "Port must be between 1 and 65535"}), 400
                except ValueError:
                    return jsonify({"error": "Invalid port number"}), 400

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
                        return jsonify({"error": "Interval must be between 1 and 3600 seconds"}), 400
                except ValueError:
                    return jsonify({"error": "Invalid interval value"}), 400

            # Realtime Mode
            if 'realtime_mode' in data:
                config.data['logging']['realtime_mode'] = bool(data['realtime_mode'])

            # InfluxDB URL
            if 'influx_url' in data:
                 config.data['influx']['url'] = data['influx_url']
            if 'influx_database' in data:
                 config.data['influx']['database'] = data['influx_database']
            if 'influx_token' in data and data['influx_token']:
                 config.data['influx']['token'] = data['influx_token']

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
                        return jsonify({"error": "MQTT port must be between 1 and 65535"}), 400
                except ValueError:
                    return jsonify({"error": "Invalid MQTT port number"}), 400

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
                        return jsonify({"error": "MQTT publish interval must be between 1 and 3600 seconds"}), 400
                except ValueError:
                    return jsonify({"error": "Invalid MQTT publish interval"}), 400

            if 'mqtt_qos' in data:
                try:
                    qos = int(data['mqtt_qos'])
                    if qos in [0, 1, 2]:
                        config.data['mqtt']['qos'] = qos
                    else:
                        return jsonify({"error": "MQTT QoS must be 0, 1, or 2"}), 400
                except ValueError:
                    return jsonify({"error": "Invalid MQTT QoS value"}), 400

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
                        return jsonify({"error": f"Invalid whitelist entry: {entry}"}), 400

                config.data['network_security']['whitelist'] = validated_whitelist

            if 'network_security_blacklist' in data:
                # Validate IP addresses/networks
                blacklist = data['network_security_blacklist']
                if isinstance(blacklist, str):
                    blacklist = [x.strip() for x in blacklist.split('\n') if x.strip()]

                # Validate each entry
                validated_blacklist = []
                for entry in blacklist:
                    try:
                        ipaddress.ip_network(entry, strict=False)
                        validated_blacklist.append(entry)
                    except ValueError:
                        return jsonify({"error": f"Invalid blacklist entry: {entry}"}), 400

                config.data['network_security']['blacklist'] = validated_blacklist

            # Handle password change
            new_pass = data.get('new_password')
            if new_pass:
                if len(new_pass) < 6:
                    return jsonify({"error": "New password too short"}), 400
                config.set_admin_password(new_pass)

            # Save config
            config.save()
            return jsonify({"success": True, "message": "Configuration saved. Restart required."})
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

    return jsonify({"success": True, "message": "Restarting service..."})

@app.route('/api/version', methods=['GET'])
def get_version():
    """Get current application version from git or package."""
    try:
        # Try to get version from git
        result = subprocess.run(
            ['git', 'describe', '--tags', '--always'],
            capture_output=True,
            text=True,
            cwd='/app',
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
        else:
            # Fallback to reading from a version file
            version_file = Path('/app/VERSION')
            if version_file.exists():
                version = version_file.read_text().strip()
            else:
                version = 'v0.5.0'  # Default version

        return jsonify({"version": version})
    except Exception as e:
        logger.error(f"Error getting version: {e}")
        return jsonify({"version": "unknown"})

@app.route('/api/check-update', methods=['GET'])
@login_required
def check_update():
    """Check for updates from GitHub."""
    try:
        # Get current version
        current_version = get_version().json.get('version', 'unknown')

        # Check GitHub for latest release
        github_api = "https://api.github.com/repos/Xerolux/idm-metrics-collector/releases/latest"
        response = requests.get(github_api, timeout=10)

        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release.get('tag_name', '')
            release_date = latest_release.get('published_at', '')
            release_notes = latest_release.get('body', '')[:200]  # First 200 chars

            # Simple version comparison (assumes semantic versioning)
            update_available = latest_version != current_version and latest_version > current_version

            return jsonify({
                "update_available": update_available,
                "current_version": current_version,
                "latest_version": latest_version,
                "release_date": release_date,
                "release_notes": release_notes
            })
        else:
            return jsonify({"error": "Failed to check for updates"}), 500

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

                # Change to app directory
                os.chdir('/opt/idm-metrics-collector')

                # Git pull
                logger.info("Pulling latest changes from git...")
                result = subprocess.run(
                    ['git', 'pull', 'origin', 'main'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    logger.error(f"Git pull failed: {result.stderr}")
                    return

                # Docker compose down and up
                logger.info("Restarting Docker Compose stack...")

                # Try docker compose (v2)
                compose_cmd = ['docker', 'compose']
                check_result = subprocess.run(
                    compose_cmd + ['version'],
                    capture_output=True,
                    timeout=5
                )

                if check_result.returncode != 0:
                    # Fallback to docker-compose (v1)
                    compose_cmd = ['docker-compose']

                # Pull images
                subprocess.run(
                    compose_cmd + ['pull'],
                    capture_output=True,
                    timeout=300
                )

                # Restart
                subprocess.run(
                    compose_cmd + ['down'],
                    capture_output=True,
                    timeout=60
                )

                subprocess.run(
                    compose_cmd + ['up', '-d'],
                    capture_output=True,
                    timeout=120
                )

                logger.info("Update completed successfully")

            except Exception as e:
                logger.error(f"Update failed: {e}")

        # Start update in background
        threading.Thread(target=do_update, daemon=True).start()

        return jsonify({"success": True, "message": "Update started"})

    except Exception as e:
        logger.error(f"Error starting update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def validate_write(sensor_name, value):
    """Validates the value against sensor constraints."""
    if not modbus_client_instance:
        return False, "Modbus client not available"

    sensor = modbus_client_instance.sensors.get(sensor_name) or modbus_client_instance.binary_sensors.get(sensor_name)
    if not sensor:
        return False, "Sensor not found"

    # Enum validation
    if hasattr(sensor, "enum") and sensor.enum:
        try:
            if str(value).isdigit():
                val_int = int(value)
                if val_int not in [m.value for m in sensor.enum]:
                     return False, f"Value {value} is not a valid option"
            else:
                 # Try key lookup
                 if value not in sensor.enum.__members__:
                      return False, f"Option {value} not found"
        except (ValueError, KeyError, AttributeError, TypeError) as e:
             logger.debug(f"Enum validation failed for {sensor_name}: {e}")
             return False, "Invalid enum value"

    # Range validation
    elif hasattr(sensor, "min_value") and hasattr(sensor, "max_value"):
        try:
            val_float = float(value)
            if sensor.min_value is not None and val_float < sensor.min_value:
                return False, f"Value {value} below minimum ({sensor.min_value})"
            if sensor.max_value is not None and val_float > sensor.max_value:
                return False, f"Value {value} above maximum ({sensor.max_value})"
        except ValueError:
            return False, "Invalid number"

    return True, None

@app.route('/api/control', methods=['GET', 'POST'])
@login_required
def control_page():
    if not config.get("web.write_enabled"):
        return jsonify({"error": "Write capabilities disabled"}), 403

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
                return jsonify({"success": True, "message": f"Successfully wrote {value} to {sensor_name}"})
            else:
                 return jsonify({"error": "Modbus client not available"}), 503
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
         return jsonify({"error": "Write capabilities disabled"}), 403

    if not scheduler_instance:
        return jsonify({"error": "Scheduler not available"}), 503

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
                    return jsonify({"success": True, "message": "Schedule added"})

        elif action == 'delete':
            job_id = data.get('job_id')
            if scheduler_instance:
                scheduler_instance.delete_job(job_id)
                return jsonify({"success": True, "message": "Schedule deleted"})

        elif action == 'toggle':
             job_id = data.get('job_id')
             current_state = data.get('current_state')
             if scheduler_instance:
                  scheduler_instance.update_job(job_id, {'enabled': not current_state})
                  state_text = "paused" if current_state else "resumed"
                  return jsonify({"success": True, "message": f"Schedule {state_text}"})

        elif action == 'run_now':
             job_id = data.get('job_id')
             if scheduler_instance:
                 job = next((j for j in scheduler_instance.jobs if j['id'] == job_id), None)
                 if job and modbus_client_instance:
                     try:
                         modbus_client_instance.write_sensor(job['sensor'], job['value'])
                         return jsonify({"success": True, "message": f"Executed: {job['sensor']} = {job['value']}"})
                     except Exception as e:
                         return jsonify({"error": str(e)}), 500
                 else:
                     return jsonify({"error": "Job not found or system unavailable"}), 404

        return jsonify({"error": "Invalid action"}), 400

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
    data = request.get_json() or {}
    include_influx = data.get('include_influx_config', True)

    result = backup_manager.create_backup(include_influx_config=include_influx)

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
        return jsonify({"error": "Invalid filename"}), 400

    backup_path = Path(backup_manager.BACKUP_DIR) / filename

    if not backup_path.exists():
        return jsonify({"error": "Backup not found"}), 404

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
            return jsonify({"error": "No backup file specified"}), 400

        # Restore from existing backup
        backup_path = Path(backup_manager.BACKUP_DIR) / filename
    else:
        # Handle uploaded file
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save uploaded file temporarily
        temp_path = Path(backup_manager.BACKUP_DIR) / f"temp_{file.filename}"
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


@app.route('/api/backup/export/influx', methods=['GET'])
@login_required
def export_influx_config():
    """Export InfluxDB configuration as JSON."""
    result = backup_manager.export_influxdb_config()

    if result.get('success'):
        return jsonify(result['data']), 200
    else:
        return jsonify(result), 500


@app.route('/api/database/delete', methods=['POST'])
@login_required
def delete_database():
    """Delete all data from the database."""
    if not influx_writer_instance:
        return jsonify({"error": "InfluxDB not available"}), 503

    if influx_writer_instance.delete_all_data():
        return jsonify({"success": True, "message": "Database deleted successfully"}), 200
    else:
        return jsonify({"error": "Failed to delete database"}), 500


def set_influx_writer(writer):
    """Set the InfluxDB writer instance for status reporting."""
    global influx_writer_instance
    influx_writer_instance = writer


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
