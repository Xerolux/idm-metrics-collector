<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  itemHeight: {
    type: Number,
    default: 60
  },
  containerHeight: {
    type: Number,
    default: 400
  },
  renderItem: {
    type: Function,
    required: true
  }
})

const scrollTop = ref(0)
const containerRef = ref(null)

const totalHeight = computed(() => props.items.length * props.itemHeight)
const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight))
const startIndex = computed(() => Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - 1))
const endIndex = computed(() =>
  Math.min(props.items.length - 1, startIndex.value + visibleCount.value + 2)
)

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value + 1).map((item, index) => ({
    item,
    index: startIndex.value + index,
    style: {
      position: 'absolute',
      top: `${(startIndex.value + index) * props.itemHeight}px`,
      width: '100%',
      height: `${props.itemHeight}px`
    }
  }))
})

const handleScroll = () => {
  if (containerRef.value) {
    scrollTop.value = containerRef.value.scrollTop
  }
}

const scrollToItem = (index) => {
  if (containerRef.value) {
    const targetScrollTop = index * props.itemHeight
    containerRef.value.scrollTop = targetScrollTop
    scrollTop.value = targetScrollTop
  }
}

// Expose method to scroll to specific item
defineExpose({
  scrollToItem
})

onMounted(() => {
  if (containerRef.value) {
    containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll)
  }
})
</script>

<template>
  <div
    class="virtual-scroller border border-gray-700 rounded-lg overflow-auto bg-gray-800"
    :style="{ height: `${containerHeight}px` }"
    ref="containerRef"
  >
    <div class="virtual-scroller-content relative" :style="{ height: `${totalHeight}px` }">
      <div
        v-for="{ item, index, style } in visibleItems"
        :key="`item-${index}`"
        :style="style"
        class="virtual-scroller-item flex items-center px-4 hover:bg-gray-700 transition-colors"
      >
        <slot :item="item" :index="index" :render-item="renderItem">
          {{ renderItem(item, index) }}
        </slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.virtual-scroller {
  scrollbar-width: thin;
  scrollbar-color: #4b5563 transparent;
}

.virtual-scroller::-webkit-scrollbar {
  width: 8px;
}

.virtual-scroller::-webkit-scrollbar-track {
  background: transparent;
}

.virtual-scroller::-webkit-scrollbar-thumb {
  background-color: #4b5563;
  border-radius: 4px;
}

.virtual-scroller::-webkit-scrollbar-thumb:hover {
  background-color: #6b7280;
}
</style>
