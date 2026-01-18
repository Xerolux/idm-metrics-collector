import { defineStore } from 'pinia'

const editModeStorageKey = 'dashboard_edit_mode'

export const useUiStore = defineStore('ui', {
  state: () => ({
    editMode: false,
    initialized: false
  }),
  actions: {
    init() {
      if (this.initialized) return
      if (typeof window !== 'undefined') {
        const stored = window.localStorage.getItem(editModeStorageKey)
        this.editMode = stored === 'true'
      }
      this.initialized = true
    },
    setEditMode(value) {
      this.editMode = value
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(editModeStorageKey, `${value}`)
      }
    },
    toggleEditMode() {
      this.setEditMode(!this.editMode)
    }
  }
})
