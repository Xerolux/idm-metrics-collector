<template>
    <div class="flex items-center gap-2">
        <Dropdown v-model="selectedId" :options="heatpumps" optionLabel="name" optionValue="id"
                  placeholder="Wärmepumpe wählen" class="w-48 md:w-64"
                  @change="onChange">
            <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center">
                    <span>{{ getHeatpumpName(slotProps.value) }}</span>
                    <span v-if="!isConnected(slotProps.value)" class="ml-2 text-red-400 text-xs">(Offline)</span>
                </div>
                <span v-else>{{ slotProps.placeholder }}</span>
            </template>
            <template #option="slotProps">
                <div class="flex items-center justify-between w-full">
                    <span>{{ slotProps.option.name }}</span>
                    <span v-if="!slotProps.option.connected" class="text-red-400 text-xs ml-2">●</span>
                    <span v-else class="text-green-400 text-xs ml-2">●</span>
                </div>
            </template>
        </Dropdown>
        <Button icon="pi pi-plus" text rounded @click="$emit('add')" />
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHeatpumpsStore } from '@/stores/heatpumps'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'

const store = useHeatpumpsStore()
const emit = defineEmits(['add'])

const heatpumps = computed(() => store.heatpumps)
const selectedId = computed({
    get: () => store.activeHeatpumpId,
    set: (val) => store.setActiveHeatpump(val)
})

const getHeatpumpName = (id) => {
    const hp = heatpumps.value.find(h => h.id === id)
    return hp ? hp.name : id
}

const isConnected = (id) => {
    const hp = heatpumps.value.find(h => h.id === id)
    return hp ? hp.connected : false
}

const onChange = () => {
    // Trigger any necessary updates
}
</script>
