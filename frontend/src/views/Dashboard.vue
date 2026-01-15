<template>
    <div class="p-4 flex flex-col h-full">
         <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4 lg:mb-6 gap-4 lg:gap-0">
             <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold">Dashboard</h1>
             <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full lg:w-auto">
                  <Button label="Widget hinzufügen" icon="pi pi-plus" @click="openAddWidget" :disabled="!editMode" class="w-full sm:w-auto order-1 sm:order-3" />
             </div>
         </div>

        <div class="grid-stack bg-gray-800/50 rounded-xl min-h-[500px] border border-gray-700/50">
            <!-- Loading skeleton for dashboard -->
            <div v-if="!grid" class="absolute inset-0 p-6">
                <SkeletonGroup variant="card" :count="6" />
            </div>
        </div>

        <Teleport v-for="widget in widgets" :key="widget.id" :to="'#mount_' + widget.id">
            <div class="relative h-full w-full p-3 flex flex-col justify-between animate-fade-in">
                <DashboardWidget
                    :title="widget.title"
                    :value="sensors[widget.sensor] !== undefined ? sensors[widget.sensor] : '...'"
                    :unit="widget.unit"
                    :trend="getTrend(widget.sensor)"
                    :status="getStatus(widget.sensor)"
                />
                 <div v-if="editMode" class="absolute top-2 right-2 cursor-pointer text-gray-400 hover:text-red-400 z-10 transition-colors p-1 rounded hover:bg-red-500/20 bg-gray-800 shadow-sm" @click="removeWidget(widget.id)">
                    <i class="pi pi-times text-sm"></i>
                </div>
            </div>
        </Teleport>

        <Dialog v-model:visible="showAddWidget" header="Widget hinzufügen" :modal="true" :style="{ width: '90vw', maxWidth: '400px' }">
            <div class="flex flex-col gap-4">
                <label class="text-sm font-medium">Sensor wählen</label>
                <Dropdown v-model="selectedSensor" :options="sensorOptions" optionLabel="name" placeholder="Wähle einen Sensor" filter class="w-full" />
                <Button label="Hinzufügen" @click="confirmAddWidget" :disabled="!selectedSensor" class="w-full" />
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { GridStack } from 'gridstack';
import 'gridstack/dist/gridstack.min.css';
import axios from 'axios';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import DashboardWidget from '../components/DashboardWidget.vue';
import SkeletonGroup from '../components/SkeletonGroup.vue';
import { debounce } from '../utils/performance.js';
import { useUiStore } from '../stores/ui';
import { storeToRefs } from 'pinia';

const grid = ref(null);
const sensors = ref({});
const widgets = ref([]);
const showAddWidget = ref(false);
const selectedSensor = ref(null);
const sensorOptions = ref([]);
const timer = ref(null);
const ui = useUiStore();
const { editMode } = storeToRefs(ui);

onMounted(async () => {
        try {
        const res = await axios.get('/api/data');
        sensors.value = res.data;
        sensorOptions.value = Object.keys(res.data).map(k => ({ name: k, value: k }));
        } catch {
            // ignore
        }

    ui.init();

    grid.value = GridStack.init({
        float: true,
        cellHeight: 80,
        minRow: 1,
        margin: 3,
        column: 6,
        disableOneColumnMode: false,
        oneColumnModeDomSort: true,
        oneColumnModeWidth: 640,
        breakpointForNColumn: {
            1: { width: 640, column: 1 },
            2: { width: 768, column: 2 },
            3: { width: 1024, column: 3 },
            4: { width: 1280, column: 4 },
            6: { width: 1536, column: 6 }
        }
    });
    applyEditMode();
    watch(editMode, () => {
        applyEditMode();
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

    grid.value.on('change', () => {
        saveLayout();
    });

        grid.value.on('dragstop', () => {
            saveLayout();
    });

    grid.value.on('resizestop', () => {
            saveLayout();
    });

    // Use debounced data fetching to improve performance
    const debouncedFetchData = debounce(fetchData, 500);
    timer.value = setInterval(debouncedFetchData, 2000);
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

const applyEditMode = () => {
    if (!grid.value) return;
    grid.value.setStatic(!editMode.value);
    grid.value.enableMove(editMode.value);
    grid.value.enableResize(editMode.value);
};

const debouncedSaveLayout = debounce(() => {
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
}, 300);

const saveLayout = () => {
    debouncedSaveLayout();
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

const previousValues = ref({});
const getTrend = (sensor) => {
    if (!previousValues.value[sensor] || !sensors.value[sensor]) return 'neutral';
    
    const current = parseFloat(sensors.value[sensor]);
    const previous = parseFloat(previousValues.value[sensor]);
    
    if (isNaN(current) || isNaN(previous)) return 'neutral';
    
    if (current > previous) return 'up';
    if (current < previous) return 'down';
    return 'neutral';
};

const getStatus = (sensor) => {
    if (!sensors.value[sensor]) return 'normal';
    
    const value = parseFloat(sensors.value[sensor]);
    if (isNaN(value)) return 'normal';
    
    // Example status logic based on sensor type
    if (sensor.includes('temp')) {
        if (value > 80) return 'error';
        if (value > 60) return 'warning';
        return 'normal';
    }
    
    if (sensor.includes('power')) {
        if (value > 5) return 'warning';
        return 'normal';
    }
    
    return 'normal';
};

// Update previous values for trend calculation
const fetchData = async () => {
    try {
        const res = await axios.get('/api/data');
        
        // Store previous values before updating
        Object.keys(res.data).forEach(key => {
            if (sensors.value[key] !== undefined) {
                previousValues.value[key] = sensors.value[key];
            }
        });
        
        sensors.value = res.data;

        if (sensorOptions.value.length === 0) {
                sensorOptions.value = Object.keys(res.data).map(k => ({ name: k, value: k }));
        }
    } catch {
        // ignore
    }
};
</script>

<style>
.grid-stack-item-content {
    background-color: #1f2937; /* gray-800 */
    background-image: linear-gradient(to bottom right, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0));
    color: white;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(75, 85, 99, 0.4); /* gray-600 with opacity */
}

.grid-stack-item:hover .grid-stack-item-content {
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    border-color: #3b82f6; /* blue-500 */
    transform: translateY(-4px);
    z-index: 10 !important;
}

.grid-stack-item.ui-draggable-dragging .grid-stack-item-content {
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
    transform: scale(1.02);
    border-color: #60a5fa;
}

.grid-stack-item.ui-resizable-resizing .grid-stack-item-content {
    border-color: #34d399;
}

/* GridStack handle styling */
.grid-stack-item .ui-resizable-se {
    background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><circle cx="10" cy="10" r="1.5" fill="%2360a5fa" opacity="0.5"/><circle cx="6" cy="10" r="1.5" fill="%2360a5fa" opacity="0.5"/><circle cx="10" cy="6" r="1.5" fill="%2360a5fa" opacity="0.5"/></svg>') no-repeat;
    width: 12px;
    height: 12px;
    right: 3px;
    bottom: 3px;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.grid-stack-item:hover .ui-resizable-se {
    opacity: 1;
}
</style>
