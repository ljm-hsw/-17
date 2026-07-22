import type { Device, DeviceCheckin, DeviceFilters, DevicePayload, DeviceSecretResult } from '../../types/device'
import { apiGet, apiPatch, apiPost } from '../http'

function query(filters: DeviceFilters) {
  const params = new URLSearchParams()
  if (filters.sceneId) params.set('scene_id', filters.sceneId)
  if (filters.spotId) params.set('spot_id', filters.spotId)
  if (filters.status) params.set('status', filters.status)
  if (filters.search) params.set('search', filters.search)
  if (filters.page) params.set('page', String(filters.page))
  if (filters.pageSize) params.set('page_size', String(filters.pageSize))
  const value = params.toString()
  return value ? `?${value}` : ''
}

export const listDevices = (filters: DeviceFilters = {}) =>
  apiGet<{ items: Device[] }>(`/api/v1/management/devices${query(filters)}`)
export const getDevice = (id: string) => apiGet<Device>(`/api/v1/management/devices/${id}`)
export const createDevice = (payload: DevicePayload) =>
  apiPost<DevicePayload, DeviceSecretResult>('/api/v1/management/devices', payload, false)
export const updateDevice = (id: string, payload: DevicePayload) =>
  apiPatch<DevicePayload, Device>(`/api/v1/management/devices/${id}`, payload)
export const rotateDeviceSecret = (id: string, payload: { confirm: true; reason: string }) =>
  apiPost<typeof payload, DeviceSecretResult>(`/api/v1/management/devices/${id}/rotate-secret`, payload, false)
export const listDeviceCheckins = (id: string) =>
  apiGet<{ items: DeviceCheckin[] }>(`/api/v1/management/devices/${id}/checkins?page_size=8`)
