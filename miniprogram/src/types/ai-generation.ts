export type AiGenerationKind = 'travelogue' | 'moments'

export type AiGenerationSource = 'video-demo' | 'profile-demo' | 'ai-chat'

export type AiGenerationStyle = 'default' | 'relaxed'

export interface AiGenerationOptions {
  readonly generationType: AiGenerationKind
  readonly source: AiGenerationSource
  readonly style: AiGenerationStyle
}

export interface AiGenerationStep {
  readonly id: string
  readonly title: string
  readonly description: string
}

export interface AiGenerationResultData {
  readonly title: string
  readonly story: string
  readonly momentsCopy: string
  readonly redBookCopy: string
}
