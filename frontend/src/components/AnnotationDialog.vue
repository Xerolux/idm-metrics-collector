<template>
    <Dialog
        v-model:visible="visible"
        modal
        :header="annotation ? 'Annotation bearbeiten' : 'Neue Annotation'"
        :style="{ width: '90vw', maxWidth: '500px' }"
    >
        <div class="space-y-4">
            <!-- Time -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Zeitpunkt</label>
                <Calendar
                    v-model="localAnnotation.time"
                    showTime
                    showSeconds
                    hourFormat="24"
                    placeholder="Datum und Uhrzeit wählen"
                    class="w-full"
                />
            </div>

            <!-- Text -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Text</label>
                <Textarea
                    v-model="localAnnotation.text"
                    rows="3"
                    placeholder="z.B. Wartung durchgeführt, Filter gewechselt..."
                    class="w-full"
                />
            </div>

            <!-- Tags -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                <Chips
                    v-model="localAnnotation.tags"
                    placeholder="Tags hinzufügen (z.B. Wartung, Fehler, Info)"
                    class="w-full"
                />
            </div>

            <!-- Color -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Farbe</label>
                <div class="flex gap-2 flex-wrap">
                    <button
                        v-for="color in presetColors"
                        :key="color"
                        @click="localAnnotation.color = color"
                        :class="[
                            'w-8 h-8 rounded-full border-2 transition-all',
                            localAnnotation.color === color
                                ? 'border-gray-900 scale-110'
                                : 'border-gray-300 hover:border-gray-400'
                        ]"
                        :style="{ backgroundColor: color }"
                        :title="color"
                    />
                </div>
            </div>

            <!-- Dashboard Scope -->
            <div>
                <div class="flex items-center gap-2">
                    <Checkbox
                        v-model="localAnnotation.isGlobal"
                        binary
                        inputId="global"
                    />
                    <label for="global" class="text-sm text-gray-700">
                        Global (alle Dashboards)
                    </label>
                </div>
                <p class="text-xs text-gray-500 mt-1 ml-6">
                    Globale Annotations werden auf allen Dashboards angezeigt
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
                @click="handleDelete"
                v-if="annotation"
                label="Löschen"
                severity="danger"
                text
            />
            <Button
                @click="handleSave"
                label="Speichern"
                severity="primary"
                :disabled="!localAnnotation.text"
            />
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Textarea from 'primevue/textarea';
import Chips from 'primevue/chips';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';

const props = defineProps({
    modelValue: { type: Boolean, default: false },
    annotation: { type: Object, default: null }, // null = new annotation
    dashboardId: { type: String, default: null }
});

const emit = defineEmits(['update:modelValue', 'saved']);

const toast = useToast();
const visible = ref(props.modelValue);
const localAnnotation = ref({
    time: null,
    text: '',
    tags: [],
    color: '#ef4444',
    isGlobal: false
});

const presetColors = [
    '#ef4444', // red
    '#f59e0b', // amber
    '#10b981', // emerald
    '#3b82f6', // blue
    '#8b5cf6', // violet
    '#ec4899', // pink
    '#6b7280', // gray
];

const resetForm = () => {
    localAnnotation.value = {
        time: new Date(),
        text: '',
        tags: [],
        color: '#ef4444',
        isGlobal: false
    };
};

const handleSave = async () => {
    try {
        // Convert time to timestamp
        const timestamp = localAnnotation.value.time
            ? Math.floor(new Date(localAnnotation.value.time).getTime() / 1000)
            : Math.floor(Date.now() / 1000);

        const data = {
            time: timestamp,
            text: localAnnotation.value.text,
            tags: localAnnotation.value.tags,
            color: localAnnotation.value.color,
            dashboard_id: localAnnotation.value.isGlobal ? null : props.dashboardId
        };

        if (props.annotation) {
            // Update existing
            await axios.put(`/api/annotations/${props.annotation.id}`, data);
        } else {
            // Create new
            await axios.post('/api/annotations', data);
        }

        emit('saved');
        visible.value = false;
        resetForm();
    } catch (error) {
        console.error('Failed to save annotation:', error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Annotation konnte nicht gespeichert werden',
            life: 5000
        });
    }
};

const handleDelete = async () => {
    try {
        await axios.delete(`/api/annotations/${props.annotation.id}`);
        emit('saved');
        visible.value = false;
        resetForm();
    } catch (error) {
        console.error('Failed to delete annotation:', error);
        toast.add({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Annotation konnte nicht gelöscht werden',
            life: 5000
        });
    }
};

watch(() => props.modelValue, (val) => {
    visible.value = val;
    if (val && props.annotation) {
        // Load existing annotation
        localAnnotation.value = {
            time: new Date(props.annotation.time * 1000),
            text: props.annotation.text,
            tags: [...props.annotation.tags],
            color: props.annotation.color,
            isGlobal: !props.annotation.dashboard_id
        };
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
