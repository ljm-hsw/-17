import type { CheckinEvent } from './dashboard'

export interface Device {
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

export interface DevicePayload {
  device_id: string
  scene_id: string
  spot_id: string
  device_type: string
  status: string
  firmware_version: string
}

export interface DeviceSecretResult extends Device {
  device_secret: string
}

export interface DeviceFilters {
  sceneId?: string
  spotId?: string
  status?: string
  search?: string
  page?: number
  pageSize?: number
}

export type DeviceCheckin = CheckinEvent
