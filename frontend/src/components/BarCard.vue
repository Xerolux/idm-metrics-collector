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

        <div class="flex justify-between items-start mb-1 px-1 flex-shrink-0">
            <div>
                <h3 class="text-gray-900 font-bold text-sm leading-tight pr-16">{{ title }}</h3>
                <span class="text-xs text-gray-500">Balkendiagramm - letzte {{ displayHours }}</span>
            </div>
            <div class="flex items-center gap-1">
                <button
                    @click="toggleFullscreen"
                    class="text-gray-400 hover:text-gray-600"
                >
                    <i :class="isFullscreen ? 'pi pi-window-minimize' : 'pi pi-expand'" class="text-xs"></i>
                </button>
            </div>
        </div>

        <div
            ref="chartContainer"
            class="flex-grow flex flex-col w-full min-h-0"
            :class="{ 'fixed inset-0 z-50 bg-white p-4 h-full w-full': isFullscreen, 'relative': !isFullscreen }"
        >
            <div v-if="isFullscreen" class="absolute top-4 right-4 z-50">
                 <button
                    @click="toggleFullscreen"
                    class="p-2 bg-gray-100 hover:bg-gray-200 rounded-full"
                >
                    <i class="pi pi-times text-lg"></i>
                </button>
            </div>

            <!-- Chart Wrapper -->
            <div class="flex-grow relative min-h-0 w-full">
                <Bar ref="chartRef" :data="chartData" :options="chartOptions" />
            </div>
        </div>

        <BarConfigDialog
            ref="configDialog"
            :bar="barConfig"
            @save="(config) => emit('save', { ...config, id: props.chartId })"
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
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Bar } from 'vue-chartjs';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import BarConfigDialog from './BarConfigDialog.vue';
import ConfirmDialog from 'primevue/confirmdialog';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const props = defineProps({
    title: { type: String, required: true },
    queries: { type: Array, required: true },
    hours: { type: [Number, String], default: 12 },
    chartId: { type: String, required: true },
    dashboardId: { type: String, required: true },
    editMode: { type: Boolean, default: false },
    barMode: { type: String, default: 'grouped' }, // 'grouped', 'stacked', 'horizontal'
    aggregation: { type: String, default: 'avg' } // 'avg', 'sum', 'min', 'max'
});

const emit = defineEmits(['deleted', 'save']);

const confirm = useConfirm();
const toast = useToast();

const chartData = ref({
    labels: [],
    datasets: []
});

const isFullscreen = ref(false);
const chartContainer = ref(null);
const chartRef = ref(null);
const configDialog = ref(null);
// const stats = ref([]);

const barConfig = computed(() => ({
    title: props.title,
    queries: props.queries,
    hours: props.hours,
    barMode: props.barMode,
    aggregation: props.aggregation
}));

const displayHours = computed(() => {
    if (props.hours === 0 || props.hours === '0') return 'Start';
    return props.hours + ' Stunden';
});

// const hasData = computed(() => chartData.value.datasets.length > 0);

const chartOptions = computed(() => {
    const isHorizontal = props.barMode === 'horizontal';
    const isDark = document.documentElement.classList.contains('my-app-dark');

    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    color: isDark ? '#f3f4f6' : '#1f2937',
                    font: { size: 10 },
                    boxWidth: 12
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                titleColor: isDark ? '#f3f4f6' : '#1f2937',
                bodyColor: isDark ? '#d1d5db' : '#4b5563',
                borderColor: isDark ? '#374151' : '#e5e7eb',
                borderWidth: 1,
                padding: 12,
                displayColors: true,
                boxPadding: 4
            }
        },
        scales: isHorizontal ? {
            x: {
                display: true,
                stacked: props.barMode === 'stacked',
                grid: {
                    color: isDark ? '#374151' : '#f0f0f0'
                },
                ticks: {
                    color: isDark ? '#9ca3af' : '#666',
                    font: { size: 10 }
                }
            },
            y: {
                display: true,
                stacked: props.barMode === 'stacked',
                grid: {
                    color: isDark ? '#374151' : '#f0f0f0'
                },
                ticks: {
                    color: isDark ? '#9ca3af' : '#666',
                    font: { size: 10 }
                }
            }
        } : {
            x: {
                display: true,
                type: 'category',
                stacked: props.barMode === 'stacked',
                grid: {
                    display: true,
                    color: isDark ? '#374151' : '#f0f0f0'
                },
                ticks: {
                    maxRotation: 45,
                    minRotation: 0,
                    color: isDark ? '#9ca3af' : '#666',
                    font: { size: 10 }
                }
            },
            y: {
                display: true,
                stacked: props.barMode === 'stacked',
                grid: {
                    color: isDark ? '#374151' : '#f0f0f0'
                },
                ticks: {
                    color: isDark ? '#9ca3af' : '#666',
                    font: { size: 10 }
                },
                beginAtZero: true
            }
        },
        elements: {
            bar: {
                borderWidth: 0
            }
        }
    };
});

const fetchData = async () => {
    try {
        const end = Math.floor(Date.now() / 1000);
        const start = props.hours === 0 || props.hours === '0' ? end - 86400 * 7 : end - (props.hours * 3600);

        const datasets = [];
        const allLabels = new Set();

        for (const query of props.queries) {
            const response = await axios.get('/api/query', {
                params: {
                    query: query.query,
                    start: start,
                    end: end,
                    step: calculateStep()
                }
            });

            const data = response.data.data;
            if (data && data.values) {
                // Aggregate data by time period
                const aggregated = aggregateData(data.values, props.aggregation);

                const labels = aggregated.map(v => v.label);
                labels.forEach(l => allLabels.add(l));

                datasets.push({
                    label: query.label || query.query,
                    data: aggregated.map(v => v.value),
                    backgroundColor: query.color || '#3b82f6',
                    borderColor: query.color || '#3b82f6',
                });
            }
        }

        chartData.value = {
            labels: Array.from(allLabels),
            datasets: datasets
        };
    } catch (error) {
        console.error('Failed to fetch bar chart data:', error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Daten konnten nicht geladen werden',
            life: 3000
        });
    }
};

const calculateStep = () => {
    // Determine step size based on hours
    const h = parseInt(props.hours) || 12;
    if (h <= 6) return 60; // 1 minute
    if (h <= 24) return 300; // 5 minutes
    if (h <= 48) return 600; // 10 minutes
    return 3600; // 1 hour
};

const aggregateData = (values, aggregation) => {
    // Aggregate data by time period (e.g., by hour, by day)
    const grouped = {};

    values.forEach(([timestamp, value]) => {
        const date = new Date(timestamp * 1000);
        let key;

        if (props.hours <= 24) {
            // Group by hour
            key = `${date.getDate()}.${date.getMonth() + 1}. ${date.getHours()}:00`;
        } else {
            // Group by day
            key = `${date.getDate()}.${date.getMonth() + 1}.`;
        }

        if (!grouped[key]) {
            grouped[key] = [];
        }
        grouped[key].push(value);
    });

    // Calculate aggregation
    return Object.entries(grouped).map(([label, vals]) => {
        let aggregatedValue;
        switch (aggregation) {
            case 'sum':
                aggregatedValue = vals.reduce((a, b) => a + b, 0);
                break;
            case 'min':
                aggregatedValue = Math.min(...vals);
                break;
            case 'max':
                aggregatedValue = Math.max(...vals);
                break;
            case 'avg':
            default:
                aggregatedValue = vals.reduce((a, b) => a + b, 0) / vals.length;
                break;
        }
        return { label, value: aggregatedValue };
    }).sort((a, b) => {
        // Sort by label (time)
        return a.label.localeCompare(b.label);
    });
};

const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value;
};

const openConfig = () => {
    configDialog.value.open();
};

const confirmDelete = () => {
    confirm.require({
        message: 'Möchtest du dieses Diagramm wirklich löschen?',
        header: 'Löschen bestätigen',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Ja',
        rejectLabel: 'Nein',
        accept: () => {
            emit('deleted', props.chartId);
        }
    });
};

watch(() => [props.queries, props.hours, props.barMode, props.aggregation], () => {
    fetchData();
}, { deep: true });

onMounted(() => {
    fetchData();
});
</script>
