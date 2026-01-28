<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Dashboard exportieren"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <!-- Export Type Selection -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Export-Typ</label>
                <div class="grid grid-cols-2 gap-3">
                    <button
                        @click="exportType = 'visual'"
                        :class="[
                            'p-3 rounded-lg border-2 text-center transition-all',
                            exportType === 'visual'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-image text-xl mb-1"></i>
                        <div class="font-medium text-sm">Visuell</div>
                        <div class="text-xs text-gray-500 mt-1">PNG / PDF Screenshot</div>
                    </button>
                    <button
                        @click="exportType = 'data'"
                        :class="[
                            'p-3 rounded-lg border-2 text-center transition-all',
                            exportType === 'data'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-database text-xl mb-1"></i>
                        <div class="font-medium text-sm">Daten</div>
                        <div class="text-xs text-gray-500 mt-1">CSV / Excel / JSON</div>
                    </button>
                </div>
            </div>

            <!-- Format Selection -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Format</label>
                <div v-if="exportType === 'visual'" class="grid grid-cols-2 gap-3">
                    <button
                        @click="selectedFormat = 'png'"
                        :class="[
                            'p-4 rounded-lg border-2 text-center transition-all',
                            selectedFormat === 'png'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-image text-2xl mb-2"></i>
                        <div class="font-medium">PNG</div>
                        <div class="text-xs text-gray-500 mt-1">Bild-Datei</div>
                    </button>
                    <button
                        @click="selectedFormat = 'pdf'"
                        :class="[
                            'p-4 rounded-lg border-2 text-center transition-all',
                            selectedFormat === 'pdf'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-file-pdf text-2xl mb-2"></i>
                        <div class="font-medium">PDF</div>
                        <div class="text-xs text-gray-500 mt-1">Dokument</div>
                    </button>
                </div>
                <div v-else class="grid grid-cols-3 gap-3">
                    <button
                        @click="selectedFormat = 'csv'"
                        :class="[
                            'p-4 rounded-lg border-2 text-center transition-all',
                            selectedFormat === 'csv'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-file text-2xl mb-2"></i>
                        <div class="font-medium">CSV</div>
                        <div class="text-xs text-gray-500 mt-1">Tabelle</div>
                    </button>
                    <button
                        @click="selectedFormat = 'excel'"
                        :class="[
                            'p-4 rounded-lg border-2 text-center transition-all',
                            selectedFormat === 'excel'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-table text-2xl mb-2"></i>
                        <div class="font-medium">Excel</div>
                        <div class="text-xs text-gray-500 mt-1">Arbeitsmappe</div>
                    </button>
                    <button
                        @click="selectedFormat = 'json'"
                        :class="[
                            'p-4 rounded-lg border-2 text-center transition-all',
                            selectedFormat === 'json'
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-200 hover:border-gray-300'
                        ]"
                    >
                        <i class="pi pi-code text-2xl mb-2"></i>
                        <div class="font-medium">JSON</div>
                        <div class="text-xs text-gray-500 mt-1">Daten</div>
                    </button>
                </div>
            </div>

            <!-- Quality Options (PNG only) -->
            <div v-if="exportType === 'visual' && selectedFormat === 'png'">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Qualität: {{ scale }}x
                </label>
                <input
                    v-model.number="scale"
                    type="range"
                    min="1"
                    max="4"
                    step="0.5"
                    class="w-full"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Klein</span>
                    <span>Standard</span>
                    <span>Hoch</span>
                </div>
            </div>

            <!-- Data Export Options -->
            <div v-if="exportType === 'data'" class="space-y-3">
                <!-- Time Range -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Zeitraum</label>
                    <select
                        v-model="timeRange"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="1h">Letzte Stunde</option>
                        <option value="6h">Letzte 6 Stunden</option>
                        <option value="12h">Letzte 12 Stunden</option>
                        <option value="24h">Letzte 24 Stunden</option>
                        <option value="7d">Letzte 7 Tage</option>
                        <option value="30d">Letzte 30 Tage</option>
                        <option value="custom">Benutzerdefiniert</option>
                    </select>
                </div>

                <!-- Custom Time Range (if selected) -->
                <div v-if="timeRange === 'custom'" class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-medium text-gray-600 mb-1">Von</label>
                        <input
                            v-model="customStartDate"
                            type="datetime-local"
                            class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
                        />
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-gray-600 mb-1">Bis</label>
                        <input
                            v-model="customEndDate"
                            type="datetime-local"
                            class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
                        />
                    </div>
                </div>

                <!-- Metrics Selection -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Metriken</label>
                    <select
                        v-model="metricsSelection"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="all">Alle Metriken</option>
                        <option value="dashboard">Nur Dashboard-Metriken</option>
                        <option value="custom">Benutzerdefiniert</option>
                    </select>
                </div>

                <!-- Custom Metrics Selection (if selected) -->
                <div v-if="metricsSelection === 'custom'">
                    <label class="block text-xs font-medium text-gray-600 mb-2">Wähle Metriken</label>
                    <div class="max-h-40 overflow-y-auto border border-gray-300 rounded p-2 space-y-1">
                        <div v-for="metric in availableMetrics" :key="metric" class="flex items-center gap-2">
                            <input
                                :id="'metric-' + metric"
                                v-model="selectedMetrics"
                                :value="metric"
                                type="checkbox"
                                class="rounded"
                            />
                            <label :for="'metric-' + metric" class="text-xs text-gray-700">{{ metric }}</label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Info -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div class="flex items-start gap-2">
                    <i class="pi pi-info-circle text-blue-600 mt-0.5"></i>
                    <div class="text-sm text-blue-800">
                        <p v-if="exportType === 'visual'">
                            <span v-if="selectedFormat === 'png'">
                                PNG eignet sich für Präsentationen und Web.
                                {{ scale === 2 ? 'Standardqualität (2x).' : scale > 2 ? 'Hohe Qualität (' + scale + 'x) - größere Datei.' : 'Niedrige Qualität - kleine Datei.' }}
                            </span>
                            <span v-else>
                                PDF eignet sich für Dokumentation und Druck.
                                Automatisch an A4 (Querformat) angepasst.
                            </span>
                        </p>
                        <p v-else>
                            <span v-if="selectedFormat === 'csv'">
                                CSV-Dateien können in Excel, Google Sheets oder jeder Analyse-Software geöffnet werden.
                            </span>
                            <span v-else-if="selectedFormat === 'excel'">
                                Excel-Dateien enthalten mehrere Sheets: Alle Daten, einzelne Metriken und Statistiken.
                            </span>
                            <span v-else-if="selectedFormat === 'json'">
                                JSON-Format für Datenaustausch und Automatisierung. Enthält Metadaten und Statistiken.
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <template #footer>
            <Button
                @click="visible = false"
                label="Abbrechen"
                severity="secondary"
                text
            />
            <Button
                @click="handleExport"
                :label="exporting ? 'Exportiere...' : 'Exportieren'"
                :icon="exporting ? 'pi pi-spinner pi-spin' : 'pi pi-download'"
                severity="primary"
                :disabled="exporting"
            />
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { exportDashboard, exportMetricsData } from '../utils/dashboardExport';
import axios from 'axios';

const props = defineProps({
    modelValue: { type: Boolean, default: false },
    dashboardName: { type: String, default: 'Dashboard' },
    dashboardElement: { type: Object, default: null },
    dashboardConfig: { type: Object, default: null }
});

const emit = defineEmits(['update:modelValue']);

const visible = ref(props.modelValue);
const exportType = ref('visual');
const selectedFormat = ref('png');
const scale = ref(2);
const exporting = ref(false);

// Data export options
const timeRange = ref('24h');
const customStartDate = ref('');
const customEndDate = ref('');
const metricsSelection = ref('all');
const selectedMetrics = ref([]);
const availableMetrics = ref([]);

// Load available metrics on mount
onMounted(async () => {
    try {
        const response = await axios.get('/api/metrics/available');
        const categories = response.data;

        // Flatten all metrics from all categories
        const metrics = [];
        for (const category of Object.values(categories)) {
            if (Array.isArray(category)) {
                metrics.push(...category);
            }
        }
        availableMetrics.value = [...new Set(metrics)]; // Remove duplicates
    } catch (error) {
        console.error('Failed to load available metrics:', error);
    }
});

// Calculate time range for data export
const getTimeRange = () => {
    const now = Math.floor(Date.now() / 1000);
    let start, end = now;

    if (timeRange.value === 'custom') {
        start = customStartDate.value ? Math.floor(new Date(customStartDate.value).getTime() / 1000) : now - 86400;
        end = customEndDate.value ? Math.floor(new Date(customEndDate.value).getTime() / 1000) : now;
    } else {
        const ranges = {
            '1h': 3600,
            '6h': 21600,
            '12h': 43200,
            '24h': 86400,
            '7d': 604800,
            '30d': 2592000
        };
        start = now - (ranges[timeRange.value] || 86400);
    }

    return { start, end };
};

// Get metrics to export
const getMetricsToExport = () => {
    if (metricsSelection.value === 'all') {
        return 'all';
    } else if (metricsSelection.value === 'dashboard' && props.dashboardConfig) {
        // Extract metrics from dashboard charts
        const metrics = new Set();
        if (props.dashboardConfig.charts) {
            props.dashboardConfig.charts.forEach(chart => {
                if (chart.queries) {
                    chart.queries.forEach(query => {
                        if (query.query) {
                            metrics.add(query.query);
                        }
                    });
                }
            });
        }
        return Array.from(metrics);
    } else if (metricsSelection.value === 'custom') {
        return selectedMetrics.value;
    }
    return 'all';
};

const handleExport = async () => {
    exporting.value = true;

    try {
        await new Promise(resolve => setTimeout(resolve, 100)); // Small delay to show spinner

        if (exportType.value === 'visual') {
            if (!props.dashboardElement) {
                console.error('No dashboard element provided');
                return;
            }

            await exportDashboard(
                props.dashboardElement,
                selectedFormat.value,
                props.dashboardName,
                {
                    scale: scale.value
                }
            );
        } else {
            // Data export
            const { start, end } = getTimeRange();
            const metrics = getMetricsToExport();

            await exportMetricsData({
                format: selectedFormat.value,
                metrics,
                start,
                end,
                step: '1m',
                dashboard_name: props.dashboardName
            });
        }

        visible.value = false;
    } catch (error) {
        console.error('Export failed:', error);
        alert('Export fehlgeschlagen: ' + error.message);
    } finally {
        exporting.value = false;
    }
};

// Reset format when export type changes
watch(exportType, (newType) => {
    if (newType === 'visual') {
        selectedFormat.value = 'png';
    } else {
        selectedFormat.value = 'csv';
    }
});

watch(() => props.modelValue, (val) => {
    visible.value = val;
});

watch(visible, (val) => {
    emit('update:modelValue', val);
});
</script>

<style scoped>
/* Add any specific styles if needed */
</style>
