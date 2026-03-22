<template>
  <TableConfigDialog :table="table" v-model:visible="visible" @save="onSave" />
</template>

<script setup>
import { ref } from 'vue'
import TableConfigDialog from '@/components/TableConfigDialog.vue'

const visible = ref(true)
const table = ref({
  title: 'Test Table',
  queries: [{ label: 'Q1', query: 'metric1' }],
  hours: 24,
  columns: [{ key: 'time', label: 'Time', type: 'timestamp' }]
})

const onSave = () => {
  console.log('Saved')
}
</script>
