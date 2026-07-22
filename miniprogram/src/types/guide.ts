export type GuideCategoryId =
  | 'all'
  | 'architecture'
  | 'sports'
  | 'study'
  | 'green'

export type SpotCategoryId = Exclude<GuideCategoryId, 'all'>

export interface GuideCategory {
  readonly id: GuideCategoryId
  readonly label: string
}

export interface GuideSpot {
  readonly id: string
  readonly markerId: number
  readonly name: string
  readonly folderName: string
  readonly latitude: number
  readonly longitude: number
  readonly iconPath: string
  readonly labelOffsetX: number
  readonly labelOffsetY: number
  readonly category: SpotCategoryId
  readonly tags: readonly string[]
  readonly summary: string
  readonly description: string
  readonly coverImage: string
  readonly gallery: readonly string[]
  readonly image: string
  readonly xPercent: number
  readonly yPercent: number
  readonly suggestedStayMinutes: readonly [number, number]
  readonly suggestedStayText: string
  readonly recommendedTimes: readonly string[]
  readonly isCheckedIn: boolean
  readonly isInRoute: boolean
  readonly isPhotoSpot: boolean
  readonly isRecommended: boolean
  readonly recommendationReason: string
  readonly checkinTip: string
  readonly relatedSpotIds: readonly string[]
}

export type SpotDistanceStatus = 'unavailable' | 'loading' | 'available' | 'error'

export interface SpotDistanceState {
  readonly status: SpotDistanceStatus
  readonly label: string
  readonly distanceMeters?: number
  readonly locationAccuracy?: number
}

export interface GuideMapCoordinate {
  readonly latitude: number
  readonly longitude: number
}

export interface GuideMapViewState extends GuideMapCoordinate {
  readonly scale: number
}

export interface GuideMapMarker {
  readonly id: number
  readonly latitude: number
  readonly longitude: number
  readonly iconPath: string
  readonly width: number
  readonly height: number
  readonly anchor: {
    readonly x: number
    readonly y: number
  }
  readonly label: {
    readonly content: string
    readonly color: string
    readonly fontSize: number
    readonly borderRadius: number
    readonly bgColor: string
    readonly padding: number
    readonly textAlign: 'center'
    readonly anchorX: number
    readonly anchorY: number
  }
  readonly zIndex: number
}

export interface GuideMapPolyline {
  readonly points: readonly GuideMapCoordinate[]
  readonly color: string
  readonly width: number
  readonly dottedLine: boolean
  readonly arrowLine: boolean
}

export interface GuideRouteSummary {
  readonly id: string
  readonly name: string
  readonly durationLabel: string
  readonly completedSpotCount: number
  readonly totalSpotCount: number
  readonly spotIds: readonly string[]
}

export interface GuidePageData {
  readonly mapImage: string
  readonly mapAlt: string
  readonly mapCenter: GuideMapCoordinate
  readonly initialMapScale: number
  readonly mapMinScale: number
  readonly mapMaxScale: number
  readonly searchPlaceholder: string
  readonly categories: readonly GuideCategory[]
  readonly spots: readonly GuideSpot[]
  readonly route: GuideRouteSummary
}
