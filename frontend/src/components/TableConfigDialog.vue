<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Tabelle konfigurieren"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Titel</label>
                <InputText
                    v-model="localTable.title"
                    class="w-full"
                    placeholder="Tabellen-Titel"
                />
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeitraum (Stunden)</label>
                <Select
                    v-model="localTable.hours"
                    :options="hourOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                />
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Einträge pro Seite</label>
                <Select
                    v-model="localTable.pageSize"
                    :options="pageSizeOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                />
            </div>

            <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-medium text-gray-700">Spalten</label>
                    <Button
                        @click="addColumn"
                        icon="pi pi-plus"
                        size="small"
                        severity="secondary"
                        label="Hinzufügen"
                    />
                </div>
                <div class="space-y-2">
                    <div
                        v-for="(column, index) in localTable.columns"
                        :key="index"
                        class="flex gap-2 items-center p-2 bg-gray-50 rounded"
                    >
                        <div class="flex-grow space-y-2">
                            <InputText
                                v-model="column.label"
                                placeholder="Label"
                                class="w-full text-sm"
                            />
                            <InputText
                                v-model="column.key"
                                placeholder="Key (z.B. timestamp, value)"
                                class="w-full text-sm"
                            />
                            <Select
                                v-model="column.type"
                                :options="typeOptions"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full text-sm"
                                placeholder="Typ"
                            />
                        </div>
                        <Button
                            @click="removeColumn(index)"
                            icon="pi pi-times"
                            size="small"
                            severity="danger"
                            text
                        />
                    </div>
                </div>
            </div>

            <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-medium text-gray-700">Queries</label>
                    <Button
                        @click="addQuery"
                        icon="pi pi-plus"
                        size="small"
                        severity="secondary"
                        label="Hinzufügen"
                    />
                </div>
                <div class="space-y-2">
                    <div
                        v-for="(query, index) in localTable.queries"
                        :key="index"
                        class="flex gap-2 items-center p-2 bg-gray-50 rounded"
                    >
                        <div class="flex-grow space-y-2">
                            <InputText
                                v-model="query.label"
                                placeholder="Label"
                                class="w-full text-sm"
                            />
                            <InputText
                                v-model="query.query"
                                placeholder="Metric name"
                                class="w-full text-sm"
                            />
                        </div>
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
</template>

<script setup>
import { ref } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Button from 'primevue/button';

const props = defineProps({
    table: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['save']);

const visible = ref(false);
const localTable = ref({
    title: '',
    queries: [],
    hours: 12,
    columns: [],
    pageSize: 50
});

const hourOptions = [
    { label: '6 Stunden', value: 6 },
    { label: '12 Stunden', value: 12 },
    { label: '24 Stunden', value: 24 },
    { label: '48 Stunden', value: 48 },
    { label: '7 Tage', value: 168 }
];

const pageSizeOptions = [
    { label: '25', value: 25 },
    { label: '50', value: 50 },
    { label: '100', value: 100 },
    { label: '200', value: 200 }
];

const typeOptions = [
    { label: 'Text', value: 'text' },
    { label: 'Zahl', value: 'number' },
    { label: 'Zeitstempel', value: 'timestamp' }
];

const open = () => {
    localTable.value = JSON.parse(JSON.stringify(props.table));
    if (!localTable.value.columns) {
        localTable.value.columns = [
            { key: 'timestamp', label: 'Zeit', type: 'timestamp' }
        ];
    }
    if (!localTable.value.queries) {
        localTable.value.queries = [];
    }
    if (!localTable.value.pageSize) {
        localTable.value.pageSize = 50;
    }
    visible.value = true;
};

const addColumn = () => {
    localTable.value.columns.push({
        key: `column_${localTable.value.columns.length}`,
        label: `Spalte ${localTable.value.columns.length}`,
        type: 'text'
    });
};

const removeColumn = (index) => {
    localTable.value.columns.splice(index, 1);
};

const addQuery = () => {
    localTable.value.queries.push({
        label: `Query ${localTable.value.queries.length + 1}`,
        query: ''
    });
};

const removeQuery = (index) => {
    localTable.value.queries.splice(index, 1);
};

const save = () => {
    emit('save', localTable.value);
    visible.value = false;
};

defineExpose({ open });
</script>
