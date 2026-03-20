<script setup>
// Xerolux 2026
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import AppFooter from '../components/AppFooter.vue'
import ErrorDisplay from '../components/ErrorDisplay.vue'
import Dialog from 'primevue/dialog'
import api from '../utils/api'

const password = ref('')
const error = ref('')
const touched = ref(false)
const showPassword = ref(false)
const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)

const showPasswordChangeDialog = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const isChangingPassword = ref(false)
const passwordChangeError = ref('')

const showReset = ref(false)
const resetHost = ref('')
const resetPort = ref('502')
const resetNewPassword = ref('')
const resetError = ref('')
const resetSuccess = ref('')
const isResetting = ref(false)

const passwordError = computed(() => {
  if (!password.value) return 'Passwort ist erforderlich'
  return ''
})

const showPasswordError = computed(() => {
  return touched.value && passwordError.value
})

const isValid = computed(() => {
  return password.value && !passwordError.value
})

const handleLogin = async () => {
  touched.value = true
  if (!isValid.value) {
    error.value = 'Bitte geben Sie ein gültiges Passwort ein'
    return
  }

  loading.value = true
  error.value = ''
  const response = await auth.login(password.value)
  loading.value = false
  if (response.success) {
    if (response.requiresPasswordChange) {
      showPasswordChangeDialog.value = true
    } else {
      router.push('/')
    }
  } else {
    error.value = 'Ungültiges Passwort'
  }
}

const handlePasswordChange = async () => {
  passwordChangeError.value = ''

  if (newPassword.value.length < 6) {
    passwordChangeError.value = 'Passwort muss mindestens 6 Zeichen lang sein'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    passwordChangeError.value = 'Passwörter stimmen nicht überein'
    return
  }

  isChangingPassword.value = true
  try {
    await api.post('/api/auth/change_password', {
      new_password: newPassword.value
    })

    showPasswordChangeDialog.value = false
    router.push('/')
  } catch (err) {
    passwordChangeError.value = err.response?.data?.message || err.message || 'Fehler beim Passwortwechsel'
  } finally {
    isChangingPassword.value = false
  }
}

const handleReset = async () => {
  resetError.value = ''
  resetSuccess.value = ''

  if (!resetHost.value || !resetPort.value || !resetNewPassword.value) {
    resetError.value = 'Bitte alle Felder ausfüllen'
    return
  }

  if (resetNewPassword.value.length < 6) {
    resetError.value = 'Passwort muss mindestens 6 Zeichen lang sein'
    return
  }

  isResetting.value = true
  try {
    const res = await api.post('/api/auth/reset_password', {
      idm_host: resetHost.value,
      idm_port: parseInt(resetPort.value),
      new_password: resetNewPassword.value
    })
    if (res.data.success) {
      resetSuccess.value = 'Passwort erfolgreich zurückgesetzt!'
      setTimeout(() => {
        showReset.value = false
        resetSuccess.value = ''
        resetHost.value = ''
        resetPort.value = '502'
        resetNewPassword.value = ''
      }, 2500)
    } else {
      resetError.value = res.data.message || 'Fehler beim Zurücksetzen'
    }
  } catch (err) {
    resetError.value = err.response?.data?.message || err.message || 'Fehler beim Zurücksetzen'
  } finally {
    isResetting.value = false
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-900 p-3 sm:p-4">
    <Card
      class="w-full max-w-sm sm:max-w-md bg-gray-800 border-gray-700 text-white mb-auto mt-auto shadow-semantic-lg"
    >
      <template #title>idm-metrics-collector</template>
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <label for="password" class="text-sm font-medium text-white">Passwort</label>
            <div class="p-inputgroup w-full">
              <InputText
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Passwort eingeben"
                :class="{
                  'border-error-500': showPasswordError,
                  'border-gray-600': !showPasswordError
                }"
                :aria-invalid="!!showPasswordError"
                aria-describedby="password-error"
                @blur="touched = true"
                @keyup.enter="handleLogin"
              />
              <Button
                :icon="showPassword ? 'pi pi-eye-slash' : 'pi pi-eye'"
                severity="secondary"
                type="button"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Passwort verbergen' : 'Passwort anzeigen'"
              />
            </div>
            <div
              id="password-error"
              v-if="showPasswordError"
              class="text-xs text-error-400 flex items-center gap-1"
              role="alert"
            >
              <i class="pi pi-exclamation-circle"></i>
              {{ passwordError }}
            </div>
          </div>
          <ErrorDisplay v-if="error" :error="error" @dismiss="error = null" />
          <template v-if="!showReset">
            <Button
              label="Login"
              @click="handleLogin"
              :loading="loading"
              :disabled="!isValid"
              class="w-full"
            />
            <div class="text-center mt-2">
              <a href="#" @click.prevent="showReset = true" class="text-sm text-blue-400 hover:text-blue-300">
                Passwort vergessen?
              </a>
            </div>
          </template>

          <template v-else>
            <div class="flex flex-col gap-3">
              <p class="text-sm text-gray-300">
                Geben Sie zur Sicherheit die IP/Host und den Port Ihrer konfigurierten IDM-Anlage ein.
              </p>
              <div class="flex flex-col gap-1">
                <label for="resetHost" class="text-xs font-medium text-white">IDM Host / IP</label>
                <InputText id="resetHost" v-model="resetHost" placeholder="z.B. 192.168.1.10" />
              </div>
              <div class="flex flex-col gap-1">
                <label for="resetPort" class="text-xs font-medium text-white">IDM Port</label>
                <InputText id="resetPort" v-model="resetPort" placeholder="502" />
              </div>
              <div class="flex flex-col gap-1">
                <label for="resetNewPassword" class="text-xs font-medium text-white">Neues Passwort</label>
                <InputText id="resetNewPassword" v-model="resetNewPassword" type="password" placeholder="Min. 6 Zeichen" />
              </div>

              <ErrorDisplay v-if="resetError" :error="resetError" @dismiss="resetError = null" />
              <div v-if="resetSuccess" class="text-green-400 text-sm mb-2 text-center">
                <i class="pi pi-check-circle mr-1"></i>{{ resetSuccess }}
              </div>

              <div class="flex justify-between gap-2 mt-2">
                <Button label="Abbrechen" severity="secondary" @click="showReset = false" class="w-1/2" />
                <Button label="Zurücksetzen" @click="handleReset" :loading="isResetting" class="w-1/2" />
              </div>
            </div>
          </template>
        </div>
      </template>
    </Card>

    <Dialog
      v-model:visible="showPasswordChangeDialog"
      modal
      header="Sicherheitsupdate erforderlich"
      :style="{ width: '25rem' }"
      :closable="false"
    >
      <p class="text-gray-300 mb-4">
        Bitte ändern Sie das Standardpasswort in ein neues, sicheres Passwort (mindestens 6 Zeichen).
      </p>
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label for="newPassword" class="text-sm font-medium text-white">Neues Passwort</label>
          <InputText
            id="newPassword"
            v-model="newPassword"
            type="password"
            placeholder="Min. 6 Zeichen"
            @keyup.enter="handlePasswordChange"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label for="confirmPassword" class="text-sm font-medium text-white">Passwort bestätigen</label>
          <InputText
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Passwort wiederholen"
            @keyup.enter="handlePasswordChange"
          />
        </div>
        <ErrorDisplay v-if="passwordChangeError" :error="passwordChangeError" @dismiss="passwordChangeError = null" />
      </div>
      <template #footer>
        <Button
          label="Passwort speichern"
          icon="pi pi-check"
          @click="handlePasswordChange"
          :loading="isChangingPassword"
        />
      </template>
    </Dialog>

    <AppFooter />
  </div>
</template>

<style scoped>
:deep(.p-card) {
  background: #1f2937;
  color: white;
}
:deep(.p-inputtext) {
  background: #374151;
  border-color: #4b5563;
  color: white;
}
</style>
