import { poseChallenges } from './checkin-success'
import type { GuideSpot } from '../types/guide'
import type { CheckinRecord } from '../types/records'
import type { JourneyMaterialItem, MaterialsPageData } from '../types/materials'
import type { VideoDemoTemporaryCheckin } from '../types/video-demo'

export const materialsDemoData = {
  title: '旅程影像',
  prototypeLabel: '功能验证原型',
  description: '当前为视觉采集与素材流转前端演示',
  integrationNotice: '照片上传、点位自动关联和姿势识别待接入',
} as const satisfies MaterialsPageData

const basePoseIds = ['victory', 'hands-on-hips', 'arms-crossed'] as const

export function buildJourneyMaterials(
  records: readonly CheckinRecord[],
  spots: readonly GuideSpot[],
  temporaryCheckins: readonly VideoDemoTemporaryCheckin[],
): readonly JourneyMaterialItem[] {
  const spotById = new Map(spots.map((spot) => [spot.id, spot]))
  const temporaryBySpotId = new Map(temporaryCheckins.map((checkin) => [checkin.spotId, checkin]))

  return records.flatMap((record, index) => {
    const spot = spotById.get(record.spotId)
    if (!spot) return []

    const temporary = temporaryBySpotId.get(record.spotId)
    const poseId = temporary?.poseId ?? basePoseIds[index % basePoseIds.length]
    const pose = poseChallenges.find((item) => item.id === poseId) ?? poseChallenges[0]

    return [{
      id: `material-${record.id}`,
      spotId: spot.id,
      spotName: spot.name,
      capturedAtLabel: record.checkedAtLabel,
      poseId,
      pose,
      // 当前仓库尚未放入 demo-photo-*.png；后续可在此直接配置真实本地素材路径。
      image: undefined,
      linkedToCheckin: true,
      isDemo: true,
    }]
  })
}
