<script setup>
import { computed, defineProps } from 'vue';

const props = defineProps({
    title: String,
    value: [String, Number],
    unit: String,
    trend: {
        type: String,
        default: 'neutral' // up, down, neutral
    },
    status: {
        type: String,
        default: 'normal' // normal, warning, error, success
    }
});

const statusColor = computed(() => {
    switch (props.status) {
        case 'success': return 'text-success-400';
        case 'warning': return 'text-warning-400';
        case 'error': return 'text-error-400';
        default: return 'text-primary-400';
    }
});

const trendIcon = computed(() => {
    switch (props.trend) {
        case 'up': return 'pi pi-arrow-up';
        case 'down': return 'pi pi-arrow-down';
        default: return '';
    }
});

const trendColor = computed(() => {
    switch (props.trend) {
        case 'up': return 'text-success-400';
        case 'down': return 'text-error-400';
        default: return '';
    }
});
</script>

<template>
    <div class="h-full flex flex-col justify-between group hover:bg-gray-700/30 transition-all duration-300 rounded-lg p-3 -m-2 border border-transparent hover:border-gray-600">
        <div class="flex justify-between items-start">
            <div class="text-gray-300 text-sm sm:text-base font-semibold tracking-wide">{{ title }}</div>
            <i v-if="trendIcon" :class="[trendIcon, trendColor, 'text-sm transition-opacity']"></i>
        </div>
        <div class="flex items-baseline gap-1 mt-auto">
             <div :class="['text-3xl sm:text-4xl font-bold truncate tracking-tight', statusColor]" :title="value">
                {{ value }}
            </div>
            <div class="text-sm font-medium text-gray-400 mb-1">{{ unit }}</div>
        </div>
    </div>
</template>
