import type {
  CheckinOverview,
  CheckinRecordSource,
  CheckinSpotSource,
  RecordsPageData,
} from '../types/records'

export function buildCheckinOverview(
  records: readonly CheckinRecordSource[],
  spots: readonly CheckinSpotSource[],
): CheckinOverview {
  const orderedValidSpotIds = spots
    .map((spot) => spot.id.trim())
    .filter((spotId, index, ids) => Boolean(spotId) && ids.indexOf(spotId) === index)
  const validSpotIds = new Set(orderedValidSpotIds)
  const checkedSpotIds = new Set<string>()

  records.forEach((record) => {
    const spotId = record.spotId.trim()
    if (validSpotIds.has(spotId)) checkedSpotIds.add(spotId)
  })

  const checkedSpotIdList = orderedValidSpotIds.filter((spotId) => checkedSpotIds.has(spotId))
  const uncheckedSpotIds = orderedValidSpotIds.filter((spotId) => !checkedSpotIds.has(spotId))
  const checkedCount = checkedSpotIdList.length
  const totalCount = orderedValidSpotIds.length
  const progressRatio = totalCount > 0 ? checkedCount / totalCount : 0

  return {
    checkedSpotIds: checkedSpotIdList,
    uncheckedSpotIds,
    checkedCount,
    uncheckedCount: uncheckedSpotIds.length,
    totalCount,
    progressRatio,
    progressPercentage: Math.round(progressRatio * 100),
  }
}

// 以下记录、时间、硬件状态、UID 与同步信息均为本地演示数据，不代表真实打卡或服务端同步。
export const recordsDemoData = {
  initialStatus: 'ready',
  records: [
    {
      id: 'demo-checkin-youth-square',
      spotId: 'youth-square',
      checkedAt: '2026-07-22T09:20:00+08:00',
      checkedAtLabel: '今天 09:20',
      method: 'nfc',
      methodLabel: 'NFC打卡',
      maskedCardUid: '••••8A3F',
      deviceProductCode: 'SCU-JA-0001',
      isDemo: true,
    },
    {
      id: 'demo-checkin-long-bridge',
      spotId: 'long-bridge',
      checkedAt: '2026-07-22T10:05:00+08:00',
      checkedAtLabel: '今天 10:05',
      method: 'camera-assisted',
      methodLabel: '摄像头辅助打卡',
      maskedCardUid: '••••8A3F',
      deviceProductCode: 'SCU-JA-0001',
      isDemo: true,
    },
    {
      id: 'demo-checkin-library',
      spotId: 'jiang-an-library',
      checkedAt: '2026-07-22T10:45:00+08:00',
      checkedAtLabel: '今天 10:45',
      method: 'nfc',
      methodLabel: 'NFC打卡',
      maskedCardUid: '••••8A3F',
      deviceProductCode: 'SCU-JA-0001',
      isDemo: true,
    },
  ],
  product: {
    productCode: 'SCU-JA-0001',
    bindingStatus: 'bound',
    lastSyncedAt: '2026-07-22T10:50:00+08:00',
    lastSyncLabel: '今天 10:50',
    isDemo: true,
  },
  route: {
    routeId: 'demo-current-campus-visit',
  },
} as const satisfies RecordsPageData
