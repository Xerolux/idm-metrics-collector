import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import _process_telemetry_batch


def test_process_batch_valid_data():
    data = [
        {"timestamp": 1234567890.0, "temp": 20.5, "active": True},
        {"timestamp": 1234567891.0, "pressure": 1.2},
    ]
    tags = "installation_id=test,model=AERO,version=1.0"

    result, count = _process_telemetry_batch(data, tags)

    assert count == 2
    assert result is not None
    lines = result.split("\n")
    assert len(lines) == 2

    # Check line 1
    # Note: dict order is preserved in Python 3.7+
    assert "heatpump_metrics,installation_id=test,model=AERO,version=1.0" in lines[0]
    assert "temp=20.5" in lines[0]
    assert "active=true" in lines[0]
    assert lines[0].endswith("1234567890000000000")

    # Check line 2
    assert "pressure=1.2" in lines[1]
    assert lines[1].endswith("1234567891000000000")


def test_process_batch_missing_timestamp():
    data = [
        {"temp": 20.5},  # Missing timestamp
        {"timestamp": 1234567890.0, "temp": 21.0},
    ]
    tags = "tag=value"

    result, count = _process_telemetry_batch(data, tags)

    assert count == 1
    assert result is not None
    assert "temp=21.0" in result
    assert "temp=20.5" not in result


def test_process_batch_empty():
    data = []
    tags = "tag=value"

    result, count = _process_telemetry_batch(data, tags)

    assert count == 0
    assert result is None


def test_process_batch_only_timestamp():
    data = [{"timestamp": 1234567890.0}]
    tags = "tag=value"

    result, count = _process_telemetry_batch(data, tags)

    # Should be skipped because no fields
    assert count == 0
    assert result is None


def test_process_batch_ignores_non_metric_types():
    # Only int, float, bool are supported as fields in this implementation
    # Strings in 'data' (values) are ignored by the logic, only used in tags
    data = [{"timestamp": 1234567890.0, "status": "running", "code": 123}]
    tags = "tag=value"

    result, count = _process_telemetry_batch(data, tags)

    assert count == 1
    assert "code=123" in result
    assert "running" not in result
