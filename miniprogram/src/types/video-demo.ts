import type { PoseType } from './checkin-success'

export interface VideoDemoTemporaryCheckin {
  readonly recordId: string
  readonly spotId: string
  readonly checkedAt: string
  readonly checkedAtLabel: string
  readonly poseId: PoseType
  readonly methodLabel: '点位打卡 · 演示'
  readonly isDemo: true
}

export interface VideoDemoState {
  readonly temporaryCheckins: readonly VideoDemoTemporaryCheckin[]
}
