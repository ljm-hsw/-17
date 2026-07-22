import type {
  CheckinEvent,
  CheckinTrendItem,
  DashboardFilters,
  DashboardSummary,
  DeviceStatus,
  SpotRankingItem,
} from '../../types/dashboard'
import { apiGet } from '../http'

function dashboardQuery(filters: DashboardFilters, extra: Record<string, string> = {}) {
  const params = new URLSearchParams({
    scene_id: filters.sceneId,
    date_from: filters.dateFrom,
    date_to: filters.dateTo,
    ...extra,
  })
  return params.toString()
}

export function getDashboardSummary(filters: DashboardFilters) {
  return apiGet<DashboardSummary>(`/api/v1/management/dashboard/summary?${dashboardQuery(filters)}`)
}

export function getCheckinTrend(filters: DashboardFilters) {
  return apiGet<{ items: CheckinTrendItem[] }>(
    `/api/v1/management/dashboard/checkin-trend?${dashboardQuery(filters)}`,
  )
}

export function getSpotRanking(filters: DashboardFilters) {
  return apiGet<{ items: SpotRankingItem[] }>(
    `/api/v1/management/dashboard/spot-ranking?${dashboardQuery(filters)}`,
  )
}

export function getLatestEvents(filters: DashboardFilters) {
  return apiGet<{ items: CheckinEvent[] }>(
    `/api/v1/management/dashboard/latest-events?${dashboardQuery(filters, { page_size: '6' })}`,
  )
}

export function getDeviceStatus(filters: DashboardFilters) {
  const params = new URLSearchParams({ scene_id: filters.sceneId })
  return apiGet<{ items: DeviceStatus[] }>(
    `/api/v1/management/dashboard/device-status?${params.toString()}`,
  )
}
