<script setup>
import { ref } from "vue";
import { useRouter } from 'vue-router'
import { useAuthStore } from "../stores/auth";
import Menubar from 'primevue/menubar';
import Button from 'primevue/button';

const router = useRouter();
const auth = useAuthStore();

const items = ref([
    {
        label: 'Dashboard',
        icon: 'pi pi-home',
        command: () => {
            router.push('/');
        }
    },
    {
        label: 'Control',
        icon: 'pi pi-sliders-h',
        command: () => {
            router.push('/control');
        }
    },
    {
        label: 'Schedule',
        icon: 'pi pi-calendar',
        command: () => {
            router.push('/schedule');
        }
    },
    {
        label: 'Logs',
        icon: 'pi pi-list',
        command: () => {
            router.push('/logs');
        }
    },
    {
        label: 'Settings',
        icon: 'pi pi-cog',
        command: () => {
            router.push('/config');
        }
    }
]);

const logout = async () => {
    await auth.logout();
    router.push('/login');
}
</script>

<template>
    <div class="card">
        <Menubar :model="items" class="rounded-none border-0 border-b border-gray-700 bg-gray-800">
             <template #start>
               <span class="text-xl font-bold px-4">IDM Logger</span>
            </template>
            <template #end>
                <div class="flex items-center gap-2">
                    <Button label="Logout" icon="pi pi-power-off" severity="danger" text @click="logout" />
                </div>
            </template>
        </Menubar>
        <main class="p-4">
             <router-view></router-view>
        </main>
    </div>
</template>
