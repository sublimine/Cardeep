// Shared session-level cache for GET /vehicles/{ulid}/platforms (K8). One module-level
// Map so VehicleTable's lazy row badge and VehicleDetailModal's "plataformas" tab never
// issue two independent fetches for the same vehicle_ulid (03-garage-fleet F2).
import { useEffect, useState } from 'react'
import { cardeep, type VehiclePlatforms } from '../../api/cardeep'

const cache = new Map<string, VehiclePlatforms>()
const inflight = new Map<string, Promise<VehiclePlatforms>>()

export function getCachedPlatforms(ulid: string): VehiclePlatforms | undefined {
  return cache.get(ulid)
}

export function fetchPlatforms(ulid: string): Promise<VehiclePlatforms> {
  const cached = cache.get(ulid)
  if (cached) return Promise.resolve(cached)
  const pending = inflight.get(ulid)
  if (pending) return pending
  const p = cardeep.vehiclePlatforms(ulid).then(data => {
    cache.set(ulid, data)
    inflight.delete(ulid)
    return data
  }).catch(err => {
    inflight.delete(ulid)
    throw err
  })
  inflight.set(ulid, p)
  return p
}

/** Lazy per-vehicle fetch, cached — null while loading/unresolved, never throws (silent-fail
 * badge: absence of platform data is not worth surfacing an error for a decorative indicator). */
export function usePlatformBadge(ulid: string): VehiclePlatforms | null {
  const [data, setData] = useState<VehiclePlatforms | null>(() => getCachedPlatforms(ulid) ?? null)
  useEffect(() => {
    if (data !== null) return
    let live = true
    fetchPlatforms(ulid).then(d => { if (live) setData(d) }).catch(() => {})
    return () => { live = false }
  }, [ulid, data])
  return data
}
