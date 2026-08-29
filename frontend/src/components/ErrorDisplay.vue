<script setup>
// Xerolux 2026
import { defineProps, computed } from 'vue'

const props = defineProps({
  error: {
    type: [String, Object],
    required: true
  },
  variant: {
    type: String,
    default: 'error' // error, warning, info
  },
  dismissible: {
    type: Boolean,
    default: true
  }
})

defineEmits(['dismiss'])

const errorType = computed(() => {
  if (props.error?.response) {
    return 'network'
  }
  if (props.error?.message) {
    return 'javascript'
  }
  return 'string'
})

const errorMessage = computed(() => {
  if (typeof props.error === 'string') {
    return props.error
  }

  if (props.error?.response?.data?.error) {
    return props.error.response.data.error
  }

  if (props.error?.response?.status === 401) {
    return 'Nicht autorisiert. Bitte melden Sie sich erneut an.'
  }

  if (props.error?.response?.status === 404) {
    return 'Ressource nicht gefunden.'
  }

  if (props.error?.response?.status >= 500) {
    return 'Server-Fehler. Bitte versuchen Sie es später erneut.'
  }

  if (props.error?.message) {
    return props.error.message
  }

  return 'Ein unerwarteter Fehler ist aufgetreten.'
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'warning':
      return 'bg-warning-900/20 border-warning-600/50 text-warning-200'
    case 'info':
      return 'bg-info-900/20 border-info-600/50 text-info-200'
    default:
      return 'bg-error-900/20 border-error-600/50 text-error-200'
  }
})

const iconClasses = computed(() => {
  switch (props.variant) {
    case 'warning':
      return 'pi pi-exclamation-triangle'
    case 'info':
      return 'pi pi-info-circle'
    default:
      return 'pi pi-times-circle'
  }
})
</script>

<template>
  <div
    :class="['rounded-lg border p-4 animate-slide-up', variantClasses]"
    :role="variant === 'error' ? 'alert' : 'status'"
    :aria-live="variant === 'error' ? 'assertive' : 'polite'"
  >
    <div class="flex items-start gap-3">
      <i :class="[iconClasses, 'text-lg mt-0.5']" aria-hidden="true"></i>
      <div class="flex-1">
        <div class="font-medium mb-1">
          <template v-if="variant === 'error'">Fehler</template>
          <template v-else-if="variant === 'warning'">Warnung</template>
          <template v-else>Information</template>
        </div>
        <div class="text-sm opacity-90">{{ errorMessage }}</div>
        <div
          v-if="errorType === 'network' && error?.response?.status"
          class="text-xs opacity-70 mt-1"
        >
          Status-Code: {{ error.response.status }}
        </div>
      </div>
      <button
        type="button"
        v-if="dismissible"
        @click="$emit('dismiss')"
        class="text-gray-400 hover:text-white transition-colors p-1 rounded hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-gray-500"
        aria-label="Schließen"
      >
        <i class="pi pi-times" aria-hidden="true"></i>
      </button>
    </div>
  </div>
</template>
