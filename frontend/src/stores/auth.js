// Xerolux 2026
import { defineStore } from 'pinia'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    isSetup: true,
    loading: false,
    error: null
  }),
  actions: {
    async checkAuth() {
      this.loading = true
      this.error = null
      try {
        const authRes = await api.get('/api/auth/check')
        this.isAuthenticated = authRes.data.authenticated
        return this.isAuthenticated
      } catch (e) {
        console.error('Auth check failed:', e)
        this.isAuthenticated = false
        this.error = e.message
        return false
      } finally {
        this.loading = false
      }
    },
    async login(password) {
      this.loading = true
      this.error = null
      try {
        await api.post('/login', { password })
        this.isAuthenticated = true
        return true
      } catch (e) {
        console.error('Login failed:', e)
        this.error = e.message
        return false
      } finally {
        this.loading = false
      }
    },
    async logout() {
      this.loading = true
      try {
        await api.get('/logout')
      } catch (e) {
        console.error('Logout error:', e)
      } finally {
        this.isAuthenticated = false
        this.loading = false
      }
    },
    clearError() {
      this.error = null
    }
  }
})
