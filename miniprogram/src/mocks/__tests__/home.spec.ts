import { describe, expect, it } from 'vitest'
import { guideDemoData } from '../guide'
import { homeDemoData } from '../home'
import { chunkItems } from '../../utils/home-scenery'

describe('home entry configuration', () => {
  it('keeps exactly five non-duplicated middle feature entries', () => {
    expect(homeDemoData.features.map((feature) => feature.id)).toEqual([
      'guide',
      'records',
      'binding',
      'recommend',
      'materials',
    ])
  })

  it('keeps AI and profile only in the bottom navigation', () => {
    const featureIds: readonly string[] = homeDemoData.features.map((feature) => feature.id)
    expect(featureIds).not.toContain('ai')
    expect(featureIds).not.toContain('profile')
    expect(homeDemoData.navigation.map((item) => item.id)).toEqual(['home', 'ai', 'profile'])
  })

  it('reuses the existing binding image', () => {
    expect(homeDemoData.features.find((feature) => feature.id === 'binding')?.image).toBe(
      '/static/home/feature-binding.png',
    )
  })

  it('uses the nine formal guide covers as the scenery source', () => {
    expect('scenery' in homeDemoData).toBe(false)
    expect(guideDemoData.spots).toHaveLength(9)
    expect(guideDemoData.spots.every((spot) => spot.coverImage.startsWith('/static/guide/spots/'))).toBe(true)
    expect(guideDemoData.spots.map((spot) => spot.name)).not.toContain('明远湖')
  })

  it('groups nine scenery spots into stable two-card swiper pages', () => {
    const source = [...guideDemoData.spots]
    const pages = chunkItems(source, 2)

    expect(pages).toHaveLength(5)
    expect(pages.map((page) => page.length)).toEqual([2, 2, 2, 2, 1])
    expect(pages.flat().map((spot) => spot.id)).toEqual(source.map((spot) => spot.id))
    expect(source).toEqual(guideDemoData.spots)
  })
})
