<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Balkendiagramm konfigurieren"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Titel</label>
                <InputText
                    v-model="localBar.title"
                    class="w-full"
                    placeholder="Titel"
                />
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeitraum (Stunden)</label>
                <Select
                    v-model="localBar.hours"
                    :options="hourOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                />
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Anzeigemodus</label>
                    <Select
                        v-model="localBar.barMode"
                        :options="barModeOptions"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Aggregation</label>
                    <Select
                        v-model="localBar.aggregation"
                        :options="aggregationOptions"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full"
                    />
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
                        v-for="(query, index) in localBar.queries"
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
import ColorPicker from 'primevue/colorpicker';

const props = defineProps({
    bar: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['save']);

const visible = ref(false);
const localBar = ref({
    title: '',
    queries: [],
    hours: 12,
    barMode: 'grouped',
    aggregation: 'avg'
});

const hourOptions = [
    { label: '6 Stunden', value: 6 },
    { label: '12 Stunden', value: 12 },
    { label: '24 Stunden', value: 24 },
    { label: '48 Stunden', value: 48 },
    { label: '7 Tage', value: 168 }
];

const barModeOptions = [
    { label: 'Gruppiert', value: 'grouped' },
    { label: 'Gestapelt', value: 'stacked' },
    { label: 'Horizontal', value: 'horizontal' }
];

const aggregationOptions = [
    { label: 'Durchschnitt', value: 'avg' },
    { label: 'Summe', value: 'sum' },
    { label: 'Minimum', value: 'min' },
    { label: 'Maximum', value: 'max' }
];

const colors = [
    '#f59e0b', '#3b82f6', '#ef4444', '#22c55e',
    '#a855f7', '#ec4899', '#14b8a6', '#f97316'
];

const open = () => {
    localBar.value = JSON.parse(JSON.stringify(props.bar));
    visible.value = true;
};

const addQuery = () => {
    const color = colors[localBar.value.queries.length % colors.length];
    localBar.value.queries.push({
        label: `Query ${localBar.value.queries.length + 1}`,
        query: '',
        color: color
    });
};

const removeQuery = (index) => {
    localBar.value.queries.splice(index, 1);
};

const save = () => {
    emit('save', localBar.value);
    visible.value = false;
};

defineExpose({ open });
</script>
