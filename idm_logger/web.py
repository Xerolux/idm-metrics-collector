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
            return redirect(url_for('login', next=request.path))
        return view(**kwargs)
    return wrapped_view

@app.before_request
def check_setup():
    if not config.is_setup() and request.endpoint != 'setup' and '/static/' not in request.path:
        return redirect(url_for('setup'))

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

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if config.is_setup():
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Save IDM
        config.data['idm']['host'] = request.form.get('idm_host')
        config.data['idm']['port'] = int(request.form.get('idm_port'))

        # Save Influx
        config.data['influx']['url'] = request.form.get('influx_url')
        config.data['influx']['org'] = request.form.get('influx_org')
        config.data['influx']['bucket'] = request.form.get('influx_bucket')
        config.data['influx']['token'] = request.form.get('influx_token')

        # Save Admin Password
        password = request.form.get('password')
        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return render_template('setup.html')

        config.set_admin_password(password)

        # Enable features
        config.data['web']['write_enabled'] = True # Default enable on setup? Or ask? User asked to be reconfigurable.
        config.data['setup_completed'] = True

        config.save()

        # Restart required? Probably. But we can update running instances too if structured well.
        # For now, we just redirect to login. The modbus client needs restart to pick up new host.
        flash("Setup complete. Please restart the service to apply changes fully.", "success")
        return redirect(url_for('login'))

    return render_template('setup.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if config.check_admin_password(password):
            session['logged_in'] = True
            next_url = request.args.get('next') or url_for('index')
            return redirect(next_url)
        else:
            flash("Invalid password", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

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

@app.route('/logs')
@login_required
def logs_page():
    logs = list(memory_handler.log_records)
    # Reverse to show newest first
    logs.reverse()
    return render_template('logs.html', logs=logs)

@app.route('/config', methods=['GET', 'POST'])
@login_required
def config_page():
    if request.method == 'POST':
        try:
            # IDM Host
            if 'idm_host' in request.form:
                config.data['idm']['host'] = request.form['idm_host']

            # Web Port
            if 'web_port' in request.form:
                try:
                    port = int(request.form['web_port'])
                    if 1024 <= port <= 65535:
                        config.data['web']['port'] = port
                    else:
                        flash("Port must be between 1024 and 65535", "danger")
                        return render_template('config.html')
                except ValueError:
                    flash("Invalid port number", "danger")
                    return render_template('config.html')

            # Write Enabled
            config.data['web']['write_enabled'] = 'write_enabled' in request.form

            # InfluxDB URL
            if 'influx_url' in request.form:
                 config.data['influx']['url'] = request.form['influx_url']

            # Handle password change
            new_pass = request.form.get('new_password')
            if new_pass:
                if len(new_pass) < 6:
                    flash("New password too short", "danger")
                    return render_template('config.html')
                config.set_admin_password(new_pass)
                flash("Password updated", "success")

            # Save config
            config.save()
            flash("Configuration saved. Restart required for some settings.", "success")
        except Exception as e:
            flash(f"Error saving config: {e}", "danger")

    return render_template('config.html')

@app.route('/restart', methods=['POST'])
@login_required
def restart_service():
    """Restart the service by sending SIGTERM to the main process."""
    flash("Restarting service...", "info")
    logger.info("Service restart requested by user")

    # Use threading to delay the restart so the response can be sent
    def delayed_restart():
        import time
        time.sleep(1)  # Give time for the response to be sent
        logger.info("Initiating restart...")
        # Send SIGTERM to main process (PID 1 in container)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=delayed_restart, daemon=True).start()

    return redirect(url_for('config_page'))

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

@app.route('/control', methods=['GET', 'POST'])
@login_required
def control_page():
    if not config.get("web.write_enabled"):
        flash("Write capabilities are disabled in configuration.", "warning")
        return redirect(url_for('index'))

    if request.method == 'POST':
        sensor_name = request.form.get('sensor')
        value = request.form.get('value')

        valid, msg = validate_write(sensor_name, value)
        if not valid:
             flash(f"Validation Error: {msg}", "danger")
        else:
            try:
                if modbus_client_instance:
                    modbus_client_instance.write_sensor(sensor_name, value)
                    flash(f"Successfully wrote {value} to {sensor_name}", "success")
                else:
                     flash("Modbus client not available", "danger")
            except Exception as e:
                flash(f"Failed to write: {e}", "danger")

    # Filter writable sensors
    writable_sensors = []
    if modbus_client_instance:
        all_sensors = {**modbus_client_instance.sensors, **modbus_client_instance.binary_sensors}
        for name, sensor in all_sensors.items():
            if sensor.supported_features != SensorFeatures.NONE:
                writable_sensors.append(sensor)

    # Sort by name
    writable_sensors.sort(key=lambda s: s.name)

    return render_template('control.html', sensors=writable_sensors)

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_page():
    if not config.get("web.write_enabled"):
         flash("Write capabilities (and scheduling) are disabled.", "warning")
         return redirect(url_for('index'))

    if not scheduler_instance:
        flash("Scheduler not available. Please restart the service.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            sensor = request.form.get('sensor')
            value = request.form.get('value')

            # Validate input for schedule too
            valid, msg = validate_write(sensor, value)
            if not valid:
                 flash(f"Validation Error: {msg}", "danger")
            else:
                job = {
                    'sensor': sensor,
                    'value': value,
                    'time': request.form.get('time'),
                    'days': request.form.getlist('days')
                }
                if scheduler_instance:
                    scheduler_instance.add_job(job)
                    flash("Schedule added", "success")

        elif action == 'delete':
            job_id = request.form.get('job_id')
            if scheduler_instance:
                scheduler_instance.delete_job(job_id)
                flash("Schedule deleted", "success")

        elif action == 'toggle':
             job_id = request.form.get('job_id')
             current_state = request.form.get('current_state') == 'True'
             if scheduler_instance:
                  scheduler_instance.update_job(job_id, {'enabled': not current_state})
                  state_text = "paused" if current_state else "resumed"
                  flash(f"Schedule {state_text}", "info")

        elif action == 'run_now':
             job_id = request.form.get('job_id')
             if scheduler_instance:
                 job = next((j for j in scheduler_instance.jobs if j['id'] == job_id), None)
                 if job and modbus_client_instance:
                     try:
                         # We skip validation here as it was validated on add, but double check doesn't hurt
                         modbus_client_instance.write_sensor(job['sensor'], job['value'])
                         flash(f"Executed: {job['sensor']} = {job['value']}", "success")
                     except Exception as e:
                         flash(f"Execution failed: {e}", "danger")
                 else:
                     flash("Job not found or system unavailable", "danger")

    jobs = scheduler_instance.jobs if scheduler_instance else []

    # Get sensors for dropdown
    writable_sensors = []
    if modbus_client_instance:
        try:
            all_sensors = {**modbus_client_instance.sensors, **modbus_client_instance.binary_sensors}
            for name, sensor in all_sensors.items():
                if sensor.supported_features != SensorFeatures.NONE:
                    writable_sensors.append(sensor)
        except Exception as e:
            logger.error(f"Error loading sensors for schedule: {e}")
            flash("Error loading sensors. Please check Modbus connection.", "danger")
    writable_sensors.sort(key=lambda s: s.name)

    return render_template('schedule.html', jobs=jobs, sensors=writable_sensors)

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
