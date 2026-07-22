import { describe, expect, it } from 'vitest'
import { guideDemoData } from '../guide'
import { buildProfileStats, profileDemoData } from '../profile'
import { recordsDemoData } from '../records'

describe('profile demo statistics', () => {
  it('keeps only feedback and device information in the service list', () => {
    expect(profileDemoData.serviceItems.map((item) => item.id)).toEqual([
      'feedback',
      'about-device',
    ])
  })

  it('derives the current 3/9 overview without hardcoded totals', () => {
    const stats = buildProfileStats(recordsDemoData.records, guideDemoData.spots)

    expect(stats).toEqual({
      checkedCount: 3,
      totalCount: 9,
      uncheckedCount: 6,
      completionRate: 33,
      digitalCardCount: 3,
    })
  })

  it('deduplicates repeated spot ids and filters invalid records', () => {
    const stats = buildProfileStats(
      [
        { spotId: 'youth-square' },
        { spotId: 'youth-square' },
        { spotId: 'not-a-guide-spot' },
      ],
      guideDemoData.spots,
    )

    expect(stats.checkedCount).toBe(1)
    expect(stats.uncheckedCount).toBe(8)
    expect(stats.digitalCardCount).toBe(1)
  })

  it('returns a safe empty-record state', () => {
    const stats = buildProfileStats([], guideDemoData.spots)

    expect(stats.checkedCount).toBe(0)
    expect(stats.totalCount).toBe(9)
    expect(stats.uncheckedCount).toBe(9)
    expect(stats.completionRate).toBe(0)
    expect(stats.digitalCardCount).toBe(0)
  })

  it('does not mutate record or spot inputs', () => {
    const recordsBefore = JSON.stringify(recordsDemoData.records)
    const spotsBefore = JSON.stringify(guideDemoData.spots)

    buildProfileStats(recordsDemoData.records, guideDemoData.spots)

    expect(JSON.stringify(recordsDemoData.records)).toBe(recordsBefore)
    expect(JSON.stringify(guideDemoData.spots)).toBe(spotsBefore)
  })
})
