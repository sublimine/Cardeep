// 08-forum-community F6: price sparkline for VehicleAnchorCard (carta §4.3).
// "Se dibuja SOLO con >=2 puntos reales. Con 1: precio plano sin sparkline. Con 0:
// nada. Prohibido interpolar, suavizar o inventar puntos." — real vehicle_event history
// only, via the SAME endpoint /vehicles/{ulid}/history already served by vehicles.py.
import { useEffect, useState } from 'react'
import { cardeep } from '../../api/cardeep'

interface PricePoint { t: number; price: number }

function extractPricePoints(events: { event_type: string; new_value: unknown; observed_at: string }[]): PricePoint[] {
  return events
    .filter((e) => e.event_type === 'NEW' || e.event_type === 'PRICE_CHANGE')
    .map((e) => {
      const v = e.new_value as { price?: number } | null
      return v?.price != null ? { t: new Date(e.observed_at).getTime(), price: v.price } : null
    })
    .filter((p): p is PricePoint => p !== null)
    .sort((a, b) => a.t - b.t)
}

export function PriceSparkline({ vehicleUlid }: { vehicleUlid: string }) {
  const [points, setPoints] = useState<PricePoint[] | null>(null)

  useEffect(() => {
    let cancelled = false
    cardeep.vehicleHistory(vehicleUlid, 1, 200)
      .then((batch) => { if (!cancelled) setPoints(extractPricePoints(batch.items)) })
      .catch(() => { if (!cancelled) setPoints([]) })
    return () => { cancelled = true }
  }, [vehicleUlid])

  if (points === null || points.length < 2) return null // 0 or 1 point: nothing drawn, never interpolated

  const width = 72
  const height = 20
  const prices = points.map((p) => p.price)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  const step = width / (points.length - 1)
  const path = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${(i * step).toFixed(1)} ${(height - ((p.price - min) / range) * height).toFixed(1)}`)
    .join(' ')
  const trendUp = points[points.length - 1].price >= points[0].price
  const color = trendUp ? '#ef4444' : '#10b981' // price went up = bad for buyer (red), down = good (green)

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-label="Histórico de precio real">
      <path d={path} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
