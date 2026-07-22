import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as dashboardApi from '../../services/management/dashboard'
import { useSceneStore } from '../../stores/scene'
import DashboardView from '../DashboardView.vue'

const apiResult = <T,>(data: T) => ({ data, requestId: 'req-dashboard' })

function mockSuccessfulDashboard() {
  vi.spyOn(dashboardApi, 'getDashboardSummary').mockResolvedValue(
    apiResult({
      generated_at: '2026-07-22T10:00:00+08:00',
      scene_id: 'jiang-an',
      date_from: '2026-07-16',
      date_to: '2026-07-22',
      today_visitors: 128,
      accepted_checkins: 356,
      bound_cards: 204,
      online_devices: 7,
    }),
  )
  vi.spyOn(dashboardApi, 'getCheckinTrend').mockResolvedValue(
    apiResult({ items: [{ date: '2026-07-22', count: 56 }] }),
  )
  vi.spyOn(dashboardApi, 'getSpotRanking').mockResolvedValue(
    apiResult({ items: [{ spot_id: 'spot-1', name: '江安图书馆', event_count: 92 }] }),
  )
  vi.spyOn(dashboardApi, 'getLatestEvents').mockResolvedValue({
    data: {
      items: [
        {
          id: 'event-1',
          event_id: 'device-event-1',
          device_id: 'device-1',
          spot_id: 'spot-1',
          user_id: 'user-1',
          card_id: 'card-1',
          visit_id: 'visit-1',
          checkin_type: 'rfid',
          status: 'accepted',
          failure_code: '',
          received_at: '2026-07-22T09:58:00+08:00',
        },
      ],
    },
    meta: { page: 1, page_size: 6, total: 1 },
    requestId: 'req-events',
  })
  vi.spyOn(dashboardApi, 'getDeviceStatus').mockResolvedValue(
    apiResult({
      items: [
        {
          id: 'device-1',
          device_id: 'SCU-JA-001',
          scene_id: 'jiang-an',
          spot_id: 'spot-1',
          device_type: 'rfid',
          secret_fingerprint: 'abcd1234',
          status: 'active',
          firmware_version: '1.0.0',
          last_seen_at: '2026-07-22T09:59:30+08:00',
          last_error_code: '',
        },
      ],
    }),
  )
}

function mountDashboard() {
  const sceneStore = useSceneStore()
  sceneStore.$patch({
    scenes: [
      {
        id: 'jiang-an',
        slug: 'jiang-an-campus',
        name: '四川大学江安校区',
        subtitle: '智慧景观导览',
        timezone: 'Asia/Shanghai',
        map_image_url: '',
        status: 'published',
      },
    ],
    currentSceneId: 'jiang-an',
  })

  return mount(DashboardView, {
    global: { stubs: { CheckinTrendChart: true } },
  })
}

describe('DashboardView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockSuccessfulDashboard()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('renders live management metrics for the selected scene', async () => {
    const wrapper = mountDashboard()
    await flushPromises()

    expect(wrapper.get('[data-test="metric-today-visitors"]').text()).toContain('128')
    expect(wrapper.get('[data-test="metric-accepted-checkins"]').text()).toContain('356')
    expect(wrapper.get('[data-test="spot-ranking"]').text()).toContain('江安图书馆')
    expect(wrapper.get('[data-test="latest-events"]').text()).toContain('RFID')
    expect(wrapper.get('[data-test="device-status"]').text()).toContain('SCU-JA-001')

    wrapper.unmount()
  })

  it('keeps successful panels visible when one dashboard request fails', async () => {
    vi.mocked(dashboardApi.getSpotRanking).mockRejectedValueOnce(new Error('排行暂时不可用'))

    const wrapper = mountDashboard()
    await flushPromises()

    expect(wrapper.get('[data-test="metric-today-visitors"]').text()).toContain('128')
    expect(wrapper.get('[data-test="spot-ranking"]').text()).toContain('排行暂时不可用')
    expect(wrapper.get('[data-test="latest-events"]').text()).toContain('RFID')

    wrapper.unmount()
  })
})
