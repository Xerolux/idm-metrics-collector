<template>
    <div class="bg-gray-800 rounded-xl p-4 border border-gray-700 h-full flex flex-col justify-between">
        <h3 class="text-lg font-bold text-center mb-2">Ambient Sensor</h3>

        <div class="grid grid-cols-2 gap-4">
            <div class="text-center">
                <span class="text-sm text-gray-400 block mb-1">Indoor</span>
                <div class="bg-orange-50/10 border border-orange-200/20 rounded-lg p-2 mb-2">
                    <div class="text-xs text-orange-200">Temperature</div>
                    <div class="text-2xl font-bold">{{ indoorTemp }} <span class="text-base font-normal">°C</span></div>
                </div>
                <div class="bg-blue-50/10 border border-blue-200/20 rounded-lg p-2">
                    <div class="text-xs text-blue-200">Humidity</div>
                    <div class="text-2xl font-bold">{{ indoorHum }} <span class="text-base font-normal">%</span></div>
                </div>
            </div>

            <div class="text-center">
                <span class="text-sm text-gray-400 block mb-1">Outdoor</span>
                <div class="bg-orange-50/10 border border-orange-200/20 rounded-lg p-2 mb-2">
                    <div class="text-xs text-orange-200">Temperature</div>
                    <div class="text-2xl font-bold">{{ outdoorTemp }} <span class="text-base font-normal">°C</span></div>
                </div>
                <div class="bg-blue-50/10 border border-blue-200/20 rounded-lg p-2">
                    <div class="text-xs text-blue-200">Humidity</div>
                    <div class="text-2xl font-bold">{{ outdoorHum }} <span class="text-base font-normal">%</span></div>
                </div>
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

// Map sensors to display values. Adjust keys based on actual sensor names
const indoorTemp = computed(() => formatValue(props.data['temp_room_circuit_A'])); // Fallback if no specific indoor sensor
const indoorHum = computed(() => formatValue(props.data['temp_internal_humidity'] || 49)); // Mock/Default if missing
const outdoorTemp = computed(() => formatValue(props.data['temp_outside']));
const outdoorHum = computed(() => formatValue(props.data['temp_external_humidity']));

const formatValue = (val) => {
    if (val === undefined || val === null) return '--';
    const num = parseFloat(val);
    if (isNaN(num)) return val;
    return num.toFixed(1);
};
</script>
