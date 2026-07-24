export type ChatRole = 'assistant' | 'user'

export type ChatMessageKind = 'text' | 'thinking' | 'spot-recommendation'

export type ChatMessageStatus = 'generating' | 'success' | 'error'

export type AiQuestionType =
  | 'route'
  | 'spot'
  | 'places'
  | 'travelogue'
  | 'moments'
  | 'general'

export interface ChatMessage {
  readonly id: string
  readonly role: ChatRole
  readonly kind: ChatMessageKind
  readonly content: string
  readonly createdAtLabel: string
  readonly status: ChatMessageStatus
  readonly avatar: string
  readonly spotId?: string
  readonly sourceQuestionId?: string
  readonly retryable?: boolean
  readonly isDemo: true
}

export interface QuickQuestion {
  readonly id: string
  readonly label: string
  readonly question: string
  readonly type: AiQuestionType
  readonly availability: 'demo' | 'unavailable'
}

export interface AiQuestionRequest {
  readonly question: string
  readonly type: AiQuestionType
  readonly sourceQuestionId: string
}

export interface AiAssistantProfile {
  readonly name: string
  readonly subtitle: string
  readonly avatar: string
  readonly userAvatar: string
}

export interface AiChatDemoData {
  readonly assistant: AiAssistantProfile
  readonly welcomeMessage: ChatMessage
  readonly quickQuestions: readonly QuickQuestion[]
  readonly responseDelayMs: number
  readonly generalReply: string
  readonly generationUnavailableReply: string
}

export interface AiDemoRouteSuggestion {
  readonly checkedSpotNames: readonly string[]
  readonly remainingSpotIds: readonly string[]
  readonly nextSpotId?: string
  readonly continuationSpotIds: readonly string[]
}

export interface AiDemoRouteReply {
  readonly content: string
  readonly nextSpotId?: string
}
