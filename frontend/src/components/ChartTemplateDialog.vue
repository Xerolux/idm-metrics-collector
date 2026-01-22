<template>
    <Dialog
        v-model:visible="visible"
        modal
        header="Dashboard aus Vorlage erstellen"
        :style="{ width: '90vw', maxWidth: '800px' }"
    >
        <div class="space-y-4">
            <!-- Category Filter -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Kategorie</label>
                <div class="flex flex-wrap gap-2">
                    <button
                        v-for="cat in categories"
                        :key="cat.id"
                        @click="selectedCategory = cat.id"
                        :class="[
                            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                            selectedCategory === cat.id
                                ? 'bg-blue-600 text-white shadow-md'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        ]"
                    >
                        <i :class="cat.icon" class="mr-2"></i>
                        {{ cat.name }}
                    </button>
                </div>
            </div>

            <!-- Templates Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div
                    v-for="template in filteredTemplates"
                    :key="template.id"
                    @click="selectTemplate(template)"
                    :class="[
                        'p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md',
                        selectedTemplate?.id === template.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                    ]"
                >
                    <div class="flex items-start gap-3">
                        <div class="p-2 bg-blue-100 rounded-lg text-blue-600">
                            <i :class="template.icon" class="text-xl"></i>
                        </div>
                        <div class="flex-grow min-w-0">
                            <h4 class="font-semibold text-gray-900 truncate">{{ template.name }}</h4>
                            <p class="text-sm text-gray-500 mt-1">{{ template.description }}</p>
                            <div class="mt-2 text-xs text-gray-400">
                                <i class="pi pi-chart-bar mr-1"></i>
                                {{ template.charts.length }} Charts
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Selected Template Preview -->
            <div v-if="selectedTemplate" class="mt-4 pt-4 border-t border-gray-200">
                <h5 class="font-semibold text-gray-900 mb-2">Vorschau: {{ selectedTemplate.name }}</h5>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div v-for="chart in selectedTemplate.charts" :key="chart.title" class="flex items-center gap-2">
                        <i class="pi pi-chart-line text-gray-400"></i>
                        <span class="truncate">{{ chart.title }}</span>
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
                @click="applyTemplate"
                label="Erstellen"
                severity="primary"
                :disabled="!selectedTemplate"
            />
        </template>
    </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { chartTemplates, getCategories } from '../utils/chartTemplates';

const props = defineProps({
    modelValue: { type: Boolean, default: false }
});

const emit = defineEmits(['update:modelValue', 'apply']);

const visible = ref(props.modelValue);
const selectedCategory = ref('all');
const selectedTemplate = ref(null);

const categories = ref([
    { id: 'all', name: 'Alle', icon: 'pi pi-th' },
    ...getCategories()
]);

const filteredTemplates = computed(() => {
    if (selectedCategory.value === 'all') {
        return chartTemplates;
    }
    return chartTemplates.filter(t => t.category === selectedCategory.value);
});

const selectTemplate = (template) => {
    selectedTemplate.value = template;
};

const applyTemplate = () => {
    if (selectedTemplate.value) {
        emit('apply', selectedTemplate.value);
        visible.value = false;
        selectedTemplate.value = null;
    }
};

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
