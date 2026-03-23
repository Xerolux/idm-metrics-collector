<template>
  <div
    class="bg-white rounded-lg p-4 shadow-sm border border-gray-200 h-full flex flex-col justify-center"
  >
    <div v-if="loading" class="flex items-center justify-center h-full">
      <i class="pi pi-spinner pi-spin text-gray-400"></i>
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-full text-center">
      <i class="pi pi-exclamation-triangle text-red-400 text-2xl mb-2"></i>
      <span class="text-xs text-gray-500">{{ error }}</span>
    </div>
    <div v-else class="flex flex-col items-center justify-center h-full">
      <!-- Label -->
      <div
        class="text-xs text-gray-500 font-medium mb-1 truncate w-full text-center"
        :title="label"
      >
        {{ displayLabel }}
      </div>

      <!-- Main Value -->
      <div class="flex items-baseline gap-1 my-1">
        <span :class="['text-3xl font-bold', trendColor]">
          {{ displayValue }}
        </span>
        <span v-if="unit" class="text-sm text-gray-500 font-medium">{{ unit }}</span>
      </div>

      <!-- Trend Indicator (optional) -->
      <div v-if="showTrend && trend !== null" class="flex items-center gap-1 text-xs mt-1">
        <i
          :class="[
            'pi',
            trend > 0
              ? 'pi-arrow-up text-red-500'
              : trend < 0
                ? 'pi-arrow-down text-blue-500'
                : 'pi-minus text-gray-400'
          ]"
        ></i>
        <span :class="trend > 0 ? 'text-red-500' : trend < 0 ? 'text-blue-500' : 'text-gray-400'">
          {{ Math.abs(trend).toFixed(1) }}%
        </span>
        <span class="text-gray-400">vs. Vorperiode</span>
      </div>

      <!-- Target Comparison (optional) -->
      <div v-if="showTarget && targetValue !== null" class="w-full mt-2">
        <div class="flex justify-between items-center text-[10px] text-gray-500 mb-1">
          <span>Soll: {{ targetValue }}{{ unit }}</span>
          <span :class="diffToTarget > 0 ? 'text-red-500' : 'text-green-500'">
            {{ diffToTarget > 0 ? '+' : '' }}{{ diffToTarget.toFixed(1) }}{{ unit }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-300"
            :class="diffToTarget <= 0 ? 'bg-green-500' : 'bg-red-500'"
            :style="{
              width: Math.min(100, Math.max(0, (currentValue / (targetValue * 1.2)) * 100)) + '%'
            }"
          ></div>
        </div>
      </div>

      <!-- Timestamp -->
      <div v-if="timestamp" class="text-[10px] text-gray-400 mt-2">
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
  showTrend: { type: Boolean, default: false },
  showTarget: { type: Boolean, default: false },
  targetQuery: { type: String, default: null },
  decimals: { type: Number, default: 1 },
  colorThresholds: {
    type: Object,
    default: () => ({
      low: null,
      high: null,
      lowColor: 'text-blue-600',
      highColor: 'text-red-600',
      normalColor: 'text-gray-900'
    })
  }
})

const loading = ref(true)
const error = ref(null)
const currentValue = ref(null)
const targetValue = ref(null)
const previousValue = ref(null)
const trend = ref(null)
const timestamp = ref(null)
let interval = null

const label = computed(() => props.title)
const displayLabel = computed(() => {
  if (label.value.length > 25) {
    return label.value.substring(0, 22) + '...'
  }
  return label.value
})

const displayValue = computed(() => {
  if (currentValue.value === null) return '-'
  return currentValue.value.toFixed(props.decimals)
})

const trendColor = computed(() => {
  if (currentValue.value === null) return 'text-gray-400'

  const { low, high, lowColor, highColor, normalColor } = props.colorThresholds

  if (low !== null && currentValue.value <= low) return lowColor
  if (high !== null && currentValue.value >= high) return highColor
  return normalColor
})

const diffToTarget = computed(() => {
  if (targetValue.value === null || currentValue.value === null) return 0
  return currentValue.value - targetValue.value
})

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
        start: Math.floor((Date.now() - 300000) / 1000), // Last 5 minutes
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

    // Fetch target value if enabled
    if (props.showTarget && props.targetQuery) {
      const targetRes = await api.get('/api/metrics/query', {
        params: { query: props.targetQuery }
      })

      if (targetRes.data?.data?.result?.[0]?.value?.[1]) {
        targetValue.value = parseFloat(targetRes.data.data.result[0].value[1])
      }
    }

    // Fetch previous value for trend if enabled
    if (props.showTrend && currentValue.value !== null) {
      const prevRes = await api.get('/api/metrics/query_range', {
        params: {
          query: props.query,
          start: Math.floor((Date.now() - 3600000) / 1000), // 1 hour ago
          end: Math.floor((Date.now() - 300000) / 1000), // 5 minutes ago
          step: 300
        }
      })

      if (prevRes.data?.data?.result?.[0]?.values) {
        const values = prevRes.data.data.result[0].values
        if (values.length > 0) {
          const avgValue = values.reduce((sum, v) => sum + parseFloat(v[1]), 0) / values.length
          previousValue.value = avgValue
          if (avgValue !== 0) {
            trend.value = ((currentValue.value - avgValue) / avgValue) * 100
          }
        }
      }
    }

    error.value = null
  } catch (e) {
    console.error('StatCard fetch error:', e)
    error.value = 'Ladefehler'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  interval = setInterval(fetchData, 30000) // Update every 30 seconds
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})
</script>

<style scoped>
/* Add any specific styles if needed */
</style>
