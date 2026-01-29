<template>
    <Dialog
        v-model:visible="visible"
        modal
        :header="variable ? 'Variable bearbeiten' : 'Neue Variable'"
        :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <div class="space-y-4">
            <!-- Variable ID -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Variable ID *
                </label>
                <InputText
                    v-model="localVariable.id"
                    placeholder="z.B. circuit, period, sensor_id"
                    :disabled="!!variable"
                    class="w-full"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Wird in Queries als ${{ '{variable_id}' }} oder ${{ '{variable_id}' }} verwendet
                </p>
            </div>

            <!-- Name -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Name *
                </label>
                <InputText
                    v-model="localVariable.name"
                    placeholder="z.B. Heizkreis, Zeitraum, Sensor"
                    class="w-full"
                />
            </div>

            <!-- Type -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Typ *
                </label>
                <Select
                    v-model="localVariable.type"
                    :options="typeOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                    @change="onTypeChange"
                />
            </div>

            <!-- Query (for type=query) -->
            <div v-if="localVariable.type === 'query'">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Query
                </label>
                <Textarea
                    v-model="localVariable.query"
                    placeholder="z.B. query_result{circuit='A'}"
                    rows="3"
                    class="w-full"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Metric query to fetch possible values
                </p>
            </div>

            <!-- Values (for type=custom) -->
            <div v-if="localVariable.type === 'custom'">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Werte
                </label>
                <Chips
                    v-model="localVariable.values"
                    placeholder="Werte hinzufügen"
                    class="w-full"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Vordefinierte Werte für das Select
                </p>
            </div>

            <!-- Default Value -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Standardwert
                </label>
                <InputText
                    v-model="localVariable.default"
                    placeholder="Standardwert"
                    class="w-full"
                />
            </div>

            <!-- Options -->
            <div class="space-y-2">
                <div class="flex items-center gap-2">
                    <Checkbox
                        v-model="localVariable.multi"
                        binary
                        inputId="multi"
                    />
                    <label for="multi" class="text-sm text-gray-700">
                        Mehrfachauswahl erlauben
                    </label>
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
                @click="handleDelete"
                v-if="variable"
                label="Löschen"
                severity="danger"
                text
            />
            <Button
                @click="handleSave"
                label="Speichern"
                severity="primary"
                :disabled="!localVariable.id || !localVariable.name || !localVariable.type"
            />
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Select from 'primevue/select';
import Chips from 'primevue/chips';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';

const props = defineProps({
    modelValue: { type: Boolean, default: false },
    variable: { type: Object, default: null }
});

const emit = defineEmits(['update:modelValue', 'saved']);

const toast = useToast();
const visible = ref(props.modelValue);
const localVariable = ref({
    id: '',
    name: '',
    type: 'custom',
    query: '',
    values: [],
    default: '',
    multi: false
});

const typeOptions = [
    { label: 'Benutzerdefiniert', value: 'custom' },
    { label: 'Query', value: 'query' },
    { label: 'Intervall', value: 'interval' }
];

const resetForm = () => {
    localVariable.value = {
        id: '',
        name: '',
        type: 'custom',
        query: '',
        values: [],
        default: '',
        multi: false
    };
};

const onTypeChange = () => {
    // Reset type-specific fields
    if (localVariable.value.type !== 'query') {
        localVariable.value.query = '';
    }
    if (localVariable.value.type !== 'custom') {
        localVariable.value.values = [];
    }
};

const handleSave = async () => {
    try {
        const data = {
            id: localVariable.value.id,
            name: localVariable.value.name,
            type: localVariable.value.type,
            query: localVariable.value.query || undefined,
            values: localVariable.value.values || undefined,
            default: localVariable.value.default || undefined,
            multi: localVariable.value.multi
        };

        if (props.variable) {
            // Update existing
            await axios.put(`/api/variables/${props.variable.id}`, data);
        } else {
            // Create new
            await axios.post('/api/variables', data);
        }

        emit('saved');
        visible.value = false;
        resetForm();
    } catch (error) {
        console.error('Failed to save variable:', error);
        const errorMsg = error.response?.data?.error || 'Variable konnte nicht gespeichert werden';
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: errorMsg,
            life: 5000
        });
    }
};

const handleDelete = async () => {
    try {
        await axios.delete(`/api/variables/${props.variable.id}`);
        emit('saved');
        visible.value = false;
        resetForm();
    } catch (error) {
        console.error('Failed to delete variable:', error);
        const errorMsg = error.response?.data?.error || 'Variable konnte nicht gelöscht werden';
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: errorMsg,
            life: 5000
        });
    }
};

watch(() => props.modelValue, (val) => {
    visible.value = val;
    if (val && props.variable) {
        // Load existing variable
        localVariable.value = { ...props.variable };
    } else if (val) {
        resetForm();
    }
});

watch(visible, (val) => {
    emit('update:modelValue', val);
    if (!val) {
        resetForm();
    }
});
</script>
