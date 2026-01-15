<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useRouter } from 'vue-router'
import { useAuthStore } from "../stores/auth";
import { useUiStore } from "../stores/ui";
import { useI18n } from 'vue-i18n';
import Menubar from 'primevue/menubar';
import Button from 'primevue/button';
import Select from 'primevue/select';
import AppFooter from './AppFooter.vue';
import NetworkStatus from './NetworkStatus.vue';

const router = useRouter();
const auth = useAuthStore();
const ui = useUiStore();
const { t, locale } = useI18n();

const editModeLabel = computed(() => (ui.editMode ? t('edit') + ': On' : t('edit') + ': Off'));
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

const isDark = ref(document.documentElement.classList.contains('my-app-dark'));
const toggleTheme = () => {
    document.documentElement.classList.toggle('my-app-dark');
    isDark.value = !isDark.value;
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
    {
        label: t('tools'),
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
        label: t('about'),
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
    <div class="flex flex-col min-h-screen transition-colors duration-200" :class="isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'">
        <NetworkStatus />
        <Menubar :model="items" class="rounded-none border-0 border-b !border-gray-700 !bg-gray-800">
             <template #start>
               <span class="text-lg sm:text-xl font-bold px-2 sm:px-4 text-white">IDM Logger</span>
            </template>
            <template #item="{ item, props }">
                <a v-ripple class="flex items-center gap-2 px-2 sm:px-3 py-2 hover:bg-gray-700 rounded cursor-pointer transition-colors text-gray-200" v-bind="props.action">
                    <i :class="item.icon" class="text-sm sm:text-base"></i>
                    <span class="hidden xl:inline text-sm sm:text-base">{{ item.label }}</span>
                </a>
            </template>
            <template #end>
                <div class="flex items-center gap-2">
                     <Select v-model="currentLang" :options="languages" optionLabel="label" optionValue="value" class="w-24 !text-sm" size="small" />

                    <Button :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'" text rounded severity="secondary" @click="toggleTheme" />

                    <Button
                        :label="ui.editMode ? '' : ''"
                        :icon="editModeIcon"
                        :severity="editModeSeverity"
                        text
                        class="p-2 sm:p-3"
                        @click="ui.toggleEditMode"
                    />
                    <Button icon="pi pi-power-off" severity="danger" text @click="logout" class="p-2 sm:p-3">
                        <span class="hidden sm:inline ml-2">{{ t('logout') }}</span>
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
