// Xerolux 2026
/**
 * Application constants
 * Centralized configuration values to avoid magic numbers
 */

// API Timeouts (in milliseconds)
export const API_TIMEOUT = {
  DEFAULT: 15000,      // Default API request timeout
  SHORT: 1000,         // Short timeout for quick requests
  MEDIUM: 10000,       // Medium timeout for standard operations
  LONG: 20000,         // Long timeout for heavy operations
  RETRY_DELAY: 1000    // Initial delay before retry
}

// Retry Configuration
export const RETRY_CONFIG = {
  MAX_RETRIES: 3,          // Maximum number of retry attempts
  INITIAL_DELAY: 1000,     // Initial delay in milliseconds
  MAX_DELAY: 10000         // Maximum delay between retries
}

// WebSocket Configuration
export const WEBSOCKET_CONFIG = {
  MAX_RECONNECT_ATTEMPTS: 10,    // Maximum reconnection attempts
  RECONNECT_DELAY: 30000,        // Delay between reconnect attempts
  RECONNECT_BACKOFF: 100,        // Backoff multiplier
  MAX_BACKOFF_DELAY: 60000,      // Maximum backoff delay
  PING_INTERVAL: 25000           // WebSocket ping interval
}

// Dashboard Configuration
export const DASHBOARD_CONFIG = {
  AUTO_REFRESH_INTERVAL: 300000,  // Auto-refresh interval (5 minutes)
  DATA_FETCH_INTERVAL: 60000,     // Data fetch interval (1 minute)
  CHART_UPDATE_INTERVAL: 1000,    // Chart update interval (1 second)
  MAX_CACHE_SIZE: 100,            // Maximum cache size
  CSS_MAX_LENGTH: 50000           // Maximum CSS length for sanitization
}

// File Upload Configuration
export const FILE_UPLOAD = {
  MAX_SIZE_MB: 10,                // Maximum file size in MB
  MAX_SIZE_BYTES: 10 * 1024 * 1024,  // Maximum file size in bytes
  ALLOWED_EXTENSIONS: ['.json', '.yaml', '.yml', '.csv']  // Allowed file extensions
}

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,          // Default items per page
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100]  // Available page size options
}

// Animation Durations (in milliseconds)
export const ANIMATION_DURATION = {
  FAST: 150,       // Fast animation
  NORMAL: 300,     // Normal animation
  SLOW: 500        // Slow animation
}

// Breakpoints (in pixels)
export const BREAKPOINTS = {
  SM: 640,         // Small screens
  MD: 768,         // Medium screens
  LG: 1024,        // Large screens
  XL: 1280,        // Extra large screens
  '2XL': 1536      // 2X large screens
}
