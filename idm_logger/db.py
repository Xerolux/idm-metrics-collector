import sqlite3
import logging
import os
import json

logger = logging.getLogger(__name__)

DB_PATH = "idm_logger.db"

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
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

        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default

    def set_setting(self, key, value):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

    # Helpers for jobs
    def get_jobs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()
        jobs = []
        for row in rows:
            job = dict(row)
            # Decode days from JSON if necessary, or store as comma separated string
            # We'll assume stored as JSON string or handle conversion in scheduler
            jobs.append(job)
        conn.close()
        return jobs

    def add_job(self, job):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jobs (id, sensor, value, time, days, enabled, last_run) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (job['id'], job['sensor'], str(job['value']), job['time'], json.dumps(job['days']), int(job['enabled']), job.get('last_run', 0))
        )
        conn.commit()
        conn.close()

    def delete_job(self, job_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
        conn.commit()
        conn.close()

    def update_job(self, job_id, fields):
        conn = self.get_connection()
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
        conn.commit()
        conn.close()

db = Database()
