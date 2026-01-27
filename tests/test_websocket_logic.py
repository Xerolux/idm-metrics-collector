import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from idm_logger.websocket_handler import WebSocketHandler


class TestWebSocketHandler:
    @pytest.fixture
    def mock_socketio(self):
        mock = MagicMock()
        mock.handlers = {}  # Explicitly initialize as dict to avoid MagicMock auto-creation

        # Mock the decorator behavior
        def on_decorator(event):
            def wrapper(f):
                # Store the handler function in the mock so we can access it
                mock.handlers[event] = f
                return f

            return wrapper

        mock.on.side_effect = on_decorator
        return mock

    @pytest.fixture
    def app(self):
        return Flask(__name__)

    @pytest.fixture
    def handler(self, app, mock_socketio):
        # We need to mock join_room
        with (
            patch("idm_logger.websocket_handler.join_room") as mock_join_room,
            patch("idm_logger.websocket_handler.emit"),
        ):
            handler = WebSocketHandler(app, mock_socketio)
            handler.mock_join_room = mock_join_room
            yield handler

    def test_subscribe_joins_room(self, handler, mock_socketio, app):
        # Access the subscribe handler captured by our mock decorator
        subscribe_handler = mock_socketio.handlers["subscribe"]

        data = {"metrics": ["metric1", "metric2"]}

        # Run with request context
        with app.test_request_context():
            # Inject sid into request context if needed, but Flask-SocketIO might use request.sid which is special
            # Flask's test request doesn't have .sid by default.
            # We must patch request.sid or use a custom context?
            # Or assume request.sid exists?
            # In Flask-SocketIO, request.sid is available.
            # But we are using a plain Flask app here.
            # We can set attribute on request?
            from flask import request

            request.sid = "test_sid"

            # Call the handler
            subscribe_handler(data)

        # Verify join_room was called for each metric
        handler.mock_join_room.assert_any_call("metric1")
        handler.mock_join_room.assert_any_call("metric2")

        # Verify subscriptions updated
        assert "test_sid" in handler.subscriptions["metric1"]
        assert "test_sid" in handler.subscriptions["metric2"]

    def test_broadcast_metrics(self, handler, mock_socketio):
        # Setup subscriptions
        handler.subscriptions["temp_outdoor"] = {"sid1"}
        handler.subscriptions["power_total"] = {"sid1", "sid2"}

        data = {"temp_outdoor": 12.5, "power_total": 1500, "unused_metric": 0}

        handler.broadcast_metrics(data)

        # Verify emit calls
        # We expect emit for temp_outdoor and power_total
        assert mock_socketio.emit.call_count == 2

        # Check arguments
        emitted_metrics = []
        for call in mock_socketio.emit.call_args_list:
            args, kwargs = call
            event = args[0]
            payload = args[1]
            room = kwargs.get("room")

            assert event == "metric_update"
            assert payload["metric"] == room
            emitted_metrics.append(payload["metric"])

        assert "temp_outdoor" in emitted_metrics
        assert "power_total" in emitted_metrics
        assert "unused_metric" not in emitted_metrics
