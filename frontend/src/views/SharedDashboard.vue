<template>
  <div class="min-h-screen p-4 md:p-8 bg-slate-100">
    <div class="mx-auto max-w-7xl">
      <div class="glass-panel rounded-2xl p-4 md:p-6">
        <div class="mb-4 border-b border-slate-200 pb-3">
          <h1 class="text-xl md:text-2xl font-bold text-slate-900">
            {{ dashboard?.name || 'Geteiltes Dashboard' }}
          </h1>
          <p class="text-sm text-slate-600">Read-only Ansicht via Share-Link</p>
        </div>

        <div v-if="loading" class="py-12 text-center text-slate-600">Dashboard wird geladen...</div>

        <div
          v-else-if="error"
          class="rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-800"
        >
          {{ error }}
        </div>

        <div
          v-else-if="passwordRequired"
          class="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <h2 class="text-lg font-semibold text-slate-900">Passwort erforderlich</h2>
          <p class="mt-1 text-sm text-slate-600">
            Dieses geteilte Dashboard ist passwortgeschützt.
          </p>
          <InputText
            v-model="password"
            class="mt-4 w-full"
            type="password"
            placeholder="Passwort eingeben"
            @keyup.enter="loadDashboard(true)"
          />
          <Button class="mt-3 w-full" label="Öffnen" @click="loadDashboard(true)" />
        </div>

        <div v-else-if="dashboard" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="chart in charts" :key="chart.id" class="h-80">
            <ChartCard
              v-if="!chart.type || chart.type === 'line'"
              :title="chart.title"
              :queries="chart.queries"
              :hours="chart.hours || 24"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
              :alert-thresholds="chart.alertThresholds || []"
            />
            <BarCard
              v-else-if="chart.type === 'bar'"
              :title="chart.title"
              :queries="chart.queries"
              :hours="chart.hours || 24"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
            />
            <StatCard
              v-else-if="chart.type === 'stat'"
              :title="chart.title"
              :query="chart.queries?.[0]?.query || ''"
              :unit="chart.queries?.[0]?.unit || ''"
              :decimals="chart.decimals || 1"
              :show-trend="chart.showTrend !== false"
              :show-target="chart.showTarget || false"
              :target-query="chart.targetQuery"
              :color-thresholds="chart.colorThresholds"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
            />
            <GaugeCard
              v-else-if="chart.type === 'gauge'"
              :title="chart.title"
              :query="chart.queries?.[0]?.query || ''"
              :min="chart.min || 0"
              :max="chart.max || 100"
              :thresholds="chart.thresholds"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
            />
            <HeatmapCard
              v-else-if="chart.type === 'heatmap'"
              :title="chart.title"
              :queries="chart.queries"
              :hours="chart.hours || 24"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
            />
            <TableCard
              v-else-if="chart.type === 'table'"
              :title="chart.title"
              :queries="chart.queries"
              :hours="chart.hours || 24"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
            />
            <StateTimelineCard
              v-else-if="chart.type === 'state_timeline'"
              :title="chart.title"
              :query="chart.queries?.[0]?.query || ''"
              :hours="chart.hours || 24"
              :chart-id="chart.id"
              :dashboard-id="dashboard.id"
              :edit-mode="false"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

import ChartCard from '../components/ChartCard.vue'
import BarCard from '../components/BarCard.vue'
import StatCard from '../components/StatCard.vue'
import GaugeCard from '../components/GaugeCard.vue'
import HeatmapCard from '../components/HeatmapCard.vue'
import TableCard from '../components/TableCard.vue'
import StateTimelineCard from '../components/StateTimelineCard.vue'

const route = useRoute()
const tokenId = computed(() => route.params.tokenId)

const loading = ref(true)
const error = ref('')
const passwordRequired = ref(false)
const password = ref('')
const dashboard = ref(null)

const charts = computed(() => dashboard.value?.charts || [])

async function loadDashboard(usePassword = false) {
  loading.value = true
  error.value = ''
  try {
    if (!tokenId.value) {
      error.value = 'Ungültiger Share-Link.'
      return
    }

    const url = `/api/sharing/tokens/${tokenId.value}/dashboard`
    const response = usePassword
      ? await axios.post(url, { password: password.value })
      : await axios.get(url)

    dashboard.value = response.data.dashboard
    passwordRequired.value = false
  } catch (e) {
    const status = e?.response?.status
    if (status === 401 && e?.response?.data?.password_required) {
      passwordRequired.value = true
      error.value = ''
    } else if (status === 404) {
      error.value = 'Freigabe-Link nicht gefunden.'
    } else if (status === 410) {
      error.value = 'Freigabe-Link ist abgelaufen.'
    } else if (status === 401) {
      error.value = 'Passwort ungültig.'
    } else {
      error.value = e?.response?.data?.error || 'Dashboard konnte nicht geladen werden.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard(false)
})
</script>
