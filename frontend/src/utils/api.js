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

    const message = error.response?.data?.error || error.response?.data?.message || error.message
    return Promise.reject(new Error(message))
  }
)

export const retryRequest = async (
  requestFn,
  maxRetries = RETRY_CONFIG.MAX_RETRIES,
  delay = RETRY_CONFIG.INITIAL_DELAY
) => {
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
        await new Promise((resolve) => setTimeout(resolve, delay * (i + 1)))
      }
    }
  }

  throw lastError
}

export const withTimeout = (promise, ms = API_TIMEOUT.MEDIUM) => {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error('Operation timed out')), ms))
  ])
}

export default api
