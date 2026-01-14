<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter } from 'vue-router'
import { useAuthStore } from "../stores/auth";
import { useUiStore } from "../stores/ui";
import Menubar from 'primevue/menubar';
import Button from 'primevue/button';
import AppFooter from './AppFooter.vue';
import NetworkStatus from './NetworkStatus.vue';

const router = useRouter();
const auth = useAuthStore();
const ui = useUiStore();

const editModeLabel = computed(() => (ui.editMode ? 'Bearbeiten: An' : 'Bearbeiten: Aus'));
const editModeIcon = computed(() => (ui.editMode ? 'pi pi-lock-open' : 'pi pi-lock'));
const editModeSeverity = computed(() => (ui.editMode ? 'success' : 'secondary'));

const navigate = (path) => {
    router.push(path);
};

const items = ref([
    {
        label: 'Dashboard',
        icon: 'pi pi-home',
        command: () => router.push('/')
    },
    {
        label: 'Steuerung',
        icon: 'pi pi-sliders-h',
        command: () => router.push('/control')
    },
    {
        label: 'Zeitplan',
        icon: 'pi pi-calendar',
        command: () => router.push('/schedule')
    },
    {
        label: 'Alarme',
        icon: 'pi pi-bell',
        command: () => router.push('/alerts')
    },
    {
        label: 'Protokolle',
        icon: 'pi pi-list',
        command: () => router.push('/logs')
    },
    {
        label: 'Einstellungen',
        icon: 'pi pi-cog',
        command: () => router.push('/config')
    },
    {
        label: 'Techniker',
        icon: 'pi pi-key',
        command: () => router.push('/tools')
    },
    {
        label: 'Grafana',
        icon: 'pi pi-chart-line',
        command: () => {
            const hostname = window.location.hostname;
            window.open(`http://${hostname}:3001`, '_blank', 'noopener');
        }
    },
    {
        label: 'Über',
        icon: 'pi pi-info-circle',
        command: () => router.push('/about')
    }
]);

const logout = async () => {
    await auth.logout();
    router.push('/login');
}

let timer;
const resetTimer = () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
        logout();
    }, 300000); // 5 minutes
};

onMounted(() => {
    ui.init();
    const events = ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => window.addEventListener(event, resetTimer));
    resetTimer();
});

onUnmounted(() => {
    const events = ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => window.removeEventListener(event, resetTimer));
    clearTimeout(timer);
});
</script>

<template>
    <div class="flex flex-col min-h-screen">
        <NetworkStatus />
        <Menubar :model="items" class="rounded-none border-0 border-b border-gray-700 bg-gray-800">
             <template #start>
               <span class="text-lg sm:text-xl font-bold px-2 sm:px-4">IDM Logger</span>
            </template>
            <template #item="{ item, props }">
                <a v-ripple class="flex items-center gap-2 px-2 sm:px-3 py-2 hover:bg-gray-700 rounded cursor-pointer transition-colors" v-bind="props.action">
                    <i :class="item.icon" class="text-sm sm:text-base"></i>
                    <span class="hidden sm:inline text-sm sm:text-base">{{ item.label }}</span>
                </a>
            </template>
            <template #end>
                <div class="flex items-center gap-2">
                    <Button
                        :label="editModeLabel"
                        :icon="editModeIcon"
                        :severity="editModeSeverity"
                        text
                        class="p-2 sm:p-3"
                        @click="ui.toggleEditMode"
                    />
                    <Button icon="pi pi-power-off" severity="danger" text @click="logout" class="p-2 sm:p-3">
                        <span class="hidden sm:inline ml-2">Abmelden</span>
                    </Button>
                </div>
            </template>
        </Menubar>
        <main class="flex-grow container mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-3 sm:py-4 md:py-6 lg:py-8">
             <router-view></router-view>
        </main>
        <AppFooter />
    </div>
</template>
