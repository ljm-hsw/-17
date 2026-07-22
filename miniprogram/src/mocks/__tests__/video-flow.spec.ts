import { describe, expect, it } from 'vitest'
import { buildJourneySpots } from '../ai-generation'
import { guideDemoData } from '../guide'
import { buildJourneyMaterials } from '../materials'
import { recordsDemoData } from '../records'

describe('journey material foundations', () => {
  it('keeps journey routes within the nine formal spots and excludes Mingyuan Lake', () => {
    const spots = buildJourneySpots(recordsDemoData.records, guideDemoData.spots)
    expect(spots.map((spot) => spot.name)).toEqual(['青春广场', '长桥', '江安图书馆'])
    expect(spots.map((spot) => spot.name)).not.toContain('明远湖')
  })

  it('uses a textual placeholder when local journey images are absent', () => {
    const items = buildJourneyMaterials(recordsDemoData.records, guideDemoData.spots, [])
    expect(items).toHaveLength(3)
    expect(items.every((item) => item.image === undefined)).toBe(true)
  })
})
