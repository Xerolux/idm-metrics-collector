<script setup>
import { ref } from "vue";
import { useRouter } from 'vue-router'
import { useAuthStore } from "../stores/auth";
import Menubar from 'primevue/menubar';
import Button from 'primevue/button';
import AppFooter from './AppFooter.vue';

const router = useRouter();
const auth = useAuthStore();

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
        label: 'Control',
        icon: 'pi pi-sliders-h',
        command: () => router.push('/control')
    },
    {
        label: 'Schedule',
        icon: 'pi pi-calendar',
        command: () => router.push('/schedule')
    },
    {
        label: 'Logs',
        icon: 'pi pi-list',
        command: () => router.push('/logs')
    },
    {
        label: 'Settings',
        icon: 'pi pi-cog',
        command: () => router.push('/config')
    },
    {
        label: 'About',
        icon: 'pi pi-info-circle',
        command: () => router.push('/about')
    }
]);

const logout = async () => {
    await auth.logout();
    router.push('/login');
}
</script>

<template>
    <div class="flex flex-col min-h-screen">
        <Menubar :model="items" class="rounded-none border-0 border-b border-gray-700 bg-gray-800">
             <template #start>
               <span class="text-xl font-bold px-4">IDM Logger</span>
            </template>
            <template #item="{ item, props }">
                <a v-ripple class="flex items-center gap-2 px-3 py-2 hover:bg-gray-700 rounded cursor-pointer" v-bind="props.action">
                    <i :class="item.icon"></i>
                    <span>{{ item.label }}</span>
                </a>
            </template>
            <template #end>
                <div class="flex items-center gap-2">
                    <Button icon="pi pi-power-off" severity="danger" text @click="logout">
                        <span class="hidden sm:inline ml-2">Logout</span>
                    </Button>
                </div>
            </template>
        </Menubar>
        <main class="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
             <router-view></router-view>
        </main>
        <AppFooter />
    </div>
</template>
