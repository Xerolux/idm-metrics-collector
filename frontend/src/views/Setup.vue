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
                                <label>Modell</label>
                                <Dropdown v-model="form.heatpump_model" :options="heatpumpModels" placeholder="Maschine auswählen" class="w-full" />
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

                    <div class="flex flex-col gap-2 border-t border-gray-700 pt-4">
                        <label class="font-bold text-purple-400">Community Daten</label>
                        <div class="flex items-start gap-3 p-3 bg-purple-900/20 border border-purple-700/50 rounded-md">
                             <Checkbox v-model="form.share_data" :binary="true" inputId="shareData" />
                             <div class="flex flex-col gap-1">
                                <label for="shareData" class="font-bold cursor-pointer">Daten teilen & Zustimmung</label>
                                <p class="text-sm text-gray-300 text-justify">
                                    Ich stimme zu, dass anonymisierte Sensordaten meiner Wärmepumpe an den Betreiber dieses Tools gesendet werden.
                                    Die Daten enthalten <strong>keine persönlichen Informationen</strong> (wie IP-Adresse, Standort oder Passwörter), sondern lediglich eine zufällige Installations-ID und technische Messwerte.
                                </p>
                                <p class="text-sm text-gray-300 mt-1 text-justify">
                                    Ich bestätige, dass die gesendeten Daten in das Eigentum des Tool-Betreibers übergehen. Dieser ist berechtigt, die Daten uneingeschränkt zu nutzen, zu analysieren, für das Training von KI-Modellen zu verwenden und diese (auch kommerziell) zu verwerten oder zu verkaufen.
                                    Im Gegenzug profitiere ich von verbesserten KI-Modellen zur Fehlererkennung, die auf diesen Gemeinschaftsdaten basieren.
                                </p>
                             </div>
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
import Dropdown from 'primevue/dropdown';
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
    password: '',
    heatpump_model: '',
    share_data: true
});

const heatpumpModels = [
    'AERO ALM 2-8',
    'AERO ALM 4-12',
    'AERO ALM 6-15',
    'AERO ALM 10-24',
    'AERO ALM 10-50 MAX',
    'AERO SLM',
    'AERO ILM',
    'TERRA SW',
    'TERRA ML',
    'TERRA SW Max',
    'iPump A',
    'iPump T',
    'iPump T7',
    'iPump T7 ONE',
    'iPump N5',
    'Andere / Unbekannt'
];

const submitSetup = async () => {
    if (form.value.password.length < 6) {
        toast.add({ severity: 'warn', summary: 'Ungültig', detail: 'Passwort muss mindestens 6 Zeichen lang sein', life: 3000 });
        return;
    }

    if (!form.value.heatpump_model) {
        toast.add({ severity: 'warn', summary: 'Fehlend', detail: 'Bitte wähle ein Wärmepumpen-Modell aus.', life: 3000 });
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
