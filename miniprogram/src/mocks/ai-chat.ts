import type { GuideSpot } from '../types/guide'
import type {
  AiChatDemoData,
  AiDemoRouteReply,
  AiDemoRouteSuggestion,
  AiQuestionType,
  ChatMessage,
} from '../types/ai-chat'
import type { CheckinRecordSource } from '../types/records'

export const AI_AVATAR_PATH = '/static/ai/ai-avatar.png'
export const USER_AVATAR_PATH = '/static/common/user-avatar-default.png'
export const AI_GENERATION_UNAVAILABLE_MESSAGE = '智能体生成服务待接入'

export const aiChatDemoData = {
  assistant: {
    name: '倾梦小游',
    subtitle: '四川大学江安校区智慧导览助手',
    avatar: AI_AVATAR_PATH,
    userAvatar: USER_AVATAR_PATH,
  },
  welcomeMessage: {
    id: 'assistant-welcome',
    role: 'assistant',
    kind: 'text',
    content:
      '你好，我是倾梦小游。\n当前智能体服务尚未正式接入，你可以先体验校园点位介绍和路线建议等前端演示功能。游记和社交文案生成将在后续接入。',
    createdAtLabel: '刚刚',
    status: 'success',
    avatar: AI_AVATAR_PATH,
    isDemo: true,
  },
  quickQuestions: [
    {
      id: 'quick-library',
      label: '介绍一下江安图书馆',
      question: '介绍一下江安图书馆',
      type: 'spot',
      availability: 'demo',
    },
    {
      id: 'quick-route',
      label: '帮我规划校园游览路线',
      question: '帮我规划校园游览路线',
      type: 'route',
      availability: 'demo',
    },
    {
      id: 'quick-travelogue',
      label: '根据我的打卡记录生成游记',
      question: '根据我的打卡记录生成游记',
      type: 'travelogue',
      availability: 'unavailable',
    },
    {
      id: 'quick-moments',
      label: '帮我写一段朋友圈文案',
      question: '帮我写一段朋友圈文案',
      type: 'moments',
      availability: 'unavailable',
    },
  ],
  responseDelayMs: 550,
  generalReply:
    '当前仅提供校园点位介绍和游览路线建议的本地前端演示。你可以输入正式点位名称，或请我规划校园游览路线。',
  generationUnavailableReply:
    '该功能的页面入口已经预留，智能体生成服务将在后续接入。',
} as const satisfies AiChatDemoData

const spotAliases: Readonly<Record<string, string>> = {
  图书馆: 'jiang-an-library',
  东门: 'east-gate-archway',
  牌坊: 'east-gate-archway',
}

const generationKeywords = [
  '生成游记',
  '编织我的游记',
  '朋友圈文案',
  '小红书文案',
  '小红书标题',
  '短视频脚本',
  '总结今天的旅行',
  '生成旅行故事',
  '重新编织',
] as const

export function findSpotIdInQuestion(
  question: string,
  spots: readonly GuideSpot[],
): string | undefined {
  const directMatch = spots.find((spot) => question.includes(spot.name))
  if (directMatch) return directMatch.id

  const alias = Object.entries(spotAliases).find(([keyword]) => question.includes(keyword))
  return alias?.[1]
}

export function inferQuestionType(question: string, spotId?: string): AiQuestionType {
  if (generationKeywords.some((keyword) => question.includes(keyword))) {
    return question.includes('朋友圈') || question.includes('小红书') || question.includes('短视频')
      ? 'moments'
      : 'travelogue'
  }
  if (question.includes('哪些地方') || question.includes('去了哪里') || question.includes('到访')) {
    return 'places'
  }
  if (
    question.includes('路线') ||
    question.includes('下一站') ||
    question.includes('去哪里') ||
    question.includes('推荐去哪')
  ) {
    return 'route'
  }
  if (spotId) return 'spot'
  return 'general'
}

export function isGenerationQuestionType(type: AiQuestionType): boolean {
  return type === 'travelogue' || type === 'moments'
}

export function buildSpotDemoReply(spot: GuideSpot): string {
  return `${spot.name}：${spot.summary}\n建议停留${spot.suggestedStayText}。${spot.recommendationReason}`
}

export function createWelcomeMessages(): ChatMessage[] {
  return [{ ...aiChatDemoData.welcomeMessage }]
}

export function buildDemoRouteSuggestion(
  spots: readonly GuideSpot[],
  routeSpotIds: readonly string[],
  records: readonly CheckinRecordSource[],
): AiDemoRouteSuggestion {
  const spotById = new Map(spots.map((spot) => [spot.id, spot]))
  const checkedSpotIds = new Set(
    records.map((record) => record.spotId).filter((spotId) => spotById.has(spotId)),
  )
  const remainingSpotIds = routeSpotIds.filter(
    (spotId) => spotById.has(spotId) && !checkedSpotIds.has(spotId),
  )
  const continuationSpotIds = remainingSpotIds.slice(1, 3)

  return {
    checkedSpotNames: [...checkedSpotIds]
      .map((spotId) => spotById.get(spotId)?.name)
      .filter((name): name is string => Boolean(name)),
    remainingSpotIds,
    nextSpotId: remainingSpotIds[0],
    continuationSpotIds,
  }
}

export function buildRouteDemoReply(
  spots: readonly GuideSpot[],
  routeSpotIds: readonly string[],
  records: readonly CheckinRecordSource[],
): AiDemoRouteReply {
  const spotById = new Map(spots.map((spot) => [spot.id, spot]))
  const suggestion = buildDemoRouteSuggestion(spots, routeSpotIds, records)
  const checkedText = suggestion.checkedSpotNames.length > 0
    ? `当前演示记录中已完成${suggestion.checkedSpotNames.join('、')}。`
    : '当前演示记录中还没有已完成点位。'
  const nextSpot = suggestion.nextSpotId
    ? spotById.get(suggestion.nextSpotId)
    : undefined
  const continuationNames = suggestion.continuationSpotIds
    .map((spotId) => spotById.get(spotId)?.name)
    .filter((name): name is string => Boolean(name))

  if (!nextSpot) {
    return {
      content: `${checkedText}推荐路线中的9个正式校园点位已经全部完成。这是前端演示建议，不代表实时导航结果。`,
    }
  }

  const continuationText = continuationNames.length > 0
    ? `，之后可继续游览${continuationNames.join('、')}`
    : ''

  return {
    content: `${checkedText}建议下一站前往${nextSpot.name}${continuationText}。这是前端演示路线，不获取实时位置，也不代表实际步行导航。`,
    nextSpotId: nextSpot.id,
  }
}
