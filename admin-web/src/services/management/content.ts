import type {
  ContentListFilters,
  RoutePayload,
  Scene,
  Spot,
  SpotMedia,
  SpotPayload,
  TravelRoute,
} from '../../types/content'
import { apiGet, apiPatch, apiPost } from '../http'

function listQuery(filters: ContentListFilters = {}) {
  const params = new URLSearchParams()
  if (filters.sceneId) params.set('scene_id', filters.sceneId)
  if (filters.status) params.set('status', filters.status)
  if (filters.search) params.set('search', filters.search)
  if (filters.page) params.set('page', String(filters.page))
  if (filters.pageSize) params.set('page_size', String(filters.pageSize))
  const query = params.toString()
  return query ? `?${query}` : ''
}

export const listScenes = () => apiGet<{ items: Scene[] }>('/api/v1/management/scenes')
export const getScene = (id: string) => apiGet<Scene>(`/api/v1/management/scenes/${id}`)
export const updateScene = (id: string, payload: Partial<Scene>) =>
  apiPatch<Partial<Scene>, Scene>(`/api/v1/management/scenes/${id}`, payload)

export const listSpots = (filters: ContentListFilters = {}) =>
  apiGet<{ items: Spot[] }>(`/api/v1/management/spots${listQuery(filters)}`)
export const createSpot = (payload: SpotPayload) =>
  apiPost<SpotPayload, Spot>('/api/v1/management/spots', payload)
export const updateSpot = (id: string, payload: SpotPayload) =>
  apiPatch<SpotPayload, Spot>(`/api/v1/management/spots/${id}`, payload)
export const publishSpot = (id: string) =>
  apiPost<Record<string, never>, Spot>(`/api/v1/management/spots/${id}/publish`, {})
export const disableSpot = (id: string, payload: { confirm: true; reason: string }) =>
  apiPost<typeof payload, Spot>(`/api/v1/management/spots/${id}/disable`, payload, false)

export type SpotMediaPayload = Omit<SpotMedia, 'id' | 'spot_id'>
export const createSpotMedia = (spotId: string, payload: SpotMediaPayload) =>
  apiPost<SpotMediaPayload, SpotMedia>(`/api/v1/management/spots/${spotId}/media`, payload)
export const updateSpotMedia = (spotId: string, mediaId: string, payload: SpotMediaPayload) =>
  apiPatch<SpotMediaPayload, SpotMedia>(
    `/api/v1/management/spots/${spotId}/media/${mediaId}`,
    payload,
  )
export const disableSpotMedia = (
  spotId: string,
  mediaId: string,
  payload: { confirm: true; reason: string },
) => apiPost<typeof payload, SpotMedia>(
  `/api/v1/management/spots/${spotId}/media/${mediaId}/disable`,
  payload,
  false,
)

export const listRoutes = (filters: ContentListFilters = {}) =>
  apiGet<{ items: TravelRoute[] }>(`/api/v1/management/routes${listQuery(filters)}`)
export const createRoute = (payload: RoutePayload) =>
  apiPost<RoutePayload, TravelRoute>('/api/v1/management/routes', payload)
export const updateRoute = (id: string, payload: RoutePayload) =>
  apiPatch<RoutePayload, TravelRoute>(`/api/v1/management/routes/${id}`, payload)
