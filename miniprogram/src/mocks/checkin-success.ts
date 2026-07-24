import type { PoseChallenge, PoseType } from '../types/checkin-success'
import { buildCheckinOverview } from './records'
import type { CheckinRecordSource, CheckinSpotSource } from '../types/records'
import { withRemoteAssets } from '../config/assets'

export const poseChallenges = withRemoteAssets([
  {
    id: 'victory',
    name: '比耶',
    instruction: '面向镜头举起一只手，比出V字手势',
    image: '/static/checkin/poses/pose-victory.png',
  },
  {
    id: 'hands-on-hips',
    name: '双手叉腰',
    instruction: '面向镜头站立，双手自然叉腰',
    image: '/static/checkin/poses/pose-hands-on-hips.png',
  },
  {
    id: 'arms-crossed',
    name: '双臂交叉',
    instruction: '面向镜头站立，双臂交叉放在胸前',
    image: '/static/checkin/poses/pose-arms-crossed.png',
  },
] as const satisfies readonly PoseChallenge[])

// 纯函数：随机数由调用方传入，便于测试时固定结果；页面默认传入 Math.random()。
export function selectPoseChallenge(
  randomValue: number,
  fixedPoseId?: PoseType,
): PoseChallenge {
  if (fixedPoseId) {
    return poseChallenges.find((pose) => pose.id === fixedPoseId) ?? poseChallenges[0]
  }

  const normalizedValue = Number.isFinite(randomValue)
    ? Math.min(Math.max(randomValue, 0), 0.999999)
    : 0
  const index = Math.floor(normalizedValue * poseChallenges.length)
  return poseChallenges[index]
}

export function buildDemoCheckinProgress(
  records: readonly CheckinRecordSource[],
  spots: readonly CheckinSpotSource[],
  newSpotId: string,
) {
  const overview = buildCheckinOverview(records, spots)
  const checkedSpotIds = new Set(overview.checkedSpotIds)
  const isValidNewSpot = spots.some((spot) => spot.id.trim() === newSpotId.trim())
  if (isValidNewSpot) checkedSpotIds.add(newSpotId.trim())

  return {
    checkedCount: checkedSpotIds.size,
    totalCount: overview.totalCount,
  }
}
