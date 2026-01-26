<template>
    <div class="min-h-screen bg-gray-100 p-2 sm:p-4">
        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center h-screen">
            <i class="pi pi-spin pi-spinner text-4xl text-teal-600"></i>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="flex justify-center items-center h-screen">
            <div class="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
                <i class="pi pi-exclamation-circle text-red-500 text-4xl mb-4"></i>
                <h2 class="text-xl font-bold mb-2">Zugriff verweigert</h2>
                <p class="text-gray-600 mb-4">{{ error }}</p>
                <Button label="Zurück zum Login" icon="pi pi-arrow-left" @click="$router.push('/login')" severity="secondary" />
            </div>
        </div>

        <!-- Dashboard Content -->
        <div v-else-if="dashboard" class="h-full flex flex-col gap-4">
            <!-- Custom CSS -->
            <component :is="'style'" v-if="sanitizedCustomCss">{{ sanitizedCustomCss }}</component>

            <!-- Header -->
            <div class="bg-white p-4 rounded-lg shadow-sm flex flex-col sm:flex-row justify-between items-center gap-4">
                <div>
                    <h1 class="text-xl font-bold text-gray-800">{{ dashboard.name }}</h1>
                    <div class="text-xs text-gray-500 flex items-center gap-2">
                        <i class="pi pi-share-alt"></i> Geteilte Ansicht
                        <span v-if="lastUpdate" class="ml-2">Updated: {{ lastUpdate }}</span>
                    </div>
                </div>

                <div class="flex items-center gap-2">
                    <Select
                        v-model="timeRange"
                        :options="timeRangeOptions"
                        optionLabel="label"
                        optionValue="value"
                        class="w-48"
                    />
                    <Button
                        icon="pi pi-refresh"
                        severity="secondary"
                        @click="refreshCharts"
                        title="Aktualisieren"
                    />
                </div>
            </div>

            <!-- Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-for="chart in dashboard.charts" :key="chart.id" class="h-80 relative bg-white rounded-lg shadow-sm border border-gray-200">
                    <ChartCard
                        v-if="!chart.type || chart.type === 'line'"
                        :title="chart.title"
                        :queries="chart.queries"
                        :hours="effectiveHours"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :alert-thresholds="chart.alertThresholds || []"
                        :key="refreshKey"
                    />
                    <BarCard
                        v-else-if="chart.type === 'bar'"
                        :title="chart.title"
                        :queries="chart.queries"
                        :hours="effectiveHours"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :key="refreshKey"
                    />
                    <StatCard
                        v-else-if="chart.type === 'stat'"
                        :title="chart.title"
                        :query="chart.queries[0]?.query || ''"
                        :unit="chart.queries[0]?.unit || ''"
                        :decimals="chart.decimals || 1"
                        :show-trend="chart.showTrend !== false"
                        :show-target="chart.showTarget || false"
                        :target-query="chart.targetQuery"
                        :color-thresholds="chart.colorThresholds"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :key="refreshKey"
                    />
                    <GaugeCard
                        v-else-if="chart.type === 'gauge'"
                        :title="chart.title"
                        :query="chart.queries[0]?.query || ''"
                        :min="chart.min || 0"
                        :max="chart.max || 100"
                        :thresholds="chart.thresholds"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :key="refreshKey"
                    />
                    <HeatmapCard
                        v-else-if="chart.type === 'heatmap'"
                        :title="chart.title"
                        :queries="chart.queries"
                        :hours="effectiveHours"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :key="refreshKey"
                    />
                    <TableCard
                        v-else-if="chart.type === 'table'"
                        :title="chart.title"
                        :queries="chart.queries"
                        :hours="effectiveHours"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :key="refreshKey"
                    />
                    <StateTimelineCard
                        v-else-if="chart.type === 'state_timeline'"
                        :title="chart.title"
                        :query="chart.queries[0]?.query || ''"
                        :hours="effectiveHours"
                        :chart-id="chart.id"
                        :dashboard-id="dashboard.id"
                        :edit-mode="false"
                        :key="refreshKey"
                    />
                </div>
            </div>
        </div>

        <!-- Password Dialog -->
        <Dialog
            v-model:visible="showPasswordDialog"
            modal
            header="Geschützter Bereich"
            :closable="false"
            :style="{ width: '90vw', maxWidth: '400px' }"
        >
            <div class="flex flex-col gap-4 py-4">
                <div class="flex items-center gap-3 text-gray-600 mb-2">
                    <i class="pi pi-lock text-2xl"></i>
                    <p>Dieses Dashboard ist passwortgeschützt. Bitte geben Sie das Passwort ein.</p>
                </div>

                <div class="flex flex-col gap-2">
                    <label for="password" class="text-sm font-medium">Passwort</label>
                    <InputText
                        id="password"
                        v-model="password"
                        type="password"
                        class="w-full"
                        :class="{'p-invalid': passwordError}"
                        @keyup.enter="submitPassword"
                        autofocus
                    />
                    <small v-if="passwordError" class="text-red-500">Falsches Passwort</small>
                </div>
            </div>
            <template #footer>
                <Button label="Zugriff anfordern" icon="pi pi-check" @click="submitPassword" />
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { sanitizeCss } from '@/utils/cssSanitizer';

// Import Components
import ChartCard from '../components/ChartCard.vue';
import BarCard from '../components/BarCard.vue';
import StatCard from '../components/StatCard.vue';
import GaugeCard from '../components/GaugeCard.vue';
import HeatmapCard from '../components/HeatmapCard.vue';
import TableCard from '../components/TableCard.vue';
import StateTimelineCard from '../components/StateTimelineCard.vue';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';

const route = useRoute();
const token = route.params.token;

const loading = ref(true);
const error = ref('');
const dashboard = ref(null);
const showPasswordDialog = ref(false);
const password = ref('');
const passwordError = ref(false);
const refreshKey = ref(0);
const lastUpdate = ref('');

// Time Range
const timeRange = ref('24h');
const timeRangeOptions = [
    { label: '12 Stunden', value: '12h' },
    { label: '24 Stunden', value: '24h' },
    { label: '48 Stunden', value: '48h' },
    { label: '72 Stunden', value: '72h' },
    { label: '1 Woche', value: '168h' }
];

const effectiveHours = computed(() => {
    if (timeRange.value === '0') return 0;
    return parseInt(timeRange.value);
});

const sanitizedCustomCss = computed(() => {
    const css = dashboard.value?.customCss;
    if (!css) return '';
    const { sanitized } = sanitizeCss(css);
    return sanitized;
});

let interceptorId;

const setupAxiosInterceptor = () => {
    interceptorId = axios.interceptors.request.use(config => {
        if (token) {
            config.headers['X-Share-Token'] = token;
        }
        if (password.value) {
            config.headers['X-Share-Password'] = password.value;
        }
        return config;
    });
};

const fetchDashboard = async () => {
    loading.value = true;
    error.value = '';

    try {
        const response = await axios.get(`/api/sharing/dashboard/${token}`);
        dashboard.value = response.data;
        lastUpdate.value = new Date().toLocaleTimeString();
        showPasswordDialog.value = false;
    } catch (err) {
        if (err.response) {
            if (err.response.status === 401 && err.response.data.require_password) {
                showPasswordDialog.value = true;
                loading.value = false;
                return;
            }
            error.value = err.response.data.error || 'Fehler beim Laden des Dashboards';
        } else {
            error.value = 'Netzwerkfehler';
        }
    } finally {
        if (!showPasswordDialog.value) {
            loading.value = false;
        }
    }
};

const submitPassword = async () => {
    if (!password.value) return;

    passwordError.value = false;
    await fetchDashboard();

    if (!dashboard.value) {
        passwordError.value = true;
    }
};

const refreshCharts = () => {
    refreshKey.value++;
    lastUpdate.value = new Date().toLocaleTimeString();
};

onMounted(() => {
    setupAxiosInterceptor();
    fetchDashboard();
});

onUnmounted(() => {
    if (interceptorId !== undefined) {
        axios.interceptors.request.eject(interceptorId);
    }
});
</script>

<style scoped>
/* Scrollbar styling */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
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
