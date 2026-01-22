
import unittest
from unittest.mock import MagicMock, patch
import json
import sqlite3
from idm_logger.scheduler import Scheduler, MutableRow

class TestSchedulerRowHandling(unittest.TestCase):
    def setUp(self):
        self.modbus_mock = MagicMock()
        # Patch db.db used in scheduler
        self.db_patcher = patch("idm_logger.scheduler.db")
        self.mock_db = self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()

    def test_load_handles_rows_and_mutability(self):
        # Create a real sqlite3.Row object to simulate DB return
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE jobs (id TEXT, sensor TEXT, value TEXT, days TEXT, last_run REAL, enabled INTEGER, time TEXT)")

        days_json = json.dumps(["Mon", "Fri"])
        cursor.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)",
                       ("job1", "sensor1", "20", days_json, 0, 1, "12:00"))

        cursor.execute("SELECT * FROM jobs")
        row = cursor.fetchone()

        # Mock get_jobs to return this row
        self.mock_db.get_jobs.return_value = [row]

        # Init scheduler (calls load)
        scheduler = Scheduler(self.modbus_mock)

        # Verify jobs loaded
        self.assertEqual(len(scheduler.jobs), 1)
        job = scheduler.jobs[0]

        # Verify it is wrapped in MutableRow
        self.assertIsInstance(job, MutableRow)

        # Verify access
        self.assertEqual(job["id"], "job1")
        self.assertEqual(job.get("sensor"), "sensor1")

        # Verify days were decoded (mutated)
        self.assertEqual(job["days"], ["Mon", "Fri"])

        # Verify we can mutate other fields (simulate last_run update)
        job["last_run"] = 12345.6
        self.assertEqual(job["last_run"], 12345.6)

        # Verify original row is untouched (optional, but good to know)
        self.assertEqual(row["last_run"], 0)

    def test_mixed_inputs(self):
        # Scheduler might have jobs from DB (Rows) and jobs added via API (dicts)

        # 1. DB Row
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE jobs (id TEXT, sensor TEXT, value TEXT, days TEXT, last_run REAL, enabled INTEGER, time TEXT)")
        days_json = json.dumps(["Mon"])
        cursor.execute("INSERT INTO jobs VALUES ('db_job', 's1', '10', ?, 0, 1, '10:00')", (days_json,))
        cursor.execute("SELECT * FROM jobs")
        row = cursor.fetchone()

        self.mock_db.get_jobs.return_value = [row]

        scheduler = Scheduler(self.modbus_mock)

        # 2. Add API job (dict)
        api_job = {
            "sensor": "s2",
            "value": "20",
            "time": "11:00",
            "days": ["Tue"],
            "enabled": True
        }
        # Mock add_job side effects
        def mock_add_job(j):
            pass
        self.mock_db.add_job.side_effect = mock_add_job

        scheduler.add_job(api_job)

        self.assertEqual(len(scheduler.jobs), 2)

        job1 = scheduler.jobs[0] # From DB
        job2 = scheduler.jobs[1] # From API

        self.assertIsInstance(job1, MutableRow)
        self.assertIsInstance(job2, dict)

        # Verify uniform access
        self.assertEqual(job1["id"], "db_job")
        self.assertEqual(job2["sensor"], "s2")

        # Verify process_jobs handles both
        # We simulate process_jobs logic by iterating and accessing
        for job in scheduler.jobs:
            _ = job.get("sensor")
            _ = job.get("days")
            if job.get("enabled"):
                job["last_run"] = 1000

        self.assertEqual(job1["last_run"], 1000)
        self.assertEqual(job2["last_run"], 1000)

    def test_mutable_row_dict_interface(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE t (a TEXT, b INTEGER)")
        cursor.execute("INSERT INTO t VALUES ('test', 1)")
        cursor.execute("SELECT * FROM t")
        row = cursor.fetchone()

        mr = MutableRow(row)

        # Test len
        self.assertEqual(len(mr), 2)

        # Test keys
        keys = list(mr.keys())
        self.assertIn('a', keys)
        self.assertIn('b', keys)

        # Test items
        items = dict(mr.items())
        self.assertEqual(items['a'], 'test')
        self.assertEqual(items['b'], 1)

        # Test mutation affects keys/items/len
        mr['c'] = 3
        self.assertEqual(len(mr), 3)
        self.assertIn('c', mr.keys())
        self.assertEqual(dict(mr)['c'], 3)

        # Test override existing
        mr['b'] = 99
        self.assertEqual(mr['b'], 99)
        self.assertEqual(dict(mr)['b'], 99)

        # Test repr
        r = repr(mr)
        self.assertIn("'a': 'test'", r)
        self.assertIn("'c': 3", r)

if __name__ == "__main__":
    unittest.main()
