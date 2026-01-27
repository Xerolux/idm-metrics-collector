import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure ml_service can find idm_logger
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create mocks for river components
mock_river = MagicMock()
mock_compose = MagicMock()

# Mock dependencies before importing ml_service.main
with patch.dict(
    sys.modules,
    {
        "idm_logger": MagicMock(),
        "idm_logger.sensor_addresses": MagicMock(),
        "idm_logger.const": MagicMock(),
        "river": mock_river,
        "river.anomaly": MagicMock(),
        "river.preprocessing": MagicMock(),
        "river.compose": mock_compose,
    },
):
    # Mock sensor addresses
    mock_sensor_addresses = sys.modules["idm_logger.sensor_addresses"]
    mock_sensor_addresses.COMMON_SENSORS = []
    mock_sensor_addresses.BINARY_SENSOR_ADDRESSES = {}
    mock_sensor_addresses.heating_circuit_sensors.return_value = []
    mock_sensor_addresses.zone_sensors.return_value = []

    mock_const = sys.modules["idm_logger.const"]

    class MockStatus:
        DEFROSTING = MagicMock(value=1)
        WATER = MagicMock(value=2)
        COOLING = MagicMock(value=4)
        HEATING = MagicMock(value=8)

    mock_const.HeatPumpStatus = MockStatus

    import ml_service.main as ml_main


class TestMLServiceMulti(unittest.TestCase):
    def setUp(self):
        # Reset global state
        ml_main.contexts = {}
        ml_main.saved_state_cache = {}
        # Reset sensors list to a predictable set
        ml_main.SENSORS = ["temp_outdoor", "power_current"]

    def test_multi_heatpump_processing(self):
        # Create a mock pipeline instance that returns a float score
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.score_one.return_value = 0.5

        # Patch create_pipeline to return our mock instance
        with patch.object(
            ml_main, "create_pipeline", return_value=mock_pipeline_instance
        ):
            with patch.object(ml_main, "requests") as mock_requests:
                # Setup mock response from VictoriaMetrics
                mock_response = {
                    "status": "success",
                    "data": {
                        "result": [
                            {
                                "metric": {
                                    "__name__": "idm_heatpump_temp_outdoor",
                                    "heatpump_id": "hp1",
                                },
                                "value": [1234567890, "10.5"],
                            },
                            {
                                "metric": {
                                    "__name__": "idm_heatpump_temp_outdoor",
                                    "heatpump_id": "hp2",
                                },
                                "value": [1234567890, "12.0"],
                            },
                            {
                                "metric": {
                                    "__name__": "idm_heatpump_power_current",
                                    "heatpump_id": "hp1",
                                },
                                "value": [1234567890, "3.5"],
                            },
                        ]
                    },
                }

                mock_requests.get.return_value.status_code = 200
                mock_requests.get.return_value.json.return_value = mock_response
                mock_requests.post.return_value.status_code = 200

                # Run job
                ml_main.job()

                # Check contexts created
                self.assertIn("hp1", ml_main.contexts)
                self.assertIn("hp2", ml_main.contexts)

                # Verify calls to write_metrics (requests.post)
                # Should be 2 calls to write_metrics
                self.assertEqual(mock_requests.post.call_count, 2)

                # Check payloads
                calls = mock_requests.post.call_args_list
                payloads = []
                for c in calls:
                    if "data" in c.kwargs:
                        payloads.append(c.kwargs["data"])
                    elif len(c.args) > 1:
                        payloads.append(c.args[1])

                hp1_found = False
                for p in payloads:
                    if 'heatpump_id="hp1"' in p:
                        hp1_found = True
                self.assertTrue(
                    hp1_found, f"Did not find payload for hp1 in {payloads}"
                )

                hp2_found = False
                for p in payloads:
                    if 'heatpump_id="hp2"' in p:
                        hp2_found = True
                self.assertTrue(
                    hp2_found, f"Did not find payload for hp2 in {payloads}"
                )

    def test_fetch_latest_data_grouping(self):
        with patch.object(ml_main, "requests") as mock_requests:
            mock_response = {
                "status": "success",
                "data": {
                    "result": [
                        {
                            "metric": {
                                "__name__": "idm_heatpump_sensor1",
                                "heatpump_id": "hp1",
                            },
                            "value": [0, "100"],
                        },
                        {
                            "metric": {
                                "__name__": "idm_heatpump_sensor1",
                                "heatpump_id": "hp2",
                            },
                            "value": [0, "200"],
                        },
                        {
                            "metric": {
                                "__name__": "idm_heatpump_sensor2",
                                "heatpump_id": "hp1",
                            },
                            "value": [0, "300"],
                        },
                    ]
                },
            }
            mock_requests.get.return_value.status_code = 200
            mock_requests.get.return_value.json.return_value = mock_response

            data = ml_main.fetch_latest_data()

            self.assertEqual(len(data), 2)
            self.assertEqual(data["hp1"]["sensor1"], 100.0)
            self.assertEqual(data["hp1"]["sensor2"], 300.0)
            self.assertEqual(data["hp2"]["sensor1"], 200.0)
            self.assertNotIn("sensor2", data["hp2"])


if __name__ == "__main__":
    unittest.main()
