<template>
    <div class="p-4 flex flex-col gap-4">
        <h1 class="text-2xl font-bold mb-4">Scheduler</h1>

        <div v-if="loading" class="flex justify-center">
            <i class="pi pi-spin pi-spinner text-4xl"></i>
        </div>

        <div v-else class="flex flex-col gap-6">
             <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                 <Card v-for="job in jobs" :key="job.id" class="bg-gray-800 text-white relative">
                      <template #title>
                          <div class="flex justify-between items-center">
                              <span class="text-lg truncate">{{ job.sensor }}</span>
                              <Tag :severity="job.enabled ? 'success' : 'warning'" :value="job.enabled ? 'Active' : 'Paused'" />
                          </div>
                      </template>
                      <template #content>
                           <div class="flex flex-col gap-2">
                                <div class="text-2xl font-bold text-blue-400">{{ job.value }}</div>
                                <div class="text-gray-400">At {{ job.time }}</div>
                                <div class="flex gap-1 flex-wrap">
                                     <Tag v-for="day in job.days" :key="day" :value="day" severity="info" />
                                </div>
                           </div>
                      </template>
                      <template #footer>
                           <div class="flex gap-2 justify-end">
                                <Button icon="pi pi-play" text severity="info" v-tooltip="'Run Now'" @click="runJob(job.id)" />
                                <Button :icon="job.enabled ? 'pi pi-pause' : 'pi pi-play'" text severity="warning" @click="toggleJob(job.id, job.enabled)" />
                                <Button icon="pi pi-trash" text severity="danger" @click="deleteJob(job.id)" />
                           </div>
                      </template>
                 </Card>

                 <Card class="bg-gray-800 text-white border-dashed border-2 border-gray-600 flex justify-center items-center cursor-pointer hover:bg-gray-700 transition-colors" @click="showAddDialog = true">
                     <template #content>
                         <div class="flex flex-col items-center justify-center h-full py-8 text-gray-400">
                             <i class="pi pi-plus text-4xl mb-2"></i>
                             <span>Add Schedule</span>
                         </div>
                     </template>
                 </Card>
             </div>
        </div>

        <Dialog v-model:visible="showAddDialog" header="Add Schedule" :modal="true" class="p-fluid">
            <div class="flex flex-col gap-4 min-w-[300px] md:min-w-[400px]">
                 <div class="flex flex-col gap-2">
                     <label>Sensor</label>
                     <Dropdown v-model="newJob.sensor" :options="sensors" optionLabel="name" optionValue="name" placeholder="Select Sensor" filter />
                 </div>
                 <div class="flex flex-col gap-2">
                     <label>Value</label>
                     <InputText v-model="newJob.value" />
                 </div>
                 <div class="flex flex-col gap-2">
                     <label>Time (HH:MM)</label>
                     <InputMask v-model="newJob.time" mask="99:99" placeholder="HH:MM" />
                 </div>
                 <div class="flex flex-col gap-2">
                     <label>Days</label>
                     <MultiSelect v-model="newJob.days" :options="days" placeholder="Select Days" display="chip" />
                 </div>
                 <Button label="Save" icon="pi pi-check" @click="addJob" :loading="saving" />
            </div>
        </Dialog>
        <Toast />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import InputMask from 'primevue/inputmask';
import MultiSelect from 'primevue/multiselect';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';

const jobs = ref([]);
const sensors = ref([]);
const loading = ref(true);
const saving = ref(false);
const showAddDialog = ref(false);
const toast = useToast();

const newJob = ref({
    sensor: null,
    value: '',
    time: '',
    days: []
});

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

onMounted(() => {
    fetchSchedule();
});

const fetchSchedule = async () => {
    loading.value = true;
    try {
        const res = await axios.get('/api/schedule');
        jobs.value = res.data.jobs;
        sensors.value = res.data.sensors;
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load schedule', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const addJob = async () => {
    saving.value = true;
    try {
        await axios.post('/api/schedule', {
            action: 'add',
            sensor: newJob.value.sensor,
            value: newJob.value.value,
            time: newJob.value.time,
            days: newJob.value.days
        });
        toast.add({ severity: 'success', summary: 'Success', detail: 'Schedule added', life: 3000 });
        showAddDialog.value = false;
        fetchSchedule();
        newJob.value = { sensor: null, value: '', time: '', days: [] };
    } catch (e) {
         toast.add({ severity: 'error', summary: 'Error', detail: e.response?.data?.error || e.message, life: 3000 });
    } finally {
        saving.value = false;
    }
};

const deleteJob = async (id) => {
    try {
        await axios.post('/api/schedule', { action: 'delete', job_id: id });
        fetchSchedule();
        toast.add({ severity: 'success', summary: 'Success', detail: 'Deleted', life: 3000 });
    } catch (e) {
         toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete', life: 3000 });
    }
};

const toggleJob = async (id, currentState) => {
     try {
        await axios.post('/api/schedule', { action: 'toggle', job_id: id, current_state: currentState });
        fetchSchedule();
    } catch (e) {
         toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to toggle', life: 3000 });
    }
};

const runJob = async (id) => {
     try {
        const res = await axios.post('/api/schedule', { action: 'run_now', job_id: id });
        toast.add({ severity: 'success', summary: 'Executed', detail: res.data.message, life: 3000 });
    } catch (e) {
         toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to run', life: 3000 });
    }
};
</script>
