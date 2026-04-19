<template>
  <div class="p-4 flex flex-col gap-4 h-[calc(100vh-2rem)] overflow-hidden glass-panel rounded-2xl">
    <h1 class="text-2xl font-bold mb-2 flex-shrink-0">Konfiguration</h1>

    <div v-if="loading" class="flex justify-center items-center h-full">
      <i class="pi pi-spin pi-spinner text-4xl"></i>
    </div>

    <div v-else class="flex flex-col lg:flex-row gap-6 h-full overflow-hidden">
      <!-- Navigation (Sidebar on Desktop, Top Scrollbar on Mobile) -->
      <div
        class="w-full lg:w-64 flex-shrink-0 flex flex-row lg:flex-col gap-2 overflow-x-auto lg:overflow-y-auto lg:overflow-visible pr-2 pb-2 lg:pb-20"
      >
        <!-- Sidebar Navigation -->
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="activeCategory = cat.id"
          class="flex items-center gap-3 p-3 rounded-lg text-left transition-colors whitespace-nowrap"
          :class="
            activeCategory === cat.id
              ? 'bg-primary-500 text-white shadow-lg'
              : 'bg-surface-800 text-surface-200 hover:bg-surface-700'
          "
        >
          <i :class="cat.icon" class="text-lg"></i>
          <span class="font-medium">{{ cat.label }}</span>
        </button>
      </div>

      <!-- Main Content Area -->
      <div
        class="flex-grow bg-surface-900 rounded-xl border border-surface-700 overflow-hidden flex flex-col"
      >
        <div class="p-6 overflow-y-auto flex-grow">
          <!-- Verbindung -->
          <div v-if="activeCategory === 'connection'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2 text-gray-100">
              Verbindung & Daten
            </h2>

            <Fieldset legend="IDM Wärmepumpe" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Installation</label>
                  <div class="flex items-center gap-2">
                    <div class="p-inputgroup flex-1">
                      <span class="p-inputgroup-addon">ID</span>
                      <InputText
                        v-model="config.installation_id"
                        readonly
                        class="w-full font-mono bg-gray-800"
                        aria-label="Installation ID"
                      />
                      <Button
                        icon="pi pi-copy"
                        severity="secondary"
                        @click="copyId"
                        aria-label="Installation ID kopieren"
                      />
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Modell</label>
                    <Dropdown
                      v-model="config.hp_model"
                      :options="models"
                      optionLabel="label"
                      optionValue="value"
                      placeholder="Modell wählen"
                      class="w-full"
                      filter
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Hersteller</label>
                    <InputText :value="config.hp_manufacturer || 'IDM'" disabled class="w-full" />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Host / IP</label>
                    <InputText v-model="config.idm.host" class="w-full" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Port</label>
                    <InputNumber v-model="config.idm.port" :useGrouping="false" class="w-full" />
                  </div>
                </div>

                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Aktivierte Heizkreise</label>
                  <div
                    class="flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"
                  >
                    <div class="flex items-center gap-2">
                      <Checkbox
                        v-model="config.idm.circuits"
                        inputId="circuitA"
                        value="A"
                        disabled
                      />
                      <label for="circuitA" class="opacity-50">Heizkreis A (Fest)</label>
                    </div>
                    <div
                      v-for="c in ['B', 'C', 'D', 'E', 'F', 'G']"
                      :key="c"
                      class="flex items-center gap-2"
                    >
                      <Checkbox v-model="config.idm.circuits" :inputId="'circuit' + c" :value="c" />
                      <label :for="'circuit' + c" class="text-gray-300">Heizkreis {{ c }}</label>
                    </div>
                  </div>
                </div>

                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Zonenmodule</label>
                  <div
                    class="flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"
                  >
                    <div v-for="z in 10" :key="z" class="flex items-center gap-2">
                      <Checkbox
                        v-model="config.idm.zones"
                        :inputId="'zone' + (z - 1)"
                        :value="z - 1"
                      />
                      <label :for="'zone' + (z - 1)" class="text-gray-300">Zone {{ z }}</label>
                    </div>
                  </div>
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="Datenbank (VictoriaMetrics)" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Write URL</label>
                  <InputText v-model="config.metrics.url" class="w-full" />
                  <small class="text-gray-300">Standard: http://victoriametrics:8428/write</small>
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="Datenerfassung" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex items-center gap-2 p-3 bg-gray-800 rounded border border-gray-700">
                  <Checkbox v-model="config.logging.realtime_mode" binary inputId="realtime_mode" />
                  <div class="flex flex-col">
                    <label for="realtime_mode" class="font-bold cursor-pointer"
                      >Echtzeit-Modus</label
                    >
                    <span class="text-sm text-gray-300"
                      >Aktualisierung im Sekundentakt (Hohe Last)</span
                    >
                  </div>
                </div>
                <div class="flex flex-col gap-2" v-if="!config.logging.realtime_mode">
                  <label class="font-bold text-sm text-gray-300"
                    >Abfrage-Intervall (Sekunden)</label
                  >
                  <InputNumber
                    v-model="config.logging.interval"
                    :min="1"
                    :max="3600"
                    :useGrouping="false"
                    class="w-full md:w-1/2"
                  />
                  <small class="text-gray-300">Standard: 60 Sekunden</small>
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="Community Daten & Telemetrie" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.telemetry.enabled" binary inputId="telemetry_enabled" />
                  <label for="telemetry_enabled" class="font-bold cursor-pointer"
                    >Community Modell nutzen</label
                  >
                </div>
              </template>

              <div v-if="config.telemetry.enabled" class="flex flex-col gap-6">
                <div
                  class="bg-purple-900/20 border border-purple-600/50 p-4 rounded flex flex-col gap-3"
                >
                  <div class="flex items-start gap-3">
                    <i class="pi pi-users text-purple-400 text-xl mt-1"></i>
                    <div class="text-sm text-purple-200">
                      Durch die Teilnahme am Community-Programm hilfst du, das
                      Anomalie-Erkennungsmodell für alle zu verbessern. Deine Daten werden
                      anonymisiert (IP-Masking) übertragen.
                      <br /><br />
                      <strong>Vorteil:</strong> Du erhältst Zugriff auf vortrainierte Modelle
                      ("Community Model"), die auf Daten vieler Wärmepumpen basieren. Dies ist
                      besonders hilfreich, wenn du noch nicht genügend eigene Daten (weniger als 1
                      Woche) hast.
                    </div>
                  </div>
                  <div class="flex justify-end">
                    <Button
                      label="Datenschutz-Details"
                      icon="pi pi-shield"
                      size="small"
                      text
                      @click="privacyDialog.open()"
                    />
                  </div>
                </div>

                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Telemetry Server URL</label>
                  <InputText
                    v-model="config.telemetry.server_url"
                    class="w-full font-mono"
                    placeholder="https://collector.xerolux.de"
                  />
                  <small class="text-gray-400"
                    >Standard: https://collector.xerolux.de – Nur ändern wenn du einen eigenen
                    Server betreibst.</small
                  >
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Client Token</label>
                    <InputText
                      v-model="config.telemetry.auth_token"
                      class="w-full font-mono"
                      type="password"
                      placeholder="Wird automatisch gesetzt"
                    />
                    <small class="text-gray-400">Für Upload und Modell-Checks.</small>
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Admin Token (optional)</label>
                    <InputText
                      v-model="config.telemetry.admin_auth_token"
                      class="w-full font-mono"
                      type="password"
                      placeholder="Nur für Admin-Endpunkte"
                    />
                    <small class="text-gray-400"
                      >Wird bevorzugt für Admin-Zone genutzt, falls gesetzt.</small
                    >
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <Button
                    label="Token automatisch abrufen"
                    icon="pi pi-key"
                    size="small"
                    severity="secondary"
                    @click="retrieveTelemetryCredentials"
                  />
                </div>

                <!-- Admin Status Indicator -->
                <div class="flex items-center gap-2" v-if="telemetryStatus">
                  <span class="font-bold text-sm text-gray-300">Status:</span>
                  <span
                    v-if="telemetryStatus.is_banned"
                    class="px-2 py-0.5 rounded bg-red-500/20 text-red-500 border border-red-500/50 text-xs font-bold uppercase"
                  >
                    <i class="pi pi-ban mr-1"></i> BANNED
                  </span>
                  <span
                    v-if="telemetryStatus.is_admin"
                    class="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-500 border border-yellow-500/50 text-xs font-bold uppercase"
                  >
                    <i class="pi pi-crown mr-1"></i> Admin
                  </span>
                  <span
                    v-else-if="telemetryStatus.role"
                    :class="
                      getRoleBadgeClass(telemetryStatus.role) +
                      ' px-2 py-0.5 rounded border border-white/20 text-xs font-bold uppercase'
                    "
                  >
                    <i class="pi pi-user mr-1"></i> {{ telemetryStatus.role }}
                  </span>
                  <span
                    v-else
                    class="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/50 text-xs font-bold uppercase"
                  >
                    <i class="pi pi-user mr-1"></i> Client
                  </span>
                </div>

                <div class="bg-gray-800 p-4 rounded border border-gray-700 mt-2">
                  <h4 class="font-bold text-lg mb-2 flex items-center gap-2">
                    <i class="pi pi-cloud"></i> Telemetrie Status
                  </h4>
                  <div v-if="telemetryStatus" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Server (Verbunden):</span>
                      <span class="font-mono truncate max-w-[150px]">{{
                        telemetryStatus.server_url
                      }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Letzte Übertragung:</span>
                      <span class="font-mono">{{
                        telemetryStatus.last_submission
                          ? new Date(telemetryStatus.last_submission * 1000).toLocaleString()
                          : 'Nie'
                      }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Letzter Modell-Check:</span>
                      <span class="font-mono">{{
                        telemetryStatus.last_model_check
                          ? new Date(telemetryStatus.last_model_check * 1000).toLocaleString()
                          : 'Nie'
                      }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Manuelle Downloads heute:</span>
                      <span class="font-mono"
                        >{{ telemetryStatus.manual_downloads_today }} / 3</span
                      >
                    </div>
                  </div>
                  <div class="flex flex-wrap gap-2 mt-4">
                    <Button
                      label="Daten jetzt senden"
                      icon="pi pi-upload"
                      size="small"
                      severity="secondary"
                      @click="manualSubmitTelemetry"
                      :loading="submittingTelemetry"
                    />
                    <Button
                      label="Modell prüfen & laden"
                      icon="pi pi-download"
                      size="small"
                      severity="help"
                      @click="manualCheckModel"
                      :loading="checkingModel"
                      :disabled="telemetryStatus?.manual_downloads_today >= 3"
                    />
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>

          <!-- MQTT -->
          <div v-if="activeCategory === 'mqtt'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2 text-gray-100">
              MQTT & Integration
            </h2>

            <Fieldset legend="MQTT Publishing" :toggleable="false">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.mqtt.enabled" binary inputId="mqtt_enabled" />
                  <span class="font-bold text-lg">MQTT Aktivieren</span>
                </div>
              </template>

              <div v-if="config.mqtt.enabled" class="flex flex-col gap-6 mt-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Broker Adresse</label>
                    <InputText
                      v-model="config.mqtt.broker"
                      placeholder="mqtt.example.com"
                      class="w-full"
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Port</label>
                    <InputNumber
                      v-model="config.mqtt.port"
                      :useGrouping="false"
                      :min="1"
                      :max="65535"
                      class="w-full"
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Benutzername</label>
                    <InputText
                      v-model="config.mqtt.username"
                      placeholder="Optional"
                      class="w-full"
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Passwort</label>
                    <InputText
                      v-model="mqttPassword"
                      type="password"
                      placeholder="••••••"
                      class="w-full"
                    />
                  </div>
                </div>

                <div class="border-t border-gray-700 pt-4">
                  <div class="flex items-center gap-2 mb-3">
                    <Checkbox v-model="config.mqtt.use_tls" binary inputId="mqtt_tls" />
                    <label for="mqtt_tls" class="font-bold cursor-pointer"
                      >TLS/SSL Verschlüsselung</label
                    >
                  </div>
                  <div v-if="config.mqtt.use_tls" class="ml-8 mb-4">
                    <div class="flex flex-col gap-2">
                      <label class="text-sm">CA-Zertifikat Pfad (optional)</label>
                      <InputText
                        v-model="config.mqtt.tls_ca_cert"
                        placeholder="/path/to/ca.crt"
                        class="w-full"
                      />
                      <small class="text-gray-300"
                        >Für selbst-signierte Zertifikate. Leer lassen für System-CA.</small
                      >
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 pt-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Topic Präfix</label>
                    <InputText v-model="config.mqtt.topic_prefix" class="w-full" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">QoS Level</label>
                    <SelectButton
                      v-model="config.mqtt.qos"
                      :options="[0, 1, 2]"
                      aria-labelledby="basic"
                      class="w-full"
                    />
                  </div>
                </div>

                <div
                  class="flex flex-col gap-3 border border-green-600/50 rounded bg-green-900/10 p-4"
                >
                  <div class="flex items-center gap-2">
                    <Checkbox
                      v-model="config.mqtt.ha_discovery_enabled"
                      binary
                      inputId="ha_discovery"
                    />
                    <label for="ha_discovery" class="font-bold text-green-400 cursor-pointer"
                      >Home Assistant Auto-Discovery</label
                    >
                  </div>
                  <div v-if="config.mqtt.ha_discovery_enabled" class="ml-8">
                    <label class="text-sm">Discovery Präfix</label>
                    <InputText v-model="config.mqtt.ha_discovery_prefix" class="w-full mt-1" />
                  </div>
                </div>
              </div>
              <div v-else class="text-gray-300 italic">
                Aktivieren Sie MQTT, um Daten an Broker wie Mosquitto oder Home Assistant zu senden.
              </div>
            </Fieldset>
          </div>

          <!-- Benachrichtigungen -->
          <div v-if="activeCategory === 'notifications'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2 text-gray-100">
              Benachrichtigungen
            </h2>

            <Fieldset legend="Signal Messenger" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.signal.enabled" binary inputId="signal_enabled" />
                  <label for="signal_enabled" class="font-bold cursor-pointer">Signal</label>
                </div>
              </template>

              <div v-if="config.signal.enabled" class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Sender Nummer</label>
                  <InputText
                    v-model="config.signal.sender"
                    placeholder="+49..."
                    class="w-full md:w-1/2"
                  />
                </div>
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300"
                    >Empfänger (Pro Zeile eine Nummer)</label
                  >
                  <Textarea v-model="signalRecipientsText" rows="3" class="w-full font-mono" />
                </div>
                <div class="flex flex-col gap-2 border-t border-gray-700 pt-4 mt-2">
                  <label class="text-sm font-bold">Erweitert</label>
                  <div class="flex flex-col gap-2">
                    <label class="text-xs">Signal CLI Pfad</label>
                    <InputText
                      v-model="config.signal.cli_path"
                      placeholder="signal-cli"
                      class="w-full md:w-1/2"
                    />
                    <small class="text-gray-300">Standard: signal-cli (im PATH)</small>
                  </div>
                </div>
                <Button
                  label="Testnachricht senden"
                  icon="pi pi-send"
                  severity="success"
                  outlined
                  @click="sendSignalTest"
                  class="w-full md:w-auto self-start"
                />
              </div>
            </Fieldset>

            <Fieldset legend="Telegram" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.telegram.enabled" binary inputId="telegram_enabled" />
                  <label for="telegram_enabled" class="font-bold cursor-pointer">Telegram</label>
                </div>
              </template>
              <div v-if="config.telegram.enabled" class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Bot Token</label>
                  <InputText
                    v-model="config.telegram.bot_token"
                    type="password"
                    class="w-full md:w-1/2"
                  />
                </div>
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Chat IDs (Kommagetrennt)</label>
                  <InputText v-model="telegramChatIdsText" class="w-full md:w-1/2" />
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="Discord" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.discord.enabled" binary inputId="discord_enabled" />
                  <label for="discord_enabled" class="font-bold cursor-pointer">Discord</label>
                </div>
              </template>
              <div v-if="config.discord.enabled" class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Webhook URL</label>
                  <InputText v-model="config.discord.webhook_url" type="password" class="w-full" />
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="E-Mail" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.email.enabled" binary inputId="email_enabled" />
                  <label for="email_enabled" class="font-bold cursor-pointer">E-Mail</label>
                </div>
              </template>
              <div v-if="config.email.enabled" class="flex flex-col gap-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">SMTP Server</label>
                    <InputText v-model="config.email.smtp_server" class="w-full" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Port</label>
                    <InputNumber
                      v-model="config.email.smtp_port"
                      :useGrouping="false"
                      class="w-full"
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Benutzername</label>
                    <InputText v-model="config.email.username" class="w-full" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Passwort</label>
                    <InputText v-model="emailPassword" type="password" class="w-full" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Absender Adresse</label>
                    <InputText v-model="config.email.sender" class="w-full" />
                  </div>
                </div>
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Empfänger (Kommagetrennt)</label>
                  <InputText v-model="emailRecipientsText" class="w-full" />
                </div>
              </div>
            </Fieldset>
          </div>

          <!-- AI -->
          <div v-if="activeCategory === 'ai'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2 text-gray-100">
              KI-Analyse
            </h2>

            <Fieldset legend="KI & Anomalieerkennung" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.ai.enabled" binary inputId="ai_enabled" />
                  <label for="ai_enabled" class="font-bold cursor-pointer"
                    >KI-Analyse Status anzeigen</label
                  >
                </div>
              </template>
              <div v-if="config.ai.enabled" class="flex flex-col gap-6">
                <div
                  class="bg-blue-900/20 border border-blue-600/50 p-4 rounded flex items-start gap-3"
                >
                  <i class="pi pi-info-circle text-blue-400 text-xl mt-1"></i>
                  <div class="text-sm text-blue-200">
                    Die Anomalieerkennung läuft nun als eigenständiger
                    <strong>ml-service</strong> Container. Er nutzt einen PyTorch
                    <code>Autoencoder</code>, um kontinuierlich aus dem Datenstrom zu lernen.
                    Anomalien werden über den Rekonstruktionsfehler erkannt.
                  </div>
                </div>

                <div class="bg-gray-800 p-4 rounded border border-gray-700 mt-4">
                  <div class="flex flex-col gap-4">
                    <div class="flex flex-col gap-2">
                      <label class="font-bold text-sm text-gray-300">KI-Modell</label>
                      <Dropdown
                        v-model="config.ai.model"
                        :options="[
                          {
                            label: 'Rolling Window (Lokal, kontinuierliches Lernen)',
                            value: 'rolling'
                          },
                          {
                            label: 'Community Modell (Vortrainiert, für neue Installationen)',
                            value: 'community'
                          }
                        ]"
                        optionLabel="label"
                        optionValue="value"
                        class="w-full"
                      />
                      <small class="text-gray-400">
                        <strong>Rolling:</strong> Lernt kontinuierlich aus deinen eigenen Daten.
                        <strong>Community:</strong> Nutzt das vortrainierte Modell vom Server.
                      </small>
                    </div>
                    <div class="flex flex-col gap-2">
                      <label class="font-bold text-sm text-gray-300">Empfindlichkeit (0-10)</label>
                      <div class="flex flex-col sm:flex-row sm:items-center gap-2">
                        <InputNumber
                          v-model="config.ai.sensitivity"
                          :min="0"
                          :max="10"
                          :minFractionDigits="2"
                          :maxFractionDigits="2"
                          :step="0.1"
                          showButtons
                          buttonLayout="horizontal"
                          decrementButtonIcon="pi pi-minus"
                          incrementButtonIcon="pi pi-plus"
                          class="w-full sm:w-40"
                        />
                        <span class="text-sm text-gray-400 italic">Empfehlung: 3.0 (Standard)</span>
                      </div>
                      <div class="text-xs text-gray-500 mt-1">
                        0 = Sehr geringe Empfindlichkeit (Weniger Alarme) – 10 = Sehr hohe
                        Empfindlichkeit (Mehr Alarme).
                      </div>
                    </div>
                  </div>
                </div>

                <div class="bg-gray-800 p-4 rounded border border-gray-700 mt-4">
                  <h4 class="font-bold text-lg mb-2 flex items-center gap-2">
                    <i class="pi pi-chart-line"></i> Service Status
                  </h4>
                  <div v-if="aiStatus" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Service:</span>
                      <span class="font-mono">{{ aiStatus.service || 'Unbekannt' }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Status:</span>
                      <span
                        class="font-bold"
                        :class="aiStatus.online ? 'text-green-400' : 'text-red-400'"
                      >
                        {{ aiStatus.online ? 'Online' : 'Offline / Keine Daten' }}
                      </span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Letzter Score:</span>
                      <span class="font-mono text-lg">{{
                        aiStatus.score ? aiStatus.score.toFixed(4) : '0.0000'
                      }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Aktuelle Anomalie:</span>
                      <span
                        class="font-bold"
                        :class="aiStatus.is_anomaly ? 'text-red-500' : 'text-green-500'"
                      >
                        {{ aiStatus.is_anomaly ? 'JA' : 'NEIN' }}
                      </span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Letztes Update:</span>
                      <span class="font-mono">{{
                        aiStatus.last_update
                          ? new Date(aiStatus.last_update * 1000).toLocaleString()
                          : '-'
                      }}</span>
                    </div>
                  </div>
                  <div v-else class="text-center py-4 text-gray-500">
                    <i class="pi pi-spin pi-spinner mr-2"></i> Lade Status...
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>

          <!-- Security -->
          <div v-if="activeCategory === 'security'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2 text-gray-100">
              Sicherheit
            </h2>

            <Fieldset legend="Webzugriff" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Admin Passwort</label>
                  <Button
                    label="Passwort ändern"
                    icon="pi pi-key"
                    severity="secondary"
                    outlined
                    class="w-full md:w-auto self-start"
                    @click="showPasswordDialog = true"
                  />
                </div>
                <div class="flex items-center gap-2 mt-2">
                  <Checkbox v-model="config.web.write_enabled" binary inputId="write_access" />
                  <div class="flex flex-col">
                    <label for="write_access" class="font-bold cursor-pointer"
                      >Schreibzugriff erlauben</label
                    >
                    <span class="text-sm text-gray-300"
                      >Erforderlich für manuelle Steuerung und Zeitpläne</span
                    >
                  </div>
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="Netzwerk Firewall" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox
                    v-model="config.network_security.enabled"
                    binary
                    inputId="network_security_enabled"
                  />
                  <label for="network_security_enabled" class="font-bold cursor-pointer"
                    >IP Whitelist/Blacklist</label
                  >
                </div>
              </template>

              <div v-if="config.network_security.enabled" class="flex flex-col gap-4">
                <div
                  class="bg-yellow-900/20 border border-yellow-600/50 p-3 rounded text-yellow-200 text-sm flex items-start gap-2"
                >
                  <i class="pi pi-exclamation-triangle mt-0.5"></i>
                  <span
                    >Deine IP ist <strong>{{ currentClientIP }}</strong
                    >. Füge diese zur Whitelist hinzu, sonst sperrst du dich aus!</span
                  >
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-green-400">Whitelist (Erlaubt)</label>
                    <Textarea
                      v-model="whitelistText"
                      rows="5"
                      class="w-full font-mono text-sm"
                      placeholder="192.168.1.0/24"
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-red-400">Blacklist (Blockiert)</label>
                    <Textarea
                      v-model="blacklistText"
                      rows="5"
                      class="w-full font-mono text-sm"
                      placeholder="1.2.3.4"
                    />
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>

          <!-- System -->
          <div v-if="activeCategory === 'system'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2 text-gray-100">
              System & Wartung
            </h2>

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <!-- Update Status -->
              <div
                data-update-section
                class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"
              >
                <h3 class="font-bold text-lg flex items-center gap-2">
                  <i class="pi pi-refresh"></i> Update Status
                </h3>
                <div class="flex items-center justify-between bg-gray-900/50 p-3 rounded">
                  <div>
                    <div class="text-sm text-gray-100 font-medium">Installierte Version</div>
                    <div class="font-mono text-white font-semibold">
                      {{ updateStatus.current_version || 'v0.0.0' }}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm text-gray-100 font-medium">Verfügbare Version</div>
                    <div class="font-mono text-green-400 font-semibold">
                      {{ updateStatus.latest_version || 'Checking...' }}
                    </div>
                  </div>
                </div>

                <!-- Docker Image Status -->
                <div v-if="updateStatus.docker" class="bg-gray-900/50 p-3 rounded mt-2">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-box text-blue-400"></i>
                    <span class="text-sm font-bold text-white">Docker Images</span>
                    <span
                      v-if="updateStatus.docker.updates_available"
                      class="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full font-semibold"
                      >Updates verfügbar</span
                    >
                  </div>
                  <div class="grid grid-cols-1 gap-2 text-xs">
                    <div
                      v-for="(img, name) in updateStatus.docker.images"
                      :key="name"
                      class="flex items-center justify-between p-2 rounded"
                      :class="
                        img.update_available
                          ? 'bg-blue-900/30 border border-blue-600/50'
                          : 'bg-gray-800'
                      "
                    >
                      <div class="flex items-center gap-2">
                        <i
                          :class="
                            img.update_available
                              ? 'pi pi-arrow-up text-blue-400'
                              : 'pi pi-check text-green-400'
                          "
                        ></i>
                        <span class="font-mono text-white font-semibold">{{ name }}</span>
                      </div>
                      <div class="text-right">
                        <span v-if="img.update_available" class="text-blue-300 font-semibold"
                          >Update verfügbar</span
                        >
                        <span v-else class="text-green-400 font-semibold">Aktuell</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Update Available Info -->
                <div
                  v-if="updateStatus.update_available"
                  class="bg-blue-900/20 border border-blue-600/50 p-3 rounded mt-2 flex flex-col gap-2"
                >
                  <div class="flex items-center gap-2 text-blue-300 text-sm font-semibold">
                    <i class="pi pi-info-circle"></i>
                    <span>Neue Version verfügbar!</span>
                  </div>
                  <p class="text-sm text-gray-100">
                    Automatische Updates sind deaktiviert. Bitte führen Sie das Update manuell
                    durch.
                  </p>
                </div>

                <!-- Update Info -->
                <div class="bg-gray-900/50 p-3 rounded mt-2">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-sync text-green-400"></i>
                    <span class="text-sm font-bold text-white">Manuelle Updates</span>
                  </div>
                  <p class="text-sm text-gray-100 mb-2">
                    Es werden keine automatischen Updates mehr durchgeführt. Neue Versionen müssen
                    manuell über die Konsole installiert werden.
                  </p>
                  <Button
                    label="Anleitung anzeigen"
                    icon="pi pi-question-circle"
                    severity="secondary"
                    size="small"
                    text
                    @click="showUpdateHelpDialog = true"
                  />
                </div>

                <div class="flex justify-end mt-2">
                  <Button
                    label="Jetzt prüfen"
                    icon="pi pi-search"
                    size="small"
                    severity="secondary"
                    @click="checkUpdates"
                    :loading="checkingUpdates"
                  />
                </div>
              </div>

              <!-- Backup Actions -->
              <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3">
                <h3 class="font-bold text-lg flex items-center gap-2">
                  <i class="pi pi-database"></i> Backup
                </h3>
                <div class="flex flex-col gap-2 mb-2">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <Checkbox v-model="config.backup.enabled" binary inputId="auto_backup" />
                      <label for="auto_backup" class="font-bold text-sm text-white"
                        >Automatisches Backup</label
                      >
                    </div>
                  </div>
                  <div
                    v-if="config.backup.enabled"
                    class="grid grid-cols-2 gap-2 text-sm bg-gray-900/30 p-2 rounded"
                  >
                    <div class="flex flex-col">
                      <label class="text-sm text-gray-100 font-medium">Intervall (Std)</label>
                      <InputNumber
                        v-model="config.backup.interval"
                        :min="1"
                        :max="168"
                        class="p-inputtext-sm"
                      />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm text-gray-100 font-medium">Behalten (Anzahl)</label>
                      <InputNumber
                        v-model="config.backup.retention"
                        :min="1"
                        :max="50"
                        class="p-inputtext-sm"
                      />
                    </div>
                    <div class="col-span-2 flex items-center gap-2 mt-1">
                      <Checkbox
                        v-model="config.backup.auto_upload"
                        binary
                        inputId="backup_upload"
                        :disabled="!config.webdav.enabled"
                      />
                      <label
                        for="backup_upload"
                        class="text-sm text-gray-100 font-medium"
                        :class="{ 'opacity-50': !config.webdav.enabled }"
                        >Automatisch in Cloud hochladen</label
                      >
                    </div>
                  </div>
                </div>

                <div class="flex gap-2">
                  <Button
                    label="Backup erstellen"
                    icon="pi pi-download"
                    size="small"
                    @click="createBackup"
                    :loading="creatingBackup"
                  />
                  <Button
                    label="Backup hochladen"
                    icon="pi pi-upload"
                    size="small"
                    severity="secondary"
                    @click="$refs.fileInput.click()"
                  />
                  <input
                    type="file"
                    ref="fileInput"
                    class="hidden"
                    @change="handleFileSelect"
                    accept=".zip"
                  />
                </div>
                <Button
                  v-if="selectedFile"
                  label="Wiederherstellen starten"
                  severity="warning"
                  class="w-full mt-2"
                  @click="restoreFromFile"
                />

                <div class="mt-2 max-h-40 overflow-y-auto">
                  <div
                    v-for="backup in backups"
                    :key="backup.filename"
                    class="flex justify-between items-center p-2 hover:bg-gray-700 rounded text-sm border-b border-gray-700 last:border-0"
                  >
                    <span class="truncate text-white font-medium">{{ backup.filename }}</span>
                    <div class="flex gap-1">
                      <Button
                        icon="pi pi-cloud-upload"
                        text
                        size="small"
                        @click="uploadToCloud(backup.filename)"
                        title="Upload to WebDAV"
                        aria-label="Upload to WebDAV"
                      />
                      <Button
                        icon="pi pi-download"
                        text
                        size="small"
                        @click="downloadBackup(backup.filename)"
                        aria-label="Herunterladen"
                      />
                      <Button
                        icon="pi pi-trash"
                        text
                        severity="danger"
                        size="small"
                        @click="confirmDeleteBackup(backup.filename)"
                        aria-label="Löschen"
                      />
                    </div>
                  </div>
                </div>

                <div class="border-t border-gray-700 pt-3 mt-2">
                  <div class="flex items-center gap-2 mb-2">
                    <Checkbox v-model="config.webdav.enabled" binary inputId="webdav_enabled" />
                    <label for="webdav_enabled" class="font-bold text-white cursor-pointer"
                      >Cloud Backup (WebDAV/Nextcloud)</label
                    >
                  </div>
                  <div v-if="config.webdav.enabled" class="flex flex-col gap-2">
                    <div class="flex flex-col gap-1">
                      <label class="text-sm text-gray-100 font-medium">URL</label>
                      <InputText
                        v-model="config.webdav.url"
                        placeholder="https://cloud.example.com/remote.php/dav/files/user/"
                        class="p-inputtext-sm w-full"
                      />
                    </div>
                    <div class="flex flex-col gap-1">
                      <label class="text-sm text-gray-100 font-medium">Benutzername</label>
                      <InputText v-model="config.webdav.username" class="p-inputtext-sm w-full" />
                    </div>
                    <div class="flex flex-col gap-1">
                      <label class="text-sm text-gray-100 font-medium">Passwort</label>
                      <InputText
                        v-model="webdavPassword"
                        type="password"
                        class="p-inputtext-sm w-full"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Service Control -->
              <div
                class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3 xl:col-span-2"
              >
                <h3 class="font-bold text-lg flex items-center gap-2 text-red-400">
                  <i class="pi pi-power-off"></i> Danger Zone
                </h3>
                <div class="flex gap-4">
                  <Button
                    label="Dienst neu starten"
                    icon="pi pi-refresh"
                    severity="warning"
                    @click="confirmRestart"
                  />
                  <Button
                    label="Datenbank löschen"
                    icon="pi pi-trash"
                    severity="danger"
                    @click="showDeleteDialog = true"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Admin Zone -->
          <div v-if="activeCategory === 'admin'" class="flex flex-col gap-6">
            <div class="flex items-center justify-between border-b border-surface-700 pb-2 mb-2">
              <h2 class="text-xl font-bold flex items-center gap-2 text-gray-100">
                <i class="pi pi-crown text-yellow-500"></i> Admin Zone
              </h2>
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-400">Auto-Refresh (30s)</span>
                <Button
                  :icon="adminAutoRefresh ? 'pi pi-pause' : 'pi pi-play'"
                  :severity="adminAutoRefresh ? 'success' : 'secondary'"
                  size="small"
                  @click="toggleAdminAutoRefresh"
                  v-tooltip.top="adminAutoRefresh ? 'Pause Auto-Refresh' : 'Start Auto-Refresh'"
                  :aria-label="adminAutoRefresh ? 'Auto-Refresh pausieren' : 'Auto-Refresh starten'"
                />
              </div>
            </div>

            <div
              v-if="telemetryStatus?.server_stats"
              class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              <!-- Global Stats -->
              <div
                class="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col items-center transition-all duration-300 hover:border-blue-500"
              >
                <i class="pi pi-database text-4xl text-blue-400 mb-2"></i>
                <transition name="counter" mode="out-in">
                  <div :key="telemetryStatus.server_stats.total_points" class="text-3xl font-bold">
                    {{ telemetryStatus.server_stats.total_points?.toLocaleString() || 0 }}
                  </div>
                </transition>
                <div class="text-gray-300 uppercase text-xs tracking-wider mt-1">
                  Total Data Points
                </div>
              </div>

              <div
                class="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col items-center transition-all duration-300 hover:border-green-500"
              >
                <i class="pi pi-desktop text-4xl text-green-400 mb-2"></i>
                <transition name="counter" mode="out-in">
                  <div
                    :key="telemetryStatus.server_stats.active_installations"
                    class="text-3xl font-bold"
                  >
                    {{ telemetryStatus.server_stats.active_installations || 0 }}
                  </div>
                </transition>
                <div class="text-gray-300 uppercase text-xs tracking-wider mt-1">
                  Active Installations
                </div>
              </div>

              <div
                class="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col items-center transition-all duration-300 hover:border-purple-500"
              >
                <i class="pi pi-box text-4xl text-purple-400 mb-2"></i>
                <transition name="counter" mode="out-in">
                  <div
                    :key="telemetryStatus.server_stats.models?.length"
                    class="text-3xl font-bold"
                  >
                    {{ telemetryStatus.server_stats.models?.length || 0 }}
                  </div>
                </transition>
                <div class="text-gray-300 uppercase text-xs tracking-wider mt-1">
                  Generated Models
                </div>
              </div>
            </div>

            <!-- Installations List -->
            <Fieldset legend="Installation Management" :toggleable="true">
              <div class="flex justify-between items-center mb-3">
                <div class="text-sm text-gray-400" v-if="adminInstallations">
                  {{ adminInstallations.showing }} von {{ adminInstallations.total }} Installationen
                  angezeigt
                </div>
                <div class="text-sm text-gray-400" v-else-if="!adminInstallationsError">
                  Installationen werden geladen...
                </div>
                <Button
                  label="Aktualisieren"
                  icon="pi pi-refresh"
                  size="small"
                  severity="secondary"
                  @click="fetchAdminInstallations"
                />
              </div>

              <!-- Error State -->
              <div
                v-if="adminInstallationsError"
                class="text-center py-6 bg-red-900/20 border border-red-700/50 rounded mb-3"
              >
                <i class="pi pi-exclamation-triangle text-red-400 text-2xl mb-2 block"></i>
                <div class="text-red-300 font-medium">
                  Installationen konnten nicht geladen werden
                </div>
                <div class="text-red-400 text-xs mt-1 font-mono">{{ adminInstallationsError }}</div>
                <Button
                  label="Erneut versuchen"
                  icon="pi pi-refresh"
                  size="small"
                  severity="danger"
                  outlined
                  class="mt-3"
                  @click="fetchAdminInstallations"
                />
              </div>

              <div class="overflow-x-auto" v-if="adminInstallations">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-gray-700">
                      <th class="text-left py-2 px-3">Installation ID</th>
                      <th class="text-center py-2 px-3">Rolle</th>
                      <th class="text-center py-2 px-3">Status</th>
                      <th class="text-right py-2 px-3">Datenpunkte</th>
                      <th class="text-right py-2 px-3">Zuletzt gesehen</th>
                      <th class="text-center py-2 px-3">Aktionen</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="inst in adminInstallations.installations"
                      :key="inst.installation_id"
                      class="border-b border-gray-800 hover:bg-gray-800/50"
                    >
                      <td class="py-2 px-3 font-mono text-xs">
                        <button
                          @click="openInstallationDetails(inst.installation_id)"
                          class="text-blue-400 hover:text-blue-300 hover:underline text-left"
                          :title="inst.installation_id"
                        >
                          {{ inst.installation_id.substring(0, 20) }}...
                        </button>
                      </td>
                      <td class="py-2 px-3 text-center">
                        <span
                          :class="getRoleBadgeClass(getInstallationRole(inst.installation_id))"
                          class="px-2 py-1 rounded text-xs font-bold"
                        >
                          {{ getInstallationRole(inst.installation_id) }}
                        </span>
                      </td>
                      <td class="py-2 px-3 text-center">
                        <span
                          v-if="isInstallationBanned(inst.installation_id)"
                          class="px-2 py-1 rounded text-xs font-bold bg-red-600 text-white"
                        >
                          <i class="pi pi-ban mr-1"></i>GESPERRT
                        </span>
                        <span v-else class="text-green-400">
                          <i class="pi pi-check-circle"></i>
                        </span>
                      </td>
                      <td class="py-2 px-3 text-right">
                        {{ inst.data_points?.toLocaleString() || 0 }}
                      </td>
                      <td class="py-2 px-3 text-right text-xs">
                        {{ inst.last_seen_formatted || 'Unbekannt' }}
                      </td>
                      <td class="py-2 px-3 text-center">
                        <div class="flex gap-1 justify-center">
                          <Button
                            icon="pi pi-user-edit"
                            severity="info"
                            size="small"
                            outlined
                            @click="openRoleDialog(inst.installation_id)"
                            v-tooltip="'Rolle ändern'"
                            aria-label="Rolle ändern"
                          />
                          <Button
                            v-if="!isInstallationBanned(inst.installation_id)"
                            icon="pi pi-ban"
                            severity="danger"
                            size="small"
                            outlined
                            @click="openBanDialog(inst.installation_id)"
                            v-tooltip="'Sperren'"
                            aria-label="Sperren"
                          />
                          <Button
                            v-else
                            icon="pi pi-unlock"
                            severity="success"
                            size="small"
                            outlined
                            @click="unbanInstallation(inst.installation_id)"
                            v-tooltip="'Entsperren'"
                            aria-label="Entsperren"
                          />
                          <Button
                            icon="pi pi-eye"
                            severity="secondary"
                            size="small"
                            outlined
                            @click="openInstallationDetails(inst.installation_id)"
                            v-tooltip="'Details'"
                            aria-label="Details anzeigen"
                          />
                        </div>
                      </td>
                    </tr>
                    <tr v-if="adminInstallations.installations?.length === 0">
                      <td colspan="6" class="py-6 text-center text-gray-500 italic">
                        Keine Installationen gefunden
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div
                v-else-if="!adminInstallationsError"
                class="text-center py-8 text-gray-400 italic bg-gray-900/30 rounded border border-gray-800 border-dashed"
              >
                <i class="pi pi-spin pi-spinner mr-2"></i> Installationen werden geladen...
              </div>
            </Fieldset>

            <Fieldset legend="Available Models" :toggleable="true" v-if="adminModels">
              <div class="mb-3 text-sm text-gray-400">
                Showing {{ adminModels.total || 0 }} model(s), Total Size:
                {{ adminModels.models?.reduce((sum, m) => sum + m.size_mb, 0).toFixed(2) || 0 }} MB
              </div>
              <div class="grid grid-cols-1 gap-4">
                <div
                  v-for="model in adminModels.models"
                  :key="model.filename"
                  class="bg-gray-900/50 p-4 rounded border border-gray-700 flex justify-between items-center"
                >
                  <div class="flex flex-col">
                    <span class="font-bold text-lg">{{ model.name }}</span>
                    <div class="text-xs text-gray-400 mt-1">
                      <div>Modified: {{ model.modified_formatted }}</div>
                      <div class="font-mono">Hash: {{ model.hash?.substring(0, 16) }}...</div>
                      <div class="flex items-center gap-1 mt-1">
                        <i class="pi pi-download text-green-400"></i>
                        <span>Downloads: {{ model.download_count || 0 }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-4">
                    <div class="flex flex-col items-end">
                      <span class="font-mono text-blue-300">{{ model.size_mb }} MB</span>
                    </div>
                    <Button
                      icon="pi pi-trash"
                      severity="danger"
                      size="small"
                      :loading="modelDeleting"
                      @click="deleteModel(model.name)"
                      v-tooltip="'Modell löschen'"
                      aria-label="Modell löschen"
                    />
                  </div>
                </div>
                <div
                  v-if="!adminModels.models || !adminModels.models.length"
                  class="text-gray-500 italic text-center p-4"
                >
                  No models available yet. Models will be generated automatically when enough data
                  is collected.
                </div>
              </div>
            </Fieldset>

            <!-- Model Downloads Chart -->
            <Fieldset
              legend="Model Downloads"
              :toggleable="true"
              v-if="adminModels && adminModels.models?.some((m) => m.download_count > 0)"
            >
              <div class="mb-3 text-sm text-gray-400">Top 10 most downloaded models</div>
              <div class="bg-gray-900/50 p-4 rounded border border-gray-700" style="height: 300px">
                <canvas ref="modelDownloadsChart"></canvas>
              </div>
            </Fieldset>

            <!-- Server Health -->
            <Fieldset legend="Server Health" :toggleable="true" v-if="adminHealth">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-server text-blue-400"></i>
                    <span class="font-bold">Server</span>
                    <i
                      v-if="adminHealth.victoriametrics?.healthy"
                      class="pi pi-check-circle text-green-400 ml-auto"
                    ></i>
                    <i v-else class="pi pi-times-circle text-red-400 ml-auto"></i>
                  </div>
                  <div class="text-sm space-y-1">
                    <div class="flex justify-between">
                      <span class="text-gray-400">Hostname:</span>
                      <span>{{ adminHealth.server?.hostname || 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">Uptime:</span>
                      <span>{{ adminHealth.server?.uptime_formatted || 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">CPU:</span>
                      <span>{{ adminHealth.server?.cpu_percent?.toFixed(1) }}%</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">RAM:</span>
                      <span
                        >{{ adminHealth.server?.memory?.used_gb?.toFixed(1) }}GB /
                        {{ adminHealth.server?.memory?.total_gb?.toFixed(1) }}GB ({{
                          adminHealth.server?.memory?.percent
                        }}%)</span
                      >
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">Disk:</span>
                      <span
                        >{{ adminHealth.server?.disk?.used_gb?.toFixed(1) }}GB /
                        {{ adminHealth.server?.disk?.total_gb?.toFixed(1) }}GB ({{
                          adminHealth.server?.disk?.percent
                        }}%)</span
                      >
                    </div>
                  </div>
                </div>
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-database text-purple-400"></i>
                    <span class="font-bold">Models</span>
                  </div>
                  <div class="text-sm space-y-1">
                    <div class="flex justify-between">
                      <span class="text-gray-400">Count:</span>
                      <span>{{ adminHealth.models?.count || 0 }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">Total Size:</span>
                      <span>{{ adminHealth.models?.total_size_mb?.toFixed(2) }} MB</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">VictoriaMetrics:</span>
                      <span
                        :class="
                          adminHealth.victoriametrics?.healthy ? 'text-green-400' : 'text-red-400'
                        "
                        >{{ adminHealth.victoriametrics?.healthy ? 'Healthy' : 'Down' }}</span
                      >
                    </div>
                  </div>
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2">
                <Dropdown
                  v-model="trainingTargetModel"
                  :options="models"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Modell für Training (optional)"
                  class="w-full"
                  showClear
                />
                <InputText
                  v-model="trainingTargetInstallationId"
                  class="w-full font-mono"
                  placeholder="Installation ID (optional, Single-Device)"
                />
                <small class="text-gray-400 md:col-span-3">
                  Wenn eine Installation-ID gesetzt ist, wird gezielt mit diesem einen Gerät
                  trainiert.
                </small>
                <InputNumber
                  v-model="trainingMinPoints"
                  :useGrouping="false"
                  class="w-full"
                  placeholder="Min Points (optional)"
                />
                <InputNumber
                  v-model="trainingMinInstallations"
                  :useGrouping="false"
                  class="w-full"
                  placeholder="Min Installations (optional)"
                />
                <InputNumber
                  v-model="trainingLookbackDays"
                  :useGrouping="false"
                  class="w-full"
                  placeholder="Lookback Days (optional)"
                />
                <div class="md:col-span-3 flex items-center gap-2 mt-1">
                  <Checkbox v-model="trainingDryRun" binary inputId="trainingDryRun" />
                  <label for="trainingDryRun" class="text-sm text-gray-300 cursor-pointer">
                    Dry-Run (nur validieren, kein Training starten)
                  </label>
                </div>
              </div>
              <div class="flex gap-2 mt-2">
                <Button
                  label="Refresh Data"
                  icon="pi pi-refresh"
                  @click="
                    async () => {
                      await Promise.all([
                        fetchAdminModels(),
                        fetchAdminHealth(),
                        fetchAdminInstallations(),
                        fetchAdminMetrics(),
                        fetchRuntimeLimits()
                      ])
                    }
                  "
                  severity="secondary"
                  size="small"
                />
                <Button
                  label="Trigger Training"
                  icon="pi pi-play"
                  @click="triggerTraining"
                  :loading="trainingInProgress"
                  severity="success"
                  size="small"
                />
              </div>
            </Fieldset>

            <!-- System Metrics -->
            <Fieldset legend="System Metrics" :toggleable="true" v-if="adminMetrics">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Request Metrics -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-chart-line text-blue-400 text-xl"></i>
                    <span class="font-bold">Requests</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ adminMetrics.requests?.total?.toLocaleString() || 0 }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Total Requests</div>
                  <div class="text-xs text-red-400 mt-1">
                    {{ adminMetrics.requests?.errors || 0 }} Errors
                  </div>
                </div>

                <!-- Data Submissions -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-upload text-green-400 text-xl"></i>
                    <span class="font-bold">Submissions</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ adminMetrics.business?.submissions?.toLocaleString() || 0 }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Data Submissions</div>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ adminMetrics.business?.data_points?.toLocaleString() || 0 }} Points
                  </div>
                </div>

                <!-- Cache Performance -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-bolt text-yellow-400 text-xl"></i>
                    <span class="font-bold">Cache</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ adminMetrics.cache?.hit_rate?.toFixed(1) || 0 }}%
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Hit Rate</div>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ adminMetrics.cache?.hits?.toLocaleString() || 0 }} Hits /
                    {{ adminMetrics.cache?.misses?.toLocaleString() || 0 }} Misses
                  </div>
                </div>

                <!-- Rate Limits -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-ban text-red-400 text-xl"></i>
                    <span class="font-bold">Rate Limits</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ adminMetrics.requests?.rate_limit_hits?.toLocaleString() || 0 }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Total Violations</div>
                </div>

                <!-- Model Downloads -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-download text-purple-400 text-xl"></i>
                    <span class="font-bold">Downloads</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ adminMetrics.business?.model_downloads?.toLocaleString() || 0 }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Model Downloads</div>
                </div>

                <!-- Training Runs -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-cog text-cyan-400 text-xl"></i>
                    <span class="font-bold">Training</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ adminMetrics.business?.training_runs?.toLocaleString() || 0 }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Total Runs</div>
                </div>

                <!-- Active Installations (from metrics) -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-users text-teal-400 text-xl"></i>
                    <span class="font-bold">Installations</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{
                      adminMetrics.business?.active_installations?.toLocaleString() ||
                      telemetryStatus.server_stats?.active_installations ||
                      0
                    }}
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Active (30d)</div>
                </div>

                <!-- Error Rate -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-exclamation-triangle text-orange-400 text-xl"></i>
                    <span class="font-bold">Error Rate</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{
                      adminMetrics.requests?.total > 0
                        ? (
                            (adminMetrics.requests.errors / adminMetrics.requests.total) *
                            100
                          ).toFixed(2)
                        : 0
                    }}%
                  </div>
                  <div class="text-xs text-gray-400 mt-1">Errors / Requests</div>
                </div>
              </div>
            </Fieldset>

            <!-- Community Analysis -->
            <Fieldset legend="Community Data Analysis" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Target Model</label>
                    <Dropdown
                      v-model="selectedStatsModel"
                      :options="
                        adminModels?.models?.map((m) => m.name) || models.map((m) => m.value)
                      "
                      placeholder="Select Model"
                      class="w-full"
                      editable
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Metrics (comma separated)</label>
                    <InputText
                      v-model="statsMetrics"
                      placeholder="cop_current, temp_outdoor"
                      class="w-full"
                    />
                  </div>
                </div>

                <Button
                  label="Analyze Community Data"
                  icon="pi pi-chart-bar"
                  @click="fetchCommunityAverages"
                  :loading="statsLoading"
                  class="w-full md:w-auto self-start"
                />

                <div
                  v-if="communityStats"
                  class="mt-4 bg-gray-900/50 p-4 rounded border border-gray-700"
                >
                  <div class="flex justify-between items-center mb-4 border-b border-gray-700 pb-2">
                    <div>
                      <span class="text-gray-400 text-sm">Model:</span>
                      <span class="ml-2 font-bold">{{ communityStats.model }}</span>
                    </div>
                    <div>
                      <span class="text-gray-400 text-sm">Sample Size:</span>
                      <span class="ml-2 font-bold text-blue-400">{{
                        communityStats.sample_size
                      }}</span>
                    </div>
                  </div>

                  <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                      <thead>
                        <tr class="text-left text-gray-400 border-b border-gray-700">
                          <th class="pb-2">Metric</th>
                          <th class="pb-2 text-right">Avg</th>
                          <th class="pb-2 text-right">Min</th>
                          <th class="pb-2 text-right">Max</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="(stats, metric) in communityStats.metrics"
                          :key="metric"
                          class="border-b border-gray-800 last:border-0"
                        >
                          <td class="py-2 font-mono text-gray-300">{{ metric }}</td>
                          <td class="py-2 text-right font-mono">
                            {{ stats.avg?.toFixed(2) ?? '-' }}
                          </td>
                          <td class="py-2 text-right font-mono text-gray-500">
                            {{ stats.min?.toFixed(2) ?? '-' }}
                          </td>
                          <td class="py-2 text-right font-mono text-gray-500">
                            {{ stats.max?.toFixed(2) ?? '-' }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </Fieldset>

            <!-- Permission Management -->
            <Fieldset legend="Permission Management" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex justify-between items-center">
                  <div class="text-sm text-gray-400">Manage admin access and roles</div>
                  <div class="flex gap-2">
                    <Button
                      label="Refresh"
                      icon="pi pi-refresh"
                      severity="secondary"
                      size="small"
                      @click="fetchPermissions"
                    />
                    <Button
                      label="Add Admin"
                      icon="pi pi-plus"
                      severity="success"
                      size="small"
                      @click="grantAdminDialogVisible = true"
                    />
                  </div>
                </div>

                <div class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead>
                      <tr class="border-b border-gray-700 text-gray-400">
                        <th class="text-left py-2">Admin ID</th>
                        <th class="text-left py-2">Permissions</th>
                        <th class="text-right py-2">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="admin in adminPermissions"
                        :key="admin.id"
                        class="border-b border-gray-800 last:border-0 hover:bg-gray-800/30"
                      >
                        <td class="py-2 font-mono text-xs text-blue-300">
                          {{ admin.id.substring(0, 12) }}...
                          <span
                            v-if="admin.id === config.installation_id"
                            class="ml-1 text-green-400 text-[10px] uppercase border border-green-800 px-1 rounded bg-green-900/30"
                            >(You)</span
                          >
                        </td>
                        <td class="py-2">
                          <div class="flex flex-wrap gap-1">
                            <span
                              v-for="perm in admin.effective_permissions"
                              :key="perm"
                              class="px-1.5 py-0.5 bg-gray-700 rounded text-xs text-gray-300 border border-gray-600"
                            >
                              {{ perm.replace('admin:', '') }}
                            </span>
                          </div>
                        </td>
                        <td class="py-2 text-right">
                          <Button
                            icon="pi pi-user-edit"
                            text
                            size="small"
                            severity="info"
                            @click="openPermissionDialog(admin)"
                            v-tooltip="'Edit Permissions'"
                            aria-label="Edit Permissions"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </Fieldset>

            <!-- Training Operations -->
            <Fieldset legend="Training Operations" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex justify-between items-center">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-bold text-gray-300">Current Status:</span>
                    <span
                      v-if="adminTraining.current && adminTraining.current.running"
                      class="px-2 py-1 bg-green-900/50 text-green-400 rounded text-xs font-bold border border-green-700"
                      >RUNNING</span
                    >
                    <span
                      v-else
                      class="px-2 py-1 bg-gray-800 text-gray-400 rounded text-xs font-bold border border-gray-700"
                      >IDLE</span
                    >
                  </div>
                  <Button
                    icon="pi pi-refresh"
                    severity="secondary"
                    size="small"
                    @click="fetchTrainingInfo"
                    v-tooltip="'Refresh'"
                    aria-label="Refresh"
                  />
                </div>

                <div
                  v-if="adminTraining.current && adminTraining.current.running"
                  class="bg-blue-900/20 border border-blue-600/50 p-3 rounded flex justify-between items-center"
                >
                  <div class="text-sm">
                    <div class="font-bold text-blue-300">Training in progress</div>
                    <div class="text-gray-300">
                      Task ID: <span class="font-mono">{{ adminTraining.current.task_id }}</span>
                    </div>
                    <div class="text-gray-400 text-xs">
                      Started:
                      {{ formatAdminTime(adminTraining.current.started_at) }}
                    </div>
                  </div>
                  <Button
                    label="Cancel"
                    icon="pi pi-times"
                    severity="danger"
                    size="small"
                    @click="cancelTraining(adminTraining.current.task_id)"
                    :loading="cancellingTraining"
                  />
                </div>

                <div class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead>
                      <tr class="border-b border-gray-700 text-gray-400">
                        <th class="text-left py-2">Timestamp</th>
                        <th class="text-left py-2">Triggered By</th>
                        <th class="text-center py-2">Result</th>
                        <th class="text-right py-2">Duration</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="task in adminTraining.history"
                        :key="task.task_id"
                        class="border-b border-gray-800 last:border-0 hover:bg-gray-800/30"
                      >
                        <td class="py-2 text-gray-300">
                          {{ formatAdminTime(task.created_at) }}
                        </td>
                        <td class="py-2 font-mono text-xs text-gray-400">
                          {{ task.triggered_by?.substring(0, 8) }}...
                        </td>
                        <td class="py-2 text-center">
                          <span
                            :class="{
                              'text-green-400': task.status === 'completed',
                              'text-red-400': task.status === 'failed',
                              'text-yellow-400': task.status === 'running'
                            }"
                            class="font-bold text-xs uppercase"
                          >
                            {{ task.status }}
                          </span>
                        </td>
                        <td class="py-2 text-right font-mono text-gray-400">
                          {{ formatTaskDuration(task) }}
                        </td>
                      </tr>
                      <tr v-if="adminTraining.history.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500 italic">
                          No training history available
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </Fieldset>

            <Fieldset legend="Runtime Limits" :toggleable="true">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-gray-400">Admin Rate Limit</label>
                  <InputNumber
                    v-model="runtimeLimitsDraft.admin_rate_limit"
                    :min="1"
                    :max="10000"
                    :useGrouping="false"
                  />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-gray-400">Max Training Queue</label>
                  <InputNumber
                    v-model="runtimeLimitsDraft.max_training_queue"
                    :min="1"
                    :max="1000"
                    :useGrouping="false"
                  />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-gray-400">Max Parallel Training</label>
                  <InputNumber
                    v-model="runtimeLimitsDraft.max_parallel_training"
                    :min="1"
                    :max="1"
                    :useGrouping="false"
                  />
                </div>
              </div>
              <div class="mt-3 flex justify-end">
                <Button
                  label="Runtime Limits speichern"
                  icon="pi pi-save"
                  size="small"
                  severity="info"
                  :loading="savingRuntimeLimits"
                  @click="saveRuntimeLimits"
                />
              </div>
            </Fieldset>

            <!-- Audit Log -->
            <Fieldset legend="Audit Log" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-2 items-end">
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">Action</label>
                    <InputText
                      v-model="auditActionFilter"
                      class="w-full"
                      placeholder="z.B. training_trigger"
                    />
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">Admin</label>
                    <InputText v-model="auditAdminFilter" class="w-full" placeholder="admin-id" />
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">Status</label>
                    <Dropdown
                      v-model="auditSuccessFilter"
                      :options="[
                        { label: 'Alle', value: 'all' },
                        { label: 'Erfolg', value: 'success' },
                        { label: 'Fehler', value: 'failure' }
                      ]"
                      optionLabel="label"
                      optionValue="value"
                      class="w-full"
                    />
                  </div>
                  <div class="flex gap-2 justify-end">
                    <Button
                      label="CSV"
                      icon="pi pi-download"
                      severity="contrast"
                      size="small"
                      outlined
                      @click="exportAuditLogCsv"
                    />
                    <Button
                      label="Refresh Log"
                      icon="pi pi-refresh"
                      severity="secondary"
                      size="small"
                      @click="fetchAuditLog"
                    />
                  </div>
                </div>
                <div class="flex justify-end">
                  <Button
                    label="Filter zurücksetzen"
                    icon="pi pi-filter-slash"
                    severity="contrast"
                    size="small"
                    outlined
                    @click="resetAuditFilters"
                  />
                </div>
                <div class="overflow-x-auto max-h-96">
                  <table class="w-full text-sm">
                    <thead>
                      <tr
                        class="border-b border-gray-700 text-gray-400 sticky top-0 bg-gray-900 z-10"
                      >
                        <th class="text-left py-2">Time</th>
                        <th class="text-left py-2">Action</th>
                        <th class="text-left py-2">Admin</th>
                        <th class="text-center py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="log in adminAuditLog"
                        :key="log.timestamp"
                        class="border-b border-gray-800 last:border-0 hover:bg-gray-800/30 font-mono text-xs"
                      >
                        <td class="py-1 text-gray-400">
                          {{ formatAdminTime(log.timestamp) }}
                        </td>
                        <td class="py-1 text-blue-300">{{ log.action }}</td>
                        <td class="py-1 text-gray-500" :title="log.admin_id">
                          {{ log.admin_id.substring(0, 8) }}
                        </td>
                        <td class="py-1 text-center">
                          <i
                            v-if="String(log.result || '').toLowerCase() === 'success'"
                            class="pi pi-check text-green-500"
                          ></i>
                          <i v-else class="pi pi-times text-red-500"></i>
                        </td>
                      </tr>
                      <tr v-if="adminAuditLog.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500 italic">
                          No audit logs available (Click Refresh)
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </Fieldset>

            <div
              class="bg-yellow-900/20 border border-yellow-600/50 p-4 rounded flex items-start gap-3"
            >
              <i class="pi pi-info-circle text-yellow-500 text-xl mt-1"></i>
              <div class="text-sm text-yellow-200">
                You are authenticated as a <strong>Community Admin</strong>. This tab provides
                exclusive insights into the telemetry server status and model generation pipeline.
              </div>
            </div>
          </div>
        </div>

        <!-- Footer (Save Button) inside the content area to be sticky at bottom -->
        <div
          class="flex gap-4 justify-end border-t border-surface-700 p-4 bg-surface-900/90 backdrop-blur z-10"
        >
          <Button
            label="Speichern"
            icon="pi pi-save"
            @click="saveConfig"
            :loading="saving"
            size="large"
            severity="primary"
          />
        </div>
      </div>
    </div>

    <!-- Dialogs -->

    <!-- Installation Details Dialog -->
    <Dialog
      v-model:visible="installationDetailDialog"
      modal
      header="Installation Details"
      :style="{ width: '90vw', maxWidth: '900px' }"
      @hide="closeInstallationDetails"
    >
      <div v-if="loadingDetails" class="flex justify-center items-center p-8">
        <i class="pi pi-spin pi-spinner text-4xl text-blue-500"></i>
      </div>

      <div v-else-if="installationDetails" class="flex flex-col gap-6">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="text-xs text-gray-400 uppercase mb-1">Heat Pump Model</div>
            <div class="text-lg font-bold">{{ installationDetails.heatpump_model }}</div>
          </div>

          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="text-xs text-gray-400 uppercase mb-1">Total Submissions</div>
            <div class="text-lg font-bold text-green-400">
              {{ installationDetails.total_submissions?.toLocaleString() || 0 }}
            </div>
          </div>

          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="text-xs text-gray-400 uppercase mb-1">Data Quality</div>
            <div class="flex items-center gap-2">
              <div
                class="text-lg font-bold"
                :class="
                  installationDetails.data_quality_score >= 0.8
                    ? 'text-green-400'
                    : 'text-yellow-400'
                "
              >
                {{ (installationDetails.data_quality_score * 100).toFixed(0) }}%
              </div>
              <i
                v-if="installationDetails.data_quality_score >= 0.8"
                class="pi pi-check-circle text-green-400"
              ></i>
              <i v-else class="pi pi-exclamation-triangle text-yellow-400"></i>
            </div>
          </div>

          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="text-xs text-gray-400 uppercase mb-1">First Seen</div>
            <div class="text-sm">
              {{
                installationDetails.first_seen
                  ? new Date(installationDetails.first_seen).toLocaleString('de-DE')
                  : 'Unknown'
              }}
            </div>
          </div>

          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="text-xs text-gray-400 uppercase mb-1">Last Seen</div>
            <div class="text-sm">
              {{
                installationDetails.last_seen
                  ? new Date(installationDetails.last_seen).toLocaleString('de-DE')
                  : 'Unknown'
              }}
            </div>
          </div>

          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="text-xs text-gray-400 uppercase mb-1">Contribution Rank</div>
            <div class="text-lg font-bold text-purple-400">
              {{ installationDetails.contribution_rank }}
            </div>
          </div>
        </div>

        <!-- Model Downloads -->
        <div
          v-if="
            installationDetails.model_downloads && installationDetails.model_downloads.length > 0
          "
        >
          <h3 class="text-lg font-bold mb-3 flex items-center gap-2">
            <i class="pi pi-download text-green-400"></i>
            Model Downloads
          </h3>
          <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
            <div class="space-y-2">
              <div
                v-for="(download, idx) in installationDetails.model_downloads"
                :key="idx"
                class="flex justify-between items-center border-b border-gray-800 pb-2 last:border-0"
              >
                <span class="font-mono text-sm">{{ download.model }}</span>
                <span class="text-xs text-gray-400">{{
                  new Date(download.downloaded_at).toLocaleString('de-DE')
                }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Submission History Timeline -->
        <div
          v-if="
            installationHistory &&
            installationHistory.history &&
            installationHistory.history.length > 0
          "
        >
          <h3 class="text-lg font-bold mb-3 flex items-center gap-2">
            <i class="pi pi-clock text-blue-400"></i>
            Recent Activity (Last 20 Entries)
          </h3>
          <div class="bg-gray-900/50 p-4 rounded border border-gray-700 max-h-64 overflow-y-auto">
            <div class="space-y-2">
              <div
                v-for="(entry, idx) in installationHistory.history"
                :key="idx"
                class="flex justify-between items-center text-sm border-b border-gray-800 pb-2 last:border-0"
              >
                <div class="flex items-center gap-2">
                  <i class="pi pi-circle-fill text-xs text-blue-400"></i>
                  <span class="font-mono text-xs text-gray-400">{{ entry.metric }}</span>
                  <span class="text-xs px-2 py-0.5 bg-gray-800 rounded"
                    >{{ entry.count }} points</span
                  >
                </div>
                <span class="text-xs text-gray-500">{{
                  new Date(entry.timestamp).toLocaleString('de-DE')
                }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
          <h3 class="text-lg font-bold mb-3 flex items-center gap-2">
            <i class="pi pi-sliders-h text-cyan-400"></i>
            Installation Settings
          </h3>
          <div v-if="installationSettingsLoading" class="text-gray-400 text-sm">
            <i class="pi pi-spin pi-spinner mr-2"></i> Lade Installation-Settings...
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label class="text-xs text-gray-400">Upload Interval (s)</label>
              <InputNumber
                v-model="installationSettings.telemetry_policy.upload_interval_seconds"
                :useGrouping="false"
                :min="10"
                :max="86400"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-xs text-gray-400">Sampling Ratio</label>
              <InputNumber
                v-model="installationSettings.telemetry_policy.sampling_ratio"
                :min="0.01"
                :max="1"
                :step="0.01"
                :minFractionDigits="2"
                :maxFractionDigits="2"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-xs text-gray-400">PII Masking</label>
              <Dropdown
                v-model="installationSettings.telemetry_policy.pii_masking_level"
                :options="[
                  { label: 'Low', value: 'low' },
                  { label: 'Standard', value: 'standard' },
                  { label: 'High', value: 'high' }
                ]"
                optionLabel="label"
                optionValue="value"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-xs text-gray-400">Anomaly Threshold</label>
              <InputNumber
                v-model="installationSettings.alert_tuning.anomaly_threshold"
                :min="0.01"
                :max="1"
                :step="0.01"
                :minFractionDigits="2"
                :maxFractionDigits="2"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-xs text-gray-400">Cooldown (s)</label>
              <InputNumber
                v-model="installationSettings.alert_tuning.cooldown_seconds"
                :useGrouping="false"
                :min="0"
                :max="86400"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-xs text-gray-400">Consecutive Hits</label>
              <InputNumber
                v-model="installationSettings.alert_tuning.consecutive_hits"
                :useGrouping="false"
                :min="1"
                :max="20"
              />
            </div>
            <div class="md:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div class="flex items-center gap-2">
                <Checkbox
                  v-model="installationSettings.feature_flags.next_gen_ai"
                  binary
                  inputId="feature_next_gen_ai"
                />
                <label for="feature_next_gen_ai" class="text-sm text-gray-300 cursor-pointer"
                  >Feature: next_gen_ai</label
                >
              </div>
              <div class="flex items-center gap-2">
                <Checkbox
                  v-model="installationSettings.feature_flags.new_dashboard"
                  binary
                  inputId="feature_new_dashboard"
                />
                <label for="feature_new_dashboard" class="text-sm text-gray-300 cursor-pointer"
                  >Feature: new_dashboard</label
                >
              </div>
              <div class="flex items-center gap-2">
                <Checkbox
                  v-model="installationSettings.feature_flags.beta_training"
                  binary
                  inputId="feature_beta_training"
                />
                <label for="feature_beta_training" class="text-sm text-gray-300 cursor-pointer"
                  >Feature: beta_training</label
                >
              </div>
            </div>
          </div>
          <div class="mt-4 flex justify-end">
            <Button
              label="Installation-Settings speichern"
              icon="pi pi-save"
              severity="info"
              size="small"
              :loading="savingInstallationSettings"
              @click="saveInstallationSettings"
            />
          </div>
        </div>

        <!-- Admin Badge -->
        <div
          v-if="installationDetails.is_admin"
          class="bg-yellow-900/20 border border-yellow-700 rounded p-3 flex items-center gap-2"
        >
          <i class="pi pi-crown text-yellow-500"></i>
          <span class="text-yellow-200">This is an admin installation</span>
        </div>
      </div>

      <div v-else class="p-8 text-center text-gray-400">No data available</div>

      <template #footer>
        <Button label="Schließen" icon="pi pi-times" @click="closeInstallationDetails" text />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showPasswordDialog"
      modal
      header="Passwort ändern"
      :style="{ width: '400px' }"
    >
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-bold text-sm text-gray-300">Neues Passwort</label>
          <InputText v-model="newPassword" type="password" class="w-full" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-bold text-sm text-gray-300">Bestätigen</label>
          <InputText
            v-model="confirmPassword"
            type="password"
            class="w-full"
            :class="{ 'p-invalid': passwordMismatch }"
          />
          <small v-if="passwordMismatch" class="text-red-500"
            >Passwörter stimmen nicht überein</small
          >
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" text @click="showPasswordDialog = false" />
        <Button
          label="Speichern"
          @click="savePassword"
          :disabled="!newPassword || !confirmPassword || passwordMismatch"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showDeleteDialog"
      modal
      header="Datenbank löschen"
      :style="{ width: '450px' }"
    >
      <div class="flex flex-col gap-4">
        <div class="flex items-start gap-3">
          <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
          <div class="flex flex-col gap-2">
            <span class="font-bold text-lg">Bist du dir absolut sicher?</span>
            <p class="text-gray-300">
              Diese Aktion löscht <span class="font-bold text-red-400">ALLE</span> Daten dauerhaft
              aus der Datenbank.
            </p>
          </div>
        </div>
        <InputText v-model="deleteConfirmationText" placeholder="Tippe DELETE" class="w-full" />
      </div>
      <template #footer>
        <Button label="Abbrechen" text @click="showDeleteDialog = false" />
        <Button
          label="Alles löschen"
          severity="danger"
          @click="confirmDeleteDatabase"
          :disabled="deleteConfirmationText !== 'DELETE'"
          :loading="deletingDatabase"
        />
      </template>
    </Dialog>

    <!-- Manual Update Help Dialog -->
    <Dialog
      v-model:visible="showUpdateHelpDialog"
      modal
      header="Update Anleitung"
      :style="{ width: '500px' }"
    >
      <div class="flex flex-col gap-4">
        <div class="bg-blue-900/20 border border-blue-600/50 p-3 rounded">
          <div class="flex items-center gap-2 text-blue-300 mb-2">
            <i class="pi pi-info-circle"></i>
            <span class="font-bold">Wichtiger Hinweis</span>
          </div>
          <p class="text-sm text-gray-300">
            Die automatische Aktualisierung (Watchtower) wurde entfernt. Bitte führen Sie Updates
            manuell über die Konsole aus, um die neuesten Funktionen und Sicherheitsverbesserungen
            zu erhalten.
          </p>
        </div>

        <div>
          <h4 class="font-bold mb-2 flex items-center gap-2">
            <i class="pi pi-terminal text-green-400"></i>
            Manuelles Update via Terminal
          </h4>
          <div class="bg-gray-900 p-3 rounded font-mono text-sm text-green-400 overflow-x-auto">
            <div class="text-gray-500"># Zum Installationsverzeichnis wechseln</div>
            <div>cd /opt/idm-metrics-collector</div>
            <div class="mt-2 text-gray-500"># Neue Images herunterladen</div>
            <div>docker compose pull</div>
            <div class="mt-2 text-gray-500"># Container neu starten</div>
            <div>docker compose up -d</div>
          </div>
        </div>

        <div class="text-xs text-gray-300">
          <i class="pi pi-lightbulb mr-1"></i>
          Nach dem Update wird die Seite automatisch neu geladen sobald der Container wieder
          erreichbar ist.
        </div>
      </div>
      <template #footer>
        <Button label="Schließen" @click="showUpdateHelpDialog = false" />
      </template>
    </Dialog>

    <!-- Role Change Dialog -->
    <Dialog
      v-model:visible="roleDialogVisible"
      header="Rolle aendern"
      :style="{ width: '400px' }"
      modal
    >
      <div class="flex flex-col gap-4">
        <div>
          <label class="text-sm text-gray-400">Installation:</label>
          <div class="font-mono text-xs bg-gray-800 p-2 rounded mt-1">
            {{ selectedInstallationForAction }}
          </div>
        </div>
        <div>
          <label class="text-sm text-gray-400 mb-2 block" for="new-role-dropdown"
            >Neue Rolle:</label
          >
          <Dropdown
            inputId="new-role-dropdown"
            v-model="newRole"
            :options="[
              { label: 'Guest - Basis-Funktionalitaet', value: 'guest' },
              { label: 'Visitor - Statistiken einsehen', value: 'visitor' },
              { label: 'Sponsor - Erweiterte Features', value: 'sponsor' },
              { label: 'Moderator - Daten einsehen', value: 'moderator' },
              { label: 'Support - Support leisten', value: 'support' },
              { label: 'Admin - Vollzugriff', value: 'admin' }
            ]"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div>
          <label class="text-sm text-gray-400 mb-2 block">Grund (optional):</label>
          <InputText
            v-model="roleReason"
            class="w-full"
            placeholder="Grund fuer die Aenderung..."
          />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="roleDialogVisible = false" />
        <Button label="Speichern" severity="success" :loading="savingRole" @click="saveRole" />
      </template>
    </Dialog>

    <!-- Ban Dialog -->
    <Dialog
      v-model:visible="banDialogVisible"
      header="Installation sperren"
      :style="{ width: '450px' }"
      modal
    >
      <div class="flex flex-col gap-4">
        <div>
          <label class="text-sm text-gray-400">Installation:</label>
          <div class="font-mono text-xs bg-gray-800 p-2 rounded mt-1">
            {{ selectedInstallationForAction }}
          </div>
        </div>
        <div>
          <label class="text-sm text-gray-400 mb-2 block">Sperrtyp:</label>
          <Dropdown
            v-model="banType"
            :options="[
              { label: 'Upload - Keine Daten einreichen', value: 'upload' },
              { label: 'Download - Keine Modelle herunterladen', value: 'download' },
              { label: 'Vollstaendig - Komplett gesperrt', value: 'full' }
            ]"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div>
          <label class="text-sm text-gray-400 mb-2 block">Grund (erforderlich):</label>
          <Textarea
            v-model="banReason"
            class="w-full"
            rows="3"
            placeholder="Grund fuer die Sperre..."
          />
        </div>
        <div>
          <label class="text-sm text-gray-400 mb-2 block">Dauer:</label>
          <Dropdown
            v-model="banDuration"
            :options="[
              { label: 'Permanent', value: null },
              { label: '1 Stunde', value: 1 },
              { label: '1 Tag', value: 24 },
              { label: '1 Woche', value: 168 },
              { label: '1 Monat', value: 720 },
              { label: '3 Monate', value: 2160 }
            ]"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="banDialogVisible = false" />
        <Button label="Sperren" severity="danger" :loading="savingBan" @click="saveBan" />
      </template>
    </Dialog>

    <!-- Permission Dialog -->
    <Dialog
      v-model:visible="permissionDialogVisible"
      header="Manage Permissions"
      :style="{ width: '400px' }"
      modal
    >
      <div class="flex flex-col gap-4">
        <div class="text-sm text-gray-400 mb-2">
          Admin: <span class="font-mono text-white">{{ selectedAdminId.substring(0, 12) }}...</span>
        </div>
        <div class="flex gap-2 items-end">
          <div class="flex-1">
            <label class="text-xs text-gray-400 block mb-1">Permission Preset</label>
            <Dropdown
              v-model="selectedPermissionPreset"
              :options="Object.keys(permissionPresets).map((k) => ({ label: k, value: k }))"
              optionLabel="label"
              optionValue="value"
              class="w-full"
            />
          </div>
          <Button
            label="Preset anwenden"
            size="small"
            severity="info"
            outlined
            @click="applyPermissionPreset"
          />
        </div>
        <div class="flex flex-col gap-2">
          <div
            v-for="perm in [
              'admin:view',
              'admin:models',
              'admin:training',
              'admin:users',
              'admin:full'
            ]"
            :key="perm"
            class="flex items-center gap-2"
          >
            <Checkbox v-model="selectedAdminPermissions" :inputId="perm" :value="perm" />
            <label
              :for="perm"
              class="cursor-pointer select-none"
              :class="perm === 'admin:full' ? 'text-yellow-400 font-bold' : 'text-gray-300'"
              >{{ perm }}</label
            >
          </div>
        </div>
        <div class="text-xs text-gray-500 mt-2">
          Note: 'admin:full' automatically includes all other permissions.
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" text severity="secondary" @click="permissionDialogVisible = false" />
        <Button
          label="Save Changes"
          severity="primary"
          :loading="savingPermissions"
          @click="savePermissions"
        />
      </template>
    </Dialog>

    <!-- Grant Admin Dialog -->
    <Dialog
      v-model:visible="grantAdminDialogVisible"
      header="Add New Admin"
      :style="{ width: '450px' }"
      modal
    >
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-bold text-gray-300">Installation ID (UUID)</label>
          <InputText
            v-model="newAdminId"
            class="w-full font-mono"
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          />
          <small class="text-gray-500">The installation must already exist in the database.</small>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" text severity="secondary" @click="grantAdminDialogVisible = false" />
        <Button
          label="Grant Access"
          severity="success"
          :loading="grantingAdmin"
          @click="grantNewAdmin"
          :disabled="!newAdminId"
        />
      </template>
    </Dialog>

    <Toast />
    <ConfirmDialog />
    <PrivacyPolicyDialog ref="privacyDialog" />
  </div>
</template>

<script setup>
// Xerolux 2026
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import api from '@/utils/api.js'
import Fieldset from 'primevue/fieldset'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import Dialog from 'primevue/dialog'
import SelectButton from 'primevue/selectbutton'
import Dropdown from 'primevue/dropdown'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { copyToClipboard } from '../utils/clipboard'
import PrivacyPolicyDialog from '../components/PrivacyPolicyDialog.vue'
import { Chart, registerables } from 'chart.js'

// Register Chart.js components
Chart.register(...registerables)

const config = ref({
  installation_id: '',
  hp_model: '',
  idm: { host: '', port: 502, circuits: ['A'], zones: [] },
  metrics: { url: '' },
  web: { write_enabled: false },
  logging: { interval: 60, realtime_mode: false },
  mqtt: {
    enabled: false,
    broker: '',
    port: 1883,
    username: '',
    topic_prefix: 'idm/heatpump',
    qos: 0,
    use_tls: false,
    tls_ca_cert: '',
    publish_interval: 60,
    ha_discovery_enabled: false,
    ha_discovery_prefix: 'homeassistant'
  },
  network_security: { enabled: false, whitelist: [], blacklist: [] },
  signal: { enabled: false, cli_path: 'signal-cli', sender: '', recipients: [] },
  telegram: { enabled: false, bot_token: '', chat_ids: [] },
  discord: { enabled: false, webhook_url: '' },
  email: {
    enabled: false,
    smtp_server: '',
    smtp_port: 587,
    username: '',
    sender: '',
    recipients: []
  },
  webdav: { enabled: false, url: '', username: '' },
  ai: { enabled: false, sensitivity: 3.0, model: 'rolling' },
  telemetry: { enabled: true, auth_token: '', admin_auth_token: '', server_url: '' },
  updates: { enabled: false, interval_hours: 12, mode: 'apply', target: 'all' },
  backup: { enabled: false, interval: 24, retention: 10, auto_upload: false }
})

const activeCategory = ref('connection')
const categories = computed(() => {
  const cats = [
    { id: 'connection', label: 'Verbindung', icon: 'pi pi-server' },
    { id: 'mqtt', label: 'MQTT & Integration', icon: 'pi pi-share-alt' },
    { id: 'notifications', label: 'Benachrichtigungen', icon: 'pi pi-bell' },
    { id: 'ai', label: 'KI-Analyse', icon: 'pi pi-chart-line' },
    { id: 'security', label: 'Sicherheit', icon: 'pi pi-shield' },
    { id: 'system', label: 'System & Wartung', icon: 'pi pi-cog' }
  ]

  if (telemetryStatus.value?.is_admin) {
    cats.push({ id: 'admin', label: 'Admin Zone', icon: 'pi pi-crown' })
  }

  return cats
})

const showPasswordDialog = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const mqttPassword = ref('')
const emailPassword = ref('')
const webdavPassword = ref('')
const whitelistText = ref('')
const blacklistText = ref('')
const signalRecipientsText = ref('')
const telegramChatIdsText = ref('')
const emailRecipientsText = ref('')
const updateStatus = ref({})
const signalStatus = ref({})
const aiStatus = ref(null)
const telemetryStatus = ref(null)
const statusLoading = ref(false)
// Admin Zone variables
const adminHealth = ref(null)
const adminInstallations = ref(null)
const adminModels = ref(null)
const adminMetrics = ref(null)
const communityStats = ref(null)
const statsLoading = ref(false)
const installationDetailDialog = ref(false)
const selectedInstallation = ref(null)
const installationDetails = ref(null)
const installationHistory = ref(null)
const loadingDetails = ref(false)
const selectedStatsModel = ref(null)
const statsMetrics = ref('cop_current, temp_outdoor')
const trainingTargetModel = ref(null)
const trainingTargetInstallationId = ref('')
const modelDeleting = ref(false)
const trainingInProgress = ref(false)
const adminAutoRefresh = ref(true)
let adminAutoRefreshInterval = null
// Installation Role/Ban Management
const installationRoles = ref(null)
const installationRolesError = ref(null)
const roleDialogVisible = ref(false)
const banDialogVisible = ref(false)
const selectedInstallationForAction = ref(null)
const newRole = ref('guest')
const roleReason = ref('')
const banType = ref('full')
const banReason = ref('')
const banDuration = ref(null)
const savingRole = ref(false)
const savingBan = ref(false)
// New Admin Features State
const adminAuditLog = ref([])
const auditActionFilter = ref('')
const auditAdminFilter = ref('')
const auditSuccessFilter = ref('all')
const adminTraining = ref({ current: null, history: [] })
const adminPermissions = ref([])
const permissionPresets = ref({})
const selectedPermissionPreset = ref('viewer')
const permissionDialogVisible = ref(false)
const selectedAdminId = ref('')
const selectedAdminPermissions = ref([])
const grantAdminDialogVisible = ref(false)
const newAdminId = ref('')
const savingPermissions = ref(false)
const grantingAdmin = ref(false)
const cancellingTraining = ref(false)
const runtimeLimits = ref(null)
const runtimeLimitsDraft = ref({
  admin_rate_limit: 20,
  max_training_queue: 10,
  max_parallel_training: 1
})
const savingRuntimeLimits = ref(false)
const trainingMinPoints = ref(null)
const trainingMinInstallations = ref(null)
const trainingLookbackDays = ref(null)
const trainingDryRun = ref(false)
const installationSettings = ref({
  telemetry_policy: {
    upload_interval_seconds: 60,
    sampling_ratio: 1.0,
    pii_masking_level: 'standard'
  },
  alert_tuning: { anomaly_threshold: 0.7, cooldown_seconds: 300, consecutive_hits: 3 },
  feature_flags: { next_gen_ai: false, new_dashboard: false, beta_training: false }
})
const installationSettingsLoading = ref(false)
const savingInstallationSettings = ref(false)

const modelDownloadsChart = ref(null)
let modelDownloadsChartInstance = null
const checkingUpdates = ref(false)
const checkingModel = ref(false)
const submittingTelemetry = ref(false)
const currentClientIP = ref('')
const loading = ref(true)
const saving = ref(false)
const toast = useToast()
const confirm = useConfirm()
const models = ref([])
const manufacturers = ref([])
const privacyDialog = ref(null)

let aiStatusInterval = null
let adminRefreshInFlight = false

const copyId = async () => {
  const success = await copyToClipboard(config.value.installation_id)
  if (success) {
    toast.add({
      severity: 'info',
      summary: 'Kopiert',
      detail: 'ID in Zwischenablage kopiert',
      life: 2000
    })
  } else {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Konnte nicht kopiert werden',
      life: 3000
    })
  }
}

// ==================== ADMIN FUNCTIONS ====================

const ADMIN_TIMEOUT = 15000

const normalizeTokenValue = (value) => {
  const token = typeof value === 'string' ? value.trim() : ''
  return token && token !== '***' ? token : ''
}

const getAdminHeaders = () => {
  const authToken =
    normalizeTokenValue(config.value.telemetry?.admin_auth_token) ||
    normalizeTokenValue(config.value.telemetry?.auth_token)
  return authToken ? { Authorization: `Bearer ${authToken}` } : {}
}

const adminGet = (url, options = {}) => axios.get(url, { timeout: ADMIN_TIMEOUT, ...options })
const adminPost = (url, data, options = {}) =>
  axios.post(url, data, { timeout: ADMIN_TIMEOUT, ...options })
const adminPut = (url, data, options = {}) =>
  axios.put(url, data, { timeout: ADMIN_TIMEOUT, ...options })
const adminDelete = (url, options = {}) => axios.delete(url, { timeout: ADMIN_TIMEOUT, ...options })

const fetchAdminHealth = async () => {
  if (!telemetryStatus.value?.is_admin) return

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/health`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    adminHealth.value = res.data
  } catch (err) {
    console.error('Failed to fetch admin health:', err)
  }
}

const adminInstallationsError = ref(null)

const fetchAdminInstallations = async () => {
  if (!telemetryStatus.value?.is_admin) return
  adminInstallationsError.value = null

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/installations`, {
      params: { installation_id: config.value.installation_id, limit: 50 },
      headers: getAdminHeaders()
    })
    adminInstallations.value = res.data
    // Fetch detailed roles independently; do not fail installation table on role endpoint errors.
    fetchInstallationRoles().catch((err) => {
      console.warn('Role list fetch failed, using inline role fallback:', err?.message || err)
    })
  } catch (err) {
    console.error('Failed to fetch admin installations:', err)
    const msg =
      err.code === 'ECONNABORTED'
        ? 'Zeitüberschreitung - Telemetrie-Server nicht erreichbar'
        : err.response?.data?.detail || err.message || 'Netzwerkfehler - Server nicht erreichbar'
    adminInstallationsError.value = msg
  }
}

// Installation Role/Ban Management Functions
const fetchInstallationRoles = async () => {
  if (!telemetryStatus.value?.is_admin) return
  installationRolesError.value = null
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/installations/list`, {
      params: { installation_id: config.value.installation_id, limit: 200 },
      headers: getAdminHeaders()
    })
    installationRoles.value = res.data
  } catch (err) {
    console.error('Failed to fetch installation roles:', err)
    installationRolesError.value =
      err.code === 'ECONNABORTED'
        ? 'Zeitüberschreitung - Telemetrie-Server nicht erreichbar'
        : err.response?.data?.detail || err.message || 'Netzwerkfehler - Server nicht erreichbar'
  }
}

const getInstallationRole = (instId) => {
  if (installationRoles.value?.items) {
    const inst = installationRoles.value.items.find((i) => i.installation_id === instId)
    if (inst?.role) return inst.role
  }
  const inline = adminInstallations.value?.installations?.find((i) => i.installation_id === instId)
  return inline?.role || 'guest'
}

const isInstallationBanned = (instId) => {
  if (installationRoles.value?.items) {
    const inst = installationRoles.value.items.find((i) => i.installation_id === instId)
    if (typeof inst?.is_banned === 'boolean') return inst.is_banned
  }
  const inline = adminInstallations.value?.installations?.find((i) => i.installation_id === instId)
  return !!inline?.is_banned
}

const getRoleBadgeClass = (role) => {
  const classes = {
    guest: 'bg-gray-600 text-white',
    visitor: 'bg-blue-600 text-white',
    sponsor: 'bg-yellow-500 text-black',
    moderator: 'bg-purple-600 text-white',
    support: 'bg-teal-600 text-white',
    admin: 'bg-red-600 text-white'
  }
  return classes[role] || classes.guest
}

const formatAdminTime = (value) => {
  if (!value) return '-'
  const date = typeof value === 'number' ? new Date(value * 1000) : new Date(value)
  return Number.isNaN(date.getTime()) ? '-' : date.toLocaleString()
}

const formatTaskDuration = (task) => {
  const raw = task?.duration_seconds ?? task?.duration
  return typeof raw === 'number' ? `${raw.toFixed(1)}s` : '-'
}

const openRoleDialog = (instId) => {
  selectedInstallationForAction.value = instId
  newRole.value = getInstallationRole(instId)
  roleReason.value = ''
  roleDialogVisible.value = true
}

const openBanDialog = (instId) => {
  selectedInstallationForAction.value = instId
  banType.value = 'full'
  banReason.value = ''
  banDuration.value = null
  banDialogVisible.value = true
}

const saveRole = async () => {
  if (!selectedInstallationForAction.value) return
  savingRole.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const authToken = config.value.telemetry?.auth_token || ''
    await adminPost(
      `${telemetryUrl}/api/v1/admin/installations/${selectedInstallationForAction.value}/role`,
      null,
      {
        params: {
          installation_id: config.value.installation_id,
          role: newRole.value,
          reason: roleReason.value || undefined
        },
        headers: getAdminHeaders()
      }
    )
    toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Rolle geaendert', life: 3000 })
    roleDialogVisible.value = false
    await fetchInstallationRoles()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Rolle konnte nicht geaendert werden',
      life: 5000
    })
  } finally {
    savingRole.value = false
  }
}

const saveBan = async () => {
  if (!selectedInstallationForAction.value || !banReason.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Hinweis',
      detail: 'Grund ist erforderlich',
      life: 3000
    })
    return
  }
  savingBan.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const authToken = config.value.telemetry?.auth_token || ''
    const params = {
      installation_id: config.value.installation_id,
      ban_type: banType.value,
      reason: banReason.value
    }
    if (banDuration.value) params.duration_hours = banDuration.value

    await adminPost(
      `${telemetryUrl}/api/v1/admin/installations/${selectedInstallationForAction.value}/ban`,
      null,
      { params, headers: getAdminHeaders() }
    )
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Installation gesperrt',
      life: 3000
    })
    banDialogVisible.value = false
    await fetchInstallationRoles()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Sperre fehlgeschlagen',
      life: 5000
    })
  } finally {
    savingBan.value = false
  }
}

const unbanInstallation = async (instId) => {
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    // Try to unban all types; ignore 4xx (not banned with that type)
    const banTypes = ['full', 'upload', 'download']
    let anySucceeded = false
    for (const bt of banTypes) {
      try {
        await adminPost(`${telemetryUrl}/api/v1/admin/installations/${instId}/unban`, null, {
          params: { installation_id: config.value.installation_id, ban_type: bt },
          headers: getAdminHeaders()
        })
        anySucceeded = true
      } catch {
        /* ignore if not banned with this type */
      }
    }
    await fetchInstallationRoles()
    if (anySucceeded || !isInstallationBanned(instId)) {
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Installation entsperrt',
        life: 3000
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Entsperren fehlgeschlagen',
        life: 5000
      })
    }
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Entsperren fehlgeschlagen',
      life: 5000
    })
  }
}

const fetchAdminModels = async () => {
  if (!telemetryStatus.value?.is_admin) return

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/models`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    adminModels.value = res.data

    // Update chart after data is loaded
    setTimeout(() => renderModelDownloadsChart(), 100)
  } catch (err) {
    console.error('Failed to fetch admin models:', err)
  }
}

const renderModelDownloadsChart = () => {
  if (!adminModels.value?.models || !modelDownloadsChart.value) return

  const ctx = modelDownloadsChart.value.getContext('2d')

  // Destroy existing chart instance
  if (modelDownloadsChartInstance) {
    modelDownloadsChartInstance.destroy()
  }

  // Prepare data
  const models = adminModels.value.models
    .filter((m) => m.download_count > 0)
    .sort((a, b) => b.download_count - a.download_count)
    .slice(0, 10) // Show top 10

  if (models.length === 0) {
    // No downloads yet
    return
  }

  const labels = models.map((m) => m.name)
  const data = models.map((m) => m.download_count)

  // Create new chart
  modelDownloadsChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Downloads',
          data: data,
          backgroundColor: 'rgba(59, 130, 246, 0.7)', // Blue
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            color: 'rgba(156, 163, 175, 0.8)'
          },
          grid: {
            color: 'rgba(75, 85, 99, 0.2)'
          }
        },
        x: {
          ticks: {
            color: 'rgba(156, 163, 175, 0.8)',
            maxRotation: 45,
            minRotation: 45
          },
          grid: {
            display: false
          }
        }
      }
    }
  })
}

const fetchAdminMetrics = async () => {
  if (!telemetryStatus.value?.is_admin) return

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/metrics`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    adminMetrics.value = res.data
  } catch (err) {
    console.error('Failed to fetch admin metrics:', err)
  }
}

const fetchCommunityAverages = async () => {
  if (!selectedStatsModel.value) {
    toast.add({
      severity: 'warn',
      summary: 'Warnung',
      detail: 'Bitte wähle ein Modell',
      life: 3000
    })
    return
  }

  statsLoading.value = true
  communityStats.value = null

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const headers = {}
    const token = normalizeTokenValue(config.value.telemetry?.auth_token)
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await api.get(`${telemetryUrl}/api/v1/community/averages`, {
      params: {
        model: selectedStatsModel.value,
        metrics: statsMetrics.value
      },
      headers: headers
    })

    communityStats.value = res.data
  } catch (err) {
    console.error('Failed to fetch community averages:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || err.message,
      life: 5000
    })
  } finally {
    statsLoading.value = false
  }
}

const fetchAuditLog = async () => {
  if (!telemetryStatus.value?.is_admin) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const successOnly =
      auditSuccessFilter.value === 'all' ? undefined : auditSuccessFilter.value === 'success'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/audit-log`, {
      params: {
        installation_id: config.value.installation_id,
        limit: 100,
        action: auditActionFilter.value || undefined,
        admin_filter: auditAdminFilter.value || undefined,
        success_only: successOnly
      },
      headers: getAdminHeaders()
    })
    adminAuditLog.value = res.data.events || []
  } catch (err) {
    console.error('Failed to fetch audit log:', err)
  }
}

const exportAuditLogCsv = async () => {
  if (!telemetryStatus.value?.is_admin) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const successOnly =
      auditSuccessFilter.value === 'all' ? undefined : auditSuccessFilter.value === 'success'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/audit-log`, {
      params: {
        installation_id: config.value.installation_id,
        limit: 500,
        action: auditActionFilter.value || undefined,
        admin_filter: auditAdminFilter.value || undefined,
        success_only: successOnly,
        format: 'csv'
      },
      headers: getAdminHeaders(),
      responseType: 'blob'
    })

    const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'telemetry_audit_log.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Audit CSV Export fehlgeschlagen',
      life: 5000
    })
  }
}

const resetAuditFilters = () => {
  auditActionFilter.value = ''
  auditAdminFilter.value = ''
  auditSuccessFilter.value = 'all'
  fetchAuditLog()
}

const fetchRuntimeLimits = async () => {
  if (!telemetryStatus.value?.is_admin) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/runtime-limits`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    runtimeLimits.value = res.data.limits
    runtimeLimitsDraft.value = { ...runtimeLimitsDraft.value, ...res.data.limits }
  } catch (err) {
    console.error('Failed to fetch runtime limits:', err)
  }
}

const saveRuntimeLimits = async () => {
  savingRuntimeLimits.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminPost(
      `${telemetryUrl}/api/v1/admin/runtime-limits`,
      {
        admin_rate_limit: Number(runtimeLimitsDraft.value.admin_rate_limit),
        max_training_queue: Number(runtimeLimitsDraft.value.max_training_queue),
        max_parallel_training: Number(runtimeLimitsDraft.value.max_parallel_training)
      },
      {
        params: { installation_id: config.value.installation_id },
        headers: getAdminHeaders()
      }
    )
    runtimeLimits.value = res.data.limits
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Runtime Limits gespeichert',
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Runtime Limits konnten nicht gespeichert werden',
      life: 5000
    })
  } finally {
    savingRuntimeLimits.value = false
  }
}

const fetchPermissionPresets = async () => {
  if (!telemetryStatus.value?.is_admin) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/permissions/presets`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    permissionPresets.value = res.data.presets || {}
  } catch (err) {
    console.error('Failed to fetch permission presets:', err)
  }
}

const applyPermissionPreset = async () => {
  if (!selectedAdminId.value || !selectedPermissionPreset.value) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    await adminPost(
      `${telemetryUrl}/api/v1/admin/permissions/apply-preset`,
      {
        target_admin_id: selectedAdminId.value,
        preset: selectedPermissionPreset.value,
        merge: false
      },
      {
        params: { installation_id: config.value.installation_id },
        headers: getAdminHeaders()
      }
    )
    await fetchPermissions()
    const admin = adminPermissions.value.find((a) => a.id === selectedAdminId.value)
    selectedAdminPermissions.value = admin?.permissions ? [...admin.permissions] : []
    toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Preset angewendet', life: 3000 })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Preset konnte nicht angewendet werden',
      life: 5000
    })
  }
}

const fetchInstallationSettings = async (instId) => {
  if (!telemetryStatus.value?.is_admin || !instId) return
  installationSettingsLoading.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/installations/${instId}/settings`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    installationSettings.value = res.data.settings || installationSettings.value
  } catch (err) {
    console.error('Failed to fetch installation settings:', err)
  } finally {
    installationSettingsLoading.value = false
  }
}

const saveInstallationSettings = async () => {
  if (!selectedInstallation.value) return
  savingInstallationSettings.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminPut(
      `${telemetryUrl}/api/v1/admin/installations/${selectedInstallation.value}/settings`,
      installationSettings.value,
      {
        params: { installation_id: config.value.installation_id },
        headers: getAdminHeaders()
      }
    )
    installationSettings.value = res.data.settings || installationSettings.value
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Installation-Settings gespeichert',
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail:
        err.response?.data?.detail || 'Installation-Settings konnten nicht gespeichert werden',
      life: 5000
    })
  } finally {
    savingInstallationSettings.value = false
  }
}

const fetchTrainingInfo = async () => {
  if (!telemetryStatus.value?.is_admin) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const headers = getAdminHeaders()
    const [currentRes, historyRes] = await Promise.all([
      adminGet(`${telemetryUrl}/api/v1/admin/training/current`, {
        params: { installation_id: config.value.installation_id },
        headers
      }),
      adminGet(`${telemetryUrl}/api/v1/admin/training/history`, {
        params: { installation_id: config.value.installation_id, limit: 20 },
        headers
      })
    ])

    adminTraining.value = {
      current: currentRes.data.running ? currentRes.data : null,
      history: historyRes.data.tasks || []
    }
  } catch (err) {
    console.error('Failed to fetch training info:', err)
  }
}

const fetchPermissions = async () => {
  if (!telemetryStatus.value?.is_admin) return
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const res = await adminGet(`${telemetryUrl}/api/v1/admin/permissions`, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })

    // Transform object to array
    adminPermissions.value = Object.entries(res.data.admins || {}).map(([id, data]) => ({
      id,
      ...data
    }))
  } catch (err) {
    console.error('Failed to fetch permissions:', err)
  }
}

const cancelTraining = async (taskId) => {
  cancellingTraining.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    await adminPost(`${telemetryUrl}/api/v1/admin/training/cancel/${taskId}`, null, {
      params: { installation_id: config.value.installation_id },
      headers: getAdminHeaders()
    })
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Training abgebrochen',
      life: 3000
    })
    await fetchTrainingInfo()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Abbruch fehlgeschlagen',
      life: 5000
    })
  } finally {
    cancellingTraining.value = false
  }
}

const openPermissionDialog = (admin) => {
  selectedAdminId.value = admin.id
  selectedAdminPermissions.value = [...admin.permissions] // Use direct permissions
  selectedPermissionPreset.value = 'viewer'
  permissionDialogVisible.value = true
}

const savePermissions = async () => {
  if (!selectedAdminId.value) return
  savingPermissions.value = true

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const admin = adminPermissions.value.find((a) => a.id === selectedAdminId.value)
    if (!admin) return

    const currentPerms = new Set(admin.permissions)
    const newPerms = new Set(selectedAdminPermissions.value)

    const headers = getAdminHeaders()

    // Grant new permissions
    for (const perm of newPerms) {
      if (!currentPerms.has(perm)) {
        await adminPost(`${telemetryUrl}/api/v1/admin/permissions/grant`, null, {
          params: {
            installation_id: config.value.installation_id,
            target_admin_id: selectedAdminId.value,
            permission: perm
          },
          headers
        })
      }
    }

    // Revoke removed permissions
    for (const perm of currentPerms) {
      if (!newPerms.has(perm)) {
        await adminPost(`${telemetryUrl}/api/v1/admin/permissions/revoke`, null, {
          params: {
            installation_id: config.value.installation_id,
            target_admin_id: selectedAdminId.value,
            permission: perm
          },
          headers
        })
      }
    }

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Berechtigungen aktualisiert',
      life: 3000
    })
    permissionDialogVisible.value = false
    await fetchPermissions()
  } catch (err) {
    console.error(err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Berechtigungen konnten nicht gespeichert werden',
      life: 5000
    })
  } finally {
    savingPermissions.value = false
  }
}

const grantNewAdmin = async () => {
  if (!newAdminId.value) return
  grantingAdmin.value = true

  try {
    // Just grant admin:view to start
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    await adminPost(`${telemetryUrl}/api/v1/admin/permissions/grant`, null, {
      params: {
        installation_id: config.value.installation_id,
        target_admin_id: newAdminId.value,
        permission: 'admin:view'
      },
      headers: getAdminHeaders()
    })

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Neuer Admin hinzugefügt',
      life: 3000
    })
    grantAdminDialogVisible.value = false
    newAdminId.value = ''
    await fetchPermissions()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Admin konnte nicht hinzugefügt werden',
      life: 5000
    })
  } finally {
    grantingAdmin.value = false
  }
}

const openInstallationDetails = async (installationId) => {
  selectedInstallation.value = installationId
  installationDetailDialog.value = true
  loadingDetails.value = true
  installationDetails.value = null
  installationHistory.value = null

  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'

    const headers = getAdminHeaders()
    // Fetch details and history in parallel
    const [detailsRes, historyRes, settingsRes] = await Promise.all([
      adminGet(`${telemetryUrl}/api/v1/admin/installations/${installationId}/details`, {
        params: { installation_id: config.value.installation_id },
        headers
      }),
      adminGet(`${telemetryUrl}/api/v1/admin/installations/${installationId}/history`, {
        params: { installation_id: config.value.installation_id, limit: 20 },
        headers
      }),
      adminGet(`${telemetryUrl}/api/v1/admin/installations/${installationId}/settings`, {
        params: { installation_id: config.value.installation_id },
        headers
      }).catch(() => ({ data: { settings: installationSettings.value } }))
    ])

    installationDetails.value = detailsRes.data
    installationHistory.value = historyRes.data
    installationSettings.value = settingsRes.data?.settings || installationSettings.value
  } catch (err) {
    console.error('Failed to fetch installation details:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: err.response?.data?.detail || 'Installation Details konnten nicht geladen werden',
      life: 5000
    })
  } finally {
    loadingDetails.value = false
  }
}

const closeInstallationDetails = () => {
  installationDetailDialog.value = false
  selectedInstallation.value = null
  installationDetails.value = null
  installationHistory.value = null
}

const deleteModel = async (modelName) => {
  // Show confirmation dialog
  confirm.require({
    message: `Möchtest du das Modell "${modelName}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`,
    header: 'Modell löschen',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Löschen',
    rejectLabel: 'Abbrechen',
    accept: async () => {
      modelDeleting.value = true
      try {
        const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
        await adminDelete(`${telemetryUrl}/api/v1/admin/models/${encodeURIComponent(modelName)}`, {
          params: { installation_id: config.value.installation_id },
          headers: getAdminHeaders()
        })

        toast.add({
          severity: 'success',
          summary: 'Modell gelöscht',
          detail: `Modell "${modelName}" wurde erfolgreich gelöscht`,
          life: 3000
        })

        // Refresh model list and stats in parallel
        await Promise.all([fetchAdminModels(), fetchAdminHealth()])
      } catch (err) {
        console.error('Failed to delete model:', err)
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail:
            'Modell konnte nicht gelöscht werden: ' + (err.response?.data?.detail || err.message),
          life: 5000
        })
      } finally {
        modelDeleting.value = false
      }
    }
  })
}

const triggerTraining = async () => {
  trainingInProgress.value = true
  try {
    const telemetryUrl = config.value.telemetry?.server_url || 'https://collector.xerolux.de'
    const params = { installation_id: config.value.installation_id }
    if (trainingTargetModel.value) params.target_model = trainingTargetModel.value
    if (trainingTargetInstallationId.value?.trim()) {
      params.target_installation_id = trainingTargetInstallationId.value.trim()
    }
    if (trainingMinPoints.value) params.min_points = Number(trainingMinPoints.value)
    if (trainingMinInstallations.value) {
      params.min_installations = Number(trainingMinInstallations.value)
    }
    if (trainingLookbackDays.value) params.lookback_days = Number(trainingLookbackDays.value)
    if (trainingDryRun.value) params.dry_run = true
    const res = await adminPost(`${telemetryUrl}/api/v1/admin/models/trigger-training`, null, {
      params,
      headers: getAdminHeaders()
    })

    if (res.data.success) {
      toast.add({
        severity: trainingDryRun.value ? 'info' : 'success',
        summary: trainingDryRun.value ? 'Dry-Run erfolgreich' : 'Training gestartet',
        detail: trainingDryRun.value
          ? 'Parameter sind gültig. Es wurde kein Training gestartet.'
          : 'Modell-Training wurde manuell ausgelöst',
        life: 3000
      })
    } else {
      toast.add({
        severity: 'warn',
        summary: 'Training gestartet (mit Warnungen)',
        detail: res.data.message || 'Siehe Logs für Details',
        life: 5000
      })
    }
  } catch (err) {
    console.error('Failed to trigger training:', err)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail:
        'Training konnte nicht gestartet werden: ' + (err.response?.data?.detail || err.message),
      life: 5000
    })
  } finally {
    trainingInProgress.value = false
  }
}

const passwordMismatch = computed(() => {
  return newPassword.value && confirmPassword.value && newPassword.value !== confirmPassword.value
})

onUnmounted(() => {
  if (aiStatusInterval) clearInterval(aiStatusInterval)
  if (adminAutoRefreshInterval) clearInterval(adminAutoRefreshInterval)
  if (modelDownloadsChartInstance) modelDownloadsChartInstance.destroy()
})

// Backup & Restore state
const backups = ref([])
const loadingBackups = ref(false)
const creatingBackup = ref(false)
const restoringBackup = ref(false)
const selectedFile = ref(null)
const fileInput = ref(null)

// Database Maintenance
const showDeleteDialog = ref(false)
const deleteConfirmationText = ref('')
const deletingDatabase = ref(false)

// Update Help Dialog
const showUpdateHelpDialog = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/api/config')
    config.value = res.data
    if (!config.value.telemetry) config.value.telemetry = {}
    config.value.telemetry.auth_token = normalizeTokenValue(config.value.telemetry.auth_token)
    config.value.telemetry.admin_auth_token = normalizeTokenValue(
      config.value.telemetry.admin_auth_token
    )

    // Convert whitelist/blacklist arrays to text
    if (config.value.network_security) {
      whitelistText.value = (config.value.network_security.whitelist || []).join('\n')
      blacklistText.value = (config.value.network_security.blacklist || []).join('\n')
    }

    if (config.value.signal) {
      signalRecipientsText.value = (config.value.signal.recipients || []).join('\n')
    }

    if (config.value.telegram) {
      telegramChatIdsText.value = (config.value.telegram.chat_ids || []).join(', ')
    }
    if (config.value.email) {
      emailRecipientsText.value = (config.value.email.recipients || []).join(', ')
    }

    // Get current client IP
    try {
      const ipRes = await api.get('/api/health')
      currentClientIP.value = ipRes.data.client_ip || 'Unbekannt'
    } catch (e) {
      console.error('Failed to get client IP', e)
    }

    // Load models
    try {
      const infoRes = await api.get('/api/info')
      if (infoRes.data.heat_pump_models) {
        models.value = infoRes.data.heat_pump_models.map((m) => ({ label: m, value: m }))
      }
      if (infoRes.data.heat_pump_manufacturers) {
        manufacturers.value = infoRes.data.heat_pump_manufacturers
      }
    } catch (e) {
      console.error('Failed to get info', e)
    }

    // Load backups
    loadBackups()
    loadStatus(true) // Show notification on initial load
    loadAiStatus()
    loadTelemetryStatus()

    // Refresh AI status periodically
    aiStatusInterval = setInterval(() => {
      loadAiStatus()
      loadTelemetryStatus()
    }, 10000)
  } catch (e) {
    console.error(e)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Konfiguration konnte nicht geladen werden',
      life: 3000
    })
  } finally {
    loading.value = false
  }
})

const sendSignalTest = async () => {
  try {
    const res = await api.post('/api/signal/test', {
      message: 'Signal Test vom IDM Metrics Collector'
    })
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Fehler',
        detail: res.data.error || 'Signal Test fehlgeschlagen',
        life: 3000
      })
    }
  } catch (e) {
    console.error(e)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || e.message,
      life: 5000
    })
  }
}

const loadStatus = async (showNotification = false) => {
  statusLoading.value = true
  try {
    const [updateRes, signalRes] = await Promise.all([
      axios.get('/api/check-update'),
      axios.get('/api/signal/status')
    ])
    updateStatus.value = updateRes.data
    signalStatus.value = signalRes.data

    // Show notification popup if updates are available (on initial load)
    if (showNotification && updateRes.data.update_available) {
      const lastSeen = localStorage.getItem('last_seen_update_version')
      const currentLatest = updateRes.data.latest_version

      // Only show if we haven't seen this version yet
      if (lastSeen !== currentLatest) {
        const dockerUpdates = updateRes.data.docker?.updates_available
        const gitUpdates = updateRes.data.git_update_available

        let detail = 'Ein Update ist verfügbar!'
        if (dockerUpdates && gitUpdates) {
          detail = 'Neue Version und Docker Images verfügbar!'
        } else if (dockerUpdates) {
          detail = 'Neue Docker Images verfügbar!'
        } else if (gitUpdates) {
          detail = `Version ${updateRes.data.latest_version} verfügbar!`
        }

        toast.add({
          severity: 'info',
          summary: 'Update verfügbar',
          detail: detail,
          life: 10000
        })

        // Show update dialog (Popup)
        showUpdateHelpDialog.value = true

        // Remember that we saw this version
        localStorage.setItem('last_seen_update_version', currentLatest)
      }
    }
  } catch (e) {
    // Silent fail for status check
    console.error('Status load failed', e)
  } finally {
    statusLoading.value = false
  }
}

const checkUpdates = async () => {
  checkingUpdates.value = true
  try {
    const res = await api.get('/api/check-update')
    updateStatus.value = res.data
    if (res.data.update_available) {
      toast.add({
        severity: 'info',
        summary: 'Update verfügbar',
        detail: `Version ${res.data.latest_version} ist verfügbar.`,
        life: 5000
      })
    } else {
      toast.add({
        severity: 'success',
        summary: 'System aktuell',
        detail: 'Keine Updates gefunden.',
        life: 3000
      })
    }
  } catch (e) {
    console.error(e)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Update-Prüfung fehlgeschlagen',
      life: 3000
    })
  } finally {
    checkingUpdates.value = false
  }
}

const savePassword = () => {
  showPasswordDialog.value = false
  saveConfig()
}

const loadAiStatus = async () => {
  try {
    const res = await api.get('/api/ai/status')
    aiStatus.value = res.data
  } catch (e) {
    console.error('Failed to load AI status', e)
  }
}

const loadTelemetryStatus = async () => {
  try {
    const res = await api.get('/api/telemetry/status')
    telemetryStatus.value = res.data

    // Load admin-specific data if admin (parallel for better performance)
    if (res.data.is_admin) {
      await Promise.all([
        fetchAdminHealth(),
        fetchAdminInstallations(),
        fetchAdminModels(),
        fetchAdminMetrics(),
        fetchTrainingInfo(),
        fetchRuntimeLimits(),
        fetchPermissionPresets()
      ])

      // Start auto-refresh for admin data
      startAdminAutoRefresh()
    }
  } catch (e) {
    console.error('Failed to load Telemetry status', e)
  }
}

const startAdminAutoRefresh = () => {
  // Clear existing interval if any
  if (adminAutoRefreshInterval) {
    clearInterval(adminAutoRefreshInterval)
  }

  // Set up auto-refresh every 30 seconds
  adminAutoRefreshInterval = setInterval(async () => {
    if (adminAutoRefresh.value && telemetryStatus.value?.is_admin) {
      if (adminRefreshInFlight) return
      adminRefreshInFlight = true
      try {
        await Promise.all([
          fetchAdminHealth(),
          fetchAdminInstallations(),
          fetchAdminModels(),
          fetchAdminMetrics(),
          fetchTrainingInfo(),
          fetchRuntimeLimits()
        ])
      } catch (e) {
        console.error('Auto-refresh failed', e)
      } finally {
        adminRefreshInFlight = false
      }
    }
  }, 30000) // 30 seconds
}

const toggleAdminAutoRefresh = () => {
  adminAutoRefresh.value = !adminAutoRefresh.value
  if (adminAutoRefresh.value) {
    startAdminAutoRefresh()
  }
}

const manualSubmitTelemetry = async () => {
  submittingTelemetry.value = true
  try {
    const res = await api.post('/api/telemetry/submit')
    toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 })
    loadTelemetryStatus()
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.message || e.message,
      life: 5000
    })
  } finally {
    submittingTelemetry.value = false
  }
}

const manualCheckModel = async () => {
  checkingModel.value = true
  try {
    const res = await api.post('/api/telemetry/check')
    toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 })
    loadTelemetryStatus()
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || e.message,
      life: 5000
    })
  } finally {
    checkingModel.value = false
  }
}

const retrieveTelemetryCredentials = async () => {
  try {
    const res = await api.post('/api/telemetry/retrieve_credentials')
    if (res.data?.status) {
      telemetryStatus.value = res.data.status
    }
    await loadTelemetryStatus()
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: res.data?.message || 'Telemetry-Zugangsdaten aktualisiert',
      life: 3000
    })
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.message || e.response?.data?.error || e.message,
      life: 5000
    })
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const payload = {
      idm_host: config.value.idm.host,
      idm_port: config.value.idm.port,
      hp_model: config.value.hp_model,
      circuits: config.value.idm.circuits,
      zones: config.value.idm.zones,
      metrics_url: config.value.metrics.url,
      write_enabled: config.value.web.write_enabled,
      logging_interval: config.value.logging.interval,
      realtime_mode: config.value.logging.realtime_mode,
      mqtt_enabled: config.value.mqtt?.enabled || false,
      mqtt_broker: config.value.mqtt?.broker || '',
      mqtt_port: config.value.mqtt?.port || 1883,
      mqtt_username: config.value.mqtt?.username || '',
      mqtt_password: mqttPassword.value || undefined,
      mqtt_topic_prefix: config.value.mqtt?.topic_prefix || 'idm/heatpump',
      mqtt_qos: config.value.mqtt?.qos || 0,
      mqtt_use_tls: config.value.mqtt?.use_tls || false,
      mqtt_tls_ca_cert: config.value.mqtt?.tls_ca_cert || '',
      mqtt_publish_interval: config.value.mqtt?.publish_interval || 60,
      mqtt_ha_discovery_enabled: config.value.mqtt?.ha_discovery_enabled || false,
      mqtt_ha_discovery_prefix: config.value.mqtt?.ha_discovery_prefix || 'homeassistant',
      network_security_enabled: config.value.network_security?.enabled || false,
      network_security_whitelist: whitelistText.value,
      network_security_blacklist: blacklistText.value,
      signal_enabled: config.value.signal?.enabled || false,
      signal_sender: config.value.signal?.sender || '',
      signal_cli_path: config.value.signal?.cli_path || 'signal-cli',
      signal_recipients: signalRecipientsText.value,
      telegram_enabled: config.value.telegram?.enabled || false,
      telegram_bot_token: config.value.telegram?.bot_token || '',
      telegram_chat_ids: telegramChatIdsText.value,
      discord_enabled: config.value.discord?.enabled || false,
      discord_webhook_url: config.value.discord?.webhook_url || '',
      email_enabled: config.value.email?.enabled || false,
      email_smtp_server: config.value.email?.smtp_server || '',
      email_smtp_port: config.value.email?.smtp_port || 587,
      email_username: config.value.email?.username || '',
      email_password: emailPassword.value || undefined,
      email_sender: config.value.email?.sender || '',
      email_recipients: emailRecipientsText.value,
      webdav_enabled: config.value.webdav?.enabled || false,
      webdav_url: config.value.webdav?.url || '',
      webdav_username: config.value.webdav?.username || '',
      webdav_password: webdavPassword.value || undefined,
      ai_enabled: config.value.ai?.enabled || false,
      ai_sensitivity: config.value.ai?.sensitivity || 3.0,
      ai_model: config.value.ai?.model || 'rolling',
      telemetry_enabled: config.value.telemetry?.enabled || false,
      telemetry_auth_token: normalizeTokenValue(config.value.telemetry?.auth_token),
      telemetry_admin_auth_token: normalizeTokenValue(config.value.telemetry?.admin_auth_token),
      telemetry_server_url: config.value.telemetry?.server_url || '',
      updates_enabled: config.value.updates?.enabled || false,
      updates_interval_hours: config.value.updates?.interval_hours || 12,
      updates_mode: config.value.updates?.mode || 'apply',
      updates_target: config.value.updates?.target || 'all',
      backup_enabled: config.value.backup?.enabled || false,
      backup_interval: config.value.backup?.interval || 24,
      backup_retention: config.value.backup?.retention || 10,
      backup_auto_upload: config.value.backup?.auto_upload || false,
      new_password: newPassword.value || undefined
    }
    const res = await api.post('/api/config', payload)
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: res.data.message || 'Einstellungen erfolgreich gespeichert',
      life: 3000
    })
    newPassword.value = ''
    confirmPassword.value = ''
    mqttPassword.value = ''
    webdavPassword.value = ''
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || e.message,
      life: 5000
    })
  } finally {
    saving.value = false
  }
}

const confirmRestart = () => {
  confirm.require({
    message: 'Bist du sicher, dass du den Dienst neu starten möchtest?',
    header: 'Bestätigung',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        const res = await api.post('/api/restart')
        toast.add({ severity: 'info', summary: 'Neustart', detail: res.data.message, life: 3000 })
      } catch (e) {
        console.error(e)
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: 'Neustart fehlgeschlagen',
          life: 3000
        })
      }
    }
  })
}

// Backup & Restore functions
const loadBackups = async () => {
  loadingBackups.value = true
  try {
    const res = await api.get('/api/backup/list')
    backups.value = res.data.backups || []
  } catch (e) {
    console.error(e)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Backups konnten nicht geladen werden',
      life: 3000
    })
  } finally {
    loadingBackups.value = false
  }
}

const createBackup = async () => {
  creatingBackup.value = true
  try {
    const res = await api.post('/api/backup/create')
    if (res.data.success) {
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: `Backup erstellt: ${res.data.filename}`,
        life: 3000
      })
      loadBackups()
    } else {
      toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 3000 })
    }
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || 'Backup Erstellung fehlgeschlagen',
      life: 3000
    })
  } finally {
    creatingBackup.value = false
  }
}

const downloadBackup = async (filename) => {
  try {
    const response = await api.get(`/api/backup/download/${filename}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Backup heruntergeladen',
      life: 2000
    })
  } catch (e) {
    console.error(e)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Backup Download fehlgeschlagen',
      life: 3000
    })
  }
}

const uploadToCloud = async (filename) => {
  try {
    toast.add({ severity: 'info', summary: 'Info', detail: 'Upload gestartet...', life: 2000 })
    const res = await api.post(`/api/backup/upload/${filename}`)
    if (res.data.success) {
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Backup erfolgreich hochgeladen',
        life: 3000
      })
    } else {
      toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 5000 })
    }
  } catch (e) {
    console.error(e)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || 'Upload fehlgeschlagen',
      life: 5000
    })
  }
}

const confirmDeleteBackup = (filename) => {
  confirm.require({
    message: `Backup "${filename}" löschen?`,
    header: 'Backup Löschen',
    icon: 'pi pi-trash',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete(`/api/backup/delete/${filename}`)
        toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Backup gelöscht', life: 2000 })
        loadBackups()
      } catch (e) {
        console.error(e)
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: 'Backup löschen fehlgeschlagen',
          life: 3000
        })
      }
    }
  })
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  selectedFile.value = file
}

const restoreFromFile = async () => {
  if (!selectedFile.value) return

  confirm.require({
    message:
      'Konfiguration aus hochgeladener Datei wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!',
    header: 'Aus Datei Wiederherstellen',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-warning',
    accept: async () => {
      restoringBackup.value = true
      try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        formData.append('restore_secrets', 'false')

        const res = await api.post('/api/backup/restore', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (res.data.success) {
          toast.add({
            severity: 'success',
            summary: 'Erfolg',
            detail: res.data.message,
            life: 5000
          })
          selectedFile.value = null
          if (fileInput.value) fileInput.value.value = ''
          setTimeout(() => location.reload(), 2000)
        } else {
          toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 5000 })
        }
      } catch (e) {
        toast.add({
          severity: 'error',
          summary: 'Fehler',
          detail: e.response?.data?.error || 'Wiederherstellung fehlgeschlagen',
          life: 5000
        })
      } finally {
        restoringBackup.value = false
      }
    }
  })
}

const confirmDeleteDatabase = async () => {
  if (deleteConfirmationText.value !== 'DELETE') return

  deletingDatabase.value = true
  try {
    const res = await api.post('/api/database/delete')
    if (res.data.success) {
      toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 5000 })
      showDeleteDialog.value = false
      deleteConfirmationText.value = ''
    } else {
      toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 5000 })
    }
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: e.response?.data?.error || 'Datenbank löschen fehlgeschlagen',
      life: 5000
    })
  } finally {
    deletingDatabase.value = false
  }
}
</script>

<style scoped>
/* Counter transition animations */
.counter-enter-active,
.counter-leave-active {
  transition: all 0.3s ease;
}

.counter-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.counter-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

.counter-enter-to,
.counter-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}
</style>
