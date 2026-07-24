import type { GuideSpot } from './guide'

export type CheckinTab = 'checked' | 'unchecked'

export type CheckinMethod = 'nfc' | 'camera-assisted' | 'device-recognition'

export type RecordsViewStatus = 'ready' | 'loading' | 'error'

export interface CheckinRecord {
  readonly id: string
  readonly spotId: string
  readonly checkedAt: string
  readonly checkedAtLabel: string
  readonly method: CheckinMethod
  readonly methodLabel: string
  readonly maskedCardUid?: string
  readonly deviceProductCode?: string
  readonly isDemo: true
}

export interface ProductSyncSummary {
  readonly productCode: string
  readonly bindingStatus: 'bound' | 'unbound'
  readonly lastSyncedAt?: string
  readonly lastSyncLabel: string
  readonly isDemo: true
}

export interface CheckinRouteOverview {
  readonly routeId: string
}

export interface RecordsPageData {
  readonly records: readonly CheckinRecord[]
  readonly product: ProductSyncSummary
  readonly route: CheckinRouteOverview
  readonly initialStatus: RecordsViewStatus
}

export interface ResolvedCheckinRecord {
  readonly record: CheckinRecord
  readonly spot: GuideSpot
}

export interface CheckinStatsData {
  readonly checkedCount: number
  readonly totalCount: number
  readonly progressRatio: number
  readonly progressPercentage: number
}

export interface CheckinRecordSource {
  readonly spotId: string
}

export interface CheckinSpotSource {
  readonly id: string
}

export interface CheckinOverview extends CheckinStatsData {
  readonly checkedSpotIds: readonly string[]
  readonly uncheckedSpotIds: readonly string[]
  readonly uncheckedCount: number
}
