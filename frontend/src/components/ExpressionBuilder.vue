<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Math-Ausdruck erstellen"
    :style="{ width: '90vw', maxWidth: '700px' }"
  >
    <div class="space-y-4">
      <!-- Expression Input -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Ausdruck</label>
        <div class="flex gap-2">
          <InputText
            v-model="expression"
            placeholder="z.B. A/B, A*100, (A+B)/2"
            class="flex-grow font-mono"
            @input="validateExpression"
          />
          <Button
            @click="showHelp = true"
            icon="pi pi-question-circle"
            severity="secondary"
            text
            title="Hilfe anzeigen"
            aria-label="Hilfe anzeigen"
          />
        </div>
        <p v-if="validationError" class="text-xs text-red-500 mt-1">{{ validationError }}</p>
        <p v-else-if="parsedQueries.length > 0" class="text-xs text-gray-500 mt-1">
          Verwendete Queries: <span class="font-mono">{{ parsedQueries.join(', ') }}</span>
        </p>
      </div>

      <!-- Quick Actions -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Schnell-Aktionen</label>
        <div class="flex flex-wrap gap-2">
          <Button
            @click="insertOperator('+')"
            label="+"
            size="small"
            severity="secondary"
            outlined
          />
          <Button
            @click="insertOperator('-')"
            label="-"
            size="small"
            severity="secondary"
            outlined
          />
          <Button
            @click="insertOperator('*')"
            label="*"
            size="small"
            severity="secondary"
            outlined
          />
          <Button
            @click="insertOperator('/')"
            label="/"
            size="small"
            severity="secondary"
            outlined
          />
          <Button
            @click="insertOperator('(')"
            label="("
            size="small"
            severity="secondary"
            outlined
          />
          <Button
            @click="insertOperator(')')"
            label=")"
            size="small"
            severity="secondary"
            outlined
          />
        </div>
      </div>

      <!-- Query Insert -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Query einfügen</label>
        <div class="flex flex-wrap gap-2">
          <Button
            v-for="query in availableQueries"
            :key="query.label"
            @click="insertQuery(query.label)"
            :label="query.label"
            size="small"
            :severity="isSelected(query.label) ? 'primary' : 'secondary'"
            outlined
          />
        </div>
        <p class="text-xs text-gray-500 mt-1">Klicke auf einen Query, um ihn einzufügen</p>
      </div>

      <!-- Functions -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Funktionen</label>
        <div class="grid grid-cols-2 gap-2">
          <Button
            @click="insertFunction('avg')"
            label="avg(A,B)"
            size="small"
            severity="secondary"
            outlined
            class="text-left"
          />
          <Button
            @click="insertFunction('sum')"
            label="sum(A,B)"
            size="small"
            severity="secondary"
            outlined
            class="text-left"
          />
          <Button
            @click="insertFunction('min')"
            label="min(A,B)"
            size="small"
            severity="secondary"
            outlined
            class="text-left"
          />
          <Button
            @click="insertFunction('max')"
            label="max(A,B)"
            size="small"
            severity="secondary"
            outlined
            class="text-left"
          />
        </div>
      </div>

      <!-- Examples -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Beispiele</label>
        <div class="space-y-1">
          <div
            v-for="example in examples"
            :key="example.expression"
            @click="expression = example.expression"
            class="p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100 flex justify-between items-center"
          >
            <span class="font-mono text-sm">{{ example.expression }}</span>
            <span class="text-xs text-gray-500">{{ example.description }}</span>
          </div>
        </div>
      </div>

      <!-- Preview -->
      <div
        v-if="expression && !validationError"
        class="p-3 bg-blue-50 rounded border border-blue-200"
      >
        <div class="text-sm">
          <span class="font-medium text-blue-900">Vorschau:</span>
          <span class="ml-2 font-mono text-blue-700">{{ expression }}</span>
        </div>
        <div class="text-xs text-blue-600 mt-1">
          Berechnet: {{ expression }} für jeden Zeitstempel
        </div>
      </div>
    </div>

    <template #footer>
      <Button @click="visible = false" label="Abbrechen" severity="secondary" text />
      <Button
        @click="save"
        label="Speichern"
        severity="primary"
        :disabled="!!validationError || !expression"
      />
    </template>
  </Dialog>

  <!-- Help Dialog -->
  <Dialog
    v-model:visible="showHelp"
    modal
    header="Hilfe: Math-Ausdrücke"
    :style="{ width: '90vw', maxWidth: '600px' }"
  >
    <div class="space-y-4 text-sm">
      <div>
        <h4 class="font-medium text-gray-900 mb-2">Operatoren</h4>
        <ul class="list-disc list-inside space-y-1 text-gray-700">
          <li><code class="font-mono bg-gray-100 px-1 rounded">+</code> Addition (A + B)</li>
          <li><code class="font-mono bg-gray-100 px-1 rounded">-</code> Subtraktion (A - B)</li>
          <li>
            <code class="font-mono bg-gray-100 px-1 rounded">*</code> Multiplikation (A * 100)
          </li>
          <li><code class="font-mono bg-gray-100 px-1 rounded">/</code> Division (A / B)</li>
          <li><code class="font-mono bg-gray-100 px-1 rounded">()</code> Klammern ((A + B) / 2)</li>
        </ul>
      </div>

      <div>
        <h4 class="font-medium text-gray-900 mb-2">Funktionen</h4>
        <ul class="list-disc list-inside space-y-1 text-gray-700">
          <li>
            <code class="font-mono bg-gray-100 px-1 rounded">avg(A,B,C)</code> Durchschnitt von
            mehreren Queries
          </li>
          <li>
            <code class="font-mono bg-gray-100 px-1 rounded">sum(A,B)</code> Summe von mehreren
            Queries
          </li>
          <li>
            <code class="font-mono bg-gray-100 px-1 rounded">min(A,B)</code> Minimum von mehreren
            Queries
          </li>
          <li>
            <code class="font-mono bg-gray-100 px-1 rounded">max(A,B)</code> Maximum von mehreren
            Queries
          </li>
        </ul>
      </div>

      <div>
        <h4 class="font-medium text-gray-900 mb-2">Beispiele</h4>
        <div class="space-y-1">
          <div class="p-2 bg-gray-50 rounded font-mono text-xs">
            A/B <span class="text-gray-500">- A durch B teilen</span>
          </div>
          <div class="p-2 bg-gray-50 rounded font-mono text-xs">
            A*100 <span class="text-gray-500">- A mit 100 multiplizieren</span>
          </div>
          <div class="p-2 bg-gray-50 rounded font-mono text-xs">
            (A+B)/2 <span class="text-gray-500">- Durchschnitt von A und B</span>
          </div>
          <div class="p-2 bg-gray-50 rounded font-mono text-xs">
            avg(A,B,C) <span class="text-gray-500">- Durchschnitt von A, B, C</span>
          </div>
          <div class="p-2 bg-gray-50 rounded font-mono text-xs">
            (A-B)*100/B <span class="text-gray-500">- Prozentsatz</span>
          </div>
        </div>
      </div>

      <div class="p-3 bg-yellow-50 rounded border border-yellow-200">
        <p class="text-yellow-800 text-xs">
          <strong>Hinweis:</strong> Query-Labels sind Großbuchstaben (A, B, C, etc.). Division durch
          Null gibt <code>null</code> zurück.
        </p>
      </div>
    </div>

    <template #footer>
      <Button @click="showHelp = false" label="Schließen" severity="primary" />
    </template>
  </Dialog>
</template>

<script setup>
// Xerolux 2026
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import {
  validateExpression,
  parseExpression,
  getExpressionExamples
} from '../utils/expressionParser.js'

const props = defineProps({
  currentExpression: {
    type: String,
    default: ''
  },
  availableQueries: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['save'])

const visible = ref(false)
const showHelp = ref(false)
const expression = ref('')
const validationError = ref('')

const examples = getExpressionExamples()

const parsedQueries = computed(() => {
  if (!expression.value) return []
  return parseExpression(expression.value)
})

const open = () => {
  expression.value = props.currentExpression
  validateExpr()
  visible.value = true
}

const validateExpr = () => {
  if (!expression.value) {
    validationError.value = ''
    return
  }

  const result = validateExpression(expression.value)
  validationError.value = result.error
}

const insertOperator = (op) => {
  expression.value += op
  validateExpr()
}

const insertQuery = (label) => {
  expression.value += label
  validateExpr()
}

const insertFunction = (func) => {
  expression.value += `${func}()`
  // Move cursor inside parentheses
  validateExpr()
}

const isSelected = (label) => {
  return parsedQueries.value.includes(label)
}

const save = () => {
  if (validationError.value || !expression.value) {
    return
  }
  emit('save', expression.value)
  visible.value = false
}

watch(expression, () => {
  validateExpression()
})

defineExpose({ open })
</script>
