# SPDX-License-Identifier: MIT
from flask import (
    Flask,
    request,
    jsonify,
    session,
    abort,
    send_from_directory,
    send_file,
)
from flask_socketio import SocketIO
from waitress import serve

try:
    from flasgger import Swagger

    HAS_FLASGGER = True
except ImportError:
    HAS_FLASGGER = False
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from .technician_auth import calculate_codes
from .config import config
from .log_handler import memory_handler
from .backup import backup_manager, BACKUP_DIR
from .mqtt import mqtt_publisher
from .signal_notifications import send_signal_message
from .notifications import notification_manager
from .update_manager import (
    check_for_update,
    perform_update as run_update,
    get_current_version,
    can_run_updates,
    can_run_docker_updates,
    check_docker_updates,
)
from .alerts import alert_manager
from .dashboard_config import dashboard_manager
from .templates import get_alert_templates
from .annotations import AnnotationManager
from .variables import VariableManager
from .expression_parser import ExpressionParser
from .websocket_handler import websocket_handler
from .sharing import SharingManager
from .model_updater import model_updater
from .manufacturers import ManufacturerRegistry
from .migrations import run_migration, get_default_heatpump_id
from shutil import which
import asyncio
import threading
import logging
import requests
import functools
import os
import signal
import ipaddress
import time
import re
import pandas as pd
import io
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Log if flasgger is not available
if not HAS_FLASGGER:
    logger.warning("flasgger not available - API documentation will be disabled")

# Input validation patterns and limits
_MAX_STRING_LENGTH = 255
_MAX_URL_LENGTH = 2048
_HOSTNAME_PATTERN = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
)
_IP_PATTERN = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$|"  # IPv4
    r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$"  # IPv6 (simplified)
)
# Dangerous shell characters to block in string inputs
_SHELL_DANGEROUS_CHARS = re.compile(r'[;&|`$(){}[\]<>\\\'"]')


def _validate_host(value: str) -> tuple[bool, str]:
    """Validate hostname or IP address."""
    if not value or not isinstance(value, str):
        return False, "Host darf nicht leer sein"
    if len(value) > _MAX_STRING_LENGTH:
        return False, f"Host darf maximal {_MAX_STRING_LENGTH} Zeichen lang sein"
    # Check if it's a valid IP
    if _IP_PATTERN.match(value):
        try:
            ipaddress.ip_address(value)
            return True, ""
        except ValueError:
            return False, "Ungültige IP-Adresse"
    # Check if it's a valid hostname
    if _HOSTNAME_PATTERN.match(value):
        return True, ""
    return False, "Ungültiger Hostname oder IP-Adresse"


def _validate_url(value: str) -> tuple[bool, str]:
    """Validate URL format."""
    if not value or not isinstance(value, str):
        return False, "URL darf nicht leer sein"
    if len(value) > _MAX_URL_LENGTH:
        return False, f"URL darf maximal {_MAX_URL_LENGTH} Zeichen lang sein"
    # Basic URL validation
    if not value.startswith(("http://", "https://")):
        return False, "URL muss mit http:// oder https:// beginnen"
    # Block dangerous characters
    if _SHELL_DANGEROUS_CHARS.search(value.split("://", 1)[-1].split("/", 1)[0]):
        return False, "URL enthält ungültige Zeichen"
    return True, ""


def _validate_string(
    value: str, field_name: str, max_length: int = None, allow_empty: bool = True
) -> tuple[bool, str]:
    """Validate generic string input."""
    if value is None:
        if allow_empty:
            return True, ""
        return False, f"{field_name} darf nicht leer sein"
    if not isinstance(value, str):
        return False, f"{field_name} muss ein Text sein"
    max_len = max_length or _MAX_STRING_LENGTH
    if len(value) > max_len:
        return False, f"{field_name} darf maximal {max_len} Zeichen lang sein"
    # Block shell injection characters in most string fields
    if _SHELL_DANGEROUS_CHARS.search(value):
        return False, f"{field_name} enthält ungültige Sonderzeichen"
    return True, ""


def _validate_topic(value: str) -> tuple[bool, str]:
    """Validate MQTT topic format."""
    if not value or not isinstance(value, str):
        return True, ""  # Allow empty topics
    if len(value) > _MAX_STRING_LENGTH:
        return False, f"Topic darf maximal {_MAX_STRING_LENGTH} Zeichen lang sein"
    # MQTT topics allow /, +, # but we should be careful
    if re.search(r'[;&|`$(){}[\]<>\\\'"]', value):
        return False, "Topic enthält ungültige Zeichen"
    return True, ""


app = Flask(__name__)
app.secret_key = config.get_flask_secret_key()
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Secure cookie flag - enable for HTTPS deployments (set web.secure_cookies: true)
app.config["SESSION_COOKIE_SECURE"] = config.get("web.secure_cookies", False)

# Initialize SocketIO with configurable CORS
# Security: Read allowed origins from config, default to same-origin only
_cors_origins = config.get("web.cors_allowed_origins", None)
if _cors_origins == "*":
    logger.warning(
        "CORS is set to allow all origins ('*'). "
        "Consider restricting to specific origins for production."
    )
socketio = SocketIO(
    app,
    cors_allowed_origins=_cors_origins,
    async_mode="threading",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
)

# Trust proxies if configured (common in Docker environments)
if os.environ.get("TRUST_PROXIES") or config.get("web.trust_proxies"):
    # X-Forwarded-For, X-Forwarded-Proto, X-Forwarded-Host, X-Forwarded-Prefix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Swagger/OpenAPI Configuration
if HAS_FLASGGER:
    app.config["SWAGGER"] = {
        "title": "IDM Metrics Collector API",
        "uiversion": 3,
        "version": "1.0.1",
        "description": "API for IDM Heat Pump Monitoring & Control",
    }
    swagger = Swagger(app)
else:
    swagger = None

# Rate Limiter Configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# Annotation Manager
annotation_manager = AnnotationManager(config)

# Variable Manager
variable_manager = VariableManager(config)

# Expression Parser
expression_parser = ExpressionParser()

# WebSocket Handler
websocket_handler.init_app(app, socketio)

# Sharing Manager
sharing_manager = SharingManager(config)

# Shared state
current_data = {}
data_lock = threading.Lock()
scheduler_instance = None
metrics_writer_instance = None
# Global heatpump_manager instance (set by run_web)
heatpump_manager_instance = None

# Cache for network security objects to avoid re-parsing on every request
_net_sec_cache = {
    "whitelist_ref": None,
    "whitelist_nets": [],
    "blacklist_ref": None,
    "blacklist_nets": [],
    "ip_results": {},  # Performance: Cache IP check results {ip_str: (allowed, timestamp)}
    "ip_cache_ttl": 300,  # Cache results for 5 minutes
}

# AI Status Cache
_ai_status_lock = threading.Lock()
_ai_status_cache = {
    "service": "ml-service (River/HST)",
    "online": False,
    "score": 0.0,
    "is_anomaly": False,
    "last_update": None,
    "error": None,
}


def _update_ai_status_once():
    """Perform a single update of the AI status."""
    try:
        metrics_url = config.data.get("metrics", {}).get(
            "url", "http://victoriametrics:8428/write"
        )
        base_url = metrics_url.replace("/write", "")
        query_url = f"{base_url}/api/v1/query"

        query = (
            'last_over_time({__name__=~"idm_anomaly_score.*|idm_anomaly_flag.*"}[2h])'
        )
        try:
            response = requests.get(query_url, params={"query": query}, timeout=10)
        except requests.RequestException as e:
            # Log specific network error but don't crash loop
            logger.debug(f"AI status update network error: {e}")
            with _ai_status_lock:
                _ai_status_cache["online"] = False
            return

        new_status = {
            "service": "ml-service (River/HST)",
            "online": False,
            "score": 0.0,
            "is_anomaly": False,
            "last_update": None,
            "error": None,
            "source": "local",  # Default
        }

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                results = data.get("data", {}).get("result", [])
                for res in results:
                    name = res["metric"].get("__name__", "")
                    val = res["value"][1]  # [timestamp, value]
                    timestamp = res["value"][0]

                    if "idm_anomaly_score" in name:
                        new_status["score"] = float(val)
                        new_status["last_update"] = timestamp
                        new_status["online"] = True
                    elif "idm_anomaly_flag" in name:
                        new_status["is_anomaly"] = float(val) > 0.5
        else:
            new_status["error"] = f"VictoriaMetrics error: {response.status_code}"

        # Check model source file existence (indirect check)
        # Ideally ML service would report this via metrics, but we can check file system if shared
        # Or add it to health check.
        # For now, let's assume if file exists in DATA_DIR, it's used (since ML service prefers it)
        import os

        DATA_DIR = os.environ.get("DATA_DIR", ".")
        model_path = os.path.join(DATA_DIR, "community_model.enc")
        if os.path.exists(model_path):
            new_status["source"] = "Community Model (Encrypted)"
            new_status["model_date"] = os.path.getmtime(model_path)
        else:
            new_status["source"] = "Local Training"

        with _ai_status_lock:
            _ai_status_cache.update(new_status)

    except Exception as e:
        logger.error(f"Error in AI status update loop: {e}")


def _update_ai_status_loop():
    """Background thread to update AI status periodically with exponential backoff."""
    logger.info("Starting AI status update loop")
    base_interval = 60  # Normal interval: 60 seconds
    max_interval = 600  # Max backoff: 10 minutes
    current_interval = base_interval
    consecutive_failures = 0

    while True:
        try:
            _update_ai_status_once()
            # Check if service is online
            with _ai_status_lock:
                is_online = _ai_status_cache.get("online", False)

            if is_online:
                # Reset backoff on success
                consecutive_failures = 0
                current_interval = base_interval
            else:
                # Exponential backoff on failure
                consecutive_failures += 1
                current_interval = min(
                    base_interval * (2 ** min(consecutive_failures, 5)), max_interval
                )
                if consecutive_failures == 1:
                    logger.debug(
                        f"AI service offline, backing off to {current_interval}s"
                    )
        except Exception as e:
            logger.error(f"Error in AI status loop: {e}")
            consecutive_failures += 1
            current_interval = min(
                base_interval * (2 ** min(consecutive_failures, 5)), max_interval
            )

        time.sleep(current_interval)


def _start_ai_status_thread():
    t = threading.Thread(target=_update_ai_status_loop, daemon=True)
    t.start()


@functools.lru_cache(maxsize=128)
def get_ip_obj(ip_str):
    """Cached IP object creation."""
    try:
        return ipaddress.ip_address(ip_str)
    except ValueError:
        return None


def update_current_data(data):
    with data_lock:
        current_data.clear()
        current_data.update(data)

    # Broadcast updates via WebSocket
    try:
        websocket_handler.broadcast_metrics(data)
    except Exception as e:
        logger.error(f"Failed to broadcast metrics: {e}")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Nicht autorisiert"}), 401
            return jsonify({"error": "Nicht autorisiert"}), 401
        return view(**kwargs)

    return wrapped_view


def auth_or_token_required(view):
    """Allow access if logged in OR if valid share token provided."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # 1. Check Session
        if session.get("logged_in"):
            return view(**kwargs)

        # 2. Check Share Token
        token_id = request.headers.get("X-Share-Token")
        if token_id:
            password = request.headers.get("X-Share-Password")
            if sharing_manager.validate_token(token_id, password):
                return view(**kwargs)

        return jsonify({"error": "Unauthorized"}), 401

    return wrapped_view


@app.before_request
def check_ip_whitelist():
    """Check if the request IP is allowed based on whitelist/blacklist."""
    if not config.get("network_security.enabled", False):
        return

    client_ip = request.remote_addr
    if not client_ip:
        return

    # Performance: Check IP result cache first (O(1) lookup)
    now = time.time()
    cached = _net_sec_cache["ip_results"].get(client_ip)
    if cached:
        allowed, cached_time = cached
        if now - cached_time < _net_sec_cache["ip_cache_ttl"]:
            if not allowed:
                abort(403)
            return
        # Cache expired, remove entry
        del _net_sec_cache["ip_results"][client_ip]

    ip = get_ip_obj(client_ip)
    if not ip:
        logger.warning(f"Invalid client IP: {client_ip}")
        _net_sec_cache["ip_results"][client_ip] = (False, now)
        abort(403)

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
            _net_sec_cache["ip_results"][client_ip] = (False, now)
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
        is_allowed = False
        for net in _net_sec_cache["whitelist_nets"]:
            if ip in net:
                is_allowed = True
                break

        if not is_allowed:
            logger.warning(f"Blocked IP {client_ip} (not in whitelist)")
            _net_sec_cache["ip_results"][client_ip] = (False, now)
            abort(403)

    # Cache successful result
    _net_sec_cache["ip_results"][client_ip] = (True, now)


# Default CSP - can be overridden via config
# Note: 'unsafe-inline' for styles is needed for Vue/PrimeVue dynamic styles
# 'unsafe-eval' removed - not needed for production Vue builds
_DEFAULT_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "connect-src 'self' ws: wss:; "
    "font-src 'self' data:; "
    "frame-src 'self'; "
    "frame-ancestors 'self'"
)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    # Use configurable CSP or default
    csp = config.get("web.content_security_policy", _DEFAULT_CSP)
    response.headers["Content-Security-Policy"] = csp
    return response


# Keys that should never be exposed to templates/frontend
_SENSITIVE_CONFIG_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "private_key",
        "smtp_password",
        "bot_token",
        "webhook_url",
        "internal_api_key",
        "telemetry_auth_token",
    }
)


def _filter_sensitive_config(data: dict, parent_key: str = "") -> dict:
    """Recursively filter sensitive data from config."""
    filtered = {}
    for key, value in data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        # Check if key contains sensitive patterns
        key_lower = key.lower()
        is_sensitive = any(s in key_lower for s in _SENSITIVE_CONFIG_KEYS)
        if is_sensitive:
            # Mask sensitive values
            filtered[key] = "***" if value else None
        elif isinstance(value, dict):
            filtered[key] = _filter_sensitive_config(value, full_key)
        else:
            filtered[key] = value
    return filtered


@app.context_processor
def inject_config():
    safe_config = _filter_sensitive_config(config.data)
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

        if "heatpump_model" in data:
            config.data["heatpump_model"] = data.get("heatpump_model")

        if "share_data" in data:
            config.data["share_data"] = bool(data.get("share_data"))

        if "telemetry_auth_token" in data:
            config.data["telemetry_auth_token"] = data.get("telemetry_auth_token")

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
@limiter.limit("30 per minute")  # Rate limit to prevent auth state enumeration
def check_auth():
    return jsonify({"authenticated": session.get("logged_in", False)})


@app.route("/logout")
@limiter.limit(
    "10 per minute"
)  # Rate limit logout to prevent session manipulation attacks
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
        # Check if we have nested data (Multi-HP)
        if any(isinstance(v, dict) for v in current_data.values()):
            # Legacy Endpoint: Return default/legacy heatpump data flattened
            hp_id = get_default_heatpump_id()
            if hp_id and hp_id in current_data:
                return jsonify(current_data[hp_id])
            # Fallback: Return first available heatpump data
            if current_data:
                first_key = next(iter(current_data))
                return jsonify(current_data[first_key])
            return jsonify({})

        return jsonify(current_data)


@app.route("/api/metrics/current")
@login_required
def get_current_metrics():
    """
    Get current values for all metrics from VictoriaMetrics.
    Returns the latest value for each metric.
    """
    try:
        metrics_url = config.data.get("metrics", {}).get(
            "url", "http://victoriametrics:8428/write"
        )
        base_url = metrics_url.replace("/write", "").replace("/api/v1/write", "")
        query_url = f"{base_url}/api/v1/query"

        # Query for latest values of all idm_heatpump and idm_anomaly metrics
        query = '{__name__=~"idm_heatpump.*|idm_anomaly.*"}'
        response = requests.get(query_url, params={"query": query}, timeout=10)

        if response.status_code != 200:
            logger.error(f"VictoriaMetrics query failed: {response.status_code}")
            return jsonify({"error": "Failed to query current values"}), 500

        data = response.json()
        if data.get("status") != "success":
            return jsonify({})

        result = data.get("data", {}).get("result", [])

        # Format: {metric_name: {value: 123, timestamp: 1234567890}}
        metrics = {}
        for item in result:
            metric = item.get("metric", {})
            name = metric.get("__name__", "")
            value = item.get("value", [None, None])[1]

            if name and value is not None:
                # Remove labels for display, keep value
                try:
                    num_value = float(value)
                    metrics[name] = {
                        "value": num_value,
                        "timestamp": item.get("value", [None, None])[0],
                    }
                except (ValueError, TypeError):
                    pass

        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Failed to fetch current metrics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboards", methods=["GET", "POST"])
@login_required
def dashboards_api():
    """Get all dashboards or create a new one."""
    if request.method == "GET":
        return jsonify(dashboard_manager.get_all_dashboards())

    if request.method == "POST":
        data = request.get_json()
        name = data.get("name", "New Dashboard")
        if not name:
            return jsonify({"error": "Name is required"}), 400
        dashboard = dashboard_manager.create_dashboard(name)
        return jsonify(dashboard), 201


@app.route("/api/dashboards/<dashboard_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def dashboard_api(dashboard_id):
    """Get, update or delete a specific dashboard."""
    if request.method == "GET":
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            return jsonify({"error": "Dashboard not found"}), 404
        return jsonify(dashboard)

    if request.method == "PUT":
        updates = request.get_json()
        dashboard = dashboard_manager.update_dashboard(dashboard_id, updates)
        if not dashboard:
            return jsonify({"error": "Dashboard not found"}), 404
        return jsonify(dashboard)

    if request.method == "DELETE":
        success = dashboard_manager.delete_dashboard(dashboard_id)
        if not success:
            return jsonify({"error": "Cannot delete dashboard"}), 400
        return jsonify({"success": True})


@app.route("/api/dashboards/<dashboard_id>/charts", methods=["POST"])
@login_required
def add_chart_api(dashboard_id):
    """Add a chart to a dashboard."""
    data = request.get_json()
    title = data.get("title")
    queries = data.get("queries", [])
    hours = data.get("hours", 12)

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not queries:
        return jsonify({"error": "Queries are required"}), 400

    chart = dashboard_manager.add_chart(dashboard_id, title, queries, hours)
    if not chart:
        return jsonify({"error": "Dashboard not found"}), 404
    return jsonify(chart), 201


@app.route(
    "/api/dashboards/<dashboard_id>/charts/<chart_id>",
    methods=["PUT", "DELETE"],
)
@login_required
def chart_api(dashboard_id, chart_id):
    """Update or delete a chart."""
    if request.method == "PUT":
        updates = request.get_json()
        chart = dashboard_manager.update_chart(dashboard_id, chart_id, updates)
        if not chart:
            return jsonify({"error": "Chart or dashboard not found"}), 404
        return jsonify(chart)

    if request.method == "DELETE":
        success = dashboard_manager.delete_chart(dashboard_id, chart_id)
        if not success:
            return jsonify({"error": "Chart or dashboard not found"}), 404
        return jsonify({"success": True})


@app.route("/api/metrics/available")
@login_required
def get_available_metrics():
    """
    Get list of all available metrics from VictoriaMetrics.
    Groups metrics by type (temp, power, pressure, etc.)
    """
    try:
        metrics_url = config.data.get("metrics", {}).get(
            "url", "http://victoriametrics:8428/write"
        )
        # Build base URL correctly
        base_url = metrics_url.replace("/write", "").replace("/api/v1/write", "")

        # Use series endpoint to get all metrics with idm_heatpump_ prefix
        query_url = f"{base_url}/api/v1/series"
        params = {
            "match[]": '{__name__=~"idm_heatpump.*|idm_anomaly_.*"}',
            "limit": "1000",
        }

        logger.debug(f"Fetching metrics from: {query_url} with params: {params}")

        response = requests.get(query_url, params=params, timeout=10)

        if response.status_code != 200:
            logger.error(
                f"VictoriaMetrics returned {response.status_code}: {response.text}"
            )
            return jsonify(
                {"error": f"Failed to query metrics: {response.status_code}"}
            ), 500

        data = response.json()
        # series endpoint returns array of objects with __name__ field
        if isinstance(data, dict):
            series_data = data.get("data", [])
        else:
            series_data = data

        # Extract unique metric names
        metric_names = set()
        for series in series_data:
            if isinstance(series, dict) and "__name__" in series:
                metric_names.add(series["__name__"])

        metric_names = sorted(metric_names)
        logger.debug(f"Found {len(metric_names)} unique metrics")

        # Group metrics by type
        grouped = {
            "temperature": [],
            "power": [],
            "pressure": [],
            "energy": [],
            "flow": [],
            "status": [],
            "mode": [],
            "control": [],
            "state": [],
            "ai": [],
            "other": [],
        }

        for name in metric_names:
            # Remove 'idm_heatpump_' prefix for display
            display_name = name.replace("idm_heatpump_", "")

            if name.startswith("idm_anomaly_"):
                grouped["ai"].append({"name": name, "display": name})
            elif display_name.startswith("temp_"):
                grouped["temperature"].append({"name": name, "display": display_name})
            elif display_name.startswith("power_"):
                grouped["power"].append({"name": name, "display": display_name})
            elif display_name.startswith("pressure_"):
                grouped["pressure"].append({"name": name, "display": display_name})
            elif display_name.startswith("energy_"):
                grouped["energy"].append({"name": name, "display": display_name})
            elif display_name.startswith("flow_"):
                grouped["flow"].append({"name": name, "display": display_name})
            elif display_name.startswith("status_"):
                grouped["status"].append({"name": name, "display": display_name})
            elif display_name.startswith("mode_"):
                grouped["mode"].append({"name": name, "display": display_name})
            elif display_name.startswith("control_"):
                grouped["control"].append({"name": name, "display": display_name})
            elif display_name.startswith("state_"):
                grouped["state"].append({"name": name, "display": display_name})
            else:
                grouped["other"].append({"name": name, "display": display_name})

        return jsonify(grouped)
    except Exception as e:
        logger.error(f"Failed to fetch available metrics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/status")
@login_required
def get_ai_status():
    """
    Get current AI service status from VictoriaMetrics.
    """
    with _ai_status_lock:
        status = _ai_status_cache.copy()
    return jsonify(status)


@app.route("/api/ai/update_now", methods=["POST"])
@login_required
def trigger_ai_update():
    """
    Manually trigger a check for community model updates.
    """
    try:
        model_updater.trigger_check()
        return jsonify(
            {"success": True, "message": "Suche nach Updates im Hintergrund gestartet."}
        )
    except Exception as e:
        logger.error(f"Failed to trigger model update: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/telemetry/pool-status", methods=["GET"])
@login_required
def get_telemetry_pool_status():
    """
    Get the current status of the community data pool from telemetry server.
    Proxies the request to the telemetry server's /api/v1/pool/status endpoint.
    """
    try:
        # Get telemetry endpoint from config or environment
        telemetry_endpoint = os.environ.get(
            "TELEMETRY_ENDPOINT", "https://collector.xerolux.de"
        )

        # Request pool status from telemetry server (public endpoint, no auth needed)
        response = requests.get(f"{telemetry_endpoint}/api/v1/pool/status", timeout=10)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            logger.warning(f"Telemetry pool status failed: {response.status_code}")
            return jsonify(
                {
                    "data_sufficient": False,
                    "total_installations": 0,
                    "total_data_points": 0,
                    "models_available": [],
                    "message": "Telemetry server returned an error.",
                    "message_de": "Telemetry-Server hat einen Fehler zurückgegeben.",
                }
            )

    except requests.exceptions.Timeout:
        logger.warning("Telemetry pool status request timed out")
        return jsonify(
            {
                "data_sufficient": False,
                "total_installations": 0,
                "total_data_points": 0,
                "models_available": [],
                "message": "Telemetry server request timed out.",
                "message_de": "Telemetry-Server Anfrage hat das Zeitlimit überschritten.",
            }
        )
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to telemetry server")
        return jsonify(
            {
                "data_sufficient": False,
                "total_installations": 0,
                "total_data_points": 0,
                "models_available": [],
                "message": "Could not connect to telemetry server. Data is collected locally.",
                "message_de": "Keine Verbindung zum Telemetry-Server. Daten werden lokal gesammelt.",
            }
        )
    except Exception as e:
        logger.error(f"Telemetry pool status failed: {e}")
        return jsonify(
            {
                "data_sufficient": False,
                "error": str(e),
                "message": "An error occurred while checking data pool status.",
                "message_de": "Fehler beim Abrufen des Datenpool-Status.",
            }
        ), 500


@app.route("/api/telemetry/community/averages", methods=["GET"])
@auth_or_token_required
def get_community_averages():
    """
    Get community averages from telemetry server.
    Proxies the request to /api/v1/community/averages.
    """
    try:
        model = request.args.get("model")
        metrics = request.args.get("metrics")

        if not model:
            return jsonify({"error": "Model parameter is required"}), 400

        # Get telemetry endpoint from config or environment
        telemetry_endpoint = os.environ.get(
            "TELEMETRY_ENDPOINT", "https://collector.xerolux.de"
        )

        auth_token = config.data.get("telemetry_auth_token")
        if not auth_token:
            # Try environment variable
            auth_token = os.environ.get("TELEMETRY_AUTH_TOKEN")

        if not auth_token:
            return jsonify(
                {
                    "error": "Telemetry auth token not configured",
                    "message": "Please configure telemetry token in settings.",
                }
            ), 401

        headers = {"Authorization": f"Bearer {auth_token}"}
        params = {"model": model}
        if metrics:
            params["metrics"] = metrics

        response = requests.get(
            f"{telemetry_endpoint}/api/v1/community/averages",
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            return jsonify(response.json())
        elif response.status_code == 401:
            return jsonify({"error": "Invalid telemetry token"}), 401
        else:
            logger.warning(
                f"Community averages failed: {response.status_code} - {response.text}"
            )
            return jsonify(
                {"error": f"Telemetry server error: {response.status_code}"}
            ), 502

    except Exception as e:
        logger.error(f"Community averages proxy failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/metrics/query_range", methods=["GET"])
@auth_or_token_required
def query_metrics_range():
    """
    Proxy request to VictoriaMetrics /api/v1/query_range
    """
    try:
        metrics_url = config.data.get("metrics", {}).get(
            "url", "http://victoriametrics:8428/write"
        )
        base_url = metrics_url.replace("/write", "")
        query_url = f"{base_url}/api/v1/query_range"

        # Forward parameters
        params = {
            "query": request.args.get("query"),
            "start": request.args.get("start"),
            "end": request.args.get("end"),
            "step": request.args.get("step"),
        }

        response = requests.get(query_url, params=params, timeout=10)
        if response.status_code != 200:
            logger.error(f"VictoriaMetrics query failed: {response.text}")
            return jsonify(
                {"status": "error", "error": response.text}
            ), response.status_code
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Metrics query failed: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/export/data", methods=["POST"])
@login_required
def export_metrics_data():
    """
    Export metrics data in various formats (CSV, Excel, JSON).

    Expects JSON:
    {
        "format": "csv|excel|json",
        "metrics": ["metric1", "metric2", ...] or "all",
        "start": timestamp or ISO string,
        "end": timestamp or ISO string,
        "step": "1m" (optional, default: auto),
        "dashboard_name": "Dashboard Name" (optional, for filename)
    }

    Returns: File download with appropriate MIME type
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        export_format = data.get("format", "csv").lower()
        metrics = data.get("metrics", "all")
        start = data.get("start")
        end = data.get("end")
        step = data.get("step", "1m")
        dashboard_name = data.get("dashboard_name", "metrics")

        # Validate format
        if export_format not in ["csv", "excel", "json"]:
            return jsonify({"error": f"Unsupported format: {export_format}"}), 400

        # Validate time range
        if not start or not end:
            return jsonify({"error": "start and end timestamps are required"}), 400

        # Get VictoriaMetrics URL
        metrics_url = config.data.get("metrics", {}).get(
            "url", "http://victoriametrics:8428/write"
        )
        base_url = metrics_url.replace("/write", "").replace("/api/v1/write", "")

        # Build metrics list
        if metrics == "all":
            # Query all available idm metrics
            query_url = f"{base_url}/api/v1/query"
            query = '{__name__=~"idm_heatpump.*|idm_anomaly.*"}'
            response = requests.get(query_url, params={"query": query}, timeout=10)

            if response.status_code != 200:
                return jsonify({"error": "Failed to fetch available metrics"}), 500

            result_data = response.json()
            if result_data.get("status") != "success":
                return jsonify({"error": "Failed to query metrics"}), 500

            metrics = [
                item.get("metric", {}).get("__name__", "")
                for item in result_data.get("data", {}).get("result", [])
            ]
            metrics = [m for m in metrics if m]  # Filter empty names

        if not metrics:
            return jsonify({"error": "No metrics selected"}), 400

        # Fetch data for each metric
        all_data = []
        query_range_url = f"{base_url}/api/v1/query_range"

        for metric in metrics:
            params = {
                "query": metric,
                "start": start,
                "end": end,
                "step": step,
            }

            response = requests.get(query_range_url, params=params, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {metric}: {response.status_code}")
                continue

            metric_data = response.json()
            if metric_data.get("status") != "success":
                continue

            results = metric_data.get("data", {}).get("result", [])
            for result in results:
                metric_name = result.get("metric", {}).get("__name__", metric)
                values = result.get("values", [])

                for timestamp, value in values:
                    try:
                        all_data.append(
                            {
                                "timestamp": datetime.fromtimestamp(float(timestamp)),
                                "metric": metric_name,
                                "value": float(value),
                            }
                        )
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid data point: {e}")
                        continue

        if not all_data:
            return jsonify(
                {"error": "No data found for selected metrics and time range"}
            ), 404

        # Create DataFrame
        df = pd.DataFrame(all_data)
        df = df.sort_values(["timestamp", "metric"])

        # Generate filename
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", dashboard_name)

        # Export based on format
        if export_format == "csv":
            # CSV export
            output = io.StringIO()
            df.to_csv(output, index=False, date_format="%Y-%m-%d %H:%M:%S")
            output.seek(0)

            return send_file(
                io.BytesIO(output.getvalue().encode("utf-8")),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"{safe_name}_export_{timestamp_str}.csv",
            )

        elif export_format == "excel":
            # Excel export
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                # Overview sheet with all data
                df.to_excel(writer, sheet_name="All Data", index=False)

                # Create separate sheet for each metric
                for metric in df["metric"].unique():
                    metric_df = df[df["metric"] == metric][
                        ["timestamp", "value"]
                    ].copy()
                    # Sanitize sheet name (max 31 chars, no special chars)
                    sheet_name = re.sub(r"[^a-zA-Z0-9_]", "_", metric)[:31]
                    metric_df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Summary statistics sheet
                summary_data = []
                for metric in df["metric"].unique():
                    metric_values = df[df["metric"] == metric]["value"]
                    summary_data.append(
                        {
                            "Metric": metric,
                            "Count": len(metric_values),
                            "Min": metric_values.min(),
                            "Max": metric_values.max(),
                            "Mean": metric_values.mean(),
                            "Median": metric_values.median(),
                            "Std Dev": metric_values.std(),
                        }
                    )

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

            output.seek(0)

            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=f"{safe_name}_export_{timestamp_str}.xlsx",
            )

        elif export_format == "json":
            # JSON export
            # Group by metric for better structure
            json_data = {
                "export_info": {
                    "dashboard": dashboard_name,
                    "exported_at": datetime.now().isoformat(),
                    "time_range": {"start": start, "end": end, "step": step},
                    "total_data_points": len(df),
                },
                "metrics": {},
            }

            for metric in df["metric"].unique():
                metric_df = df[df["metric"] == metric]
                json_data["metrics"][metric] = {
                    "data": [
                        {
                            "timestamp": row["timestamp"].isoformat(),
                            "value": row["value"],
                        }
                        for _, row in metric_df.iterrows()
                    ],
                    "statistics": {
                        "count": len(metric_df),
                        "min": float(metric_df["value"].min()),
                        "max": float(metric_df["value"].max()),
                        "mean": float(metric_df["value"].mean()),
                        "median": float(metric_df["value"].median()),
                    },
                }

            return send_file(
                io.BytesIO(jsonify(json_data).get_data()),
                mimetype="application/json",
                as_attachment=True,
                download_name=f"{safe_name}_export_{timestamp_str}.json",
            )

    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        return jsonify({"error": f"Export failed: {str(e)}"}), 500


@app.route("/api/query/evaluate", methods=["POST"])
@auth_or_token_required
def evaluate_expression():
    """
    Evaluate a mathematical expression on query results.

    Expects JSON:
    {
        "expression": "A/B",  // Expression to evaluate
        "queries": {           // Query results for each label
            "A": [[timestamp1, value1], [timestamp2, value2], ...],
            "B": [[timestamp1, value1], [timestamp2, value2], ...]
        }
    }

    Returns:
    {
        "status": "success",
        "data": {
            "values": [[timestamp1, result1], [timestamp2, result2], ...]
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "error": "No data provided"}), 400

        expression = data.get("expression")
        queries = data.get("queries", {})

        if not expression:
            return jsonify({"status": "error", "error": "Expression is required"}), 400

        if not queries:
            return jsonify({"status": "error", "error": "Queries are required"}), 400

        # Validate expression
        is_valid, error_msg = expression_parser.validate_expression(expression)
        if not is_valid:
            return jsonify({"status": "error", "error": error_msg}), 400

        # Set query results
        expression_parser.set_query_results(queries)

        # Evaluate expression
        results = expression_parser.evaluate_expression_series(expression)

        return jsonify({"status": "success", "data": {"values": results}})
    except Exception as e:
        logger.error(f"Expression evaluation failed: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/internal/ml_alert", methods=["POST"])
@limiter.limit("60 per minute")  # Rate limit internal API
def ml_alert_endpoint():
    """
    Internal endpoint for ML service to send anomaly alerts.
    Protected by shared secret if configured.
    """
    import hmac

    # Security Check
    internal_key = config.get("internal_api_key")
    if not internal_key:
        logger.error("INTERNAL_API_KEY not configured - rejecting ML alert")
        return jsonify({"error": "Configuration Error: INTERNAL_API_KEY not set"}), 503

    auth_header = request.headers.get("X-Internal-Secret")
    # Use constant-time comparison to prevent timing attacks
    if not auth_header or not hmac.compare_digest(auth_header, internal_key):
        logger.warning(
            f"Unauthorized access attempt to ml_alert from {request.remote_addr}"
        )
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        score = data.get("score", 0.0)
        threshold = data.get("threshold", 0.7)
        message = data.get("message", f"ML Alert: Score {score}")
        extra_data = data.get("data", {})
        mode = extra_data.get("mode", "unknown")

        logger.warning(
            f"ML Alert received: {message} (Score: {score}, Threshold: {threshold})"
        )

        # Send notification via notification manager
        notification_manager.send_all(
            message=message, subject="IDM ML Anomalie-Warnung"
        )

        # Add Annotation to Dashboard (Rückkanal)
        try:
            annotation_manager.add_annotation(
                time=int(time.time()),
                text=message,  # Includes top features
                tags=["ai", "anomaly", mode],
                color="#ef4444",
            )
        except Exception as e:
            logger.error(f"Failed to create annotation for ML alert: {e}")

        return jsonify(
            {"status": "success", "message": "Alert processed", "notified": True}
        ), 200

    except Exception as e:
        logger.error(f"Failed to process ML alert: {e}")
        return jsonify({"error": str(e)}), 500


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

    # Check if any heat pump is connected
    modbus_connected = False
    if heatpump_manager_instance:
        status_list = heatpump_manager_instance.get_status()
        modbus_connected = any(hp.get("connected", False) for hp in status_list)

    return jsonify(
        {
            "status": "running",
            "setup_completed": config.is_setup(),
            "metrics": metrics_status,
            "mqtt": mqtt_status,
            "modbus_connected": modbus_connected,
            "scheduler_running": scheduler_instance is not None
            and config.get("web.write_enabled"),
        }
    )


@app.route("/api/websocket/stats")
@login_required
def websocket_stats():
    """Get WebSocket connection statistics."""
    return jsonify(websocket_handler.get_stats())


@app.route("/api/logs")
@login_required
def logs_page():
    since_id = request.args.get("since_id", type=int)
    # Performance: Add pagination with configurable limit (default 100, max 1000)
    limit = request.args.get("limit", default=100, type=int)
    limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
    logs = memory_handler.get_logs(since_id=since_id)
    # logs are already in [newest, ..., oldest] order
    return jsonify(logs[:limit])


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
        # Filter sensitive data before sending to frontend
        safe_config = _filter_sensitive_config(config.data)
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
            # IDM Host - validate hostname/IP (allow empty for initial setup)
            if "idm_host" in data:
                host_value = data["idm_host"]
                if host_value:  # Only validate if not empty
                    valid, err = _validate_host(host_value)
                    if not valid:
                        return jsonify({"error": f"IDM Host: {err}"}), 400
                config.data["idm"]["host"] = host_value
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
                valid, err = _validate_url(data["metrics_url"])
                if not valid:
                    return jsonify({"error": f"Metrics URL: {err}"}), 400
                config.data["metrics"]["url"] = data["metrics_url"]

            # MQTT
            if "mqtt_enabled" in data:
                config.data["mqtt"]["enabled"] = bool(data["mqtt_enabled"])
            if "mqtt_broker" in data:
                broker_value = data["mqtt_broker"]
                # Only validate broker if it's not empty
                if broker_value:
                    valid, err = _validate_host(broker_value)
                    if not valid:
                        return jsonify({"error": f"MQTT Broker: {err}"}), 400
                else:
                    # If broker is empty, automatically disable MQTT
                    config.data["mqtt"]["enabled"] = False
                config.data["mqtt"]["broker"] = broker_value
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
                valid, err = _validate_string(data["mqtt_username"], "MQTT Username")
                if not valid:
                    return jsonify({"error": err}), 400
                config.data["mqtt"]["username"] = data["mqtt_username"]
            if "mqtt_password" in data and data["mqtt_password"]:
                # Passwords can contain special chars, just limit length
                if len(data["mqtt_password"]) > _MAX_STRING_LENGTH:
                    return jsonify({"error": "MQTT Passwort zu lang"}), 400
                config.data["mqtt"]["password"] = data["mqtt_password"]
            if "mqtt_use_tls" in data:
                config.data["mqtt"]["use_tls"] = bool(data["mqtt_use_tls"])
            if "mqtt_tls_ca_cert" in data:
                # CA cert path validation
                valid, err = _validate_string(
                    data["mqtt_tls_ca_cert"], "TLS CA Cert Pfad"
                )
                if not valid:
                    return jsonify({"error": err}), 400
                config.data["mqtt"]["tls_ca_cert"] = data["mqtt_tls_ca_cert"]
            if "mqtt_topic_prefix" in data:
                valid, err = _validate_topic(data["mqtt_topic_prefix"])
                if not valid:
                    return jsonify({"error": f"MQTT Topic: {err}"}), 400
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

            # Telegram
            if "telegram_enabled" in data:
                config.data["telegram"]["enabled"] = bool(data["telegram_enabled"])
            if "telegram_bot_token" in data:
                # Skip if masked value "***" is sent back
                if data["telegram_bot_token"] and data["telegram_bot_token"] != "***":
                    config.data["telegram"]["bot_token"] = data["telegram_bot_token"]
            if "telegram_chat_ids" in data:
                chat_ids = data["telegram_chat_ids"]
                if isinstance(chat_ids, str):
                    chat_ids = [x.strip() for x in chat_ids.split(",") if x.strip()]
                config.data["telegram"]["chat_ids"] = chat_ids

            # Discord
            if "discord_enabled" in data:
                config.data["discord"]["enabled"] = bool(data["discord_enabled"])
            if "discord_webhook_url" in data:
                # Skip if masked value "***" is sent back
                if data["discord_webhook_url"] and data["discord_webhook_url"] != "***":
                    config.data["discord"]["webhook_url"] = data["discord_webhook_url"]

            # Email
            if "email_enabled" in data:
                config.data["email"]["enabled"] = bool(data["email_enabled"])
            if "email_smtp_server" in data:
                config.data["email"]["smtp_server"] = data["email_smtp_server"]
            if "email_smtp_port" in data:
                try:
                    port = int(data["email_smtp_port"])
                    if 1 <= port <= 65535:
                        config.data["email"]["smtp_port"] = port
                except ValueError:
                    return jsonify({"error": "Ungültiger SMTP Port"}), 400
            if "email_username" in data:
                config.data["email"]["username"] = data["email_username"]
            if "email_password" in data and data["email_password"]:
                config.data["email"]["password"] = data["email_password"]
            if "email_sender" in data:
                config.data["email"]["sender"] = data["email_sender"]
            if "email_recipients" in data:
                recipients = data["email_recipients"]
                if isinstance(recipients, str):
                    recipients = [x.strip() for x in recipients.split(",") if x.strip()]
                config.data["email"]["recipients"] = recipients

            # WebDAV
            if "webdav_enabled" in data:
                config.data["webdav"]["enabled"] = bool(data["webdav_enabled"])
            if "webdav_url" in data:
                config.data["webdav"]["url"] = data["webdav_url"]
            if "webdav_username" in data:
                config.data["webdav"]["username"] = data["webdav_username"]
            if "webdav_password" in data and data["webdav_password"]:
                config.data["webdav"]["password"] = data["webdav_password"]

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
                mode = data["updates_mode"]
                # Default to "apply" if invalid value
                if mode not in ["check", "apply"]:
                    mode = "apply"
                config.data["updates"]["mode"] = mode
            if "updates_target" in data:
                target = data["updates_target"]
                # Default to "all" if invalid value
                if target not in ["all", "major", "minor", "patch"]:
                    target = "all"
                config.data["updates"]["target"] = target
            if "updates_channel" in data:
                channel = data["updates_channel"]
                # Default to "latest" if invalid/empty value
                if channel not in ["latest", "beta", "release"]:
                    channel = "latest"
                config.data["updates"]["channel"] = channel

            # Backup
            if "backup_enabled" in data:
                if "backup" not in config.data:
                    config.data["backup"] = {}
                config.data["backup"]["enabled"] = bool(data["backup_enabled"])
            if "backup_interval" in data:
                if "backup" not in config.data:
                    config.data["backup"] = {}
                try:
                    interval = int(data["backup_interval"])
                    if 1 <= interval <= 168:
                        config.data["backup"]["interval"] = interval
                    else:
                        return jsonify({"error": "Backup Intervall ungültig"}), 400
                except ValueError:
                    return jsonify({"error": "Backup Intervall ungültig"}), 400
            if "backup_retention" in data:
                if "backup" not in config.data:
                    config.data["backup"] = {}
                try:
                    ret = int(data["backup_retention"])
                    if 1 <= ret <= 50:
                        config.data["backup"]["retention"] = ret
                    else:
                        return jsonify({"error": "Backup Anzahl ungültig"}), 400
                except ValueError:
                    return jsonify({"error": "Backup Anzahl ungültig"}), 400
            if "backup_auto_upload" in data:
                if "backup" not in config.data:
                    config.data["backup"] = {}
                config.data["backup"]["auto_upload"] = bool(data["backup_auto_upload"])

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

            # Data Sharing
            if "heatpump_model" in data:
                config.data["heatpump_model"] = data["heatpump_model"]
            if "share_data" in data:
                config.data["share_data"] = bool(data["share_data"])
            if "telemetry_auth_token" in data:
                # Skip if masked value "***" is sent back
                if data["telemetry_auth_token"] and data["telemetry_auth_token"] != "***":
                    config.data["telemetry_auth_token"] = data["telemetry_auth_token"]

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
        data = request.get_json() or {}
        docker_only = data.get("docker_only", False)

        # Check if any update method is available
        can_git = can_run_updates()
        can_docker = can_run_docker_updates()

        if not can_git and not can_docker:
            logger.warning("Update skipped: neither git repo nor docker available.")
            return jsonify(
                {
                    "success": False,
                    "error": "Update nicht möglich: Weder Git-Repository noch Docker verfügbar.",
                }
            ), 400

        update_method = "docker" if (docker_only or not can_git) else "git+docker"

        def do_update():
            try:
                time.sleep(2)
                run_update(docker_only=docker_only or not can_git)
            except Exception as e:
                logger.error(f"Update failed: {e}")

        threading.Thread(target=do_update, daemon=True).start()
        return jsonify(
            {"success": True, "message": "Update gestartet", "method": update_method}
        )
    except Exception as e:
        logger.error(f"Error starting update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/docker/status", methods=["GET"])
@login_required
def get_docker_status():
    """Get Docker image update status."""
    try:
        status = check_docker_updates()
        status["can_update"] = can_run_docker_updates()
        status["git_available"] = can_run_updates()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking Docker status: {e}")
        return jsonify({"error": str(e)}), 500


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


def validate_write(sensor_name, value, hp_id=None):
    if not heatpump_manager_instance:
        return False, "HeatpumpManager nicht verfügbar"

    if not hp_id:
        hp_id = get_default_heatpump_id()

    conn = heatpump_manager_instance.get_connection(hp_id)
    if not conn:
        return False, "Wärmepumpe nicht gefunden oder nicht verbunden"

    # Find sensor in connection sensors
    sensor = next((s for s in conn.sensors if s.id == sensor_name), None)

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
        hp_id = data.get("heatpump_id") or get_default_heatpump_id()

        valid, msg = validate_write(sensor_name, value, hp_id)
        if not valid:
            return jsonify({"error": msg}), 400

        try:
            if heatpump_manager_instance:
                _run_async(
                    heatpump_manager_instance.write_value(hp_id, sensor_name, value)
                )
                return jsonify(
                    {
                        "success": True,
                        "message": f"{value} erfolgreich auf {sensor_name} geschrieben",
                    }
                )
            else:
                return jsonify({"error": "HeatpumpManager nicht verfügbar"}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Get writable sensors for default HP (Legacy support)
    # New frontend should use /api/heatpumps/<hp_id> to get sensors
    writable_sensors = []
    if heatpump_manager_instance:
        hp_id = get_default_heatpump_id()
        conn = heatpump_manager_instance.get_connection(hp_id)
        if conn:
            for sensor in conn.sensors:
                if sensor.is_writable:
                    s_info = {
                        "name": sensor.name,
                        "unit": sensor.unit,
                        "description": "",
                        "features": "WRITE",  # Simplified
                        "min": sensor.min_value,
                        "max": sensor.max_value,
                        "enum": list(sensor.enum_values.items())
                        if sensor.enum_values
                        else None,
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
                if job and heatpump_manager_instance:
                    try:
                        hp_id = job.get("heatpump_id") or get_default_heatpump_id()
                        _run_async(
                            heatpump_manager_instance.write_value(
                                hp_id, job["sensor"], job["value"]
                            )
                        )
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
    if heatpump_manager_instance:
        try:
            hp_id = get_default_heatpump_id()
            conn = heatpump_manager_instance.get_connection(hp_id)
            if conn:
                for sensor in conn.sensors:
                    if sensor.is_writable:
                        s_info = {
                            "name": sensor.name,
                            "unit": sensor.unit,
                            "enum": list(sensor.enum_values.items())
                            if sensor.enum_values
                            else None,
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


@app.route("/api/backup/upload/<filename>", methods=["POST"])
@login_required
def upload_backup(filename):
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Ungültiger Dateiname"}), 400

    backup_path = Path(BACKUP_DIR) / filename
    if not backup_path.exists():
        return jsonify({"error": "Backup nicht gefunden"}), 404

    result = backup_manager.upload_to_webdav(str(backup_path))
    if result.get("success"):
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


# ============================================================================
# Annotations API
# ============================================================================


@app.route("/api/annotations", methods=["GET"])
@auth_or_token_required
def get_annotations():
    """Get all annotations or filter by dashboard and time range"""
    try:
        dashboard_id = request.args.get("dashboard_id")
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)

        if dashboard_id:
            annotations = annotation_manager.get_annotations_for_dashboard(dashboard_id)
        elif start and end:
            annotations = annotation_manager.get_annotations_for_time_range(
                start, end, dashboard_id
            )
        else:
            annotations = annotation_manager.get_all_annotations()

        return jsonify([a.to_dict() for a in annotations])
    except Exception as e:
        logger.error(f"Failed to get annotations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/annotations", methods=["POST"])
@login_required
def create_annotation():
    """Create a new annotation"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("text"):
            return jsonify({"error": "text is required"}), 400

        # Convert time to timestamp if provided as string
        time = data.get("time")
        if time and isinstance(time, str):
            from datetime import datetime

            time = int(datetime.fromisoformat(time.replace("Z", "+00:00")).timestamp())
        elif not time:
            from datetime import datetime

            time = int(datetime.now().timestamp())

        annotation = annotation_manager.add_annotation(
            time=time,
            text=data["text"],
            tags=data.get("tags", []),
            color=data.get("color", "#ef4444"),
            dashboard_id=data.get("dashboard_id"),
        )

        return jsonify(annotation.to_dict()), 201
    except Exception as e:
        logger.error(f"Failed to create annotation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/annotations/<annotation_id>", methods=["GET"])
@login_required
def get_annotation(annotation_id):
    """Get a specific annotation"""
    try:
        annotation = annotation_manager.get_annotation(annotation_id)
        if not annotation:
            return jsonify({"error": "Annotation not found"}), 404
        return jsonify(annotation.to_dict())
    except Exception as e:
        logger.error(f"Failed to get annotation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/annotations/<annotation_id>", methods=["PUT"])
@login_required
def update_annotation(annotation_id):
    """Update an annotation"""
    try:
        data = request.get_json()

        # Convert time to timestamp if provided as string
        time = data.get("time")
        if time and isinstance(time, str):
            from datetime import datetime

            time = int(datetime.fromisoformat(time.replace("Z", "+00:00")).timestamp())

        annotation = annotation_manager.update_annotation(
            annotation_id=annotation_id,
            time=time,
            text=data.get("text"),
            tags=data.get("tags"),
            color=data.get("color"),
        )

        if not annotation:
            return jsonify({"error": "Annotation not found"}), 404

        return jsonify(annotation.to_dict())
    except Exception as e:
        logger.error(f"Failed to update annotation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/annotations/<annotation_id>", methods=["DELETE"])
@login_required
def delete_annotation(annotation_id):
    """Delete an annotation"""
    try:
        success = annotation_manager.delete_annotation(annotation_id)
        if not success:
            return jsonify({"error": "Annotation not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Failed to delete annotation: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Variables API
# ============================================================================


@app.route("/api/variables", methods=["GET"])
@login_required
def get_variables():
    """Get all variables or values for a specific variable"""
    try:
        # Check if we need to fetch values for a specific variable
        variable_id = request.args.get("fetch_values_for")

        if variable_id:
            metrics_url = config.data.get("metrics", {}).get(
                "url", "http://victoriametrics:8428/write"
            )
            return jsonify(
                variable_manager.get_variable_values(variable_id, metrics_url)
            )
        else:
            # Return all variable definitions (without values)
            variables = variable_manager.get_all_variables()
            return jsonify([v.to_dict() for v in variables])
    except Exception as e:
        logger.error(f"Failed to get variables: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/variables", methods=["POST"])
@login_required
def create_variable():
    """Create a new variable"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("id") or not data.get("name") or not data.get("type"):
            return jsonify({"error": "id, name, and type are required"}), 400

        variable = variable_manager.add_variable(
            var_id=data["id"],
            name=data["name"],
            var_type=data["type"],
            query=data.get("query"),
            values=data.get("values"),
            default=data.get("default"),
            multi=data.get("multi", False),
            regex=data.get("regex"),
        )

        return jsonify(variable.to_dict()), 201
    except Exception as e:
        logger.error(f"Failed to create variable: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/variables/<variable_id>", methods=["GET"])
@login_required
def get_variable(variable_id):
    """Get a specific variable"""
    try:
        # Check if we need to fetch values
        if request.args.get("fetch_values"):
            metrics_url = config.data.get("metrics", {}).get(
                "url", "http://victoriametrics:8428/write"
            )
            return jsonify(
                variable_manager.get_variable_values(variable_id, metrics_url)
            )
        else:
            variable = variable_manager.get_variable(variable_id)
            if not variable:
                return jsonify({"error": "Variable not found"}), 404
            return jsonify(variable.to_dict())
    except Exception as e:
        logger.error(f"Failed to get variable: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/variables/<variable_id>", methods=["PUT"])
@login_required
def update_variable(variable_id):
    """Update a variable"""
    try:
        data = request.get_json()

        variable = variable_manager.update_variable(
            variable_id=variable_id,
            name=data.get("name"),
            type=data.get("type"),
            query=data.get("query"),
            values=data.get("values"),
            default=data.get("default"),
            multi=data.get("multi"),
            regex=data.get("regex"),
        )

        if not variable:
            return jsonify({"error": "Variable not found"}), 404

        return jsonify(variable.to_dict())
    except Exception as e:
        logger.error(f"Failed to update variable: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/variables/<variable_id>", methods=["DELETE"])
@login_required
def delete_variable(variable_id):
    """Delete a variable"""
    try:
        success = variable_manager.delete_variable(variable_id)
        if not success:
            return jsonify({"error": "Variable not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Failed to delete variable: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/variables/substitute", methods=["POST"])
@login_required
def substitute_variables():
    """
    Substitute variables in a query string.

    Request body:
    {
        "query": "temp_{circuit}_current",
        "variables": {"circuit": "A"}
    }

    Returns:
    {
        "result": "temp_A_current"
    }
    """
    try:
        data = request.get_json()
        query = data.get("query", "")
        variables = data.get("variables", {})

        result = variable_manager.substitute_variables(query, variables)
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"Failed to substitute variables: {e}")
        return jsonify({"error": str(e)}), 500


def set_metrics_writer(writer):
    global metrics_writer_instance
    metrics_writer_instance = writer


# ============================================================================
# Sharing API
# ============================================================================


@app.route("/api/sharing/tokens", methods=["GET"])
@login_required
def get_share_tokens():
    """Get all share tokens or tokens for a specific dashboard."""
    try:
        dashboard_id = request.args.get("dashboard_id")

        if dashboard_id:
            tokens = sharing_manager.get_tokens_for_dashboard(dashboard_id)
        else:
            tokens = sharing_manager.get_all_tokens()

        return jsonify([token.to_dict() for token in tokens])
    except Exception as e:
        logger.error(f"Failed to get share tokens: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sharing/tokens", methods=["POST"])
@login_required
def create_share_token():
    """Create a new share token for a dashboard."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("dashboard_id"):
            return jsonify({"error": "dashboard_id is required"}), 400

        from flask import session

        created_by = session.get("user", "anonymous")

        token = sharing_manager.create_share_token(
            dashboard_id=data["dashboard_id"],
            created_by=created_by,
            expires_in_days=data.get("expires_in_days"),
            password=data.get("password"),
            is_public=data.get("is_public", False),
        )

        return jsonify(token.to_dict()), 201
    except Exception as e:
        logger.error(f"Failed to create share token: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sharing/tokens/<token_id>", methods=["GET"])
def get_share_token(token_id):
    """Get a share token by ID (no auth required for accessing)."""
    try:
        token = sharing_manager.get_token(token_id)
        if not token:
            return jsonify({"error": "Token not found"}), 404

        # Record access
        sharing_manager.record_access(token_id)

        return jsonify(token.to_dict())
    except Exception as e:
        logger.error(f"Failed to get share token: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sharing/tokens/<token_id>", methods=["DELETE"])
@login_required
def delete_share_token(token_id):
    """Delete a share token."""
    try:
        if sharing_manager.delete_token(token_id):
            return jsonify({"status": "success", "message": "Token deleted"})
        else:
            return jsonify({"error": "Token not found"}), 404
    except Exception as e:
        logger.error(f"Failed to delete share token: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sharing/tokens/<token_id>/validate", methods=["POST"])
def validate_share_token(token_id):
    """Validate a share token with optional password."""
    try:
        data = request.get_json() or {}
        password = data.get("password")

        is_valid = sharing_manager.validate_token(token_id, password)

        if is_valid:
            token = sharing_manager.get_token(token_id)
            sharing_manager.record_access(token_id)
            return jsonify({"valid": True, "dashboard_id": token.dashboard_id})
        else:
            return jsonify({"valid": False, "error": "Invalid or expired token"}), 401
    except Exception as e:
        logger.error(f"Failed to validate share token: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/shared/<token_id>")
def view_shared_dashboard(token_id):
    """View a shared dashboard."""
    try:
        token = sharing_manager.get_token(token_id)
        if not token:
            return "Shared dashboard not found", 404

        if token.is_expired():
            return "Shared dashboard has expired", 410

        # Get dashboard
        dashboard = dashboard_manager.get_dashboard(token.dashboard_id)
        if not dashboard:
            return "Dashboard not found", 404

        # Check if password protected
        if not token.is_public and token.password_hash:
            # Render password prompt
            return send_from_directory("frontend", "index.html")

        # Render dashboard in view-only mode
        return send_from_directory("frontend", "index.html")
    except Exception as e:
        logger.error(f"Failed to view shared dashboard: {e}")
        return "Error loading shared dashboard", 500


@app.route("/api/sharing/dashboard/<token_id>", methods=["GET"])
def get_shared_dashboard_data(token_id):
    """Get dashboard configuration via share token."""
    try:
        # Get password from header
        password = request.headers.get("X-Share-Password")

        # Validate token
        if not sharing_manager.validate_token(token_id, password):
            # Check if it's just missing password for a protected token
            token = sharing_manager.get_token(token_id)
            if (
                token
                and not token.is_expired()
                and token.password_hash
                and not password
            ):
                return jsonify(
                    {"error": "Password required", "require_password": True}
                ), 401
            return jsonify({"error": "Invalid or expired token"}), 403

        token = sharing_manager.get_token(token_id)

        # Get dashboard
        dashboard = dashboard_manager.get_dashboard(token.dashboard_id)
        if not dashboard:
            return jsonify({"error": "Dashboard not found"}), 404

        # Record access
        sharing_manager.record_access(token_id)

        return jsonify(dashboard)
    except Exception as e:
        logger.error(f"Failed to get shared dashboard data: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Multi-Heatpump API ====================
# These endpoints support managing multiple heat pumps


def _run_async(coro):
    """Run an async coroutine from sync Flask context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route("/api/heatpumps", methods=["GET"])
@login_required
def list_heatpumps():
    """
    List all configured heat pumps.
    ---
    tags:
      - Heatpumps
    responses:
      200:
        description: List of heat pumps with status
    """
    from .db import db

    heatpumps = db.get_heatpumps()

    # Add connection status if manager is available
    if heatpump_manager_instance:
        status_map = {s["id"]: s for s in heatpump_manager_instance.get_status()}
        for hp in heatpumps:
            if hp["id"] in status_map:
                hp.update(
                    {
                        "connected": status_map[hp["id"]].get("connected", False),
                        "error_count": status_map[hp["id"]].get("error_count", 0),
                        "last_error": status_map[hp["id"]].get("last_error"),
                    }
                )
            else:
                hp["connected"] = False

    return jsonify(heatpumps)


@app.route("/api/heatpumps", methods=["POST"])
@login_required
def add_heatpump():
    """
    Add a new heat pump.
    ---
    tags:
      - Heatpumps
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
            - manufacturer
            - model
            - connection
          properties:
            name:
              type: string
            manufacturer:
              type: string
            model:
              type: string
            connection:
              type: object
            config:
              type: object
    responses:
      201:
        description: Heat pump created
      400:
        description: Invalid request
    """
    data = request.get_json()

    # Validate required fields
    required = ["name", "manufacturer", "model", "connection"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Fehlende Felder: {', '.join(missing)}"}), 400

    # Validate connection
    conn = data.get("connection", {})
    if not conn.get("host"):
        return jsonify({"error": "Host ist erforderlich"}), 400

    valid, err = _validate_host(conn["host"])
    if not valid:
        return jsonify({"error": err}), 400

    # Validate manufacturer/model
    if not ManufacturerRegistry.is_supported(data["manufacturer"], data["model"]):
        return jsonify(
            {"error": f"Nicht unterstützt: {data['manufacturer']}/{data['model']}"}
        ), 400

    try:
        if heatpump_manager_instance:
            hp_id = _run_async(heatpump_manager_instance.add_heatpump(data))
        else:
            # Fallback to direct DB insert
            from .db import db

            hp_id = db.add_heatpump(
                {
                    "name": data["name"],
                    "manufacturer": data["manufacturer"],
                    "model": data["model"],
                    "connection_config": data.get("connection", {}),
                    "device_config": data.get("config", {}),
                    "enabled": data.get("enabled", True),
                }
            )

        return jsonify({"id": hp_id, "message": "Wärmepumpe hinzugefügt"}), 201

    except Exception as e:
        logger.error(f"Failed to add heatpump: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/heatpumps/<hp_id>", methods=["GET"])
@login_required
def get_heatpump(hp_id):
    """
    Get details of a specific heat pump.
    ---
    tags:
      - Heatpumps
    parameters:
      - name: hp_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Heat pump details
      404:
        description: Not found
    """
    from .db import db

    hp = db.get_heatpump(hp_id)
    if not hp:
        return jsonify({"error": "Nicht gefunden"}), 404

    # Add capabilities
    driver = ManufacturerRegistry.get_driver(hp["manufacturer"], hp["model"])
    if driver:
        hp["capabilities"] = driver.get_capabilities().to_dict()
        hp["setup_instructions"] = driver.get_setup_instructions()

    # Add connection status
    if heatpump_manager_instance:
        info = heatpump_manager_instance.get_heatpump_info(hp_id)
        if info:
            hp["connected"] = info.get("connected", False)
            hp["sensors"] = info.get("sensors", [])
            hp["last_values"] = info.get("last_values", {})

    return jsonify(hp)


@app.route("/api/heatpumps/<hp_id>", methods=["PUT"])
@login_required
def update_heatpump(hp_id):
    """
    Update a heat pump configuration.
    ---
    tags:
      - Heatpumps
    """
    from .db import db

    data = request.get_json()

    # Validate connection if provided
    if "connection" in data or "connection_config" in data:
        conn = data.get("connection") or data.get("connection_config", {})
        if conn.get("host"):
            valid, err = _validate_host(conn["host"])
            if not valid:
                return jsonify({"error": err}), 400

    try:
        # Normalize field names
        update_fields = {}
        if "name" in data:
            update_fields["name"] = data["name"]
        if "connection" in data:
            update_fields["connection_config"] = data["connection"]
        if "connection_config" in data:
            update_fields["connection_config"] = data["connection_config"]
        if "config" in data:
            update_fields["device_config"] = data["config"]
        if "device_config" in data:
            update_fields["device_config"] = data["device_config"]
        if "enabled" in data:
            update_fields["enabled"] = data["enabled"]

        db.update_heatpump(hp_id, update_fields)

        # Reconnect if connection changed
        if heatpump_manager_instance and (
            "connection_config" in update_fields or "device_config" in update_fields
        ):
            _run_async(heatpump_manager_instance.reconnect(hp_id))

        return jsonify({"message": "Aktualisiert"})

    except Exception as e:
        logger.error(f"Failed to update heatpump {hp_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/heatpumps/<hp_id>", methods=["DELETE"])
@login_required
def delete_heatpump(hp_id):
    """
    Delete a heat pump.
    ---
    tags:
      - Heatpumps
    """
    try:
        if heatpump_manager_instance:
            _run_async(heatpump_manager_instance.remove_heatpump(hp_id))
        else:
            from .db import db

            db.delete_heatpump(hp_id)

        return jsonify({"message": "Wärmepumpe entfernt"})

    except Exception as e:
        logger.error(f"Failed to delete heatpump {hp_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/heatpumps/<hp_id>/test", methods=["POST"])
@login_required
def test_heatpump_connection(hp_id):
    """
    Test connection to a heat pump.
    ---
    tags:
      - Heatpumps
    """
    from .db import db
    from pymodbus.client import ModbusTcpClient

    hp = db.get_heatpump(hp_id)
    if not hp:
        return jsonify({"error": "Nicht gefunden"}), 404

    conn = hp.get("connection_config", {})
    host = conn.get("host")
    port = conn.get("port", 502)

    if not host:
        return jsonify({"success": False, "message": "Kein Host konfiguriert"})

    try:
        client = ModbusTcpClient(host=host, port=port, timeout=5)
        connected = client.connect()

        if connected:
            # Try to read a test register
            result = client.read_holding_registers(1000, count=2, slave=1)
            client.close()

            if result.isError():
                return jsonify(
                    {
                        "success": False,
                        "message": f"Verbunden, aber Lesefehler: {result}",
                    }
                )

            return jsonify(
                {"success": True, "message": f"Erfolgreich verbunden mit {host}:{port}"}
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": f"Verbindung zu {host}:{port} fehlgeschlagen",
                }
            )

    except Exception as e:
        return jsonify({"success": False, "message": f"Verbindungsfehler: {str(e)}"})


@app.route("/api/heatpumps/<hp_id>/enable", methods=["POST"])
@login_required
def enable_heatpump(hp_id):
    """
    Enable or disable a heat pump.
    ---
    tags:
      - Heatpumps
    """
    data = request.get_json() or {}
    enabled = data.get("enabled", True)

    try:
        if heatpump_manager_instance:
            _run_async(heatpump_manager_instance.enable_heatpump(hp_id, enabled))
        else:
            from .db import db

            db.update_heatpump(hp_id, {"enabled": enabled})

        status = "aktiviert" if enabled else "deaktiviert"
        return jsonify({"message": f"Wärmepumpe {status}"})

    except Exception as e:
        logger.error(f"Failed to enable/disable heatpump {hp_id}: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Manufacturer API ====================


@app.route("/api/manufacturers", methods=["GET"])
def list_manufacturers():
    """
    List all supported manufacturers and models.
    ---
    tags:
      - Manufacturers
    responses:
      200:
        description: List of manufacturers with their models
    """
    return jsonify(ManufacturerRegistry.list_manufacturers())


@app.route("/api/manufacturers/<mfr>/models/<model>/setup", methods=["GET"])
def get_model_setup(mfr, model):
    """
    Get setup instructions for a specific model.
    ---
    tags:
      - Manufacturers
    """
    driver = ManufacturerRegistry.get_driver(mfr, model)
    if not driver:
        return jsonify({"error": "Nicht gefunden"}), 404

    return jsonify(
        {
            "manufacturer": mfr,
            "model": model,
            "display_name": driver.DISPLAY_NAME,
            "protocol": driver.PROTOCOL,
            "default_port": driver.DEFAULT_PORT,
            "capabilities": driver.get_capabilities().to_dict(),
            "instructions": driver.get_setup_instructions(),
            "dashboard_template": driver.get_dashboard_template(),
        }
    )


# ==================== Multi-Device Data API ====================


@app.route("/api/data/all", methods=["GET"])
def get_all_heatpump_data():
    """
    Get current data from all heat pumps.
    ---
    tags:
      - Data
    responses:
      200:
        description: Data from all heat pumps
    """
    if not heatpump_manager_instance:
        return jsonify({"error": "HeatpumpManager nicht initialisiert"}), 503

    try:
        data = _run_async(heatpump_manager_instance.read_all())
        return jsonify(data)
    except Exception as e:
        logger.error(f"Failed to read all heatpumps: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/<hp_id>", methods=["GET"])
def get_heatpump_data(hp_id):
    """
    Get current data from a specific heat pump.
    ---
    tags:
      - Data
    """
    if not heatpump_manager_instance:
        return jsonify({"error": "HeatpumpManager nicht initialisiert"}), 503

    try:
        data = _run_async(heatpump_manager_instance.read_heatpump(hp_id))
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to read heatpump {hp_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/control/<hp_id>", methods=["POST"])
@login_required
def control_heatpump(hp_id):
    """
    Write a value to a heat pump sensor.
    ---
    tags:
      - Control
    """
    if not config.get("web.write_enabled", False):
        return jsonify({"error": "Schreibzugriff ist deaktiviert"}), 403

    data = request.get_json()
    sensor = data.get("sensor")
    value = data.get("value")

    if not sensor:
        return jsonify({"error": "Sensor fehlt"}), 400

    if value is None:
        return jsonify({"error": "Wert fehlt"}), 400

    try:
        if heatpump_manager_instance:
            success = _run_async(
                heatpump_manager_instance.write_value(hp_id, sensor, value)
            )
            if success:
                return jsonify({"message": f"{sensor} auf {value} gesetzt"})
            else:
                return jsonify({"error": "Schreibfehler"}), 500
        else:
            return jsonify({"error": "HeatpumpManager nicht initialisiert"}), 503

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to write to {hp_id}/{sensor}: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Multi-Device Dashboard API ====================


@app.route("/api/dashboards/heatpump/<hp_id>", methods=["GET"])
def get_heatpump_dashboards(hp_id):
    """
    Get all dashboards for a specific heat pump.
    ---
    tags:
      - Dashboards
    """
    from .db import db

    dashboards = db.get_dashboards(heatpump_id=hp_id)
    return jsonify(dashboards)


# ==================== End Multi-Heatpump API ====================


def run_web(heatpump_manager, scheduler):
    global scheduler_instance, heatpump_manager_instance
    scheduler_instance = scheduler
    heatpump_manager_instance = heatpump_manager

    # Run migration on startup
    run_migration()

    # Start background tasks
    _start_ai_status_thread()

    if config.get("web.enabled"):
        host = config.get("web.host", "0.0.0.0")
        port = config.get("web.port", 5000)

        # Check if WebSocket is enabled
        websocket_enabled = config.get("web.websocket_enabled", True)

        try:
            if websocket_enabled:
                logger.info(
                    f"Starting web server with WebSocket support on {host}:{port}"
                )
                # Use socketio.run for WebSocket support
                # Note: For production, use gunicorn with eventlet or gunicorn with --worker-class socketio.GunicornWorker
                socketio.run(
                    app,
                    host=host,
                    port=port,
                    allow_unsafe_werkzeug=True,  # Required for WebSocket with Werkzeug
                )
            else:
                logger.info(
                    f"Starting production web server (Waitress) on {host}:{port}"
                )
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
