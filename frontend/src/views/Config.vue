<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Konfiguration</h1>

        <div v-if="loading" class="flex justify-center">
            <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else>
            <TabView :scrollable="true">
                <TabPanel header="Verbindung">
                     <div class="flex flex-col gap-6">
                        <Fieldset legend="IDM Wärmepumpe" :toggleable="true">
                             <div class="flex flex-col gap-4">
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div class="flex flex-col gap-2">
                                        <label>Host / IP</label>
                                        <InputText v-model="config.idm.host" class="w-full" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Port</label>
                                        <InputNumber v-model="config.idm.port" :useGrouping="false" class="w-full" />
                                    </div>
                                </div>

                                <div class="flex flex-col gap-2">
                                    <label class="font-bold">Aktivierte Heizkreise</label>
                                    <div class="flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50">
                                        <div class="flex items-center gap-2">
                                            <Checkbox v-model="config.idm.circuits" inputId="circuitA" value="A" disabled />
                                            <label for="circuitA" class="opacity-50">Heizkreis A (Fest)</label>
                                        </div>
                                        <div v-for="c in ['B', 'C', 'D', 'E', 'F', 'G']" :key="c" class="flex items-center gap-2">
                                            <Checkbox v-model="config.idm.circuits" :inputId="'circuit'+c" :value="c" />
                                            <label :for="'circuit'+c">Heizkreis {{ c }}</label>
                                        </div>
                                    </div>
                                </div>

                                 <div class="flex flex-col gap-2">
                                    <label class="font-bold">Zonenmodule</label>
                                    <div class="flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50">
                                        <div v-for="z in 10" :key="z" class="flex items-center gap-2">
                                            <Checkbox v-model="config.idm.zones" :inputId="'zone'+(z-1)" :value="(z-1)" />
                                            <label :for="'zone'+(z-1)">Zone {{ z }}</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Fieldset>

                        <Fieldset legend="Datenbank (VictoriaMetrics)" :toggleable="true">
                            <div class="flex flex-col gap-4">
                                <div class="flex flex-col gap-2">
                                    <label>Write URL</label>
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
                                         <label for="realtime_mode" class="font-bold cursor-pointer">Echtzeit-Modus</label>
                                         <span class="text-sm text-gray-400">Aktualisierung im Sekundentakt (Hohe Last)</span>
                                    </div>
                                </div>
                                <div class="flex flex-col gap-2" v-if="!config.logging.realtime_mode">
                                    <label>Abfrage-Intervall (Sekunden)</label>
                                    <InputNumber v-model="config.logging.interval" :min="1" :max="3600" :useGrouping="false" class="w-full md:w-1/2" />
                                    <small class="text-gray-400">Standard: 60 Sekunden</small>
                                </div>
                            </div>
                        </Fieldset>
                    </div>
                </TabPanel>

                <TabPanel header="MQTT & Integration">
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
                                    <label>Broker Adresse</label>
                                    <InputText v-model="config.mqtt.broker" placeholder="mqtt.example.com" class="w-full" />
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>Port</label>
                                    <InputNumber v-model="config.mqtt.port" :useGrouping="false" :min="1" :max="65535" class="w-full" />
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>Benutzername</label>
                                    <InputText v-model="config.mqtt.username" placeholder="Optional" class="w-full" />
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>Passwort</label>
                                    <InputText v-model="mqttPassword" type="password" placeholder="••••••" class="w-full" />
                                </div>
                            </div>

                            <div class="border-t border-gray-700 pt-4">
                                <div class="flex items-center gap-2 mb-3">
                                    <Checkbox v-model="config.mqtt.use_tls" binary inputId="mqtt_tls" />
                                    <label for="mqtt_tls" class="font-bold cursor-pointer">TLS/SSL Verschlüsselung</label>
                                </div>
                                <div v-if="config.mqtt.use_tls" class="ml-8 mb-4">
                                    <div class="flex flex-col gap-2">
                                        <label class="text-sm">CA-Zertifikat Pfad (optional)</label>
                                        <InputText v-model="config.mqtt.tls_ca_cert" placeholder="/path/to/ca.crt" class="w-full" />
                                        <small class="text-gray-400">Für selbst-signierte Zertifikate. Leer lassen für System-CA.</small>
                                    </div>
                                </div>
                            </div>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 pt-4">
                                <div class="flex flex-col gap-2">
                                    <label>Topic Präfix</label>
                                    <InputText v-model="config.mqtt.topic_prefix" class="w-full" />
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>QoS Level</label>
                                    <SelectButton v-model="config.mqtt.qos" :options="[0, 1, 2]" aria-labelledby="basic" class="w-full" />
                                </div>
                            </div>

                            <div class="flex flex-col gap-3 border border-green-600/50 rounded bg-green-900/10 p-4">
                                <div class="flex items-center gap-2">
                                    <Checkbox v-model="config.mqtt.ha_discovery_enabled" binary inputId="ha_discovery" />
                                    <label for="ha_discovery" class="font-bold text-green-400 cursor-pointer">Home Assistant Auto-Discovery</label>
                                </div>
                                <div v-if="config.mqtt.ha_discovery_enabled" class="ml-8">
                                    <label class="text-sm">Discovery Präfix</label>
                                    <InputText v-model="config.mqtt.ha_discovery_prefix" class="w-full mt-1" />
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-gray-400 italic">
                            Aktivieren Sie MQTT, um Daten an Broker wie Mosquitto oder Home Assistant zu senden.
                        </div>
                    </Fieldset>
                </TabPanel>

                <TabPanel header="Benachrichtigungen">
                    <div class="flex flex-col gap-6">
                        <Fieldset legend="Signal Messenger" :toggleable="true">
                            <template #legend>
                                <div class="flex items-center gap-2">
                                    <Checkbox v-model="config.signal.enabled" binary />
                                    <span class="font-bold">Signal</span>
                                </div>
                            </template>

                            <div v-if="config.signal.enabled" class="flex flex-col gap-4">
                                <div class="flex flex-col gap-2">
                                    <label>Sender Nummer</label>
                                    <InputText v-model="config.signal.sender" placeholder="+49..." class="w-full md:w-1/2" />
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>Empfänger (Pro Zeile eine Nummer)</label>
                                    <Textarea v-model="signalRecipientsText" rows="3" class="w-full font-mono" />
                                </div>
                                <div class="flex flex-col gap-2 border-t border-gray-700 pt-4 mt-2">
                                    <label class="text-sm font-bold">Erweitert</label>
                                    <div class="flex flex-col gap-2">
                                        <label class="text-xs">Signal CLI Pfad</label>
                                        <InputText v-model="config.signal.cli_path" placeholder="signal-cli" class="w-full md:w-1/2" />
                                        <small class="text-gray-400">Standard: signal-cli (im PATH)</small>
                                    </div>
                                </div>
                                <Button label="Testnachricht senden" icon="pi pi-send" severity="success" outlined @click="sendSignalTest" class="w-full md:w-auto self-start" />
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
                                    <label>Bot Token</label>
                                    <InputText v-model="config.telegram.bot_token" type="password" class="w-full md:w-1/2" />
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>Chat IDs (Kommagetrennt)</label>
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
                                    <label>Webhook URL</label>
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
                                        <label>SMTP Server</label>
                                        <InputText v-model="config.email.smtp_server" class="w-full" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Port</label>
                                        <InputNumber v-model="config.email.smtp_port" :useGrouping="false" class="w-full" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Benutzername</label>
                                        <InputText v-model="config.email.username" class="w-full" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Passwort</label>
                                        <InputText v-model="emailPassword" type="password" class="w-full" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Absender Adresse</label>
                                        <InputText v-model="config.email.sender" class="w-full" />
                                    </div>
                                </div>
                                <div class="flex flex-col gap-2">
                                    <label>Empfänger (Kommagetrennt)</label>
                                    <InputText v-model="emailRecipientsText" class="w-full" />
                                </div>
                            </div>
                        </Fieldset>
                    </div>
                </TabPanel>

                <TabPanel header="KI-Analyse">
                     <div class="flex flex-col gap-6">
                        <Fieldset legend="Community Daten & Modell" :toggleable="true">
                            <div class="flex flex-col gap-4">
                                <div class="flex flex-col gap-2">
                                    <label>Wärmepumpen Modell</label>
                                    <Dropdown v-model="config.heatpump_model" :options="heatpumpModels" placeholder="Maschine auswählen" class="w-full md:w-1/2" />
                                    <small class="text-gray-400">Notwendig für die korrekte Einordnung der Daten.</small>
                                </div>

                                <div class="flex items-start gap-3 p-3 bg-purple-900/20 border border-purple-700/50 rounded-md">
                                     <Checkbox v-model="config.share_data" :binary="true" inputId="shareDataConf" />
                                     <div class="flex flex-col gap-1">
                                        <label for="shareDataConf" class="font-bold cursor-pointer">Daten teilen & Zustimmung</label>
                                        <p class="text-sm text-gray-300 text-justify">
                                            Hiermit stimme ich zu, dass anonymisierte Daten (unter Ausschluss persönlicher Informationen) an den Betreiber gesendet werden.
                                            Die Daten gehen in das Eigentum des Betreibers über, der diese zu Trainingszwecken nutzen und kommerziell verwerten darf.
                                        </p>
                                     </div>
                                </div>

                                <div class="flex flex-col gap-2 mt-2">
                                    <label>Telemetry Authentifizierungs-Token (Optional)</label>
                                    <InputText v-model="config.telemetry_auth_token" type="password" placeholder="Nur erforderlich für private Server" class="w-full" />
                                    <small class="text-gray-400">Wird benötigt, wenn der Telemetry-Server eine Authentifizierung erfordert.</small>
                                </div>
                            </div>
                        </Fieldset>

                        <Fieldset legend="KI & Anomalieerkennung" :toggleable="true">
                            <template #legend>
                                <div class="flex items-center gap-2">
                                    <Checkbox v-model="config.ai.enabled" binary />
                                    <span class="font-bold">KI-Analyse Status anzeigen</span>
                                </div>
                            </template>
                             <div v-if="config.ai.enabled" class="flex flex-col gap-6">
                                 <div class="bg-blue-900/20 border border-blue-600/50 p-4 rounded flex items-start gap-3">
                                     <i class="pi pi-info-circle text-blue-400 text-xl mt-1"></i>
                                     <div class="text-sm text-blue-200">
                                         Die Anomalieerkennung läuft nun als eigenständiger <strong>ml-service</strong> Container.
                                         Er nutzt die "HalfSpaceTrees" Methode (via Python <code>river</code>), um kontinuierlich aus dem Datenstrom zu lernen.
                                     </div>
                                 </div>

                                 <div class="bg-gray-800 p-4 rounded border border-gray-700 mt-4">
                                     <h4 class="font-bold text-lg mb-2 flex items-center gap-2">
                                         <i class="pi pi-chart-line"></i> Service Status
                                     </h4>
                                     <div v-if="aiStatus" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                         <div class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Service:</span>
                                             <span class="font-mono">{{ aiStatus.service || 'Unbekannt' }}</span>
                                         </div>
                                         <div class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Modell-Quelle:</span>
                                             <span class="font-bold font-mono" :class="aiStatus.source.includes('Community') ? 'text-purple-400' : 'text-blue-400'">
                                                 {{ aiStatus.source || 'Local' }}
                                             </span>
                                         </div>
                                         <div v-if="aiStatus.model_date" class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Modell-Datum:</span>
                                             <span class="font-mono text-purple-300">
                                                 {{ new Date(aiStatus.model_date * 1000).toLocaleString() }}
                                             </span>
                                         </div>
                                         <div class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Status:</span>
                                             <span class="font-bold" :class="aiStatus.online ? 'text-green-400' : 'text-red-400'">
                                                 {{ aiStatus.online ? 'Online' : 'Offline / Keine Daten' }}
                                             </span>
                                         </div>
                                         <div class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Letzter Score:</span>
                                             <span class="font-mono text-lg">{{ aiStatus.score ? aiStatus.score.toFixed(4) : '0.0000' }}</span>
                                         </div>
                                         <div class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Aktuelle Anomalie:</span>
                                             <span class="font-bold" :class="aiStatus.is_anomaly ? 'text-red-500' : 'text-green-500'">
                                                 {{ aiStatus.is_anomaly ? 'JA' : 'NEIN' }}
                                             </span>
                                         </div>
                                          <div class="flex justify-between border-b border-gray-700 py-2">
                                             <span class="text-gray-400">Letztes Update:</span>
                                             <span class="font-mono">{{ aiStatus.last_update ? new Date(aiStatus.last_update * 1000).toLocaleString() : '-' }}</span>
                                         </div>
                                     </div>
                                     <div v-else class="text-center py-4 text-gray-500">
                                         <i class="pi pi-spin pi-spinner mr-2"></i> Lade Status...
                                     </div>
                                 </div>

                                 <div class="flex justify-end">
                                     <Button label="Jetzt nach Modell-Updates suchen" icon="pi pi-cloud-download" severity="secondary" size="small" @click="triggerModelUpdate" :loading="modelUpdateLoading" />
                                 </div>
                             </div>
                        </Fieldset>
                     </div>
                </TabPanel>

                <TabPanel header="Sicherheit">
                    <div class="flex flex-col gap-6">
                         <Fieldset legend="Webzugriff" :toggleable="true">
                            <div class="flex flex-col gap-4">
                                <div class="flex flex-col gap-2">
                                    <label>Admin Passwort</label>
                                    <Button label="Passwort ändern" icon="pi pi-key" severity="secondary" outlined class="w-full md:w-auto self-start" @click="showPasswordDialog = true" />
                                </div>
                                <div class="flex items-center gap-2 mt-2">
                                    <Checkbox v-model="config.web.write_enabled" binary inputId="write_access" />
                                    <div class="flex flex-col">
                                        <label for="write_access" class="font-bold cursor-pointer">Schreibzugriff erlauben</label>
                                        <span class="text-sm text-gray-400">Erforderlich für manuelle Steuerung und Zeitpläne</span>
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
                                <div class="bg-yellow-900/20 border border-yellow-600/50 p-3 rounded text-yellow-200 text-sm flex items-start gap-2">
                                    <i class="pi pi-exclamation-triangle mt-0.5"></i>
                                    <span>Deine IP ist <strong>{{ currentClientIP }}</strong>. Füge diese zur Whitelist hinzu, sonst sperrst du dich aus!</span>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div class="flex flex-col gap-2">
                                        <label class="font-bold text-green-400">Whitelist (Erlaubt)</label>
                                        <Textarea v-model="whitelistText" rows="5" class="w-full font-mono text-sm" placeholder="192.168.1.0/24" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label class="font-bold text-red-400">Blacklist (Blockiert)</label>
                                        <Textarea v-model="blacklistText" rows="5" class="w-full font-mono text-sm" placeholder="1.2.3.4" />
                                    </div>
                                </div>
                            </div>
                        </Fieldset>
                    </div>
                </TabPanel>

                <TabPanel header="System & Wartung">
                    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <!-- Update Status -->
                        <div data-update-section class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3">
                            <h3 class="font-bold text-lg flex items-center gap-2">
                                <i class="pi pi-refresh"></i> Update Status
                            </h3>
                             <div class="flex items-center justify-between bg-gray-900/50 p-3 rounded">
                                 <div>
                                     <div class="text-sm text-gray-400">Installierte Version</div>
                                     <div class="font-mono">{{ updateStatus.current_version || 'v0.0.0' }}</div>
                                 </div>
                                 <div class="text-right">
                                     <div class="text-sm text-gray-400">Verfügbare Version</div>
                                     <div class="font-mono text-green-400">{{ updateStatus.latest_version || 'Checking...' }}</div>
                                 </div>
                             </div>

                             <!-- Docker Image Status -->
                             <div v-if="updateStatus.docker" class="bg-gray-900/50 p-3 rounded mt-2">
                                 <div class="flex items-center gap-2 mb-2">
                                     <i class="pi pi-box text-blue-400"></i>
                                     <span class="text-sm font-bold">Docker Images</span>
                                     <span v-if="updateStatus.docker.updates_available" class="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">Updates verfügbar</span>
                                 </div>
                                 <div class="grid grid-cols-1 gap-2 text-xs">
                                     <div v-for="(img, name) in updateStatus.docker.images" :key="name"
                                          class="flex items-center justify-between p-2 rounded"
                                          :class="img.update_available ? 'bg-blue-900/30 border border-blue-600/50' : 'bg-gray-800'">
                                         <div class="flex items-center gap-2">
                                             <i :class="img.update_available ? 'pi pi-arrow-up text-blue-400' : 'pi pi-check text-green-400'"></i>
                                             <span class="font-mono">{{ name }}</span>
                                         </div>
                                         <div class="text-right">
                                             <span v-if="img.update_available" class="text-blue-300">Update verfügbar</span>
                                             <span v-else class="text-green-400">Aktuell</span>
                                         </div>
                                     </div>
                                 </div>
                             </div>

                             <!-- Update Available Info -->
                             <div v-if="updateStatus.update_available" class="bg-blue-900/20 border border-blue-600/50 p-3 rounded mt-2 flex flex-col gap-2">
                                <div class="flex items-center gap-2 text-blue-300 text-sm">
                                    <i class="pi pi-info-circle"></i>
                                    <span>Neue Version verfügbar!</span>
                                </div>
                                <p class="text-xs text-gray-400">
                                    Watchtower aktualisiert automatisch täglich um 3:00 Uhr.
                                </p>
                             </div>

                             <!-- Watchtower Info -->
                             <div class="bg-gray-900/50 p-3 rounded mt-2">
                                 <div class="flex items-center gap-2 mb-2">
                                     <i class="pi pi-sync text-green-400"></i>
                                     <span class="text-sm font-bold">Automatische Updates</span>
                                 </div>
                                 <p class="text-xs text-gray-400 mb-2">
                                     Watchtower prüft täglich um <span class="text-green-400 font-mono">03:00 Uhr</span> auf neue Docker Images und aktualisiert automatisch.
                                 </p>
                                 <Button label="Anleitung für manuelles Update" icon="pi pi-question-circle" severity="secondary" size="small" text @click="showUpdateHelpDialog = true" />
                             </div>

                             <div class="flex justify-end mt-2">
                                 <Button label="Jetzt prüfen" icon="pi pi-search" size="small" severity="secondary" @click="checkUpdates" :loading="checkingUpdates" />
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
                                         <label for="auto_backup" class="font-bold text-sm">Automatisches Backup</label>
                                    </div>
                                </div>
                                <div v-if="config.backup.enabled" class="grid grid-cols-2 gap-2 text-sm bg-gray-900/30 p-2 rounded">
                                     <div class="flex flex-col">
                                         <label class="text-xs text-gray-400">Intervall (Std)</label>
                                         <InputNumber v-model="config.backup.interval" :min="1" :max="168" class="p-inputtext-sm" />
                                     </div>
                                     <div class="flex flex-col">
                                         <label class="text-xs text-gray-400">Behalten (Anzahl)</label>
                                         <InputNumber v-model="config.backup.retention" :min="1" :max="50" class="p-inputtext-sm" />
                                     </div>
                                      <div class="col-span-2 flex items-center gap-2 mt-1">
                                         <Checkbox v-model="config.backup.auto_upload" binary inputId="backup_upload" :disabled="!config.webdav.enabled" />
                                         <label for="backup_upload" class="text-xs" :class="{'opacity-50': !config.webdav.enabled}">Automatisch in Cloud hochladen</label>
                                    </div>
                                </div>
                            </div>

                            <div class="flex gap-2">
                                <Button label="Backup erstellen" icon="pi pi-download" size="small" @click="createBackup" :loading="creatingBackup" />
                                <Button label="Backup hochladen" icon="pi pi-upload" size="small" severity="secondary" @click="$refs.fileInput.click()" />
                                <input type="file" ref="fileInput" class="hidden" @change="handleFileSelect" accept=".zip" />
                            </div>
                            <Button v-if="selectedFile" label="Wiederherstellen starten" severity="warning" class="w-full mt-2" @click="restoreFromFile" />

                             <div class="mt-2 max-h-40 overflow-y-auto">
                                <div v-for="backup in backups" :key="backup.filename" class="flex justify-between items-center p-2 hover:bg-gray-700 rounded text-sm border-b border-gray-700 last:border-0">
                                    <span class="truncate">{{ backup.filename }}</span>
                                    <div class="flex gap-1">
                                        <Button icon="pi pi-cloud-upload" text size="small" @click="uploadToCloud(backup.filename)" title="Upload to WebDAV" />
                                        <Button icon="pi pi-download" text size="small" @click="downloadBackup(backup.filename)" />
                                        <Button icon="pi pi-trash" text severity="danger" size="small" @click="confirmDeleteBackup(backup.filename)" />
                                    </div>
                                </div>
                             </div>

                             <div class="border-t border-gray-700 pt-3 mt-2">
                                 <div class="flex items-center gap-2 mb-2">
                                    <Checkbox v-model="config.webdav.enabled" binary inputId="webdav_enabled" />
                                    <label for="webdav_enabled" class="font-bold cursor-pointer">Cloud Backup (WebDAV/Nextcloud)</label>
                                </div>
                                <div v-if="config.webdav.enabled" class="flex flex-col gap-2">
                                    <div class="flex flex-col gap-1">
                                        <label class="text-xs">URL</label>
                                        <InputText v-model="config.webdav.url" placeholder="https://cloud.example.com/remote.php/dav/files/user/" class="p-inputtext-sm w-full" />
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <label class="text-xs">Benutzername</label>
                                        <InputText v-model="config.webdav.username" class="p-inputtext-sm w-full" />
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <label class="text-xs">Passwort</label>
                                        <InputText v-model="webdavPassword" type="password" class="p-inputtext-sm w-full" />
                                    </div>
                                </div>
                             </div>
                        </div>

                         <!-- Service Control -->
                         <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3 xl:col-span-2">
                            <h3 class="font-bold text-lg flex items-center gap-2 text-red-400">
                                <i class="pi pi-power-off"></i> Danger Zone
                            </h3>
                            <div class="flex gap-4">
                                <Button label="Dienst neu starten" icon="pi pi-refresh" severity="warning" @click="confirmRestart" />
                                <Button label="Datenbank löschen" icon="pi pi-trash" severity="danger" @click="showDeleteDialog = true" />
                            </div>
                        </div>
                    </div>
                </TabPanel>

            </TabView>
        </div>

        <div class="flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4 sticky bottom-0 bg-gray-900/90 backdrop-blur p-4 z-10">
            <Button label="Speichern" icon="pi pi-save" @click="saveConfig" :loading="saving" size="large" severity="primary" />
        </div>

        <!-- Dialogs -->
        <Dialog v-model:visible="showPasswordDialog" modal header="Passwort ändern" :style="{ width: '400px' }">
            <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                    <label>Neues Passwort</label>
                    <InputText v-model="newPassword" type="password" class="w-full" />
                </div>
                 <div class="flex flex-col gap-2">
                    <label>Bestätigen</label>
                    <InputText v-model="confirmPassword" type="password" class="w-full" :class="{'p-invalid': passwordMismatch}" />
                    <small v-if="passwordMismatch" class="text-red-500">Passwörter stimmen nicht überein</small>
                </div>
            </div>
             <template #footer>
                <Button label="Abbrechen" text @click="showPasswordDialog = false" />
                <Button label="Speichern" @click="savePassword" :disabled="!newPassword || !confirmPassword || passwordMismatch" />
            </template>
        </Dialog>

        <Dialog v-model:visible="showDeleteDialog" modal header="Datenbank löschen" :style="{ width: '450px' }">
            <div class="flex flex-col gap-4">
                <div class="flex items-start gap-3">
                    <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
                    <div class="flex flex-col gap-2">
                        <span class="font-bold text-lg">Bist du dir absolut sicher?</span>
                        <p class="text-gray-300">
                            Diese Aktion löscht <span class="font-bold text-red-400">ALLE</span> Daten dauerhaft aus der Datenbank.
                        </p>
                    </div>
                </div>
                <InputText v-model="deleteConfirmationText" placeholder="Tippe DELETE" class="w-full" />
            </div>
            <template #footer>
                <Button label="Abbrechen" text @click="showDeleteDialog = false" />
                <Button label="Alles löschen" severity="danger" @click="confirmDeleteDatabase" :disabled="deleteConfirmationText !== 'DELETE'" :loading="deletingDatabase" />
            </template>
        </Dialog>

        <!-- Manual Update Help Dialog -->
        <Dialog v-model:visible="showUpdateHelpDialog" modal header="Manuelles Update" :style="{ width: '500px' }">
            <div class="flex flex-col gap-4">
                <div class="bg-blue-900/20 border border-blue-600/50 p-3 rounded">
                    <div class="flex items-center gap-2 text-blue-300 mb-2">
                        <i class="pi pi-info-circle"></i>
                        <span class="font-bold">Automatische Updates</span>
                    </div>
                    <p class="text-sm text-gray-300">
                        Watchtower aktualisiert Docker Images automatisch täglich um 3:00 Uhr.
                        Manuelle Updates sind nur nötig, wenn Sie nicht warten möchten.
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

                <div class="text-xs text-gray-400">
                    <i class="pi pi-lightbulb mr-1"></i>
                    Nach dem Update wird die Seite automatisch neu geladen sobald der Container wieder erreichbar ist.
                </div>
            </div>
            <template #footer>
                <Button label="Schließen" @click="showUpdateHelpDialog = false" />
            </template>
        </Dialog>

        <Toast />
        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import axios from 'axios';
import Fieldset from 'primevue/fieldset';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import Dialog from 'primevue/dialog';
import SelectButton from 'primevue/selectbutton';
import Dropdown from 'primevue/dropdown';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';


const config = ref({
    idm: { host: '', port: 502, circuits: ['A'], zones: [] },
    metrics: { url: '' },
    web: { write_enabled: false },
    logging: { interval: 60, realtime_mode: false },
    mqtt: { enabled: false, broker: '', port: 1883, username: '', topic_prefix: 'idm/heatpump', qos: 0, use_tls: false, tls_ca_cert: '', publish_interval: 60, ha_discovery_enabled: false, ha_discovery_prefix: 'homeassistant' },
    network_security: { enabled: false, whitelist: [], blacklist: [] },
    signal: { enabled: false, cli_path: 'signal-cli', sender: '', recipients: [] },
    telegram: { enabled: false, bot_token: '', chat_ids: [] },
    discord: { enabled: false, webhook_url: '' },
    email: { enabled: false, smtp_server: '', smtp_port: 587, username: '', sender: '', recipients: [] },
    webdav: { enabled: false, url: '', username: '' },
    ai: { enabled: false, sensitivity: 3.0, model: 'rolling' },
    updates: { enabled: false, interval_hours: 12, mode: 'apply', target: 'all', channel: 'latest' },
    backup: { enabled: false, interval: 24, retention: 10, auto_upload: false },
    heatpump_model: '',
    share_data: true
});

const heatpumpModels = [
    'AERO ALM 2-8',
    'AERO ALM 4-12',
    'AERO ALM 6-15',
    'AERO ALM 10-24',
    'AERO ALM 10-50 MAX',
    'AERO SLM',
    'AERO ILM',
    'TERRA SW',
    'TERRA ML',
    'TERRA SW Max',
    'iPump A',
    'iPump T',
    'iPump T7',
    'iPump T7 ONE',
    'iPump N5',
    'Andere / Unbekannt'
];
const showPasswordDialog = ref(false);
const newPassword = ref('');
const confirmPassword = ref('');
const mqttPassword = ref('');
const emailPassword = ref('');
const webdavPassword = ref('');
const whitelistText = ref('');
const blacklistText = ref('');
const signalRecipientsText = ref('');
const telegramChatIdsText = ref('');
const emailRecipientsText = ref('');
const updateStatus = ref({});
const signalStatus = ref({});
const aiStatus = ref(null);
const statusLoading = ref(false);
const checkingUpdates = ref(false);
const modelUpdateLoading = ref(false);
const currentClientIP = ref('');
const loading = ref(true);
const saving = ref(false);
const toast = useToast();
const confirm = useConfirm();

let aiStatusInterval = null;

const passwordMismatch = computed(() => {
    return newPassword.value && confirmPassword.value && newPassword.value !== confirmPassword.value;
});

onUnmounted(() => {
    if (aiStatusInterval) clearInterval(aiStatusInterval);
});

// Backup & Restore state
const backups = ref([]);
const loadingBackups = ref(false);
const creatingBackup = ref(false);
const restoringBackup = ref(false);
const selectedFile = ref(null);
const fileInput = ref(null);

// Database Maintenance
const showDeleteDialog = ref(false);
const deleteConfirmationText = ref('');
const deletingDatabase = ref(false);
const updating = ref(false);

// Update Help Dialog
const showUpdateHelpDialog = ref(false);

onMounted(async () => {
    try {
        const res = await axios.get('/api/config');
        config.value = res.data;

        // Convert whitelist/blacklist arrays to text
        if (config.value.network_security) {
            whitelistText.value = (config.value.network_security.whitelist || []).join('\n');
            blacklistText.value = (config.value.network_security.blacklist || []).join('\n');
        }

        if (config.value.signal) {
            signalRecipientsText.value = (config.value.signal.recipients || []).join('\n');
        }

        if (config.value.telegram) {
            telegramChatIdsText.value = (config.value.telegram.chat_ids || []).join(', ');
        }
        if (config.value.email) {
            emailRecipientsText.value = (config.value.email.recipients || []).join(', ');
        }

        // Get current client IP
        try {
            const ipRes = await axios.get('/api/health');
            currentClientIP.value = ipRes.data.client_ip || 'Unbekannt';
        } catch (e) {
            console.error('Failed to get client IP', e);
        }

        // Load backups
        loadBackups();
        loadStatus(true);  // Show notification on initial load
        loadAiStatus();

        // Refresh AI status periodically
        aiStatusInterval = setInterval(loadAiStatus, 10000);
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Konfiguration konnte nicht geladen werden', life: 3000 });
    } finally {
        loading.value = false;
    }
});

const sendSignalTest = async () => {
    try {
        const res = await axios.post('/api/signal/test', { message: 'Signal Test vom IDM Metrics Collector' });
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error || 'Signal Test fehlgeschlagen', life: 3000 });
        }
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
    }
};

const loadStatus = async (showNotification = false) => {
    statusLoading.value = true;
    try {
        const [updateRes, signalRes] = await Promise.all([
            axios.get('/api/check-update', { params: { channel: config.value.updates?.channel || 'latest' } }),
            axios.get('/api/signal/status')
        ]);
        updateStatus.value = updateRes.data;
        signalStatus.value = signalRes.data;

        // Show notification popup if updates are available (on initial load)
        if (showNotification && updateRes.data.update_available) {
            const dockerUpdates = updateRes.data.docker?.updates_available;
            const gitUpdates = updateRes.data.git_update_available;

            let detail = 'Ein Update ist verfügbar!';
            if (dockerUpdates && gitUpdates) {
                detail = 'Neue Version und Docker Images verfügbar!';
            } else if (dockerUpdates) {
                detail = 'Neue Docker Images verfügbar!';
            } else if (gitUpdates) {
                detail = `Version ${updateRes.data.latest_version} verfügbar!`;
            }

            toast.add({
                severity: 'info',
                summary: 'Update verfügbar',
                detail: detail,
                life: 10000
            });
        }
    } catch (e) {
        // Silent fail for status check
        console.error("Status load failed", e);
    } finally {
        statusLoading.value = false;
    }
};

const checkUpdates = async () => {
    checkingUpdates.value = true;
    try {
        const res = await axios.get('/api/check-update', { params: { channel: config.value.updates.channel } });
        updateStatus.value = res.data;
        if (res.data.update_available) {
             toast.add({ severity: 'info', summary: 'Update verfügbar', detail: `Version ${res.data.latest_version} ist verfügbar.`, life: 5000 });
        } else {
             toast.add({ severity: 'success', summary: 'System aktuell', detail: 'Keine Updates gefunden.', life: 3000 });
        }
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Update-Prüfung fehlgeschlagen', life: 3000 });
    } finally {
        checkingUpdates.value = false;
    }
};

const savePassword = () => {
    // Password will be saved when main saveConfig is called, or we can save it separately.
    // Given the architecture, newPassword variable is used in saveConfig.
    // So we just close the dialog and let the user click "Save" on the main page?
    // User request implies immediate action "Pop up zum Passwort ändern".
    // But existing saveConfig handles it. Let's make the dialog just set the variable and then user saves?
    // OR we trigger save immediately. Let's trigger save immediately for better UX if it's a separate dialog.
    // Actually, saveConfig handles everything. To avoid confusion, let's call saveConfig here ONLY with password?
    // The backend endpoint accepts partial updates effectively by merging.
    // However, saveConfig sends the WHOLE config object.
    // So we can just set the variable, close dialog, and call saveConfig.

    showPasswordDialog.value = false;
    saveConfig();
};

const loadAiStatus = async () => {
    try {
        const res = await axios.get('/api/ai/status');
        aiStatus.value = res.data;
    } catch (e) {
        console.error("Failed to load AI status", e);
    }
};

const triggerModelUpdate = async () => {
    modelUpdateLoading.value = true;
    try {
        const res = await axios.post('/api/ai/update_now');
        toast.add({ severity: 'success', summary: 'Gestartet', detail: res.data.message, life: 3000 });
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Update-Suche konnte nicht gestartet werden', life: 3000 });
    } finally {
        modelUpdateLoading.value = false;
    }
};

const saveConfig = async () => {
    saving.value = true;
    try {
        const payload = {
            idm_host: config.value.idm.host,
            idm_port: config.value.idm.port,
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
            heatpump_model: config.value.heatpump_model || '',
            share_data: config.value.share_data || false,
            telemetry_auth_token: config.value.telemetry_auth_token || '',
            updates_enabled: config.value.updates?.enabled || false,
            updates_interval_hours: config.value.updates?.interval_hours || 12,
            updates_mode: config.value.updates?.mode || 'apply',
            updates_target: config.value.updates?.target || 'all',
            updates_channel: config.value.updates?.channel || 'latest',
            backup_enabled: config.value.backup?.enabled || false,
            backup_interval: config.value.backup?.interval || 24,
            backup_retention: config.value.backup?.retention || 10,
            backup_auto_upload: config.value.backup?.auto_upload || false,
            new_password: newPassword.value || undefined
        };
        const res = await axios.post('/api/config', payload);
        toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message || 'Einstellungen erfolgreich gespeichert', life: 3000 });
        newPassword.value = '';
        confirmPassword.value = '';
        mqttPassword.value = '';
        webdavPassword.value = '';
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
    } finally {
        saving.value = false;
    }
};

const confirmRestart = () => {
    confirm.require({
        message: 'Bist du sicher, dass du den Dienst neu starten möchtest?',
        header: 'Bestätigung',
        icon: 'pi pi-exclamation-triangle',
        accept: async () => {
            try {
                const res = await axios.post('/api/restart');
                toast.add({ severity: 'info', summary: 'Neustart', detail: res.data.message, life: 3000 });
            } catch (e) {
        console.error(e);
                toast.add({ severity: 'error', summary: 'Fehler', detail: 'Neustart fehlgeschlagen', life: 3000 });
            }
        }
    });
};

// Backup & Restore functions
const loadBackups = async () => {
    loadingBackups.value = true;
    try {
        const res = await axios.get('/api/backup/list');
        backups.value = res.data.backups || [];
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Backups konnten nicht geladen werden', life: 3000 });
    } finally {
        loadingBackups.value = false;
    }
};

const createBackup = async () => {
    creatingBackup.value = true;
    try {
        const res = await axios.post('/api/backup/create');
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Erfolg', detail: `Backup erstellt: ${res.data.filename}`, life: 3000 });
            loadBackups();
        } else {
            toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 3000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || 'Backup Erstellung fehlgeschlagen', life: 3000 });
    } finally {
        creatingBackup.value = false;
    }
};

const downloadBackup = async (filename) => {
    try {
        const response = await axios.get(`/api/backup/download/${filename}`, {
            responseType: 'blob'
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Backup heruntergeladen', life: 2000 });
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Backup Download fehlgeschlagen', life: 3000 });
    }
};

const uploadToCloud = async (filename) => {
    try {
        toast.add({ severity: 'info', summary: 'Info', detail: 'Upload gestartet...', life: 2000 });
        const res = await axios.post(`/api/backup/upload/${filename}`);
        if (res.data.success) {
             toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Backup erfolgreich hochgeladen', life: 3000 });
        } else {
             toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 5000 });
        }
    } catch (e) {
        console.error(e);
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || 'Upload fehlgeschlagen', life: 5000 });
    }
};

const confirmDeleteBackup = (filename) => {
    confirm.require({
        message: `Backup "${filename}" löschen?`,
        header: 'Backup Löschen',
        icon: 'pi pi-trash',
        acceptClass: 'p-button-danger',
        accept: async () => {
            try {
                await axios.delete(`/api/backup/delete/${filename}`);
                toast.add({ severity: 'success', summary: 'Erfolg', detail: 'Backup gelöscht', life: 2000 });
                loadBackups();
            } catch (e) {
        console.error(e);
                toast.add({ severity: 'error', summary: 'Fehler', detail: 'Backup löschen fehlgeschlagen', life: 3000 });
            }
        }
    });
};

const handleFileSelect = (event) => {
    const file = event.target.files[0];
    selectedFile.value = file;
};

const restoreFromFile = async () => {
    if (!selectedFile.value) return;

    confirm.require({
        message: 'Konfiguration aus hochgeladener Datei wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!',
        header: 'Aus Datei Wiederherstellen',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-warning',
        accept: async () => {
            restoringBackup.value = true;
            try {
                const formData = new FormData();
                formData.append('file', selectedFile.value);
                formData.append('restore_secrets', 'false');

                const res = await axios.post('/api/backup/restore', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });

                if (res.data.success) {
                    toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 5000 });
                    selectedFile.value = null;
                    if (fileInput.value) fileInput.value.value = '';
                    setTimeout(() => location.reload(), 2000);
                } else {
                    toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 5000 });
                }
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || 'Wiederherstellung fehlgeschlagen', life: 5000 });
            } finally {
                restoringBackup.value = false;
            }
        }
    });
};

const confirmDeleteDatabase = async () => {
    if (deleteConfirmationText.value !== 'DELETE') return;

    deletingDatabase.value = true;
    try {
        const res = await axios.post('/api/database/delete');
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 5000 });
            showDeleteDialog.value = false;
            deleteConfirmationText.value = '';
        } else {
            toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || 'Datenbank löschen fehlgeschlagen', life: 5000 });
    } finally {
        deletingDatabase.value = false;
    }
};

</script>
