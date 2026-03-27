# Xerolux 2026
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib

sys.path.insert(0, os.getcwd())


class TestMlRatio(unittest.TestCase):
    def setUp(self):
        self.mock_torch = MagicMock()
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "torch": self.mock_torch,
                "torch.nn": MagicMock(),
                "torch.nn.Module": MagicMock,
                "schedule": MagicMock(),
                "joblib": MagicMock(),
                "flask": MagicMock(),
            },
        )
        self.modules_patcher.start()
        self.addCleanup(self.modules_patcher.stop)

        self.env_patcher = patch.dict(
            os.environ,
            {
                "METRICS_URL": "http://test-vm",
                "MIN_DATA_RATIO": "0.4",
                "MODEL_PATH": "/tmp/test_model.pkl",
                "WARMUP_UPDATES": "5",
                "ALARM_CONSECUTIVE_HITS": "3",
                "IDM_LOGGER_URL": "http://test-logger",
            },
        )
        self.env_patcher.start()
        self.addCleanup(self.env_patcher.stop)

        import ml_service.config as ml_config
        import ml_service.main as ml_main

        importlib.reload(ml_config)
        importlib.reload(ml_main)
        self.ml_main = ml_main
        self.ml_config = ml_config

        self.ml_main.logger = MagicMock()

    @patch("ml_service.main.fetch_latest_data")
    @patch("ml_service.main.write_metrics")
    def test_job_proceeds_even_if_insufficient_data(self, mock_write, mock_fetch):
        original_sensors = self.ml_main.SENSORS
        self.ml_main.SENSORS = [
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
        ]

        mock_fetch.return_value = {"s1": 1.0, "s2": 1.0, "s3": 1.0}

        original_ratio = self.ml_config.config.min_data_ratio
        self.ml_config.config.min_data_ratio = 0.4

        self.ml_main.job()

        self.ml_main.logger.warning.assert_called()
        found_warning = False
        for call in self.ml_main.logger.warning.call_args_list:
            msg = call[0][0]
            if "Low data availability" in msg and "Proceeding anyway" in msg:
                found_warning = True
                break

        self.assertTrue(found_warning, "Should log 'Low data availability' warning")
        mock_write.assert_called()

        self.ml_main.SENSORS = original_sensors
        self.ml_config.config.min_data_ratio = original_ratio

    @patch("ml_service.main.fetch_latest_data")
    @patch("ml_service.main.write_metrics")
    def test_job_proceeds_if_sufficient_data(self, mock_write, mock_fetch):
        original_sensors = self.ml_main.SENSORS
        self.ml_main.SENSORS = [
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
        ]
        original_ratio = self.ml_config.config.min_data_ratio
        self.ml_config.config.min_data_ratio = 0.4

        mock_fetch.return_value = {"s1": 1.0, "s2": 1.0, "s3": 1.0, "s4": 1.0}

        self.ml_main.job()

        mock_write.assert_called()

        self.ml_main.SENSORS = original_sensors
        self.ml_config.config.min_data_ratio = original_ratio


if __name__ == "__main__":
    unittest.main()
