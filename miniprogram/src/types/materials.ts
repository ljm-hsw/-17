import type { PoseChallenge, PoseType } from './checkin-success'

export interface JourneyMaterialItem {
  readonly id: string
  readonly spotId: string
  readonly spotName: string
  readonly capturedAtLabel: string
  readonly poseId: PoseType
  readonly pose: PoseChallenge
  readonly image?: string
  readonly linkedToCheckin: boolean
  readonly isDemo: true
}

export interface MaterialsPageData {
  readonly title: string
  readonly prototypeLabel: string
  readonly description: string
  readonly integrationNotice: string
}
