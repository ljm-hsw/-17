import { effectScope, ref } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as dashboardApi from '../../../services/management/dashboard'
import { useDashboard } from '../useDashboard'

const apiResult = <T,>(data: T) => ({ data, requestId: 'req-dashboard' })

describe('useDashboard', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('polls current information and clears every timer when its scope stops', async () => {
    vi.useFakeTimers()
    const summary = vi.spyOn(dashboardApi, 'getDashboardSummary').mockResolvedValue(
      apiResult({
        generated_at: '2026-07-22T10:00:00+08:00',
        scene_id: 'jiang-an',
        date_from: '2026-07-16',
        date_to: '2026-07-22',
        today_visitors: 1,
        accepted_checkins: 2,
        bound_cards: 3,
        online_devices: 4,
      }),
    )
    vi.spyOn(dashboardApi, 'getCheckinTrend').mockResolvedValue(apiResult({ items: [] }))
    vi.spyOn(dashboardApi, 'getSpotRanking').mockResolvedValue(apiResult({ items: [] }))
    const latestEvents = vi
      .spyOn(dashboardApi, 'getLatestEvents')
      .mockResolvedValue({ data: { items: [] }, requestId: 'req-events' })
    vi.spyOn(dashboardApi, 'getDeviceStatus').mockResolvedValue(apiResult({ items: [] }))

    const scope = effectScope()
    scope.run(() =>
      useDashboard({
        sceneId: ref('jiang-an'),
        dateFrom: ref('2026-07-16'),
        dateTo: ref('2026-07-22'),
      }),
    )
    await vi.advanceTimersByTimeAsync(10_000)

    expect(summary).toHaveBeenCalledTimes(2)
    expect(latestEvents).toHaveBeenCalledTimes(3)

    scope.stop()
    await vi.advanceTimersByTimeAsync(20_000)
    expect(summary).toHaveBeenCalledTimes(2)
    expect(latestEvents).toHaveBeenCalledTimes(3)
  })
})
