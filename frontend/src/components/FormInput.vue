<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  min: {
    type: Number,
    default: null
  },
  max: {
    type: Number,
    default: null
  },
  step: {
    type: String,
    default: 'any'
  },
  helpText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isValid = computed(() => {
  if (props.error) return false
  if (props.required && !inputValue.value) return false
  if (props.type === 'number' && inputValue.value !== '') {
    const num = parseFloat(inputValue.value)
    if (isNaN(num)) return false
    if (props.min !== null && num < props.min) return false
    if (props.max !== null && num > props.max) return false
  }
  return true
})

const inputClasses = computed(() => {
  const classes = [
    'w-full px-3 py-2 rounded-md border transition-all duration-200 focus:outline-none focus:ring-2',
    'bg-gray-700 border-gray-600 text-white placeholder-gray-400',
    'focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-30'
  ]

  if (!isValid.value) {
    classes.push('border-error-500 focus:border-error-500 focus:ring-error-500')
  }

  if (props.disabled) {
    classes.push('opacity-50 cursor-not-allowed')
  }

  return classes.join(' ')
})
</script>

<template>
  <div class="space-y-2">
    <label
      v-if="label"
      :class="['text-sm font-medium', !isValid ? 'text-error-400' : 'text-gray-300']"
    >
      {{ label }}
      <span v-if="required" class="text-error-400">*</span>
    </label>

    <input
      :type="type"
      :value="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :min="min"
      :max="max"
      :step="step"
      :class="inputClasses"
      @input="inputValue = $event.target.value"
      @blur="emit('blur')"
      @focus="emit('focus')"
    />

    <div v-if="error" class="text-xs text-error-400 flex items-center gap-1">
      <i class="pi pi-exclamation-circle"></i>
      {{ error }}
    </div>

    <div v-else-if="helpText" class="text-xs text-gray-400">
      {{ helpText }}
    </div>

    <div v-if="type === 'number' && (min !== null || max !== null)" class="text-xs text-gray-500">
      Bereich: {{ min ?? '-∞' }} bis {{ max ?? '+∞' }}
    </div>
  </div>
</template>
