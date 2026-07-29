<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Datenschutz & Lizenzbedingungen"
    :style="{ width: '50vw' }"
    :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
  >
    <div class="flex flex-col gap-6 text-sm text-gray-100">
      <!-- Privacy Policy -->
      <section>
        <h3 class="font-bold text-lg mb-2 text-white">Datenschutzerklärung</h3>
        <p class="mb-2">
          Wir nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Diese Software sammelt Daten
          ausschließlich zum Zweck der Überwachung, Analyse und Optimierung Ihrer Wärmepumpenanlage.
        </p>

        <h4 class="font-bold mt-3 mb-1">1. Datenerfassung</h4>
        <p class="mb-2">
          <strong>Installation ID:</strong> Bei der Ersteinrichtung wird eine zufällige
          "Installation ID" (UUID) generiert. Diese dient ausschließlich dazu, Ihre Installation
          technisch zu identifizieren (z.B. bei Support-Anfragen oder beim Teilen von Logs). Sie ist
          nicht mit personenbezogenen Daten (wie Name, Adresse) verknüpft.
        </p>
        <p class="mb-2">
          <strong>Wärmepumpen-Daten:</strong> Es werden technische Messwerte (Temperaturen, Drücke,
          Status) Ihrer IDM Wärmepumpe lokal in einer Datenbank (VictoriaMetrics) gespeichert.
        </p>

        <h4 class="font-bold mt-3 mb-1">2. Datenübermittlung</h4>
        <p class="mb-2">
          Standardmäßig verbleiben alle Daten <strong>lokal auf Ihrem System</strong>. Eine
          Übermittlung an Dritte erfolgt nur durch Ihre explizite Handlung (z.B. Nutzung der "Share
          Log" Funktion).
        </p>
        <p class="mb-2">
          Wenn Sie Logs teilen ("Share Log"), werden ausgewählte Log-Daten sowie Ihre Installation
          ID und das Wärmepumpen-Modell temporär an einen Paste-Service (MicroBin) gesendet, um
          einen Link zum Teilen zu generieren.
        </p>

        <h4 class="font-bold mt-3 mb-1">3. Lokale KI</h4>
        <p class="mb-2">
          Die Anomalie-Erkennung wird vom lokalen ML-Dienst ausgeführt. Messdaten, trainierte
          Modelle und Analyseergebnisse bleiben in Ihrer Installation und werden nicht an einen
          zentralen Telemetrie- oder Modellserver übertragen.
        </p>
        <ul class="list-disc ml-5 mb-2 space-y-1">
          <li><strong>Training:</strong> Verwendet ausschließlich Ihre lokal gespeicherten Werte.</li>
          <li><strong>Kontrolle:</strong> Die KI kann jederzeit in den Einstellungen deaktiviert werden.</li>
          <li><strong>Netzwerk:</strong> Die lokale KI benötigt keine Internetverbindung.</li>
        </ul>
      </section>

      <!-- License -->
      <section class="border-t border-gray-700 pt-4">
        <h3 class="font-bold text-lg mb-2 text-white">Lizenzvereinbarung</h3>
        <div class="bg-blue-900/30 p-3 rounded border border-blue-700 mb-4">
          <p class="font-medium text-blue-100">
            Diese Software unterliegt einem Dual-Lizenz-Modell.
          </p>
        </div>

        <h4 class="font-bold mt-3 mb-1">Privatnutzung (Open Source)</h4>
        <p class="mb-2">
          Für die private, nicht-kommerzielle Nutzung ist diese Software
          <strong>kostenlos</strong> und quelloffen unter den Bedingungen der
          <strong>MIT Lizenz</strong> verfügbar. Sie dürfen den Code einsehen, modifizieren und für
          eigene Zwecke nutzen.
        </p>

        <h4 class="font-bold mt-3 mb-1">Kommerzielle Nutzung</h4>
        <p class="mb-2">
          Jegliche gewerbliche oder kommerzielle Nutzung (z.B. durch Heizungsbauer, Energieberater,
          Service-Anbieter) ist <strong>nicht gestattet</strong> ohne eine gültige kommerzielle
          Lizenz. Bitte kontaktieren Sie uns für eine Lizenzierung.
        </p>
      </section>
    </div>

    <template #footer>
      <Button
        label="Schließen"
        icon="pi pi-times"
        @click="visible = false"
        text
        severity="secondary"
      />
    </template>
  </Dialog>
</template>

<script setup>
// Xerolux 2026
import { ref, defineExpose } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const visible = ref(false)

const open = () => {
  visible.value = true
}

const close = () => {
  visible.value = false
}

defineExpose({
  open,
  close
})
</script>
