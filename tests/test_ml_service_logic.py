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

        import ml_service.main as main

        importlib.reload(main)
        self.main = main

        self.main.SENSORS = ["sensor1", "sensor2", "status_heat_pump"]
        # Mock models
        self.main.models = {
            "heating": MagicMock(),
            "cooling": MagicMock(),
            "water": MagicMock(),
            "standby": MagicMock(),
        }
        self.main.logger = MagicMock()
        self.main.last_data_points = {}
        self.main.consecutive_anomalies = 0
        self.main.update_counter = 0

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
            self.assertEqual(self.main.consecutive_anomalies, 1)

            # Hit 2
            self.main.job()
            mock_alert.assert_not_called()
            self.assertEqual(self.main.consecutive_anomalies, 2)

            # Hit 3 (Threshold is 3)
            self.main.job()
            mock_alert.assert_called()
            self.assertEqual(self.main.consecutive_anomalies, 3)

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
            # We need update_counter > 5.
            # It starts at 0.
            # 0 -> 1
            # 1 -> 2
            # 2 -> 3
            # 3 -> 4
            # 4 -> 5
            # 5 -> 6 (Now it satisfies > 5)

            # But the check happens BEFORE increment.
            # So:
            # call 1 (cnt=0): check 0>5 (False), inc -> 1
            # call 2 (cnt=1): check 1>5 (False), inc -> 2
            # call 3 (cnt=2): check 2>5 (False), inc -> 3
            # call 4 (cnt=3): check 3>5 (False), inc -> 4
            # call 5 (cnt=4): check 4>5 (False), inc -> 5
            # call 6 (cnt=5): check 5>5 (False), inc -> 6
            # call 7 (cnt=6): check 6>5 (True), inc -> 7

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
                patch("builtins.open", mock_open()),
                patch("pickle.dump") as mock_dump,
                patch("os.makedirs"),
            ):
                res = self.main.save_model_state()

                # Check for errors
                if not res:
                    # If failed, print error log
                    print(f"Error logs: {self.main.logger.error.call_args_list}")

                mock_dump.assert_called()
                args, _ = mock_dump.call_args
                self.assertEqual(args[0], self.main.models)


if __name__ == "__main__":
    unittest.main()
