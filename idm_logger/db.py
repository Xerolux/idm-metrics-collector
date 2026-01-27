# SPDX-License-Identifier: MIT
import sqlite3
import logging
import os
import json
import threading
import time
import uuid
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database schema version for migrations
SCHEMA_VERSION = 2  # Version 2 adds multi-heatpump support

# Whitelisted column names for SQL injection prevention
ALLOWED_JOB_COLUMNS = frozenset(
    {"sensor", "value", "time", "days", "enabled", "last_run", "heatpump_id"}
)
ALLOWED_ALERT_COLUMNS = frozenset(
    {
        "name",
        "type",
        "sensor",
        "condition",
        "threshold",
        "message",
        "enabled",
        "interval_seconds",
        "last_triggered",
        "heatpump_id",
    }
)
ALLOWED_HEATPUMP_COLUMNS = frozenset(
    {
        "name",
        "manufacturer",
        "model",
        "connection_config",
        "device_config",
        "enabled",
    }
)

# Use DATA_DIR environment variable or current directory for persistence
DATA_DIR = os.environ.get("DATA_DIR", ".")

# Support in-memory database for testing
TESTING = os.environ.get("TESTING", "").lower() in ("1", "true", "yes")
if TESTING:
    DB_PATH = ":memory:"
else:
    DB_PATH = os.path.join(DATA_DIR, "idm_logger.db")


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        # Thread lock to ensure safe concurrent access
        self._lock = threading.RLock()
        self._conn = None
        self.init_db()

    def get_connection(self):
        """Get the persistent database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path, check_same_thread=False, timeout=10.0
            )
            self._conn.row_factory = sqlite3.Row
        return self._conn

    @contextmanager
    def _get_locked_connection(self):
        """Context manager for thread-safe database operations."""
        with self._lock:
            conn = self.get_connection()
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def init_db(self):
        """Initialize database tables."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()

                # Settings table (key, value)
                # Value stored as TEXT. Complex objects stored as JSON string.
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)

                # Jobs table for scheduler
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        sensor TEXT,
                        value TEXT,
                        time TEXT,
                        days TEXT,
                        enabled INTEGER,
                        last_run REAL
                    )
                """)

                # Alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        type TEXT,
                        sensor TEXT,
                        condition TEXT,
                        threshold TEXT,
                        message TEXT,
                        enabled INTEGER,
                        interval_seconds INTEGER,
                        last_triggered REAL
                    )
                """)

                # Heatpumps table for multi-device support (v2)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS heatpumps (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        manufacturer TEXT NOT NULL,
                        model TEXT NOT NULL,
                        connection_config TEXT NOT NULL,
                        device_config TEXT DEFAULT '{}',
                        enabled INTEGER DEFAULT 1,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)

                # Dashboards table for per-device dashboards (v2)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dashboards (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        heatpump_id TEXT,
                        config TEXT NOT NULL,
                        position INTEGER DEFAULT 0,
                        created_at REAL NOT NULL,
                        FOREIGN KEY (heatpump_id) REFERENCES heatpumps(id)
                            ON DELETE CASCADE
                    )
                """)

                # Performance: Create indexes for frequently queried columns
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_jobs_enabled ON jobs(enabled)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_jobs_sensor ON jobs(sensor)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_alerts_enabled ON alerts(enabled)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_alerts_sensor ON alerts(sensor)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_heatpumps_enabled ON heatpumps(enabled)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_dashboards_heatpump ON dashboards(heatpump_id)"
                )

                # Run migrations
                self._run_migrations(cursor)

            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise

    def _run_migrations(self, cursor):
        """Run database migrations to update schema."""
        # Get current schema version
        cursor.execute("SELECT value FROM settings WHERE key='schema_version'")
        row = cursor.fetchone()
        current_version = int(row["value"]) if row else 1

        if current_version < SCHEMA_VERSION:
            logger.info(
                f"Migrating database from v{current_version} to v{SCHEMA_VERSION}"
            )

            # Migration v1 -> v2: Add heatpump_id to jobs and alerts
            if current_version < 2:
                self._migrate_v1_to_v2(cursor)

            # Update schema version
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION)),
            )
            logger.info(f"Database migration completed to v{SCHEMA_VERSION}")

    def _migrate_v1_to_v2(self, cursor):
        """
        Migration from v1 to v2: Add multi-heatpump support.

        Changes:
        - Add heatpump_id column to jobs table
        - Add heatpump_id column to alerts table
        - Create legacy heatpump entry from existing config
        """
        logger.info("Running migration v1 -> v2: Adding multi-heatpump support")

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(jobs)")
        job_columns = [col[1] for col in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(alerts)")
        alert_columns = [col[1] for col in cursor.fetchall()]

        # Add heatpump_id to jobs if not exists
        if "heatpump_id" not in job_columns:
            cursor.execute("ALTER TABLE jobs ADD COLUMN heatpump_id TEXT DEFAULT NULL")
            logger.debug("Added heatpump_id column to jobs table")

        # Add heatpump_id to alerts if not exists
        if "heatpump_id" not in alert_columns:
            cursor.execute(
                "ALTER TABLE alerts ADD COLUMN heatpump_id TEXT DEFAULT NULL"
            )
            logger.debug("Added heatpump_id column to alerts table")

        # Create index for heatpump_id columns
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_heatpump ON jobs(heatpump_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alerts_heatpump ON alerts(heatpump_id)"
        )

    def get_setting(self, key, default=None):
        """Get a setting value from database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
                row = cursor.fetchone()
                return row["value"] if row else default
        except sqlite3.Error as e:
            logger.error(f"Failed to get setting '{key}': {e}")
            return default

    def set_setting(self, key, value):
        """Set a setting value in database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, value),
                )
            logger.debug(f"Setting '{key}' updated")
        except sqlite3.Error as e:
            logger.error(f"Failed to set setting '{key}': {e}", exc_info=True)
            raise

    # Helpers for jobs
    def get_jobs(self):
        """Get all scheduled jobs from database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM jobs")
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve jobs: {e}", exc_info=True)
            return []

    def add_job(self, job):
        """Add a new scheduled job to database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO jobs (id, sensor, value, time, days, enabled, last_run, heatpump_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        job["id"],
                        job["sensor"],
                        str(job["value"]),
                        job["time"],
                        json.dumps(job["days"]),
                        int(job["enabled"]),
                        job.get("last_run", 0),
                        job.get("heatpump_id"),
                    ),
                )
            logger.info(f"Job {job['id']} added successfully")
        except sqlite3.Error as e:
            logger.error(
                f"Failed to add job {job.get('id', 'unknown')}: {e}", exc_info=True
            )
            raise

    def delete_job(self, job_id):
        """Delete a scheduled job from database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            logger.info(f"Job {job_id} deleted successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete job {job_id}: {e}", exc_info=True)
            raise

    def update_job(self, job_id, fields):
        """Update a scheduled job in database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                # fields is dict - validate column names against whitelist
                query_parts = []
                values = []
                for k, v in fields.items():
                    # Security: Only allow whitelisted column names
                    if k not in ALLOWED_JOB_COLUMNS:
                        logger.warning(
                            f"Rejected invalid column name in job update: {k}"
                        )
                        continue
                    query_parts.append(f"{k}=?")
                    if k == "days":
                        values.append(json.dumps(v))
                    elif k == "enabled":
                        values.append(int(v))
                    else:
                        values.append(v)

                if not query_parts:
                    logger.warning(f"No valid fields to update for job {job_id}")
                    return

                values.append(job_id)
                query = f"UPDATE jobs SET {', '.join(query_parts)} WHERE id=?"
                cursor.execute(query, tuple(values))
            logger.debug(f"Job {job_id} updated successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to update job {job_id}: {e}", exc_info=True)
            raise

    def update_jobs_last_run(self, updates):
        """
        Batch update last_run for multiple jobs.
        updates: list of (job_id, last_run_timestamp)
        """
        if not updates:
            return
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    "UPDATE jobs SET last_run=? WHERE id=?",
                    [(ts, jid) for jid, ts in updates],
                )
            logger.debug(f"Updated last_run for {len(updates)} jobs")
        except sqlite3.Error as e:
            logger.error(f"Failed to batch update jobs: {e}", exc_info=True)
            raise

    # Helpers for alerts
    def get_alerts(self):
        """Get all alerts from database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM alerts")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve alerts: {e}", exc_info=True)
            return []

    def add_alert(self, alert):
        """Add a new alert to database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO alerts
                       (id, name, type, sensor, condition, threshold, message, enabled, interval_seconds, last_triggered, heatpump_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        alert["id"],
                        alert["name"],
                        alert["type"],
                        alert.get("sensor"),
                        alert.get("condition"),
                        str(alert.get("threshold")),
                        alert["message"],
                        int(alert["enabled"]),
                        alert.get("interval_seconds", 0),
                        alert.get("last_triggered", 0),
                        alert.get("heatpump_id"),
                    ),
                )
            logger.info(f"Alert {alert['id']} added successfully")
        except sqlite3.Error as e:
            logger.error(
                f"Failed to add alert {alert.get('id', 'unknown')}: {e}", exc_info=True
            )
            raise

    def delete_alert(self, alert_id):
        """Delete an alert from database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
            logger.info(f"Alert {alert_id} deleted successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete alert {alert_id}: {e}", exc_info=True)
            raise

    def update_alert(self, alert_id, fields):
        """Update an alert in database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                # Validate column names against whitelist
                query_parts = []
                values = []
                for k, v in fields.items():
                    # Security: Only allow whitelisted column names
                    if k not in ALLOWED_ALERT_COLUMNS:
                        logger.warning(
                            f"Rejected invalid column name in alert update: {k}"
                        )
                        continue
                    query_parts.append(f"{k}=?")
                    if k == "enabled":
                        values.append(int(v))
                    else:
                        values.append(v)

                if not query_parts:
                    logger.warning(f"No valid fields to update for alert {alert_id}")
                    return

                values.append(alert_id)
                query = f"UPDATE alerts SET {', '.join(query_parts)} WHERE id=?"
                cursor.execute(query, tuple(values))
            logger.debug(f"Alert {alert_id} updated successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to update alert {alert_id}: {e}", exc_info=True)
            raise

    def update_alerts_last_triggered(self, alert_ids, timestamp):
        """Update the last_triggered timestamp for multiple alerts."""
        if not alert_ids:
            return
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                placeholders = ",".join("?" for _ in alert_ids)
                query = (
                    f"UPDATE alerts SET last_triggered=? WHERE id IN ({placeholders})"
                )
                params = [timestamp] + alert_ids
                cursor.execute(query, tuple(params))
            logger.debug(f"Updated last_triggered for {len(alert_ids)} alerts.")
        except sqlite3.Error as e:
            logger.error(f"Failed to bulk update alerts: {e}", exc_info=True)
            raise

    # ==================== Heatpump CRUD Operations ====================

    def get_heatpumps(self):
        """Get all configured heatpumps."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM heatpumps ORDER BY created_at")
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    hp = dict(row)
                    # Parse JSON fields
                    hp["connection_config"] = json.loads(
                        hp.get("connection_config", "{}")
                    )
                    hp["device_config"] = json.loads(hp.get("device_config", "{}"))
                    hp["enabled"] = bool(hp.get("enabled", 1))
                    result.append(hp)
                return result
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve heatpumps: {e}", exc_info=True)
            return []

    def get_heatpump(self, hp_id):
        """Get a single heatpump by ID."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM heatpumps WHERE id=?", (hp_id,))
                row = cursor.fetchone()
                if row:
                    hp = dict(row)
                    hp["connection_config"] = json.loads(
                        hp.get("connection_config", "{}")
                    )
                    hp["device_config"] = json.loads(hp.get("device_config", "{}"))
                    hp["enabled"] = bool(hp.get("enabled", 1))
                    return hp
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get heatpump {hp_id}: {e}", exc_info=True)
            return None

    def add_heatpump(self, heatpump):
        """Add a new heatpump."""
        try:
            hp_id = heatpump.get("id") or f"hp-{uuid.uuid4().hex[:8]}"
            now = time.time()

            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO heatpumps
                       (id, name, manufacturer, model, connection_config, device_config, enabled, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        hp_id,
                        heatpump["name"],
                        heatpump["manufacturer"],
                        heatpump["model"],
                        json.dumps(heatpump.get("connection_config", {})),
                        json.dumps(heatpump.get("device_config", {})),
                        int(heatpump.get("enabled", True)),
                        now,
                        now,
                    ),
                )
            logger.info(f"Heatpump {hp_id} ({heatpump['name']}) added successfully")
            return hp_id
        except sqlite3.Error as e:
            logger.error(f"Failed to add heatpump: {e}", exc_info=True)
            raise

    def update_heatpump(self, hp_id, fields):
        """Update a heatpump's configuration."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                query_parts = ["updated_at=?"]
                values = [time.time()]

                for k, v in fields.items():
                    if k not in ALLOWED_HEATPUMP_COLUMNS:
                        logger.warning(
                            f"Rejected invalid column in heatpump update: {k}"
                        )
                        continue

                    query_parts.append(f"{k}=?")
                    if k in ("connection_config", "device_config"):
                        values.append(json.dumps(v))
                    elif k == "enabled":
                        values.append(int(v))
                    else:
                        values.append(v)

                if len(query_parts) == 1:
                    logger.warning(f"No valid fields to update for heatpump {hp_id}")
                    return

                values.append(hp_id)
                query = f"UPDATE heatpumps SET {', '.join(query_parts)} WHERE id=?"
                cursor.execute(query, tuple(values))
            logger.info(f"Heatpump {hp_id} updated successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to update heatpump {hp_id}: {e}", exc_info=True)
            raise

    def delete_heatpump(self, hp_id):
        """Delete a heatpump and its associated data."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                # Delete associated dashboards (CASCADE should handle this, but be explicit)
                cursor.execute("DELETE FROM dashboards WHERE heatpump_id=?", (hp_id,))
                # Nullify heatpump_id in jobs and alerts (keep them but unlink)
                cursor.execute(
                    "UPDATE jobs SET heatpump_id=NULL WHERE heatpump_id=?", (hp_id,)
                )
                cursor.execute(
                    "UPDATE alerts SET heatpump_id=NULL WHERE heatpump_id=?", (hp_id,)
                )
                # Delete the heatpump
                cursor.execute("DELETE FROM heatpumps WHERE id=?", (hp_id,))
            logger.info(f"Heatpump {hp_id} deleted successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete heatpump {hp_id}: {e}", exc_info=True)
            raise

    def get_enabled_heatpumps(self):
        """Get all enabled heatpumps."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM heatpumps WHERE enabled=1 ORDER BY created_at"
                )
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    hp = dict(row)
                    hp["connection_config"] = json.loads(
                        hp.get("connection_config", "{}")
                    )
                    hp["device_config"] = json.loads(hp.get("device_config", "{}"))
                    hp["enabled"] = True
                    result.append(hp)
                return result
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve enabled heatpumps: {e}", exc_info=True)
            return []

    # ==================== Dashboard CRUD Operations ====================

    def get_dashboards(self, heatpump_id=None):
        """Get all dashboards, optionally filtered by heatpump_id."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                if heatpump_id:
                    cursor.execute(
                        "SELECT * FROM dashboards WHERE heatpump_id=? ORDER BY position",
                        (heatpump_id,),
                    )
                else:
                    cursor.execute("SELECT * FROM dashboards ORDER BY position")
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    dash = dict(row)
                    dash["config"] = json.loads(dash.get("config", "{}"))
                    result.append(dash)
                return result
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve dashboards: {e}", exc_info=True)
            return []

    def get_dashboard(self, dash_id):
        """Get a single dashboard by ID."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM dashboards WHERE id=?", (dash_id,))
                row = cursor.fetchone()
                if row:
                    dash = dict(row)
                    dash["config"] = json.loads(dash.get("config", "{}"))
                    return dash
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get dashboard {dash_id}: {e}", exc_info=True)
            return None

    def add_dashboard(self, dashboard):
        """Add a new dashboard."""
        try:
            dash_id = dashboard.get("id") or f"dash-{uuid.uuid4().hex[:8]}"
            now = time.time()

            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO dashboards
                       (id, name, heatpump_id, config, position, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        dash_id,
                        dashboard["name"],
                        dashboard.get("heatpump_id"),
                        json.dumps(dashboard.get("config", {})),
                        dashboard.get("position", 0),
                        now,
                    ),
                )
            logger.info(f"Dashboard {dash_id} added successfully")
            return dash_id
        except sqlite3.Error as e:
            logger.error(f"Failed to add dashboard: {e}", exc_info=True)
            raise

    def update_dashboard(self, dash_id, fields):
        """Update a dashboard."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                query_parts = []
                values = []

                allowed = {"name", "heatpump_id", "config", "position"}
                for k, v in fields.items():
                    if k not in allowed:
                        continue
                    query_parts.append(f"{k}=?")
                    if k == "config":
                        values.append(json.dumps(v))
                    else:
                        values.append(v)

                if not query_parts:
                    return

                values.append(dash_id)
                query = f"UPDATE dashboards SET {', '.join(query_parts)} WHERE id=?"
                cursor.execute(query, tuple(values))
            logger.debug(f"Dashboard {dash_id} updated")
        except sqlite3.Error as e:
            logger.error(f"Failed to update dashboard {dash_id}: {e}", exc_info=True)
            raise

    def delete_dashboard(self, dash_id):
        """Delete a dashboard."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dashboards WHERE id=?", (dash_id,))
            logger.info(f"Dashboard {dash_id} deleted")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete dashboard {dash_id}: {e}", exc_info=True)
            raise

    def delete_dashboards_for_heatpump(self, heatpump_id):
        """Delete all dashboards for a specific heatpump."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM dashboards WHERE heatpump_id=?", (heatpump_id,)
                )
            logger.info(f"Deleted dashboards for heatpump {heatpump_id}")
        except sqlite3.Error as e:
            logger.error(
                f"Failed to delete dashboards for {heatpump_id}: {e}", exc_info=True
            )
            raise

    # ==================== Filtered queries with heatpump_id ====================

    def get_jobs_for_heatpump(self, heatpump_id):
        """Get all jobs for a specific heatpump."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM jobs WHERE heatpump_id=? OR heatpump_id IS NULL",
                    (heatpump_id,),
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to get jobs for heatpump {heatpump_id}: {e}")
            return []

    def get_alerts_for_heatpump(self, heatpump_id):
        """Get all alerts for a specific heatpump."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM alerts WHERE heatpump_id=? OR heatpump_id IS NULL",
                    (heatpump_id,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get alerts for heatpump {heatpump_id}: {e}")
            return []


db = Database()
