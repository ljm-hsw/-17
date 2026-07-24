import { reactive, readonly } from 'vue'
import type { CheckinRecord, CheckinRecordSource } from '../types/records'
import type { VideoDemoState, VideoDemoTemporaryCheckin } from '../types/video-demo'

export const ENABLE_VIDEO_DEMO_MODE = true

const mutableVideoDemoState = reactive<{
  temporaryCheckins: VideoDemoTemporaryCheckin[]
}>({
  temporaryCheckins: [],
})

export const videoDemoState = readonly(mutableVideoDemoState) as VideoDemoState

export function addVideoDemoCheckin(checkin: VideoDemoTemporaryCheckin) {
  if (!ENABLE_VIDEO_DEMO_MODE) return

  const nextCheckins = mutableVideoDemoState.temporaryCheckins.filter(
    (item) => item.spotId !== checkin.spotId,
  )
  nextCheckins.push(checkin)
  mutableVideoDemoState.temporaryCheckins = nextCheckins
}

export function resetVideoDemoState() {
  mutableVideoDemoState.temporaryCheckins = []
}

export function mergeVideoDemoRecordSources(
  records: readonly CheckinRecordSource[],
): readonly CheckinRecordSource[] {
  if (!ENABLE_VIDEO_DEMO_MODE) return records
  return [
    ...records,
    ...mutableVideoDemoState.temporaryCheckins.map((checkin) => ({
      spotId: checkin.spotId,
    })),
  ]
}

export function mergeVideoDemoCheckinRecords(
  records: readonly CheckinRecord[],
): readonly CheckinRecord[] {
  if (!ENABLE_VIDEO_DEMO_MODE) return records
  return [
    ...records,
    ...mutableVideoDemoState.temporaryCheckins.map((checkin) => ({
      id: checkin.recordId,
      spotId: checkin.spotId,
      checkedAt: checkin.checkedAt,
      checkedAtLabel: checkin.checkedAtLabel,
      method: 'device-recognition' as const,
      methodLabel: checkin.methodLabel,
      isDemo: true as const,
    })),
  ]
}
