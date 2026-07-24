import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { guideDemoData } from '../guide'
import { buildCheckinOverview, recordsDemoData } from '../records'
import {
  addVideoDemoCheckin,
  mergeVideoDemoRecordSources,
  resetVideoDemoState,
} from '../../state/video-demo'

describe('video demo memory state', () => {
  beforeEach(resetVideoDemoState)
  afterEach(resetVideoDemoState)

  it('adds a temporary fourth checkin without mutating the source mock', () => {
    const before = JSON.stringify(recordsDemoData.records)
    addVideoDemoCheckin({
      recordId: 'video-demo-bugao',
      spotId: 'bugao-mountain',
      checkedAt: '2026-07-22T12:00:00+08:00',
      checkedAtLabel: '今天 12:00',
      methodLabel: '点位打卡 · 演示',
      poseId: 'victory',
      isDemo: true,
    })
    const overview = buildCheckinOverview(
      mergeVideoDemoRecordSources(recordsDemoData.records),
      guideDemoData.spots,
    )
    expect(overview.checkedCount).toBe(4)
    expect(overview.totalCount).toBe(9)
    expect(JSON.stringify(recordsDemoData.records)).toBe(before)
  })

  it('returns to the original 3/9 state after a reset', () => {
    addVideoDemoCheckin({
      recordId: 'video-demo-bugao',
      spotId: 'bugao-mountain',
      checkedAt: '2026-07-22T12:00:00+08:00',
      checkedAtLabel: '今天 12:00',
      methodLabel: '点位打卡 · 演示',
      poseId: 'victory',
      isDemo: true,
    })
    resetVideoDemoState()
    expect(buildCheckinOverview(
      mergeVideoDemoRecordSources(recordsDemoData.records),
      guideDemoData.spots,
    ).checkedCount).toBe(3)
  })
})
