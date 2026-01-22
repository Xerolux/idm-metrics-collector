<template>
    <div class="rounded-lg h-full flex flex-col relative overflow-hidden" :class="cardClass">
        <!-- Title -->
        <div class="px-3 pt-2 text-[11px] font-medium opacity-80 truncate" :title="title">
            {{ title }}
        </div>

        <!-- Main Value -->
        <div class="px-3 py-1 flex items-baseline gap-1" v-if="!isStatus">
            <span class="text-2xl font-bold tracking-tight">{{ formattedValue }}</span>
            <span class="text-xs opacity-70 font-medium">{{ unit }}</span>
        </div>

        <!-- Status Value -->
        <div v-else class="flex-grow flex items-center justify-center p-2">
             <span class="text-2xl font-bold tracking-tight">{{ statusText }}</span>
        </div>

        <!-- Sparkline Chart -->
        <div v-if="!isStatus" class="absolute bottom-0 left-0 right-0 h-12 w-full opacity-50">
            <Line v-if="chartData.datasets.length > 0" :data="chartData" :options="chartOptions" />
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Line } from 'vue-chartjs';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler
);

const props = defineProps({
    title: { type: String, required: true },
    metric: { type: String, required: true },
    unit: { type: String, default: '' },
    color: { type: String, default: '#3b82f6' },
    isStatus: { type: Boolean, default: false },
    currentValue: { type: [Number, String, null], default: null }
});

const chartData = ref({
    labels: [],
    datasets: []
});

const formattedValue = computed(() => {
    if (props.currentValue === null || props.currentValue === undefined) return '--';
    const num = Number(props.currentValue);
    if (isNaN(num)) return props.currentValue;
    return num.toFixed(1); // Standard format
    // Use decimal digits from parent if needed, but 1 is usually fine for overview
});

const statusText = computed(() => {
    if (props.currentValue === null || props.currentValue === undefined) return '--';
    const num = Number(props.currentValue);
    if (props.metric.includes('status_heat_pump')) {
         if (num === 0) return 'Aus';
         if (num === 1) return 'Heizen';
         if (num === 2) return 'Kühlen';
         if (num === 4) return 'WW';
         if (num === 8) return 'Abtauen';
    }
    return String(props.currentValue);
});

const cardClass = computed(() => {
    if (props.isStatus) {
        // Status Colors based on value
        const num = Number(props.currentValue);
        // Default green for running
        if (num > 0) return 'bg-[#4ade80] text-white'; // Green like image
        return 'bg-gray-100 text-gray-500'; // Off
    }
    // Dark card background
    return 'bg-[#1e293b] text-white border border-gray-700 shadow-md';
});

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
        annotation: false,
        zoom: false
    },
    scales: {
        x: { display: false },
        y: { display: false }
    },
    elements: {
        point: { radius: 0 },
        line: { borderWidth: 1.5, tension: 0.4 }
    },
    layout: { padding: 0 }
};

const fetchHistory = async () => {
    if (props.isStatus) return; // No chart for status

    const end = Math.floor(Date.now() / 1000);
    const start = end - (24 * 3600); // 24h
    const step = 300; // 5 min resolution

    try {
        const res = await axios.get('/api/metrics/query_range', {
            params: {
                query: props.metric,
                start,
                end,
                step
            }
        });

        if (res.data && res.data.status === 'success') {
            const result = res.data.data.result;
            if (result.length > 0) {
                const values = result[0].values;
                const labels = values.map(v => v[0]);
                const data = values.map(v => parseFloat(v[1]));

                chartData.value = {
                    labels,
                    datasets: [{
                        data,
                        borderColor: props.color,
                        backgroundColor: props.color + '20', // transparent fill
                        fill: true,
                    }]
                };
            }
        }
    } catch (e) {
        console.error("Overview chart fetch failed", e);
    }
};

let refreshTimer = null;

onMounted(() => {
    fetchHistory();
    // Refresh history every 5 mins
    refreshTimer = setInterval(fetchHistory, 300000);
});

onUnmounted(() => {
    if (refreshTimer) clearInterval(refreshTimer);
});

watch(() => props.metric, fetchHistory);

</script>
