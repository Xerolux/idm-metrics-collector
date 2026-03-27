# Xerolux 2026
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import importlib
import pickle
from idm_logger.const import HeatPumpStatus

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestMLServiceLogic(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ,
            {
                "METRICS_URL": "http://test-vm",
                "MIN_DATA_RATIO": "0.4",
                "MODEL_PATH": "/tmp/test_model.pkl",
                "WARMUP_UPDATES": "5",
                "ALARM_CONSECUTIVE_HITS": "3",
                "IDM_LOGGER_URL": "http://test-logger",
                "INTERNAL_API_KEY": "test-key",
            },
        )
        self.env_patcher.start()

        if "torch" not in sys.modules:
            self.torch_patcher = patch.dict(
                sys.modules,
                {
                    "torch": MagicMock(),
                    "torch.nn": MagicMock(),
                    "torch.nn.Module": MagicMock,
                },
            )
            self.torch_patcher.start()
        else:
            self.torch_patcher = None

        try:
            import ml_service.main as main
            import ml_service.config as ml_config

            importlib.reload(ml_config)
            importlib.reload(main)
            self.main = main
        except ImportError:
            self.skipTest("ML Service dependencies not met")

        self.main.SENSORS = ["sensor1", "sensor2", "status_heat_pump"]
        self.main.models = {
            "heating": MagicMock(),
            "cooling": MagicMock(),
            "water": MagicMock(),
            "standby": MagicMock(),
        }
        for mode_model in self.main.models.values():
            mode_model.scaler = MagicMock()
            mode_model.scaler.means = {}
            mode_model.scaler.vars = {}
            mode_model.steps = {}
        self.main.logger = MagicMock()
        self.main.last_data_points = {}
        self.main.consecutive_anomalies = {}
        self.main.update_counter = 0
        self.main.model_trained = False

    def tearDown(self):
        self.env_patcher.stop()
        if self.torch_patcher:
            self.torch_patcher.stop()

    def test_determine_mode(self):
        data = {"status_heat_pump": HeatPumpStatus.HEATING.value}
        self.assertEqual(self.main.determine_mode(data), "heating")

        data = {"status_heat_pump": HeatPumpStatus.COOLING.value}
        self.assertEqual(self.main.determine_mode(data), "cooling")

        data = {
            "status_heat_pump": HeatPumpStatus.HEATING.value
            | HeatPumpStatus.DEFROSTING.value
        }
        self.assertEqual(self.main.determine_mode(data), "defrost")

        data = {"status_heat_pump": 0}
        self.assertEqual(self.main.determine_mode(data), "standby")

    def test_feature_engineering_delta(self):
        data1 = {"sensor1": 10.0, "status_heat_pump": 0}
        res1 = self.main.enrich_features(data1)
        self.assertNotIn("sensor1_delta", res1)

        data2 = {"sensor1": 15.0, "status_heat_pump": 0}
        res2 = self.main.enrich_features(data2)
        self.assertEqual(res2["sensor1_delta"], 5.0)

    def test_job_flow(self):
        with (
            patch.object(self.main, "fetch_latest_data") as mock_fetch,
            patch.object(self.main, "write_metrics") as mock_write,
            patch.object(self.main, "send_anomaly_alert") as mock_alert,
        ):
            mock_fetch.return_value = {
                "sensor1": 10.0,
                "status_heat_pump": HeatPumpStatus.HEATING.value,
            }
            self.main.models["heating"].score_one.return_value = 0.1
            self.main.models["heating"].steps = {}

            self.main.job()

            self.main.models["heating"].learn_one.assert_called()
            mock_write.assert_called()
            args, _ = mock_write.call_args
            self.assertEqual(args[4], "heating")
            mock_alert.assert_not_called()

    def test_debounce_logic(self):
        with (
            patch.object(self.main, "fetch_latest_data") as mock_fetch,
            patch.object(self.main, "write_metrics"),
            patch.object(self.main, "send_anomaly_alert") as mock_alert,
            patch.object(self.main, "get_top_features", return_value=[]),
        ):
            mock_fetch.return_value = {
                "sensor1": 10.0,
                "status_heat_pump": HeatPumpStatus.HEATING.value,
            }
            self.main.models["heating"].score_one.return_value = 0.9
            self.main.models["heating"].steps = {}
            self.main.model_trained = True

            self.main.job()
            mock_alert.assert_not_called()
            self.assertEqual(self.main.consecutive_anomalies.get("heating", 0), 1)

            self.main.job()
            mock_alert.assert_not_called()
            self.assertEqual(self.main.consecutive_anomalies.get("heating", 0), 2)

            self.main.job()
            mock_alert.assert_called()
            self.assertEqual(self.main.consecutive_anomalies.get("heating", 0), 3)

    def test_warmup_logic(self):
        with (
            patch.object(self.main, "fetch_latest_data") as mock_fetch,
            patch.object(self.main, "write_metrics"),
        ):
            mock_fetch.return_value = {"sensor1": 10.0}
            self.main.models["standby"].score_one.return_value = 0.0

            for _ in range(7):
                self.main.job()

            self.assertTrue(self.main.model_trained)

    def test_persistence(self):
        if not hasattr(self.main, "pickle"):
            self.main.pickle = pickle

        with patch("ml_service.main.USE_JOBLIB", False):
            with (
                patch("ml_service.main.threading.Thread") as mock_thread,
                patch("ml_service.main.pickle.dumps") as mock_dumps,
                patch("os.makedirs"),
            ):
                mock_dumps.return_value = b"serialized_data"

                res = self.main.save_model_state()

                if not res:
                    print(f"Error logs: {self.main.logger.error.call_args_list}")

                mock_dumps.assert_called_once_with(self.main.models)

                mock_thread.assert_called_once()
                call_kwargs = mock_thread.call_args[1]
                self.assertEqual(call_kwargs["target"], self.main._save_worker)
                self.assertEqual(call_kwargs["args"][0], b"serialized_data")
                mock_thread.return_value.start.assert_called_once()

    def test_save_worker(self):
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("os.replace") as mock_replace,
            patch("os.remove") as mock_remove,
            patch("uuid.uuid4", return_value="1234"),
        ):
            self.main._save_worker(b"data", "/path/to/model")

            expected_temp = "/path/to/model.1234.tmp"
            mock_file.assert_called_with(expected_temp, "wb")
            mock_file().write.assert_called_with(b"data")
            mock_replace.assert_called_with(expected_temp, "/path/to/model")

            mock_replace.side_effect = OSError("Disk full")
            with patch("os.path.exists", return_value=True):
                self.main._save_worker(b"data", "/path/to/model")
                mock_remove.assert_called_with(expected_temp)

    def test_autoencoder_model_score_learn(self):
        if isinstance(sys.modules.get("torch"), MagicMock):
            self.skipTest("Torch mocked")

        from ml_service.models import AutoencoderModel

        model = AutoencoderModel(hidden_dim=8, latent_dim=4, train_steps=1)

        data = {"sensor1": 10.0, "sensor2": 20.0, "sensor3": 30.0}

        score = model.score_one(data)
        self.assertEqual(score, 0.0)

        model.learn_one(data)

        self.assertEqual(model.feature_order, ["sensor1", "sensor2", "sensor3"])

        score = model.score_one(data)
        self.assertIsInstance(score, float)

    def test_autoencoder_model_online_scaler(self):
        if isinstance(sys.modules.get("torch"), MagicMock):
            self.skipTest("Torch mocked")

        from ml_service.models import OnlineStandardScaler

        scaler = OnlineStandardScaler()

        scaler.partial_fit({"a": 10.0, "b": 20.0})
        scaler.partial_fit({"a": 20.0, "b": 40.0})

        self.assertAlmostEqual(scaler.means["a"], 15.0)
        self.assertAlmostEqual(scaler.means["b"], 30.0)

        scaled = scaler.transform({"a": 15.0, "b": 30.0}, ["a", "b"])
        self.assertAlmostEqual(scaled[0], 0.0, places=1)
        self.assertAlmostEqual(scaled[1], 0.0, places=1)

    def test_get_top_features_with_autoencoder(self):
        model = MagicMock()
        model.get_top_features.return_value = [
            {"feature": "sensor1", "score": 2.0, "value": 14.0, "mean": 10.0}
        ]

        data = {"sensor1": 14.0, "sensor2": 23.0}

        result = self.main.get_top_features(model, data, n=2)

        model.get_top_features.assert_called_once_with(data, n=2)
        self.assertEqual(len(result), 1)

    def test_fetch_latest_data(self):
        with patch("ml_service.main.http_session.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "status": "success",
                "data": {
                    "result": [
                        {
                            "metric": {"__name__": "idm_heatpump_sensor1"},
                            "value": [1234567890, "10.5"],
                        },
                        {
                            "metric": {"__name__": "idm_heatpump_sensor2"},
                            "value": [1234567890, "20.0"],
                        },
                    ]
                },
            }

            with patch("ml_service.config.config.measurement_name", "idm_heatpump"):
                with patch("ml_service.main.config") as mock_cfg:
                    mock_cfg.measurement_name = "idm_heatpump"
                    mock_cfg.metrics_url = "http://test-vm"
                    data = self.main.fetch_latest_data()

            self.assertIsNotNone(data)
            self.assertEqual(data["sensor1"], 10.5)
            self.assertEqual(data["sensor2"], 20.0)

            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertIn("data", kwargs)
            self.assertIn("query", kwargs["data"])


if __name__ == "__main__":
    unittest.main()
