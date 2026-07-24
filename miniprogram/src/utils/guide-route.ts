import type { GuideSpot } from '../types/guide'
import type { CheckinRecordSource } from '../types/records'

export function resolveGuideRouteSpots(
  routeSpotIds: readonly string[],
  spots: readonly GuideSpot[],
): readonly GuideSpot[] {
  const spotById = new Map(spots.map((spot) => [spot.id, spot]))
  const seen = new Set<string>()

  return routeSpotIds.flatMap((spotId) => {
    if (seen.has(spotId)) return []
    const spot = spotById.get(spotId)
    if (!spot) return []
    seen.add(spotId)
    return [spot]
  })
}

export function resolveCheckedRouteSpotIds(
  routeSpots: readonly GuideSpot[],
  records: readonly CheckinRecordSource[],
): readonly string[] {
  const routeSpotIds = new Set(routeSpots.map((spot) => spot.id))
  const checked = new Set<string>()
  records.forEach((record) => {
    if (routeSpotIds.has(record.spotId)) checked.add(record.spotId)
  })
  return routeSpots.map((spot) => spot.id).filter((spotId) => checked.has(spotId))
}

export function resolveCheckedSpotIdsInRecordOrder(
  records: readonly CheckinRecordSource[],
  spots: readonly GuideSpot[],
): readonly string[] {
  const validSpotIds = new Set(spots.map((spot) => spot.id))
  const seen = new Set<string>()

  return records.flatMap((record) => {
    const spotId = record.spotId.trim()
    if (!validSpotIds.has(spotId) || seen.has(spotId)) return []
    seen.add(spotId)
    return [spotId]
  })
}

export function resolveCurrentRouteSpots(
  records: readonly CheckinRecordSource[],
  addedSpotIds: readonly string[],
  spots: readonly GuideSpot[],
): readonly GuideSpot[] {
  const spotById = new Map(spots.map((spot) => [spot.id, spot]))
  const checkedSpotIds = resolveCheckedSpotIdsInRecordOrder(records, spots)
  const checkedSpotIdSet = new Set(checkedSpotIds)
  const seenAddedSpotIds = new Set<string>()
  const validAddedSpotIds = addedSpotIds.filter((spotId) => {
    if (!spotById.has(spotId) || checkedSpotIdSet.has(spotId) || seenAddedSpotIds.has(spotId)) {
      return false
    }
    seenAddedSpotIds.add(spotId)
    return true
  })

  return [...checkedSpotIds, ...validAddedSpotIds]
    .map((spotId) => spotById.get(spotId))
    .filter((spot): spot is GuideSpot => Boolean(spot))
}
