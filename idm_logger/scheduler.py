# SPDX-License-Identifier: MIT
import threading
import time
import logging
import json
import datetime
import sqlite3
from .db import db

logger = logging.getLogger(__name__)


class Job:
    __slots__ = ('_data', 'days', 'last_run')

    def __init__(self, data):
        self._data = data
        # Handle mutable days list (from JSON string or list)
        # sqlite3.Row supports string index access
        try:
            d = data["days"]
        except (KeyError, IndexError):
            d = []

        if isinstance(d, str):
            try:
                self.days = json.loads(d)
            except (json.JSONDecodeError, ValueError, TypeError):
                self.days = []
        else:
            self.days = d if d else []

        try:
            self.last_run = data["last_run"]
        except (KeyError, IndexError):
            self.last_run = 0

    # Read-only properties
    @property
    def id(self):
        return self._data["id"]

    @property
    def sensor(self):
        return self._data["sensor"]

    @property
    def value(self):
        return self._data["value"]

    @property
    def time(self):
        return self._data["time"]

    @property
    def enabled(self):
        return self._data["enabled"]

    def get(self, key, default=None):
        """Compatibility with dict-like access for scheduler logic."""
        if key == "days":
            return self.days
        if key == "last_run":
            return self.last_run

        # Check standard properties
        if key == "id": return self.id
        if key == "sensor": return self.sensor
        if key == "value": return self.value
        if key == "time": return self.time
        if key == "enabled": return self.enabled

        # Fallback to underlying data if dict, or default if Row
        try:
            return self._data[key]
        except (KeyError, IndexError):
            return default

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        if key == "days":
            self.days = value
        elif key == "last_run":
            self.last_run = value
        else:
            # If we need to set other keys, we must upgrade to dict
            self._ensure_mutable()
            self._data[key] = value

    def update(self, new_data):
        """Update mutable fields or underlying data."""
        # Check if we are updating handled mutable fields
        handled = set(["days", "last_run"])

        for k, v in new_data.items():
            if k == "days":
                self.days = v
            elif k == "last_run":
                self.last_run = v
            else:
                # Need to update underlying data
                self._ensure_mutable()
                self._data[k] = v

    def _ensure_mutable(self):
        """Convert underlying sqlite3.Row to dict if needed."""
        if isinstance(self._data, sqlite3.Row):
            self._data = dict(self._data)


class Scheduler:
    def __init__(self, modbus_client):
        self.modbus_client = modbus_client
        self.jobs = []
        self.lock = threading.Lock()
        self.running = False
        self.load()

    def load(self):
        with self.lock:
            # db.get_jobs now returns sqlite3.Row objects (list of rows)
            rows = db.get_jobs()
            self.jobs = [Job(row) for row in rows]

    def add_job(self, job_data):
        with self.lock:
            job_data["id"] = str(int(time.time() * 1000))
            if "enabled" not in job_data:
                job_data["enabled"] = True

            # DB insert
            db.add_job(job_data)

            # Update memory - Wrap the dict in Job
            self.jobs.append(Job(job_data))

    def delete_job(self, job_id):
        with self.lock:
            db.delete_job(job_id)
            self.jobs = [j for j in self.jobs if j.id != job_id]

    def update_job(self, job_id, new_data):
        with self.lock:
            db.update_job(job_id, new_data)
            for job in self.jobs:
                if job.id == job_id:
                    job.update(new_data)
                    break

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        logger.info("Scheduler started")
        while self.running:
            try:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M")
                current_day = now.strftime("%a")

                with self.lock:
                    for job in self.jobs:
                        if not job.enabled:
                            continue

                        days = job.days
                        if days and current_day not in days:
                            continue

                        if job.time == current_time:
                            last_run = job.last_run
                            if last_run and (time.time() - last_run) < 65:
                                continue

                            logger.info(
                                f"Executing scheduled job: {job.sensor} = {job.value}"
                            )
                            try:
                                self.modbus_client.write_sensor(
                                    job.sensor, job.value
                                )
                                # Update last run in DB and Memory
                                now_ts = time.time()

                                # Update memory object (optimized)
                                job.last_run = now_ts

                                # Update DB (async/separate)
                                db.update_job(job.id, {"last_run": now_ts})
                            except Exception as e:
                                logger.error(f"Scheduled job failed: {e}")

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

            sleep_time = 60 - time.time() % 60
            time.sleep(sleep_time)
