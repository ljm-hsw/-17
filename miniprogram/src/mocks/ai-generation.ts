import type { GuideSpot } from '../types/guide'
import type {
  AiGenerationOptions,
  AiGenerationResultData,
  AiGenerationSource,
  AiGenerationStyle,
} from '../types/ai-generation'
import type { CheckinRecord } from '../types/records'

const generationSources: readonly AiGenerationSource[] = ['video-demo', 'profile-demo', 'ai-chat']
const generationStyles: readonly AiGenerationStyle[] = ['default', 'relaxed']

export const aiGenerationDemoData = {
  badge: '前端功能演示 · 智能体服务待接入',
  resultBadge: '前端演示结果 · 智能体服务待接入',
  durationMs: 2000,
  steps: [
    { id: 'records', title: '正在读取打卡点位', description: '整理本次校园游览的点位顺序' },
    { id: 'route', title: '正在梳理游览路线', description: '将点位串联为清晰的旅程脉络' },
    { id: 'materials', title: '正在关联旅程影像', description: '检查当前前端演示素材' },
    { id: 'story', title: '正在组织故事表达', description: '生成固定的前端演示结果' },
  ],
  result: {
    title: '《在江安，把青春走成一条路线》',
    story: '从青春广场出发，沿着长桥感受校园水岸的舒展，再走进江安图书馆，在光影与书香中放慢脚步。后来抵达不高山，开阔的草地和起伏的景观让这段校园漫游多了一份轻松。四个点位串成的不只是路线，也是一次重新认识江安的过程。',
    momentsCopy: '今天在江安，把青春广场、长桥、江安图书馆和不高山走成了一条路线。边走边看，校园里的风景也有了自己的故事。',
    redBookCopy: '江安校区漫游路线：青春广场 → 长桥 → 江安图书馆 → 不高山。适合慢慢走、慢慢拍，也适合把校园日常收藏成一段有温度的记忆。',
  } satisfies AiGenerationResultData,
} as const

export function parseAiGenerationOptions(options?: Record<string, unknown>): AiGenerationOptions {
  const generationType = options?.generationType === 'moments' ? 'moments' : 'travelogue'
  const source = typeof options?.source === 'string' && generationSources.includes(options.source as AiGenerationSource)
    ? options.source as AiGenerationSource
    : 'video-demo'
  const style = typeof options?.style === 'string' && generationStyles.includes(options.style as AiGenerationStyle)
    ? options.style as AiGenerationStyle
    : 'default'
  return { generationType, source, style }
}

export function buildJourneySpots(
  records: readonly CheckinRecord[],
  spots: readonly GuideSpot[],
): readonly GuideSpot[] {
  const spotById = new Map(spots.map((spot) => [spot.id, spot]))
  const seen = new Set<string>()
  return [...records]
    .sort((left, right) => Date.parse(left.checkedAt) - Date.parse(right.checkedAt))
    .flatMap((record) => {
      if (seen.has(record.spotId)) return []
      const spot = spotById.get(record.spotId)
      if (!spot) return []
      seen.add(record.spotId)
      return [spot]
    })
}

export function buildAiGenerationResult(
  spots: readonly GuideSpot[],
  style: AiGenerationStyle = 'default',
): AiGenerationResultData {
  const names = spots.map((spot) => spot.name)
  const route = names.join('、')
  const hasBugaoMountain = spots.some((spot) => spot.id === 'bugao-mountain')
  const ending = hasBugaoMountain
    ? '最后抵达不高山，开阔的草地让这段校园漫游多了一份轻松。'
    : '在图书馆的光影与书香中，这段校园漫游暂时落下句点。'
  const story = style === 'relaxed'
    ? `今天慢慢走过${route}。没有赶路，只是边走边看，顺手把江安的风景收进了这段演示故事里。${ending}`
    : `从青春广场出发，沿着长桥感受校园水岸的舒展，再走进江安图书馆，在光影与书香中放慢脚步。${ending}这些点位串成的不只是路线，也是一次重新认识江安的过程。`

  return {
    ...aiGenerationDemoData.result,
    story,
    momentsCopy: `今天在江安，把${route}走成了一条路线。边走边看，校园里的风景也有了自己的故事。`,
    redBookCopy: `江安校区漫游路线：${names.join(' → ')}。适合慢慢走、慢慢拍，也适合把校园日常收藏成一段有温度的记忆。`,
  }
}
