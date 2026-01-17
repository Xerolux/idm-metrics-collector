<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Password from 'primevue/password';
import Button from 'primevue/button';
import AppFooter from '../components/AppFooter.vue';
import ErrorDisplay from '../components/ErrorDisplay.vue';

const password = ref('');
const error = ref('');
const touched = ref(false);
const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);

const passwordError = computed(() => {
  if (!password.value) return 'Passwort ist erforderlich';
  if (password.value.length < 1) return 'Passwort ist zu kurz';
  return '';
});

const showPasswordError = computed(() => {
  return touched.value && passwordError.value;
});

const isValid = computed(() => {
  return password.value && !passwordError.value;
});

const handleLogin = async () => {
    touched.value = true;
    if (!isValid.value) {
        error.value = 'Bitte geben Sie ein gültiges Passwort ein';
        return;
    }

    loading.value = true;
    error.value = '';
    const success = await auth.login(password.value);
    loading.value = false;
    if (success) {
        router.push('/');
    } else {
        error.value = 'Ungültiges Passwort';
    }
};
</script>

<template>
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-900 p-3 sm:p-4">
        <Card class="w-full max-w-sm sm:max-w-md bg-gray-800 border-gray-700 text-white mb-auto mt-auto shadow-semantic-lg">
            <template #title>idm-metrics-collector</template>
            <template #content>
                <div class="flex flex-col gap-4">
                    <div class="flex flex-col gap-2">
                        <label for="password" class="text-sm font-medium text-gray-300">Passwort</label>
                        <Password
                            inputId="password"
                            v-model="password" 
                            placeholder="Passwort eingeben"
                            :inputClass="{ 'border-error-500': showPasswordError, 'border-gray-600': !showPasswordError }"
                            toggleMask
                            :feedback="false"
                            fluid
                            @blur="touched = true"
                            @keyup.enter="handleLogin"
                        />
                        <div v-if="showPasswordError" class="text-xs text-error-400 flex items-center gap-1">
                            <i class="pi pi-exclamation-circle"></i>
                            {{ passwordError }}
                        </div>
                    </div>
                    <ErrorDisplay v-if="error" :error="error" @dismiss="error = null" />
                    <Button 
                        label="Login" 
                        @click="handleLogin" 
                        :loading="loading" 
                        :disabled="!isValid"
                        class="w-full"
                    />
                </div>
            </template>
        </Card>
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
