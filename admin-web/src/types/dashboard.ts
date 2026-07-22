export interface DashboardFilters {
  sceneId: string
  dateFrom: string
  dateTo: string
}

export interface DashboardSummary {
  generated_at: string
  scene_id: string | null
  date_from: string
  date_to: string
  today_visitors: number
  accepted_checkins: number
  bound_cards: number
  online_devices: number
}

export interface CheckinTrendItem {
  date: string
  count: number
}

export interface SpotRankingItem {
  spot_id: string
  name: string
  event_count: number
}

export interface CheckinEvent {
  id: string
  event_id: string
  device_id: string
  spot_id: string
  user_id: string | null
  card_id: string | null
  visit_id: string | null
  checkin_type: string
  status: string
  failure_code: string
  received_at: string
}

export interface DeviceStatus {
  id: string
  device_id: string
  scene_id: string
  spot_id: string
  device_type: string
  secret_fingerprint: string
  status: string
  firmware_version: string
  last_seen_at: string | null
  last_error_code: string
}
