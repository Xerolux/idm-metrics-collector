<script setup>
// Xerolux 2026
import { ref, onMounted, onUnmounted, watch } from 'vue'

const isBrowserOnline = ref(navigator.onLine)
const isBackendOnline = ref(false)
const showOfflineBanner = ref(!navigator.onLine)

// Check backend connectivity
const checkBackendHealth = async () => {
  try {
    const response = await fetch('/api/health', {
      method: 'GET',
      cache: 'no-cache',
      timeout: 5000
    })
    isBackendOnline.value = response.ok
  } catch (error) {
    console.error(error)
    isBackendOnline.value = false
  }
}

// Combined online status
const isOnline = ref(isBrowserOnline.value && isBackendOnline.value)

// Listen for browser online/offline events
const handleBrowserOnline = () => {
  isBrowserOnline.value = true
  checkBackendHealth()
}

const handleBrowserOffline = () => {
  isBrowserOnline.value = false
  isOnline.value = false
  showOfflineBanner.value = true
}

// Update combined status
const updateOnlineStatus = () => {
  const wasOnline = isOnline.value
  isOnline.value = isBrowserOnline.value && isBackendOnline.value

  // Show offline banner if we went offline
  if (wasOnline && !isOnline.value) {
    showOfflineBanner.value = true
  } else if (!wasOnline && isOnline.value) {
    showOfflineBanner.value = false
  }
}

window.addEventListener('online', handleBrowserOnline)
window.addEventListener('offline', handleBrowserOffline)

// Check backend status periodically
let healthCheckInterval
onMounted(() => {
  checkBackendHealth()
  healthCheckInterval = setInterval(checkBackendHealth, 30000) // Check every 30 seconds
})

onUnmounted(() => {
  clearInterval(healthCheckInterval)
  window.removeEventListener('online', handleBrowserOnline)
  window.removeEventListener('offline', handleBrowserOffline)
})

// Get status text for tooltip
const getStatusText = () => {
  if (!isBrowserOnline.value) return 'Browser Offline'
  if (!isBackendOnline.value) return 'Backend Offline'
  return 'Online'
}

// Watch for backend status changes and update combined status
watch([isBrowserOnline, isBackendOnline], () => {
  updateOnlineStatus()
})
</script>

<template>
  <!-- Offline Banner -->
  <Transition name="slide-down">
    <div
      v-if="showOfflineBanner"
      class="fixed top-0 left-0 right-0 bg-warning-900 border-b border-warning-600 text-warning-200 p-3 z-50"
    >
      <div class="container mx-auto flex items-center gap-2">
        <i class="pi pi-wifi-slash"></i>
        <span class="text-sm font-medium">
          {{
            !isBrowserOnline
              ? 'Browser Offline - Keine Internetverbindung'
              : 'Backend Offline - Server nicht erreichbar'
          }}
        </span>
      </div>
    </div>
  </Transition>

  <!-- Connection Status Indicator -->
  <div class="fixed bottom-4 right-4 z-40">
    <div
      :class="[
        'w-3 h-3 rounded-full border-2 border-gray-700',
        isOnline ? 'bg-success-500' : isBrowserOnline ? 'bg-warning-500' : 'bg-error-500'
      ]"
      :title="getStatusText()"
    ></div>
  </div>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
