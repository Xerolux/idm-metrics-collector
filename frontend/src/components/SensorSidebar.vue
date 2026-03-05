<template>
  <div class="bg-white rounded-lg p-3 shadow-sm border border-gray-200 overflow-y-auto">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-gray-900 font-bold text-sm">Verfügbare Sensoren</h3>
      <button
        @click="refreshMetrics"
        class="p-1 hover:bg-gray-100 rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-teal-500"
        :disabled="loading"
        title="Sensoren aktualisieren"
        aria-label="Sensoren aktualisieren"
      >
        <i :class="loading ? 'pi pi-spin pi-spinner' : 'pi pi-refresh'" class="text-gray-500"></i>
      </button>
    </div>

    <input
      v-model="searchQuery"
      type="text"
      placeholder="Suchen..."
      class="w-full px-3 py-2 text-sm border border-gray-300 rounded mb-3 focus:outline-none focus:ring-2 focus:ring-teal-500"
    />

    <div v-if="loading" class="text-center py-8 text-gray-500 text-sm">
      <i class="pi pi-spin pi-spinner text-2xl mb-2"></i>
      <p>Lade Sensoren...</p>
    </div>

    <div v-else-if="error" class="text-center py-8 text-red-500 text-sm">
      <i class="pi pi-exclamation-triangle text-2xl mb-2"></i>
      <p>{{ error }}</p>
    </div>

    <div v-else class="space-y-3">
      <div v-for="(metrics, category) in filteredMetrics" :key="category">
        <div v-if="metrics.length > 0" class="border-b border-gray-200 pb-2 last:border-b-0">
          <h4 class="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">
            {{ getCategoryLabel(category) }}
          </h4>
          <div class="space-y-1">
            <button
              v-for="metric in metrics"
              :key="metric.name"
              @click="selectSensor(metric)"
              class="w-full text-left px-2 py-1.5 text-xs rounded hover:bg-teal-50 hover:text-teal-700 transition-colors flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-teal-500"
            >
              <i class="pi pi-chart-line text-teal-600"></i>
              <span>{{ metric.display }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedSensors.length > 0" class="mt-4 pt-3 border-t border-gray-200">
      <h4 class="text-xs font-semibold text-gray-600 mb-2">Ausgewählt:</h4>
      <div class="flex flex-wrap gap-1">
        <span
          v-for="sensor in selectedSensors"
          :key="sensor.name"
          class="inline-flex items-center gap-1 px-2 py-1 bg-teal-100 text-teal-800 rounded text-xs"
        >
          {{ sensor.display }}
          <button
            @click="removeSensor(sensor)"
            class="hover:text-teal-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-teal-500 rounded-sm"
            title="Sensor entfernen"
            aria-label="Sensor entfernen"
          >
            <i class="pi pi-times text-xs"></i>
          </button>
        </span>
      </div>
      <button
        @click="addToChart"
        class="w-full mt-3 bg-teal-600 hover:bg-teal-700 text-white py-2 px-3 rounded text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-teal-500 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="!canAddToChart"
      >
        <i class="pi pi-plus mr-1"></i>
        Zu Chart hinzufügen
      </button>
    </div>
  </div>
</template>

<script setup>
// Xerolux 2026
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['add-to-chart'])

const metrics = ref({})
const searchQuery = ref('')
const selectedSensors = ref([])
const loading = ref(false)
const error = ref(null)

const filteredMetrics = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const filtered = {}
  for (const [category, metricsList] of Object.entries(metrics.value)) {
    const filteredList = metricsList.filter((m) => m.display.toLowerCase().includes(query))
    if (filteredList.length > 0) {
      filtered[category] = filteredList
    }
  }
  return filtered
})

const canAddToChart = computed(() => selectedSensors.value.length > 0)

const getCategoryLabel = (category) => {
  const labels = {
    temperature: 'Temperatur',
    power: 'Leistung',
    pressure: 'Druck',
    energy: 'Energie',
    flow: 'Durchfluss',
    status: 'Status',
    mode: 'Modus',
    other: 'Andere'
  }
  return labels[category] || category
}

const refreshMetrics = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await axios.get('/api/metrics/available')
    metrics.value = res.data
  } catch (e) {
    error.value = 'Fehler beim Laden der Sensoren'
    console.error(e)
  } finally {
    loading.value = false
  }
}

const selectSensor = (sensor) => {
  if (!selectedSensors.value.find((s) => s.name === sensor.name)) {
    selectedSensors.value.push(sensor)
  }
}

const removeSensor = (sensor) => {
  selectedSensors.value = selectedSensors.value.filter((s) => s.name !== sensor.name)
}

const addToChart = () => {
  if (selectedSensors.value.length > 0) {
    emit('add-to-chart', [...selectedSensors.value])
    selectedSensors.value = []
  }
}

onMounted(() => {
  refreshMetrics()
})
</script>

<style scoped>
/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
