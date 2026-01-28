<template>
    <div class="p-4 flex flex-col gap-4">
        <div class="flex justify-between items-center mb-4">
            <h1 class="text-2xl font-bold">Systemprotokolle</h1>
            <div class="flex gap-2">
                <Button
                    label="Teilen"
                    icon="pi pi-share-alt"
                    @click="shareLogs"
                    :disabled="logs.length === 0"
                    :loading="sharing"
                    severity="info"
                />
                <Button
                    label="Protokoll herunterladen"
                    icon="pi pi-download"
                    @click="downloadLogs"
                    :disabled="logs.length === 0"
                    severity="secondary"
                />
            </div>
        </div>

        <div v-if="loading && logs.length === 0" class="flex justify-center">
             <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else class="bg-gray-800 rounded p-4 font-mono text-sm h-[600px] overflow-y-auto">
             <div v-for="(log, index) in logs" :key="log.id || index" class="mb-1 border-b border-gray-700 pb-1">
                 <span class="text-gray-400">[{{ log.asctime }}]</span>
                 <span :class="getLevelColor(log.levelname)" class="mx-2 font-bold">{{ log.levelname }}</span>
                 <span class="text-blue-300">{{ log.name }}:</span>
                 <span class="text-white ml-2">{{ log.message }}</span>
             </div>
        </div>

        <!-- Share Dialog -->
        <Dialog v-model:visible="shareDialogVisible" modal header="Protokoll geteilt" :style="{ width: '500px' }">
            <div class="flex flex-col gap-4">
                <p class="text-gray-300">
                    Das Protokoll wurde erfolgreich hochgeladen und verschlüsselt.
                    Dieser Link ist 1 Woche gültig.
                </p>
                <div class="flex gap-2">
                    <InputText v-model="shareLink" class="w-full" readonly />
                    <Button icon="pi pi-copy" @click="copyLink" />
                </div>
            </div>
            <template #footer>
                <Button label="Schließen" @click="shareDialogVisible = false" text />
            </template>
        </Dialog>
        <Toast />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const logs = ref([]);
const loading = ref(true);
const timer = ref(null);
const lastId = ref(0);

// Sharing state
const sharing = ref(false);
const shareDialogVisible = ref(false);
const shareLink = ref('');

onMounted(() => {
    fetchLogs();
    timer.value = setInterval(fetchLogs, 5000);
});

onUnmounted(() => {
    if (timer.value) clearInterval(timer.value);
});

const fetchLogs = async () => {
    try {
        const url = lastId.value > 0 ? `/api/logs?since_id=${lastId.value}` : '/api/logs';
        const res = await axios.get(url);

        if (res.data && res.data.length > 0) {
            // Logs are returned [newest, ..., oldest]
            if (lastId.value === 0) {
                // Initial load
                logs.value = res.data;
            } else {
                // Incremental load: prepend new logs
                logs.value = [...res.data, ...logs.value].slice(0, 1000);
            }
            // Update lastId from the newest log (first in list)
            if (logs.value.length > 0) {
                lastId.value = logs.value[0].id || 0;
            }
        }
    } catch (e) {
        console.error("Protokolle konnten nicht abgerufen werden", e);
    } finally {
        loading.value = false;
    }
};

const downloadLogs = () => {
    // Direct download link
    window.location.href = '/api/logs/download';
};

const shareLogs = async () => {
    sharing.value = true;
    try {
        const res = await axios.post('/api/logs/share');
        if (res.data.success) {
            shareLink.value = res.data.link;
            shareDialogVisible.value = true;
        } else {
            toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error || 'Upload fehlgeschlagen', life: 5000 });
        }
    } catch (e) {
        console.error("Fehler beim Teilen", e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
    } finally {
        sharing.value = false;
    }
};

const copyLink = () => {
    navigator.clipboard.writeText(shareLink.value);
    toast.add({ severity: 'success', summary: 'Kopiert', detail: 'Link in die Zwischenablage kopiert', life: 2000 });
};

const getLevelColor = (level) => {
    switch(level) {
        case 'INFO': return 'text-green-400';
        case 'WARNING': return 'text-yellow-400';
        case 'ERROR': return 'text-red-400';
        case 'CRITICAL': return 'text-red-600';
        default: return 'text-gray-400';
    }
};
</script>
