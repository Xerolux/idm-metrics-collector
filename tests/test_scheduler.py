import unittest
from unittest.mock import MagicMock, patch
import datetime
from idm_logger.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.modbus_mock = MagicMock()
        # Patch db.db used in scheduler
        self.db_patcher = patch("idm_logger.scheduler.db")
        self.mock_db = self.db_patcher.start()

        self.scheduler = Scheduler(self.modbus_mock)
        # Clear jobs loaded from mock db
        self.scheduler.jobs = []

    def tearDown(self):
        self.db_patcher.stop()

    def test_process_jobs_batching(self):
        # Use a fixed time for testing to avoid day mismatch issues
        fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0)  # A Monday
        current_time = fixed_now.strftime("%H:%M")
        current_day = fixed_now.strftime("%a")

        # Add 3 jobs that should run
        for i in range(3):
            job = {
                "id": f"job_{i}",
                "sensor": f"sensor_{i}",
                "value": i,
                "time": current_time,
                "days": [current_day],
                "enabled": True,
                "last_run": 0,
            }
            self.scheduler.jobs.append(job)

        # Add a job that should NOT run (wrong time)
        wrong_time_job = {
            "id": "job_skip",
            "sensor": "sensor_skip",
            "value": 1,
            "time": "25:00",  # Invalid time, won't match
            "days": [current_day],
            "enabled": True,
            "last_run": 0,
        }
        self.scheduler.jobs.append(wrong_time_job)

        # Run process_jobs
        with patch("idm_logger.scheduler.datetime") as mock_datetime:
            mock_datetime.datetime.now.return_value = fixed_now
            # We also need to mock time.time() because the scheduler uses it for last_run check
            with patch("idm_logger.scheduler.time.time") as mock_time:
                mock_time.return_value = 100000  # Fixed timestamp

                self.scheduler.process_jobs()

        # Verify modbus writes
        self.assertEqual(self.modbus_mock.write_sensor.call_count, 3)

        # Verify db.update_jobs_last_run was called once with 3 updates
        self.mock_db.update_jobs_last_run.assert_called_once()
        args, _ = self.mock_db.update_jobs_last_run.call_args
        updates = args[0]
        self.assertEqual(len(updates), 3)

        # Check job IDs in updates
        updated_ids = {u[0] for u in updates}
        self.assertEqual(updated_ids, {"job_0", "job_1", "job_2"})

        # Check that jobs in memory were updated
        for i in range(3):
            self.assertTrue(self.scheduler.jobs[i]["last_run"] > 0)

        self.assertEqual(self.scheduler.jobs[3]["last_run"], 0)

    def test_process_jobs_no_updates(self):
        # No jobs
        self.scheduler.process_jobs()
        self.mock_db.update_jobs_last_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
