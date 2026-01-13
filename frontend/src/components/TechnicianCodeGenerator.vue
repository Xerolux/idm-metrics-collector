<template>
  <div class="flex flex-col gap-6">
    <div class="p-4 border border-yellow-500/50 rounded bg-yellow-500/10">
      <div class="flex items-center gap-2 font-bold mb-2 text-yellow-400">
         <i class="pi pi-exclamation-triangle"></i>
         <span>Warning</span>
      </div>
      <p class="text-sm text-gray-200">
        Use these codes only if you know what you are doing! Modifying settings in the technician menu can damage your heat pump.
        <br>
        The codes are calculated based on the current date and time (updated every second).
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Current Time Display -->
       <div class="p-4 bg-gray-700 rounded flex flex-col items-center justify-center gap-2">
         <span class="text-gray-400 text-sm">Reference Time</span>
         <span class="text-2xl font-mono font-bold">{{ formattedTime }}</span>
         <span class="text-sm text-gray-500">{{ formattedDate }}</span>
       </div>

      <!-- Codes -->
      <div class="flex flex-col gap-4">
          <div class="p-4 bg-gray-700 rounded flex flex-col gap-1">
             <span class="text-gray-400 text-sm">Level 1 Code (4-digit)</span>
             <div class="flex items-center justify-between">
                <span class="text-3xl font-mono text-blue-400 font-bold tracking-widest">{{ codeLevel1 }}</span>
                <Button icon="pi pi-copy" text rounded size="small" @click="copy(codeLevel1)" />
             </div>
          </div>

           <div class="p-4 bg-gray-700 rounded flex flex-col gap-1">
             <span class="text-gray-400 text-sm">Level 2 Code (5-digit)</span>
             <div class="flex items-center justify-between">
                <span class="text-3xl font-mono text-green-400 font-bold tracking-widest">{{ codeLevel2 }}</span>
                <Button icon="pi pi-copy" text rounded size="small" @click="copy(codeLevel2)" />
             </div>
          </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const currentTime = ref(new Date());
const intervalId = ref(null);

const updateTime = () => {
    currentTime.value = new Date();
};

onMounted(() => {
    updateTime();
    intervalId.value = setInterval(updateTime, 1000);
});

onUnmounted(() => {
    if (intervalId.value) clearInterval(intervalId.value);
});

const formattedTime = computed(() => {
    return currentTime.value.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
});

const formattedDate = computed(() => {
    return currentTime.value.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
});

const codeLevel1 = computed(() => {
    const d = currentTime.value.getDate().toString().padStart(2, '0');
    const m = (currentTime.value.getMonth() + 1).toString().padStart(2, '0');
    return `${d}${m}`;
});

const codeLevel2 = computed(() => {
    // Logic: hh_last + hh_first + year_last + month_last + day_last

    // Hours (24h format, 2 digits)
    const hours = currentTime.value.getHours().toString().padStart(2, '0');
    const hh_first = hours[0];
    const hh_last = hours[1];

    // Year (full year string)
    const year = currentTime.value.getFullYear().toString();
    const year_last = year.slice(-1);

    // Month (1-based string)
    const month = (currentTime.value.getMonth() + 1).toString();
    const month_last = month.slice(-1);

    // Day (1-based string)
    const day = currentTime.value.getDate().toString();
    const day_last = day.slice(-1);

    return `${hh_last}${hh_first}${year_last}${month_last}${day_last}`;
});

const copy = (text) => {
    navigator.clipboard.writeText(text);
    toast.add({ severity: 'success', summary: 'Copied', detail: 'Code copied to clipboard', life: 2000 });
};
</script>
