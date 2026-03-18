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
        const response = await api.post('/api/auth/login', { password })
        if (response.data.requires_password_change) {
          this.isAuthenticated = false
          return {
            success: true,
            requiresPasswordChange: true
          }
        }

        this.isAuthenticated = true
        return {
          success: true,
          requiresPasswordChange: false
        }
      } catch (e) {
        console.error('Login failed:', e)
        this.error = e.message
        return { success: false, requiresPasswordChange: false }
      } finally {
        this.loading = false
      }
    },
    async logout() {
      this.loading = true
      try {
        await api.get('/api/auth/logout')
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
