<template>
    <div class="space-y-3 overflow-y-auto">
        <div v-if="loading" class="text-center py-8 text-gray-500">
            <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {{ error }}
        </div>

        <div v-for="(categoryMetrics, category) in filteredMetrics" :key="category" class="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-2">
                <i :class="getCategoryIcon(category)"></i>
                {{ getCategoryLabel(category) }}
            </h3>
            <div class="space-y-1">
                <div
                    v-for="metric in categoryMetrics"
                    :key="metric.name"
                    class="flex justify-between items-center text-sm p-1.5 rounded hover:bg-gray-50 cursor-grab active:cursor-grabbing group transition-colors"
                    draggable="true"
                    @dragstart="onDragStart($event, metric)"
                >
                    <div class="flex flex-col min-w-0">
                        <span class="text-gray-700 font-medium truncate" :title="metric.display">{{ metric.display }}</span>
                        <span class="text-[10px] text-gray-400 font-mono truncate">{{ metric.name }}</span>
                    </div>
                    <span class="font-mono font-bold whitespace-nowrap ml-2" :class="getValueClass(metric.name, currentValues[metric.name]?.value)">
                         {{ formatValue(metric.name, currentValues[metric.name]?.value) }}
                         <span class="text-[10px] text-gray-400 font-normal">{{ getUnit(metric.name) }}</span>
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import axios from 'axios';

const emit = defineEmits(['sensor-drag-start']);

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

const filteredMetrics = computed(() => {
    const filtered = {};
    for (const [key, val] of Object.entries(metrics.value)) {
        if (val && val.length > 0) {
            filtered[key] = val;
        }
    }
    return filtered;
});

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

const getCategoryLabel = (category) => {
    const labels = {
        temperature: 'Temperaturen',
        power: 'Leistung',
        pressure: 'Druck',
        energy: 'Energie',
        flow: 'Durchfluss',
        status: 'Status',
        mode: 'Modi',
        control: 'Steuerung',
        state: 'Zustand',
        other: 'Sonstige'
    };
    return labels[category] || category;
};

const getCategoryIcon = (category) => {
    const icons = {
        temperature: 'pi pi-sun text-orange-500',
        power: 'pi pi-bolt text-yellow-500',
        pressure: 'pi pi-bars text-teal-500',
        energy: 'pi pi-chart-line text-green-500',
        flow: 'pi pi-arrow-right text-cyan-500',
        status: 'pi pi-info-circle text-blue-500',
        mode: 'pi pi-cog text-gray-500',
        control: 'pi pi-sliders-h text-purple-500',
        state: 'pi pi-check-circle text-emerald-500',
        other: 'pi pi-box text-gray-400'
    };
    return icons[category] || 'pi pi-circle';
};

const formatValue = (name, value) => {
    if (value === undefined || value === null) return '-';

    // Status/Mode mapping
    if (name.includes('status') || name.includes('mode') || name.includes('flag')) {
         const num = Number(value);
         // Simple mapping for common states
         if (name.includes('status_heat_pump')) {
             if (num === 0) return 'Aus';
             if (num === 1) return 'Heizen';
             if (num === 2) return 'Kühlen';
             if (num === 4) return 'WW';
             if (num === 8) return 'Abtauen';
         }
         if (num === 0) return 'Aus';
         if (num === 1) return 'Ein';
         return num;
    }

    return Number(value).toFixed(1);
};

const getUnit = (name) => {
    if (name.includes('temp')) return '°C';
    if (name.includes('power')) return 'W'; // or kW based on scaling
    if (name.includes('pressure')) return 'bar';
    if (name.includes('energy')) return 'kWh';
    if (name.includes('flow')) return 'l/min'; // Assuming
    if (name.includes('score')) return '%';
    return '';
};

const getValueClass = (name, value) => {
    if (value === undefined || value === null) return 'text-gray-400';

    if (name.includes('temp')) {
        const num = Number(value);
        if (num < 0) return 'text-blue-600';
        if (num > 50) return 'text-red-600';
        if (num > 25) return 'text-orange-500';
        return 'text-green-600';
    }

    if (name.includes('status') || name.includes('flag')) {
        return Number(value) > 0 ? 'text-blue-600' : 'text-gray-500';
    }

    return 'text-gray-800';
};

const onDragStart = (event, metric) => {
    event.dataTransfer.setData('application/json', JSON.stringify(metric));
    event.dataTransfer.effectAllowed = 'copy';
    emit('sensor-drag-start', metric);
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
    width: 4px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 2px;
}
::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}
</style>
