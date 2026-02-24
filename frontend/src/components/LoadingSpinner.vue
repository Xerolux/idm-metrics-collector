<script setup>
// Xerolux 2026
import { defineProps } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md' // sm, md, lg, xl, 2xl, 3xl
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
  xl: 'w-12 h-12 text-xl',
  '2xl': 'w-16 h-16 text-2xl',
  '3xl': 'w-24 h-24 text-3xl'
}
</script>

<template>
  <div
    class="flex items-center justify-center"
    role="status"
    :aria-label="!text ? 'Laden...' : undefined"
  >
    <div :class="['animate-spin text-primary-500', sizeClasses[props.size]]">
      <i class="pi pi-spinner" aria-hidden="true"></i>
    </div>
    <span v-if="text" class="ml-2 text-gray-500 font-medium">{{ text }}</span>
  </div>
</template>
