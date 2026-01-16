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
                        <span>Über IDM Metrics Collector</span>
                    </div>
                </template>
                <template #subtitle>
                    Open Source Logger für IDM Wärmepumpen mit AI-Unterstützung
                </template>
                <template #content>
                    <div class="space-y-6">

                        <!-- Project Info -->
                        <div>
                            <p class="text-gray-700 dark:text-gray-300 mb-4">
                                Ein umfassendes Tool zum Protokollieren, Visualisieren und Steuern von IDM-Wärmepumpen über Modbus TCP.
                                Jetzt neu mit integrierter KI-Anomalieerkennung zur frühzeitigen Identifikation von Unregelmäßigkeiten.
                            </p>

                            <h3 class="text-lg font-semibold mb-2">Hauptfunktionen</h3>
                            <ul class="list-disc list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-1">
                                <li>Detailliertes Logging & Visualisierung (VictoriaMetrics + Grafana)</li>
                                <li>Intelligente Steuerung via Modbus TCP</li>
                                <li>AI Anomalie-Erkennung (Echtzeit-Überwachung mit River)</li>
                                <li>Techniker-Tools (Code Generator)</li>
                                <li>Benachrichtigungssystem (Signal Messenger)</li>
                            </ul>

                            <div class="flex flex-wrap gap-2">
                                <a href="https://github.com/Xerolux/idm-metrics-collector" target="_blank" rel="noopener">
                                    <Button label="GitHub Repository" icon="pi pi-github" severity="secondary" />
                                </a>
                                <a href="https://github.com/Xerolux/idm-metrics-collector/blob/main/LICENSE" target="_blank" rel="noopener">
                                    <Button label="MIT Lizenz" icon="pi pi-file" severity="secondary" outlined />
                                </a>
                                <a href="https://www.buymeacoffee.com/xerolux" target="_blank" rel="noopener">
                                    <Button label="Spenden / Donate" icon="pi pi-coffee" severity="warning" />
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
                                <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">VictoriaMetrics</span>
                                <span class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">River (Online ML)</span>
                                <span class="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">Docker</span>
                            </div>
                        </div>

                        <!-- Disclaimer -->
                        <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded border border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
                            <h4 class="font-bold mb-1">Haftungsausschluss / Disclaimer</h4>
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
                        Erstellt mit <i class="pi pi-heart-fill text-red-500 mx-1" style="font-size: 0.7rem"></i> von xerolux
                    </div>
                </template>
            </Card>
        </div>
    </div>
</template>
