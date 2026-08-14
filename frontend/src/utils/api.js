// Xerolux 2026
import axios from 'axios'
import { API_TIMEOUT, RETRY_CONFIG } from './constants'

const api = axios.create({
  baseURL: '',
  timeout: API_TIMEOUT.DEFAULT,
  headers: {
    'Content-Type': 'application/json'
  }
})

let isRefreshing = false
let failedQueue = []
const MAX_CACHE_SIZE = 100
const getRequestCache = new Map()

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use(
  (config) => {
    // Ensure non-idempotent requests are never cached by browsers/proxies
    if (['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase())) {
      config.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
      config.headers['Pragma'] = 'no-cache'
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout:', originalRequest.url)
      return Promise.reject(new Error('Zeitüberschreitung - Server antwortet nicht'))
    }

    if (!error.response) {
      console.error('Network error:', error.message)
      return Promise.reject(new Error('Netzwerkfehler - Server nicht erreichbar'))
    }

    if (error.response.status === 401 && !originalRequest._retry) {
      const url = originalRequest.url || ''
      // Auth endpoints use 401 as an expected result (wrong password, wrong
      // security answer). Do not attempt a session refresh or force-logout;
      // surface the backend message to the caller directly.
      const isAuthEndpoint =
        url === '/api/auth/check' ||
        url === '/api/auth/login' ||
        url === '/api/auth/reset_password' ||
        url === '/api/auth/change_password'
      if (isAuthEndpoint) {
        if (url === '/api/auth/check' && typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth:logout'))
        }
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await api.get('/api/auth/check')
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth:logout'))
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    const rawMessage = error.response?.data?.error || error.response?.data?.message || error.message
    return Promise.reject(new Error(sanitizeErrorMessage(rawMessage)))
  }
)

export const retryRequest = async (requestFn, maxRetries = RETRY_CONFIG.MAX_RETRIES, delay = RETRY_CONFIG.INITIAL_DELAY) => {
  let lastError

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error
      if (error.message?.includes('401') || error.message?.includes('403')) {
        throw error
      }
      if (i < maxRetries - 1) {
        await new Promise((resolve) => setTimeout(resolve, delay * Math.pow(2, i)))
      }
    }
  }

  throw lastError
}

export const withTimeout = (promise, ms = API_TIMEOUT.MEDIUM) => {
  let timeoutId
  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error('Operation timed out')), ms)
  })
  return Promise.race([
    Promise.resolve(promise).finally(() => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }),
    timeoutPromise
  ])
}

const sanitizeErrorMessage = (raw) => {
  if (raw == null) return 'Unbekannter Fehler'
  let message = typeof raw === 'string' ? raw : String(raw)
  // Strip HTML tags that reverse proxies may return (e.g. 502 pages)
  message = message.replace(/<[^>]*>/g, ' ')
  // Collapse whitespace
  message = message.replace(/\s+/g, ' ').trim()
  // Limit length to avoid huge error banners
  return message.length > 200 ? `${message.slice(0, 200)}…` : message
}

const buildGetCacheKey = (url, config = {}) => {
  const params = config?.params ? JSON.stringify(config.params) : ''
  return `${url}::${params}`
}

// Deduplicate identical GET requests for a short window to reduce chart burst load.
export const cachedGet = (url, config = {}, cacheMs = 1500) => {
  const key = buildGetCacheKey(url, config)
  const now = Date.now()
  const cached = getRequestCache.get(key)

  if (cached && cached.expiresAt > now) {
    return cached.promise
  }

  const requestPromise = api.get(url, config).finally(() => {
    const entry = getRequestCache.get(key)
    if (entry && entry.promise === requestPromise) {
      setTimeout(() => {
        const current = getRequestCache.get(key)
        if (current && current.promise === requestPromise) {
          getRequestCache.delete(key)
        }
      }, cacheMs)
    }
  })

  if (getRequestCache.size >= MAX_CACHE_SIZE) {
    const oldestKey = getRequestCache.keys().next().value
    getRequestCache.delete(oldestKey)
  }

  getRequestCache.set(key, {
    promise: requestPromise,
    expiresAt: now + cacheMs
  })

  return requestPromise
}

export default api
