<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Configuration</h1>

        <div v-if="loading" class="flex justify-center">
            <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else>
            <TabView>
                <TabPanel header="General">
                    <div class="flex flex-col gap-6">
                        <Card class="bg-gray-800 text-white">
                            <template #title>IDM Heat Pump</template>
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
                                        <label class="font-bold">Enabled Features</label>
                                        <div class="flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50">
                                            <div class="flex items-center gap-2">
                                                <Checkbox v-model="config.idm.circuits" inputId="circuitA" value="A" disabled />
                                                <label for="circuitA" class="opacity-50">Circuit A (Always On)</label>
                                            </div>
                                            <div class="flex flex-wrap gap-4">
                                                <div v-for="c in ['B', 'C', 'D', 'E', 'F', 'G']" :key="c" class="flex items-center gap-2">
                                                    <Checkbox v-model="config.idm.circuits" :inputId="'circuit'+c" :value="c" />
                                                    <label :for="'circuit'+c">Circuit {{ c }}</label>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="flex flex-col gap-2 p-2 border border-gray-700 rounded bg-gray-900/50">
                                            <label class="text-sm text-gray-400">Zone Modules</label>
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
                            <template #title>InfluxDB</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex flex-col gap-2">
                                        <label>URL</label>
                                        <InputText v-model="config.influx.url" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Organization</label>
                                        <InputText v-model="config.influx.org" />
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <label>Bucket</label>
                                        <InputText v-model="config.influx.bucket" />
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </TabPanel>

                <TabPanel header="Collection">
                    <Card class="bg-gray-800 text-white">
                        <template #title>Data Collection</template>
                        <template #content>
                            <div class="flex flex-col gap-4">
                                <div class="flex items-center gap-2">
                                    <Checkbox v-model="config.logging.realtime_mode" binary inputId="realtime_mode" />
                                    <label for="realtime_mode">Realtime Mode (1 second interval)</label>
                                </div>
                                <div class="flex flex-col gap-2" v-if="!config.logging.realtime_mode">
                                    <label>Polling Interval (seconds)</label>
                                    <InputNumber v-model="config.logging.interval" :min="1" :max="3600" :useGrouping="false" />
                                    <small class="text-gray-400">How often to read data from heat pump (1-3600 seconds)</small>
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
                                    <label for="mqtt_enabled" class="font-bold">Enable MQTT Publishing</label>
                                </div>

                                <div v-if="config.mqtt.enabled" class="flex flex-col gap-4 p-3 border border-blue-600 rounded bg-blue-900/10">
                                    <div class="flex flex-col gap-2">
                                        <label>Broker Address</label>
                                        <InputText v-model="config.mqtt.broker" placeholder="mqtt.example.com" />
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Port</label>
                                        <InputNumber v-model="config.mqtt.port" :useGrouping="false" :min="1" :max="65535" />
                                        <small class="text-gray-400">Default: 1883 (non-TLS) or 8883 (TLS)</small>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Username (Optional)</label>
                                        <InputText v-model="config.mqtt.username" placeholder="Optional" />
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Password (Optional)</label>
                                        <InputText v-model="mqttPassword" type="password" placeholder="Leave empty to keep current" />
                                        <small class="text-gray-400">Only updated if provided</small>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Topic Prefix</label>
                                        <InputText v-model="config.mqtt.topic_prefix" placeholder="idm/heatpump" />
                                        <small class="text-gray-400">Topics will be: {prefix}/{sensor_name}</small>
                                    </div>

                                    <div class="p-3 border border-green-600 rounded bg-green-900/10 flex flex-col gap-3">
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-home text-green-400"></i>
                                            <span class="font-bold text-green-400">Home Assistant Discovery</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <Checkbox v-model="config.mqtt.ha_discovery_enabled" binary inputId="ha_discovery_enabled" />
                                            <label for="ha_discovery_enabled">Enable Home Assistant Discovery</label>
                                        </div>
                                        <div class="flex flex-col gap-2" v-if="config.mqtt.ha_discovery_enabled">
                                            <label>Discovery Prefix</label>
                                            <InputText v-model="config.mqtt.ha_discovery_prefix" placeholder="homeassistant" />
                                            <small class="text-gray-400">Default: homeassistant</small>
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
                                        <label for="mqtt_use_tls">Use TLS/SSL encryption</label>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <label>Publish Interval (seconds)</label>
                                        <InputNumber v-model="config.mqtt.publish_interval" :min="1" :max="3600" :useGrouping="false" />
                                        <small class="text-gray-400">How often to publish sensor data (1-3600 seconds)</small>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Card>
                </TabPanel>

                <TabPanel header="Security">
                    <div class="flex flex-col gap-6">
                        <Card class="bg-gray-800 text-white">
                            <template #title>Admin Security</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex flex-col gap-2">
                                        <label>New Password</label>
                                        <InputText v-model="newPassword" type="password" />
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white" v-if="config.network_security">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-shield text-yellow-400"></i>
                                    <span>Network Access Control</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.network_security.enabled" binary inputId="network_security_enabled" />
                                        <label for="network_security_enabled" class="font-bold">Enable IP-based Access Control</label>
                                    </div>

                                    <div v-if="config.network_security.enabled" class="flex flex-col gap-4 p-3 border border-yellow-600 rounded bg-yellow-900/10">
                                        <div class="flex items-start gap-2 text-yellow-400">
                                            <i class="pi pi-exclamation-triangle mt-1"></i>
                                            <small>Warning: Make sure your IP is whitelisted before enabling, or you will be locked out!</small>
                                        </div>

                                        <div class="flex flex-col gap-2">
                                            <label class="font-semibold">
                                                <i class="pi pi-check-circle text-green-400"></i> Whitelist (Allow these IPs)
                                            </label>
                                            <Textarea
                                                v-model="whitelistText"
                                                placeholder="192.168.1.0/24&#10;10.0.0.5&#10;172.16.0.0/16"
                                                rows="4"
                                                class="font-mono text-sm"
                                            />
                                            <small class="text-gray-400">
                                                One IP address or network (CIDR) per line. If whitelist is empty, all IPs are allowed (unless blacklisted).
                                                <br>Example: 192.168.1.0/24 allows 192.168.1.1 - 192.168.1.254
                                            </small>
                                        </div>

                                        <div class="flex flex-col gap-2">
                                            <label class="font-semibold">
                                                <i class="pi pi-ban text-red-400"></i> Blacklist (Block these IPs)
                                            </label>
                                            <Textarea
                                                v-model="blacklistText"
                                                placeholder="203.0.113.0/24&#10;198.51.100.5"
                                                rows="4"
                                                class="font-mono text-sm"
                                            />
                                            <small class="text-gray-400">
                                                One IP address or network (CIDR) per line. Blacklist is checked first (blocks before whitelist).
                                            </small>
                                        </div>

                                        <div class="p-3 bg-blue-900/30 border border-blue-600 rounded">
                                            <div class="flex items-start gap-2">
                                                <i class="pi pi-info-circle text-blue-400 mt-1"></i>
                                                <div class="text-sm text-blue-200">
                                                    <strong>Your current IP:</strong> {{ currentClientIP || 'Loading...' }}
                                                    <br><small class="text-blue-300">Make sure to add this to the whitelist!</small>
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
                            <template #title>Web Interface</template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <div class="flex items-center gap-2">
                                        <Checkbox v-model="config.web.write_enabled" binary inputId="write_enabled" />
                                        <label for="write_enabled">Enable Write Access (Manual Control & Schedule)</label>
                                    </div>
                                </div>
                            </template>
                        </Card>

                        <Card class="bg-gray-800 text-white">
                            <template #title>
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-database text-blue-400"></i>
                                    <span>Backup & Restore</span>
                                </div>
                            </template>
                            <template #content>
                                <div class="flex flex-col gap-4">
                                    <!-- Create Backup -->
                                    <div class="flex flex-col gap-3 p-4 border border-blue-600 rounded bg-blue-900/10">
                                        <h3 class="text-lg font-semibold flex items-center gap-2">
                                            <i class="pi pi-download"></i>
                                            Create Backup
                                        </h3>
                                        <div class="flex items-center gap-2">
                                            <Checkbox v-model="backupIncludeInflux" binary inputId="backup_include_influx" />
                                            <label for="backup_include_influx">Include InfluxDB credentials (sensitive)</label>
                                        </div>
                                        <Button
                                            label="Create Backup Now"
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
                                                Available Backups
                                            </h3>
                                            <Button
                                                label="Refresh"
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
                                            No backups available
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
                                            Restore from File
                                        </h3>
                                        <div class="flex items-start gap-2 text-yellow-400">
                                            <i class="pi pi-exclamation-triangle mt-1"></i>
                                            <small>Warning: Restoring will overwrite current configuration!</small>
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
                                            label="Restore from Selected File"
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
                             <Button label="Restart Service" icon="pi pi-refresh" severity="danger" @click="confirmRestart" />
                        </div>
                    </div>
                </TabPanel>

                <TabPanel header="Database">
                    <Card class="bg-gray-800 text-white">
                        <template #title>
                            <div class="flex items-center gap-2">
                                <i class="pi pi-database text-red-400"></i>
                                <span>Database Maintenance</span>
                            </div>
                        </template>
                        <template #content>
                            <div class="flex flex-col gap-4">
                                <div class="flex flex-col gap-4 p-4 border border-red-600 rounded bg-red-900/10">
                                    <div class="flex items-start gap-2 text-red-400">
                                        <i class="pi pi-exclamation-triangle mt-1"></i>
                                        <div>
                                            <span class="font-bold">Danger Zone</span>
                                            <p class="text-sm opacity-80">
                                                These actions are destructive and cannot be undone. Please be careful.
                                            </p>
                                        </div>
                                    </div>

                                    <div class="flex items-center justify-between mt-2">
                                        <div class="flex flex-col">
                                            <span class="font-semibold">Delete All Data</span>
                                            <span class="text-sm text-gray-400">Permanently remove all logged data from InfluxDB.</span>
                                        </div>
                                        <Button
                                            label="Delete Database"
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
                                <span>Technician Code Generator</span>
                            </div>
                        </template>
                        <template #content>
                            <TechnicianCodeGenerator />
                        </template>
                    </Card>
                </TabPanel>
            </TabView>
        </div>

        <Dialog v-model:visible="showDeleteDialog" modal header="Delete Database" :style="{ width: '450px' }">
            <div class="flex flex-col gap-4">
                <div class="flex items-start gap-3">
                    <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
                    <div class="flex flex-col gap-2">
                        <span class="font-bold text-lg">Are you absolutely sure?</span>
                        <p class="text-gray-300">
                            This action will permanently delete <span class="font-bold text-red-400">ALL</span> data from the database.
                            This cannot be undone.
                        </p>
                        <p class="text-sm text-gray-400">
                            Please type <span class="font-mono bg-gray-700 px-1 rounded">DELETE</span> to confirm.
                        </p>
                    </div>
                </div>

                <div class="flex flex-col gap-2">
                    <InputText
                        v-model="deleteConfirmationText"
                        placeholder="Type DELETE to confirm"
                        class="w-full"
                        :class="{'p-invalid': deleteConfirmationText && deleteConfirmationText !== 'DELETE'}"
                    />
                </div>
            </div>

            <template #footer>
                <Button label="Cancel" icon="pi pi-times" text @click="showDeleteDialog = false" />
                <Button
                    label="Delete Everything"
                    icon="pi pi-trash"
                    severity="danger"
                    @click="confirmDeleteDatabase"
                    :disabled="deleteConfirmationText !== 'DELETE'"
                    :loading="deletingDatabase"
                />
            </template>
        </Dialog>

        <div class="flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4">
            <Button label="Save Configuration" icon="pi pi-save" @click="saveConfig" :loading="saving" size="large" />
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
    influx: { url: '', org: '', bucket: '' },
    web: { write_enabled: false },
    logging: { interval: 60, realtime_mode: false },
    mqtt: { enabled: false, broker: '', port: 1883, username: '', topic_prefix: 'idm/heatpump', qos: 0, use_tls: false, publish_interval: 60, ha_discovery_enabled: false, ha_discovery_prefix: 'homeassistant' },
    network_security: { enabled: false, whitelist: [], blacklist: [] }
});
const newPassword = ref('');
const mqttPassword = ref('');
const whitelistText = ref('');
const blacklistText = ref('');
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

// Database Maintenance
const showDeleteDialog = ref(false);
const deleteConfirmationText = ref('');
const deletingDatabase = ref(false);

onMounted(async () => {
    try {
        const res = await axios.get('/api/config');
        config.value = res.data;

        // Convert whitelist/blacklist arrays to text
        if (config.value.network_security) {
            whitelistText.value = (config.value.network_security.whitelist || []).join('\n');
            blacklistText.value = (config.value.network_security.blacklist || []).join('\n');
        }

        // Get current client IP
        try {
            const ipRes = await axios.get('/api/health');
            currentClientIP.value = ipRes.data.client_ip || 'Unknown';
        } catch (e) {
            console.error('Failed to get client IP', e);
        }

        // Load backups
        loadBackups();
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load config', life: 3000 });
    } finally {
        loading.value = false;
    }
});

const saveConfig = async () => {
    saving.value = true;
    try {
        const payload = {
            idm_host: config.value.idm.host,
            idm_port: config.value.idm.port,
            circuits: config.value.idm.circuits,
            zones: config.value.idm.zones,
            influx_url: config.value.influx.url,
            influx_org: config.value.influx.org,
            influx_bucket: config.value.influx.bucket,
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
            new_password: newPassword.value || undefined
        };
        const res = await axios.post('/api/config', payload);
        toast.add({ severity: 'success', summary: 'Success', detail: res.data.message || 'Settings saved successfully', life: 3000 });
        newPassword.value = '';
        mqttPassword.value = '';
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || e.message, life: 5000 });
    } finally {
        saving.value = false;
    }
};

const confirmRestart = () => {
    confirm.require({
        message: 'Are you sure you want to restart the service?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: async () => {
            try {
                const res = await axios.post('/api/restart');
                toast.add({ severity: 'info', summary: 'Restarting', detail: res.data.message, life: 3000 });
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to restart', life: 3000 });
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
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load backups', life: 3000 });
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
            toast.add({ severity: 'success', summary: 'Success', detail: `Backup created: ${res.data.filename}`, life: 3000 });
            loadBackups();
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 3000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || 'Failed to create backup', life: 3000 });
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
        toast.add({ severity: 'success', summary: 'Success', detail: 'Backup downloaded', life: 2000 });
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to download backup', life: 3000 });
    }
};

const confirmRestore = (filename) => {
    confirm.require({
        message: `Restore configuration from "${filename}"? This will overwrite your current settings!`,
        header: 'Restore Backup',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-warning',
        accept: async () => {
            restoringBackup.value = true;
            try {
                const res = await axios.post('/api/backup/restore', { filename });
                if (res.data.success) {
                    toast.add({ severity: 'success', summary: 'Success', detail: res.data.message, life: 5000 });
                    setTimeout(() => location.reload(), 2000);
                } else {
                    toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 5000 });
                }
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || 'Restore failed', life: 5000 });
            } finally {
                restoringBackup.value = false;
            }
        }
    });
};

const confirmDeleteBackup = (filename) => {
    confirm.require({
        message: `Delete backup "${filename}"?`,
        header: 'Delete Backup',
        icon: 'pi pi-trash',
        acceptClass: 'p-button-danger',
        accept: async () => {
            try {
                await axios.delete(`/api/backup/delete/${filename}`);
                toast.add({ severity: 'success', summary: 'Success', detail: 'Backup deleted', life: 2000 });
                loadBackups();
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete backup', life: 3000 });
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
        message: 'Restore configuration from uploaded file? This will overwrite your current settings!',
        header: 'Restore from File',
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
                    toast.add({ severity: 'success', summary: 'Success', detail: res.data.message, life: 5000 });
                    selectedFile.value = null;
                    if (fileInput.value) fileInput.value.value = '';
                    setTimeout(() => location.reload(), 2000);
                } else {
                    toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 5000 });
                }
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || 'Restore failed', life: 5000 });
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
            toast.add({ severity: 'success', summary: 'Success', detail: res.data.message, life: 5000 });
            showDeleteDialog.value = false;
            deleteConfirmationText.value = '';
        } else {
            toast.add({ severity: 'error', summary: 'Error', detail: res.data.error, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || 'Failed to delete database', life: 5000 });
    } finally {
        deletingDatabase.value = false;
    }
};
</script>
