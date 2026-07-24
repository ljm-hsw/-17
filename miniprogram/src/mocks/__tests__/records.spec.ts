import { describe, expect, it } from 'vitest'
import { buildDemoCheckinProgress } from '../checkin-success'
import { guideDemoData } from '../guide'
import { buildCheckinOverview, recordsDemoData } from '../records'

describe('shared check-in overview', () => {
  it('derives 3/9, 33% and six unchecked spots from valid unique ids', () => {
    const overview = buildCheckinOverview(recordsDemoData.records, guideDemoData.spots)

    expect(overview.checkedCount).toBe(3)
    expect(overview.totalCount).toBe(9)
    expect(overview.uncheckedCount).toBe(6)
    expect(overview.progressPercentage).toBe(33)
    expect(overview.checkedSpotIds).toEqual([
      'youth-square',
      'jiang-an-library',
      'long-bridge',
    ])
    expect(overview.uncheckedSpotIds[0]).toBe('bugao-mountain')
  })

  it('deduplicates repeated records and ignores invalid spot ids', () => {
    const overview = buildCheckinOverview(
      [
        { spotId: 'youth-square' },
        { spotId: 'youth-square' },
        { spotId: 'missing-spot' },
      ],
      guideDemoData.spots,
    )

    expect(overview.checkedCount).toBe(1)
    expect(overview.uncheckedCount).toBe(8)
  })

  it('previews a new check-in as 4/9 without mutating source mocks', () => {
    const recordsBefore = JSON.stringify(recordsDemoData.records)
    const spotsBefore = JSON.stringify(guideDemoData.spots)
    const progress = buildDemoCheckinProgress(
      recordsDemoData.records,
      guideDemoData.spots,
      'bugao-mountain',
    )

    expect(progress).toEqual({ checkedCount: 4, totalCount: 9 })
    expect(JSON.stringify(recordsDemoData.records)).toBe(recordsBefore)
    expect(JSON.stringify(guideDemoData.spots)).toBe(spotsBefore)
  })

  it('keeps routes and related spots inside the official nine-spot set', () => {
    const validSpotIds = new Set(guideDemoData.spots.map((spot) => spot.id))

    expect(guideDemoData.route.spotIds).toHaveLength(9)
    guideDemoData.route.spotIds.forEach((spotId) => expect(validSpotIds.has(spotId)).toBe(true))
    guideDemoData.spots.forEach((spot) => {
      spot.relatedSpotIds.forEach((spotId) => expect(validSpotIds.has(spotId)).toBe(true))
    })
  })
})
