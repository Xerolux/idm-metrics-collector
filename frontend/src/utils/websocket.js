// Xerolux 2026
/**
 * WebSocket Client for real-time metric updates.
 *
 * Provides automatic reconnection, subscription management,
 * and event handling for WebSocket connections.
 */

import { io } from 'socket.io-client'
import { WEBSOCKET_CONFIG } from './constants'

export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error'
}

export class WebSocketClient {
  constructor() {
    this.socket = null
    this.connectionState = ConnectionState.DISCONNECTED
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = WEBSOCKET_CONFIG.MAX_RECONNECT_ATTEMPTS
    this.reconnectDelay = WEBSOCKET_CONFIG.RECONNECT_BACKOFF
    this.maxReconnectDelay = WEBSOCKET_CONFIG.MAX_BACKOFF_DELAY
    this.listeners = new Map()
    this.subscriptions = new Set()
    this.dashboardId = null
    this._metricUpdateBuffer = {}
    this._metricUpdateTimer = null
    this._metricUpdateDebounceMs = 100
    this._connectionQuality = 'good'
    this._lastPongTime = null
    this._pingInterval = null
    this._pendingSubscriptions = []
    this._isIntentionallyDisconnected = false
  }

  _handleMetricUpdate(data) {
    if (data && data.metric) {
      this._metricUpdateBuffer[data.metric] = data
    } else if (data) {
      Object.assign(this._metricUpdateBuffer, data)
    }

    if (this._metricUpdateTimer) {
      clearTimeout(this._metricUpdateTimer)
    }

    this._metricUpdateTimer = setTimeout(() => {
      const bufferedData = this._metricUpdateBuffer
      this._metricUpdateBuffer = {}
      this._metricUpdateTimer = null

      if (Object.keys(bufferedData).length > 0) {
        this._emit('metric_update', bufferedData)
      }
    }, this._metricUpdateDebounceMs)
  }

  _startPingMonitor() {
    this._stopPingMonitor()

    this._pingInterval = setInterval(() => {
      if (this.socket?.connected) {
        const now = Date.now()
        if (this._lastPongTime && now - this._lastPongTime > WEBSOCKET_CONFIG.MAX_BACKOFF_DELAY) {
          this._connectionQuality = 'poor'
          this._emit('quality_change', 'poor')
        }
        this.ping()
      }
    }, WEBSOCKET_CONFIG.PING_INTERVAL)
  }

  _stopPingMonitor() {
    if (this._pingInterval) {
      clearInterval(this._pingInterval)
      this._pingInterval = null
    }
  }

  connect(url = null, options = {}) {
    if (this.socket?.connected || this.connectionState === ConnectionState.CONNECTING) {
      return
    }

    // Clean up any leftover disconnected socket before creating a new one
    // (prevents listener leaks / duplicate emissions after error states).
    if (this.socket) {
      this.socket.removeAllListeners()
      this.socket.disconnect()
      this.socket = null
    }

    this._isIntentionallyDisconnected = false
    this.connectionState = ConnectionState.CONNECTING
    this._emitStateChange()

    const defaultOptions = {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      reconnectionDelayMax: this.maxReconnectDelay,
      timeout: 20000,
      forceNew: false,
      ...options
    }

    this.socket = io(url || window.location.origin, defaultOptions)
    this._setupEventHandlers()
  }

  disconnect() {
    this._isIntentionallyDisconnected = true
    this._stopPingMonitor()

    if (this._metricUpdateTimer) {
      clearTimeout(this._metricUpdateTimer)
      this._metricUpdateTimer = null
    }
    this._metricUpdateBuffer = {}

    if (this.socket) {
      this.socket.removeAllListeners()
      this.socket.disconnect()
      this.socket = null
    }
    this.connectionState = ConnectionState.DISCONNECTED
    this.subscriptions.clear()
    this._pendingSubscriptions = []
    this.dashboardId = null
    this._emitStateChange()
  }

  subscribe(metrics, dashboardId = null) {
    const newMetrics = metrics.filter((m) => !this.subscriptions.has(m))
    newMetrics.forEach((m) => this.subscriptions.add(m))

    if (dashboardId) {
      this.dashboardId = dashboardId
    }

    if (!this.socket?.connected) {
      this._pendingSubscriptions.push({ metrics: newMetrics, dashboardId })
      return
    }

    if (newMetrics.length > 0) {
      this.socket.emit('subscribe', {
        metrics: newMetrics,
        dashboard_id: dashboardId
      })
    }
  }

  unsubscribe(metrics, dashboardId = null) {
    metrics.forEach((m) => this.subscriptions.delete(m))

    if (!this.socket?.connected) {
      return
    }

    this.socket.emit('unsubscribe', {
      metrics,
      dashboard_id: dashboardId
    })
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (!this.listeners.has(event)) {
      return
    }
    const listeners = this.listeners.get(event)
    const index = listeners.indexOf(callback)
    if (index > -1) {
      listeners.splice(index, 1)
    }
  }

  ping() {
    if (this.socket?.connected) {
      this.socket.emit('ping')
    }
  }

  getState() {
    return this.connectionState
  }

  isConnected() {
    return this.connectionState === ConnectionState.CONNECTED
  }

  getConnectionQuality() {
    return this._connectionQuality
  }

  getSubscriptions() {
    return new Set(this.subscriptions)
  }

  _setupEventHandlers() {
    this.socket.on('connect', () => {
      this.connectionState = ConnectionState.CONNECTED
      this.reconnectAttempts = 0
      this._connectionQuality = 'good'
      this._lastPongTime = Date.now()
      this._emitStateChange()
      this._startPingMonitor()

      if (this.subscriptions.size > 0 || this.dashboardId) {
        this.socket.emit('subscribe', {
          metrics: Array.from(this.subscriptions),
          dashboard_id: this.dashboardId
        })
      }

      while (this._pendingSubscriptions.length > 0) {
        const pending = this._pendingSubscriptions.shift()
        if (pending.metrics.length > 0) {
          this.socket.emit('subscribe', {
            metrics: pending.metrics,
            dashboard_id: pending.dashboardId || this.dashboardId
          })
        }
      }
    })

    this.socket.on('disconnect', (reason) => {
      this._stopPingMonitor()
      this.connectionState = ConnectionState.DISCONNECTED
      this._emit('disconnected', { reason })
      this._emitStateChange()
    })

    this.socket.io.on('reconnect', (attemptNumber) => {
      this.connectionState = ConnectionState.CONNECTED
      this.reconnectAttempts = 0
      this._emit('reconnected', { attempts: attemptNumber })
      this._emitStateChange()
    })

    this.socket.io.on('reconnect_attempt', (attemptNumber) => {
      this.connectionState = ConnectionState.RECONNECTING
      this.reconnectAttempts = attemptNumber
      this._emitStateChange()
    })

    this.socket.io.on('reconnect_failed', () => {
      this.connectionState = ConnectionState.ERROR
      this._emit('reconnect_failed')
      this._emitStateChange()
    })

    this.socket.on('connect_error', (error) => {
      this.connectionState = ConnectionState.ERROR
      this._emit('error', { message: error.message })
      this._emitStateChange()
    })

    this.socket.on('error', (error) => {
      this._emit('error', { message: error })
    })

    this.socket.on('connected', () => {
      this._emit('server_connected')
    })

    this.socket.on('metric_update', (data) => {
      this._handleMetricUpdate(data)
    })

    this.socket.on('dashboard_update', (data) => {
      this._emit('dashboard_update', data)
    })

    this.socket.on('subscribed', (data) => {
      this._emit('subscribed', data)
    })

    this.socket.on('unsubscribed', (data) => {
      this._emit('unsubscribed', data)
    })

    this.socket.on('pong', (data) => {
      this._lastPongTime = Date.now()
      this._connectionQuality = 'good'
      this._emit('pong', data)
    })
  }

  _emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in ${event} listener:`, error)
        }
      })
    }
  }

  _emitStateChange() {
    this._emit('state_change', {
      state: this.connectionState,
      reconnectAttempts: this.reconnectAttempts,
      quality: this._connectionQuality
    })
  }
}

export const wsClient = new WebSocketClient()

export function useWebSocket(onMetricUpdate = null, onStateChange = null) {
  if (!wsClient.isConnected() && !wsClient._isIntentionallyDisconnected) {
    wsClient.connect()
  }

  const registeredListeners = []

  if (onMetricUpdate) {
    wsClient.on('metric_update', onMetricUpdate)
    registeredListeners.push(['metric_update', onMetricUpdate])
  }

  if (onStateChange) {
    wsClient.on('state_change', onStateChange)
    registeredListeners.push(['state_change', onStateChange])
  }

  const cleanup = () => {
    registeredListeners.forEach(([event, callback]) => {
      wsClient.off(event, callback)
    })
    registeredListeners.length = 0
  }

  return {
    client: wsClient,
    subscribe: (metrics, dashboardId) => wsClient.subscribe(metrics, dashboardId),
    unsubscribe: (metrics, dashboardId) => wsClient.unsubscribe(metrics, dashboardId),
    disconnect: () => wsClient.disconnect(),
    isConnected: () => wsClient.isConnected(),
    getState: () => wsClient.getState(),
    getQuality: () => wsClient.getConnectionQuality(),
    cleanup
  }
}

export default wsClient
