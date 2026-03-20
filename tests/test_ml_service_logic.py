# Xerolux 2026
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import importlib
import pickle
from idm_logger.const import HeatPumpStatus

# Add repo root to path
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
            },
        )
        self.env_patcher.start()

        # Mock torch if not installed
        if "torch" not in sys.modules:
            sys.modules["torch"] = MagicMock()
            sys.modules["torch.nn"] = MagicMock()
            sys.modules["torch.nn.Module"] = MagicMock

        try:
            import ml_service.main as main

            importlib.reload(main)
            self.main = main
        except ImportError:
            self.skipTest("ML Service dependencies not met")

        self.main.SENSORS = ["sensor1", "sensor2", "status_heat_pump"]
        # Mock models with AutoencoderModel-like interface
        self.main.models = {
            "heating": MagicMock(),
            "cooling": MagicMock(),
            "water": MagicMock(),
            "standby": MagicMock(),
        }
        # Add scaler attribute to mocked models for get_top_features compatibility
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

    def test_determine_mode(self):
        # Heating
        data = {"status_heat_pump": HeatPumpStatus.HEATING.value}
        self.assertEqual(self.main.determine_mode(data), "heating")

        # Cooling
        data = {"status_heat_pump": HeatPumpStatus.COOLING.value}
        self.assertEqual(self.main.determine_mode(data), "cooling")

        # Defrost (priority)
        data = {
            "status_heat_pump": HeatPumpStatus.HEATING.value
            | HeatPumpStatus.DEFROSTING.value
        }
        self.assertEqual(self.main.determine_mode(data), "defrost")

        # Standby
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
            # 1. Normal run, heating mode
            mock_fetch.return_value = {
                "sensor1": 10.0,
                "status_heat_pump": HeatPumpStatus.HEATING.value,
            }
            self.main.models["heating"].score_one.return_value = 0.1  # Low score
            self.main.models["heating"].steps = {}

            self.main.job()

            self.main.models["heating"].learn_one.assert_called()
            mock_write.assert_called()
            args, _ = mock_write.call_args
            self.assertEqual(args[4], "heating")  # Check mode arg
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
            self.main.models[
                "heating"
            ].score_one.return_value = 0.9  # High score (Anomaly)
            self.main.models["heating"].steps = {}
            self.main.model_trained = True  # Force trained

            # Hit 1
            self.main.job()
            mock_alert.assert_not_called()
            self.assertEqual(self.main.consecutive_anomalies.get("heating", 0), 1)

            # Hit 2
            self.main.job()
            mock_alert.assert_not_called()
            self.assertEqual(self.main.consecutive_anomalies.get("heating", 0), 2)

            # Hit 3 (Threshold is 3)
            self.main.job()
            mock_alert.assert_called()
            self.assertEqual(self.main.consecutive_anomalies.get("heating", 0), 3)

    def test_warmup_logic(self):
        # We need to force update_counter to match what we expect.
        # job() increments it at the end.

        with (
            patch.object(self.main, "fetch_latest_data") as mock_fetch,
            patch.object(self.main, "write_metrics"),
        ):
            mock_fetch.return_value = {"sensor1": 10.0}
            self.main.models["standby"].score_one.return_value = 0.0

            # Run enough times to exceed WARMUP_UPDATES=5
            for _ in range(7):
                self.main.job()

            self.assertTrue(self.main.model_trained)

    def test_persistence(self):
        # Inject pickle if missing (because joblib was preferred)
        if not hasattr(self.main, "pickle"):
            self.main.pickle = pickle

        # Force USE_JOBLIB to False using string patch, which is safer for module globals
        with patch("ml_service.main.USE_JOBLIB", False):
            with (
                patch("ml_service.main.threading.Thread") as mock_thread,
                patch("ml_service.main.pickle.dumps") as mock_dumps,
                patch("os.makedirs"),
            ):
                mock_dumps.return_value = b"serialized_data"

                res = self.main.save_model_state()

                # Check for errors
                if not res:
                    # If failed, print error log
                    print(f"Error logs: {self.main.logger.error.call_args_list}")

                # Verify serialization (snapshot)
                mock_dumps.assert_called_once_with(self.main.models)

                # Verify thread spawn
                mock_thread.assert_called_once()
                call_kwargs = mock_thread.call_args[1]
                self.assertEqual(call_kwargs["target"], self.main._save_worker)
                self.assertEqual(call_kwargs["args"][0], b"serialized_data")
                self.assertEqual(call_kwargs["args"][1], "/tmp/test_model.pkl")
                self.assertEqual(call_kwargs["daemon"], False)
                mock_thread.return_value.start.assert_called_once()

    def test_save_worker(self):
        """Test the background worker file writing logic."""
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("os.replace") as mock_replace,
            patch("os.remove") as mock_remove,
            patch("uuid.uuid4", return_value="1234"),
        ):
            # Test success path
            self.main._save_worker(b"data", "/path/to/model")

            # Check file write to temp
            expected_temp = "/path/to/model.1234.tmp"
            mock_file.assert_called_with(expected_temp, "wb")
            mock_file().write.assert_called_with(b"data")

            # Check rename
            mock_replace.assert_called_with(expected_temp, "/path/to/model")

            # Test failure path (cleanup)
            mock_replace.side_effect = OSError("Disk full")
            with patch("os.path.exists", return_value=True):
                self.main._save_worker(b"data", "/path/to/model")
                mock_remove.assert_called_with(expected_temp)

    def test_autoencoder_model_score_learn(self):
        """Test that AutoencoderModel score_one and learn_one work correctly."""
        if isinstance(self.main.torch, MagicMock):
            self.skipTest("Torch mocked")

        model = self.main.AutoencoderModel(hidden_dim=8, latent_dim=4, train_steps=1)

        data = {"sensor1": 10.0, "sensor2": 20.0, "sensor3": 30.0}

        # First score should return 0.0 (no feature order yet)
        score = model.score_one(data)
        self.assertEqual(score, 0.0)

        # Learn from data
        model.learn_one(data)

        # After learning, feature_order should be set
        self.assertEqual(model.feature_order, ["sensor1", "sensor2", "sensor3"])

        # Score after learning should return a value
        score = model.score_one(data)
        self.assertIsInstance(score, float)

    def test_autoencoder_model_online_scaler(self):
        """Test that the OnlineStandardScaler tracks statistics correctly."""
        scaler = self.main.OnlineStandardScaler()

        # Fit with some data
        scaler.partial_fit({"a": 10.0, "b": 20.0})
        scaler.partial_fit({"a": 20.0, "b": 40.0})

        # Check means
        self.assertAlmostEqual(scaler.means["a"], 15.0)
        self.assertAlmostEqual(scaler.means["b"], 30.0)

        # Check that transform produces scaled values
        scaled = scaler.transform({"a": 15.0, "b": 30.0}, ["a", "b"])
        # Mean values should scale to ~0
        self.assertAlmostEqual(scaled[0], 0.0, places=1)
        self.assertAlmostEqual(scaled[1], 0.0, places=1)

    def test_get_top_features_with_autoencoder(self):
        """Test get_top_features works with AutoencoderModel's scaler."""
        model = MagicMock()
        model.scaler = MagicMock()
        model.scaler.means = {"sensor1": 10.0, "sensor2": 20.0}
        model.scaler.vars = {"sensor1": 4.0, "sensor2": 9.0}

        data = {"sensor1": 14.0, "sensor2": 23.0}

        result = self.main.get_top_features(model, data, n=2)

        self.assertEqual(len(result), 2)
        # sensor1 has z-score = |14-10|/2 = 2.0
        # sensor2 has z-score = |23-20|/3 = 1.0
        self.assertEqual(result[0]["feature"], "sensor1")
        self.assertAlmostEqual(result[0]["score"], 2.0)

    def test_fetch_latest_data(self):
        """Test fetch_latest_data uses POST and parses response correctly."""
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

            # Set measurement name to match mock data
            with patch("ml_service.main.MEASUREMENT_NAME", "idm_heatpump"):
                data = self.main.fetch_latest_data()

            self.assertIsNotNone(data)
            self.assertEqual(data["sensor1"], 10.5)
            self.assertEqual(data["sensor2"], 20.0)

            # Verify POST was used with correct data
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertIn("data", kwargs)
            self.assertIn("query", kwargs["data"])
            self.assertIn("idm_heatpump_sensor1", kwargs["data"]["query"])


if __name__ == "__main__":
    unittest.main()
