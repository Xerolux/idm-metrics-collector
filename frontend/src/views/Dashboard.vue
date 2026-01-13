<template>
    <div class="p-4 flex flex-col h-full">
         <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4 sm:gap-0">
            <h1 class="text-2xl font-bold">Dashboard</h1>
            <div class="flex gap-2">
                 <Button label="Grafana öffnen" icon="pi pi-chart-line" @click="openGrafana" severity="secondary" />
                 <Button label="Widget hinzufügen" icon="pi pi-plus" @click="openAddWidget" />
            </div>
        </div>

        <div class="grid-stack bg-gray-800 rounded-lg min-h-[500px]"></div>

        <Teleport v-for="widget in widgets" :key="widget.id" :to="'#mount_' + widget.id">
            <div class="relative h-full w-full p-3 flex flex-col justify-between">
                <DashboardWidget
                    :title="widget.title"
                    :value="sensors[widget.sensor] !== undefined ? sensors[widget.sensor] : '...'"
                    :unit="widget.unit"
                />
                 <div class="absolute top-1 right-1 cursor-pointer text-gray-500 hover:text-red-500 z-10" @click="removeWidget(widget.id)">
                    <i class="pi pi-times"></i>
                </div>
            </div>
        </Teleport>

        <Dialog v-model:visible="showAddWidget" header="Widget hinzufügen" :modal="true">
            <div class="flex flex-col gap-4 min-w-[300px]">
                <label>Sensor wählen</label>
                <Dropdown v-model="selectedSensor" :options="sensorOptions" optionLabel="name" placeholder="Wähle einen Sensor" filter />
                <Button label="Hinzufügen" @click="confirmAddWidget" :disabled="!selectedSensor" />
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { GridStack } from 'gridstack';
import 'gridstack/dist/gridstack.min.css';
import axios from 'axios';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import DashboardWidget from '../components/DashboardWidget.vue';

const grid = ref(null);
const sensors = ref({});
const widgets = ref([]);
const showAddWidget = ref(false);
const selectedSensor = ref(null);
const sensorOptions = ref([]);
const timer = ref(null);

onMounted(async () => {
        try {
        const res = await axios.get('/api/data');
        sensors.value = res.data;
        sensorOptions.value = Object.keys(res.data).map(k => ({ name: k, value: k }));
        } catch(e) {}

    grid.value = GridStack.init({
        float: true,
        cellHeight: 100,
        minRow: 1,
        margin: 5,
        column: 6,
        disableOneColumnMode: false,
        oneColumnModeDomSort: true,
        oneColumnModeWidth: 768
    });

    const savedLayout = localStorage.getItem('dashboard_layout');
    let layoutToLoad = [];
    const defaults = [
        // 6 Standard-Widgets - Heizkreis A und COP nur in Grafana als Diagramme!
        { x: 0, y: 0, w: 2, h: 2, id: 'w1', sensor: 'temp_outside', title: 'Außentemperatur', unit: '°C' },
        { x: 2, y: 0, w: 2, h: 2, id: 'w2', sensor: 'temp_heat_pump_flow', title: 'Vorlauf WP', unit: '°C' },
        { x: 4, y: 0, w: 2, h: 2, id: 'w3', sensor: 'temp_heat_pump_return', title: 'Rücklauf WP', unit: '°C' },
        { x: 0, y: 2, w: 2, h: 2, id: 'w4', sensor: 'temp_heat_storage', title: 'Pufferspeicher', unit: '°C' },
        { x: 2, y: 2, w: 2, h: 2, id: 'w5', sensor: 'temp_water_heater_top', title: 'Warmwasser', unit: '°C' },
        { x: 4, y: 2, w: 2, h: 2, id: 'w6', sensor: 'power_current_draw', title: 'Leistungsaufnahme', unit: 'kW' },
    ];

    if (savedLayout) {
        try {
            layoutToLoad = JSON.parse(savedLayout);
        } catch (e) { console.error(e) }
    }

    if (!layoutToLoad || layoutToLoad.length === 0) {
        layoutToLoad = defaults;
    }

    loadGrid(layoutToLoad);

    grid.value.on('change', (event, items) => {
        saveLayout();
    });

        grid.value.on('dragstop', (event, element) => {
            saveLayout();
    });

    grid.value.on('resizestop', (event, element) => {
            saveLayout();
    });

    timer.value = setInterval(fetchData, 2000);
});

onUnmounted(() => {
        if (timer.value) clearInterval(timer.value);
});

const loadGrid = (layout) => {
    grid.value.removeAll();
    widgets.value = [];

    layout.forEach(item => {
        addWidgetToGrid(item);
    });
};

const addWidgetToGrid = (item) => {
    const id = item.id || `w_${Date.now()}`;
    const contentHtml = `<div id="mount_${id}" class="h-full w-full relative"></div>`;

    // Create widget without content first to avoid escaping issues
    const el = grid.value.addWidget({
        x: item.x,
        y: item.y,
        w: item.w,
        h: item.h,
        id: id,
        content: ''
    });

    // Manually set innerHTML of the content div
    if (el) {
        const contentEl = el.querySelector('.grid-stack-item-content');
        if (contentEl) {
            contentEl.innerHTML = contentHtml;
        }
    }

    // Ensure DOM is ready before Vue tries to Teleport
    nextTick(() => {
        widgets.value.push({
            ...item,
            id: id
        });
    });
};

const saveLayout = () => {
        const items = grid.value.getGridItems();
        const layout = items.map(item => {
            const w = widgets.value.find(x => x.id == item.gridstackNode.id);
            return {
                x: item.gridstackNode.x,
                y: item.gridstackNode.y,
                w: item.gridstackNode.w,
                h: item.gridstackNode.h,
                id: item.gridstackNode.id,
                sensor: w ? w.sensor : '',
                title: w ? w.title : '',
                unit: w ? w.unit : ''
            };
        });
        localStorage.setItem('dashboard_layout', JSON.stringify(layout));
};

const fetchData = async () => {
    try {
        const res = await axios.get('/api/data');
        sensors.value = res.data;

        if (sensorOptions.value.length === 0) {
                sensorOptions.value = Object.keys(res.data).map(k => ({ name: k, value: k }));
        }
    } catch (e) {}
};

const openAddWidget = () => {
    showAddWidget.value = true;
};

const confirmAddWidget = () => {
    if (selectedSensor.value) {
        addWidgetToGrid({
            x: 0, y: 0, w: 2, h: 2,
            sensor: selectedSensor.value.value,
            title: selectedSensor.value.name,
            unit: ''
        });
        showAddWidget.value = false;
        selectedSensor.value = null;
        saveLayout();
    }
};

const removeWidget = (id) => {
        const el = document.getElementById(`mount_${id}`);
        if (el) {
            const gridItem = el.closest('.grid-stack-item');
            if (gridItem) {
                 grid.value.removeWidget(gridItem);
            }
        }

        widgets.value = widgets.value.filter(w => w.id !== id);
        saveLayout();
};

const openGrafana = () => {
    const hostname = window.location.hostname;
    window.open(`http://${hostname}:3001`, '_blank');
};
</script>

<style>
.grid-stack-item-content {
    background-color: #1f2937; /* gray-800 */
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}
</style>
