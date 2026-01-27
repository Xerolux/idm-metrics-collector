<template>
    <div
        ref="dashboardElement"
        class="h-full flex flex-col gap-3"
        :data-dashboard-id="currentDashboardId"
    >
        <!-- Applied custom CSS (scoped, sanitized for security) -->
        <component
            :is="'style'"
            v-if="sanitizedCustomCss"
            :data-dashboard-id="currentDashboardId"
        >
            {{ sanitizedCustomCss }}
        </component>

        <!-- Top Bar -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 flex-shrink-0">
            <div class="flex flex-wrap items-center gap-2 flex-grow w-full sm:w-auto">
                <!-- Heatpump Selector -->
                <HeatpumpSelector
                    v-model:show-setup="showHeatpumpSetup"
                    @added="onHeatpumpAdded"
                />

                <Select
                    v-model="currentDashboardId"
                    :options="filteredDashboards"
                    optionLabel="name"
                    optionValue="id"
                    class="w-full sm:w-64"
                    placeholder="Dashboard wählen"
                />
                <div class="flex gap-2">
                    <Button
                        @click="createDashboard"
                        icon="pi pi-plus"
                        severity="primary"
                        title="Neues Dashboard"
                    />
                    <Button
                        @click="showTemplateDialog = true"
                        icon="pi pi-copy"
                        severity="secondary"
                        title="Aus Vorlage erstellen"
                    />
                    <Button
                        @click="openDashboardSettings"
                        icon="pi pi-cog"
                        severity="secondary"
                        title="Dashboard Einstellungen"
                    />
                    <Button
                        @click="confirmDeleteDashboard"
                        icon="pi pi-trash"
                        severity="danger"
                        :disabled="dashboards.length <= 1"
                        title="Dashboard löschen"
                    />
                </div>
            </div>
            <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                <!-- Time Range Selector -->
                <Select
                    v-model="timeRange"
                    :options="timeRangeOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full sm:w-48"
                    @change="onTimeRangeChange"
                />
                <div class="flex gap-2">
                    <Button
                        @click="showExportDialog = true"
                        icon="pi pi-download"
                        severity="secondary"
                        title="Exportieren"
                    />
                    <Button
                        @click="showAnnotationsDialog = true"
                        icon="pi pi-bookmark"
                        severity="secondary"
                        title="Annotations"
                    />
                    <Button
                        @click="showVariablesDialog = true"
                        icon="pi pi-sliders-h"
                        severity="secondary"
                        title="Variables"
                    />
                    <Button
                        @click="editMode = !editMode"
                        :icon="editMode ? 'pi pi-lock-open' : 'pi pi-lock'"
                        :severity="editMode ? 'success' : 'secondary'"
                        :label="editMode ? 'Bearbeiten' : 'Normal'"
                    />
                </div>
            </div>
        </div>

        <!-- Overview Header -->
        <OverviewHeader />

        <!-- Variable Selector -->
        <VariableSelector
            v-if="variables.length > 0 && !editMode"
            @change="onVariableChange"
        />

        <div class="flex-grow min-h-0 flex flex-col lg:flex-row gap-3 lg:overflow-hidden">
            <!-- Left Sidebar: Current Values -->
            <div class="w-full lg:w-72 flex-shrink-0 overflow-y-auto">
                <SensorValues @sensor-drag-start="onSensorDragStart" />
            </div>

            <!-- Main Grid with Drag & Drop -->
            <div
                class="flex-grow overflow-y-auto pb-4 pr-1 relative"
                @dragover.prevent
                @drop="onDrop"
            >
                <div v-if="isDraggingSensor" class="absolute inset-0 bg-teal-50/50 z-50 border-2 border-dashed border-teal-500 rounded-lg flex items-center justify-center pointer-events-none">
                     <div class="bg-white p-4 rounded shadow-lg text-teal-700 font-bold">
                         <i class="pi pi-plus mr-2"></i>Hier ablegen um Chart zu erstellen
                     </div>
                </div>

                <!-- Draggable Charts Grid -->
                <draggable
                    v-model="currentCharts"
                    :disabled="!editMode"
                    item-key="id"
                    class="grid grid-cols-1 md:grid-cols-2 gap-3"
                    ghost-class="ghost-card"
                    drag-class="dragging-card"
                    handle=".drag-handle"
                    @start="onDragStart"
                    @end="onDragEnd"
                >
                    <template #item="{ element: chart }">
                        <div class="h-80 relative group">
                            <!-- Drag Handle -->
                            <div v-if="editMode" class="drag-handle absolute top-2 left-2 z-20 cursor-move p-1 bg-white/80 rounded hover:bg-white shadow-sm text-gray-400 hover:text-gray-700">
                                <i class="pi pi-bars"></i>
                            </div>

                            <!-- Dynamic Chart Component -->
                            <ChartCard
                                v-if="!chart.type || chart.type === 'line'"
                                :title="chart.title"
                                :queries="chart.queries"
                                :hours="effectiveHours"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                :alert-thresholds="chart.alertThresholds || []"
                                @deleted="onChartDeleted"
                            />
                            <BarCard
                                v-else-if="chart.type === 'bar'"
                                :title="chart.title"
                                :queries="chart.queries"
                                :hours="effectiveHours"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                            <StatCard
                                v-else-if="chart.type === 'stat'"
                                :title="chart.title"
                                :query="chart.queries[0]?.query || ''"
                                :unit="chart.queries[0]?.unit || ''"
                                :decimals="chart.decimals || 1"
                                :show-trend="chart.showTrend !== false"
                                :show-target="chart.showTarget || false"
                                :target-query="chart.targetQuery"
                                :color-thresholds="chart.colorThresholds"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                            <GaugeCard
                                v-else-if="chart.type === 'gauge'"
                                :title="chart.title"
                                :query="chart.queries[0]?.query || ''"
                                :min="chart.min || 0"
                                :max="chart.max || 100"
                                :thresholds="chart.thresholds"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                            <HeatmapCard
                                v-else-if="chart.type === 'heatmap'"
                                :title="chart.title"
                                :queries="chart.queries"
                                :hours="effectiveHours"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                            <TableCard
                                v-else-if="chart.type === 'table'"
                                :title="chart.title"
                                :queries="chart.queries"
                                :hours="effectiveHours"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                            <StateTimelineCard
                                v-else-if="chart.type === 'state_timeline'"
                                :title="chart.title"
                                :query="chart.queries[0]?.query || ''"
                                :hours="effectiveHours"
                                :chart-id="chart.id"
                                :dashboard-id="currentDashboardId"
                                :edit-mode="editMode"
                                @deleted="onChartDeleted"
                            />
                            <TelemetryStatusCard
                                v-else-if="chart.type === 'telemetry_status'"
                                :sharing-enabled="chart.sharingEnabled !== false"
                            />
                        </div>
                    </template>
                </draggable>

                <!-- Add Chart Button in Edit Mode -->
                <div
                    v-if="editMode"
                    class="mt-3 h-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center hover:border-teal-500 hover:bg-teal-50 cursor-pointer transition-colors"
                    @click="showAddChartDialog = true"
                >
                    <div class="text-center text-gray-500">
                        <i class="pi pi-plus text-4xl mb-2"></i>
                        <p class="font-medium">Chart manuell hinzufügen</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Chart Dialog -->
        <Dialog
            v-model:visible="showAddChartDialog"
            modal
            header="Neuer Chart"
            :style="{ width: '90vw', maxWidth: '600px' }"
        >
            <div class="space-y-4">
                <div v-if="activeHeatpumpId" class="bg-blue-50 p-2 rounded text-sm text-blue-700">
                    Chart wird für Wärmepumpe <strong>{{ activeHeatpumpId }}</strong> erstellt.
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Chart-Typ</label>
                    <Select
                        v-model="newChart.type"
                        :options="chartTypeOptions"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full"
                        placeholder="Chart-Typ wählen"
                    >
                        <template #value="slotProps">
                            <div v-if="slotProps.value" class="flex items-center gap-2">
                                <i :class="slotProps.option.icon" class="text-lg"></i>
                                <span>{{ slotProps.option.label }}</span>
                            </div>
                            <span v-else>{{ slotProps.placeholder }}</span>
                        </template>
                        <template #option="slotProps">
                            <div class="flex items-center gap-2">
                                <i :class="slotProps.option.icon" class="text-lg"></i>
                                <div>
                                    <div class="font-medium">{{ slotProps.option.label }}</div>
                                    <div class="text-xs text-gray-500">{{ slotProps.option.description }}</div>
                                </div>
                            </div>
                        </template>
                    </Select>
                </div>
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
                    <Select
                        v-model="newChart.hours"
                        :options="timeRangeOptions"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full"
                    />
                </div>
                <!-- Query selector for Line/Bar charts -->
                <div v-if="newChart.type === 'line' || newChart.type === 'bar'">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Datenquelle</label>
                    <div class="text-xs text-gray-500 mb-2">
                        Ziehe Sensoren aus der linken Sidebar in den Chart
                    </div>
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
                    :disabled="!newChart.title || !newChart.type"
                />
            </template>
        </Dialog>

        <ChartTemplateDialog v-model="showTemplateDialog" @apply="applyTemplate" />

        <ExportDialog
            v-model="showExportDialog"
            :dashboard-name="currentDashboard?.name || 'Dashboard'"
            :dashboard-element="dashboardElement"
            :dashboard-config="currentDashboard"
        />

        <Dialog
            v-model:visible="showAnnotationsDialog"
            modal
            header="Annotations verwalten"
            :style="{ width: '90vw', maxWidth: '600px' }"
        >
            <AnnotationList
                v-if="showAnnotationsDialog"
                :dashboard-id="currentDashboardId"
                :start-time="annotationsStartTime"
                :end-time="annotationsEndTime"
            />
        </Dialog>

        <Dialog
            v-model:visible="showVariablesDialog"
            modal
            header="Template Variables verwalten"
            :style="{ width: '90vw', maxWidth: '800px' }"
        >
            <div class="space-y-4">
                <div class="flex justify-between items-center mb-4">
                    <p class="text-sm text-gray-600">
                        Variables können in Queries als ${{ '{variable_id}' }} verwendet werden
                    </p>
                    <Button
                        @click="showAddVariableDialog = true"
                        icon="pi pi-plus"
                        size="small"
                        severity="primary"
                        label="Neu"
                    />
                </div>

                <div
                    v-if="variables.length === 0"
                    class="text-center py-8 text-gray-500 text-sm"
                >
                    Keine Variables vorhanden
                </div>

                <div
                    v-for="variable in variables"
                    :key="variable.id"
                    class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
                >
                    <div class="flex-grow">
                        <div class="font-medium text-sm">{{ variable.name }}</div>
                        <div class="text-xs text-gray-500">
                            ID: ${{ '{' + variable.id + '}' }} |
                            Typ: {{ variable.type }} |
                            {{ variable.multi ? 'Mehrfach' : 'Einfach' }}auswahl
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <Button
                            @click="editVariable(variable)"
                            icon="pi pi-pencil"
                            size="small"
                            text
                            severity="secondary"
                        />
                        <Button
                            @click="confirmDeleteVariable(variable)"
                            icon="pi pi-times"
                            size="small"
                            text
                            severity="danger"
                        />
                    </div>
                </div>
            </div>
        </Dialog>

        <VariableDialog
            v-model="showAddVariableDialog"
            :variable="editingVariable"
            @saved="loadVariables"
        />

        <CssEditor
            v-model="showCssEditor"
            :css="currentDashboard?.customCss || ''"
            @save="handleCssSave"
        />

        <ConfirmDialog />
        <Toast />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import axios from 'axios';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import draggable from 'vuedraggable';
import { useHeatpumpsStore } from '@/stores/heatpumps';
import { getSupportedChartTypes } from '../utils/chartTypes';
import ChartCard from './ChartCard.vue';
import BarCard from './BarCard.vue';
import StatCard from './StatCard.vue';
import GaugeCard from './GaugeCard.vue';
import HeatmapCard from './HeatmapCard.vue';
import TableCard from './TableCard.vue';
import StateTimelineCard from './StateTimelineCard.vue';
import TelemetryStatusCard from './TelemetryStatusCard.vue';
import SensorValues from './SensorValues.vue';
import OverviewHeader from './OverviewHeader.vue';
import HeatpumpSelector from './heatpump/HeatpumpSelector.vue';
import Select from 'primevue/select';
// import MultiSelect from 'primevue/multiselect';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import ChartTemplateDialog from './ChartTemplateDialog.vue';
import ExportDialog from './ExportDialog.vue';
import AnnotationList from './AnnotationList.vue';
import VariableDialog from './VariableDialog.vue';
import VariableSelector from './VariableSelector.vue';
import CssEditor from './CssEditor.vue';
import { sanitizeCss } from '@/utils/cssSanitizer';

const confirm = useConfirm();
const toast = useToast();
const hpStore = useHeatpumpsStore();

const dashboards = ref([]);
const currentDashboardId = ref('');
const editMode = ref(false);
const showAddChartDialog = ref(false);
const showTemplateDialog = ref(false);
const showExportDialog = ref(false);
const showAnnotationsDialog = ref(false);
const showVariablesDialog = ref(false);
const showAddVariableDialog = ref(false);
const showCssEditor = ref(false);
const pendingSensors = ref([]);
const isDraggingSensor = ref(false);
const dashboardElement = ref(null);
const variables = ref([]);
const editingVariable = ref(null);
const variableValues = ref({});

// Time range selector
const timeRange = ref('24h');
const timeRangeOptions = [
    { label: '12 Stunden', value: '12h' },
    { label: '24 Stunden', value: '24h' },
    { label: '48 Stunden', value: '48h' },
    { label: '72 Stunden', value: '72h' },
    { label: '1 Woche', value: '168h' },
    { label: '1 Monat', value: '720h' },
    { label: '3 Monate', value: '2160h' },
    { label: '6 Monate', value: '4320h' },
    { label: '1 Jahr', value: '8760h' },
    { label: 'Alles', value: '0' }
];

const effectiveHours = computed(() => {
    if (timeRange.value === '0') return 0;
    return parseInt(timeRange.value);
});

const newChart = ref({
    type: 'line',
    title: '',
    hours: '24h'
});

// Chart type options for the dropdown
const chartTypeOptions = computed(() => {
    return getSupportedChartTypes().map(config => ({
        value: config.type,
        label: config.name,
        icon: config.icon,
        description: config.description
    }));
});

const activeHeatpumpId = computed(() => hpStore.activeHeatpumpId);

// Filter dashboards by heatpump
const filteredDashboards = computed(() => {
    if (!activeHeatpumpId.value) return dashboards.value;
    return dashboards.value.filter(d =>
        !d.heatpump_id || d.heatpump_id === activeHeatpumpId.value
    );
});

const currentDashboard = computed(() => {
    return dashboards.value.find(d => d.id === currentDashboardId.value);
});

// Watch active heatpump to switch dashboard
watch(activeHeatpumpId, (newId) => {
    if (newId) {
        loadDashboards();
    }
});

const onHeatpumpAdded = () => {
    hpStore.fetchHeatpumps();
};

// Sanitize custom CSS to prevent XSS/CSS injection attacks
const sanitizedCustomCss = computed(() => {
    const css = currentDashboard.value?.customCss;
    if (!css) return '';
    const { sanitized } = sanitizeCss(css);
    return sanitized;
});

// Annotations time range
const annotationsStartTime = computed(() => {
    const end = Math.floor(Date.now() / 1000);
    const start = effectiveHours.value === 0 ? end - 86400 * 7 : end - (effectiveHours.value * 3600);
    return start;
});

const annotationsEndTime = computed(() => {
    return Math.floor(Date.now() / 1000);
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
        const params = {};
        if (activeHeatpumpId.value) {
            params.heatpump_id = activeHeatpumpId.value;
        }
        const res = await axios.get('/api/dashboards/heatpump/' + (activeHeatpumpId.value || 'default'));

        let data = res.data;
        if (!Array.isArray(data)) {
             // Try general endpoint if heatpump specific failed
             const res2 = await axios.get('/api/dashboards');
             data = res2.data;
        }

        dashboards.value = data;

        // Select first if current invalid
        if (!dashboards.value.find(d => d.id === currentDashboardId.value)) {
            if (dashboards.value.length > 0) {
                currentDashboardId.value = dashboards.value[0].id;
            } else {
                currentDashboardId.value = '';
            }
        }
    } catch (error) {
        console.error(error);
        // Fallback to generic load
        try {
             const res = await axios.get('/api/dashboards');
             dashboards.value = res.data;
        } catch (e) {
             toast.add({
                severity: 'error',
                summary: 'Fehler',
                detail: 'Dashboards konnten nicht geladen werden',
                life: 5000
            });
        }
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
        const payload = {
            name,
            heatpump_id: activeHeatpumpId.value
        };
        const res = await axios.post('/api/dashboards', payload);
        dashboards.value.push(res.data);
        currentDashboardId.value = res.data.id;
        toast.add({
            severity: 'success',
            summary: 'Erstellt',
            detail: `Dashboard "${name}" erstellt`,
            life: 3000
        });
    } catch (error) {
        console.error(error);
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
    } catch (error) {
        console.error(error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Dashboard konnte nicht gelöscht werden',
            life: 5000
        });
    }
};

const onTimeRangeChange = () => {
};

// Variables management
const loadVariables = async () => {
    try {
        const response = await axios.get('/api/variables');
        variables.value = response.data;
    } catch (error) {
        console.error('Failed to load variables:', error);
    }
};

const editVariable = (variable) => {
    editingVariable.value = variable;
    showAddVariableDialog.value = true;
};

const confirmDeleteVariable = (variable) => {
    confirm.require({
        message: `Variable "${variable.name}" wirklich löschen?`,
        header: 'Löschen bestätigen',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Ja',
        rejectLabel: 'Nein',
        accept: async () => {
            try {
                await axios.delete(`/api/variables/${variable.id}`);
                await loadVariables();
            } catch (error) {
                console.error('Failed to delete variable:', error);
            }
        }
    });
};

// Handle variable value changes - trigger refresh of all charts
const onVariableChange = (newValues) => {
    variableValues.value = newValues;
    // Force all ChartCard components to refresh by re-rendering
    // The key is to trigger the computed properties in ChartCard
    // This is done by changing the currentDashboardId, which forces a re-fetch
    loadDashboards();
};

// Dashboard settings (including CSS)
const openDashboardSettings = () => {
    showCssEditor.value = true;
};

const handleCssSave = async (css) => {
    if (!currentDashboard.value) return;

    try {
        await axios.put(`/api/dashboards/${currentDashboard.value.id}`, {
            name: currentDashboard.value.name,
            customCss: css
        });

        await loadDashboards();

        toast.add({
            severity: 'success',
            summary: 'Erfolg',
            detail: 'CSS gespeichert',
            life: 2000
        });
    } catch (error) {
        console.error('Failed to save CSS:', error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'CSS konnte nicht gespeichert werden',
            life: 5000
        });
    }
};

const addChart = async () => {
    const queries = pendingSensors.value.length > 0 ? pendingSensors.value.map((s, i) => {
        const colors = ['#f59e0b', '#3b82f6', '#ef4444', '#22c55e', '#a855f7', '#ec4899'];
        return {
            label: s.display,
            query: s.name,
            color: colors[i % colors.length]
        };
    }) : [];

    const hoursVal = newChart.value.hours === '0' ? 0 : parseInt(newChart.value.hours);

    try {
        const res = await axios.post(`/api/dashboards/${currentDashboardId.value}/charts`, {
            type: newChart.value.type,
            title: newChart.value.title,
            queries,
            hours: hoursVal
        });

        const dashboard = dashboards.value.find(d => d.id === currentDashboardId.value);
        if (dashboard) {
            dashboard.charts.push(res.data);
            currentCharts.value = [...dashboard.charts];
        }

        showAddChartDialog.value = false;
        newChart.value = { type: 'line', title: '', hours: '24h' };
        pendingSensors.value = [];

        toast.add({
            severity: 'success',
            summary: 'Hinzugefügt',
            detail: 'Chart wurde hinzugefügt',
            life: 3000
        });
    } catch (error) {
        console.error(error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Chart konnte nicht hinzugefügt werden',
            life: 5000
        });
    }
};

const onSensorDragStart = () => {
    isDraggingSensor.value = true;
};

const onDrop = async (event) => {
    isDraggingSensor.value = false;
    try {
        const metricData = event.dataTransfer.getData('application/json');
        if (!metricData) return;

        const metric = JSON.parse(metricData);

        // Add single chart for dropped metric
        const colors = ['#f59e0b', '#3b82f6', '#ef4444', '#22c55e', '#a855f7', '#ec4899'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];

        const queries = [{
            label: metric.display,
            query: metric.name,
            color: randomColor
        }];

        const res = await axios.post(`/api/dashboards/${currentDashboardId.value}/charts`, {
            title: metric.display,
            queries,
            hours: effectiveHours.value
        });

        const dashboard = dashboards.value.find(d => d.id === currentDashboardId.value);
        if (dashboard) {
            dashboard.charts.push(res.data);
            currentCharts.value = [...dashboard.charts];
        }

        toast.add({
            severity: 'success',
            summary: 'Hinzugefügt',
            detail: 'Chart erstellt',
            life: 2000
        });

    } catch (e) {
        console.error("Drop error", e);
    }
};

// Global drag end listener to reset state if dropped outside
const onGlobalDragEnd = () => {
    isDraggingSensor.value = false;
};

onMounted(async () => {
    await hpStore.fetchHeatpumps();
    loadDashboards();
    loadVariables();
    document.addEventListener('dragend', onGlobalDragEnd);
});

onUnmounted(() => {
    document.removeEventListener('dragend', onGlobalDragEnd);
});

const onChartDeleted = () => {
    loadDashboards();
};

const applyTemplate = async (template) => {
    try {
        // Create new dashboard
        const dashRes = await axios.post('/api/dashboards', { name: template.name });
        const newDashboard = dashRes.data;

        // Add all charts from template
        for (const chartConfig of template.charts) {
            await axios.post(`/api/dashboards/${newDashboard.id}/charts`, {
                title: chartConfig.title,
                queries: chartConfig.queries,
                hours: chartConfig.hours,
                yAxisMode: chartConfig.yAxisMode || 'single'
            });
        }

        // Reload dashboards and switch to new one
        await loadDashboards();
        currentDashboardId.value = newDashboard.id;

        toast.add({
            severity: 'success',
            summary: 'Erstellt',
            detail: `Dashboard "${template.name}" aus Vorlage erstellt`,
            life: 3000
        });
    } catch (e) {
        console.error('Template apply error:', e);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Vorlage konnte nicht angewendet werden',
            life: 5000
        });
    }
};
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
