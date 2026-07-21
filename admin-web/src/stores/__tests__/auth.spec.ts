import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import * as authApi from '../../services/auth'
import { tokenStorage } from '../../services/tokenStorage'
import type { ManagementUser } from '../../types/auth'
import { useAuthStore } from '../auth'

const operator: ManagementUser = {
  id: 'operator-1',
  username: 'operator',
  nickname: '内容运营',
  is_superuser: false,
  is_demo: false,
  permissions: ['scenes.view_spot'],
}

describe('auth store', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('stores tokens and the management user after login', async () => {
    vi.spyOn(authApi, 'login').mockResolvedValue({
      data: { access: 'access', refresh: 'refresh', user: operator },
      requestId: 'req-login',
    })
    const store = useAuthStore()

    await store.login('operator', 'valid-password')

    expect(store.user).toEqual(operator)
    expect(store.isAuthenticated).toBe(true)
    expect(tokenStorage.get()).toEqual({ access: 'access', refresh: 'refresh' })
    expect(store.can('scenes.view_spot')).toBe(true)
    expect(store.can('iot.view_device')).toBe(false)
  })

  it('restores a saved session and clears an invalid one', async () => {
    tokenStorage.save('access', 'refresh')
    vi.spyOn(authApi, 'getManagementMe')
      .mockResolvedValueOnce({ data: operator, requestId: 'req-me' })
      .mockRejectedValueOnce(new Error('expired'))

    const validStore = useAuthStore()
    await validStore.restore()
    expect(validStore.user).toEqual(operator)

    setActivePinia(createPinia())
    const invalidStore = useAuthStore()
    await invalidStore.restore()
    expect(invalidStore.user).toBeNull()
    expect(tokenStorage.get()).toEqual({ access: null, refresh: null })
  })

  it('allows a superuser and clears all session state on logout', () => {
    const store = useAuthStore()
    store.$patch({ user: { ...operator, is_superuser: true } })
    tokenStorage.save('access', 'refresh')

    expect(store.can('iot.change_device')).toBe(true)
    store.logout()

    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(tokenStorage.get()).toEqual({ access: null, refresh: null })
  })
})
