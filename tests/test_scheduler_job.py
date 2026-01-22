# SPDX-License-Identifier: MIT
import json
import sqlite3
import pytest
from idm_logger.scheduler import Job

class TestSchedulerJob:
    def test_job_from_dict(self):
        data = {
            "id": "1",
            "sensor": "temp",
            "value": 20,
            "time": "12:00",
            "days": ["Mon"],
            "enabled": True,
            "last_run": 100.0
        }
        job = Job(data)

        # Test properties
        assert job.id == "1"
        assert job.sensor == "temp"
        assert job.value == 20
        assert job.time == "12:00"
        assert job.days == ["Mon"]
        assert job.enabled is True
        assert job.last_run == 100.0

        # Test dict-like access
        assert job["id"] == "1"
        assert job.get("sensor") == "temp"
        assert job.get("days") == ["Mon"]

        # Test mutable update
        job.update({"last_run": 200.0})
        assert job.last_run == 200.0
        assert job.get("last_run") == 200.0

    def test_job_from_row(self):
        # Create a mock row using sqlite3
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE jobs (id, sensor, value, time, days, enabled, last_run)")
        cursor.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)",
                       ("2", "hum", "50", "13:00", '["Fri"]', 1, 0))
        cursor.execute("SELECT * FROM jobs")
        row = cursor.fetchone()

        job = Job(row)

        # Test properties
        assert job.id == "2"
        assert job.sensor == "hum"
        assert job.days == ["Fri"]
        assert job.last_run == 0

        # Test dict-like access
        assert job["id"] == "2"

        # Test mutable update (should convert to dict internally)
        job.update({"last_run": 300.0})
        assert job.last_run == 300.0

        # Test days update
        job["days"] = ["Sat"]
        assert job.days == ["Sat"]

        # Test setting unknown key (upgrades to dict)
        job["new_key"] = "test"
        assert job["new_key"] == "test"
