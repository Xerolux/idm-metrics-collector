# SPDX-License-Identifier: MIT
import threading
import time
import logging
import json
import datetime
from .db import db

logger = logging.getLogger(__name__)


class MutableRow:
    """Wrapper around sqlite3.Row (or dict) to allow mutation."""

    __slots__ = ("_row", "_overrides")

    def __init__(self, row):
        self._row = row
        self._overrides = None

    def __getitem__(self, key):
        if self._overrides and key in self._overrides:
            return self._overrides[key]
        return self._row[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except (IndexError, KeyError):
            return default

    def __setitem__(self, key, value):
        if self._overrides is None:
            self._overrides = {}
        self._overrides[key] = value

    def update(self, other):
        if self._overrides is None:
            self._overrides = {}
        self._overrides.update(other)

    def __iter__(self):
        # Merge keys from row and overrides
        keys = set(self._row.keys())
        if self._overrides:
            keys.update(self._overrides.keys())
        return iter(keys)

    def __len__(self):
        keys = set(self._row.keys())
        if self._overrides:
            keys.update(self._overrides.keys())
        return len(keys)

    def keys(self):
        return list(self)

    def items(self):
        return [(k, self[k]) for k in self]

    def values(self):
        return [self[k] for k in self]

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self)})"


class Scheduler:
    def __init__(self, modbus_client):
        self.modbus_client = modbus_client
        self.jobs = []
        self.lock = threading.Lock()
        self.running = False
        self.load()

    def load(self):
        with self.lock:
            self.jobs = [MutableRow(row) for row in db.get_jobs()]
            # Convert JSON string days to list
            for job in self.jobs:
                if isinstance(job.get("days"), str):
                    try:
                        job["days"] = json.loads(job["days"])
                    except (json.JSONDecodeError, ValueError, TypeError):
                        job["days"] = []
                        logger.warning(
                            f"Failed to parse days for job {job.get('id')}, defaulting to empty list"
                        )

    def add_job(self, job):
        with self.lock:
            job["id"] = str(int(time.time() * 1000))
            if "enabled" not in job:
                job["enabled"] = True

            # DB insert
            db.add_job(job)

            # Update memory
            self.jobs.append(job)

    def delete_job(self, job_id):
        with self.lock:
            db.delete_job(job_id)
            self.jobs = [j for j in self.jobs if j.get("id") != job_id]

    def update_job(self, job_id, new_data):
        with self.lock:
            db.update_job(job_id, new_data)
            for job in self.jobs:
                if job.get("id") == job_id:
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
            self.process_jobs()
            sleep_time = 60 - time.time() % 60
            time.sleep(sleep_time)

    def process_jobs(self):
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = now.strftime("%a")

            updates = []

            with self.lock:
                for job in self.jobs:
                    if not job.get("enabled"):
                        continue

                    days = job.get("days", [])
                    if days and current_day not in days:
                        continue

                    if job.get("time") == current_time:
                        last_run = job.get("last_run")
                        if last_run and (time.time() - last_run) < 65:
                            continue

                        logger.info(
                            f"Executing scheduled job: {job.get('sensor')} = {job.get('value')}"
                        )
                        try:
                            self.modbus_client.write_sensor(
                                job.get("sensor"), job.get("value")
                            )
                            # Update last run in Memory
                            now_ts = time.time()
                            job["last_run"] = now_ts
                            # Collect for batch DB update
                            updates.append((job["id"], now_ts))
                        except Exception as e:
                            logger.error(f"Scheduled job failed: {e}")

            # Batch update DB outside the loop (but still essentially part of the process)
            if updates:
                db.update_jobs_last_run(updates)

        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
