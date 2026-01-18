<script setup>
import { computed } from 'vue'
import SkeletonLoader from './SkeletonLoader.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  count: {
    type: Number,
    default: 3
  },
  variant: {
    type: String,
    default: 'card' // card, list, table
  }
})

const skeletonItems = computed(() => Array.from({ length: props.count }, (_, i) => i))
</script>

<template>
  <div v-if="variant === 'card'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div v-for="i in skeletonItems" :key="i" class="bg-gray-800 rounded-lg p-4 animate-fade-in">
      <SkeletonLoader height="1.5rem" width="80%" class="mb-3" />
      <SkeletonLoader height="0.875rem" width="60%" class="mb-2" />
      <SkeletonLoader height="2rem" width="100%" class="mb-2" />
      <SkeletonLoader height="2.5rem" width="40%" />
    </div>
  </div>

  <div v-else-if="variant === 'list'" class="space-y-3">
    <div v-for="i in skeletonItems" :key="i" class="bg-gray-800 rounded-lg p-4 animate-fade-in">
      <div class="flex items-center gap-3">
        <SkeletonLoader variant="circle" width="2rem" height="2rem" />
        <div class="flex-1">
          <SkeletonLoader height="1rem" width="70%" class="mb-2" />
          <SkeletonLoader height="0.75rem" width="50%" />
        </div>
        <SkeletonLoader width="4rem" height="2rem" />
      </div>
    </div>
  </div>

  <div v-else-if="variant === 'table'" class="bg-gray-800 rounded-lg overflow-hidden">
    <div class="border-b border-gray-700 p-4">
      <SkeletonLoader height="1.5rem" width="30%" />
    </div>
    <div v-for="i in skeletonItems" :key="i" class="border-b border-gray-700 p-4">
      <div class="grid grid-cols-4 gap-4">
        <SkeletonLoader height="1rem" width="80%" />
        <SkeletonLoader height="1rem" width="90%" />
        <SkeletonLoader height="1rem" width="60%" />
        <SkeletonLoader height="1rem" width="40%" />
      </div>
    </div>
  </div>
</template>
