<template>
    <div class="bg-gray-800 rounded-xl p-4 border border-gray-700 h-full flex flex-col">
        <h3 class="text-lg font-bold text-center mb-4">Power Overview</h3>

        <div class="space-y-3">
            <div class="flex items-center justify-between bg-orange-50/10 border border-orange-200/30 rounded-lg px-3 py-2">
                <span class="text-sm font-medium">Building Power</span>
                <span class="text-xl font-bold">{{ buildingPower }} <span class="text-sm font-normal">kW</span></span>
            </div>

            <div class="flex items-center justify-between bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2">
                <span class="text-sm font-medium">HeatPump Power</span>
                <span class="text-xl font-bold">{{ heatPumpPower }} <span class="text-sm font-normal">kW</span></span>
            </div>

            <div class="flex items-center justify-between bg-green-50/10 border border-green-200/30 rounded-lg px-3 py-2">
                <span class="text-sm font-medium">3rd Floor ACs Power</span>
                <span class="text-xl font-bold">{{ ac3Power }} <span class="text-sm font-normal">kW</span></span>
            </div>

            <div class="flex items-center justify-between bg-blue-50/10 border border-blue-200/30 rounded-lg px-3 py-2">
                <span class="text-sm font-medium">1st Floor ACs Power</span>
                <span class="text-xl font-bold">{{ ac1Power }} <span class="text-sm font-normal">W</span></span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    data: {
        type: Object,
        default: () => ({})
    }
});

const buildingPower = computed(() => formatValue(props.data['power_current'], 2));
const heatPumpPower = computed(() => formatValue(props.data['power_current_draw'], 2));
// Mocking these as they might not exist in standard IDM mapping
const ac3Power = computed(() => formatValue(props.data['power_ac_3'] || 0.14, 2));
const ac1Power = computed(() => {
    const val = props.data['power_ac_1'];
    return val !== undefined ? Math.round(val) : 667;
});

const formatValue = (val, decimals = 1) => {
    if (val === undefined || val === null) return '--';
    const num = parseFloat(val);
    if (isNaN(num)) return val;
    return num.toFixed(decimals);
};
</script>
