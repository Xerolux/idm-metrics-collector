import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idm_logger.websocket_handler import WebSocketHandler
from idm_logger.web import app


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
    def mock_app(self):
        return MagicMock()

    @pytest.fixture
    def handler(self, mock_app, mock_socketio):
        # We need to mock join_room AND request context
        # We pass new=MagicMock() to avoid patching mechanism inspecting the original request object which triggers context error
        mock_req = MagicMock()
        mock_req.sid = "test_sid"

        # Patch idm_logger.websocket_handler.join_room because it is imported into that module
        with (
            patch("idm_logger.websocket_handler.join_room") as mock_join_room,
            patch("idm_logger.websocket_handler.emit"),
        ):
            handler = WebSocketHandler(mock_app, mock_socketio)
            handler.mock_join_room = mock_join_room
            # We don't patch request here because we use app.test_request_context
            yield handler

    def test_subscribe_joins_room(self, handler, mock_socketio):
        # Access the subscribe handler captured by our mock decorator
        subscribe_handler = mock_socketio.handlers["subscribe"]

        data = {"metrics": ["metric1", "metric2"]}

        # Call the handler inside a request context
        with app.test_request_context("/"):
            # Mock the sid which is accessed via request.sid
            # However, since we patched 'request' in the handler fixture to be a MagicMock,
            # the handler code using `request.sid` will use the mock.
            # BUT the Runtime Error came from `idm_logger/websocket_handler.py:77: in handle_subscribe sid = request.sid`.
            # Wait, if `handler` fixture patches `request`, why did it fail?
            # Let's look at the fixture.
            # `patch('idm_logger.websocket_handler.request', new=mock_req)`
            # This replaces `request` object imported in `websocket_handler`.
            # But `websocket_handler.py` might do `from flask import request`.
            # If so, `patch('idm_logger.websocket_handler.request')` patches the name in that module.
            # If the code failed with RuntimeError from werkzeug.local, it means it used the REAL flask.request.
            # This implies `patch` failed to replace it or `websocket_handler` uses `flask.request` directly?
            # Using `app.test_request_context` is the safer/correct way regardless of patching.

            # We also need to mock the sid on the context's request, OR rely on the patch if it works.
            # If the patch didn't work, we need to set sid on the real request.
            # But let's try just the context first.
            from flask import request as flask_request

            flask_request.sid = "test_sid"

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
