# SPDX-License-Identifier: MIT
import sqlite3
import logging
import os
import json
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Whitelisted column names for SQL injection prevention
ALLOWED_JOB_COLUMNS = frozenset({"sensor", "value", "time", "days", "enabled", "last_run"})
ALLOWED_ALERT_COLUMNS = frozenset({
    "name", "type", "sensor", "condition", "threshold",
    "message", "enabled", "interval_seconds", "last_triggered"
})

# Use DATA_DIR environment variable or current directory for persistence
DATA_DIR = os.environ.get("DATA_DIR", ".")
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
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise

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
                    "INSERT INTO jobs (id, sensor, value, time, days, enabled, last_run) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        job["id"],
                        job["sensor"],
                        str(job["value"]),
                        job["time"],
                        json.dumps(job["days"]),
                        int(job["enabled"]),
                        job.get("last_run", 0),
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
                        logger.warning(f"Rejected invalid column name in job update: {k}")
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
                       (id, name, type, sensor, condition, threshold, message, enabled, interval_seconds, last_triggered)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                        logger.warning(f"Rejected invalid column name in alert update: {k}")
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


db = Database()
