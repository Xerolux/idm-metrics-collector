<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="System Update erforderlich"
    :closable="false"
    :style="{ width: '450px' }"
  >
    <div class="flex flex-col gap-4">
      <Message severity="info" :closable="false">
        Bitte wähle dein Wärmepumpen-Modell aus, um fortzufahren. Diese Information wird für
        diagnostische Zwecke benötigt.
      </Message>

      <div class="flex flex-col gap-2">
        <label class="font-bold">Hersteller</label>
        <InputText value="IDM" disabled class="w-full" />
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-bold">Modell</label>
        <Dropdown
          v-model="selectedModel"
          :options="models"
          optionLabel="label"
          optionValue="value"
          placeholder="Modell wählen"
          class="w-full"
          filter
        />
      </div>
    </div>
    <template #footer>
      <Button
        label="Speichern"
        icon="pi pi-check"
        @click="save"
        :loading="saving"
        :disabled="!selectedModel"
      />
    </template>
  </Dialog>
</template>

<script setup>
// Xerolux 2026
import { ref, onMounted } from 'vue'
import api from '@/utils/api.js'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/select'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'

const visible = ref(false)
const saving = ref(false)
const selectedModel = ref(null)
const models = ref([])
const toast = useToast()

const checkConfig = async () => {
  try {
    const res = await api.get('/api/config')
    // If hp_model is missing or empty, show dialog
    if (!res.data.hp_model) {
      visible.value = true
      loadModels()
    }
  } catch (e) {
    // If not authenticated (401), do nothing
    if (e.response && e.response.status === 401) {
      return
    }
    console.error('Check config failed', e)
  }
}

const loadModels = async () => {
  try {
    const res = await api.get('/api/info')
    if (res.data.heat_pump_models) {
      models.value = res.data.heat_pump_models.map((m) => ({ label: m, value: m }))
    } else {
      // Fallback
      models.value = [
        { label: 'AERO ALM 6-15', value: 'AERO ALM 6-15' },
        { label: 'Other', value: 'Other' }
      ]
    }
  } catch (e) {
    console.error('Failed to load models', e)
  }
}

const save = async () => {
  if (!selectedModel.value) return

  saving.value = true
  try {
    await api.post('/api/config', {
      hp_model: selectedModel.value
    })
    toast.add({
      severity: 'success',
      summary: 'Gespeichert',
      detail: 'Modell erfolgreich aktualisiert',
      life: 3000
    })
    visible.value = false
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || e.message,
      life: 5000
    })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  // Check after short delay to ensure app is mounted/authed
  setTimeout(checkConfig, 1000)
})
</script>
