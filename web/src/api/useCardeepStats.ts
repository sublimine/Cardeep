import { useEffect, useState } from 'react'
import { cardeep, type Stats } from './cardeep'

export interface MarketCoverage {
  numerator: number
  denominator: number
  coveragePct: number
}

interface LandingStats {
  stats: Stats | null
  coverage: MarketCoverage | null
  loading: boolean
  /** True once the fetch has settled (success or failure) — lets callers show a stable fallback instead of a perpetual skeleton. */
  ready: boolean
}

/**
 * Real censo numbers for the public landing (`/stats` + `/geo/seal`, venta segment).
 * No fabricated figures: on fetch failure `stats`/`coverage` stay null and callers
 * render the last-known-good copy already baked into the page instead of a fake number.
 */
export function useLandingStats(): LandingStats {
  const [stats, setStats] = useState<Stats | null>(null)
  const [coverage, setCoverage] = useState<MarketCoverage | null>(null)
  const [loading, setLoading] = useState(true)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const controller = new AbortController()

    Promise.allSettled([cardeep.stats(controller.signal), cardeep.geoSeal(controller.signal)]).then(
      ([statsResult, sealResult]) => {
        if (controller.signal.aborted) return
        if (statsResult.status === 'fulfilled') setStats(statsResult.value)
        if (sealResult.status === 'fulfilled') {
          const venta = sealResult.value.segments.venta
          if (venta) {
            setCoverage({
              numerator: venta.national.numerator,
              denominator: venta.national.denominator,
              coveragePct: venta.national.coverage_pct,
            })
          }
        }
        setLoading(false)
        setReady(true)
      }
    )

    return () => controller.abort()
  }, [])

  return { stats, coverage, loading, ready }
}
