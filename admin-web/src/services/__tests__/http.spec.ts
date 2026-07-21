import { afterEach, describe, expect, it, vi } from 'vitest'

import { apiGet, apiPost } from '../http'
import { tokenStorage } from '../tokenStorage'

function jsonResponse(status: number, payload: unknown) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  }
}

describe('management HTTP client', () => {
  afterEach(() => {
    tokenStorage.clear()
    vi.restoreAllMocks()
  })

  it('unwraps data, pagination metadata and request id', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(200, {
          data: { items: [{ id: 'scene-1' }] },
          meta: { page: 1, page_size: 20, total: 1 },
          request_id: 'req-list',
        }),
      ),
    )

    await expect(apiGet<{ items: Array<{ id: string }> }>('/api/v1/management/scenes')).resolves.toEqual({
      data: { items: [{ id: 'scene-1' }] },
      meta: { page: 1, page_size: 20, total: 1 },
      requestId: 'req-list',
    })
  })

  it('normalizes backend failures with details and request id', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(403, {
          error: {
            code: 'PERMISSION_DENIED',
            message: '没有权限执行此操作',
            details: { status: '不能修改' },
          },
          request_id: 'req-403',
        }),
      ),
    )

    await expect(apiGet('/api/v1/management/scenes')).rejects.toEqual(
      expect.objectContaining({
        code: 'PERMISSION_DENIED',
        message: '没有权限执行此操作',
        status: 403,
        details: { status: '不能修改' },
        requestId: 'req-403',
      }),
    )
  })

  it('shares one refresh request across simultaneous expired reads', async () => {
    tokenStorage.save('expired-access', 'valid-refresh')
    const fetchMock = vi.fn().mockImplementation(async (input: string, init?: RequestInit) => {
      if (input.endsWith('/api/v1/auth/refresh')) {
        return jsonResponse(200, {
          data: { access: 'renewed-access' },
          request_id: 'req-refresh',
        })
      }
      const authorization = new Headers(init?.headers).get('Authorization')
      if (authorization === 'Bearer expired-access') {
        return jsonResponse(401, {
          error: { code: 'AUTH_REQUIRED', message: '请先登录', details: {} },
          request_id: 'req-expired',
        })
      }
      return jsonResponse(200, {
        data: { ok: true },
        request_id: 'req-ok',
      })
    })
    vi.stubGlobal('fetch', fetchMock)

    const [first, second] = await Promise.all([
      apiGet<{ ok: boolean }>('/api/v1/management/dashboard/summary'),
      apiGet<{ ok: boolean }>('/api/v1/management/dashboard/device-status'),
    ])

    expect(first.data.ok).toBe(true)
    expect(second.data.ok).toBe(true)
    expect(
      fetchMock.mock.calls.filter(([input]) => String(input).endsWith('/api/v1/auth/refresh')),
    ).toHaveLength(1)
    expect(tokenStorage.get().access).toBe('renewed-access')
  })

  it('does not automatically retry a protected write', async () => {
    tokenStorage.save('expired-access', 'valid-refresh')
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(401, {
        error: { code: 'AUTH_REQUIRED', message: '请先登录', details: {} },
        request_id: 'req-risk',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(
      apiPost(
        '/api/v1/management/devices/device-1/rotate-secret',
        { confirm: true, reason: '例行轮换' },
        false,
      ),
    ).rejects.toEqual(expect.objectContaining({ code: 'AUTH_REQUIRED' }))
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
