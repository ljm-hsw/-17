import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { guideDemoData } from '../guide'
import { recordsDemoData } from '../records'
import {
  addSpotToRoute,
  clearAddedRouteSpots,
  getAddedRouteSpotIds,
  removeSpotFromRoute,
} from '../../state/route-plan'
import {
  addVideoDemoCheckin,
  mergeVideoDemoRecordSources,
  resetVideoDemoState,
} from '../../state/video-demo'
import { resolveCurrentRouteSpots } from '../../utils/guide-route'

const srcRoot = resolve(process.cwd(), 'src')
const readSource = (relativePath: string) =>
  readFileSync(resolve(srcRoot, relativePath), 'utf8')

function resolveCurrentRoute() {
  return resolveCurrentRouteSpots(
    mergeVideoDemoRecordSources(recordsDemoData.records),
    getAddedRouteSpotIds(),
    guideDemoData.spots,
  )
}

describe('current guide route plan', () => {
  beforeEach(() => {
    clearAddedRouteSpots()
    resetVideoDemoState()
  })

  afterEach(() => {
    clearAddedRouteSpots()
    resetVideoDemoState()
  })

  it('keeps the nine calibrated native-map markers intact', () => {
    expect(guideDemoData.spots).toHaveLength(9)
    expect(guideDemoData.spots.map((spot) => spot.markerId)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9])
    expect(guideDemoData.spots.every((spot) => spot.iconPath === '/static/guide/tubiao.png')).toBe(true)
    expect(guideDemoData.spots.map((spot) => [spot.latitude, spot.longitude])).toEqual([
      [30.554531, 103.994836],
      [30.556812, 103.999863],
      [30.555092, 103.997113],
      [30.559115, 103.993583],
      [30.560511, 104.007083],
      [30.557698, 103.99491],
      [30.558487, 104.005793],
      [30.556539, 103.995347],
      [30.556515, 104.001068],
    ])
  })

  it('starts with only the three checked spots in checkin order', () => {
    expect(resolveCurrentRoute().map((spot) => spot.id)).toEqual([
      'youth-square',
      'long-bridge',
      'jiang-an-library',
    ])
    expect(resolveCurrentRoute()).toHaveLength(3)
    expect(resolveCurrentRoute().map((spot) => spot.name)).not.toContain('明远湖')
  })

  it('adds and removes an unchecked spot without selecting every formal spot', () => {
    expect(addSpotToRoute('bugao-mountain')).toBe(true)
    expect(resolveCurrentRoute().map((spot) => spot.id)).toEqual([
      'youth-square',
      'long-bridge',
      'jiang-an-library',
      'bugao-mountain',
    ])
    expect(resolveCurrentRoute()).toHaveLength(4)
    expect(resolveCurrentRoute().map((spot) => spot.id)).not.toContain('gymnasium')

    expect(removeSpotFromRoute('bugao-mountain')).toBe(true)
    expect(resolveCurrentRoute()).toHaveLength(3)
  })

  it('rejects invalid ids and deduplicates repeated additions', () => {
    expect(addSpotToRoute('bugao-mountain')).toBe(true)
    expect(addSpotToRoute('bugao-mountain')).toBe(false)
    expect(addSpotToRoute('mingyuan-lake')).toBe(false)
    expect(getAddedRouteSpotIds()).toEqual(['bugao-mountain'])
  })

  it('deduplicates a manually added spot after its temporary checkin and marks 4/9', () => {
    const recordsBefore = JSON.stringify(recordsDemoData.records)
    addSpotToRoute('bugao-mountain')
    addVideoDemoCheckin({
      recordId: 'route-demo-bugao',
      spotId: 'bugao-mountain',
      checkedAt: '2026-07-22T12:00:00+08:00',
      checkedAtLabel: '今天 12:00',
      methodLabel: '点位打卡 · 演示',
      poseId: 'victory',
      isDemo: true,
    })

    const route = resolveCurrentRoute()
    expect(route).toHaveLength(4)
    expect(route.filter((spot) => spot.id === 'bugao-mountain')).toHaveLength(1)
    expect(mergeVideoDemoRecordSources(recordsDemoData.records)).toHaveLength(4)
    expect(JSON.stringify(recordsDemoData.records)).toBe(recordsBefore)
  })

  it('does not pass polyline or include-points to the native map', () => {
    const campusMap = readSource('components/guide/CampusMap.vue')
    const guidePage = readSource('pages/guide/index.vue')
    const routeList = readSource('components/guide/RouteOverviewList.vue')

    expect(campusMap).not.toContain(':polyline=')
    expect(campusMap).not.toContain(':include-points=')
    expect(guidePage).not.toContain('guideDemoData.route.spotIds')
    expect(routeList).not.toContain('推荐游览顺序')
    expect(routeList).not.toContain('formatSequence')
  })
})
