import importlib
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.getcwd())


class TestMLSync(unittest.TestCase):
    def setUp(self):
        self.mock_torch = MagicMock()
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "torch": self.mock_torch,
                "torch.nn": MagicMock(),
                "schedule": MagicMock(),
                "joblib": MagicMock(),
            },
        )
        self.modules_patcher.start()
        self.addCleanup(self.modules_patcher.stop)

        self.env_patcher = patch.dict(
            os.environ,
            {
                "ANOMALY_THRESHOLD": "0.85",
                "IDM_LOGGER_URL": "http://test-logger",
                "INTERNAL_API_KEY": "test-key",
                "CUDA_VISIBLE_DEVICES": "",
                "METRICS_URL": "http://test-vm",
                "MODEL_PATH": "/tmp/test_model.pkl",
            },
        )
        self.env_patcher.start()
        self.addCleanup(self.env_patcher.stop)

        try:
            import ml_service.config as ml_config
            import ml_service.main as ml_main

            importlib.reload(ml_config)
            importlib.reload(ml_main)
            self.ml_main = ml_main
            self.ml_config = ml_config
        except ImportError as e:
            print(f"ImportError: {e}")
            sys.exit(1)

        self.ml_config.config.anomaly_threshold = 0.85
        self.ml_main.logger.setLevel(logging.CRITICAL)

    def tearDown(self):
        pass

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensitivity": 5.0, "threshold": 0.85}
        mock_get.return_value = mock_response

        self.ml_main.fetch_remote_config()

        self.assertAlmostEqual(self.ml_config.config.anomaly_threshold, 0.85, places=3)

        mock_get.assert_called_with(
            "http://test-logger/api/internal/ml_config",
            headers={"X-Internal-Secret": "test-key"},
            timeout=2,
        )

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        self.ml_main.fetch_remote_config()

        self.assertEqual(self.ml_config.config.anomaly_threshold, 0.85)

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_exception(self, mock_get):
        mock_get.side_effect = Exception("Connection error")

        self.ml_main.fetch_remote_config()

        self.assertEqual(self.ml_config.config.anomaly_threshold, 0.85)

    @patch("ml_service.main.fetch_remote_config")
    @patch("ml_service.main.fetch_latest_data")
    def test_job_calls_fetch_config(self, mock_fetch_data, mock_fetch_config):
        mock_fetch_data.return_value = None

        self.ml_main.job()

        mock_fetch_config.assert_called_once()


if __name__ == "__main__":
    unittest.main()
