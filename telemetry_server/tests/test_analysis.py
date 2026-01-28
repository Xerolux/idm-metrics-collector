from unittest.mock import patch, MagicMock
import sys
import os

# Ensure telemetry_server is in path (similar to conftest, but explicit for this test module if needed)
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis import get_community_averages


@patch("requests.get")
def test_get_community_averages_success(mock_get):
    # Mock responses for count, avg, min, max
    # count query
    r1 = MagicMock()
    r1.status_code = 200
    r1.json.return_value = {
        "status": "success",
        "data": {"result": [{"value": [123456, "10"]}]},
    }

    # avg query
    r2 = MagicMock()
    r2.status_code = 200
    r2.json.return_value = {
        "status": "success",
        "data": {"result": [{"value": [123456, "4.2"]}]},
    }

    # min/max queries
    r3 = MagicMock()
    r3.status_code = 200
    r3.json.return_value = {
        "status": "success",
        "data": {"result": [{"value": [123456, "3.5"]}]},
    }

    mock_get.side_effect = [r1, r2, r3, r3]  # count, avg, min, max

    result = get_community_averages("AERO_SLM", ["cop_current"])

    assert result["model"] == "AERO_SLM"
    assert result["sample_size"] == 10
    assert "metrics" in result
    assert "cop_current" in result["metrics"]
    assert result["metrics"]["cop_current"]["avg"] == 4.2
    assert result["metrics"]["cop_current"]["min"] == 3.5


@patch("requests.get")
def test_get_community_averages_no_data(mock_get):
    # count query returns 0
    r1 = MagicMock()
    r1.status_code = 200
    r1.json.return_value = {
        "status": "success",
        "data": {"result": []},  # No result means 0? Or result with value 0?
        # count() returns a vector if matches, or empty if no matches?
        # Actually count() over time usually returns something if time series exist.
        # Let's assume empty result means 0.
    }
    mock_get.return_value = r1

    result = get_community_averages("Unknown", ["cop_current"])
    assert result["sample_size"] == 0
    assert result["metrics"] == {}


@patch("requests.get")
def test_get_community_averages_error(mock_get):
    mock_get.side_effect = Exception("VM Down")

    result = get_community_averages("AERO_SLM", ["cop_current"])
    assert "error" in result
