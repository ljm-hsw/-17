import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { getManagementMe, login as loginRequest } from '../services/auth'
import { tokenStorage } from '../services/tokenStorage'
import type { ManagementUser } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<ManagementUser | null>(null)
  const restored = ref(false)
  const isAuthenticated = computed(() => user.value !== null)

  async function login(username: string, password: string) {
    const response = await loginRequest(username, password)
    tokenStorage.save(response.data.access, response.data.refresh)
    user.value = response.data.user
    restored.value = true
  }

  async function restore() {
    if (restored.value) return
    restored.value = true
    if (!tokenStorage.get().access) return
    try {
      const response = await getManagementMe()
      user.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    restored.value = true
    tokenStorage.clear()
  }

  function can(permission?: string) {
    if (!permission) return true
    if (user.value?.is_superuser) return true
    return user.value?.permissions.includes(permission) ?? false
  }

  return {
    user,
    isAuthenticated,
    login,
    restore,
    logout,
    can,
  }
})
