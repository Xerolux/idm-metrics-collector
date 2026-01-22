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
                <span class="text-xs text-gray-500">Heatmap - letzte {{ displayHours }}</span>
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

            <!-- Heatmap Chart -->
            <div class="flex-grow relative min-h-0 w-full">
                <canvas ref="canvasRef"></canvas>
            </div>

            <!-- Legend -->
            <div class="mt-2 flex items-center justify-center gap-2">
                <span class="text-xs text-gray-500">Min</span>
                <div
                    class="h-4 rounded"
                    :style="{
                        background: `linear-gradient(to right, ${colorScale.min}, ${colorScale.mid}, ${colorScale.max})`,
                        width: '200px'
                    }"
                ></div>
                <span class="text-xs text-gray-500">Max</span>
            </div>
        </div>

        <HeatmapConfigDialog
            ref="configDialog"
            :heatmap="heatmapConfig"
            @save="onConfigSave"
        />

        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import HeatmapConfigDialog from './HeatmapConfigDialog.vue';
import ConfirmDialog from 'primevue/confirmdialog';

const props = defineProps({
    title: { type: String, required: true },
    query: { type: Object, required: true },
    hours: { type: [Number, String], default: 12 },
    chartId: { type: String, required: true },
    dashboardId: { type: String, required: true },
    editMode: { type: Boolean, default: false },
    colorScale: {
        type: Object,
        default: () => ({
            min: '#3b82f6',  // Blue
            mid: '#fbbf24',  // Yellow
            max: '#ef4444'   // Red
        })
    },
    buckets: { type: Number, default: 24 }, // Number of time buckets
    valueRange: { type: Array, default: () => [null, null] } // [min, max] or null for auto
});

const emit = defineEmits(['deleted', 'save']);

const confirm = useConfirm();
const toast = useToast();

const isFullscreen = ref(false);
const canvasRef = ref(null);
const configDialog = ref(null);
const chartContainer = ref(null);
const chartInstance = ref(null);

const heatmapData = ref([]);
const minValue = ref(0);
const maxValue = ref(0);

const heatmapConfig = computed(() => ({
    title: props.title,
    query: props.query,
    hours: props.hours,
    colorScale: props.colorScale,
    buckets: props.buckets,
    valueRange: props.valueRange
}));

const displayHours = computed(() => {
    if (props.hours === 0 || props.hours === '0') return 'Start';
    return props.hours + ' Stunden';
});

const renderHeatmap = () => {
    if (!canvasRef.value || heatmapData.value.length === 0) return;

    const ctx = canvasRef.value.getContext('2d');

    // Destroy existing chart
    if (chartInstance.value) {
        chartInstance.value.destroy();
    }

    // Calculate bucket boundaries
    // const bucketSize = Math.ceil(heatmapData.value.length / props.buckets);

    // Create matrix data for chartjs-chart-matrix
    const matrixData = [];
    // const labels = [];

    for (let i = 0; i < heatmapData.value.length; i++) {
        const [timestamp, value] = heatmapData.value[i];
        const date = new Date(timestamp * 1000);
        const hour = date.getHours();
        const day = date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });

        // const bucketIndex = Math.floor(i / bucketSize);

        matrixData.push({
            x: day,
            y: hour,
            v: value
        });
    }

    // Get value range
    const values = heatmapData.value.map(([, v]) => v);
    const dataMin = props.valueRange[0] !== null ? props.valueRange[0] : Math.min(...values);
    const dataMax = props.valueRange[1] !== null ? props.valueRange[1] : Math.max(...values);

    minValue.value = dataMin;
    maxValue.value = dataMax;

    // Color scale function
    const getColor = (value) => {
        const normalized = (value - dataMin) / (dataMax - dataMin);

        if (normalized < 0.5) {
            // Blue to Yellow
            const ratio = normalized * 2;
            return interpolateColor(props.colorScale.min, props.colorScale.mid, ratio);
        } else {
            // Yellow to Red
            const ratio = (normalized - 0.5) * 2;
            return interpolateColor(props.colorScale.mid, props.colorScale.max, ratio);
        }
    };

    // Create chart
    chartInstance.value = new Chart(ctx, {
        type: 'matrix',
        data: {
            datasets: [{
                label: props.title,
                data: matrixData,
                backgroundColor(ctx) {
                    const value = ctx.dataset.data[ctx.dataIndex]?.v;
                    if (value === undefined || value === null) return '#e5e7eb';
                    return getColor(value);
                },
                borderColor: '#ffffff',
                borderWidth: 1,
                width: ({ chart }) => (chart.chartArea || {}).width / props.buckets - 1,
                height: ({ chart }) => ((chart.chartArea || {}).height / 24) - 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: false,
                tooltip: {
                    callbacks: {
                        title: (items) => {
                            const item = items[0];
                            const data = item.dataset.data[item.dataIndex];
                            return `${data.x} - ${data.y}:00 Uhr`;
                        },
                        label: (context) => {
                            const value = context.dataset.data[context.dataIndex]?.v;
                            return `Wert: ${value !== null ? value.toFixed(2) : 'N/A'}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    labels: [...new Set(matrixData.map(d => d.x))],
                    ticks: {
                        font: { size: 10 }
                    }
                },
                y: {
                    type: 'category',
                    labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
                    offset: true,
                    ticks: {
                        font: { size: 9 }
                    }
                }
            }
        }
    });
};

const interpolateColor = (color1, color2, factor) => {
    // Simple color interpolation
    const c1 = hexToRgb(color1);
    const c2 = hexToRgb(color2);

    const r = Math.round(c1.r + factor * (c2.r - c1.r));
    const g = Math.round(c1.g + factor * (c2.g - c1.g));
    const b = Math.round(c1.b + factor * (c2.b - c1.b));

    return `rgb(${r}, ${g}, ${b})`;
};

const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
};

const fetchData = async () => {
    try {
        const end = Math.floor(Date.now() / 1000);
        const start = props.hours === 0 || props.hours === '0' ? end - 86400 * 7 : end - (props.hours * 3600);

        const response = await axios.get('/api/query', {
            params: {
                query: props.query.query,
                start: start,
                end: end,
                step: calculateStep()
            }
        });

        const data = response.data.data;
        if (data && data.values) {
            heatmapData.value = data.values;
            setTimeout(renderHeatmap, 100);
        }
    } catch (error) {
        console.error('Failed to fetch heatmap data:', error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Daten konnten nicht geladen werden',
            life: 3000
        });
    }
};

const calculateStep = () => {
    const h = parseInt(props.hours) || 12;
    if (h <= 6) return 300; // 5 minutes
    if (h <= 24) return 600; // 10 minutes
    return 3600; // 1 hour
};

const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value;
    setTimeout(renderHeatmap, 100);
};

const openConfig = () => {
    configDialog.value.open();
};

const confirmDelete = () => {
    confirm.require({
        message: 'Möchtest du diese Heatmap wirklich löschen?',
        header: 'Löschen bestätigen',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Ja',
        rejectLabel: 'Nein',
        accept: () => {
            emit('deleted', props.chartId);
        }
    });
};

const onConfigSave = (config) => {
    emit('save', { ...config, id: props.chartId });
};

const setupCanvas = () => {
    if (!canvasRef.value) return;
    const container = canvasRef.value.parentElement;
    canvasRef.value.width = container.clientWidth;
    canvasRef.value.height = container.clientHeight;
};

watch(() => [props.query, props.hours, props.colorScale, props.buckets, props.valueRange], () => {
    fetchData();
}, { deep: true });

watch(isFullscreen, () => {
    setTimeout(() => {
        setupCanvas();
        renderHeatmap();
    }, 100);
});

onMounted(() => {
    setupCanvas();
    fetchData();

    const resizeObserver = new ResizeObserver(() => {
        setupCanvas();
        renderHeatmap();
    });

    if (canvasRef.value) {
        resizeObserver.observe(canvasRef.value.parentElement);
    }

    const interval = setInterval(fetchData, 60000);

    return () => {
        resizeObserver.disconnect();
        clearInterval(interval);
    };
});

onUnmounted(() => {
    if (chartInstance.value) {
        chartInstance.value.destroy();
    }
});
</script>

<script>
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix';
import Chart from 'chart.js/auto';

// Register chartjs-chart-matrix
Chart.register(MatrixController, MatrixElement);
</script>
