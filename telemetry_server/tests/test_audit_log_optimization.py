import json
import os
import pytest
from telemetry_server.audit_log import AuditLogger


# Fixture to mock AUDIT_LOG_DIR
@pytest.fixture
def mock_audit_log_dir(tmp_path):
    # Set environment variable
    original_env = os.environ.get("AUDIT_LOG_DIR")
    os.environ["AUDIT_LOG_DIR"] = str(tmp_path)

    # Reload audit_log module to pick up the new env var
    import importlib
    import telemetry_server.audit_log

    importlib.reload(telemetry_server.audit_log)

    yield tmp_path

    # Restore environment variable
    if original_env:
        os.environ["AUDIT_LOG_DIR"] = original_env
    else:
        del os.environ["AUDIT_LOG_DIR"]


def test_get_recent_events_empty_file(mock_audit_log_dir):
    logger = AuditLogger()
    events = logger.get_recent_events()
    assert events == []


def test_get_recent_events_small_file(mock_audit_log_dir):
    logger = AuditLogger()

    # Create log file with 3 events
    events_data = [
        {"timestamp": "2023-10-26T10:00:00+00:00", "id": 1},
        {"timestamp": "2023-10-26T10:00:01+00:00", "id": 2},
        {"timestamp": "2023-10-26T10:00:02+00:00", "id": 3},
    ]

    with open(logger.log_file, "w") as f:
        for event in events_data:
            f.write(json.dumps(event) + "\n")

    events = logger.get_recent_events(limit=2)
    assert len(events) == 2
    # Should be returned most recent first (id 3, then id 2)
    assert events[0]["id"] == 3
    assert events[1]["id"] == 2


def test_get_recent_events_large_limit(mock_audit_log_dir):
    logger = AuditLogger()

    # Create log file with 3 events
    events_data = [
        {"timestamp": "2023-10-26T10:00:00+00:00", "id": 1},
        {"timestamp": "2023-10-26T10:00:01+00:00", "id": 2},
        {"timestamp": "2023-10-26T10:00:02+00:00", "id": 3},
    ]

    with open(logger.log_file, "w") as f:
        for event in events_data:
            f.write(json.dumps(event) + "\n")

    events = logger.get_recent_events(limit=10)
    assert len(events) == 3
    # Should be returned most recent first (id 3, then id 2, then id 1)
    assert events[0]["id"] == 3
    assert events[1]["id"] == 2
    assert events[2]["id"] == 1


def test_get_recent_events_malformed_lines(mock_audit_log_dir):
    logger = AuditLogger()

    with open(logger.log_file, "w") as f:
        f.write('{"id": 1}\n')
        f.write("invalid json\n")
        f.write('{"id": 2}\n')

    events = logger.get_recent_events(limit=10)
    assert len(events) == 2
    assert events[0]["id"] == 2
    assert events[1]["id"] == 1


def test_get_recent_events_unicode(mock_audit_log_dir):
    logger = AuditLogger()

    with open(logger.log_file, "w", encoding="utf-8") as f:
        f.write('{"msg": "héllo"}\n')
        f.write('{"msg": "wørld"}\n')

    events = logger.get_recent_events(limit=10)
    assert len(events) == 2
    assert events[0]["msg"] == "wørld"
    assert events[1]["msg"] == "héllo"


def test_get_recent_events_no_newline_at_end(mock_audit_log_dir):
    logger = AuditLogger()

    with open(logger.log_file, "w", encoding="utf-8") as f:
        f.write('{"id": 1}\n')
        f.write('{"id": 2}')  # No newline at end

    events = logger.get_recent_events(limit=10)
    assert len(events) == 2
    assert events[0]["id"] == 2
    assert events[1]["id"] == 1
