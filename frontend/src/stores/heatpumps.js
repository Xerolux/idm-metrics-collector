import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useHeatpumpsStore = defineStore('heatpumps', () => {
  const heatpumps = ref([])
  const manufacturers = ref([])
  const activeHeatpumpId = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const activeHeatpump = computed(() =>
    heatpumps.value.find(hp => hp.id === activeHeatpumpId.value)
  )

  const connectedHeatpumps = computed(() =>
    heatpumps.value.filter(hp => hp.connected && hp.enabled)
  )

  // Actions
  async function fetchHeatpumps() {
    loading.value = true
    try {
      const response = await axios.get('/api/heatpumps')
      heatpumps.value = response.data

      // Set first heatpump as active if none selected
      if (!activeHeatpumpId.value && heatpumps.value.length > 0) {
        activeHeatpumpId.value = heatpumps.value[0].id
      } else if (activeHeatpumpId.value && !heatpumps.value.find(hp => hp.id === activeHeatpumpId.value)) {
        // If active HP no longer exists, select first
        activeHeatpumpId.value = heatpumps.value[0]?.id || null
      }
    } catch (e) {
      error.value = 'Fehler beim Laden der Wärmepumpen'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchManufacturers() {
    try {
        const response = await axios.get('/api/manufacturers')
        manufacturers.value = response.data
    } catch (e) {
        console.error(e)
    }
  }

  async function addHeatpump(config) {
    const response = await axios.post('/api/heatpumps', config)
    await fetchHeatpumps()
    return response.data.id
  }

  async function removeHeatpump(id) {
    await axios.delete(`/api/heatpumps/${id}`)
    await fetchHeatpumps()

    if (activeHeatpumpId.value === id) {
      activeHeatpumpId.value = heatpumps.value[0]?.id || null
    }
  }

  async function updateHeatpump(id, data) {
    await axios.put(`/api/heatpumps/${id}`, data)
    await fetchHeatpumps()
  }

  async function testConnection(id) {
    const response = await axios.post(`/api/heatpumps/${id}/test`)
    return response.data
  }

  async function enableHeatpump(id, enabled) {
      await axios.post(`/api/heatpumps/${id}/enable`, { enabled })
      await fetchHeatpumps()
  }

  function setActiveHeatpump(id) {
    activeHeatpumpId.value = id
  }

  return {
    heatpumps,
    manufacturers,
    activeHeatpumpId,
    activeHeatpump,
    connectedHeatpumps,
    loading,
    error,
    fetchHeatpumps,
    fetchManufacturers,
    addHeatpump,
    removeHeatpump,
    updateHeatpump,
    testConnection,
    enableHeatpump,
    setActiveHeatpump
  }
})
