import {
  createRouter,
  createWebHistory,
  type RouterHistory,
  type RouteRecordRaw,
} from 'vue-router'

import { useAuthStore } from '../stores/auth'
import DashboardView from '../views/DashboardView.vue'
import ForbiddenView from '../views/ForbiddenView.vue'
import LoginView from '../views/LoginView.vue'
import NotFoundView from '../views/NotFoundView.vue'

export const routes: RouteRecordRaw[] = [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    { path: '/403', name: 'forbidden', component: ForbiddenView },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

export function createManagementRouter(history: RouterHistory = createWebHistory()) {
  const managementRouter = createRouter({ history, routes })

  managementRouter.beforeEach(async (to) => {
    const auth = useAuthStore()
    await auth.restore()

    if (to.name === 'login' && auth.isAuthenticated) {
      return { name: 'dashboard' }
    }
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    const permission = typeof to.meta.permission === 'string' ? to.meta.permission : undefined
    if (permission && !auth.can(permission)) {
      return { name: 'forbidden' }
    }
    return true
  })

  return managementRouter
}

export const router = createManagementRouter()
