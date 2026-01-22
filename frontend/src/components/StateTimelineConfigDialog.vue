<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Status-Timeline konfigurieren"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Titel</label>
                <InputText
                    v-model="localTimeline.title"
                    class="w-full"
                    placeholder="Timeline-Titel"
                />
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeitraum (Stunden)</label>
                <Select
                    v-model="localTimeline.hours"
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
                        v-model="localTimeline.query.label"
                        placeholder="Label"
                        class="w-full text-sm mb-2"
                    />
                    <InputText
                        v-model="localTimeline.query.query"
                        placeholder="Metric name (z.B. idm_heatpump_operation_state)"
                        class="w-full text-sm"
                    />
                </div>
            </div>

            <div>
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-sm font-medium text-gray-700">Status-Farben</label>
                    <Button
                        @click="addStateColor"
                        icon="pi pi-plus"
                        size="small"
                        severity="secondary"
                        label="Hinzufügen"
                    />
                </div>
                <div class="space-y-2">
                    <div
                        v-for="(color, index) in Object.keys(localTimeline.stateColors)"
                        :key="index"
                        class="flex items-center gap-2 p-2 bg-gray-50 rounded"
                    >
                        <InputText
                            v-model="tempStates[index]"
                            placeholder="Status (z.B. An, Aus)"
                            class="flex-grow text-sm"
                        />
                        <ColorPicker
                            v-model="localTimeline.stateColors[color]"
                            format="hex"
                            class="w-10"
                        />
                        <Button
                            @click="removeStateColor(color)"
                            icon="pi pi-times"
                            size="small"
                            severity="danger"
                            text
                        />
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                    Definieren Sie hier die Zustände und ihre Farben
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
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Button from 'primevue/button';
import ColorPicker from 'primevue/colorpicker';

const props = defineProps({
    timeline: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['save']);

const visible = ref(false);
const localTimeline = ref({
    title: '',
    query: { label: '', query: '' },
    hours: 12,
    stateColors: {}
});

const tempStates = ref([]);

const hourOptions = [
    { label: '6 Stunden', value: 6 },
    { label: '12 Stunden', value: 12 },
    { label: '24 Stunden', value: 24 },
    { label: '48 Stunden', value: 48 },
    { label: '7 Tage', value: 168 }
];

const open = () => {
    localTimeline.value = JSON.parse(JSON.stringify(props.timeline));

    // Convert stateColors object to array
    tempStates.value = Object.keys(localTimeline.value.stateColors || {});

    if (!localTimeline.value.stateColors) {
        localTimeline.value.stateColors = {
            'An': '#22c55e',
            'Aus': '#ef4444'
        };
        tempStates.value = ['An', 'Aus'];
    }

    visible.value = true;
};

const addStateColor = () => {
    const newState = `State_${Object.keys(localTimeline.value.stateColors).length + 1}`;
    localTimeline.value.stateColors[newState] = '#6b7280';
    tempStates.value = Object.keys(localTimeline.value.stateColors);
};

const removeStateColor = (state) => {
    delete localTimeline.value.stateColors[state];
    tempStates.value = Object.keys(localTimeline.value.stateColors);
};

const save = () => {
    emit('save', localTimeline.value);
    visible.value = false;
};

watch(() => props.timeline, () => {
    // Rebuild tempStates when stateColors changes
    tempStates.value = Object.keys(localTimeline.value.stateColors || {});
});

watch(tempStates, (newStates) => {
    // Keep stateColors in sync
    const newColors = {};
    newStates.forEach(state => {
        if (props.timeline.stateColors[state]) {
            newColors[state] = props.timeline.stateColors[state];
        } else {
            newColors[state] = localTimeline.value.stateColors[state] || '#6b7280';
        }
    });
    localTimeline.value.stateColors = newColors;
});

defineExpose({ open });
</script>
