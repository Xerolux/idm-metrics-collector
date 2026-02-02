<template>
  <div class="p-4 flex flex-col gap-4 h-[calc(100vh-2rem)] overflow-hidden">
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
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2">
              Verbindung & Daten
            </h2>

            <Fieldset legend="IDM Wärmepumpe" :toggleable="true">
              <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Installation</label>
                  <div class="flex items-center gap-2">
                    <div class="p-inputgroup flex-1">
                      <span class="p-inputgroup-addon">ID</span>
                      <InputText v-model="config.installation_id" readonly class="w-full font-mono bg-gray-800" />
                      <Button icon="pi pi-copy" severity="secondary" @click="copyId" />
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
                  <label class="font-bold text-sm text-gray-300">Abfrage-Intervall (Sekunden)</label>
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
                  <Checkbox v-model="config.telemetry.enabled" binary />
                  <span class="font-bold">Community Modell nutzen</span>
                </div>
              </template>

              <div v-if="config.telemetry.enabled" class="flex flex-col gap-6">
                <div class="bg-purple-900/20 border border-purple-600/50 p-4 rounded flex flex-col gap-3">
                  <div class="flex items-start gap-3">
                    <i class="pi pi-users text-purple-400 text-xl mt-1"></i>
                    <div class="text-sm text-purple-200">
                      Durch die Teilnahme am Community-Programm hilfst du, das Anomalie-Erkennungsmodell für alle zu verbessern.
                      Deine Daten werden anonymisiert (IP-Masking) übertragen.
                      <br><br>
                      <strong>Vorteil:</strong> Du erhältst Zugriff auf vortrainierte Modelle ("Community Model"), die auf Daten vieler Wärmepumpen basieren.
                      Dies ist besonders hilfreich, wenn du noch nicht genügend eigene Daten (weniger als 1 Woche) hast.
                    </div>
                  </div>
                  <div class="flex justify-end">
                    <Button label="Datenschutz-Details" icon="pi pi-shield" size="small" text @click="privacyDialog.open()" />
                  </div>
                </div>

                <div class="flex flex-col gap-2">
                  <label class="font-bold text-sm text-gray-300">Telemetry Server URL</label>
                  <div
                    class="p-2 bg-gray-900 rounded border border-gray-700 font-mono text-gray-400"
                  >
                    https://collector.xerolux.de
                  </div>
                  <small class="text-gray-400"
                    >Standard: https://collector.xerolux.de (Community Server). Dieser
                    Wert ist fest eingestellt.</small
                  >
                </div>

                <!-- Admin Status Indicator -->
                <div class="flex items-center gap-2" v-if="telemetryStatus">
                  <span class="font-bold text-sm text-gray-300">Status:</span>
                  <span
                    v-if="telemetryStatus.is_admin"
                    class="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-500 border border-yellow-500/50 text-xs font-bold uppercase"
                  >
                    <i class="pi pi-crown mr-1"></i> Admin
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
                      <span class="font-mono truncate max-w-[150px]">{{ telemetryStatus.server_url }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Letzte Übertragung:</span>
                      <span class="font-mono">{{ telemetryStatus.last_submission ? new Date(telemetryStatus.last_submission * 1000).toLocaleString() : 'Nie' }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Letzter Modell-Check:</span>
                      <span class="font-mono">{{ telemetryStatus.last_model_check ? new Date(telemetryStatus.last_model_check * 1000).toLocaleString() : 'Nie' }}</span>
                    </div>
                    <div class="flex justify-between border-b border-gray-700 py-2">
                      <span class="text-gray-300">Manuelle Downloads heute:</span>
                      <span class="font-mono">{{ telemetryStatus.manual_downloads_today }} / 3</span>
                    </div>
                  </div>
                  <div class="flex flex-wrap gap-2 mt-4">
                    <Button label="Daten jetzt senden" icon="pi pi-upload" size="small" severity="secondary" @click="manualSubmitTelemetry" :loading="submittingTelemetry" />
                    <Button label="Modell prüfen & laden" icon="pi pi-download" size="small" severity="help" @click="manualCheckModel" :loading="checkingModel" :disabled="telemetryStatus?.manual_downloads_today >= 3" />
                  </div>
                </div>
              </div>
            </Fieldset>
          </div>

          <!-- MQTT -->
          <div v-if="activeCategory === 'mqtt'" class="flex flex-col gap-6">
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2">
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
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2">
              Benachrichtigungen
            </h2>

            <Fieldset legend="Signal Messenger" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.signal.enabled" binary />
                  <span class="font-bold">Signal</span>
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
                  <label class="font-bold text-sm text-gray-300">Empfänger (Pro Zeile eine Nummer)</label>
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
                  <Checkbox v-model="config.telegram.enabled" binary />
                  <span class="font-bold">Telegram</span>
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
                  <Checkbox v-model="config.discord.enabled" binary />
                  <span class="font-bold">Discord</span>
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
                  <Checkbox v-model="config.email.enabled" binary />
                  <span class="font-bold">E-Mail</span>
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
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2">KI-Analyse</h2>

            <Fieldset legend="KI & Anomalieerkennung" :toggleable="true">
              <template #legend>
                <div class="flex items-center gap-2">
                  <Checkbox v-model="config.ai.enabled" binary />
                  <span class="font-bold">KI-Analyse Status anzeigen</span>
                </div>
              </template>
              <div v-if="config.ai.enabled" class="flex flex-col gap-6">
                <div
                  class="bg-blue-900/20 border border-blue-600/50 p-4 rounded flex items-start gap-3"
                >
                  <i class="pi pi-info-circle text-blue-400 text-xl mt-1"></i>
                  <div class="text-sm text-blue-200">
                    Die Anomalieerkennung läuft nun als eigenständiger
                    <strong>ml-service</strong> Container. Er nutzt die "HalfSpaceTrees" Methode
                    (via Python <code>river</code>), um kontinuierlich aus dem Datenstrom zu lernen.
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
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2">Sicherheit</h2>

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
                  <Checkbox v-model="config.network_security.enabled" binary />
                  <span class="font-bold">IP Whitelist/Blacklist</span>
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
            <h2 class="text-xl font-bold border-b border-surface-700 pb-2 mb-2">
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
                    <div class="font-mono text-white font-semibold">{{ updateStatus.current_version || 'v0.0.0' }}</div>
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
                    Automatische Updates sind deaktiviert. Bitte führen Sie das Update manuell durch.
                  </p>
                </div>

                <!-- Update Info -->
                <div class="bg-gray-900/50 p-3 rounded mt-2">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-sync text-green-400"></i>
                    <span class="text-sm font-bold text-white">Manuelle Updates</span>
                  </div>
                  <p class="text-sm text-gray-100 mb-2">
                    Es werden keine automatischen Updates mehr durchgeführt.
                    Neue Versionen müssen manuell über die Konsole installiert werden.
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
                      />
                      <Button
                        icon="pi pi-download"
                        text
                        size="small"
                        @click="downloadBackup(backup.filename)"
                      />
                      <Button
                        icon="pi pi-trash"
                        text
                        severity="danger"
                        size="small"
                        @click="confirmDeleteBackup(backup.filename)"
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
              <h2 class="text-xl font-bold flex items-center gap-2">
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
                />
              </div>
            </div>

            <div v-if="telemetryStatus?.server_stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <!-- Global Stats -->
              <div class="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col items-center transition-all duration-300 hover:border-blue-500">
                <i class="pi pi-database text-4xl text-blue-400 mb-2"></i>
                <transition name="counter" mode="out-in">
                  <div :key="telemetryStatus.server_stats.total_points" class="text-3xl font-bold">
                    {{ telemetryStatus.server_stats.total_points?.toLocaleString() || 0 }}
                  </div>
                </transition>
                <div class="text-gray-300 uppercase text-xs tracking-wider mt-1">Total Data Points</div>
              </div>

              <div class="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col items-center transition-all duration-300 hover:border-green-500">
                <i class="pi pi-desktop text-4xl text-green-400 mb-2"></i>
                <transition name="counter" mode="out-in">
                  <div :key="telemetryStatus.server_stats.active_installations" class="text-3xl font-bold">
                    {{ telemetryStatus.server_stats.active_installations || 0 }}
                  </div>
                </transition>
                <div class="text-gray-300 uppercase text-xs tracking-wider mt-1">Active Installations</div>
              </div>

              <div class="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col items-center transition-all duration-300 hover:border-purple-500">
                 <i class="pi pi-box text-4xl text-purple-400 mb-2"></i>
                 <transition name="counter" mode="out-in">
                   <div :key="telemetryStatus.server_stats.models?.length" class="text-3xl font-bold">
                     {{ telemetryStatus.server_stats.models?.length || 0 }}
                   </div>
                 </transition>
                 <div class="text-gray-300 uppercase text-xs tracking-wider mt-1">Generated Models</div>
              </div>
            </div>

            <Fieldset legend="Available Models" :toggleable="true" v-if="adminModels">
              <div class="mb-3 text-sm text-gray-400">
                Showing {{ adminModels.total || 0 }} model(s), Total Size: {{ adminModels.models?.reduce((sum, m) => sum + m.size_mb, 0).toFixed(2) || 0 }} MB
              </div>
              <div class="grid grid-cols-1 gap-4">
                <div v-for="model in adminModels.models" :key="model.filename"
                     class="bg-gray-900/50 p-4 rounded border border-gray-700 flex justify-between items-center">
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
                    />
                  </div>
                </div>
                <div v-if="!adminModels.models || !adminModels.models.length" class="text-gray-500 italic text-center p-4">
                  No models available yet. Models will be generated automatically when enough data is collected.
                </div>
              </div>
            </Fieldset>

            <!-- Model Downloads Chart -->
            <Fieldset legend="Model Downloads" :toggleable="true" v-if="adminModels && adminModels.models?.some(m => m.download_count > 0)">
              <div class="mb-3 text-sm text-gray-400">
                Top 10 most downloaded models
              </div>
              <div class="bg-gray-900/50 p-4 rounded border border-gray-700" style="height: 300px;">
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
                    <i v-if="adminHealth.victoriametrics?.healthy" class="pi pi-check-circle text-green-400 ml-auto"></i>
                    <i v-else class="pi pi-times-circle text-red-400 ml-auto"></i>
                  </div>
                  <div class="text-sm space-y-1">
                    <div class="flex justify-between"><span class="text-gray-400">Hostname:</span> <span>{{ adminHealth.server?.hostname || 'N/A' }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">Uptime:</span> <span>{{ adminHealth.server?.uptime_formatted || 'N/A' }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">CPU:</span> <span>{{ adminHealth.server?.cpu_percent?.toFixed(1) }}%</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">RAM:</span> <span>{{ adminHealth.server?.memory?.used_gb?.toFixed(1) }}GB / {{ adminHealth.server?.memory?.total_gb?.toFixed(1) }}GB ({{ adminHealth.server?.memory?.percent }}%)</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">Disk:</span> <span>{{ adminHealth.server?.disk?.used_gb?.toFixed(1) }}GB / {{ adminHealth.server?.disk?.total_gb?.toFixed(1) }}GB ({{ adminHealth.server?.disk?.percent }}%)</span></div>
                  </div>
                </div>
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-database text-purple-400"></i>
                    <span class="font-bold">Models</span>
                  </div>
                  <div class="text-sm space-y-1">
                    <div class="flex justify-between"><span class="text-gray-400">Count:</span> <span>{{ adminHealth.models?.count || 0 }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">Total Size:</span> <span>{{ adminHealth.models?.total_size_mb?.toFixed(2) }} MB</span></div>
                    <div class="flex justify-between"><span class="text-gray-400">VictoriaMetrics:</span> <span :class="adminHealth.victoriametrics?.healthy ? 'text-green-400' : 'text-red-400'">{{ adminHealth.victoriametrics?.healthy ? 'Healthy' : 'Down' }}</span></div>
                  </div>
                </div>
              </div>
              <div class="flex gap-2 mt-2">
                <Button
                  label="Refresh Data"
                  icon="pi pi-refresh"
                  @click="async () => { await Promise.all([fetchAdminModels(), fetchAdminHealth(), fetchAdminInstallations(), fetchAdminMetrics()]); }"
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

            <!-- Installations List -->
            <Fieldset legend="Active Installations" :toggleable="true" v-if="adminInstallations">
              <div class="text-sm text-gray-400 mb-2">Showing {{ adminInstallations.showing }} of {{ adminInstallations.total }} installations</div>
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-gray-700">
                      <th class="text-left py-2 px-3">Installation ID</th>
                      <th class="text-right py-2 px-3">Data Points</th>
                      <th class="text-right py-2 px-3">Last Seen</th>
                      <th class="text-center py-2 px-3">Admin</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="inst in adminInstallations.installations" :key="inst.installation_id" class="border-b border-gray-800 hover:bg-gray-800/50">
                      <td class="py-2 px-3 font-mono text-xs">{{ inst.installation_id.substring(0, 20) }}...</td>
                      <td class="py-2 px-3 text-right">{{ inst.data_points?.toLocaleString() || 0 }}</td>
                      <td class="py-2 px-3 text-right">{{ inst.last_seen_formatted || 'Unknown' }}</td>
                      <td class="py-2 px-3 text-center">
                        <i v-if="inst.is_admin" class="pi pi-crown text-yellow-500"></i>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
                  <div class="text-2xl font-bold">{{ adminMetrics.requests?.total?.toLocaleString() || 0 }}</div>
                  <div class="text-xs text-gray-400 mt-1">Total Requests</div>
                  <div class="text-xs text-red-400 mt-1">{{ adminMetrics.requests?.errors || 0 }} Errors</div>
                </div>

                <!-- Data Submissions -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-upload text-green-400 text-xl"></i>
                    <span class="font-bold">Submissions</span>
                  </div>
                  <div class="text-2xl font-bold">{{ adminMetrics.business?.submissions?.toLocaleString() || 0 }}</div>
                  <div class="text-xs text-gray-400 mt-1">Data Submissions</div>
                  <div class="text-xs text-gray-400 mt-1">{{ adminMetrics.business?.data_points?.toLocaleString() || 0 }} Points</div>
                </div>

                <!-- Cache Performance -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-bolt text-yellow-400 text-xl"></i>
                    <span class="font-bold">Cache</span>
                  </div>
                  <div class="text-2xl font-bold">{{ adminMetrics.cache?.hit_rate?.toFixed(1) || 0 }}%</div>
                  <div class="text-xs text-gray-400 mt-1">Hit Rate</div>
                  <div class="text-xs text-gray-400 mt-1">{{ adminMetrics.cache?.hits?.toLocaleString() || 0 }} Hits / {{ adminMetrics.cache?.misses?.toLocaleString() || 0 }} Misses</div>
                </div>

                <!-- Rate Limits -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-ban text-red-400 text-xl"></i>
                    <span class="font-bold">Rate Limits</span>
                  </div>
                  <div class="text-2xl font-bold">{{ adminMetrics.requests?.rate_limit_hits?.toLocaleString() || 0 }}</div>
                  <div class="text-xs text-gray-400 mt-1">Total Violations</div>
                </div>

                <!-- Model Downloads -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-download text-purple-400 text-xl"></i>
                    <span class="font-bold">Downloads</span>
                  </div>
                  <div class="text-2xl font-bold">{{ adminMetrics.business?.model_downloads?.toLocaleString() || 0 }}</div>
                  <div class="text-xs text-gray-400 mt-1">Model Downloads</div>
                </div>

                <!-- Training Runs -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-cog text-cyan-400 text-xl"></i>
                    <span class="font-bold">Training</span>
                  </div>
                  <div class="text-2xl font-bold">{{ adminMetrics.business?.training_runs?.toLocaleString() || 0 }}</div>
                  <div class="text-xs text-gray-400 mt-1">Total Runs</div>
                </div>

                <!-- Active Installations (from metrics) -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-users text-teal-400 text-xl"></i>
                    <span class="font-bold">Installations</span>
                  </div>
                  <div class="text-2xl font-bold">{{ adminMetrics.business?.active_installations?.toLocaleString() || telemetryStatus.server_stats?.active_installations || 0 }}</div>
                  <div class="text-xs text-gray-400 mt-1">Active (30d)</div>
                </div>

                <!-- Error Rate -->
                <div class="bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex items-center gap-2 mb-2">
                    <i class="pi pi-exclamation-triangle text-orange-400 text-xl"></i>
                    <span class="font-bold">Error Rate</span>
                  </div>
                  <div class="text-2xl font-bold">
                    {{ (adminMetrics.requests?.total > 0 ? (adminMetrics.requests.errors / adminMetrics.requests.total * 100).toFixed(2) : 0) }}%
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
                      :options="adminModels?.models?.map(m => m.name) || models.map(m => m.value)"
                      placeholder="Select Model"
                      class="w-full"
                      editable
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm text-gray-300">Metrics (comma separated)</label>
                    <InputText v-model="statsMetrics" placeholder="cop_current, temp_outdoor" class="w-full" />
                  </div>
                </div>

                <Button
                  label="Analyze Community Data"
                  icon="pi pi-chart-bar"
                  @click="fetchCommunityAverages"
                  :loading="statsLoading"
                  class="w-full md:w-auto self-start"
                />

                <div v-if="communityStats" class="mt-4 bg-gray-900/50 p-4 rounded border border-gray-700">
                  <div class="flex justify-between items-center mb-4 border-b border-gray-700 pb-2">
                    <div>
                      <span class="text-gray-400 text-sm">Model:</span>
                      <span class="ml-2 font-bold">{{ communityStats.model }}</span>
                    </div>
                    <div>
                      <span class="text-gray-400 text-sm">Sample Size:</span>
                      <span class="ml-2 font-bold text-blue-400">{{ communityStats.sample_size }}</span>
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
                        <tr v-for="(stats, metric) in communityStats.metrics" :key="metric" class="border-b border-gray-800 last:border-0">
                          <td class="py-2 font-mono text-gray-300">{{ metric }}</td>
                          <td class="py-2 text-right font-mono">{{ stats.avg?.toFixed(2) ?? '-' }}</td>
                          <td class="py-2 text-right font-mono text-gray-500">{{ stats.min?.toFixed(2) ?? '-' }}</td>
                          <td class="py-2 text-right font-mono text-gray-500">{{ stats.max?.toFixed(2) ?? '-' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </Fieldset>

            <div class="bg-yellow-900/20 border border-yellow-600/50 p-4 rounded flex items-start gap-3">
              <i class="pi pi-info-circle text-yellow-500 text-xl mt-1"></i>
              <div class="text-sm text-yellow-200">
                You are authenticated as a <strong>Community Admin</strong>. This tab provides exclusive insights into the telemetry server status and model generation pipeline.
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
            Die automatische Aktualisierung (Watchtower) wurde entfernt.
            Bitte führen Sie Updates manuell über die Konsole aus, um die neuesten Funktionen und Sicherheitsverbesserungen zu erhalten.
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

    <Toast />
    <ConfirmDialog />
    <PrivacyPolicyDialog ref="privacyDialog" />
  </div>
</template>

<script setup>
// Xerolux 2026
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
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
  telemetry: { enabled: true, auth_token: '', server_url: '' },
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
const selectedStatsModel = ref(null)
const statsMetrics = ref('cop_current, temp_outdoor')
const modelDeleting = ref(false)
const trainingInProgress = ref(false)
const adminAutoRefresh = ref(true)
let adminAutoRefreshInterval = null
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

const copyId = async () => {
  const success = await copyToClipboard(config.value.installation_id)
  if (success) {
    toast.add({ severity: 'info', summary: 'Kopiert', detail: 'ID in Zwischenablage kopiert', life: 2000 })
  } else {
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'Konnte nicht kopiert werden', life: 3000 })
  }
}

// ==================== ADMIN FUNCTIONS ====================

const fetchAdminHealth = async () => {
  if (!telemetryStatus.value?.is_admin) return

  try {
    const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
    const res = await axios.get(`${telemetryUrl}/api/v1/admin/health`, {
      params: { installation_id: config.value.installation_id }
    })
    adminHealth.value = res.data
  } catch (err) {
    console.error('Failed to fetch admin health:', err)
  }
}

const fetchAdminInstallations = async () => {
  if (!telemetryStatus.value?.is_admin) return

  try {
    const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
    const res = await axios.get(`${telemetryUrl}/api/v1/admin/installations`, {
      params: { installation_id: config.value.installation_id, limit: 50 }
    })
    adminInstallations.value = res.data
  } catch (err) {
    console.error('Failed to fetch admin installations:', err)
  }
}

const fetchAdminModels = async () => {
  if (!telemetryStatus.value?.is_admin) return

  try {
    const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
    const res = await axios.get(`${telemetryUrl}/api/v1/admin/models`, {
      params: { installation_id: config.value.installation_id }
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
    .filter(m => m.download_count > 0)
    .sort((a, b) => b.download_count - a.download_count)
    .slice(0, 10) // Show top 10

  if (models.length === 0) {
    // No downloads yet
    return
  }

  const labels = models.map(m => m.name)
  const data = models.map(m => m.download_count)

  // Create new chart
  modelDownloadsChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Downloads',
        data: data,
        backgroundColor: 'rgba(59, 130, 246, 0.7)', // Blue
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1
      }]
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
    const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
    const res = await axios.get(`${telemetryUrl}/api/v1/admin/metrics`, {
      params: { installation_id: config.value.installation_id }
    })
    adminMetrics.value = res.data
  } catch (err) {
    console.error('Failed to fetch admin metrics:', err)
  }
}

const fetchCommunityAverages = async () => {
  if (!selectedStatsModel.value) {
    toast.add({ severity: 'warn', summary: 'Warnung', detail: 'Bitte wähle ein Modell', life: 3000 })
    return
  }

  statsLoading.value = true
  communityStats.value = null

  try {
    const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
    const headers = {}
    if (config.value.telemetry?.auth_token) {
      headers['Authorization'] = `Bearer ${config.value.telemetry.auth_token}`
    }

    const res = await axios.get(`${telemetryUrl}/api/v1/community/averages`, {
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
        const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
        await axios.delete(`${telemetryUrl}/api/v1/admin/models/${encodeURIComponent(modelName)}`, {
          params: { installation_id: config.value.installation_id }
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
          detail: 'Modell konnte nicht gelöscht werden: ' + (err.response?.data?.detail || err.message),
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
    const telemetryUrl = config.value.telemetry?.url || 'https://collector.xerolux.de'
    const res = await axios.post(`${telemetryUrl}/api/v1/admin/models/trigger-training`, null, {
      params: { installation_id: config.value.installation_id }
    })

    if (res.data.success) {
      toast.add({
        severity: 'success',
        summary: 'Training gestartet',
        detail: 'Modell-Training wurde manuell ausgelöst',
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
      detail: 'Training konnte nicht gestartet werden: ' + (err.response?.data?.detail || err.message),
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
    const res = await axios.get('/api/config')
    config.value = res.data

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
      const ipRes = await axios.get('/api/health')
      currentClientIP.value = ipRes.data.client_ip || 'Unbekannt'
    } catch (e) {
      console.error('Failed to get client IP', e)
    }

    // Load models
    try {
      const infoRes = await axios.get('/api/info')
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
    const res = await axios.post('/api/signal/test', {
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
    const res = await axios.get('/api/check-update')
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
    const res = await axios.get('/api/ai/status')
    aiStatus.value = res.data
  } catch (e) {
    console.error('Failed to load AI status', e)
  }
}

const loadTelemetryStatus = async () => {
  try {
    const res = await axios.get('/api/telemetry/status')
    telemetryStatus.value = res.data

    // Load admin-specific data if admin (parallel for better performance)
    if (res.data.is_admin) {
      await Promise.all([
        fetchAdminHealth(),
        fetchAdminInstallations(),
        fetchAdminModels(),
        fetchAdminMetrics()
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
      try {
        await Promise.all([
          fetchAdminHealth(),
          fetchAdminInstallations(),
          fetchAdminModels(),
          fetchAdminMetrics()
        ])
      } catch (e) {
        console.error('Auto-refresh failed', e)
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
    const res = await axios.post('/api/telemetry/submit')
    toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 })
    loadTelemetryStatus()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.message || e.message, life: 5000 })
  } finally {
    submittingTelemetry.value = false
  }
}

const manualCheckModel = async () => {
  checkingModel.value = true
  try {
    const res = await axios.post('/api/telemetry/check')
    toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 })
    loadTelemetryStatus()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 })
  } finally {
    checkingModel.value = false
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
      telemetry_auth_token: config.value.telemetry?.auth_token || '',
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
    const res = await axios.post('/api/config', payload)
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
        const res = await axios.post('/api/restart')
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
    const res = await axios.get('/api/backup/list')
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
    const res = await axios.post('/api/backup/create')
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
    const response = await axios.get(`/api/backup/download/${filename}`, {
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
    const res = await axios.post(`/api/backup/upload/${filename}`)
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
        await axios.delete(`/api/backup/delete/${filename}`)
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

        const res = await axios.post('/api/backup/restore', formData, {
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
    const res = await axios.post('/api/database/delete')
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
