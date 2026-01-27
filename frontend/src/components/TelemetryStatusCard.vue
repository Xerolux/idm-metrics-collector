<template>
    <div class="bg-white rounded-lg p-4 h-full flex flex-col shadow-sm border border-gray-200">
        <div class="flex items-center justify-between mb-3">
            <h3 class="text-gray-900 font-bold text-sm flex items-center gap-2">
                <i class="pi pi-cloud text-purple-500"></i>
                Community Status
            </h3>
            <button
                @click="refreshStatus"
                class="text-gray-400 hover:text-gray-600 p-1"
                :class="{ 'animate-spin': loading }"
                title="Aktualisieren"
            >
                <i class="pi pi-refresh text-xs"></i>
            </button>
        </div>

        <div v-if="loading" class="flex-grow flex items-center justify-center">
            <i class="pi pi-spin pi-spinner text-2xl text-gray-400"></i>
        </div>

        <div v-else-if="status" class="flex-grow flex flex-col gap-3">
            <!-- Contribution Status -->
            <div
                class="p-3 rounded-lg flex items-center gap-3"
                :class="sharingEnabled ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'"
            >
                <i
                    class="text-xl"
                    :class="sharingEnabled ? 'pi pi-check-circle text-green-500' : 'pi pi-circle text-gray-400'"
                ></i>
                <div>
                    <div class="text-sm font-medium" :class="sharingEnabled ? 'text-green-700' : 'text-gray-600'">
                        {{ sharingEnabled ? 'Daten werden geteilt' : 'Teilen deaktiviert' }}
                    </div>
                    <div class="text-xs text-gray-500">
                        {{ sharingEnabled ? 'Sie tragen zur Community bei' : 'Aktivieren Sie das Teilen in den Einstellungen' }}
                    </div>
                </div>
            </div>

            <!-- Pool Status -->
            <div class="grid grid-cols-2 gap-2">
                <div class="text-center p-2 bg-gray-50 rounded">
                    <div class="text-lg font-bold text-purple-600">{{ status.total_installations || 0 }}</div>
                    <div class="text-xs text-gray-500">Nutzer</div>
                </div>
                <div class="text-center p-2 bg-gray-50 rounded">
                    <div class="text-lg font-bold text-blue-600">{{ formatNumber(status.total_data_points || 0) }}</div>
                    <div class="text-xs text-gray-500">Datenpunkte</div>
                </div>
            </div>

            <!-- Model Status -->
            <div
                class="p-2 rounded text-center text-sm"
                :class="status.data_sufficient ? 'bg-purple-50 text-purple-700' : 'bg-yellow-50 text-yellow-700'"
            >
                <i
                    class="mr-1"
                    :class="status.data_sufficient ? 'pi pi-check' : 'pi pi-clock'"
                ></i>
                {{ status.data_sufficient ? 'Community-Modell verfügbar' : 'Modell wird trainiert...' }}
            </div>
        </div>

        <div v-else class="flex-grow flex items-center justify-center text-gray-400 text-sm">
            <div class="text-center">
                <i class="pi pi-exclamation-circle text-xl mb-2"></i>
                <p>Status nicht verfügbar</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import axios from 'axios';

const props = defineProps({
    sharingEnabled: {
        type: Boolean,
        default: true
    }
});

const status = ref(null);
const loading = ref(false);
let refreshInterval = null;

const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
};

const refreshStatus = async () => {
    loading.value = true;
    try {
        const response = await axios.get('/api/telemetry/pool-status');
        status.value = response.data;
    } catch (error) {
        console.warn('Could not fetch telemetry status:', error);
        status.value = null;
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    refreshStatus();
    // Refresh every 5 minutes
    refreshInterval = setInterval(refreshStatus, 300000);
});

onUnmounted(() => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
</script>
