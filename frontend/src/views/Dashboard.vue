<template>
    <div class="p-2 sm:p-4 h-screen flex flex-col bg-gray-100 overflow-hidden">
        <!-- Top Bar -->
        <div class="flex items-center justify-between mb-2 sm:mb-4 px-1">
            <div class="flex items-center gap-2 text-sm sm:text-base text-gray-600">
                <i class="pi pi-th-large"></i>
                <span class="font-bold">Dashboards</span>
                <i class="pi pi-angle-right text-xs"></i>
                <span>Alle</span>
                <i class="pi pi-angle-right text-xs"></i>
                <span class="text-gray-900 font-semibold">Home Dashboard</span>
            </div>
            <div class="flex items-center gap-3">
                 <button class="p-2 hover:bg-gray-200 rounded text-gray-600"><i class="pi pi-expand"></i></button>
                 <button class="p-2 hover:bg-gray-200 rounded text-gray-600"><i class="pi pi-bell"></i></button>
                 <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-bold">MK</div>
            </div>
        </div>

        <div class="flex flex-col lg:flex-row gap-3 h-full overflow-hidden">
            <!-- Left Sidebar -->
            <div class="w-full lg:w-64 flex-shrink-0 flex flex-col gap-3 overflow-y-auto pb-4">
                <div class="flex gap-2">
                    <button class="flex-1 bg-teal-700 hover:bg-teal-800 text-white py-2 px-3 rounded flex items-center justify-center gap-2 text-sm font-medium transition-colors">
                        <i class="pi pi-chart-bar"></i> Chart Dashboard
                    </button>
                    <button class="bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 px-3 rounded flex items-center justify-center gap-2 text-sm font-medium transition-colors">
                        <i class="pi pi-file-export"></i>
                    </button>
                </div>

                <AmbientSensorCard :data="sensors" />
                <PowerOverviewCard :data="sensors" />
            </div>

            <!-- Main Grid -->
            <div class="flex-grow grid grid-cols-1 md:grid-cols-2 gap-3 overflow-y-auto pb-20 lg:pb-4 pr-1">
                <div class="h-64 md:h-80">
                    <LineChartCard
                        title="Underfloor Heating: Flow & Return Temp"
                        :queries="[
                            { label: 'Flow Temp', query: 'temp_flow_current_circuit_A', color: '#f59e0b' },
                            { label: 'Return Temp', query: 'temp_return_circuit_A', color: '#3b82f6' },
                            { label: 'Heat Pump Power', query: 'power_current_draw', color: '#ef4444' },
                            { label: 'Outdoor Temp', query: 'temp_outside', color: '#22c55e' }
                        ]"
                    />
                </div>

                <div class="h-64 md:h-80">
                    <LineChartCard
                        title="Tank Heating Sensing"
                        :queries="[
                            { label: 'Buffer Tank Top', query: 'temp_heat_storage', color: '#a855f7' },
                            { label: 'Buffer Tank Bottom', query: 'temp_cold_storage', color: '#3b82f6' },
                            { label: 'Heat Pump Power', query: 'power_current_draw', color: '#ef4444' }
                        ]"
                        :hours="24"
                    />
                </div>

                <div class="h-64 md:h-80">
                    <LineChartCard
                        title="Radiators Flow & Return: 1st & 2nd Floor"
                        :queries="[
                            { label: 'Flow Temp', query: 'temp_flow_current_circuit_B', color: '#f59e0b' },
                            { label: 'Return Temp', query: 'temp_return_circuit_B', color: '#3b82f6' },
                            { label: 'Heat Pump Power', query: 'power_current_draw', color: '#ef4444' },
                            { label: 'Outdoor Temp', query: 'temp_outside', color: '#22c55e' }
                        ]"
                    />
                </div>

                <div class="h-64 md:h-80">
                    <LineChartCard
                        title="3rd Floor: Flow & Return Temperatures"
                        :queries="[
                            { label: 'Flow Temp', query: 'temp_flow_current_circuit_C', color: '#f59e0b' },
                            { label: 'Return Temp', query: 'temp_return_circuit_C', color: '#3b82f6' },
                            { label: 'Heat Pump Power', query: 'power_current_draw', color: '#ef4444' },
                            { label: 'Outdoor Temp', query: 'temp_outside', color: '#22c55e' }
                        ]"
                    />
                </div>

                 <div class="h-64 md:h-80">
                    <LineChartCard
                        title="3rd Floor Deep Dive"
                        :queries="[
                            { label: 'Flow Temp', query: 'temp_flow_current_circuit_C', color: '#f59e0b' },
                            { label: 'Return Temp', query: 'temp_return_circuit_C', color: '#3b82f6' },
                            { label: 'Indoor Temp', query: 'temp_room_circuit_C', color: '#a855f7' },
                            { label: 'Outdoor Temp', query: 'temp_outside', color: '#22c55e' }
                        ]"
                    />
                </div>

                 <div class="h-64 md:h-80">
                    <LineChartCard
                        title="Consumption change"
                        :queries="[
                            { label: 'Building Total', query: 'power_current', color: '#3b82f6' },
                            { label: 'Heat Pump Total', query: 'power_current_draw', color: '#ef4444' },
                            { label: 'Outdoor Temp', query: 'temp_outside', color: '#22c55e' }
                        ]"
                        :hours="24"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import AmbientSensorCard from '../components/AmbientSensorCard.vue';
import PowerOverviewCard from '../components/PowerOverviewCard.vue';
import LineChartCard from '../components/LineChartCard.vue';

const sensors = ref({});
const timer = ref(null);

const fetchData = async () => {
    try {
        const res = await axios.get('/api/data');
        sensors.value = res.data;
    } catch {
        // ignore
    }
};

onMounted(() => {
    fetchData();
    timer.value = setInterval(fetchData, 5000);
});

onUnmounted(() => {
    if (timer.value) clearInterval(timer.value);
});
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
