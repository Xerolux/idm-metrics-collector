<template>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
    <OverviewCard
      title="Aussentemperatur"
      metric="idm_heatpump_temp_outside"
      unit="°C"
      color="#3b82f6"
      :current-value="getValue('idm_heatpump_temp_outside')"
    />
    <OverviewCard
      title="Vorlauf WP"
      metric="idm_heatpump_temp_heat_pump_flow"
      unit="°C"
      color="#eab308"
      :current-value="getValue('idm_heatpump_temp_heat_pump_flow')"
    />
    <OverviewCard
      title="Rücklauf WP"
      metric="idm_heatpump_temp_heat_pump_return"
      unit="°C"
      color="#eab308"
      :current-value="getValue('idm_heatpump_temp_heat_pump_return')"
    />
    <OverviewCard
      title="Warmwasser oben"
      metric="idm_heatpump_temp_water_heater_top"
      unit="°C"
      color="#22c55e"
      :current-value="getValue('idm_heatpump_temp_water_heater_top')"
    />
    <OverviewCard
      title="Leistungsaufnahme"
      metric="idm_heatpump_power_current_draw"
      unit="kW"
      color="#22c55e"
      :current-value="getValue('idm_heatpump_power_current_draw')"
    />
    <OverviewCard
      title="Status WP"
      metric="idm_heatpump_status_heat_pump"
      :is-status="true"
      :current-value="getValue('idm_heatpump_status_heat_pump')"
    />
  </div>
</template>

<script setup>
// Xerolux 2026
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api.js'
import OverviewCard from './OverviewCard.vue'

const currentValues = ref({})
let refreshTimer = null

const loadCurrentValues = async () => {
  try {
    const res = await api.get('/api/metrics/current')
    currentValues.value = res.data
  } catch (e) {
    console.error('Failed to load overview values', e)
  }
}

const getValue = (name) => {
  const item = currentValues.value[name]
  // metrics/current returns object where key is metric name
  // and value is { value: X, timestamp: Y } or just X depending on implementation
  // Looking at SensorValues.vue, it accesses `currentValues[metric.name]?.value`
  // Wait, check SensorValues.vue implementation again.

  // In SensorValues:
  // currentValues.value = res.data;
  // {{ formatValue(metric.name, currentValues[metric.name]?.value) }}

  // The idm_logger/web.py endpoint /api/metrics/current likely returns dict { name: { value: val, ... } }
  // But wait, the standard Prometheus export format is usually just values?
  // Let's assume the structure used in SensorValues is correct.

  if (item && typeof item === 'object' && 'value' in item) {
    return item.value
  }
  return item
}

onMounted(() => {
  loadCurrentValues()
  refreshTimer = setInterval(loadCurrentValues, 5000) // 5s refresh
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>
