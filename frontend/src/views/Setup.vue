<template>
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-900 p-4">
        <Card class="w-full max-w-2xl bg-gray-800 border-gray-700 text-white mb-auto mt-auto">
            <template #title>Ersteinrichtung</template>
            <template #content>
                <div class="flex flex-col gap-6">
                    <Message severity="info" :closable="false">Willkommen beim IDM Logger. Bitte konfiguriere die Grundeinstellungen.</Message>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex flex-col gap-2">
                             <label class="font-bold text-blue-400">IDM Wärmepumpe</label>
                             <div class="flex flex-col gap-2">
                                <label>Host IP</label>
                                <InputText v-model="form.idm_host" placeholder="192.168.x.x" />
                            </div>
                            <div class="flex flex-col gap-2">
                                <label>Modbus Port</label>
                                <InputNumber v-model="form.idm_port" :useGrouping="false" />
                            </div>

                            <div class="flex flex-col gap-2">
                                <label class="font-bold">Aktivierte Features</label>
                                <div class="flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="form.circuits" inputId="circuitA" value="A" disabled />
                                        <label for="circuitA" class="opacity-50">Heizkreis A (Immer aktiv)</label>
                                    </div>
                                    <div class="flex flex-wrap gap-4">
                                        <div v-for="c in ['B', 'C', 'D', 'E', 'F', 'G']" :key="c" class="flex items-center gap-2">
                                            <Checkbox v-model="form.circuits" :inputId="'circuit'+c" :value="c" />
                                            <label :for="'circuit'+c">Heizkreis {{ c }}</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50">
                                    <label class="text-sm text-gray-400">Zonenmodule</label>
                                    <div class="flex flex-wrap gap-4">
                                        <div v-for="z in 10" :key="z" class="flex items-center gap-2">
                                            <Checkbox v-model="form.zones" :inputId="'zone'+(z-1)" :value="(z-1)" />
                                            <label :for="'zone'+(z-1)">Zone {{ z }}</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                         <div class="flex flex-col gap-2">
                             <label class="font-bold text-green-400">VictoriaMetrics</label>
                             <div class="flex flex-col gap-2">
                                <label>Metrics URL</label>
                                <InputText v-model="form.metrics_url" placeholder="http://victoriametrics:8428/write" />
                                <small class="text-gray-400">Standard: http://victoriametrics:8428/write</small>
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-col gap-2 border-t border-gray-700 pt-4">
                        <label class="font-bold text-red-400">Admin Sicherheit</label>
                        <div class="flex flex-col gap-2">
                            <label>Admin Passwort</label>
                            <InputText v-model="form.password" type="password" placeholder="Wähle ein sicheres Passwort" />
                             <small class="text-gray-400">Mindestens 6 Zeichen.</small>
                        </div>
                    </div>

                    <div class="flex justify-end pt-4">
                        <Button label="Einrichtung abschließen" icon="pi pi-check" @click="submitSetup" :loading="loading" />
                    </div>
                </div>
            </template>
        </Card>
        <Toast />
        <AppFooter />
    </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Toast from 'primevue/toast';
import Checkbox from 'primevue/checkbox';
import { useToast } from 'primevue/usetoast';
import AppFooter from '../components/AppFooter.vue';

const router = useRouter();
const toast = useToast();
const loading = ref(false);

const form = ref({
    idm_host: '',
    idm_port: 502,
    circuits: ['A'],
    zones: [],
    metrics_url: 'http://victoriametrics:8428/write',
    password: ''
});

const submitSetup = async () => {
    if (form.value.password.length < 6) {
        toast.add({ severity: 'warn', summary: 'Ungültig', detail: 'Passwort muss mindestens 6 Zeichen lang sein', life: 3000 });
        return;
    }

    loading.value = true;
    try {
        const res = await axios.post('/api/setup', form.value);
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Einrichtung abgeschlossen', life: 3000 });
            setTimeout(() => {
                router.push('/login');
            }, 1000);
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
};
</script>
