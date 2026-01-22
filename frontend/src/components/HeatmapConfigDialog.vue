<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Heatmap konfigurieren"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Titel</label>
                <InputText
                    v-model="localHeatmap.title"
                    class="w-full"
                    placeholder="Heatmap-Titel"
                />
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeitraum (Stunden)</label>
                <Select
                    v-model="localHeatmap.hours"
                    :options="hourOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                />
            </div>

            <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-medium text-gray-700">Query</label>
                </div>
                <div class="p-2 bg-gray-50 rounded">
                    <InputText
                        v-model="localHeatmap.query.label"
                        placeholder="Label"
                        class="w-full text-sm mb-2"
                    />
                    <InputText
                        v-model="localHeatmap.query.query"
                        placeholder="Metric name"
                        class="w-full text-sm"
                    />
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeit-Buckets</label>
                <Select
                    v-model="localHeatmap.buckets"
                    :options="bucketOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Anzahl der Zeitabschnitte auf der X-Achse
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Farbskala</label>
                <div class="space-y-3">
                    <div class="flex items-center gap-2">
                        <span class="text-sm text-gray-600 w-16">Min:</span>
                        <ColorPicker
                            v-model="localHeatmap.colorScale.min"
                            format="hex"
                            class="w-10"
                        />
                        <InputText
                            v-model="localHeatmap.colorScale.min"
                            class="flex-grow text-sm"
                        />
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-sm text-gray-600 w-16">Mitte:</span>
                        <ColorPicker
                            v-model="localHeatmap.colorScale.mid"
                            format="hex"
                            class="w-10"
                        />
                        <InputText
                            v-model="localHeatmap.colorScale.mid"
                            class="flex-grow text-sm"
                        />
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-sm text-gray-600 w-16">Max:</span>
                        <ColorPicker
                            v-model="localHeatmap.colorScale.max"
                            format="hex"
                            class="w-10"
                        />
                        <InputText
                            v-model="localHeatmap.colorScale.max"
                            class="flex-grow text-sm"
                        />
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                    Farbverlauf von niedrigen zu hohen Werten
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Wertebereich (Optional)</label>
                <div class="flex gap-2 items-center">
                    <InputText
                        v-model.number="localHeatmap.valueRange[0]"
                        type="number"
                        placeholder="Auto"
                        class="w-full text-sm"
                    />
                    <span class="text-gray-500">bis</span>
                    <InputText
                        v-model.number="localHeatmap.valueRange[1]"
                        type="number"
                        placeholder="Auto"
                        class="w-full text-sm"
                    />
                </div>
                <p class="text-xs text-gray-500 mt-1">
                    Leer lassen für automatische Bereichserkennung
                </p>
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
    heatmap: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['save']);

const visible = ref(false);
const localHeatmap = ref({
    title: '',
    query: { label: '', query: '' },
    hours: 12,
    colorScale: {
        min: '#3b82f6',
        mid: '#fbbf24',
        max: '#ef4444'
    },
    buckets: 24,
    valueRange: [null, null]
});

const hourOptions = [
    { label: '6 Stunden', value: 6 },
    { label: '12 Stunden', value: 12 },
    { label: '24 Stunden', value: 24 },
    { label: '48 Stunden', value: 48 },
    { label: '7 Tage', value: 168 }
];

const bucketOptions = [
    { label: '12 Buckets', value: 12 },
    { label: '24 Buckets (Stunden)', value: 24 },
    { label: '48 Buckets', value: 48 },
    { label: '96 Buckets', value: 96 }
];

const open = () => {
    localHeatmap.value = JSON.parse(JSON.stringify(props.heatmap));

    // Ensure defaults
    if (!localHeatmap.value.colorScale) {
        localHeatmap.value.colorScale = {
            min: '#3b82f6',
            mid: '#fbbf24',
            max: '#ef4444'
        };
    }
    if (!localHeatmap.value.buckets) {
        localHeatmap.value.buckets = 24;
    }
    if (!localHeatmap.value.valueRange) {
        localHeatmap.value.valueRange = [null, null];
    }

    visible.value = true;
};

const save = () => {
    emit('save', localHeatmap.value);
    visible.value = false;
};

defineExpose({ open });
</script>
