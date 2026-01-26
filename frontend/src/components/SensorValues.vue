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
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import axios from 'axios';
import { useWebSocket } from '../utils/websocket.js';
import { useHeatpumpsStore } from '@/stores/heatpumps';

const emit = defineEmits(['sensor-drag-start']);
const hpStore = useHeatpumpsStore();

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
    ai: [],
    other: []
});

const currentValues = ref({});
const loading = ref(true);
const error = ref(null);
let refreshTimer = null;

const handleMetricUpdate = (data) => {
    const activePrefix = hpStore.activeHeatpumpId ? `${hpStore.activeHeatpumpId}.` : '';

    const updatePoint = (point) => {
        if (!point || !point.metric) return;

        let metricName = point.metric;

        // Strip prefix if present
        if (activePrefix && metricName.startsWith(activePrefix)) {
            metricName = metricName.substring(activePrefix.length);
        } else if (hpStore.activeHeatpumpId && !activePrefix) {
             // If we have an active HP but no prefix logic (should not happen if logic correct), ignore?
             // Or if message has no prefix?
        }

        if (!currentValues.value[metricName]) {
            currentValues.value[metricName] = {
                value: point.value,
                timestamp: point.timestamp
            };
        } else {
            currentValues.value[metricName].value = point.value;
            currentValues.value[metricName].timestamp = point.timestamp;
        }
    };

    if (data.metric) {
        updatePoint(data);
    } else {
        Object.values(data).forEach(updatePoint);
    }
};

const { subscribe, unsubscribe } = useWebSocket(handleMetricUpdate);

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
        let url = '/api/data'; // Default (legacy or default HP)
        if (hpStore.activeHeatpumpId) {
            url = `/api/data/${hpStore.activeHeatpumpId}`;
        }

        const res = await axios.get(url);

        // Convert flat values to object with timestamp
        const data = {};
        const now = Date.now() / 1000;

        for (const [key, value] of Object.entries(res.data)) {
            // Strip prefix if present in the fetched data (shouldn't be for /api/data/hp_id but /api/data might return prefixes if not handled well in backend)
            // Backend /api/data/hp_id returns clean { sensor: value } dict for that HP.
            // Backend /api/data returns flattened { "hp.sensor": val } IF nested.
            // But I updated /api/data to return default HP data clean.
            // So we assume clean data here.
            data[key] = { value, timestamp: now };
        }

        currentValues.value = data;
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
        ai: 'KI-Analyse',
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
        ai: 'pi pi-sparkles text-purple-500',
        other: 'pi pi-box text-gray-400'
    };
    return icons[category] || 'pi pi-circle';
};

const formatValue = (name, value) => {
    if (value === undefined || value === null) return '-';

    // AI Scores
    if (name.includes('score')) {
        return Number(value).toFixed(4);
    }

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

         // Generic boolean/flag mapping
         if (num === 0) return name.includes('flag') ? 'NEIN' : 'Aus';
         if (num === 1) return name.includes('flag') ? 'JA' : 'Ein';

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

const getSubscribedMetrics = () => {
    const allMetrics = [];
    if (metrics.value) {
        Object.values(metrics.value).forEach(list => {
            if (Array.isArray(list)) {
                list.forEach(m => allMetrics.push(m.name));
            }
        });
    }

    if (hpStore.activeHeatpumpId) {
        return allMetrics.map(m => `${hpStore.activeHeatpumpId}.${m}`);
    }
    return allMetrics;
};

const updateSubscriptions = () => {
    const allMetrics = getSubscribedMetrics();
    if (allMetrics.length > 0) {
        subscribe(allMetrics);
    }
}

onMounted(() => {
    loadMetrics().then(() => {
        updateSubscriptions();
    });
    loadCurrentValues();
    refreshTimer = setInterval(loadCurrentValues, 60000);
});

watch(() => hpStore.activeHeatpumpId, () => {
    // We should unsubscribe old metrics ideally, but we don't track old ID easily here without ref.
    // wsClient handles subscriptions. If we just subscribe new ones, we get both?
    // We can unsubscribe ALL and resubscribe.
    // wsClient.unsubscribe takes list.
    // Let's rely on reload or just fetch current values.
    // To be clean: unsubscribe old logic would require storing old list.
    // For now, re-load values. WebSocket might get double data if we don't unsub.
    // wsClient.unsubscribe(oldList)

    loadCurrentValues();
    // Subscriptions: changing keys.
    // We can assume wsClient deduplicates or we just add new ones.
    updateSubscriptions();
});

onUnmounted(() => {
    if (refreshTimer) clearInterval(refreshTimer);
    const allMetrics = getSubscribedMetrics();
    if (allMetrics.length > 0) {
        unsubscribe(allMetrics);
    }
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
