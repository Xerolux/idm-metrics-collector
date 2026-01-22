<template>
    <div class="h-full flex flex-col gap-3">
        <!-- Top Bar -->
        <div class="flex items-center justify-between gap-3 flex-shrink-0">
            <div class="flex items-center gap-2 flex-grow">
                <Dropdown
                    v-model="currentDashboardId"
                    :options="dashboards"
                    optionLabel="name"
                    optionValue="id"
                    class="w-64"
                    placeholder="Dashboard wählen"
                />
                <Button
                    @click="createDashboard"
                    icon="pi pi-plus"
                    severity="primary"
                    title="Neues Dashboard"
                />
                <Button
                    @click="confirmDeleteDashboard"
                    icon="pi pi-trash"
                    severity="danger"
                    :disabled="dashboards.length <= 1"
                    title="Dashboard löschen"
                />
            </div>
            <div class="flex items-center gap-2">
                <!-- Time Range Selector -->
                <Dropdown
                    v-model="timeRange"
                    :options="timeRangeOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-40"
                    @change="onTimeRangeChange"
                />
                <Button
                    @click="editMode = !editMode"
                    :icon="editMode ? 'pi pi-lock-open' : 'pi pi-lock'"
                    :severity="editMode ? 'success' : 'secondary'"
                    :label="editMode ? 'Bearbeiten' : 'Normal'"
                />
            </div>
        </div>

        <div class="flex flex-col lg:flex-row gap-3 overflow-hidden">
            <!-- Left Sidebar: Current Values -->
            <div class="w-full lg:w-72 flex-shrink-0 overflow-y-auto">
                <SensorValues />
            </div>

            <!-- Main Grid with Drag & Drop -->
            <div class="flex-grow overflow-y-auto pb-4 pr-1">
                <!-- Draggable Charts Grid -->
                <draggable
                    v-model="currentCharts"
                    :disabled="!editMode"
                    item-key="id"
                    class="grid grid-cols-1 md:grid-cols-2 gap-3"
                    ghost-class="ghost-card"
                    drag-class="dragging-card"
                    @start="onDragStart"
                    @end="onDragEnd"
                >
                    <template #item="{ element: chart }">
                        <div class="h-64 md:h-80">
                            <ChartCard
                                :title="chart.title"
                                :queries="chart.queries"
                                :hours="effectiveHours"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                        </div>
                    </template>
                </draggable>

                <!-- Add Chart Button in Edit Mode -->
                <div
                    v-if="editMode"
                    class="h-64 md:h-80 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center hover:border-teal-500 hover:bg-teal-50 cursor-pointer transition-colors"
                    @click="showAddChartDialog = true"
                >
                    <div class="text-center text-gray-500">
                        <i class="pi pi-plus text-4xl mb-2"></i>
                        <p class="font-medium">Chart hinzufügen</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Chart Dialog -->
        <Dialog
            v-model:visible="showAddChartDialog"
            modal
            header="Neuer Chart"
            :style="{ width: '90vw', maxWidth: '500px' }"
        >
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Titel</label>
                    <InputText
                        v-model="newChart.title"
                        class="w-full"
                        placeholder="Chart-Titel"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Zeitraum (Stunden)</label>
                    <Dropdown
                        v-model="newChart.hours"
                        :options="hourOptions"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full"
                    />
                </div>
            </div>
            <template #footer>
                <Button
                    @click="showAddChartDialog = false"
                    label="Abbrechen"
                    severity="secondary"
                    text
                />
                <Button
                    @click="addChart"
                    label="Hinzufügen"
                    severity="primary"
                    :disabled="!newChart.title || pendingSensors.length === 0"
                />
            </template>
        </Dialog>

        <ConfirmDialog />
        <Toast />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import draggable from 'vuedraggable';
import ChartCard from './ChartCard.vue';
import SensorValues from './SensorValues.vue';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';

const confirm = useConfirm();
const toast = useToast();

const dashboards = ref([]);
const currentDashboardId = ref('');
const editMode = ref(false);
const showAddChartDialog = ref(false);
const pendingSensors = ref([]);

// Time range selector
const timeRange = ref('24h');
const timeRangeOptions = [
    { label: '6 Stunden', value: '6h' },
    { label: '12 Stunden', value: '12h' },
    { label: '24 Stunden', value: '24h' },
    { label: '48 Stunden', value: '48h' },
    { label: '7 Tage', value: '168h' }
];

const effectiveHours = computed(() => {
    return parseInt(timeRange.value);
});

const newChart = ref({
    title: '',
    hours: 24
});

const hourOptions = [
    { label: '6 Stunden', value: 6 },
    { label: '12 Stunden', value: 12 },
    { label: '24 Stunden', value: 24 },
    { label: '48 Stunden', value: 48 },
    { label: '7 Tage', value: 168 }
];

const currentDashboard = computed(() => {
    return dashboards.value.find(d => d.id === currentDashboardId.value);
});

// Use v-model directly for draggable - it needs to be writable
const currentCharts = ref([]);

// Debounce timer
let saveTimer = null;
let isDragging = false;

// Watch for dashboard changes and update charts
watch(() => currentDashboardId.value, (newId) => {
    const dashboard = dashboards.value.find(d => d.id === newId);
    if (dashboard && dashboard.charts) {
        currentCharts.value = [...dashboard.charts];
    } else {
        currentCharts.value = [];
    }
}, { immediate: true });

// Watch for charts array changes (from drag & drop)
watch(currentCharts, (newCharts) => {
    // Only save if we're in edit mode, NOT dragging, and dashboard exists
    if (editMode.value && !isDragging && currentDashboard.value) {
        // Debounce save to avoid too many API calls
        if (saveTimer) clearTimeout(saveTimer);
        saveTimer = setTimeout(() => {
            saveChartOrder(newCharts);
        }, 500);
    }
}, { deep: true });

const loadDashboards = async () => {
    try {
        const res = await axios.get('/api/dashboards');
        dashboards.value = res.data;
        if (dashboards.value.length > 0 && !currentDashboardId.value) {
            currentDashboardId.value = dashboards.value[0].id;
        }
    } catch (e) {
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Dashboards konnten nicht geladen werden',
            life: 5000
        });
    }
};

const saveChartOrder = async (charts) => {
    try {
        await axios.put(`/api/dashboards/${currentDashboardId.value}`, {
            charts: charts
        });
        // Update local dashboard data
        const dashboard = dashboards.value.find(d => d.id === currentDashboardId.value);
        if (dashboard) {
            dashboard.charts = [...charts];
        }
    } catch (e) {
        console.error('Failed to save chart order:', e);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Reihenfolge konnte nicht gespeichert werden',
            life: 3000
        });
    }
};

const onDragStart = () => {
    isDragging = true;
};

const onDragEnd = () => {
    isDragging = false;
    // Save immediately after drag ends
    saveChartOrder(currentCharts.value);
    toast.add({
        severity: 'success',
        summary: 'Gespeichert',
        detail: 'Chart-Reihenfolge gespeichert',
        life: 2000
    });
};

const createDashboard = async () => {
    const name = prompt('Name des neuen Dashboards:');
    if (!name) return;

    try {
        const res = await axios.post('/api/dashboards', { name });
        dashboards.value.push(res.data);
        currentDashboardId.value = res.data.id;
        toast.add({
            severity: 'success',
            summary: 'Erstellt',
            detail: `Dashboard "${name}" erstellt`,
            life: 3000
        });
    } catch (e) {
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Dashboard konnte nicht erstellt werden',
            life: 5000
        });
    }
};

const confirmDeleteDashboard = () => {
    if (dashboards.value.length <= 1) return;

    const dashboard = currentDashboard.value;
    confirm.require({
        message: `Dashboard "${dashboard.name}" wirklich löschen?`,
        header: 'Bestätigung',
        icon: 'pi pi-exclamation-triangle',
        accept: () => deleteDashboard()
    });
};

const deleteDashboard = async () => {
    try {
        await axios.delete(`/api/dashboards/${currentDashboardId.value}`);
        dashboards.value = dashboards.value.filter(d => d.id !== currentDashboardId.value);
        currentDashboardId.value = dashboards.value[0]?.id || '';
        toast.add({
            severity: 'success',
            summary: 'Gelöscht',
            detail: 'Dashboard wurde gelöscht',
            life: 3000
        });
    } catch (e) {
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Dashboard konnte nicht gelöscht werden',
            life: 5000
        });
    }
};

const onTimeRangeChange = () => {
    console.log('Time range changed to:', timeRange.value);
};

const addChart = async () => {
    const queries = pendingSensors.value.map((s, i) => {
        const colors = ['#f59e0b', '#3b82f6', '#ef4444', '#22c55e', '#a855f7', '#ec4899'];
        return {
            label: s.display,
            query: s.name,
            color: colors[i % colors.length]
        };
    });

    try {
        const res = await axios.post(`/api/dashboards/${currentDashboardId.value}/charts`, {
            title: newChart.value.title,
            queries,
            hours: newChart.value.hours
        });

        const dashboard = dashboards.value.find(d => d.id === currentDashboardId.value);
        if (dashboard) {
            dashboard.charts.push(res.data);
            currentCharts.value = [...dashboard.charts];
        }

        showAddChartDialog.value = false;
        newChart.value = { title: '', hours: 24 };
        pendingSensors.value = [];

        toast.add({
            severity: 'success',
            summary: 'Hinzugefügt',
            detail: 'Chart wurde hinzugefügt',
            life: 3000
        });
    } catch (e) {
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Chart konnte nicht hinzugefügt werden',
            life: 5000
        });
    }
};

const onChartDeleted = () => {
    loadDashboards();
};

onMounted(() => {
    loadDashboards();
});
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

/* Drag & Drop Styles */
.ghost-card {
    opacity: 0.5;
    background: #f0f9ff;
}

.dragging-card {
    cursor: grabbing;
    opacity: 0.9;
    transform: scale(1.02);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
</style>
