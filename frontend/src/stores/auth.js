import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    isSetup: true
  }),
  actions: {
    async checkAuth() {
      try {
        const authRes = await axios.get('/api/auth/check')
        this.isAuthenticated = authRes.data.authenticated
        return this.isAuthenticated
      } catch (e) {
        this.isAuthenticated = false
        return false
      }
    },
    async login(password) {
      try {
        await axios.post('/login', { password }, {
            headers: { 'Content-Type': 'application/json' }
        })
        this.isAuthenticated = true
        return true
      } catch (e) {
        return false
      }
    },
    async logout() {
      await axios.get('/logout')
      this.isAuthenticated = false
    }
  }
})
