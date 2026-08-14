<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Custom CSS"
    :style="{ width: '90vw', maxWidth: '800px' }"
  >
    <div class="space-y-4">
      <!-- Info -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div class="flex items-start gap-2">
          <i class="pi pi-info-circle text-blue-600 mt-0.5"></i>
          <div class="text-sm text-blue-800">
            <p class="font-medium mb-1">Custom CSS für dieses Dashboard</p>
            <p class="text-xs">
              CSS wird automatisch auf alle Elemente dieses Dashboards angewendet (scoped). Verwende
              Sie normale CSS-Selektoren.
            </p>
          </div>
        </div>
      </div>

      <!-- Examples -->
      <details class="bg-gray-50 rounded-lg p-3">
        <summary class="cursor-pointer text-sm font-medium text-gray-700 mb-2">
          Beispiele anzeigen
        </summary>
        <div class="mt-2 space-y-2 text-xs">
          <div>
            <strong>Hintergrundfarbe ändern:</strong>
            <pre class="bg-white p-2 rounded mt-1 overflow-x-auto">
.dashboard-container { background: #f0f9ff; }</pre
            >
          </div>
          <div>
            <strong>Chart-Titel anpassen:</strong>
            <pre class="bg-white p-2 rounded mt-1 overflow-x-auto">
.chart-title { font-size: 18px; color: #1e40af; }</pre
            >
          </div>
          <div>
            <strong>Border entfernen:</strong>
            <pre class="bg-white p-2 rounded mt-1 overflow-x-auto">
.chart-card { border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }</pre
            >
          </div>
        </div>
      </details>

      <!-- CSS Editor -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"> CSS Code </label>
        <Textarea
          v-model="localCss"
          rows="20"
          class="w-full font-mono text-sm"
          placeholder="/* Custom CSS hier einfügen */
.dashboard-container {
    /* Your styles here */
}"
          :class="{ 'border-red-500': hasErrors }"
        />
        <div v-if="hasErrors" class="mt-2 text-sm text-red-600">
          <i class="pi pi-exclamation-triangle mr-1"></i>
          {{ errorMessage }}
        </div>
      </div>

      <!-- Classes Reference -->
      <details class="bg-gray-50 rounded-lg p-3">
        <summary class="cursor-pointer text-sm font-medium text-gray-700 mb-2">
          Verfügbare CSS-Klassen
        </summary>
        <div class="mt-2 text-xs space-y-1">
          <div><code>.dashboard-container</code> - Dashboard Container</div>
          <div><code>.chart-card</code> - Einzelne Chart-Karte</div>
          <div><code>.chart-title</code> - Chart-Titel</div>
          <div><code>.chart-stats</code> - Statistik-Tabelle</div>
          <div><code>.overview-header</code> - Übersicht-Header</div>
        </div>
      </details>
    </div>

    <template #footer>
      <Button @click="visible = false" label="Abbrechen" severity="secondary" text />
      <Button @click="handleClear" label="Löschen" severity="danger" text v-if="localCss" />
      <Button @click="handleSave" label="Speichern" severity="primary" />
    </template>
  </Dialog>
</template>

<script setup>
// Xerolux 2026
import { ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { sanitizeCss, validateCss, hasDangerousPatterns } from '@/utils/cssSanitizer'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  css: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'save'])

const visible = ref(props.modelValue)
const localCss = ref(props.css || '')
const appliedCss = ref(props.css || '')
const securityWarnings = ref([])

const hasErrors = computed(() => {
  if (!localCss.value.trim()) {
    return false
  }

  // Validate CSS syntax
  const { valid } = validateCss(localCss.value)
  if (!valid) {
    return true
  }

  // Check for dangerous patterns
  if (hasDangerousPatterns(localCss.value)) {
    return true
  }

  return false
})

const errorMessage = computed(() => {
  if (!localCss.value.trim()) {
    return ''
  }

  // Check syntax
  const { errors } = validateCss(localCss.value)
  if (errors.length > 0) {
    return errors[0]
  }

  // Check for dangerous patterns
  if (hasDangerousPatterns(localCss.value)) {
    return 'CSS enthält nicht erlaubte Muster (z.B. @import, expression, javascript:)'
  }

  return ''
})

const handleSave = () => {
  if (hasErrors.value) {
    return
  }

  // Sanitize CSS before saving
  const { sanitized, warnings, blocked } = sanitizeCss(localCss.value)
  securityWarnings.value = [...warnings, ...blocked]

  appliedCss.value = sanitized
  emit('save', sanitized)
  visible.value = false
}

const handleClear = () => {
  localCss.value = ''
  appliedCss.value = ''
  emit('save', '')
  visible.value = false
}

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
    if (val) {
      localCss.value = props.css || ''
    }
  }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
})
</script>

<style scoped>
pre {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
