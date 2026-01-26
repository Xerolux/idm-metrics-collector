<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useRouter } from 'vue-router'
import { useAuthStore } from "../stores/auth";
import { useUiStore } from "../stores/ui";
import { useI18n } from 'vue-i18n';
import axios from 'axios';
import Menubar from 'primevue/menubar';
import Button from 'primevue/button';
import Select from 'primevue/select';
import AppFooter from './AppFooter.vue';
import NetworkStatus from './NetworkStatus.vue';

const router = useRouter();
const auth = useAuthStore();
const ui = useUiStore();
const { t, locale } = useI18n();

// Update notification state
const updateAvailable = ref(false);
const updateInfo = ref(null);
const showUpdateBanner = ref(true);

// Migration/Telemetry Warning
const showMigrationWarning = ref(false);

const editModeIcon = computed(() => (ui.editMode ? 'pi pi-lock-open' : 'pi pi-lock'));
const editModeSeverity = computed(() => (ui.editMode ? 'success' : 'secondary'));

const languages = ref([
    { label: 'Deutsch', value: 'de' },
    { label: 'English', value: 'en' }
]);
const currentLang = ref('de');

watch(currentLang, (newLang) => {
    locale.value = newLang;
});

const isDark = computed(() => ui.darkMode);

const toggleTheme = () => {
    ui.toggleDarkMode();
};

const items = computed(() => [
    {
        label: t('dashboard'),
        icon: 'pi pi-home',
        command: () => router.push('/')
    },
    {
        label: t('control'),
        icon: 'pi pi-sliders-h',
        command: () => router.push('/control')
    },
    {
        label: t('schedule'),
        icon: 'pi pi-calendar',
        command: () => router.push('/schedule')
    },
    {
        label: t('alerts'),
        icon: 'pi pi-bell',
        command: () => router.push('/alerts')
    },
    {
        label: t('logs'),
        icon: 'pi pi-list',
        command: () => router.push('/logs')
    },
    {
        label: t('config'),
        icon: 'pi pi-cog',
        command: () => router.push('/config')
    },
    // Uncomment to enable Grafana link in navigation
    // {
    //     label: 'Grafana',
    //     icon: 'pi pi-chart-line',
    //     command: () => {
    //         const hostname = window.location.hostname;
    //         window.open(`http://${hostname}:3001`, '_blank', 'noopener');
    //     }
    // },
    {
        label: t('codegen'),
        icon: 'pi pi-lock',
        command: () => router.push('/tools')
    },
    {
        label: t('about'),
        icon: 'pi pi-info-circle',
        command: () => router.push('/about')
    },
    {
        label: ui.editMode ? 'Bearbeiten beenden' : 'Bearbeiten',
        icon: ui.editMode ? 'pi pi-lock-open' : 'pi pi-lock',
        command: () => ui.toggleEditMode()
    }
]);

const logout = async () => {
    await auth.logout();
    router.push('/login');
}

// Check for updates and config state
const checkSystemState = async () => {
    try {
        // Check updates
        const updateRes = await axios.get('/api/check-update');
        if (updateRes.data.update_available) {
            updateAvailable.value = true;
            updateInfo.value = updateRes.data;
        }

        // Check Config for Migration (Telemetry active but no model selected)
        const configRes = await axios.get('/api/config');
        if (configRes.data.share_data && !configRes.data.heatpump_model) {
            showMigrationWarning.value = true;
        }

    } catch (e) {
        console.error('System state check failed:', e);
    }
};

const goToUpdate = () => {
    router.push('/config');
    // Scroll to update section after navigation
    setTimeout(() => {
        const updateSection = document.querySelector('[data-update-section]');
        if (updateSection) {
            updateSection.scrollIntoView({ behavior: 'smooth' });
        }
    }, 100);
};

const dismissUpdateBanner = () => {
    showUpdateBanner.value = false;
};

let timer;
const resetTimer = () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
        logout();
    }, 300000); // 5 minutes
};

onMounted(() => {
    ui.init();
    // Apply dark mode on mount
    if (ui.darkMode) {
        document.documentElement.classList.add('my-app-dark');
    }
    const events = ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => window.addEventListener(event, resetTimer));
    resetTimer();

    // Check for updates on app load
    checkSystemState();
});

onUnmounted(() => {
    const events = ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => window.removeEventListener(event, resetTimer));
    clearTimeout(timer);
});
</script>

<template>
    <div class="flex flex-col min-h-screen transition-colors duration-200" :class="isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'">
        <NetworkStatus />

        <!-- Update Available Banner -->
        <div v-if="updateAvailable && showUpdateBanner"
             class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 flex items-center justify-between cursor-pointer hover:from-blue-500 hover:to-blue-600 transition-all"
             @click="goToUpdate">
            <div class="flex items-center gap-3">
                <i class="pi pi-sync text-lg"></i>
                <span class="font-medium">
                    Update verfügbar!
                    <span v-if="updateInfo?.docker?.updates_available" class="hidden sm:inline">
                        - Neue Docker Images
                    </span>
                    <span v-if="updateInfo?.latest_version" class="hidden md:inline">
                        ({{ updateInfo.latest_version }})
                    </span>
                </span>
                <span class="text-blue-200 text-sm hidden lg:inline">
                    <i class="pi pi-clock mr-1"></i>Auto-Update täglich 03:00
                </span>
            </div>
            <button @click.stop="dismissUpdateBanner" class="p-1 hover:bg-blue-500 rounded transition-colors" title="Ausblenden">
                <i class="pi pi-times"></i>
            </button>
        </div>

        <!-- Migration Warning Banner -->
        <div v-if="showMigrationWarning"
             class="bg-gradient-to-r from-orange-600 to-orange-700 text-white px-4 py-2 flex items-center justify-between cursor-pointer hover:from-orange-500 hover:to-orange-600 transition-all"
             @click="router.push('/config')">
            <div class="flex items-center gap-3">
                <i class="pi pi-exclamation-triangle text-lg"></i>
                <span class="font-medium">
                    Bitte Wärmepumpen-Modell konfigurieren!
                </span>
                <span class="text-orange-200 text-sm hidden sm:inline">
                    Notwendig für KI-Verbesserungen.
                </span>
            </div>
            <div class="flex items-center gap-2">
                <span class="text-sm font-bold underline">Einstellungen</span>
                <i class="pi pi-arrow-right"></i>
            </div>
        </div>

        <Menubar :model="items" breakpoint="1280px" class="rounded-none border-0 border-b !border-gray-700 !bg-gray-800">
             <template #start>
               <span class="text-lg sm:text-xl font-bold px-2 sm:px-4 text-white">IDM Metrics Collector</span>
            </template>
            <template #item="{ item, props }">
                <a v-ripple class="flex items-center gap-2 px-2 sm:px-3 py-2 hover:bg-gray-700 rounded cursor-pointer transition-colors text-gray-200" v-bind="props.action">
                    <i :class="item.icon" class="text-sm sm:text-base"></i>
                    <span class="text-sm sm:text-base">{{ item.label }}</span>
                </a>
            </template>
            <template #end>
                <div class="flex items-center gap-1 sm:gap-2 mr-2 sm:mr-4">
                     <Select v-model="currentLang" :options="languages" optionLabel="label" optionValue="value" class="w-20 sm:w-24 !text-sm" size="small" />

                    <Button :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'" text rounded severity="secondary" @click="toggleTheme" class="w-8 h-8 sm:w-auto sm:h-auto" />

                    <Button
                        :label="ui.editMode ? '' : ''"
                        :icon="editModeIcon"
                        :severity="editModeSeverity"
                        text
                        class="p-1 sm:p-2"
                        @click="ui.toggleEditMode"
                    />
<Button icon="pi pi-power-off" severity="danger" text @click="logout" class="p-1 sm:p-2" />
                </div>
            </template>
        </Menubar>
        <main class="flex-grow container mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-3 sm:py-4 md:py-6 lg:py-8">
             <router-view></router-view>
        </main>
        <AppFooter />
    </div>
</template>
