<script setup>
import { onErrorCaptured, onMounted, onUnmounted, ref } from 'vue'
import { useUiStore } from './stores/ui'
import { useAuthStore } from './stores/auth'

const uiStore = useUiStore()
const authStore = useAuthStore()
const hasError = ref(false)
const errorMessage = ref('')

const handleAuthLogout = () => {
  authStore.isAuthenticated = false
}

onMounted(() => {
  uiStore.init()
  window.addEventListener('auth:logout', handleAuthLogout)
})

onUnmounted(() => {
  window.removeEventListener('auth:logout', handleAuthLogout)
})

onErrorCaptured((error) => {
  console.error('Unhandled component error:', error)
  hasError.value = true
  errorMessage.value = error.message || 'An unexpected error occurred'
  return false
})
</script>

<template>
  <div class="min-h-screen text-white">
    <div v-if="hasError" class="flex items-center justify-center min-h-screen">
      <div class="text-center p-8 max-w-md">
        <h2 class="text-xl font-semibold text-red-400 mb-4">Something went wrong</h2>
        <p class="text-gray-400 mb-6">{{ errorMessage }}</p>
        <button
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
          @click="
            hasError = false
            errorMessage = ''
          "
        >
          Retry
        </button>
      </div>
    </div>
    <router-view v-else></router-view>
  </div>
</template>

<style></style>
