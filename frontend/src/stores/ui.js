// Xerolux 2026
import { defineStore } from 'pinia'

const editModeStorageKey = 'dashboard_edit_mode'
const darkModeStorageKey = 'dashboard_dark_mode'

export const useUiStore = defineStore('ui', {
  state: () => ({
    editMode: false,
    darkMode: false,
    initialized: false,
    darkModeMediaQuery: null
  }),
  actions: {
    init() {
      if (this.initialized) return
      if (typeof window !== 'undefined') {
        const stored = window.localStorage.getItem(editModeStorageKey)
        this.editMode = stored === 'true'

        // Check dark mode preference
        const storedDarkMode = window.localStorage.getItem(darkModeStorageKey)
        if (storedDarkMode !== null) {
          this.darkMode = storedDarkMode === 'true'
        } else {
          // Default to system preference
          this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
        }

        // Listen for system preference changes (store reference for cleanup)
        this.darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        this._darkModeChangeListener = (e) => {
          if (window.localStorage.getItem(darkModeStorageKey) === null) {
            this.darkMode = e.matches
          }
        }
        this.darkModeMediaQuery.addEventListener('change', this._darkModeChangeListener)
      }
      this.initialized = true
    },
    cleanup() {
      if (this.darkModeMediaQuery && this._darkModeChangeListener) {
        this.darkModeMediaQuery.removeEventListener('change', this._darkModeChangeListener)
        this.darkModeMediaQuery = null
        this._darkModeChangeListener = null
      }
      this.initialized = false
    },
    setEditMode(value) {
      this.editMode = value
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(editModeStorageKey, `${value}`)
      }
    },
    toggleEditMode() {
      this.setEditMode(!this.editMode)
    },
    setDarkMode(value) {
      this.darkMode = value
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(darkModeStorageKey, `${value}`)
      }
      if (value) {
        document.documentElement.classList.add('my-app-dark')
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('my-app-dark')
        document.documentElement.classList.remove('dark')
      }
    },
    toggleDarkMode() {
      this.setDarkMode(!this.darkMode)
    }
  }
})
