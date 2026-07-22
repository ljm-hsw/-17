import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useDisplayStore } from '../display'

describe('display store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('enters and exits the read-only competition display mode', async () => {
    const requestFullscreen = vi.fn().mockResolvedValue(undefined)
    const exitFullscreen = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(document.documentElement, 'requestFullscreen', {
      configurable: true,
      value: requestFullscreen,
    })
    Object.defineProperty(document, 'exitFullscreen', {
      configurable: true,
      value: exitFullscreen,
    })

    const store = useDisplayStore()
    await store.enterDemoMode()
    expect(store.isDemoMode).toBe(true)
    expect(requestFullscreen).toHaveBeenCalledOnce()

    await store.exitDemoMode()
    expect(store.isDemoMode).toBe(false)
    expect(exitFullscreen).toHaveBeenCalledOnce()
  })
})
