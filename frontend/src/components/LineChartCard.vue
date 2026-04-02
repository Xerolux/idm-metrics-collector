<template>
  <div
    class="bg-white dark:bg-gray-800 rounded-lg p-2 h-full flex flex-col shadow-sm border border-gray-200 dark:border-gray-700"
  >
    <div class="flex justify-between items-start mb-1 px-1">
      <div>
        <h3 class="text-gray-900 dark:text-gray-100 font-bold text-sm leading-tight">
          {{ title }}
        </h3>
        <span class="text-xs text-gray-500 dark:text-gray-400"
          >Verlauf - letzte {{ hours }} Stunden</span
        >
      </div>
      <button
        type="button"
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-gray-500 rounded"
        title="Vollbild umschalten"
        aria-label="Vollbild umschalten"
      >
        <i class="pi pi-expand text-xs"></i>
      </button>
    </div>
    <div v-if="loading" class="flex-grow flex items-center justify-center">
      <i class="pi pi-spin pi-spinner text-gray-400 text-xl"></i>
    </div>
    <div v-else-if="error" class="flex-grow flex items-center justify-center">
      <span class="text-xs text-red-500">{{ error }}</span>
    </div>
    <div v-else class="flex-grow relative w-full min-h-0">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div class="flex flex-wrap gap-x-3 gap-y-1 justify-center mt-1 px-1">
      <div v-for="(dataset, idx) in chartData.datasets" :key="idx" class="flex items-center gap-1">
        <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: dataset.borderColor }"></span>
        <span class="text-[10px] text-gray-600 dark:text-gray-400 leading-none">{{
          dataset.label
        }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
// Xerolux 2026
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Line } from 'vue-chartjs'
import api from '@/utils/api.js'
import { createBaseOptions, isDarkMode } from '@/utils/chartConfig.js'

const props = defineProps({
  title: { type: String, required: true },
  queries: { type: Array, required: true }, // Array of { label: 'Name', query: 'metric_name', color: '#hex' }
  hours: { type: Number, default: 12 }
})

const chartData = ref({ labels: [], datasets: [] })
const loading = ref(true)
const error = ref(null)
let refreshInterval = null

const chartOptions = computed(() => {
  const base = createBaseOptions(false, isDarkMode())
  return {
    ...base,
    plugins: {
      ...base.plugins,
      tooltip: {
        ...base.plugins.tooltip,
        callbacks: {
          label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(2) ?? '-'}`
        }
      }
    }
  }
})

const fetchData = async () => {
  const end = Math.floor(Date.now() / 1000)
  const start = end - props.hours * 3600
  const step = Math.max(60, Math.floor((end - start) / 200)) // ~200 points max

  error.value = null

  try {
    const promises = props.queries.map((q) =>
      api
        .get('/api/metrics/query_range', {
          params: { query: q.query, start, end, step }
        })
        .then((res) => ({ q, res }))
        .catch((e) => {
          console.error(`Chart data fetch error for ${q.label}:`, e)
          return { q, res: null }
        })
    )

    const results = await Promise.all(promises)
    const datasets = []

    for (const { q, res } of results) {
      if (res?.data?.status === 'success') {
        const result = res.data.data.result
        if (result.length > 0) {
          const values = result[0].values // [[timestamp, "value"], ...]
          datasets.push({
            label: q.label,
            data: values.map((v) => ({ x: v[0] * 1000, y: parseFloat(v[1]) })),
            borderColor: q.color,
            backgroundColor: q.color + '20',
            fill: false,
            pointRadius: 0,
            pointHitRadius: 10,
            pointHoverRadius: 4
          })
        }
      }
    }

    chartData.value = { datasets }
  } catch (e) {
    error.value = 'Fehler beim Laden der Daten'
    console.error('LineChartCard fetch error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  refreshInterval = setInterval(fetchData, 60000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})

watch(
  () => props.hours,
  () => {
    loading.value = true
    fetchData()
  }
)
</script>
