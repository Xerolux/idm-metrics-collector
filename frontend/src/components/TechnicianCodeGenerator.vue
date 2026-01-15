<template>
  <div class="flex flex-col gap-6">
    <div class="p-4 border border-yellow-500/50 rounded bg-yellow-500/10">
      <div class="flex items-center gap-2 font-bold mb-2 text-yellow-400">
         <i class="pi pi-exclamation-triangle"></i>
         <span>Warnung</span>
      </div>
      <p class="text-sm text-gray-200">
        Verwende diese Codes nur, wenn du weißt, was du tust! Änderungen im Technikermenü können deine Wärmepumpe beschädigen.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Codes -->
      <div class="flex flex-col gap-4 col-span-2 md:col-span-1">
          <div class="p-4 bg-gray-700 rounded flex flex-col gap-1">
             <span class="text-gray-400 text-sm">Level 1 Code (4-stellig)</span>
             <div class="flex items-center justify-between">
                <span class="text-3xl font-mono text-blue-400 font-bold tracking-widest">{{ codes.level_1 || '----' }}</span>
                <Button icon="pi pi-copy" text rounded size="small" @click="copy(codes.level_1)" :disabled="!codes.level_1" />
             </div>
          </div>

           <div class="p-4 bg-gray-700 rounded flex flex-col gap-1">
             <span class="text-gray-400 text-sm">Level 2 Code (5-stellig)</span>
             <div class="flex items-center justify-between">
                <span class="text-3xl font-mono text-green-400 font-bold tracking-widest">{{ codes.level_2 || '-----' }}</span>
                <Button icon="pi pi-copy" text rounded size="small" @click="copy(codes.level_2)" :disabled="!codes.level_2" />
             </div>
          </div>
      </div>

       <div class="flex flex-col justify-center items-start gap-4">
            <Button label="Codes aktualisieren" icon="pi pi-refresh" @click="fetchCodes" :loading="loading" />
            <div class="flex flex-col gap-1 text-xs text-gray-400">
                <p>
                    <span class="font-bold">Serverzeit:</span> {{ codes.server_time || '--:--:--' }}
                </p>
                <p>
                    Level 1 Code ändert sich täglich.<br>
                    Level 2 Code ändert sich stündlich.
                </p>
            </div>
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
const codes = ref({ level_1: '', level_2: '', server_time: '' });
const loading = ref(false);
let intervalId = null;

const fetchCodes = async () => {
    loading.value = true;
    try {
        const res = await axios.get('/api/tools/technician-code?t=' + Date.now());
        codes.value = res.data;
        toast.add({ severity: 'success', summary: 'Aktualisiert', detail: 'Codes erfolgreich aktualisiert', life: 2000 });
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Technikercodes konnten nicht abgerufen werden', life: 3000 });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchCodes();
    intervalId = setInterval(fetchCodes, 60000);
});

onUnmounted(() => {
    if (intervalId) clearInterval(intervalId);
});

const copy = async (text) => {
    if (!text) return;
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            textArea.style.top = "0";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
        toast.add({ severity: 'success', summary: 'Kopiert', detail: 'Code in die Zwischenablage kopiert', life: 2000 });
    } catch (err) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Konnte nicht kopiert werden', life: 2000 });
    }
};
</script>
