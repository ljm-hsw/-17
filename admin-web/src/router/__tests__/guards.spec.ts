import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { beforeEach, describe, expect, it } from 'vitest'

import type { ManagementUser } from '../../types/auth'
import { useAuthStore } from '../../stores/auth'
import { createManagementRouter } from '../index'

const reader: ManagementUser = {
  id: 'reader-1',
  username: 'reader',
  nickname: '只读人员',
  is_superuser: false,
  is_demo: false,
  permissions: [],
}

describe('management router guards', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
  })

  it('redirects an anonymous protected route to login with its destination', async () => {
    const router = createManagementRouter(createMemoryHistory())

    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/dashboard')
  })

  it('redirects an authenticated user without route permission to 403', async () => {
    const store = useAuthStore()
    store.$patch({ user: reader })
    const router = createManagementRouter(createMemoryHistory())
    router.addRoute({
      path: '/devices',
      name: 'devices-test',
      component: { template: '<div>devices</div>' },
      meta: { requiresAuth: true, permission: 'iot.view_device' },
    })

    await router.push('/devices')

    expect(router.currentRoute.value.name).toBe('forbidden')
  })
})
