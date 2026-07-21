import { afterEach, describe, expect, it, vi } from 'vitest'

import { getBackendHealth } from '../api'

describe('getBackendHealth', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('unwraps the stable API envelope', async () => {
    vi.stubGlobal('uni', {
      request: vi.fn().mockResolvedValue({
        statusCode: 200,
        data: { data: { status: 'ok' } },
      }),
    })

    await expect(getBackendHealth()).resolves.toBe('ok')
  })
})
