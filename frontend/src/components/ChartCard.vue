<template>
    <div class="bg-white rounded-lg p-2 h-full flex flex-col shadow-sm border border-gray-200 relative">
        <div
            v-if="editMode"
            class="absolute top-2 right-2 z-10 flex gap-1"
        >
            <button
                @click="openConfig"
                class="p-1.5 bg-white hover:bg-gray-100 rounded shadow text-gray-600"
                title="Bearbeiten"
            >
                <i class="pi pi-pencil text-xs"></i>
            </button>
            <button
                @click="confirmDelete"
                class="p-1.5 bg-white hover:bg-red-50 rounded shadow text-red-500"
                title="Löschen"
            >
                <i class="pi pi-trash text-xs"></i>
            </button>
        </div>

        <div class="flex justify-between items-start mb-1 px-1">
            <div>
                <h3 class="text-gray-900 font-bold text-sm leading-tight pr-16">{{ title }}</h3>
                <span class="text-xs text-gray-500">Verlauf - letzte {{ displayHours }}</span>
            </div>
            <button
                @click="toggleFullscreen"
                class="text-gray-400 hover:text-gray-600"
            >
                <i :class="isFullscreen ? 'pi pi-window-minimize' : 'pi pi-expand'" class="text-xs"></i>
            </button>
        </div>

        <div
            ref="chartContainer"
            class="flex-grow relative w-full min-h-0"
            :class="{ 'fixed inset-0 z-50 bg-white p-4 h-full w-full': isFullscreen }"
        >
            <div v-if="isFullscreen" class="absolute top-4 right-4 z-50">
                 <button
                    @click="toggleFullscreen"
                    class="p-2 bg-gray-100 hover:bg-gray-200 rounded-full"
                >
                    <i class="pi pi-times text-lg"></i>
                </button>
            </div>
            <Line :data="chartData" :options="chartOptions" />
            <!-- Stats Overlay (Bottom) -->
            <div v-if="hasData" class="absolute bottom-2 left-2 right-2 flex justify-center gap-4 text-[10px] text-gray-500 bg-white/80 p-1 rounded backdrop-blur-sm pointer-events-none">
                 <div v-for="stat in stats" :key="stat.label" class="flex gap-2">
                     <span class="font-bold" :style="{ color: stat.color }">{{ stat.label }}:</span>
                     <span>Min: {{ stat.min.toFixed(1) }}</span>
                     <span>Max: {{ stat.max.toFixed(1) }}</span>
                     <span>Avg: {{ stat.avg.toFixed(1) }}</span>
                 </div>
            </div>
        </div>

        <div v-if="!isFullscreen" class="flex flex-wrap gap-x-3 gap-y-1 justify-center mt-1 px-1">
            <div v-for="(dataset, idx) in chartData.datasets" :key="idx" class="flex items-center gap-1">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: dataset.borderColor }"></span>
                <span class="text-[10px] text-gray-600 leading-none">{{ dataset.label }}</span>
            </div>
        </div>

        <ChartConfigDialog
            ref="configDialog"
            :chart="chartConfig"
            @save="onConfigSave"
        />

        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
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
import 'chartjs-adapter-date-fns';
import zoomPlugin from 'chartjs-plugin-zoom';
import { Line } from 'vue-chartjs';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import ChartConfigDialog from './ChartConfigDialog.vue';
import ConfirmDialog from 'primevue/confirmdialog';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  zoomPlugin
);

const props = defineProps({
    title: { type: String, required: true },
    queries: { type: Array, required: true },
    hours: { type: [Number, String], default: 12 },
    chartId: { type: String, required: true },
    dashboardId: { type: String, required: true },
    editMode: { type: Boolean, default: false }
});

const emit = defineEmits(['deleted']);

const confirm = useConfirm();
const toast = useToast();

const chartData = ref({
    labels: [],
    datasets: []
});

const isFullscreen = ref(false);
const chartContainer = ref(null);
const configDialog = ref(null);
const stats = ref([]);

const chartConfig = computed(() => ({
    title: props.title,
    queries: props.queries,
    hours: props.hours
}));

const displayHours = computed(() => {
    if (props.hours === 0 || props.hours === '0') return 'Start';
    return props.hours + ' Stunden';
});

const hasData = computed(() => chartData.value.datasets.length > 0);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            mode: 'index',
            intersect: false,
        },
        zoom: {
            zoom: {
                wheel: {
                    enabled: true,
                },
                pinch: {
                    enabled: true
                },
                mode: 'x',
            },
            pan: {
                enabled: true,
                mode: 'x',
            }
        }
    },
    scales: {
        x: {
            display: true,
            type: 'time',
             time: {
                tooltipFormat: 'dd.MM.yyyy HH:mm',
                displayFormats: {
                    hour: 'HH:mm',
                    day: 'dd.MM'
                }
            },
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
            tension: 0.4,
            borderWidth: 2
        }
    }
};

const calculateStats = (datasets) => {
    const calculatedStats = [];
    datasets.forEach(ds => {
        const values = ds.data.filter(v => v !== null && !isNaN(v));
        if (values.length > 0) {
            const min = Math.min(...values);
            const max = Math.max(...values);
            const sum = values.reduce((a, b) => a + b, 0);
            const avg = sum / values.length;
            calculatedStats.push({
                label: ds.label,
                color: ds.borderColor,
                min,
                max,
                avg
            });
        }
    });
    stats.value = calculatedStats;
};

const fetchData = async () => {
    const end = Math.floor(Date.now() / 1000);
    let start;

    // Check for "All" (0)
    if (props.hours === 0 || props.hours === '0') {
         start = end - (365 * 24 * 3600); // Default to 1 year if "All" is selected to avoid too much data, or maybe 5 years
    } else {
         start = end - (parseInt(props.hours) * 3600);
    }

    const duration = end - start;
    // Dynamic step calculation to avoid fetching too many points
    // Aim for around 500-1000 points
    const step = Math.max(60, Math.floor(duration / 500));

    const datasets = [];

    const promises = props.queries.map(async (q) => {
        try {
            const res = await axios.get('/api/metrics/query_range', {
                params: {
                    query: q.query,
                    start,
                    end,
                    step
                }
            });
            return { q, res };
        } catch (e) {
            console.error(`Chart data fetch error for ${q.label}:`, e);
            return { q, res: null };
        }
    });

    const results = await Promise.all(promises);

    for (const { q, res } of results) {
        if (res && res.data && res.data.status === 'success') {
            const result = res.data.data.result;
            if (result.length > 0) {
                const values = result[0].values; // [[timestamp, "value"], ...]
                const dataPoints = values.map(v => ({
                    x: v[0] * 1000,
                    y: parseFloat(v[1])
                }));

                datasets.push({
                    label: q.label,
                    data: dataPoints,
                    borderColor: q.color,
                    backgroundColor: q.color,
                    fill: false
                });
            }
        }
    }

    chartData.value = {
        datasets
    };
    calculateStats(datasets);
};

const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value;
};

const openConfig = () => {
    configDialog.value?.open();
};

const onConfigSave = async (config) => {
    try {
        await axios.put(`/api/dashboards/${props.dashboardId}/charts/${props.chartId}`, config);
        toast.add({
            severity: 'success',
            summary: 'Erfolg',
            detail: 'Chart gespeichert',
            life: 3000
        });
    } catch (e) {
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Chart konnte nicht gespeichert werden',
            life: 5000
        });
    }
};

const confirmDelete = () => {
    confirm.require({
        message: 'Chart wirklich löschen?',
        header: 'Bestätigung',
        icon: 'pi pi-exclamation-triangle',
        accept: () => deleteChart()
    });
};

const deleteChart = async () => {
    try {
        await axios.delete(`/api/dashboards/${props.dashboardId}/charts/${props.chartId}`);
        toast.add({
            severity: 'success',
            summary: 'Gelöscht',
            detail: 'Chart wurde gelöscht',
            life: 3000
        });
        emit('deleted');
    } catch (e) {
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Chart konnte nicht gelöscht werden',
            life: 5000
        });
    }
};

onMounted(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);

    // Cleanup on fullscreen change
    watch(isFullscreen, () => {
        // Force chart resize
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });

    return () => clearInterval(interval);
});

watch(() => props.queries, fetchData);
watch(() => props.hours, fetchData);
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
