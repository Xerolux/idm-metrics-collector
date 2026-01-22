<template>
    <div class="space-y-3 overflow-y-auto">
        <!-- Temperature Sensors -->
        <div v-if="metrics.temperature.length > 0" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                <i class="pi pi-sun text-orange-500"></i>
                Temperaturen
            </h3>
            <div class="space-y-2">
                <div v-for="metric in metrics.temperature" :key="metric.name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">{{ getDisplayName(metric.display) }}</span>
                    <span class="font-mono font-semibold" :class="getValueClass(currentValues[metric.name]?.value)">
                        {{ formatValue(currentValues[metric.name]?.value) }}°C
                    </span>
                </div>
            </div>
        </div>

        <!-- Power Sensors -->
        <div v-if="metrics.power.length > 0" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                <i class="pi pi-bolt text-yellow-500"></i>
                Leistung
            </h3>
            <div class="space-y-2">
                <div v-for="metric in metrics.power" :key="metric.name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">{{ getDisplayName(metric.display) }}</span>
                    <span class="font-mono font-semibold text-blue-600">
                        {{ formatValue(currentValues[metric.name]?.value) }} W
                    </span>
                </div>
            </div>
        </div>

        <!-- Status/State Sensors -->
        <div v-if="metrics.status.length > 0 || metrics.state.length > 0" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                <i class="pi pi-info-circle text-blue-500"></i>
                Status
            </h3>
            <div class="space-y-2">
                <div v-for="metric in [...metrics.status, ...metrics.state]" :key="metric.name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">{{ getDisplayName(metric.display) }}</span>
                    <span class="font-semibold" :class="getStatusClass(currentValues[metric.name]?.value)">
                        {{ formatStatus(currentValues[metric.name]?.value) }}
                    </span>
                </div>
            </div>
        </div>

        <!-- Mode Sensors -->
        <div v-if="metrics.mode.length > 0" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                <i class="pi pi-cog text-gray-500"></i>
 Modi
            </h3>
            <div class="space-y-2">
                <div v-for="metric in metrics.mode" :key="metric.name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">{{ getDisplayName(metric.display) }}</span>
                    <span class="font-semibold text-purple-600">
                        {{ formatMode(currentValues[metric.name]?.value) }}
                    </span>
                </div>
            </div>
        </div>

        <!-- Pressure -->
        <div v-if="metrics.pressure.length > 0" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                <i class="pi pi-bars text-teal-500"></i>
                Druck
            </h3>
            <div class="space-y-2">
                <div v-for="metric in metrics.pressure" :key="metric.name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">{{ getDisplayName(metric.display) }}</span>
                    <span class="font-mono font-semibold text-teal-600">
                        {{ formatValue(currentValues[metric.name]?.value) }} bar
                    </span>
                </div>
            </div>
        </div>

        <!-- Flow -->
        <div v-if="metrics.flow.length > 0" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                <i class="pi pi-arrow-right text-cyan-500"></i>
                Durchfluss
            </h3>
            <div class="space-y-2">
                <div v-for="metric in metrics.flow" :key="metric.name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">{{ getDisplayName(metric.display) }}</span>
                    <span class="font-mono font-semibold text-cyan-600">
                        {{ formatValue(currentValues[metric.name]?.value) }} L/min
                    </span>
                </div>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8 text-gray-500">
            <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <!-- Error State -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {{ error }}
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const metrics = ref({
    temperature: [],
    power: [],
    pressure: [],
    energy: [],
    flow: [],
    status: [],
    mode: [],
    control: [],
    state: [],
    other: []
});

const currentValues = ref({});
const loading = ref(true);
const error = ref(null);
let refreshTimer = null;

const loadMetrics = async () => {
    try {
        const res = await axios.get('/api/metrics/available');
        metrics.value = res.data;
    } catch (e) {
        error.value = 'Fehler beim Laden der Metriken';
        console.error(e);
    }
};

const loadCurrentValues = async () => {
    try {
        const res = await axios.get('/api/metrics/current');
        currentValues.value = res.data;
        loading.value = false;
        error.value = null;
    } catch (e) {
        error.value = 'Fehler beim Laden der Werte';
        console.error(e);
    }
};

const getDisplayName = (name) => {
    // Convert metric names to German display names
    const translations = {
        'temp_outside': 'Außentemperatur',
        'temp_heat_pump_flow': 'Vorlauf WP',
        'temp_heat_pump_return': 'Rücklauf WP',
        'temp_water_heater_top': 'Warmwasser oben',
        'temp_water_heater_bottom': 'Warmwasser unten',
        'temp_water_target': 'WW Sollwert',
        'temp_flow_current_circuit_a': 'Vorlauf Ist HK A',
        'temp_flow_target_circuit_a': 'Vorlauf Soll HK A',
        'temp_room_circuit_a': 'Raumtemperatur HK A',
        'temp_heat_storage': 'Pufferspeicher',
        'temp_cold_storage': 'Kältespeicher',
        'temp_heat_source_input': 'Quelle Eingang',
        'temp_heat_source_output': 'Quelle Ausgang',
        'power_current': 'Wärmeleistung',
        'power_current_draw': 'Leistungsaufnahme',
        'energy_heat_total': 'Energie Gesamt',
        'energy_heat_heating': 'Energie Heizung',
        'energy_heat_total_water': 'Energie Warmwasser',
        'status_heat_pump': 'Status WP',
        'anomaly_score': 'Anomalie Score',
        'anomaly_flag': 'Anomalie Erkannt',
    };
    return translations[name] || name.replace(/_/g, ' ');
};

const formatValue = (value) => {
    if (value === undefined || value === null) return '-';
    return Number(value).toFixed(1);
};

const formatStatus = (value) => {
    if (value === undefined || value === null) return '-';
    const num = Number(value);
    if (num === 0) return 'Aus';
    if (num === 1) return 'An';
    return num;
};

const formatMode = (value) => {
    if (value === undefined || value === null) return '-';
    const num = Number(value);
    const modes = {
        0: 'Standby',
        1: 'Heizen',
        2: 'Kühlen',
        3: 'Abtauen',
        4: 'Legionellenschutz'
    };
    return modes[num] || num;
};

const getValueClass = (value) => {
    if (value === undefined || value === null) return 'text-gray-400';
    const num = Number(value);
    if (num < -5) return 'text-blue-600'; // Kalt
    if (num > 50) return 'text-red-600'; // Heiß
    if (num > 30) return 'text-orange-500'; // Warm
    return 'text-green-600'; // Normal
};

const getStatusClass = (value) => {
    if (value === undefined || value === null) return 'text-gray-400';
    const num = Number(value);
    if (num === 0) return 'text-gray-500';
    if (num === 1) return 'text-green-600';
    return 'text-orange-500';
};

onMounted(() => {
    loadMetrics();
    loadCurrentValues();
    refreshTimer = setInterval(loadCurrentValues, 5000);
});

onUnmounted(() => {
    if (refreshTimer) clearInterval(refreshTimer);
});
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
