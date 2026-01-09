<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Configuration</h1>

        <div v-if="loading" class="flex justify-center">
            <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card class="bg-gray-800 text-white">
                <template #title>IDM Heat Pump</template>
                <template #content>
                    <div class="flex flex-col gap-4">
                        <div class="flex flex-col gap-2">
                            <label>Host / IP</label>
                            <InputText v-model="config.idm.host" />
                        </div>
                        <div class="flex flex-col gap-2">
                            <label>Port</label>
                            <InputNumber v-model="config.idm.port" :useGrouping="false" />
                        </div>
                    </div>
                </template>
            </Card>

            <Card class="bg-gray-800 text-white">
                <template #title>InfluxDB</template>
                <template #content>
                    <div class="flex flex-col gap-4">
                         <div class="flex flex-col gap-2">
                            <label>URL</label>
                            <InputText v-model="config.influx.url" />
                        </div>
                        <div class="flex flex-col gap-2">
                            <label>Organization</label>
                            <InputText v-model="config.influx.org" />
                        </div>
                         <div class="flex flex-col gap-2">
                            <label>Bucket</label>
                            <InputText v-model="config.influx.bucket" />
                        </div>
                    </div>
                </template>
            </Card>

            <Card class="bg-gray-800 text-white">
                <template #title>Web Interface</template>
                <template #content>
                     <div class="flex flex-col gap-4">
                         <div class="flex items-center gap-2">
                             <Checkbox v-model="config.web.write_enabled" binary inputId="write_enabled" />
                             <label for="write_enabled">Enable Write Access (Manual Control & Schedule)</label>
                         </div>
                     </div>
                </template>
            </Card>

            <Card class="bg-gray-800 text-white">
                <template #title>Admin Security</template>
                <template #content>
                    <div class="flex flex-col gap-4">
                        <div class="flex flex-col gap-2">
                             <label>New Password</label>
                             <InputText v-model="newPassword" type="password" />
                        </div>
                    </div>
                </template>
            </Card>
        </div>

        <div class="flex gap-4 mt-4">
            <Button label="Save Configuration" icon="pi pi-save" @click="saveConfig" :loading="saving" />
            <Button label="Restart Service" icon="pi pi-refresh" severity="danger" @click="confirmRestart" />
        </div>

        <Toast />
        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

const config = ref({
    idm: { host: '', port: 502 },
    influx: { url: '', org: '', bucket: '' },
    web: { write_enabled: false }
});
const newPassword = ref('');
const loading = ref(true);
const saving = ref(false);
const toast = useToast();
const confirm = useConfirm();

onMounted(async () => {
    try {
        const res = await axios.get('/api/config');
        config.value = res.data;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load config', life: 3000 });
    } finally {
        loading.value = false;
    }
});

const saveConfig = async () => {
    saving.value = true;
    try {
        const payload = {
            idm_host: config.value.idm.host,
            idm_port: config.value.idm.port,
            influx_url: config.value.influx.url,
            write_enabled: config.value.web.write_enabled,
            new_password: newPassword.value || undefined
        };
        const res = await axios.post('/api/config', payload);
        toast.add({ severity: 'success', summary: 'Success', detail: res.data.message, life: 3000 });
        newPassword.value = '';
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || e.message, life: 5000 });
    } finally {
        saving.value = false;
    }
};

const confirmRestart = () => {
    confirm.require({
        message: 'Are you sure you want to restart the service?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: async () => {
            try {
                const res = await axios.post('/api/restart');
                toast.add({ severity: 'info', summary: 'Restarting', detail: res.data.message, life: 3000 });
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to restart', life: 3000 });
            }
        }
    });
};
</script>
