<template>
    <div class="flex flex-col gap-6">
        <h1 class="text-2xl font-bold mb-4">Werkzeuge</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card class="bg-gray-800 text-white">
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-key text-yellow-400"></i>
                        <span>Technikercode Generator</span>
                    </div>
                </template>
                <template #content>
                    <TechnicianCodeGenerator />
                </template>
            </Card>
        </div>
    </div>
</template>

<script setup>
import Card from 'primevue/card';
import TechnicianCodeGenerator from '../components/TechnicianCodeGenerator.vue';
</script>
