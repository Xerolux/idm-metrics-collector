import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('../views/Setup.vue')
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: '/control',
        name: 'Control',
        component: () => import('../views/Control.vue')
      },
      {
        path: '/schedule',
        name: 'Schedule',
        component: () => import('../views/Schedule.vue')
      },
      {
        path: '/alerts',
        name: 'Alerts',
        component: () => import('../views/Alerts.vue')
      },
      {
        path: '/config',
        name: 'Config',
        component: () => import('../views/Config.vue')
      },
      {
        path: '/logs',
        name: 'Logs',
        component: () => import('../views/Logs.vue')
      },
      {
        path: '/tools',
        name: 'Tools',
        component: () => import('../views/Tools.vue')
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('../views/About.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth) {
     const valid = await auth.checkAuth()
     if (!valid) {
         next('/login')
         return
     }
  }
  next()
})

export default router
