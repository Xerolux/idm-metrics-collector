<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Chart konfigurieren"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Titel</label>
                <InputText
                    v-model="localChart.title"
                    class="w-full"
                    placeholder="Chart-Titel"
                />
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeitraum (Stunden)</label>
                <Select
                    v-model="localChart.hours"
                    :options="hourOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                />
            </div>

            <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-medium text-gray-700">Queries</label>
                    <div class="flex gap-1">
                        <Button
                            @click="addQuery"
                            icon="pi pi-plus"
                            size="small"
                            severity="secondary"
                            label="Query"
                        />
                        <Button
                            @click="addExpression"
                            icon="pi pi-calculator"
                            size="small"
                            severity="info"
                            label="Expression"
                        />
                    </div>
                </div>
                <div class="space-y-2">
                    <div
                        v-for="(query, index) in localChart.queries"
                        :key="index"
                        class="flex gap-2 items-center p-2 bg-gray-50 rounded"
                    >
                        <div class="flex-grow space-y-2">
                            <div class="flex gap-2">
                                <InputText
                                    v-model="query.label"
                                    placeholder="Label"
                                    class="flex-grow text-sm"
                                />
                                <Select
                                    v-model="query.type"
                                    :options="queryTypes"
                                    optionLabel="label"
                                    optionValue="value"
                                    class="w-32 text-sm"
                                />
                            </div>
                            <div v-if="query.type === 'metric'" class="flex gap-2">
                                <InputText
                                    v-model="query.query"
                                    placeholder="Metric name (z.B. temp_flow_current_circuit_A)"
                                    class="flex-grow text-sm"
                                />
                            </div>
                            <div v-else-if="query.type === 'expression'" class="flex gap-2">
                                <InputText
                                    v-model="query.expression"
                                    placeholder="Expression (z.B. A/B)"
                                    class="flex-grow text-sm font-mono"
                                    readonly
                                />
                                <Button
                                    @click="openExpressionBuilder(index)"
                                    icon="pi pi-pencil"
                                    size="small"
                                    severity="secondary"
                                    text
                                    title="Expression bearbeiten"
                                />
                            </div>
                        </div>
                        <div class="flex items-center gap-1">
                            <ColorPicker
                                v-model="query.color"
                                format="hex"
                                class="w-10"
                            />
                            <Button
                                @click="removeQuery(index)"
                                icon="pi pi-times"
                                size="small"
                                severity="danger"
                                text
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-medium text-gray-700">Alert Thresholds</label>
                    <Button
                        @click="addThreshold"
                        icon="pi pi-plus"
                        size="small"
                        severity="secondary"
                        label="Hinzufügen"
                    />
                </div>
                <div class="space-y-2">
                    <div
                        v-for="(threshold, index) in localChart.alertThresholds"
                        :key="index"
                        class="flex gap-2 items-center p-2 bg-red-50 rounded border border-red-200"
                    >
                        <div class="flex-grow space-y-2">
                            <InputText
                                v-model.number="threshold.value"
                                type="number"
                                placeholder="Wert"
                                class="w-full text-sm"
                            />
                            <InputText
                                v-model="threshold.label"
                                placeholder="Label (z.B. Kritisch)"
                                class="w-full text-sm"
                            />
                        </div>
                        <div class="flex items-center gap-1">
                            <ColorPicker
                                v-model="threshold.color"
                                format="hex"
                                class="w-10"
                            />
                            <Button
                                @click="removeThreshold(index)"
                                icon="pi pi-times"
                                size="small"
                                severity="danger"
                                text
                            />
                        </div>
                    </div>
                    <div v-if="localChart.alertThresholds.length === 0" class="text-xs text-gray-500 text-center py-2">
                        Keine Alert-Thresholds konfiguriert
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
                @click="save"
                label="Speichern"
                severity="primary"
            />
        </template>
    </Dialog>

    <ExpressionBuilder
        v-model:visible="expressionBuilderVisible"
        :currentExpression="currentExpressionIndex !== null ? localChart.queries[currentExpressionIndex]?.expression : ''"
        :availableQueries="availableQueries"
        @save="onExpressionSave"
    />
</template>

<script setup>
import { ref, computed } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Button from 'primevue/button';
import ColorPicker from 'primevue/colorpicker';
import ExpressionBuilder from './ExpressionBuilder.vue';

const props = defineProps({
    chart: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['save']);

const visible = ref(false);
const expressionBuilderVisible = ref(false);
const currentExpressionIndex = ref(null);

const localChart = ref({
    title: '',
    queries: [],
    hours: 12,
    alertThresholds: []
});

const hourOptions = [
    { label: '6 Stunden', value: 6 },
    { label: '12 Stunden', value: 12 },
    { label: '24 Stunden', value: 24 },
    { label: '48 Stunden', value: 48 },
    { label: '7 Tage', value: 168 }
];

const queryTypes = [
    { label: 'Metric', value: 'metric' },
    { label: 'Expression', value: 'expression' }
];

const colors = [
    '#f59e0b', '#3b82f6', '#ef4444', '#22c55e',
    '#a855f7', '#ec4899', '#14b8a6', '#f97316'
];

// Get available queries for expression builder
const availableQueries = computed(() => {
    return localChart.value.queries
        .filter(q => q.type === 'metric' && q.label)
        .map(q => ({
            label: q.label.toUpperCase(),
            query: q.query
        }));
});

const open = () => {
    localChart.value = JSON.parse(JSON.stringify(props.chart));

    // Ensure all queries have a type
    localChart.value.queries.forEach(q => {
        if (!q.type) {
            q.type = 'metric';
        }
    });

    visible.value = true;
};

const addQuery = () => {
    const color = colors[localChart.value.queries.length % colors.length];
    localChart.value.queries.push({
        label: `Query ${localChart.value.queries.length + 1}`,
        query: '',
        type: 'metric',
        color: color
    });
};

const addExpression = () => {
    const color = colors[localChart.value.queries.length % colors.length];
    localChart.value.queries.push({
        label: `Expression ${localChart.value.queries.length + 1}`,
        expression: '',
        type: 'expression',
        color: color
    });
};

const removeQuery = (index) => {
    localChart.value.queries.splice(index, 1);
};

const openExpressionBuilder = (index) => {
    currentExpressionIndex.value = index;
    expressionBuilderVisible.value = true;
};

const onExpressionSave = (expression) => {
    if (currentExpressionIndex.value !== null) {
        localChart.value.queries[currentExpressionIndex.value].expression = expression;
    }
    expressionBuilderVisible.value = false;
    currentExpressionIndex.value = null;
};

const addThreshold = () => {
    localChart.value.alertThresholds.push({
        value: 80,
        label: 'Warnung',
        color: '#ef4444'
    });
};

const removeThreshold = (index) => {
    localChart.value.alertThresholds.splice(index, 1);
};

const save = () => {
    emit('save', localChart.value);
    visible.value = false;
};

defineExpose({ open });
</script>
