<template>
  <div class="heatpump-setup flex flex-col gap-4">
    <!-- Steps -->
    <div class="flex justify-between mb-4">
      <div v-for="(step, index) in steps" :key="index"
           class="flex items-center"
           :class="{'text-blue-400 font-bold': currentStep === index, 'text-gray-500': currentStep !== index}">
        <span class="w-6 h-6 rounded-full border flex items-center justify-center mr-2"
              :class="currentStep === index ? 'border-blue-400' : 'border-gray-500'">
              {{ index + 1 }}
        </span>
        {{ step }}
      </div>
    </div>

    <!-- Content -->
    <div class="step-content min-h-[300px]">
        <!-- Step 1: Manufacturer & Model -->
        <div v-if="currentStep === 0" class="flex flex-col gap-4">
            <h3>Hersteller auswählen</h3>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div v-for="mfr in manufacturers" :key="mfr.id"
                     class="p-4 border rounded cursor-pointer hover:bg-gray-700 flex flex-col items-center gap-2"
                     :class="form.manufacturer === mfr.id ? 'border-blue-500 bg-gray-700' : 'border-gray-600'"
                     @click="selectManufacturer(mfr.id)">
                    <span class="font-bold">{{ mfr.name }}</span>
                </div>
            </div>

            <div v-if="form.manufacturer" class="flex flex-col gap-2 mt-4">
                <label>Modell auswählen</label>
                <Dropdown v-model="form.model" :options="selectedManufacturerModels" optionLabel="name" optionValue="id" placeholder="Modell wählen" class="w-full" />
            </div>
        </div>

        <!-- Step 2: Connection -->
        <div v-if="currentStep === 1" class="flex flex-col gap-4">
            <Message severity="info" v-if="setupInstructions" :closable="false">{{ setupInstructions }}</Message>

            <div class="flex flex-col gap-2">
                <label>Host / IP</label>
                <InputText v-model="form.connection.host" placeholder="192.168.1.100" />
            </div>
            <div class="flex flex-col gap-2">
                <label>Port</label>
                <InputNumber v-model="form.connection.port" :useGrouping="false" />
            </div>
            <div class="flex flex-col gap-2">
                <label>Unit ID</label>
                <InputNumber v-model="form.connection.unit_id" :useGrouping="false" />
            </div>

            <div class="flex items-center gap-2 mt-2">
                <Button label="Verbindung testen" @click="testConnection" :loading="testing" severity="secondary" />
                <span v-if="testResult" :class="testResult.success ? 'text-green-400' : 'text-red-400'">
                    {{ testResult.message }}
                </span>
            </div>
        </div>

        <!-- Step 3: Config -->
        <div v-if="currentStep === 2" class="flex flex-col gap-4">
            <div class="flex flex-col gap-2">
                <label>Name (Anzeige)</label>
                <InputText v-model="form.name" placeholder="z.B. Wärmepumpe Hauptgebäude" />
            </div>

            <div v-if="form.manufacturer === 'idm'" class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                    <label>Heizkreise</label>
                    <div class="flex flex-wrap gap-4">
                        <div v-for="c in ['A', 'B', 'C', 'D', 'E', 'F', 'G']" :key="c" class="flex items-center gap-2">
                            <Checkbox v-model="form.config.circuits" :inputId="'circuit'+c" :value="c" />
                            <label :for="'circuit'+c">{{ c }}</label>
                        </div>
                    </div>
                </div>
                <div class="flex flex-col gap-2">
                    <label>Zonen</label>
                    <div class="flex flex-wrap gap-4">
                        <div v-for="z in 12" :key="z" class="flex items-center gap-2">
                            <Checkbox v-model="form.config.zones" :inputId="'zone'+(z-1)" :value="(z-1)" />
                            <label :for="'zone'+(z-1)">{{ z }}</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Navigation -->
    <div class="flex justify-between mt-6 pt-4 border-t border-gray-700">
        <Button label="Zurück" @click="currentStep--" :disabled="currentStep === 0" severity="secondary" />
        <Button v-if="currentStep < 2" label="Weiter" @click="currentStep++" :disabled="!canProceed" />
        <Button v-else label="Hinzufügen" @click="submit" :loading="submitting" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useHeatpumpsStore } from '@/stores/heatpumps'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Message from 'primevue/message'

const emit = defineEmits(['complete', 'cancel'])
const store = useHeatpumpsStore()

const steps = ['Hersteller', 'Verbindung', 'Konfiguration']
const currentStep = ref(0)
const testing = ref(false)
const testResult = ref(null)
const submitting = ref(false)

const form = ref({
  name: '',
  manufacturer: '',
  model: '',
  connection: {
    host: '',
    port: 502,
    unit_id: 1
  },
  config: {
    circuits: ['A'],
    zones: []
  }
})

const manufacturers = computed(() => store.manufacturers)
const selectedManufacturerModels = computed(() => {
    const mfr = manufacturers.value.find(m => m.id === form.value.manufacturer)
    return mfr ? mfr.models : []
})

const setupInstructions = computed(() => {
    return null
})

const canProceed = computed(() => {
    if (currentStep.value === 0) return form.value.manufacturer && form.value.model
    if (currentStep.value === 1) return form.value.connection.host && form.value.connection.port
    return true
})

const selectManufacturer = (id) => {
    form.value.manufacturer = id
    form.value.model = '' // Reset model
}

const testConnection = async () => {
    testing.value = true
    setTimeout(() => {
        testing.value = false
        testResult.value = { success: true, message: 'Nicht implementiert (wird beim Speichern geprüft)' }
    }, 1000)
}

const submit = async () => {
    submitting.value = true
    try {
        await store.addHeatpump(form.value)
        emit('complete')
    } catch (e) {
        console.error(e)
    } finally {
        submitting.value = false
    }
}

onMounted(() => {
    store.fetchManufacturers()
})
</script>
