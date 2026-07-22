import { onScopeDispose, reactive, ref, watch, type Ref } from 'vue'

import {
  getCheckinTrend,
  getDashboardSummary,
  getDeviceStatus,
  getLatestEvents,
  getSpotRanking,
} from '../../services/management/dashboard'
import type {
  CheckinEvent,
  CheckinTrendItem,
  DashboardFilters,
  DashboardSummary,
  DeviceStatus,
  SpotRankingItem,
} from '../../types/dashboard'

type Section = 'summary' | 'trend' | 'ranking' | 'events' | 'devices'

interface UseDashboardOptions {
  sceneId: Ref<string>
  dateFrom: Ref<string>
  dateTo: Ref<string>
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : '数据加载失败，请稍后重试'
}

export function useDashboard(options: UseDashboardOptions) {
  const summary = ref<DashboardSummary | null>(null)
  const trend = ref<CheckinTrendItem[]>([])
  const ranking = ref<SpotRankingItem[]>([])
  const events = ref<CheckinEvent[]>([])
  const devices = ref<DeviceStatus[]>([])
  const errors = reactive<Record<Section, string>>({
    summary: '',
    trend: '',
    ranking: '',
    events: '',
    devices: '',
  })
  const loading = reactive<Record<Section, boolean>>({
    summary: true,
    trend: true,
    ranking: true,
    events: true,
    devices: true,
  })

  const filters = (): DashboardFilters => ({
    sceneId: options.sceneId.value,
    dateFrom: options.dateFrom.value,
    dateTo: options.dateTo.value,
  })

  async function loadSection(section: Section) {
    if (!options.sceneId.value) return
    loading[section] = true
    errors[section] = ''
    try {
      if (section === 'summary') summary.value = (await getDashboardSummary(filters())).data
      if (section === 'trend') trend.value = (await getCheckinTrend(filters())).data.items
      if (section === 'ranking') ranking.value = (await getSpotRanking(filters())).data.items
      if (section === 'events') events.value = (await getLatestEvents(filters())).data.items
      if (section === 'devices') devices.value = (await getDeviceStatus(filters())).data.items
    } catch (error) {
      errors[section] = errorMessage(error)
    } finally {
      loading[section] = false
    }
  }

  function refreshAll() {
    return Promise.allSettled(
      (['summary', 'trend', 'ranking', 'events', 'devices'] as Section[]).map(loadSection),
    )
  }

  void refreshAll()
  watch([options.sceneId, options.dateFrom, options.dateTo], refreshAll)

  const eventsTimer = window.setInterval(() => void loadSection('events'), 5_000)
  const overviewTimer = window.setInterval(() => {
    void loadSection('summary')
    void loadSection('devices')
  }, 10_000)

  onScopeDispose(() => {
    window.clearInterval(eventsTimer)
    window.clearInterval(overviewTimer)
  })

  return {
    summary,
    trend,
    ranking,
    events,
    devices,
    errors,
    loading,
    loadSection,
    refreshAll,
  }
}
