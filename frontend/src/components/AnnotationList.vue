<template>
    <div class="space-y-2">
        <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold">Annotations</h3>
            <Button
                @click="showAddDialog = true"
                icon="pi pi-plus"
                size="small"
                severity="primary"
                label="Neu"
            />
        </div>

        <div
            v-if="annotations.length === 0"
            class="text-center py-8 text-gray-500 text-sm"
        >
            Keine Annotations vorhanden
        </div>

        <div
            v-for="annotation in sortedAnnotations"
            :key="annotation.id"
            class="flex items-start gap-3 p-3 bg-white rounded-lg border border-gray-200 hover:shadow-sm transition-shadow"
        >
            <!-- Color bar -->
            <div
                class="w-1 rounded-full flex-shrink-0"
                :style="{ backgroundColor: annotation.color }"
            ></div>

            <!-- Content -->
            <div class="flex-grow min-w-0">
                <div class="flex items-start justify-between gap-2">
                    <p class="text-sm text-gray-900">{{ annotation.text }}</p>
                    <div class="flex items-center gap-1 flex-shrink-0">
                        <Button
                            @click="editAnnotation(annotation)"
                            icon="pi pi-pencil"
                            size="small"
                            text
                            severity="secondary"
                            class="p-1"
                        />
                        <Button
                            @click="confirmDelete(annotation)"
                            icon="pi pi-times"
                            size="small"
                            text
                            severity="danger"
                            class="p-1"
                        />
                    </div>
                </div>

                <div class="flex items-center gap-2 mt-1">
                    <span class="text-xs text-gray-500">
                        {{ formatDate(annotation.time) }}
                    </span>
                    <span
                        v-for="tag in annotation.tags"
                        :key="tag"
                        class="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs"
                    >
                        {{ tag }}
                    </span>
                    <span
                        v-if="!annotation.dashboard_id"
                        class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs"
                    >
                        Global
                    </span>
                </div>
            </div>
        </div>

        <!-- Add/Edit Dialog -->
        <AnnotationDialog
            v-model="showAddDialog"
            :annotation="editingAnnotation"
            :dashboard-id="dashboardId"
            @saved="loadAnnotations"
        />

        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Button from 'primevue/button';
import AnnotationDialog from './AnnotationDialog.vue';
import ConfirmDialog from 'primevue/confirmdialog';
import { useConfirm } from 'primevue/useconfirm';
import axios from 'axios';

const props = defineProps({
    dashboardId: { type: String, required: true },
    startTime: { type: Number, default: null },
    endTime: { type: Number, default: null }
});

const confirm = useConfirm();

const annotations = ref([]);
const showAddDialog = ref(false);
const editingAnnotation = ref(null);

const sortedAnnotations = computed(() => {
    return [...annotations.value].sort((a, b) => b.time - a.time);
});

const loadAnnotations = async () => {
    try {
        const params = {};
        if (props.dashboardId) {
            params.dashboard_id = props.dashboardId;
        }
        if (props.startTime && props.endTime) {
            params.start = props.startTime;
            params.end = props.endTime;
        }

        const response = await axios.get('/api/annotations', { params });
        annotations.value = response.data;
    } catch (error) {
        console.error('Failed to load annotations:', error);
    }
};

const editAnnotation = (annotation) => {
    editingAnnotation.value = annotation;
    showAddDialog.value = true;
};

const confirmDelete = (annotation) => {
    confirm.require({
        message: `Annotation "${annotation.text}" wirklich löschen?`,
        header: 'Löschen bestätigen',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Ja',
        rejectLabel: 'Nein',
        accept: async () => {
            try {
                await axios.delete(`/api/annotations/${annotation.id}`);
                await loadAnnotations();
            } catch (error) {
                console.error('Failed to delete annotation:', error);
            }
        }
    });
};

const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

onMounted(() => {
    loadAnnotations();
});
</script>
