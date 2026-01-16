<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const version = ref('Loading...');

onMounted(async () => {
    try {
        const res = await axios.get('/api/version');
        version.value = res.data.version;
    } catch (e) {
        version.value = 'Unknown';
    }
});
</script>

<template>
    <footer class="text-center text-xs text-gray-500 py-4 mt-auto w-full border-t border-gray-200 dark:border-gray-800">
        <div class="container mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>Version: {{ version }}</span>
            <span class="hidden sm:inline">|</span>
            <span>Erstellt mit <i class="pi pi-heart text-red-500"></i> von xerolux</span>
        </div>
    </footer>
</template>
