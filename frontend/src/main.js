// Xerolux 2026
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import 'primeicons/primeicons.css'

import App from './App.vue'
import router from './router'
import './style.css'
import './utils/chartConfig'

import de from './locales/de.json'
import en from './locales/en.json'

const i18n = createI18n({
  legacy: false, // use Composition API
  locale: 'de',
  fallbackLocale: 'en',
  messages: {
    de,
    en
  }
})

const app = createApp(App)

app.config.errorHandler = (err, instance, info) => {
  // Log to console for debugging but avoid leaking internals to the UI
  console.error('Unhandled Vue error:', err, info)
  // Try to show a toast if the app is mounted far enough
  try {
    const toast = instance?.$.appContext?.config?.globalProperties?.$toast
    if (toast) {
      toast.add({
        severity: 'error',
        summary: 'Anwendungsfehler',
        detail: 'Ein unerwarteter Fehler ist aufgetreten. Bitte Seite neu laden.',
        life: 5000
      })
    }
  } catch {
    // ignore
  }
}

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.my-app-dark'
    }
  }
})
app.use(ToastService)
app.use(ConfirmationService)

window.addEventListener('unhandledrejection', (event) => {
  // Prevent unhandled promise rejections from flooding the console with stack traces
  // that may contain internal paths. The api interceptor already surfaces user-safe messages.
  if (
    event.reason?.message?.includes('Netzwerkfehler') ||
    event.reason?.message?.includes('Zeitüberschreitung')
  ) {
    event.preventDefault()
  }
})

app.mount('#app')
