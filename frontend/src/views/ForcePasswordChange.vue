<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-900 text-slate-200">
    <div class="w-full max-w-md p-8 space-y-6 bg-slate-800 rounded-lg shadow-xl border border-slate-700">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-red-500 mb-2">Sicherheitswarnung</h1>
        <p class="text-slate-400">
          Sie verwenden noch das Standardpasswort. Bitte ändern Sie es sofort, um fortzufahren.
        </p>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-slate-300">Neues Passwort</label>
          <Password v-model="password" toggleMask class="w-full" :feedback="true" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-slate-300">Passwort bestätigen</label>
          <Password v-model="confirmPassword" toggleMask class="w-full" :feedback="false" />
        </div>

        <div v-if="error" class="p-3 bg-red-900/50 border border-red-500/50 rounded text-red-200 text-sm">
          {{ error }}
        </div>

        <Button label="Passwort ändern" @click="changePassword" :loading="loading" class="w-full" severity="danger" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

const changePassword = async () => {
  if (password.value.length < 6) {
    error.value = 'Passwort muss mindestens 6 Zeichen lang sein'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwörter stimmen nicht überein'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const res = await axios.post('/api/config', {
      new_password: password.value
    })

    if (res.data.success) {
      // Refresh auth status
      await authStore.checkAuth()
      if (!authStore.mustChangePassword) {
         router.push('/')
      } else {
         error.value = 'Fehler beim Aktualisieren des Status'
      }
    } else {
      error.value = res.data.error || 'Fehler beim Ändern des Passworts'
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Verbindungsfehler'
  } finally {
    loading.value = false
  }
}
</script>
