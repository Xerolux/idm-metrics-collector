<template>
    <div class="p-2 sm:p-4 min-h-screen lg:h-screen flex flex-col bg-gray-100 lg:overflow-hidden">
        <DashboardManager />
    </div>
</template>

<script setup>
import DashboardManager from '../components/DashboardManager.vue';
</script>

<style scoped>
/* Scrollbar styling for a cleaner look */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}
</style>
