import type { GuideCategoryId, GuideSpot } from './guide'

export type RecommendationFilterId = GuideCategoryId | 'checked' | 'unchecked'

export interface RecommendationFilterOption {
  readonly id: RecommendationFilterId
  readonly label: string
}

export interface RecommendationListItem {
  readonly spot: GuideSpot
  readonly isCheckedIn: boolean
  readonly isInRoute: boolean
}
