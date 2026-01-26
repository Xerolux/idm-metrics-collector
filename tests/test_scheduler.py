import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import datetime
from idm_logger.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.hp_manager_mock = MagicMock()
        self.hp_manager_mock.write_value = AsyncMock()

        # Patch db.db used in scheduler
        self.db_patcher = patch("idm_logger.scheduler.db")
        self.mock_db = self.db_patcher.start()

        # Patch migration default id
        self.migration_patcher = patch("idm_logger.scheduler.get_default_heatpump_id")
        self.mock_get_default_id = self.migration_patcher.start()
        self.mock_get_default_id.return_value = "hp-legacy"

        self.scheduler = Scheduler(self.hp_manager_mock)
        # Clear jobs loaded from mock db
        self.scheduler.jobs = []

    def tearDown(self):
        self.db_patcher.stop()
        self.migration_patcher.stop()

    def test_process_jobs_batching(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_day = datetime.datetime.now().strftime("%a")

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
                "heatpump_id": "hp-1",
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
        self.scheduler.process_jobs()

        # Verify modbus writes
        self.assertEqual(self.hp_manager_mock.write_value.call_count, 3)

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
