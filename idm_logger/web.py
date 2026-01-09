from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from .config import config
from .sensor_addresses import SensorFeatures
from .log_handler import memory_handler
import threading
import logging
import functools
import os
import sys
import signal

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me_in_prod" # In real app, make random

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

        # Save Influx
        config.data['influx']['url'] = data.get('influx_url')
        config.data['influx']['org'] = data.get('influx_org')
        config.data['influx']['bucket'] = data.get('influx_bucket')
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
    return app.send_static_file('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')
    if config.check_admin_password(password):
        session['logged_in'] = True
        return jsonify({"success": True})
    else:
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
        "setup_completed": config.is_setup()
    }), 200


@app.route('/api/status')
def status_check():
    """Detailed status endpoint with InfluxDB connection info."""
    influx_status = None
    if influx_writer_instance:
        influx_status = influx_writer_instance.get_status()

    return jsonify({
        "status": "running",
        "setup_completed": config.is_setup(),
        "influx": influx_status,
        "modbus_connected": modbus_client_instance is not None,
        "scheduler_running": scheduler_instance is not None and config.get("web.write_enabled")
    })

@app.route('/api/logs')
@login_required
def logs_page():
    logs = list(memory_handler.log_records)
    logs.reverse()
    return jsonify(logs)

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def config_page():
    if request.method == 'GET':
        # Return safe config
        safe_config = config.data.copy()
        if 'influx' in safe_config:
            safe_config['influx'] = safe_config['influx'].copy()
            if 'token' in safe_config['influx']:
                 safe_config['influx']['token'] = '******' # Don't send token
            if 'password' in safe_config['influx']:
                 safe_config['influx']['password'] = '******'
        return jsonify(safe_config)

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

            # Write Enabled
            if 'write_enabled' in data:
                config.data['web']['write_enabled'] = bool(data['write_enabled'])

            # InfluxDB URL
            if 'influx_url' in data:
                 config.data['influx']['url'] = data['influx_url']

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
        except Exception:
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
                    "enum": [{"name": m.name, "value": m.value} for m in sensor.enum] if hasattr(sensor, "enum") and sensor.enum else None
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
                        "enum": [{"name": m.name, "value": m.value} for m in sensor.enum] if hasattr(sensor, "enum") and sensor.enum else None
                    }
                    writable_sensors.append(s_info)
        except Exception as e:
            logger.error(f"Error loading sensors for schedule: {e}")

    writable_sensors.sort(key=lambda s: s['name'])

    return jsonify({"jobs": jobs, "sensors": writable_sensors})

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
            app.run(host=host, port=port, use_reloader=False)
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
