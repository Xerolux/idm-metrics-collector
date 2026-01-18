<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Object],
    required: true
  },
  options: {
    type: Array,
    required: true
  },
  optionLabel: {
    type: String,
    default: 'label'
  },
  optionValue: {
    type: String,
    default: 'value'
  },
  label: {
    type: String,
    default: ''
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
  filter: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isValid = computed(() => {
  if (props.error) return false
  if (props.required && !selectedValue.value) return false
  return true
})

const inputClasses = computed(() => {
  const classes = [
    'w-full px-3 py-2 rounded-md border transition-all duration-200 focus:outline-none focus:ring-2',
    'bg-gray-700 border-gray-600 text-white',
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

    <select
      :value="selectedValue"
      :disabled="disabled"
      :class="inputClasses"
      @change="selectedValue = $event.target.value"
    >
      <option value="" disabled>{{ placeholder || 'Bitte wählen...' }}</option>
      <option v-for="option in options" :key="option[optionValue]" :value="option[optionValue]">
        {{ option[optionLabel] }}
      </option>
    </select>

    <div v-if="error" class="text-xs text-error-400 flex items-center gap-1">
      <i class="pi pi-exclamation-circle"></i>
      {{ error }}
    </div>
  </div>
</template>
