// Bounded set of vehicles allowed to render a real DOM <img> overlay
// (drei <Html transform>) in the 3D garage. Recomputed on demand — camera
// 'end' events and hover/selection changes — never per-frame, so it costs
// nothing during smooth orbiting.
import { useCallback, useState } from 'react'
import type { CardPlacement } from './layout'
import { PHOTO_OVERLAY_BUDGET } from '../config'

export function usePhotoBudget(cards: readonly CardPlacement[]) {
  const [eligible, setEligible] = useState<Set<string>>(new Set())

  const recompute = useCallback((camera: { x: number; y: number; z: number }, pinned: readonly string[]) => {
    const withDist = cards.map(c => ({
      ulid: c.vehicle.vehicle_ulid,
      distSq: (c.x - camera.x) ** 2 + (c.y - camera.y) ** 2 + (c.z - camera.z) ** 2,
    }))
    withDist.sort((a, b) => a.distSq - b.distSq)
    const nearest = withDist.slice(0, PHOTO_OVERLAY_BUDGET).map(d => d.ulid)
    setEligible(new Set([...nearest, ...pinned]))
  }, [cards])

  return { eligible, recompute }
}
