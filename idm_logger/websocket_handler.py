"""
WebSocket Handler for real-time data updates.

This module provides WebSocket support for pushing real-time metric updates
to connected clients without requiring polling.
"""

import logging
from typing import Dict, Set
from flask_socketio import emit, join_room, leave_room
from flask import request

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handler for WebSocket connections and real-time updates."""

    def __init__(self, app=None, socketio=None):
        """
        Initialize the WebSocket handler.

        Args:
            app: Flask application instance
            socketio: SocketIO instance
        """
        self.socketio = socketio
        self.app = app
        self.subscriptions: Dict[str, Set[str]] = {}  # metric -> set of session ids
        self.dashboard_subscriptions: Dict[
            str, Set[str]
        ] = {}  # dashboard_id -> set of session ids

        if app:
            self.init_app(app, socketio)

    def init_app(self, app, socketio):
        """
        Initialize with Flask app.

        Args:
            app: Flask application instance
            socketio: SocketIO instance
        """
        self.app = app
        self.socketio = socketio

        # Register event handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register SocketIO event handlers."""

        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection."""
            from flask import session

            user = session.get("user", "anonymous")
            logger.info(f"WebSocket client connected: {request.sid} as {user}")
            emit("connected", {"status": "connected", "sid": request.sid})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info(f"WebSocket client disconnected: {request.sid}")
            self._cleanup_subscriptions(request.sid)

        @self.socketio.on("subscribe")
        def handle_subscribe(data):
            """
            Handle subscription to specific metrics.

            Args:
                data: { 'metrics': ['metric1', 'metric2'], 'dashboard_id': '...' }
            """
            sid = request.sid
            metrics = data.get("metrics", [])
            dashboard_id = data.get("dashboard_id")

            logger.info(f"Client {sid} subscribing to metrics: {metrics}")

            # Subscribe to metrics
            for metric in metrics:
                if metric not in self.subscriptions:
                    self.subscriptions[metric] = set()
                self.subscriptions[metric].add(sid)
                join_room(metric)

            # Subscribe to dashboard room
            if dashboard_id:
                if dashboard_id not in self.dashboard_subscriptions:
                    self.dashboard_subscriptions[dashboard_id] = set()
                self.dashboard_subscriptions[dashboard_id].add(sid)
                join_room(f"dashboard_{dashboard_id}")

            emit("subscribed", {"metrics": metrics, "dashboard_id": dashboard_id})

        @self.socketio.on("unsubscribe")
        def handle_unsubscribe(data):
            """
            Handle unsubscription from specific metrics.

            Args:
                data: { 'metrics': ['metric1', 'metric2'], 'dashboard_id': '...' }
            """
            sid = request.sid
            metrics = data.get("metrics", [])
            dashboard_id = data.get("dashboard_id")

            logger.info(f"Client {sid} unsubscribing from metrics: {metrics}")

            # Unsubscribe from metrics
            for metric in metrics:
                if metric in self.subscriptions:
                    self.subscriptions[metric].discard(sid)

            # Unsubscribe from dashboard room
            if dashboard_id:
                if dashboard_id in self.dashboard_subscriptions:
                    self.dashboard_subscriptions[dashboard_id].discard(sid)
                leave_room(f"dashboard_{dashboard_id}")

            emit("unsubscribed", {"metrics": metrics, "dashboard_id": dashboard_id})

        @self.socketio.on("ping")
        def handle_ping():
            """Handle ping from client."""
            emit("pong", {"timestamp": int(1000 * self.socketio.server.time())})

    def _cleanup_subscriptions(self, sid: str):
        """
        Clean up subscriptions for a disconnected client.

        Args:
            sid: Session ID to clean up
        """
        # Remove from metric subscriptions
        for metric in list(self.subscriptions.keys()):
            self.subscriptions[metric].discard(sid)
            if not self.subscriptions[metric]:
                del self.subscriptions[metric]

        # Remove from dashboard subscriptions
        for dashboard_id in list(self.dashboard_subscriptions.keys()):
            self.dashboard_subscriptions[dashboard_id].discard(sid)
            if not self.dashboard_subscriptions[dashboard_id]:
                del self.dashboard_subscriptions[dashboard_id]

    def broadcast_metric_update(self, metric: str, value: float, timestamp: int):
        """
        Broadcast a metric update to all subscribed clients.

        Args:
            metric: Metric name
            value: Metric value
            timestamp: Unix timestamp
        """
        if metric not in self.subscriptions:
            return

        data = {"metric": metric, "value": value, "timestamp": timestamp}
        self.socketio.emit("metric_update", data, room=metric)

    def broadcast_metrics(self, data: Dict):
        """
        Broadcast multiple metric updates to subscribed clients.

        Args:
            data: Dictionary of metric values {metric_name: value, ...}
        """
        import time

        timestamp = int(time.time())

        for metric, value in data.items():
            # Skip internal fields or non-metric data if any
            if not isinstance(metric, str):
                continue

            if metric in self.subscriptions and self.subscriptions[metric]:
                payload = {"metric": metric, "value": value, "timestamp": timestamp}
                self.socketio.emit("metric_update", payload, room=metric)

    def broadcast_dashboard_update(self, dashboard_id: str, data: dict):
        """
        Broadcast a dashboard update to all subscribed clients.

        Args:
            dashboard_id: Dashboard ID
            data: Update data
        """
        self.socketio.emit("dashboard_update", data, room=f"dashboard_{dashboard_id}")

    def get_stats(self) -> dict:
        """
        Get WebSocket handler statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_connections": len(self.socketio.manager.get_namespaces()),
            "metric_subscriptions": {
                metric: len(sids) for metric, sids in self.subscriptions.items()
            },
            "dashboard_subscriptions": {
                dashboard_id: len(sids)
                for dashboard_id, sids in self.dashboard_subscriptions.items()
            },
        }


# Global instance
websocket_handler = WebSocketHandler()
