<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Alarme & Benachrichtigungen</h1>
      <button @click="openModal()" class="btn-primary">
        <span class="mr-2">+</span> Neuer Alarm
      </button>
    </div>

    <Toast />
    <ConfirmDialog />

    <!-- Alert List -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
      <div v-if="loading" class="p-6 text-center text-gray-500">Lade Alarme...</div>
      <div v-else-if="alerts.length === 0" class="p-6 text-center text-gray-500">
        Keine Alarme konfiguriert.
      </div>
      <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <li v-for="alert in alerts" :key="alert.id" class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition">
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white truncate">{{ alert.name }}</h3>
                <span :class="{'bg-green-100 text-green-800': alert.enabled, 'bg-gray-100 text-gray-800': !alert.enabled}"
                      class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ alert.enabled ? 'Aktiv' : 'Inaktiv' }}
                </span>
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  {{ alert.type === 'threshold' ? 'Grenzwert' : 'Status' }}
                </span>
              </div>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                <span v-if="alert.type === 'threshold'">
                  Wenn <strong>{{ alert.sensor }}</strong> {{ alert.condition }} <strong>{{ alert.threshold }}</strong>
                </span>
                <span v-else>
                  Regelmäßiger Statusbericht
                </span>
                <span class="mx-2">•</span>
                <span>Intervall: {{ formatInterval(alert.interval_seconds) }}</span>
              </p>
              <p class="mt-1 text-xs text-gray-400 font-mono truncate">
                "{{ alert.message }}"
              </p>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button @click="toggleAlert(alert)" class="text-gray-400 hover:text-blue-500" :aria-label="alert.enabled ? 'Alarm deaktivieren' : 'Alarm aktivieren'" :title="alert.enabled ? 'Alarm deaktivieren' : 'Alarm aktivieren'">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" v-if="!alert.enabled" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" v-else />
                </svg>
              </button>
              <button @click="openModal(alert)" class="text-gray-400 hover:text-yellow-500" aria-label="Alarm bearbeiten" title="Alarm bearbeiten">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
              <button @click="deleteAlert(alert)" class="text-gray-400 hover:text-red-500" aria-label="Alarm löschen" title="Alarm löschen">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="showModal"
      :header="editingAlert ? 'Alarm bearbeiten' : 'Neuer Alarm'"
      modal
      :style="{ width: '90vw', maxWidth: '600px' }"
    >
        <form id="alert-form" @submit.prevent="saveAlert" class="space-y-4">

          <!-- Template Selection -->
          <div v-if="!editingAlert" class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
             <label class="block text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">Vorlage laden (Optional)</label>
             <select @change="loadTemplate($event)" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-sm">
               <option value="">-- Vorlage auswählen --</option>
               <option v-for="t in templates" :key="t.name" :value="t.name">
                 {{ t.name }} - {{ t.description }}
               </option>
             </select>
             <p class="mt-1 text-xs text-blue-800 dark:text-blue-200">
               Wähle eine Vorlage, um die Felder automatisch auszufüllen.
             </p>
          </div>

          <!-- Name -->
          <div>
            <label for="alert-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
            <input id="alert-name" type="text" v-model="form.name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
          </div>

          <!-- Type -->
          <div>
            <label for="alert-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Typ</label>
            <select id="alert-type" v-model="form.type" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option value="threshold">Grenzwert-Alarm</option>
              <option value="status">Statusbericht</option>
            </select>
          </div>

          <!-- Sensor Config (Threshold only) -->
          <div v-if="form.type === 'threshold'" class="space-y-4 border-l-4 border-blue-500 pl-4 py-2 bg-gray-50 dark:bg-gray-900">
            <div>
              <label for="alert-sensor" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Sensor</label>
              <select id="alert-sensor" v-model="form.sensor" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                <option v-for="s in sensors" :key="s.name" :value="s.name">{{ s.name }} ({{ s.unit }})</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="alert-condition" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Bedingung</label>
                <select id="alert-condition" v-model="form.condition" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                  <option value=">">Größer als (&gt;)</option>
                  <option value="<">Kleiner als (&lt;)</option>
                  <option value="=">Gleich (=)</option>
                  <option value="!=">Ungleich (!=)</option>
                </select>
              </div>
              <div>
                <label for="alert-threshold" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Schwellenwert</label>
                <input id="alert-threshold" type="text" v-model="form.threshold" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              </div>
            </div>
          </div>

          <!-- Interval -->
          <div>
            <label for="alert-interval" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ form.type === 'status' ? 'Sende-Intervall (Sekunden)' : 'Cooldown / Sperrzeit (Sekunden)' }}
            </label>
            <input id="alert-interval" type="number" v-model="form.interval_seconds" min="0" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <p class="mt-1 text-xs text-gray-500">
              {{ form.type === 'status' ? 'Wie oft soll der Status gesendet werden (z.B. 86400 für täglich).' : 'Wie lange soll nach einem Alarm gewartet werden, bis erneut gesendet wird.' }}
            </p>
          </div>

          <!-- Message -->
          <div>
            <label for="alert-message" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Nachricht (Anpassbar)</label>
            <textarea id="alert-message" v-model="form.message" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white" placeholder="Gib hier deine individuelle Nachricht ein..."></textarea>
            <p class="mt-1 text-xs text-gray-500">
              Du kannst diesen Text bearbeiten. Verfügbare Platzhalter: {value}, {sensor}, {name}, {time}
            </p>
          </div>
        </form>

        <template #footer>
            <Button label="Abbrechen" icon="pi pi-times" text severity="secondary" @click="closeModal" />
            <Button label="Speichern" icon="pi pi-check" severity="primary" type="submit" form="alert-form" />
        </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

const alerts = ref([]);
const sensors = ref([]);
const templates = ref([]);
const loading = ref(true);
const showModal = ref(false);
const editingAlert = ref(null);
const toast = useToast();
const confirm = useConfirm();

const form = ref({
  name: '',
  type: 'threshold',
  sensor: '',
  condition: '>',
  threshold: '',
  message: 'Alarm: {name} - {sensor} ist {value} um {time}',
  interval_seconds: 3600,
  enabled: true
});

onMounted(async () => {
  await fetchSensors();
  await fetchAlerts();
  await fetchTemplates();
});

async function fetchTemplates() {
  try {
    const response = await axios.get('/api/alerts/templates');
    templates.value = response.data;
  } catch (e) {
    console.error("Failed to load templates", e);
  }
}

async function fetchSensors() {
  try {
    const response = await axios.get('/api/control'); // Reuse control endpoint to get sensors
    sensors.value = response.data;
  } catch (e) {
    console.error("Failed to load sensors", e);
  }
}

async function fetchAlerts() {
  loading.value = true;
  try {
    const response = await axios.get('/api/alerts');
    alerts.value = response.data;
  } catch (e) {
    console.error("Failed to load alerts", e);
  } finally {
    loading.value = false;
  }
}

function openModal(alert = null) {
  if (alert) {
    editingAlert.value = alert;
    form.value = { ...alert };
  } else {
    editingAlert.value = null;
    form.value = {
      name: '',
      type: 'threshold',
      sensor: sensors.value.length > 0 ? sensors.value[0].name : '',
      condition: '>',
      threshold: '',
      message: 'Alarm: {name} - {sensor} ist {value} um {time}',
      interval_seconds: 3600,
      enabled: true
    };
  }
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingAlert.value = null;
}

function loadTemplate(event) {
  const tName = event.target.value;
  if (!tName) return;
  const template = templates.value.find(t => t.name === tName);
  if (template) {
    form.value = { ...form.value, ...template.alert_data };
    // Ensure enabled is true by default for templates
    form.value.enabled = true;
  }
  // Reset select
  event.target.value = "";
}

async function saveAlert() {
  try {
    if (editingAlert.value) {
      await axios.put('/api/alerts', { id: editingAlert.value.id, ...form.value });
      toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Alarm aktualisiert', life: 3000 });
    } else {
      await axios.post('/api/alerts', form.value);
      toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Alarm erstellt', life: 3000 });
    }
    await fetchAlerts();
    closeModal();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
  }
}

const deleteAlert = (alert) => {
  confirm.require({
    message: `Alarm "${alert.name}" wirklich löschen?`,
    header: 'Bestätigung',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await axios.delete(`/api/alerts?id=${alert.id}`);
        toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Alarm gelöscht', life: 3000 });
        await fetchAlerts();
      } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Fehler beim Löschen', life: 5000 });
      }
    }
  });
};

async function toggleAlert(alert) {
  try {
    await axios.put('/api/alerts', { id: alert.id, enabled: !alert.enabled });
    toast.add({ severity: 'success', summary: 'Erfolg', detail: `Alarm ${alert.enabled ? 'deaktiviert' : 'aktiviert'}`, life: 2000 });
    await fetchAlerts();
  } catch (e) {
    console.error("Failed to toggle alert", e);
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'Status konnte nicht geändert werden', life: 3000 });
  }
}

function formatInterval(seconds) {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds/60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds/3600)}h`;
  return `${Math.floor(seconds/86400)}d`;
}
</script>
