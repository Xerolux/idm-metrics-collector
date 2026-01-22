<template>
    <div class="variable-selector">
        <div
            v-for="variable in variables"
            :key="variable.id"
            class="mb-3"
        >
            <label class="block text-xs font-medium text-gray-600 mb-1">
                {{ variable.name }}
            </label>
            <Select
                v-if="!variable.multi"
                v-model="selectedValues[variable.id]"
                :options="variable.values"
                optionLabel="label"
                optionValue="value"
                :placeholder="`Wähle ${variable.name}...`"
                class="w-full text-sm"
                @change="onValueChange(variable.id)"
            />
            <MultiSelect
                v-else
                v-model="selectedValues[variable.id]"
                :options="variable.values"
                optionLabel="label"
                optionValue="value"
                :placeholder="`Wähle ${variable.name}...`"
                class="w-full text-sm"
                @change="onValueChange(variable.id)"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Select from 'primevue/select';
import MultiSelect from 'primevue/multiselect';
import axios from 'axios';

// const props = defineProps({
//     dashboardId: { type: String, default: null }
// });

const emit = defineEmits(['change']);

const variables = ref([]);
const selectedValues = ref({});

const loadVariables = async () => {
    try {
        // First get all variable definitions
        const response = await axios.get('/api/variables');
        const variableDefs = response.data;

        // Then fetch values for each variable
        for (const varDef of variableDefs) {
            const valueResponse = await axios.get(`/api/variables/${varDef.id}`, {
                params: { fetch_values: true }
            });

            const varData = valueResponse.data;
            variables.value.push(varData);

            // Set default value
            if (varData.default) {
                if (varData.multi) {
                    selectedValues.value[varData.id] = varData.default.split(',');
                } else {
                    selectedValues.value[varData.id] = varData.default;
                }
            }
        }

        // Emit initial values
        emit('change', selectedValues.value);
    } catch (error) {
        console.error('Failed to load variables:', error);
    }
};

const onValueChange = () => {
    emit('change', selectedValues.value);
};

// Expose method to get current values
const getValues = () => {
    return selectedValues.value;
};

// Expose method to get flattened values (for multi-select)
const getFlattenedValues = () => {
    const result = {};
    for (const [key, value] of Object.entries(selectedValues.value)) {
        if (Array.isArray(value)) {
            result[key] = value.join(',');
        } else {
            result[key] = value;
        }
    }
    return result;
};

defineExpose({
    getValues,
    getFlattenedValues
});

onMounted(() => {
    loadVariables();
});
</script>

<style scoped>
.variable-selector {
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
}
</style>
