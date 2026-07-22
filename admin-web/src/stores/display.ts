import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useDisplayStore = defineStore('display', () => {
  const isDemoMode = ref(false)

  async function enterDemoMode() {
    isDemoMode.value = true
    try {
      await document.documentElement.requestFullscreen?.()
    } catch {
      // Browsers may deny fullscreen without a direct user gesture; the read-only layout still applies.
    }
  }

  async function exitDemoMode() {
    isDemoMode.value = false
    try {
      await document.exitFullscreen?.()
    } catch {
      // Exiting the read-only layout must not depend on the fullscreen browser API.
    }
  }

  async function toggleDemoMode() {
    if (isDemoMode.value) await exitDemoMode()
    else await enterDemoMode()
  }

  return { isDemoMode, enterDemoMode, exitDemoMode, toggleDemoMode }
})
