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
                <span class="text-xs text-gray-500">Status-Verlauf - letzte {{ displayHours }}</span>
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

            <!-- Timeline Chart -->
            <div class="flex-grow relative min-h-0 w-full">
                <canvas ref="canvasRef"></canvas>
            </div>

            <!-- Legend -->
            <div class="mt-2 flex flex-wrap gap-2 justify-center">
                <div
                    v-for="(state, index) in uniqueStates"
                    :key="index"
                    class="flex items-center gap-1 px-2 py-1 rounded text-xs"
                    :style="{ backgroundColor: stateColors[state] + '20', color: stateColors[state] }"
                >
                    <div class="w-2 h-2 rounded-full" :style="{ backgroundColor: stateColors[state] }"></div>
                    <span>{{ state }}</span>
                </div>
            </div>
        </div>

        <StateTimelineConfigDialog
            ref="configDialog"
            :timeline="timelineConfig"
            @save="onConfigSave"
        />

        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import StateTimelineConfigDialog from './StateTimelineConfigDialog.vue';
import ConfirmDialog from 'primevue/confirmdialog';

const props = defineProps({
    title: { type: String, required: true },
    query: { type: Object, required: true }, // Single query for state
    hours: { type: [Number, String], default: 12 },
    chartId: { type: String, required: true },
    dashboardId: { type: String, required: true },
    editMode: { type: Boolean, default: false },
    stateColors: { type: Object, default: () => ({}) } // { 'An': '#22c55e', 'Aus': '#ef4444' }
});

const emit = defineEmits(['deleted', 'save']);

const confirm = useConfirm();
const toast = useToast();

const isFullscreen = ref(false);
const canvasRef = ref(null);
const configDialog = ref(null);
// const chartInstance = ref(null);

const timelineData = ref([]);
const uniqueStates = ref([]);

const timelineConfig = computed(() => ({
    title: props.title,
    query: props.query,
    hours: props.hours,
    stateColors: props.stateColors
}));

const displayHours = computed(() => {
    if (props.hours === 0 || props.hours === '0') return 'Start';
    return props.hours + ' Stunden';
});

const renderTimeline = () => {
    if (!canvasRef.value || timelineData.value.length === 0) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const padding = { top: 20, right: 20, bottom: 40, left: 120 };
    const width = canvas.width - padding.left - padding.right;
    const height = canvas.height - padding.top - padding.bottom;

    // Get time range
    const startTime = timelineData.value[0].start;
    const endTime = timelineData.value[timelineData.value.length - 1].end;
    const timeRange = endTime - startTime;

    // Draw Y-axis labels (states)
    const states = [...new Set(timelineData.value.map(d => d.state))];
    const stateHeight = height / states.length;

    states.forEach((state, index) => {
        const y = padding.top + index * stateHeight + stateHeight / 2;
        ctx.fillStyle = props.stateColors[state] || '#6b7280';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(state, padding.left - 10, y);
    });

    // Draw timeline segments
    timelineData.value.forEach((segment) => {
        const stateIndex = states.indexOf(segment.state);
        const y = padding.top + stateIndex * stateHeight;
        const segmentHeight = stateHeight;

        // Calculate x positions
        const x1 = padding.left + ((segment.start - startTime) / timeRange) * width;
        const x2 = padding.left + ((segment.end - startTime) / timeRange) * width;
        const segmentWidth = x2 - x1;

        // Draw segment
        ctx.fillStyle = props.stateColors[segment.state] || '#6b7280';
        ctx.fillRect(x1, y, Math.max(segmentWidth, 1), segmentHeight);

        // Draw border
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.strokeRect(x1, y, Math.max(segmentWidth, 1), segmentHeight);
    });

    // Draw time axis
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding.left, padding.top + height);
    ctx.lineTo(padding.left + width, padding.top + height);
    ctx.stroke();

    // Draw time labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    const timeSteps = 6;
    for (let i = 0; i <= timeSteps; i++) {
        const x = padding.left + (width / timeSteps) * i;
        const time = startTime + (timeRange / timeSteps) * i;
        const date = new Date(time * 1000);

        let label;
        if (timeRange > 86400) { // More than 1 day
            label = date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });
        } else {
            label = date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
        }

        ctx.fillText(label, x, padding.top + height + 10);
    }
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
            // Detect state changes
            const segments = [];
            let currentState = null;
            let segmentStart = null;

            data.values.forEach(([timestamp, value]) => {
                const state = String(value);

                if (state !== currentState) {
                    // State changed
                    if (segmentStart !== null) {
                        segments.push({
                            state: currentState,
                            start: segmentStart,
                            end: timestamp
                        });
                    }

                    currentState = state;
                    segmentStart = timestamp;
                }
            });

            // Add last segment
            if (segmentStart !== null && currentState !== null) {
                segments.push({
                    state: currentState,
                    start: segmentStart,
                    end: end
                });
            }

            timelineData.value = segments;
            uniqueStates.value = [...new Set(segments.map(s => s.state))];

            // Render after data is loaded
            setTimeout(renderTimeline, 100);
        }
    } catch (error) {
        console.error('Failed to fetch timeline data:', error);
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
    if (h <= 6) return 60;
    if (h <= 24) return 300;
    return 600;
};

const toggleFullscreen = () => {
    isFullscreen.value = !isFullscreen.value;
    setTimeout(renderTimeline, 100);
};

const openConfig = () => {
    configDialog.value.open();
};

const confirmDelete = () => {
    confirm.require({
        message: 'Möchtest du diese Timeline wirklich löschen?',
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

// Setup canvas size
const setupCanvas = () => {
    if (!canvasRef.value) return;

    const container = canvasRef.value.parentElement;
    canvasRef.value.width = container.clientWidth;
    canvasRef.value.height = container.clientHeight;
};

watch(() => [props.query, props.hours, props.stateColors], () => {
    fetchData();
}, { deep: true });

watch(isFullscreen, () => {
    setTimeout(() => {
        setupCanvas();
        renderTimeline();
    }, 100);
});

onMounted(() => {
    setupCanvas();
    fetchData();

    // Setup resize observer
    const resizeObserver = new ResizeObserver(() => {
        setupCanvas();
        renderTimeline();
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
    // Cleanup
});
</script>
