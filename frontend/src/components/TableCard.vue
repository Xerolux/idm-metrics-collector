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
                <span class="text-xs text-gray-500">Tabelle - letzte {{ displayHours }}</span>
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
            ref="tableContainer"
            class="flex-grow flex flex-col w-full min-h-0 overflow-hidden"
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

            <!-- Controls -->
            <div class="flex items-center gap-2 mb-2 flex-shrink-0">
                <InputText
                    v-model="filterText"
                    placeholder="Filtern..."
                    class="text-sm w-48"
                />
                <Select
                    v-model="sortBy"
                    :options="sortOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="text-sm w-40"
                    placeholder="Sortieren"
                />
                <Button
                    @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
                    :icon="sortOrder === 'asc' ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down'"
                    size="small"
                    severity="secondary"
                    text
                />
            </div>

            <!-- Table -->
            <div class="flex-grow overflow-auto border rounded">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 sticky top-0">
                        <tr>
                            <th
                                v-for="column in columns"
                                :key="column.key"
                                @click="sortBy = column.key"
                                class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                            >
                                {{ column.label }}
                                <i v-if="sortBy === column.key" class="ml-1"
                                   :class="sortOrder === 'asc' ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down'" />
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <tr
                            v-for="(row, index) in paginatedRows"
                            :key="index"
                            class="hover:bg-gray-50"
                        >
                            <td
                                v-for="column in columns"
                                :key="column.key"
                                class="px-3 py-2 whitespace-nowrap"
                            >
                                <span v-if="column.type === 'timestamp'">
                                    {{ formatTimestamp(row[column.key]) }}
                                </span>
                                <span v-else-if="column.type === 'number'">
                                    {{ formatNumber(row[column.key]) }}
                                </span>
                                <span v-else>
                                    {{ row[column.key] }}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="flex items-center justify-between mt-2 flex-shrink-0">
                <div class="text-xs text-gray-500">
                    Zeige {{ startIndex + 1 }}-{{ Math.min(endIndex, filteredRows.length) }} von {{ filteredRows.length }} Einträgen
                </div>
                <div class="flex items-center gap-1">
                    <Button
                        @click="currentPage--"
                        :disabled="currentPage === 1"
                        icon="pi pi-chevron-left"
                        size="small"
                        severity="secondary"
                        text
                    />
                    <span class="text-xs text-gray-600 px-2">{{ currentPage }} / {{ totalPages }}</span>
                    <Button
                        @click="currentPage++"
                        :disabled="currentPage === totalPages"
                        icon="pi pi-chevron-right"
                        size="small"
                        severity="secondary"
                        text
                    />
                </div>
            </div>
        </div>

        <TableConfigDialog
            ref="configDialog"
            :table="tableConfig"
            @save="onConfigSave"
        />

        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import TableConfigDialog from './TableConfigDialog.vue';
import ConfirmDialog from 'primevue/confirmdialog';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Button from 'primevue/button';

const props = defineProps({
    title: { type: String, required: true },
    queries: { type: Array, required: true },
    hours: { type: [Number, String], default: 12 },
    chartId: { type: String, required: true },
    dashboardId: { type: String, required: true },
    editMode: { type: Boolean, default: false },
    columns: { type: Array, default: () => [] }, // [{key, label, type}]
    pageSize: { type: Number, default: 50 }
});

const emit = defineEmits(['deleted', 'save']);

const confirm = useConfirm();
const toast = useToast();

const isFullscreen = ref(false);
const tableContainer = ref(null);
const configDialog = ref(null);
const tableData = ref([]);

const filterText = ref('');
const sortBy = ref('timestamp');
const sortOrder = ref('desc');
const currentPage = ref(1);

const tableConfig = computed(() => ({
    title: props.title,
    queries: props.queries,
    hours: props.hours,
    columns: props.columns
}));

const displayHours = computed(() => {
    if (props.hours === 0 || props.hours === '0') return 'Start';
    return props.hours + ' Stunden';
});

const sortOptions = computed(() => {
    return props.columns.map(col => ({
        label: col.label,
        value: col.key
    }));
});

const filteredRows = computed(() => {
    if (!filterText.value) {
        return tableData.value;
    }

    const filter = filterText.value.toLowerCase();
    return tableData.value.filter(row => {
        return Object.values(row).some(val =>
            String(val).toLowerCase().includes(filter)
        );
    });
});

const sortedRows = computed(() => {
    const rows = [...filteredRows.value];

    rows.sort((a, b) => {
        const aVal = a[sortBy.value];
        const bVal = b[sortBy.value];

        if (sortOrder.value === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    return rows;
});

const totalPages = computed(() => {
    return Math.ceil(sortedRows.value.length / props.pageSize);
});

const startIndex = computed(() => {
    return (currentPage.value - 1) * props.pageSize;
});

const endIndex = computed(() => {
    return startIndex.value + props.pageSize;
});

const paginatedRows = computed(() => {
    return sortedRows.value.slice(startIndex.value, endIndex.value);
});

const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

const formatNumber = (num) => {
    if (num === null || num === undefined) return '-';
    if (typeof num === 'number') {
        return num.toFixed(2);
    }
    return num;
};

const fetchData = async () => {
    try {
        const end = Math.floor(Date.now() / 1000);
        const start = props.hours === 0 || props.hours === '0' ? end - 86400 * 7 : end - (props.hours * 3600);

        const allData = [];

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
                // Convert to table rows
                data.values.forEach(([timestamp, value]) => {
                    allData.push({
                        timestamp: timestamp,
                        [query.label || query.query]: value
                    });
                });
            }
        }

        tableData.value = allData;
    } catch (error) {
        console.error('Failed to fetch table data:', error);
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
};

const openConfig = () => {
    configDialog.value.open();
};

const confirmDelete = () => {
    confirm.require({
        message: 'Möchtest du diese Tabelle wirklich löschen?',
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

watch(() => [props.queries, props.hours], () => {
    fetchData();
}, { deep: true });

watch(currentPage, () => {
    // Reset to top when page changes
    if (tableContainer.value) {
        tableContainer.value.scrollTop = 0;
    }
});

onMounted(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);

    return () => clearInterval(interval);
});
</script>
