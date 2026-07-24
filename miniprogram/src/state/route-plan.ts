import { reactive, readonly } from 'vue'
import { guideDemoData } from '../mocks/guide'

export interface RoutePlanState {
  readonly addedSpotIds: readonly string[]
}

const validSpotIds = new Set<string>(guideDemoData.spots.map((spot) => spot.id))

const mutableRoutePlanState = reactive<{
  addedSpotIds: string[]
}>({
  addedSpotIds: [],
})

export const routePlanState = readonly(mutableRoutePlanState) as RoutePlanState

export function addSpotToRoute(spotId: string): boolean {
  if (!validSpotIds.has(spotId) || mutableRoutePlanState.addedSpotIds.includes(spotId)) {
    return false
  }

  mutableRoutePlanState.addedSpotIds = [...mutableRoutePlanState.addedSpotIds, spotId]
  return true
}

export function removeSpotFromRoute(spotId: string): boolean {
  if (!mutableRoutePlanState.addedSpotIds.includes(spotId)) return false
  mutableRoutePlanState.addedSpotIds = mutableRoutePlanState.addedSpotIds.filter(
    (item) => item !== spotId,
  )
  return true
}

export function isSpotInRoute(spotId: string): boolean {
  return mutableRoutePlanState.addedSpotIds.includes(spotId)
}

export function getAddedRouteSpotIds(): readonly string[] {
  return [...mutableRoutePlanState.addedSpotIds]
}

export function clearAddedRouteSpots() {
  mutableRoutePlanState.addedSpotIds = []
}
