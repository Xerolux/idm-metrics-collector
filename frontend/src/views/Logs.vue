<template>
    <div class="p-4 flex flex-col gap-4">
        <div class="flex justify-between items-center mb-4">
            <h1 class="text-2xl font-bold">Systemprotokolle</h1>
            <Button
                label="Protokoll herunterladen"
                icon="pi pi-download"
                @click="downloadLogs"
                :disabled="logs.length === 0"
                severity="secondary"
            />
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
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import Button from 'primevue/button';

const logs = ref([]);
const loading = ref(true);
const timer = ref(null);
const lastId = ref(0);

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
