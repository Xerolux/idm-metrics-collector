<template>
    <div class="bg-white rounded-lg p-2 h-full flex flex-col shadow-sm border border-gray-200">
        <div class="flex justify-between items-start mb-1 px-1">
            <div>
                <h3 class="text-gray-900 font-bold text-sm leading-tight">{{ title }}</h3>
                <span class="text-xs text-gray-500">Verlauf - letzte {{ hours }} Stunden</span>
            </div>
            <button class="text-gray-400 hover:text-gray-600">
                <i class="pi pi-expand text-xs"></i>
            </button>
        </div>
        <div class="flex-grow relative w-full min-h-0">
            <Line :data="chartData" :options="chartOptions" />
        </div>
        <div class="flex flex-wrap gap-x-3 gap-y-1 justify-center mt-1 px-1">
            <div v-for="(dataset, idx) in chartData.datasets" :key="idx" class="flex items-center gap-1">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: dataset.borderColor }"></span>
                <span class="text-[10px] text-gray-600 leading-none">{{ dataset.label }}</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import { Line } from 'vue-chartjs';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const props = defineProps({
    title: { type: String, required: true },
    queries: { type: Array, required: true }, // Array of { label: 'Name', query: 'metric_name', color: '#hex' }
    hours: { type: Number, default: 12 }
});

const chartData = ref({
    labels: [],
    datasets: []
});

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false // Custom legend outside
        },
        tooltip: {
            mode: 'index',
            intersect: false,
        }
    },
    scales: {
        x: {
            display: true,
            grid: {
                display: true,
                color: '#f0f0f0'
            },
            ticks: {
                maxTicksLimit: 8,
                maxRotation: 0,
                color: '#666',
                font: { size: 10 }
            }
        },
        y: {
            display: true,
            grid: {
                color: '#f0f0f0'
            },
            ticks: {
                color: '#666',
                font: { size: 10 }
            }
        }
    },
    elements: {
        point: {
            radius: 0,
            hitRadius: 10,
            hoverRadius: 4
        },
        line: {
            tension: 0.4, // Smooth curves
            borderWidth: 2
        }
    }
};

const fetchData = async () => {
    const end = Math.floor(Date.now() / 1000);
    const start = end - (props.hours * 3600);
    const step = Math.max(60, Math.floor((end - start) / 100)); // ~100 points

    const datasets = [];
    let labels = [];

    for (const q of props.queries) {
        try {
            const res = await axios.get('/api/metrics/query_range', {
                params: {
                    query: q.query,
                    start,
                    end,
                    step
                }
            });

            if (res.data && res.data.status === 'success') {
                const result = res.data.data.result;
                if (result.length > 0) {
                    const values = result[0].values; // [[timestamp, "value"], ...]
                    const dataPoints = values.map(v => parseFloat(v[1]));

                    if (labels.length === 0) {
                        labels = values.map(v => {
                            const date = new Date(v[0] * 1000);
                            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        });
                    }

                    datasets.push({
                        label: q.label,
                        data: dataPoints,
                        borderColor: q.color,
                        backgroundColor: q.color,
                        fill: false
                    });
                }
            }
        } catch (e) {
            console.error("Chart data fetch error:", e);
        }
    }

    chartData.value = {
        labels,
        datasets
    };
};

onMounted(() => {
    fetchData();
    setInterval(fetchData, 60000); // Refresh every minute
});

watch(() => props.hours, fetchData);
</script>
