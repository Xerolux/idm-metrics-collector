<script setup>
import Card from 'primevue/card';
import Button from 'primevue/button';
</script>

<template>
    <div class="flex justify-center">
        <div class="w-full max-w-3xl">
            <Card class="shadow-lg">
                <template #title>
                    <div class="flex items-center gap-2">
                        <i class="pi pi-info-circle text-2xl text-blue-500"></i>
                        <span>About IDM Metrics Collector</span>
                    </div>
                </template>
                <template #subtitle>
                    Open Source Logger for IDM Heat Pumps
                </template>
                <template #content>
                    <div class="space-y-6">

                        <!-- Project Info -->
                        <div>
                            <p class="text-gray-700 dark:text-gray-300 mb-4">
                                A comprehensive tool to log, visualize, and control IDM Heat Pumps via Modbus TCP.
                                Built with modern web technologies for optimal performance on all devices.
                            </p>
                            <div class="flex flex-wrap gap-2">
                                <a href="https://github.com/Xerolux/idm-metrics-collector" target="_blank" rel="noopener">
                                    <Button label="GitHub Repository" icon="pi pi-github" severity="secondary" />
                                </a>
                                <a href="https://github.com/Xerolux/idm-metrics-collector/blob/main/LICENSE" target="_blank" rel="noopener">
                                    <Button label="MIT License" icon="pi pi-file" severity="secondary" outlined />
                                </a>
                            </div>
                        </div>

                        <!-- Tech Stack -->
                        <div>
                            <h3 class="text-lg font-semibold mb-2">Powered By</h3>
                            <div class="flex flex-wrap gap-2">
                                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Vue 3</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">PrimeVue</span>
                                <span class="px-3 py-1 bg-cyan-100 text-cyan-800 rounded-full text-sm font-medium">Tailwind CSS</span>
                                <span class="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">Flask</span>
                                <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">InfluxDB v3</span>
                            </div>
                        </div>

                        <!-- Disclaimer -->
                        <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded border border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
                            <h4 class="font-bold mb-1">Disclaimer / Haftungsausschluss</h4>
                            <p class="italic">
                                THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
                                INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
                                PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
                                FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY.
                            </p>
                            <p class="mt-2 text-xs">
                                Alle Rechte liegen bei den jeweiligen Urhebern. Nutzung auf eigene Gefahr.
                            </p>
                        </div>

                    </div>
                </template>
                <template #footer>
                    <div class="text-center text-xs text-gray-400">
                        Made with <i class="pi pi-heart-fill text-red-500 mx-1" style="font-size: 0.7rem"></i> by xerolux
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>
