
import uuid
import sys
import os

# Add telemetry_server to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import TelemetryPayload, _process_telemetry_payload

def test_process_telemetry_payload_optimization():
    """Verify optimized payload processing logic."""

    # Test data
    payload = TelemetryPayload(
        installation_id="d9990d31-b6b3-48e7-b960-b659250b0800",
        heatpump_model="Test Model 123",
        version="1.0.0",
        data=[
            {
                "timestamp": 1700000000.0,
                "temp_in": 20.5,
                "status": True,
                "valve_open": False,
                "ignore_me": "string" # Should be ignored
            },
            {
                "timestamp": 1700000001.0,
                "temp_in": 21.0,
                "status": False
            }
        ]
    )

    # Expected output format
    # heatpump_metrics,installation_id=...,model=...,version=... field=val timestamp

    # Expected tags
    tags = "installation_id=d9990d31-b6b3-48e7-b960-b659250b0800,model=Test_Model_123,version=1.0.0"
    prefix = f"heatpump_metrics,{tags} "

    # Process
    result = _process_telemetry_payload(payload)
    lines = result.split("\n")

    assert len(lines) == 2

    # Check line 1
    # Order of fields depends on dict iteration order (insertion order since Python 3.7)
    # But we should be robust.
    line1 = lines[0]
    assert line1.startswith(prefix)
    assert str(int(1700000000.0 * 1e9)) in line1
    assert "temp_in=20.5" in line1
    assert "status=true" in line1  # Check for lowercase bool
    assert "valve_open=false" in line1 # Check for lowercase bool
    assert "ignore_me" not in line1 # String should be ignored

    # Check line 2
    line2 = lines[1]
    assert line2.startswith(prefix)
    assert str(int(1700000001.0 * 1e9)) in line2
    assert "temp_in=21.0" in line2
    assert "status=false" in line2

def test_process_telemetry_payload_empty():
    """Verify empty payload handling."""
    payload = TelemetryPayload(
        installation_id=str(uuid.uuid4()),
        heatpump_model="Model",
        version="1",
        data=[]
    )
    assert _process_telemetry_payload(payload) == ""

def test_process_telemetry_payload_no_timestamp():
    """Verify records without timestamp are skipped."""
    payload = TelemetryPayload(
        installation_id=str(uuid.uuid4()),
        heatpump_model="Model",
        version="1",
        data=[{"value": 10}] # Missing timestamp
    )
    assert _process_telemetry_payload(payload) == ""

if __name__ == "__main__":
    # Manually run if executed directly (e.g. for debugging)
    # We need to mock _process_telemetry_payload if it's not imported yet?
    # No, we assume this file is run AFTER implementation or during development.
    pass
