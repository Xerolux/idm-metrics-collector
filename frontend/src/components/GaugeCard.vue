<template>
  <div class="bg-white rounded-lg p-4 shadow-sm border border-gray-200 h-full flex flex-col">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <i class="pi pi-spinner pi-spin text-gray-400"></i>
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-full text-center">
      <i class="pi pi-exclamation-triangle text-red-400 text-2xl mb-2"></i>
      <span class="text-xs text-gray-500">{{ error }}</span>
    </div>
    <div v-else class="flex flex-col h-full">
      <!-- Header -->
      <div class="text-center mb-2">
        <div class="text-xs text-gray-500 font-medium truncate" :title="title">
          {{ displayTitle }}
        </div>
      </div>

      <!-- Gauge Chart -->
      <div class="flex-grow flex items-center justify-center relative">
        <svg class="w-full h-full" viewBox="0 0 200 120">
          <!-- Background Arc -->
          <path
            :d="arcPath"
            fill="none"
            :stroke="backgroundColor"
            stroke-width="20"
            stroke-linecap="round"
          />

          <!-- Value Arc -->
          <path
            :d="arcPath"
            fill="none"
            :stroke="valueColor"
            stroke-width="20"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            class="transition-all duration-500 ease-out"
          />

          <!-- Zone Markers (optional) -->
          <g v-if="showZones">
            <line
              v-for="(zone, index) in zones"
              :key="index"
              :x1="getZoneX(zone.value)"
              :y1="getZoneY(zone.value)"
              :x2="getZoneX(zone.value, 35)"
              :y2="getZoneY(zone.value, 35)"
              :stroke="zone.color"
              stroke-width="2"
            />
          </g>

          <!-- Center Text -->
          <text x="100" y="95" text-anchor="middle" class="text-3xl font-bold" :fill="valueColor">
            {{ displayValue }}
          </text>
          <text x="100" y="110" text-anchor="middle" class="text-xs" fill="#6b7280">
            {{ unit }}
          </text>
        </svg>
      </div>

      <!-- Target/Actual Info -->
      <div v-if="showTarget && targetValue !== null" class="mt-2 pt-2 border-t border-gray-100">
        <div class="flex justify-between items-center text-[10px]">
          <span class="text-gray-500">Soll: {{ targetValue.toFixed(1) }}{{ unit }}</span>
          <span :class="diffToTarget >= 0 ? 'text-red-500' : 'text-green-500'">
            {{ diffToTarget >= 0 ? '+' : '' }}{{ diffToTarget.toFixed(1) }}
          </span>
        </div>
      </div>

      <!-- Timestamp -->
      <div v-if="timestamp" class="text-[10px] text-gray-400 text-center mt-1">
        {{ formatTimestamp(timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup>
// Xerolux 2026
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api.js'

const props = defineProps({
  title: { type: String, required: true },
  query: { type: String, required: true },
  unit: { type: String, default: '' },
  min: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  target: { type: Number, default: null },
  targetQuery: { type: String, default: null },
  decimals: { type: Number, default: 1 },
  showZones: { type: Boolean, default: false },
  showTarget: { type: Boolean, default: false },
  zones: {
    type: Array,
    default: () => [
      { value: 33, color: '#22c55e' },
      { value: 66, color: '#f59e0b' }
    ]
  }
})

const loading = ref(true)
const error = ref(null)
const currentValue = ref(null)
const targetValue = ref(null)
const timestamp = ref(null)
let interval = null

// SVG Arc Configuration
const centerX = 100
const centerY = 100
const radius = 80
const startAngle = -180 // Start from left (9 o'clock position)
const endAngle = 0 // End at right (3 o'clock position)

const displayTitle = computed(() => {
  if (props.title.length > 25) {
    return props.title.substring(0, 22) + '...'
  }
  return props.title
})

const displayValue = computed(() => {
  if (currentValue.value === null) return '-'
  return currentValue.value.toFixed(props.decimals)
})

const percentage = computed(() => {
  if (currentValue.value === null) return 0
  const range = props.max - props.min
  if (range === 0) return 0
  return Math.max(0, Math.min(100, ((currentValue.value - props.min) / range) * 100))
})

const circumference = computed(() => {
  // Semi-circle circumference
  return Math.PI * radius
})

const dashOffset = computed(() => {
  return circumference.value * (1 - percentage.value / 100)
})

const arcPath = computed(() => {
  // Create semi-circle arc path
  const startX = centerX + radius * Math.cos((startAngle * Math.PI) / 180)
  const startY = centerY + radius * Math.sin((startAngle * Math.PI) / 180)
  const endX = centerX + radius * Math.cos((endAngle * Math.PI) / 180)
  const endY = centerY + radius * Math.sin((endAngle * Math.PI) / 180)

  return `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`
})

const valueColor = computed(() => {
  if (currentValue.value === null) return '#9ca3af'

  // Zone-based coloring
  if (props.showZones && props.zones.length > 0) {
    const sortedZones = [...props.zones].sort((a, b) => a.value - b.value)
    for (const zone of sortedZones) {
      if (percentage.value <= zone.value) {
        return zone.color
      }
    }
    return '#ef4444' // Red if above all zones
  }

  // Default: Green if in middle range, red if at extremes
  if (percentage.value < 20 || percentage.value > 80) return '#ef4444'
  if (percentage.value < 40 || percentage.value > 60) return '#f59e0b'
  return '#22c55e'
})

const backgroundColor = computed(() => '#e5e7eb')

const diffToTarget = computed(() => {
  if (targetValue.value === null || currentValue.value === null) return 0
  return currentValue.value - targetValue.value
})

const getZoneX = (value, r = radius) => {
  const range = props.max - props.min
  const pct = Math.max(0, Math.min(100, ((value - props.min) / range) * 100))
  const angle = startAngle + (pct / 100) * (endAngle - startAngle)
  return centerX + r * Math.cos((angle * Math.PI) / 180)
}

const getZoneY = (value, r = radius) => {
  const range = props.max - props.min
  const pct = Math.max(0, Math.min(100, ((value - props.min) / range) * 100))
  const angle = startAngle + (pct / 100) * (endAngle - startAngle)
  return centerY + r * Math.sin((angle * Math.PI) / 180)
}

const formatTimestamp = (ts) => {
  if (!ts) return ''
  const date = new Date(ts)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return 'Gerade eben'
  if (diff < 3600000) return `vor ${Math.floor(diff / 60000)} Min.`
  if (diff < 86400000) return `vor ${Math.floor(diff / 3600000)} Std.`
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchData = async () => {
  try {
    // Fetch current value
    const currentRes = await api.get('/api/metrics/query_range', {
      params: {
        query: props.query,
        start: Math.floor((Date.now() - 300000) / 1000),
        end: Math.floor(Date.now() / 1000),
        step: 60
      }
    })

    if (currentRes.data?.data?.result?.[0]?.values) {
      const values = currentRes.data.data.result[0].values
      if (values.length > 0) {
        const lastValue = values[values.length - 1]
        currentValue.value = parseFloat(lastValue[1])
        timestamp.value = lastValue[0] * 1000
      }
    }

    // Fetch target value if query provided
    if (props.showTarget && props.targetQuery) {
      const targetRes = await api.get('/api/metrics/query', {
        params: { query: props.targetQuery }
      })

      if (targetRes.data?.data?.result?.[0]?.value?.[1]) {
        targetValue.value = parseFloat(targetRes.data.data.result[0].value[1])
      }
    } else if (props.showTarget && props.target !== null) {
      targetValue.value = props.target
    }

    error.value = null
  } catch (e) {
    console.error('GaugeCard fetch error:', e)
    error.value = 'Ladefehler'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  interval = setInterval(fetchData, 30000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})
</script>

<style scoped>
/* Add smooth transitions */
path {
  transition:
    stroke-dashoffset 0.5s ease-out,
    stroke 0.3s ease;
}
</style>
