import threading
import time
import logging
import json
import datetime
from .db import db

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, modbus_client):
        self.modbus_client = modbus_client
        self.jobs = []
        self.lock = threading.Lock()
        self.running = False
        self.load()

    def load(self):
        with self.lock:
            self.jobs = db.get_jobs()
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
            try:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M")
                current_day = now.strftime("%a")

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
                                # Update last run in DB and Memory
                                now_ts = time.time()
                                job["last_run"] = now_ts
                                db.update_job(job["id"], {"last_run": now_ts})
                            except Exception as e:
                                logger.error(f"Scheduled job failed: {e}")

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

            sleep_time = 60 - time.time() % 60
            time.sleep(sleep_time)
