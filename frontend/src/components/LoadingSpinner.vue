<script setup>
// Xerolux 2026
import { defineProps } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md' // sm, md, lg, xl
  },
  text: {
    type: String,
    default: ''
  }
})

const sizeClasses = {
  sm: 'w-4 h-4 text-sm',
  md: 'w-6 h-6 text-base',
  lg: 'w-8 h-8 text-lg',
  xl: 'w-12 h-12 text-xl'
}
</script>

<template>
  <div class="flex items-center justify-center" role="status" aria-live="polite">
    <div :class="['animate-spin text-primary-500', sizeClasses[props.size]]" aria-hidden="true">
      <i class="pi pi-spinner"></i>
    </div>
    <span v-if="text" class="ml-2 text-gray-400">{{ text }}</span>
    <span v-else class="sr-only">Laden...</span>
  </div>
</template>
