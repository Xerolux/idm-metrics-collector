<script setup>
import { computed } from 'vue'

const props = defineProps({
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '1rem'
  },
  class: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'rect' // rect, circle, text
  }
})

const computedClass = computed(() => {
  const baseClass = 'animate-pulse bg-gray-700 rounded'
  const variantClass =
    {
      rect: '',
      circle: 'rounded-full',
      text: 'h-4'
    }[props.variant] || ''

  return `${baseClass} ${variantClass} ${props.class}`
})

const computedStyle = computed(() => {
  const style = {}
  if (props.width && props.width !== '100%') style.width = props.width
  if (props.height && props.height !== '1rem') style.height = props.height
  return style
})
</script>

<template>
  <div :class="computedClass" :style="computedStyle"></div>
</template>
