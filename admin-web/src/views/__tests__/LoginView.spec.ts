import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '../../stores/auth'
import { createManagementRouter } from '../../router'
import LoginView from '../LoginView.vue'

describe('LoginView', () => {
  it('submits credentials and returns to the requested route', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createManagementRouter(createMemoryHistory())
    await router.push('/login?redirect=/dashboard')
    const store = useAuthStore()
    const login = vi.spyOn(store, 'login').mockImplementation(async () => {
      store.$patch({
        user: {
          id: 'demo-1',
          username: 'demo_admin',
          nickname: '演示管理员',
          is_superuser: true,
          is_demo: true,
          permissions: [],
        },
      })
    })
    const wrapper = mount(LoginView, { global: { plugins: [pinia, router] } })

    await wrapper.get('[data-test="login-username"]').setValue('demo_admin')
    await wrapper.get('[data-test="login-password"]').setValue('valid-password')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(login).toHaveBeenCalledWith('demo_admin', 'valid-password')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })
})
