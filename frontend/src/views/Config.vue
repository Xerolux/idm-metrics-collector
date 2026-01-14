<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Konfiguration</h1>

        <div v-if="loading" class="flex justify-center">
            <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else>
            <TabView>
                <TabPanel header="Allgemein">
                    <div class="flex flex-col gap-6">
                        <Card class="bg-gray-800 text-white">
                            <template #title>IDM Wärmepumpe</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex flex-col gap-2">
                                        <label>Host / IP</label>
                                        <InputText v-model="config.idm.host" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Port</label>
                                        <InputNumber v-model="config.idm.port" :useGrouping="false" />
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label class="font-bold">Aktivierte Features</label>
                                        <div class="flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50">
                                            <div class="flex items-center gap-2">
                                                <Checkbox v-model="config.idm.circuits" inputId="circuitA" value="A" disabled />
                                                <label for="circuitA" class="opacity-50">Heizkreis A (Immer aktiv)</label>
                                            </div>
                                            <div class="flex flex-wrap gap-4">
                                                <div v-for="c in ['B', 'C', 'D', 'E', 'F', 'G']" :key="c" class="flex items-center gap-2">
                                                    <Checkbox v-model="config.idm.circuits" :inputId="'circuit'+c" :value="c" />
                                                    <label :for="'circuit'+c">Heizkreis {{ c }}</label>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50">
                                            <label class="text-sm text-gray-400">Zonenmodule</label>
                                            <div class="flex flex-wrap gap-4">
                                                <div v-for="z in 10" :key="z" class="flex items-center gap-2">
                                                    <Checkbox v-model="config.idm.zones" :inputId="'zone'+(z-1)" :value="(z-1)" />
                                                    <label :for="'zone'+(z-1)">Zone {{ z }}</label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white">
                            <template #title>VictoriaMetrics</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex flex-col gap-2">
                                        <label>URL</label>
                                        <InputText v-model="config.metrics.url" />
                                        <small class="text-gray-300">Standard: http://victoriametrics:8428/write</small>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </TabPanel>

                <TabPanel header="Datenerfassung">
                    <Card class="bg-gray-800 text-white">
                        <template #title>Datenerfassung</template>
                        <template #content>
                            <div class="flex flex-col gap-4">
                                <div class="flex items-center gap-2">
                                    <Checkbox v-model="config.logging.realtime_mode" binary inputId="realtime_mode" />
                                    <label for="realtime_mode">Echtzeit-Modus (1 Sekunden Intervall)</label>
                                </div>
                                <div class="flex flex-col gap-2" v-if="!config.logging.realtime_mode">
                                    <label>Abfrage-Intervall (Sekunden)</label>
                                    <InputNumber v-model="config.logging.interval" :min="1" :max="3600" :useGrouping="false" />
                                    <small class="text-gray-400">Wie oft Daten von der Wärmepumpe gelesen werden (1-3600 Sekunden)</small>
                                </div>
                            </div>
                        </template>
                    </Card>
                </TabPanel>

                <TabPanel header="MQTT">
                    <Card class="bg-gray-800 text-white" v-if="config.mqtt">
                        <template #title>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-send text-blue-400"></i>
                                <span>MQTT Publishing</span>
                            </div>
                        </template>
                        <template #content>
                            <div class="flex flex-col gap-4">
                                <div class="flex items-center gap-2">
                                    <Checkbox v-model="config.mqtt.enabled" binary inputId="mqtt_enabled" />
                                    <label for="mqtt_enabled" class="font-bold">MQTT Publishing aktivieren</label>
                                </div>

                                <div v-if="config.mqtt.enabled" class="flex flex-col gap-4 p-3 border border-blue-600 rounded bg-blue-900/10">
                                    <div class="flex flex-col gap-2">
                                        <label>Broker Adresse</label>
                                        <InputText v-model="config.mqtt.broker" placeholder="mqtt.example.com" />
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Port</label>
                                        <InputNumber v-model="config.mqtt.port" :useGrouping="false" :min="1" :max="65535" />
                                        <small class="text-gray-400">Standard: 1883 (ohne TLS) oder 8883 (TLS)</small>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Benutzername (Optional)</label>
                                        <InputText v-model="config.mqtt.username" placeholder="Optional" />
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Passwort (Optional)</label>
                                        <InputText v-model="mqttPassword" type="password" placeholder="Leer lassen um aktuelles zu behalten" />
                                        <small class="text-gray-400">Wird nur aktualisiert wenn angegeben</small>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Topic Präfix</label>
                                        <InputText v-model="config.mqtt.topic_prefix" placeholder="idm/heatpump" />
                                        <small class="text-gray-400">Topics sind: {prefix}/{sensor_name}</small>
                                    </div>

                                    <div class="p-3 border border-green-600 rounded bg-green-900/10 flex flex-col gap-3">
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-home text-green-400"></i>
                                            <span class="font-bold text-green-400">Home Assistant Discovery</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <Checkbox v-model="config.mqtt.ha_discovery_enabled" binary inputId="ha_discovery_enabled" />
                                            <label for="ha_discovery_enabled">Home Assistant Discovery aktivieren</label>
                                        </div>
                                        <div class="flex flex-col gap-2" v-if="config.mqtt.ha_discovery_enabled">
                                            <label>Discovery Präfix</label>
                                            <InputText v-model="config.mqtt.ha_discovery_prefix" placeholder="homeassistant" />
                                            <small class="text-gray-400">Standard: homeassistant</small>
                                        </div>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>QoS Level</label>
                                        <select v-model="config.mqtt.qos" class="p-2 bg-gray-700 border border-gray-600 rounded">
                                            <option :value="0">0 - At most once</option>
                                            <option :value="1">1 - At least once</option>
                                            <option :value="2">2 - Exactly once</option>
                                        </select>
                                    </div>

                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.mqtt.use_tls" binary inputId="mqtt_use_tls" />
                                        <label for="mqtt_use_tls">TLS/SSL Verschlüsselung nutzen</label>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Publish Intervall (Sekunden)</label>
                                        <InputNumber v-model="config.mqtt.publish_interval" :min="1" :max="3600" :useGrouping="false" />
                                        <small class="text-gray-400">Wie oft Sensordaten veröffentlicht werden (1-3600 Sekunden)</small>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Card>
                </TabPanel>

                <TabPanel header="Benachrichtigungen & AI">
                    <div class="flex flex-col gap-6">
                        <Card class="bg-gray-800 text-white" v-if="config.signal">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-comments text-green-400"></i>
                                    <span>Signal Benachrichtigungen</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.signal.enabled" binary inputId="signal_enabled" />
                                        <label for="signal_enabled" class="font-bold">Aktivieren</label>
                                    </div>

                                    <div v-if="config.signal.enabled" class="flex flex-col gap-4 p-3 border border-green-600 rounded bg-green-900/10">
                                        <div class="flex flex-col gap-2">
                                            <label>Signal CLI Pfad</label>
                                            <InputText v-model="config.signal.cli_path" placeholder="signal-cli" />
                                        </div>
                                        <div class="flex flex-col gap-2">
                                            <label>Sender-Nummer</label>
                                            <InputText v-model="config.signal.sender" placeholder="+49..." />
                                        </div>
                                        <div class="flex flex-col gap-2">
                                            <label>Empfänger (eine Nummer pro Zeile)</label>
                                            <Textarea v-model="signalRecipientsText" rows="4" class="font-mono text-sm" />
                                        </div>
                                        <Button label="Signal Test senden" icon="pi pi-send" severity="success" @click="sendSignalTest" />
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white" v-if="config.ai">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-bolt text-purple-400"></i>
                                    <span>AI Anomalie-Erkennung</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.ai.enabled" binary inputId="ai_enabled" />
                                        <label for="ai_enabled" class="font-bold">AI Alarm aktivieren</label>
                                    </div>
                                    <small class="text-gray-400">Das System lernt automatisch Muster, auch wenn der Alarm deaktiviert ist.</small>

                                    <div v-if="config.ai.enabled" class="flex flex-col gap-4 p-3 border border-purple-600 rounded bg-purple-900/10">
                                        <div class="flex flex-col gap-2">
                                            <label>Sensitivität (Sigma)</label>
                                            <InputNumber v-model="config.ai.sensitivity" :min="1.0" :max="10.0" :step="0.1" :minFractionDigits="1" mode="decimal" />
                                            <small class="text-gray-400">
                                                Niedriger (z.B. 2.0) = Empfindlicher, mehr Fehlalarme.
                                                Höher (z.B. 4.0) = Nur starke Abweichungen.
                                                Standard: 3.0
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </TabPanel>

                <TabPanel header="Sicherheit">
                    <div class="flex flex-col gap-6">
                        <Card class="bg-gray-800 text-white">
                            <template #title>Admin Sicherheit</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex flex-col gap-2">
                                        <label>Neues Passwort</label>
                                        <InputText v-model="newPassword" type="password" />
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white" v-if="config.network_security">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-shield text-yellow-400"></i>
                                    <span>Netzwerkzugriffskontrolle</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.network_security.enabled" binary inputId="network_security_enabled" />
                                        <label for="network_security_enabled" class="font-bold">IP-basierte Zugriffskontrolle aktivieren</label>
                                    </div>

                                    <div v-if="config.network_security.enabled" class="flex flex-col gap-4 p-3 border border-yellow-600 rounded bg-yellow-900/10">
                                        <div class="flex items-start gap-2 text-yellow-400">
                                            <i class="pi pi-exclamation-triangle mt-1"></i>
                                            <small>Warnung: Stelle sicher, dass deine IP auf der Whitelist steht, bevor du dies aktivierst, sonst sperrst du dich aus!</small>
                                        </div>

                                        <div class="flex flex-col gap-2">
                                            <label class="font-semibold">
                                                <i class="pi pi-check-circle text-green-400"></i> Whitelist (Diese IPs erlauben)
                                            </label>
                                            <Textarea
                                                v-model="whitelistText"
                                                placeholder="192.168.1.0/24&#10;10.0.0.5&#10;172.16.0.0/16"
                                                rows="4"
                                                class="font-mono text-sm"
                                            />
                                            <small class="text-gray-400">
                                                Eine IP-Adresse oder Netzwerk (CIDR) pro Zeile. Wenn Whitelist leer ist, sind alle IPs erlaubt (außer Blacklist).
                                                <br>Beispiel: 192.168.1.0/24 erlaubt 192.168.1.1 - 192.168.1.254
                                            </small>
                                        </div>

                                        <div class="flex flex-col gap-2">
                                            <label class="font-semibold">
                                                <i class="pi pi-ban text-red-400"></i> Blacklist (Diese IPs blockieren)
                                            </label>
                                            <Textarea
                                                v-model="blacklistText"
                                                placeholder="203.0.113.0/24&#10;198.51.100.5"
                                                rows="4"
                                                class="font-mono text-sm"
                                            />
                                            <small class="text-gray-400">
                                                Eine IP-Adresse oder Netzwerk (CIDR) pro Zeile. Blacklist wird zuerst geprüft (blockiert vor Whitelist).
                                            </small>
                                        </div>

                                        <div class="p-3 bg-blue-900/30 border border-blue-600 rounded">
                                            <div class="flex items-start gap-2">
                                                <i class="pi pi-info-circle text-blue-400 mt-1"></i>
                                                <div class="text-sm text-blue-200">
                                                    <strong>Deine aktuelle IP:</strong> {{ currentClientIP || 'Lade...' }}
                                                    <br><small class="text-blue-300">Stelle sicher, diese zur Whitelist hinzuzufügen!</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </TabPanel>

                <TabPanel header="System">
                    <div class="flex flex-col gap-6">
                        <Card class="bg-gray-800 text-white">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-chart-bar text-teal-400"></i>
                                    <span>Status</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center justify-between">
                                        <div>
                                            <div class="font-semibold">Updates</div>
                                            <div class="text-sm text-gray-400">
                                                Aktuell: {{ updateStatus.current_version || '...' }} · Latest: {{ updateStatus.latest_version || '...' }}
                                            </div>
                                            <div class="text-xs text-gray-400" v-if="updateStatus.update_type && updateStatus.update_type !== 'none'">
                                                Typ: {{ updateStatus.update_type }}
                                            </div>
                                        </div>
                                        <span
                                            class="text-xs font-semibold px-2 py-1 rounded-full"
                                            :class="updateStatus.update_available ? 'bg-yellow-500/20 text-yellow-200' : 'bg-green-500/20 text-green-200'"
                                        >
                                            {{ updateStatus.update_available ? 'Update verfügbar' : 'Aktuell' }}
                                        </span>
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <div>
                                            <div class="font-semibold">Signal</div>
                                            <div class="text-sm text-gray-400">
                                                {{ signalStatus.enabled ? 'Aktiviert' : 'Deaktiviert' }}
                                                · Empfänger: {{ signalStatus.recipients_count ?? 0 }}
                                            </div>
                                            <div class="text-xs text-gray-400">
                                                CLI: {{ signalStatus.cli_available ? 'Verfügbar' : 'Nicht gefunden' }}
                                            </div>
                                        </div>
                                    </div>
                                    <div class="flex justify-end">
                                        <Button label="Status aktualisieren" icon="pi pi-refresh" size="small" @click="loadStatus" :loading="statusLoading" />
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white" v-if="config.updates">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-refresh text-purple-400"></i>
                                    <span>Auto-Updates</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.updates.enabled" binary inputId="updates_enabled" />
                                        <label for="updates_enabled">Automatisch auf Updates prüfen & anwenden</label>
                                    </div>
                                    <div class="flex flex-col gap-2" v-if="config.updates.enabled">
                                        <label>Prüf-Intervall (Stunden)</label>
                                        <InputNumber v-model="config.updates.interval_hours" :min="1" :max="168" :useGrouping="false" />
                                        <small class="text-gray-400">1-168 Stunden (1 Woche)</small>
                                        <label class="mt-2">Modus</label>
                                        <select v-model="config.updates.mode" class="p-2 bg-gray-700 border border-gray-600 rounded">
                                            <option value="apply">Automatisch updaten</option>
                                            <option value="check">Nur prüfen</option>
                                        </select>
                                        <label class="mt-2">Update-Ziel</label>
                                        <select v-model="config.updates.target" class="p-2 bg-gray-700 border border-gray-600 rounded">
                                            <option value="all">Alle Updates</option>
                                            <option value="major">Nur Major</option>
                                            <option value="minor">Nur Minor</option>
                                            <option value="patch">Nur Patch</option>
                                        </select>
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white">
                            <template #title>Weboberfläche</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.web.write_enabled" binary inputId="write_enabled" />
                                        <label for="write_enabled">Schreibzugriff aktivieren (Manuelle Steuerung & Zeitplan)</label>
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-database text-blue-400"></i>
                                    <span>Backup & Wiederherstellung</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <!-- Create Backup -->
                                    <div class="flex flex-col gap-3 p-4 border border-blue-600 rounded bg-blue-900/10">
                                        <h3 class="text-lg font-semibold flex items-center gap-2">
                                            <i class="pi pi-download"></i>
                                            Backup erstellen
                                        </h3>
                                        <div class="flex items-center gap-2">
                                            <Checkbox v-model="backupIncludeInflux" binary inputId="backup_include_influx" />
                                            <label for="backup_include_influx">Metrics Zugangsdaten einschließen (sensibel)</label>
                                        </div>
                                        <Button
                                            label="Backup jetzt erstellen"
                                            icon="pi pi-download"
                                            @click="createBackup"
                                            :loading="creatingBackup"
                                            severity="info"
                                        />
                                    </div>

                                    <!-- Backup List -->
                                    <div class="flex flex-col gap-3">
                                        <div class="flex justify-between items-center">
                                            <h3 class="text-lg font-semibold flex items-center gap-2">
                                                <i class="pi pi-list"></i>
                                                Verfügbare Backups
                                            </h3>
                                            <Button
                                                label="Aktualisieren"
                                                icon="pi pi-refresh"
                                                @click="loadBackups"
                                                size="small"
                                                text
                                            />
                                        </div>

                                        <div v-if="loadingBackups" class="flex justify-center p-4">
                                            <i class="pi pi-spin pi-spinner text-2xl"></i>
                                        </div>

                                        <div v-else-if="backups.length === 0" class="text-center text-gray-400 p-4">
                                            Keine Backups verfügbar
                                        </div>

                                        <div v-else class="flex flex-col gap-2">
                                            <div
                                                v-for="backup in backups"
                                                :key="backup.filename"
                                                class="flex items-center justify-between p-3 bg-gray-700 rounded hover:bg-gray-600"
                                            >
                                                <div class="flex flex-col">
                                                    <span class="font-mono text-sm">{{ backup.filename }}</span>
                                                    <span class="text-xs text-gray-400">
                                                        {{ formatDate(backup.created_at) }} • {{ formatSize(backup.size) }}
                                                    </span>
                                                </div>
                                                <div class="flex gap-2">
                                                    <Button
                                                        icon="pi pi-download"
                                                        @click="downloadBackup(backup.filename)"
                                                        size="small"
                                                        severity="info"
                                                        text
                                                    />
                                                    <Button
                                                        icon="pi pi-upload"
                                                        @click="confirmRestore(backup.filename)"
                                                        size="small"
                                                        severity="warning"
                                                        text
                                                    />
                                                    <Button
                                                        icon="pi pi-trash"
                                                        @click="confirmDeleteBackup(backup.filename)"
                                                        size="small"
                                                        severity="danger"
                                                        text
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Upload Backup -->
                                    <div class="flex flex-col gap-3 p-4 border border-yellow-600 rounded bg-yellow-900/10">
                                        <h3 class="text-lg font-semibold flex items-center gap-2">
                                            <i class="pi pi-upload"></i>
                                            Aus Datei wiederherstellen
                                        </h3>
                                        <div class="flex items-start gap-2 text-yellow-400">
                                            <i class="pi pi-exclamation-triangle mt-1"></i>
                                            <small>Warnung: Wiederherstellung überschreibt die aktuelle Konfiguration!</small>
                                        </div>
                                        <input
                                            type="file"
                                            ref="fileInput"
                                            @change="handleFileSelect"
                                            accept=".zip"
                                            class="block w-full text-sm text-gray-400
                                                file:mr-4 file:py-2 file:px-4
                                                file:rounded file:border-0
                                                file:text-sm file:font-semibold
                                                file:bg-blue-600 file:text-white
                                                hover:file:bg-blue-700"
                                        />
                                        <Button
                                            label="Aus gewählter Datei wiederherstellen"
                                            icon="pi pi-upload"
                                            @click="restoreFromFile"
                                            :disabled="!selectedFile"
                                            :loading="restoringBackup"
                                            severity="warning"
                                        />
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <div class="flex justify-end">
                             <Button label="Dienst neu starten" icon="pi pi-refresh" severity="danger" @click="confirmRestart" />
                        </div>
                    </div>
                </TabPanel>

                <TabPanel header="Datenbank">
                    <Card class="bg-gray-800 text-white">
                        <template #title>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-database text-red-400"></i>
                                <span>Datenbank Wartung</span>
                            </div>
                        </template>
                        <template #content>
                            <div class="flex flex-col gap-4">
                                <div class="flex flex-col gap-2 p-4 border border-blue-600 rounded bg-blue-900/10">
                                    <div class="flex items-center justify-between gap-4">
                                        <div>
                                            <div class="font-semibold">VictoriaMetrics UI</div>
                                            <div class="text-sm text-gray-300">
                                                Öffne die VictoriaMetrics UI (vmui) für Datenabfragen und Administration.
                                            </div>
                                            <div class="text-xs text-gray-400 mt-1">{{ explorerUrl }}</div>
                                        </div>
                                        <Button
                                            label="Explorer öffnen"
                                            icon="pi pi-external-link"
                                            severity="info"
                                            @click="openExplorer"
                                        />
                                    </div>
                                </div>
                                <div class="flex flex-col gap-4 p-4 border border-red-600 rounded bg-red-900/10">
                                    <div class="flex items-start gap-2 text-red-400">
                                        <i class="pi pi-exclamation-triangle mt-1"></i>
                                        <div>
                                            <span class="font-bold">Gefahrenzone</span>
                                            <p class="text-sm opacity-80">
                                                Diese Aktionen sind destruktiv und können nicht rückgängig gemacht werden. Bitte sei vorsichtig.
                                            </p>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between mt-2">
                                        <div class="flex flex-col">
                                            <span class="font-semibold">Alle Daten löschen</span>
                                            <span class="text-sm text-gray-400">Entferne dauerhaft alle geloggten Daten aus VictoriaMetrics.</span>
                                        </div>
                                        <Button
                                            label="Datenbank löschen"
                                            icon="pi pi-trash"
                                            severity="danger"
                                            @click="showDeleteDialog = true"
                                        />
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Card>
                </TabPanel>

                <TabPanel header="Tools">
                    <Card class="bg-gray-800 text-white">
                        <template #title>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-key text-yellow-400"></i>
                                <span>Technikercode Generator</span>
                            </div>
                        </template>
                        <template #content>
                            <TechnicianCodeGenerator />
                        </template>
                    </Card>
                </TabPanel>
            </TabView>
        </div>

        <Dialog v-model:visible="showDeleteDialog" modal header="Datenbank löschen" :style="{ width: '450px' }">
            <div class="flex flex-col gap-4">
                <div class="flex items-start gap-3">
                    <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
                    <div class="flex flex-col gap-2">
                        <span class="font-bold text-lg">Bist du dir absolut sicher?</span>
                        <p class="text-gray-300">
                            Diese Aktion löscht <span class="font-bold text-red-400">ALLE</span> Daten dauerhaft aus der Datenbank.
                            Das kann nicht rückgängig gemacht werden.
                        </p>
                        <p class="text-sm text-gray-400">
                            Bitte tippe <span class="font-mono bg-gray-700 px-1 rounded">DELETE</span> zur Bestätigung.
                        </p>
                    </div>
                </div>

                <div class="flex flex-col gap-2">
                    <InputText
                        v-model="deleteConfirmationText"
                        placeholder="Tippe DELETE zur Bestätigung"
                        class="w-full"
                        :class="{'p-invalid': deleteConfirmationText && deleteConfirmationText !== 'DELETE'}"
                    />
                </div>
            </div>

            <template #footer>
                <Button label="Abbrechen" icon="pi pi-times" text @click="showDeleteDialog = false" />
                <Button
                    label="Alles löschen"
                    icon="pi pi-trash"
                    severity="danger"
                    @click="confirmDeleteDatabase"
                    :disabled="deleteConfirmationText !== 'DELETE'"
                    :loading="deletingDatabase"
                />
            </template>
        </Dialog>

        <div class="flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4">
            <Button label="Konfiguration speichern" icon="pi pi-save" @click="saveConfig" :loading="saving" size="large" />
        </div>

        <Toast />
        <ConfirmDialog />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
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
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import TechnicianCodeGenerator from '../components/TechnicianCodeGenerator.vue';

const config = ref({
    idm: { host: '', port: 502, circuits: ['A'], zones: [] },
    metrics: { url: '' },
    web: { write_enabled: false },
    logging: { interval: 60, realtime_mode: false },
    mqtt: { enabled: false, broker: '', port: 1883, username: '', topic_prefix: 'idm/heatpump', qos: 0, use_tls: false, publish_interval: 60, ha_discovery_enabled: false, ha_discovery_prefix: 'homeassistant' },
    network_security: { enabled: false, whitelist: [], blacklist: [] },
    signal: { enabled: false, cli_path: 'signal-cli', sender: '', recipients: [] },
    ai: { enabled: false, sensitivity: 3.0 },
    updates: { enabled: false, interval_hours: 12, mode: 'apply', target: 'all' }
});
const newPassword = ref('');
const mqttPassword = ref('');
const whitelistText = ref('');
const blacklistText = ref('');
const signalRecipientsText = ref('');
const updateStatus = ref({});
const signalStatus = ref({});
const statusLoading = ref(false);
const currentClientIP = ref('');
const loading = ref(true);
const saving = ref(false);
const toast = useToast();
const confirm = useConfirm();

// Backup & Restore state
const backups = ref([]);
const loadingBackups = ref(false);
const creatingBackup = ref(false);
const restoringBackup = ref(false);
const backupIncludeInflux = ref(true);
const selectedFile = ref(null);
const fileInput = ref(null);
const explorerUrl = ref('http://localhost:8888');

// Database Maintenance
const showDeleteDialog = ref(false);
const deleteConfirmationText = ref('');
const deletingDatabase = ref(false);

onMounted(async () => {
    try {
        if (typeof window !== 'undefined') {
            explorerUrl.value = `${window.location.protocol}//${window.location.hostname}:8428/vmui/`;
        }
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

        // Get current client IP
        try {
            const ipRes = await axios.get('/api/health');
            currentClientIP.value = ipRes.data.client_ip || 'Unbekannt';
        } catch (e) {
            console.error('Failed to get client IP', e);
        }

        // Load backups
        loadBackups();
        loadStatus();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Konfiguration konnte nicht geladen werden', life: 3000 });
    } finally {
        loading.value = false;
    }
});

const openExplorer = () => {
    if (typeof window === 'undefined') return;
    window.open(explorerUrl.value, '_blank', 'noopener');
};

const sendSignalTest = async () => {
    try {
        const res = await axios.post('/api/signal/test', { message: 'Signal Test vom IDM Metrics Collector' });
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Fehler', detail: res.data.error || 'Signal Test fehlgeschlagen', life: 3000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: e.response?.data?.error || e.message, life: 5000 });
    }
};

const loadStatus = async () => {
    statusLoading.value = true;
    try {
        const [updateRes, signalRes] = await Promise.all([
            axios.get('/api/check-update'),
            axios.get('/api/signal/status')
        ]);
        updateStatus.value = updateRes.data;
        signalStatus.value = signalRes.data;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Status konnte nicht geladen werden', life: 3000 });
    } finally {
        statusLoading.value = false;
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
            ai_enabled: config.value.ai?.enabled || false,
            ai_sensitivity: config.value.ai?.sensitivity || 3.0,
            updates_enabled: config.value.updates?.enabled || false,
            updates_interval_hours: config.value.updates?.interval_hours || 12,
            updates_mode: config.value.updates?.mode || 'apply',
            updates_target: config.value.updates?.target || 'all',
            new_password: newPassword.value || undefined
        };
        const res = await axios.post('/api/config', payload);
        toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message || 'Einstellungen erfolgreich gespeichert', life: 3000 });
        newPassword.value = '';
        mqttPassword.value = '';
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
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Backups konnten nicht geladen werden', life: 3000 });
    } finally {
        loadingBackups.value = false;
    }
};

const createBackup = async () => {
    creatingBackup.value = true;
    try {
        const res = await axios.post('/api/backup/create', {
            include_influx_config: backupIncludeInflux.value
        });
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
        toast.add({ severity: 'error', summary: 'Fehler', detail: 'Backup Download fehlgeschlagen', life: 3000 });
    }
};

const confirmRestore = (filename) => {
    confirm.require({
        message: `Konfiguration von "${filename}" wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!`,
        header: 'Backup Wiederherstellen',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-warning',
        accept: async () => {
            restoringBackup.value = true;
            try {
                const res = await axios.post('/api/backup/restore', { filename });
                if (res.data.success) {
                    toast.add({ severity: 'success', summary: 'Erfolg', detail: res.data.message, life: 5000 });
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

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
};

const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
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
