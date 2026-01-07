import threading
import time
import logging
import yaml
import os
import datetime

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, modbus_client, schedule_file="schedule.yaml"):
        self.modbus_client = modbus_client
        self.schedule_file = schedule_file
        self.jobs = []
        self.lock = threading.Lock()
        self.running = False
        self.load()

    def load(self):
        with self.lock:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r') as f:
                    try:
                        self.jobs = yaml.safe_load(f) or []
                    except yaml.YAMLError as e:
                        logger.error(f"Failed to load schedule: {e}")
            else:
                self.jobs = []

    def save(self):
        with self.lock:
            with open(self.schedule_file, 'w') as f:
                yaml.dump(self.jobs, f)

    def add_job(self, job):
        with self.lock:
            job['id'] = str(int(time.time() * 1000)) # Simple ID
            if 'enabled' not in job:
                job['enabled'] = True
            self.jobs.append(job)
        self.save()

    def delete_job(self, job_id):
        with self.lock:
            self.jobs = [j for j in self.jobs if j.get('id') != job_id]
        self.save()

    def update_job(self, job_id, new_data):
         with self.lock:
            for job in self.jobs:
                if job.get('id') == job_id:
                    job.update(new_data)
                    break
         self.save()

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
                current_day = now.strftime("%a") # Mon, Tue, ...

                with self.lock:
                    for job in self.jobs:
                        if not job.get('enabled'):
                            continue

                        # Check days
                        days = job.get('days', [])
                        if days and current_day not in days:
                            continue

                        # Check time
                        if job.get('time') == current_time:
                            # To avoid re-triggering within the same minute, we track last run?
                            # Or simpler: The loop sleeps 60s. But it might drift.
                            # Better: Track last_run timestamp in job (in memory)
                            last_run = job.get('last_run')
                            # If run within last 65 seconds
                            if last_run and (time.time() - last_run) < 65:
                                continue

                            logger.info(f"Executing scheduled job: {job.get('sensor')} = {job.get('value')}")
                            try:
                                self.modbus_client.write_sensor(job.get('sensor'), job.get('value'))
                                job['last_run'] = time.time()
                            except Exception as e:
                                logger.error(f"Scheduled job failed: {e}")

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

            # Align to next minute start
            sleep_time = 60 - time.time() % 60
            time.sleep(sleep_time)
