import sqlite3
import logging
import os
import json
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Use DATA_DIR environment variable or current directory for persistence
DATA_DIR = os.environ.get("DATA_DIR", ".")
DB_PATH = os.path.join(DATA_DIR, "idm_logger.db")

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        # Thread lock to ensure safe concurrent access
        self._lock = threading.RLock()
        self.init_db()

    def get_connection(self):
        """Get a new database connection with row factory."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

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
            finally:
                conn.close()

    def init_db(self):
        """Initialize database tables."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()

                # Settings table (key, value)
                # Value stored as TEXT. Complex objects stored as JSON string.
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')

                # Jobs table for scheduler
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        sensor TEXT,
                        value TEXT,
                        time TEXT,
                        days TEXT,
                        enabled INTEGER,
                        last_run REAL
                    )
                ''')
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
                return row['value'] if row else default
        except sqlite3.Error as e:
            logger.error(f"Failed to get setting '{key}': {e}")
            return default

    def set_setting(self, key, value):
        """Set a setting value in database."""
        try:
            with self._get_locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
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
                rows = cursor.fetchall()
                jobs = []
                for row in rows:
                    job = dict(row)
                    # Decode days from JSON if necessary, or store as comma separated string
                    # We'll assume stored as JSON string or handle conversion in scheduler
                    jobs.append(job)
                return jobs
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
                    (job['id'], job['sensor'], str(job['value']), job['time'], json.dumps(job['days']), int(job['enabled']), job.get('last_run', 0))
                )
            logger.info(f"Job {job['id']} added successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to add job {job.get('id', 'unknown')}: {e}", exc_info=True)
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
                # fields is dict
                query_parts = []
                values = []
                for k, v in fields.items():
                    query_parts.append(f"{k}=?")
                    if k == 'days':
                        values.append(json.dumps(v))
                    elif k == 'enabled':
                        values.append(int(v))
                    else:
                        values.append(v)

                values.append(job_id)
                query = f"UPDATE jobs SET {', '.join(query_parts)} WHERE id=?"
                cursor.execute(query, tuple(values))
            logger.debug(f"Job {job_id} updated successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to update job {job_id}: {e}", exc_info=True)
            raise

db = Database()
