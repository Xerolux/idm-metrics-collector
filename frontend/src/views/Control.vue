<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Manual Control</h1>

        <div v-if="loading" class="flex justify-center">
            <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else-if="error" class="text-red-500">
            {{ error }}
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card v-for="sensor in sensors" :key="sensor.name" class="bg-gray-800 text-white">
                <template #title>
                    <div class="text-lg truncate" :title="sensor.name">{{ sensor.name }}</div>
                </template>
                <template #content>
                    <div class="flex flex-col gap-3">
                        <div class="text-gray-400 text-sm">{{ sensor.description }}</div>

                        <!-- EEPROM Warning -->
                        <div v-if="sensor.eeprom_sensitive" class="bg-yellow-900 border border-yellow-600 text-yellow-200 p-2 rounded text-xs">
                            <i class="pi pi-exclamation-triangle mr-1"></i>
                            <strong>ACHTUNG:</strong> EEPROM-sensitiv! Begrenzte Schreibzyklen - nicht häufig schreiben!
                        </div>

                        <!-- Cyclic Change Warning -->
                        <div v-if="sensor.cyclic_change_required" class="bg-blue-900 border border-blue-600 text-blue-200 p-2 rounded text-xs">
                            <i class="pi pi-info-circle mr-1"></i>
                            <strong>HINWEIS:</strong> Wert sollte zyklisch geändert werden (z.B. alle 10 Minuten)
                        </div>

                        <div v-if="sensor.enum" class="flex flex-col gap-2">
                            <Dropdown v-model="formValues[sensor.name]" :options="sensor.enum" optionLabel="name" optionValue="value" placeholder="Select Value" class="w-full" />
                        </div>
                        <div v-else class="flex flex-col gap-2">
                             <InputText v-model="formValues[sensor.name]" type="text" placeholder="Value" />
                             <small v-if="sensor.min !== null || sensor.max !== null" class="text-gray-500">
                                Range: {{ sensor.min ?? '-∞' }} to {{ sensor.max ?? '+∞' }}
                             </small>
                        </div>

                        <Button label="Write" icon="pi pi-send" @click="writeSensor(sensor)" :loading="writing[sensor.name]" />
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
import Dropdown from 'primevue/dropdown';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

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
        } catch(e) {}

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
            toast.add({ severity: 'success', summary: 'Success', detail: res.data.message, life: 3000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || e.message, life: 5000 });
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
            message: `Register: ${sensor.name}\nNew Value: ${value}\n\nThis register has limited write cycles. Frequent writing may damage the hardware.`,
            header: 'EEPROM Warning',
            icon: 'pi pi-exclamation-triangle',
            rejectProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptProps: {
                label: 'Proceed',
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
