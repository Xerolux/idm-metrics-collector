# SPDX-License-Identifier: MIT
"""Tests for scheduler functionality."""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import datetime
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import helper from conftest
from conftest import create_mock_db_module


class TestScheduler(unittest.TestCase):
    def setUp(self):
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        self.hp_manager_mock = MagicMock()
        self.hp_manager_mock.write_value = AsyncMock()

        # Create properly configured mock db module
        self.mock_db_module = create_mock_db_module()
        self.mock_db = self.mock_db_module.db
        self.mock_db.get_jobs.return_value = []

        # Patch modules before importing scheduler
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": self.mock_db_module,
            },
        )
        self.modules_patcher.start()

        # Now import Scheduler
        from idm_logger.scheduler import Scheduler

        self.Scheduler = Scheduler
        self.scheduler = Scheduler(self.hp_manager_mock)
        # Clear jobs loaded from mock db
        self.scheduler.jobs = []

    def tearDown(self):
        self.modules_patcher.stop()
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

    def test_process_jobs_batching(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_day = datetime.datetime.now().strftime("%a")

        # Patch asyncio.run to avoid event loop issues and verify calls
        # Also temporarily replace write_value with MagicMock to avoid unawaited coroutine warnings
        # (since asyncio.run is mocked, it won't await the result of write_value)
        self.hp_manager_mock.write_value = MagicMock()

        with patch("asyncio.run") as mock_asyncio_run:
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

            # Verify asyncio.run was called (which calls write_value)
            self.assertEqual(mock_asyncio_run.call_count, 3)

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
