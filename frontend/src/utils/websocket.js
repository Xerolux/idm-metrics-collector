/**
 * WebSocket Client for real-time metric updates.
 *
 * Provides automatic reconnection, subscription management,
 * and event handling for WebSocket connections.
 */

import { io } from 'socket.io-client';

/**
 * WebSocket connection state
 */
export const ConnectionState = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    RECONNECTING: 'reconnecting',
    ERROR: 'error'
};

/**
 * WebSocket client class
 */
export class WebSocketClient {
    constructor() {
        this.socket = null;
        this.connectionState = ConnectionState.DISCONNECTED;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.listeners = new Map();
        this.subscriptions = new Set();
        this.dashboardId = null;
    }

    /**
     * Connect to WebSocket server
     *
     * @param {string} url - Server URL (optional, defaults to current location)
     * @param {Object} options - Socket.IO options
     */
    connect(url = null, options = {}) {
        if (this.socket?.connected || this.connectionState === ConnectionState.CONNECTING) {
            if (this.socket?.connected) console.warn('WebSocket already connected');
            return;
        }

        this.connectionState = ConnectionState.CONNECTING;
        this._emitStateChange();

        const defaultOptions = {
            transports: ['websocket', 'polling'],
            reconnection: true, // Let Socket.IO handle reconnection
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: this.reconnectDelay,
            reconnectionDelayMax: this.maxReconnectDelay,
            ...options
        };

        this.socket = io(url || window.location.origin, defaultOptions);

        this._setupEventHandlers();
    }

    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.connectionState = ConnectionState.DISCONNECTED;
        this.subscriptions.clear();
        this.dashboardId = null;
        this._emitStateChange();
    }

    /**
     * Subscribe to metric updates
     *
     * @param {Array<string>} metrics - Array of metric names to subscribe to
     * @param {string} dashboardId - Dashboard ID (optional)
     */
    subscribe(metrics, dashboardId = null) {
        // Store subscriptions
        metrics.forEach(m => this.subscriptions.add(m));
        if (dashboardId) {
            this.dashboardId = dashboardId;
        }

        if (!this.socket?.connected) {
            console.log('WebSocket not connected, subscription queued for:', metrics);
            return;
        }

        this.socket.emit('subscribe', {
            metrics,
            dashboard_id: dashboardId
        });

        console.log(`Subscribed to metrics: ${metrics.join(', ')}`);
    }

    /**
     * Unsubscribe from metric updates
     *
     * @param {Array<string>} metrics - Array of metric names to unsubscribe from
     * @param {string} dashboardId - Dashboard ID (optional)
     */
    unsubscribe(metrics, dashboardId = null) {
        // Remove from stored subscriptions
        metrics.forEach(m => this.subscriptions.delete(m));

        if (!this.socket?.connected) {
            return;
        }

        this.socket.emit('unsubscribe', {
            metrics,
            dashboard_id: dashboardId
        });

        console.log(`Unsubscribed from metrics: ${metrics.join(', ')}`);
    }

    /**
     * Add event listener
     *
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    /**
     * Remove event listener
     *
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    off(event, callback) {
        if (!this.listeners.has(event)) {
            return;
        }
        const listeners = this.listeners.get(event);
        const index = listeners.indexOf(callback);
        if (index > -1) {
            listeners.splice(index, 1);
        }
    }

    /**
     * Send ping to server
     */
    ping() {
        if (this.socket?.connected) {
            this.socket.emit('ping');
        }
    }

    /**
     * Get connection state
     *
     * @returns {string} Connection state
     */
    getState() {
        return this.connectionState;
    }

    /**
     * Check if connected
     *
     * @returns {boolean} True if connected
     */
    isConnected() {
        return this.connectionState === ConnectionState.CONNECTED;
    }

    /**
     * Get current subscriptions
     *
     * @returns {Set<string>} Set of subscribed metrics
     */
    getSubscriptions() {
        return new Set(this.subscriptions);
    }

    /**
     * Setup Socket.IO event handlers
     * @private
     */
    _setupEventHandlers() {
        this.socket.on('connect', () => {
            console.log('WebSocket connected:', this.socket.id);
            this.connectionState = ConnectionState.CONNECTED;
            this.reconnectAttempts = 0;
            this._emitStateChange();

            // Re-subscribe to previous subscriptions
            if (this.subscriptions.size > 0 || this.dashboardId) {
                this.socket.emit('subscribe', {
                    metrics: Array.from(this.subscriptions),
                    dashboard_id: this.dashboardId
                });
            }
        });

        this.socket.on('disconnect', (reason) => {
            console.log('WebSocket disconnected:', reason);
            this.connectionState = ConnectionState.DISCONNECTED;
            this._emitStateChange();
        });

        this.socket.on('reconnect', (attemptNumber) => {
            console.log(`WebSocket reconnected after ${attemptNumber} attempts`);
            this.connectionState = ConnectionState.CONNECTED;
            this.reconnectAttempts = 0;
            this._emitStateChange();
        });

        this.socket.on('reconnect_attempt', (attemptNumber) => {
            console.log(`WebSocket reconnect attempt ${attemptNumber}`);
            this.connectionState = ConnectionState.RECONNECTING;
            this.reconnectAttempts = attemptNumber;
            this._emitStateChange();
        });

        this.socket.on('reconnect_failed', () => {
            console.error('WebSocket reconnection failed');
            this.connectionState = ConnectionState.ERROR;
            this._emitStateChange();
        });

        this.socket.on('error', (error) => {
            console.error('WebSocket error:', error);
            this.connectionState = ConnectionState.ERROR;
            this._emitStateChange();
        });

        // Server events
        this.socket.on('connected', (data) => {
            console.log('Server confirmed connection:', data);
        });

        this.socket.on('metric_update', (data) => {
            this._emit('metric_update', data);
        });

        this.socket.on('dashboard_update', (data) => {
            this._emit('dashboard_update', data);
        });

        this.socket.on('subscribed', (data) => {
            this._emit('subscribed', data);
        });

        this.socket.on('unsubscribed', (data) => {
            this._emit('unsubscribed', data);
        });

        this.socket.on('pong', (data) => {
            this._emit('pong', data);
        });
    }

    /**
     * Emit event to listeners
     * @private
     */
    _emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} listener:`, error);
                }
            });
        }
    }

    /**
     * Emit state change event
     * @private
     */
    _emitStateChange() {
        this._emit('state_change', this.connectionState);
    }
}

/**
 * Global WebSocket client instance
 */
export const wsClient = new WebSocketClient();

/**
 * Auto-connect hook for Vue components
 *
 * @param {Function} onMetricUpdate - Callback for metric updates
 * @param {Function} onStateChange - Callback for connection state changes
 * @returns {Object} - WebSocket client instance and helper functions
 */
export function useWebSocket(onMetricUpdate = null, onStateChange = null) {
    // Connect if not already connected
    if (!wsClient.isConnected()) {
        wsClient.connect();
    }

    // Register listeners
    if (onMetricUpdate) {
        wsClient.on('metric_update', onMetricUpdate);
    }

    if (onStateChange) {
        wsClient.on('state_change', onStateChange);
    }

    return {
        client: wsClient,
        subscribe: (metrics, dashboardId) => wsClient.subscribe(metrics, dashboardId),
        unsubscribe: (metrics, dashboardId) => wsClient.unsubscribe(metrics, dashboardId),
        disconnect: () => wsClient.disconnect(),
        isConnected: () => wsClient.isConnected(),
        getState: () => wsClient.getState()
    };
}

export default wsClient;
