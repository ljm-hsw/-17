export type HomeFeatureId = 'guide' | 'records' | 'binding' | 'recommend'

export type HomeNavigationId = 'home' | 'ai' | 'profile'

export interface HomeBrand {
  readonly title: string
  readonly subtitle: string
  readonly logo: string
}

export interface HomeProgress {
  readonly visitedCount: number
  readonly totalCount: number
}

export interface HomeProduct {
  readonly label: string
  readonly code: string
  readonly status: string
  readonly editIcon: string
}

export interface HomeFeature {
  readonly id: HomeFeatureId
  readonly title: string
  readonly description: readonly string[]
  readonly image: string
}

export interface HomeSceneryItem {
  readonly id: string
  readonly title: string
  readonly image: string
}

export interface HomeNavigationItem {
  readonly id: HomeNavigationId
  readonly label: string
  readonly icon: string
}

export interface HomePageData {
  readonly brand: HomeBrand
  readonly heroImage: string
  readonly heroAlt: string
  readonly progress: HomeProgress
  readonly product: HomeProduct
  readonly features: readonly HomeFeature[]
  readonly scenery: readonly HomeSceneryItem[]
  readonly navigation: readonly HomeNavigationItem[]
}
