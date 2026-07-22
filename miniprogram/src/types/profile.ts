export interface ProfileUserDemo {
  readonly nickname: string
  readonly roleLabel: string
  readonly avatar: string
  readonly demoLabel: string
  readonly isDemo: true
}

export interface ProfileStats {
  readonly checkedCount: number
  readonly totalCount: number
  readonly uncheckedCount: number
  readonly completionRate: number
  readonly digitalCardCount: number
}

export type ProfileServiceId = 'feedback' | 'about-device'

export interface ProfileServiceItem {
  readonly id: ProfileServiceId
  readonly title: string
  readonly iconText: string
}

export interface ProfilePageData {
  readonly user: ProfileUserDemo
  readonly serviceItems: readonly ProfileServiceItem[]
}

export interface ProfileRecordSource {
  readonly spotId: string
}

export interface ProfileSpotSource {
  readonly id: string
}
