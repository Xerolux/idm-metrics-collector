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
                <span class="text-xs text-gray-500">Verlauf - letzte {{ displayHours }}</span>
            </div>
            <div class="flex items-center gap-1">
                <button
                    @click="resetZoom"
                    class="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
                    title="Zoom zurücksetzen"
                    v-if="isZoomed"
                >
                    <i class="pi pi-times text-xs"></i>
                </button>
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
                <!-- No Data Message -->
                <div
                    v-if="!hasData && !isLoading"
                    class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
                >
                    <div class="text-center">
                        <i class="pi pi-info-circle text-2xl mb-2"></i>
                        <p>Keine Daten verfügbar</p>
                        <p class="text-xs mt-1" v-if="queries && queries.length === 0">
                            Ziehe Sensoren aus der linken Sidebar in diesen Chart
                        </p>
                    </div>
                </div>
                <!-- Loading State -->
                <div
                    v-if="isLoading"
                    class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
                >
                    <i class="pi pi-spin pi-spinner text-2xl"></i>
                </div>
                <Line v-if="!isLoading" ref="chartRef" :data="chartData" :options="chartOptions" @zoom="onZoom" @zoomComplete="onZoomComplete" />
            </div>

            <!-- Stats Table (embedded below chart) -->
            <div v-if="hasData" class="mt-auto pt-2 border-t border-gray-100 flex-shrink-0">
                 <div v-for="stat in stats" :key="stat.label" class="flex items-center justify-between text-[10px] text-gray-600 px-1 py-0.5 hover:bg-gray-50 rounded transition-colors">
                     <div class="flex items-center gap-2 min-w-0 overflow-hidden">
                         <span class="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm" :style="{ backgroundColor: stat.color }"></span>
                         <span class="font-medium truncate" :title="stat.label">{{ stat.label }}</span>
                     </div>
                     <div class="flex gap-3 flex-shrink-0 font-mono text-[10px]">
                         <div class="flex flex-col sm:flex-row sm:gap-1 items-end sm:items-baseline">
                            <span class="text-gray-400 text-[9px]">Min</span>
                            <span class="text-gray-700 font-semibold">{{ stat.min.toFixed(1) }}</span>
                         </div>
                         <div class="flex flex-col sm:flex-row sm:gap-1 items-end sm:items-baseline">
                            <span class="text-gray-400 text-[9px]">Max</span>
                            <span class="text-gray-700 font-semibold">{{ stat.max.toFixed(1) }}</span>
                         </div>
                         <div class="flex flex-col sm:flex-row sm:gap-1 items-end sm:items-baseline">
                            <span class="text-gray-400 text-[9px]">Avg</span>
                            <span class="text-gray-700 font-semibold">{{ stat.avg.toFixed(1) }}</span>
                         </div>
                     </div>
                 </div>
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
import { ref, shallowRef, onMounted, onUnmounted, watch, computed } from 'vue';
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
import annotationPlugin from 'chartjs-plugin-annotation';
import { Line } from 'vue-chartjs';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import { wsClient } from '../utils/websocket.js';
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
  zoomPlugin,
  annotationPlugin
);

const props = defineProps({
    title: { type: String, required: true },
    queries: { type: Array, required: true },
    hours: { type: [Number, String], default: 12 },
    chartId: { type: String, required: true },
    dashboardId: { type: String, required: true },
    editMode: { type: Boolean, default: false },
    yAxisMode: { type: String, default: 'single' }, // 'single' or 'dual'
    alertThresholds: { type: Array, default: () => [] } // [{value: 80, color: 'red', label: 'Critical'}, ...]
});

const emit = defineEmits(['deleted']);

const confirm = useConfirm();
const toast = useToast();

// ⚡ Bolt: Use shallowRef for performance with large datasets to avoid deep reactivity overhead.
// The chart is manually updated for real-time data, and replaced entirely for historical fetches.
const chartData = shallowRef({
    labels: [],
    datasets: []
});

const isFullscreen = ref(false);
const isZoomed = ref(false);
const isLoading = ref(true);
const chartContainer = ref(null);
const chartRef = ref(null);
const configDialog = ref(null);
const stats = ref([]);
const annotations = ref([]);
const pendingUpdate = ref(false);
let interval = null;


const chartConfig = computed(() => ({
    title: props.title,
    queries: props.queries,
    hours: props.hours,
    alertThresholds: props.alertThresholds
}));

const displayHours = computed(() => {
    if (props.hours === 0 || props.hours === '0') return 'Start';
    return props.hours + ' Stunden';
});

const hasData = computed(() => chartData.value.datasets.length > 0);

const chartOptions = computed(() => {
    const isDual = props.yAxisMode === 'dual' && props.queries.length > 1;
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
                display: false
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
                boxPadding: 4,
                usePointStyle: true,
                callbacks: {
                    title: function(context) {
                        if (context[0] && context[0].parsed.x) {
                            const date = new Date(context[0].parsed.x);
                            return date.toLocaleString('de-DE', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                        }
                        return '';
                    },
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toFixed(2);
                        }
                        return label;
                    }
                }
            },
            zoom: {
                zoom: {
                    wheel: {
                        enabled: false
                    },
                    pinch: {
                        enabled: true
                    },
                    drag: {
                        enabled: true
                    }
                },
                pan: {
                    enabled: true,
                    mode: 'x'
                }
            },
            annotation: {
                annotations: {
                    // Alert thresholds (horizontal lines)
                    ...props.alertThresholds.reduce((acc, threshold, index) => {
                        acc[`threshold-${index}`] = {
                            type: 'line',
                            yMin: threshold.value,
                            yMax: threshold.value,
                            borderColor: threshold.color || 'red',
                            borderWidth: 2,
                            borderDash: [6, 6],
                            label: {
                                display: true,
                                content: threshold.label || `Threshold: ${threshold.value}`,
                                position: 'end',
                                backgroundColor: threshold.color || 'red',
                                font: { size: 10 }
                            }
                        };
                        return acc;
                    }, {}),
                    // Time-based annotations (vertical lines)
                    ...annotations.value.reduce((acc, annotation, index) => {
                        if (!annotation.time || isNaN(annotation.time)) return acc;
                        acc[`annotation-${index}`] = {
                            type: 'line',
                            xMin: annotation.time * 1000, // Chart.js uses milliseconds
                            xMax: annotation.time * 1000,
                            borderColor: annotation.color,
                            borderWidth: 2,
                            borderDash: [4, 4],
                            label: {
                                display: true,
                                content: annotation.text,
                                position: 'start',
                                backgroundColor: annotation.color,
                                color: '#fff',
                                font: { size: 10 },
                                xAdjust: 5,
                                yAdjust: -10
                            }
                        };
                        return acc;
                    }, {})
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
                    color: isDark ? '#374151' : '#f0f0f0'
                },
                ticks: {
                    maxTicksLimit: 8,
                    maxRotation: 0,
                    color: isDark ? '#9ca3af' : '#666',
                    font: { size: 10 }
                }
            },
            y: {
                display: true,
                position: 'left',
                grid: {
                    color: isDark ? '#374151' : '#f0f0f0'
                },
                ticks: {
                    color: isDark ? '#9ca3af' : '#666',
                    font: { size: 10 }
                }
            },
            ...(isDual ? {
                y1: {
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: isDark ? '#9ca3af' : '#666',
                        font: { size: 10 }
                    }
                }
            } : {})
        },
        elements: {
            point: {
                radius: 2,
                hitRadius: 10,
                hoverRadius: 4
            },
            line: {
                tension: 0.4,
                borderWidth: 2
            }
        }
    };
});

const calculateStats = (datasets) => {
    const calculatedStats = [];
    datasets.forEach(ds => {
        // Extract y values and filter out non-numbers
        // Data format is [{x, y}, ...]
        const values = ds.data.map(d => d.y).filter(v => v !== null && !isNaN(v));

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
    console.log('[ChartCard] fetchData called for:', props.title, 'with', props.queries?.length || 0, 'queries');
    isLoading.value = true;

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

    // Check if we have any queries
    if (!props.queries || props.queries.length === 0) {
        console.warn('[ChartCard] No queries configured for chart:', props.title);
        isLoading.value = false;
        return;
    }

    // Separate metric and expression queries
    const metricQueries = props.queries.filter(q => !q.type || q.type === 'metric');
    const expressionQueries = props.queries.filter(q => q.type === 'expression');

    // Fetch all metric queries first
    const metricPromises = metricQueries.map(async (q) => {
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
        } catch (error) {
            console.error(`Chart data fetch error for ${q.label}:`, error);
            return { q, res: null };
        }
    });

    const metricResults = await Promise.all(metricPromises);

    // Build a map of query data for expression evaluation
    const queryDataMap = {};

    // Process metric queries
    for (const { q, res } of metricResults) {
        if (res && res.data && res.data.status === 'success') {
            const result = res.data.data.result;

            console.log(`[ChartCard] Data for ${q.label}:`, {
                resultCount: result.length,
                hasValues: result.length > 0 && result[0].values
            });

            if (result.length > 0) {
                const values = result[0].values; // [[timestamp, "value"], ...]
                const dataPoints = values.map(v => ({
                    x: v[0] * 1000,
                    y: parseFloat(v[1])
                }));

                const dataset = {
                    label: q.label,
                    _query: q.query,
                    data: dataPoints,
                    borderColor: q.color,
                    backgroundColor: q.color,
                    fill: false,
                    spanGaps: true
                };

                // Assign to second Y-axis if in dual mode and this is the second query
                if (props.yAxisMode === 'dual' && datasets.length >= 1) {
                    dataset.yAxisID = 'y1';
                }

                datasets.push(dataset);

                // Store data for expression evaluation
                if (q.label) {
                    queryDataMap[q.label.toUpperCase()] = values;
                }
            }
        }
    }

    // Evaluate expression queries
    for (const q of expressionQueries) {
        if (q.expression && q.label) {
            try {
                const exprRes = await axios.post('/api/query/evaluate', {
                    expression: q.expression,
                    queries: queryDataMap
                });

                if (exprRes.data && exprRes.data.status === 'success') {
                    const values = exprRes.data.data.values; // [[timestamp, value], ...]
                    const dataPoints = values.map(v => ({
                        x: v[0] * 1000,
                        y: parseFloat(v[1])
                    }));

                    const dataset = {
                        label: q.label,
                        data: dataPoints,
                        borderColor: q.color,
                        backgroundColor: q.color,
                        fill: false,
                        spanGaps: true
                    };

                    // Assign to second Y-axis if in dual mode
                    if (props.yAxisMode === 'dual' && datasets.length >= 1) {
                        dataset.yAxisID = 'y1';
                    }

                    datasets.push(dataset);
                }
            } catch (error) {
                console.error(`Expression evaluation error for ${q.label}:`, error);
            }
        }
    }

    chartData.value = {
        labels: [],
        datasets
    };
    calculateStats(datasets);
    isLoading.value = false;

    console.log('[ChartCard] fetchData complete for:', props.title, 'with', datasets.length, 'datasets');
};

const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value;
};

const resetZoom = () => {
    if (chartRef.value) {
        const chart = chartRef.value.chart;
        chart.resetZoom();
        isZoomed.value = false;
    }
};

const onZoom = () => {
    isZoomed.value = true;
};

const onZoomComplete = () => {
    // Check if zoom is actually applied
    if (chartRef.value) {
        const chart = chartRef.value.chart;
        const xScale = chart.scales.x;
        if (xScale.min > xScale.options.min || xScale.max < xScale.options.max) {
            isZoomed.value = true;
        } else {
            isZoomed.value = false;
        }
    }
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
    } catch (error) {
        console.error('Save error:', error);
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
    } catch (error) {
        console.error('Delete error:', error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Chart konnte nicht gelöscht werden',
            life: 5000
        });
    }
};

const loadAnnotations = async () => {
    try {
        const end = Math.floor(Date.now() / 1000);
        const start = props.hours === 0 || props.hours === '0' ? end - 86400 * 7 : end - (props.hours * 3600);

        const response = await axios.get('/api/annotations', {
            params: {
                dashboard_id: props.dashboardId,
                start: start,
                end: end
            }
        });

        annotations.value = response.data;
    } catch (error) {
        console.error('Failed to load annotations:', error);
        // Don't show toast for annotations loading errors
    }
};

const requestChartUpdate = () => {
    if (pendingUpdate.value) return;

    pendingUpdate.value = true;
    requestAnimationFrame(() => {
        if (chartRef.value && chartRef.value.chart) {
            chartRef.value.chart.update('none');
        }
        pendingUpdate.value = false;
    });
};

// Handle metric updates
const handleMetricUpdate = (data) => {
    if (!chartRef.value || !chartData.value.datasets) return;

    let updated = false;

    // ⚡ Bolt: Helper to process a single point, handling both single and batched updates
    const processPoint = (point) => {
        if (!point || !point.metric) return;

        const metric = point.metric;
        const value = point.value;
        const timestamp = point.timestamp * 1000; // Convert to milliseconds

        // Find dataset that corresponds to this metric
        const dataset = chartData.value.datasets.find(ds => ds._query === metric);

        if (dataset) {
            // Add new data point
            dataset.data.push({ x: timestamp, y: value });

            // Remove old data points to prevent memory leak (keep last 1000 points)
            if (dataset.data.length > 1000) {
                dataset.data.shift();
            }
            updated = true;
        }
    };

    // Check if batch (map) or single
    if (data.metric) {
        processPoint(data);
    } else {
        // Assume batch map from wsClient
        Object.values(data).forEach(point => processPoint(point));
    }

    if (updated) {
        requestChartUpdate();
    }
};

onMounted(() => {
    // Debug: Log props
    console.log('[ChartCard] Mounted with props:', {
        title: props.title,
        queriesCount: props.queries?.length || 0,
        queries: props.queries,
        hours: props.hours,
        chartId: props.chartId,
        dashboardId: props.dashboardId
    });

    fetchData();
    loadAnnotations();
    interval = setInterval(fetchData, 60000);

    // WebSocket connection for real-time updates
    if (wsClient && !wsClient.isConnected()) {
        wsClient.connect();
    }

    // Subscribe to metric updates
    const metrics = props.queries
        .filter(q => !q.type || q.type === 'metric')
        .map(q => q.query);

    if (metrics.length > 0) {
        wsClient.subscribe(metrics, props.dashboardId);
    } else {
        console.warn('[ChartCard] No metrics to subscribe to for chart:', props.title);
    }

    wsClient.on('metric_update', handleMetricUpdate);

    // Cleanup on fullscreen change
    watch(isFullscreen, () => {
        // Force chart resize
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
});

onUnmounted(() => {
    if (interval) clearInterval(interval);

    // Remove event listener
    wsClient.off('metric_update', handleMetricUpdate);

    // Unsubscribe from WebSocket updates
    if (wsClient && wsClient.isConnected()) {
        const metrics = props.queries
            .filter(q => !q.type || q.type === 'metric')
            .map(q => q.query);

        if (metrics.length > 0) {
            wsClient.unsubscribe(metrics, props.dashboardId);
        }
    }
});

watch(() => props.queries, fetchData);
watch(() => props.hours, () => {
    fetchData();
    loadAnnotations();
});
watch(() => props.dashboardId, loadAnnotations);
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
