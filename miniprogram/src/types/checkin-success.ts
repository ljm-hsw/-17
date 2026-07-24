import type { GuideSpot } from './guide'

export type PoseType = 'victory' | 'hands-on-hips' | 'arms-crossed'

export interface PoseChallenge {
  readonly id: PoseType
  readonly name: string
  readonly instruction: string
  readonly image: string
}

export interface CheckinSuccessData {
  readonly recordId: string
  readonly spotId: GuideSpot['id']
  readonly checkedAtLabel: string
  readonly methodLabel: string
  readonly checkedCount: number
  readonly totalCount: number
  readonly pose: PoseChallenge
  readonly checkedAt?: string
  readonly checkinMethod?: string
  readonly userId?: string
  readonly photoRequired?: boolean
  readonly poseChallengeId?: PoseType
  readonly isDemo: true
}
