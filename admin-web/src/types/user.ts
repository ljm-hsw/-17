import type { CardBinding } from './card'
import type { CheckinEvent } from './dashboard'

export interface ManagementVisitor {
  id: string
  username: string
  nickname: string
  avatar_url: string
  is_demo: boolean
  is_active: boolean
  active_card_count: number
}

export interface VisitSession {
  id: string
  user_id: string
  scene_id: string
  local_date: string
  started_at: string
  last_checkin_at: string | null
}

export interface UserDetailData {
  user: ManagementVisitor | null
  bindings: CardBinding[]
  visits: VisitSession[]
  checkins: CheckinEvent[]
}
