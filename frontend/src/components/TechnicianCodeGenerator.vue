<template>
  <div class="flex flex-col gap-6">
    <div class="p-4 border border-yellow-500/50 rounded bg-yellow-500/10">
      <div class="flex items-center gap-2 font-bold mb-2 text-yellow-400">
         <i class="pi pi-exclamation-triangle"></i>
         <span>Warning</span>
      </div>
      <p class="text-sm text-gray-200">
        Use these codes only if you know what you are doing! Modifying settings in the technician menu can damage your heat pump.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Codes -->
      <div class="flex flex-col gap-4 col-span-2 md:col-span-1">
          <div class="p-4 bg-gray-700 rounded flex flex-col gap-1">
             <span class="text-gray-400 text-sm">Level 1 Code (4-digit)</span>
             <div class="flex items-center justify-between">
                <span class="text-3xl font-mono text-blue-400 font-bold tracking-widest">{{ codes.level_1 || '----' }}</span>
                <Button icon="pi pi-copy" text rounded size="small" @click="copy(codes.level_1)" :disabled="!codes.level_1" />
             </div>
          </div>

           <div class="p-4 bg-gray-700 rounded flex flex-col gap-1">
             <span class="text-gray-400 text-sm">Level 2 Code (5-digit)</span>
             <div class="flex items-center justify-between">
                <span class="text-3xl font-mono text-green-400 font-bold tracking-widest">{{ codes.level_2 || '-----' }}</span>
                <Button icon="pi pi-copy" text rounded size="small" @click="copy(codes.level_2)" :disabled="!codes.level_2" />
             </div>
          </div>
      </div>

       <div class="flex flex-col justify-center items-start gap-4">
            <Button label="Refresh Codes" icon="pi pi-refresh" @click="fetchCodes" :loading="loading" />
            <p class="text-xs text-gray-400">
                Codes are generated based on the current server time.
            </p>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';

const toast = useToast();
const codes = ref({ level_1: '', level_2: '' });
const loading = ref(false);
let intervalId = null;

const fetchCodes = async () => {
    loading.value = true;
    try {
        // Add timestamp to prevent caching
        const res = await axios.get(`/api/tools/technician-code?t=${Date.now()}`);
        codes.value = res.data;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to fetch technician codes', life: 3000 });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchCodes();
    // Refresh every 10 seconds to ensure codes are up-to-date
    intervalId = setInterval(fetchCodes, 10000);
});

onUnmounted(() => {
    if (intervalId) clearInterval(intervalId);
});

const copy = (text) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    toast.add({ severity: 'success', summary: 'Copied', detail: 'Code copied to clipboard', life: 2000 });
};
</script>
