export type SpotDetailPageStatus = 'ready' | 'missing-id' | 'not-found'

export interface SpotDetailCheckinState {
  readonly isCheckedIn: boolean
}

export interface SpotGalleryChangeEvent {
  readonly detail: {
    readonly current: number
  }
}
