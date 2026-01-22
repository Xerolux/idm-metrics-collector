<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Manuelle Steuerung</h1>

        <div v-if="loading" class="flex justify-center items-center py-12">
            <LoadingSpinner size="xl" text="Lade Steuerungselemente..." />
        </div>

        <ErrorDisplay v-else-if="error" :error="error" @dismiss="error = null" />

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
            <Card v-for="sensor in sensors" :key="sensor.name" class="bg-gray-800 text-white">
                <template #title>
                    <div class="text-base sm:text-lg font-medium truncate" :title="sensor.name">{{ sensor.name }}</div>
                </template>
                <template #content>
                    <div class="flex flex-col gap-3">
                        <div class="text-gray-400 text-sm">{{ sensor.description }}</div>

                        <!-- EEPROM Warning -->
                        <div v-if="sensor.eeprom_sensitive" class="bg-yellow-900/50 border border-yellow-600/50 text-yellow-200 p-2 sm:p-3 rounded text-xs sm:text-sm">
                            <i class="pi pi-exclamation-triangle mr-1"></i>
                            <strong>ACHTUNG:</strong> EEPROM-sensitiv! Begrenzte Schreibzyklen
                        </div>

                        <!-- Cyclic Change Warning -->
                        <div v-if="sensor.cyclic_change_required" class="bg-info-900/50 border border-info-600/50 text-info-200 p-2 sm:p-3 rounded text-xs sm:text-sm">
                            <i class="pi pi-info-circle mr-1"></i>
                            <strong>HINWEIS:</strong> Zyklische Änderung empfohlen
                        </div>

                        <div v-if="sensor.enum" class="flex flex-col gap-2">
                            <Select v-model="formValues[sensor.name]" :options="sensor.enum" optionLabel="name" optionValue="value" placeholder="Wert wählen" class="w-full" />
                        </div>
                        <div v-else class="flex flex-col gap-2">
                             <InputText v-model="formValues[sensor.name]" type="text" placeholder="Wert" />
                             <small v-if="sensor.min !== null || sensor.max !== null" class="text-gray-500">
                                Bereich: {{ sensor.min ?? '-∞' }} bis {{ sensor.max ?? '+∞' }}
                             </small>
                        </div>

                        <Button label="Schreiben" icon="pi pi-send" @click="writeSensor(sensor)" :loading="writing[sensor.name]" />
                    </div>
                </template>
            </Card>
        </div>
        <Toast />
        <ConfirmDialog group="eeprom" class="eeprom-confirm-dialog" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import ErrorDisplay from '../components/ErrorDisplay.vue';

const sensors = ref([]);
const formValues = ref({});
const loading = ref(true);
const error = ref(null);
const writing = ref({});
const toast = useToast();
const confirm = useConfirm();

onMounted(async () => {
    try {
        const res = await axios.get('/api/control');
        sensors.value = res.data;
        // Initialize form values
        try {
            const dataRes = await axios.get('/api/data');
             sensors.value.forEach(s => {
                formValues.value[s.name] = dataRes.data[s.name];
            });
        } catch {
            // ignore
        }

    } catch (e) {
        error.value = e.response?.data?.error || e.message;
    } finally {
        loading.value = false;
    }
});

const executeWrite = async (sensor, value) => {
    writing.value[sensor.name] = true;
    try {
        const res = await axios.post('/api/control', {
            sensor: sensor.name,
            value: value
        });
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
    } finally {
        writing.value[sensor.name] = false;
    }
};

const writeSensor = (sensor) => {
    const value = formValues.value[sensor.name];
    if (value === undefined || value === null) return;

    // Extra confirmation for EEPROM-sensitive registers
    if (sensor.eeprom_sensitive) {
        confirm.require({
            group: 'eeprom',
            message: `Register: ${sensor.name}\nNeuer Wert: ${value}\n\nDieses Register hat begrenzte Schreibzyklen. Häufiges Schreiben kann die Hardware beschädigen.`,
            header: 'EEPROM Warnung',
            icon: 'pi pi-exclamation-triangle',
            rejectProps: {
                label: 'Abbrechen',
                severity: 'secondary',
                outlined: true
            },
            acceptProps: {
                label: 'Fortfahren',
                severity: 'danger'
            },
            accept: () => {
                executeWrite(sensor, value);
            },
            reject: () => {
                // do nothing
            }
        });
    } else {
        executeWrite(sensor, value);
    }
};
</script>

<style>
/* Global styles for the confirmation dialog to handle teleportation */
.eeprom-confirm-dialog .p-dialog-message {
    white-space: pre-line;
}

/* Dark mode overrides for this specific dialog */
.eeprom-confirm-dialog .p-dialog-header,
.eeprom-confirm-dialog .p-dialog-content,
.eeprom-confirm-dialog .p-dialog-footer {
    background-color: #1f2937 !important; /* gray-800 */
    color: white !important;
    border-color: #374151; /* gray-700 */
}

.eeprom-confirm-dialog .p-dialog-header-icon {
    color: #9ca3af !important; /* gray-400 */
}
.eeprom-confirm-dialog .p-dialog-header-icon:hover {
    color: white !important;
}
</style>
