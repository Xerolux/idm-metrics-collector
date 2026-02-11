// Xerolux 2026
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import 'primeicons/primeicons.css'

import App from './App.vue'
import router from './router'
import './style.css'

import de from './locales/de.json'
import en from './locales/en.json'
import fr from './locales/fr.json'
import it from './locales/it.json'
import es from './locales/es.json'
import nl from './locales/nl.json'
import pl from './locales/pl.json'
import cs from './locales/cs.json'
import no from './locales/no.json'
import sv from './locales/sv.json'

const i18n = createI18n({
  legacy: false, // use Composition API
  locale: 'de',
  fallbackLocale: 'en',
  messages: {
    de,
    en,
    fr,
    it,
    es,
    nl,
    pl,
    cs,
    no,
    sv
  }
})

const app = createApp(App)

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

app.mount('#app')
