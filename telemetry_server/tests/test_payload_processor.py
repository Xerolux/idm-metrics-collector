from app import _process_telemetry_batch


def test_process_telemetry_batch():
    tags = "installation_id=test-uuid,model=HeatPump_A,version=1.0.0"
    payload_data = [
        {
            "timestamp": 1700000000.123,
            "temperature_out": 5.5,
            "compressor_active": True,
        },
        {"timestamp": 1700000060.0, "temperature_out": 5.6, "compressor_active": False},
        {"invalid": "data", "temperature_out": 5.7},  # missing timestamp
    ]

    lines = _process_telemetry_batch(payload_data, tags)

    assert len(lines) == 2

    # Check first line
    line1 = lines[0]
    assert "heatpump_metrics," in line1
    assert tags in line1
    assert "temperature_out=5.5" in line1
    assert "compressor_active=true" in line1

    # Let's do exact match where possible
    parts = line1.split(" ")
    assert len(parts) == 3
    assert parts[0] == f"heatpump_metrics,{tags}"
    assert "temperature_out=5.5" in parts[1]
    assert "compressor_active=true" in parts[1]

    # Check second line
    line2 = lines[1]
    parts2 = line2.split(" ")
    assert len(parts2) == 3
    assert parts2[0] == f"heatpump_metrics,{tags}"
    assert "temperature_out=5.6" in parts2[1]
    assert "compressor_active=false" in parts2[1]


def test_process_telemetry_batch_empty():
    lines = _process_telemetry_batch([], "tags=foo")
    assert len(lines) == 0


def test_process_telemetry_batch_no_valid_fields():
    payload_data = [
        {"timestamp": 1700000000.0, "text_field_ignored": "ignored"},
        {"timestamp": 1700000060.0, "nested_dict_ignored": {"temp": 5}},
    ]
    lines = _process_telemetry_batch(payload_data, "tags=foo")
    assert len(lines) == 0
