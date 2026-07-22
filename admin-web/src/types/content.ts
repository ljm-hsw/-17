export interface Scene {
  id: string
  slug: string
  name: string
  subtitle: string
  timezone: string
  map_image_url: string
  status: string
}

export type PublishStatus = 'draft' | 'published' | 'disabled'

export interface SpotMedia {
  id: string
  spot_id: string
  url: string
  storage_key: string
  media_type: 'image'
  caption: string
  sort_order: number
  status: PublishStatus
}

export interface Spot {
  id: string
  scene_id: string
  slug: string
  name: string
  category: string
  summary: string
  description: string
  knowledge_content: string
  map_x: string
  map_y: string
  tags: string[]
  suggested_stay_minutes: number
  status: PublishStatus
  is_checkin_enabled: boolean
  is_photo_spot: boolean
  media: SpotMedia[]
}

export type SpotPayload = Omit<Spot, 'id' | 'media'>

export interface RouteStop {
  spot_id: string
  order: number
  note: string
}

export interface TravelRoute {
  id: string
  scene_id: string
  slug: string
  name: string
  summary: string
  estimated_minutes: number
  status: PublishStatus
  stops: RouteStop[]
}

export type RoutePayload = Omit<TravelRoute, 'id'>

export interface ContentListFilters {
  sceneId?: string
  status?: string
  search?: string
  page?: number
  pageSize?: number
}
