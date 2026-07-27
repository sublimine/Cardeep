// Shared session-level cache for GET /market/price-position/{ulid} (K9). Consumes
// 01-market-intelligence's M2 endpoint — never re-derives a median (00-MASTER.md
// C-1). VehicleTable's lazy row badge and the "Mercado" screen's fleet-wide
// distribution both read through this ONE cache so a vehicle's position is never
// fetched twice in the same session (03-garage-fleet F4).
import { useEffect, useState } from 'react'
import { cardeep, type PricePosition } from '../../api/cardeep'

const cache = new Map<string, PricePosition>()
const inflight = new Map<string, Promise<PricePosition>>()

export function getCachedPricePosition(ulid: string): PricePosition | undefined {
  return cache.get(ulid)
}

export function fetchPricePosition(ulid: string): Promise<PricePosition> {
  const cached = cache.get(ulid)
  if (cached) return Promise.resolve(cached)
  const pending = inflight.get(ulid)
  if (pending) return pending
  const p = cardeep.marketPricePosition(ulid).then(data => {
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

/** Lazy per-vehicle fetch, cached — null while loading/unresolved. Never throws:
 * absence of a computable position (no run yet, segment below MIN_COHORT_N) is a
 * legitimate T1-honest state, not an error worth surfacing on a table badge. */
export function usePricePositionBadge(ulid: string): PricePosition | null {
  const [data, setData] = useState<PricePosition | null>(() => getCachedPricePosition(ulid) ?? null)
  useEffect(() => {
    if (data !== null) return
    let live = true
    fetchPricePosition(ulid).then(d => { if (live) setData(d) }).catch(() => {})
    return () => { live = false }
  }, [ulid, data])
  return data
}
