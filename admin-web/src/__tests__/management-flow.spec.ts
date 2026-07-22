import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import * as http from '../services/http'
import { confirmCardImport } from '../services/management/cards'
import { rotateDeviceSecret } from '../services/management/devices'
import { forceUnbind } from '../services/management/users'
import { createManagementRouter } from '../router'
import { useAuthStore } from '../stores/auth'

describe('management demo integration', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
    useAuthStore().$patch({ user: { id: 'admin', username: 'demo_admin', nickname: '演示管理员', is_superuser: true, is_demo: true, permissions: [] } })
    vi.restoreAllMocks()
  })

  it('registers every management area behind the authenticated shell', () => {
    const router = createManagementRouter(createMemoryHistory())
    const routes = Object.fromEntries(router.getRoutes().map((route) => [String(route.name), route.meta.permission]))
    expect(routes).toMatchObject({
      dashboard: undefined,
      scenes: 'scenes.view_scene', spots: 'scenes.view_spot', routes: 'scenes.view_route',
      devices: 'iot.view_device', cards: 'accounts.view_card', users: 'accounts.view_cardbinding',
      visits: 'visits.view_visitsession', checkins: 'visits.view_checkinevent', 'audit-logs': undefined,
    })
  })

  it('keeps every high-risk write explicit and non-retryable', async () => {
    const post = vi.spyOn(http, 'apiPost').mockResolvedValue({ data: {} as never, requestId: 'req-risk' })
    await rotateDeviceSecret('device-1', { confirm: true, reason: '设备疑似泄露' })
    await forceUnbind('binding-1', { confirm: true, reason: '用户确认卡片遗失' })
    await confirmCardImport([{ serial_no: 'SCU-JA-0001', card_uid: 'AABBCCDD' }])

    expect(post.mock.calls).toEqual(expect.arrayContaining([
      ['/api/v1/management/devices/device-1/rotate-secret', { confirm: true, reason: '设备疑似泄露' }, false],
      ['/api/v1/management/bindings/binding-1/force-unbind', { confirm: true, reason: '用户确认卡片遗失' }, false],
      ['/api/v1/management/cards/import-confirm', { rows: [{ serial_no: 'SCU-JA-0001', card_uid: 'AABBCCDD' }], confirm: true }, false],
    ]))
  })
})
