// Pure positioning math for the 3D garage — a ring of curved "pavilions", one
// per make, each a curved wall of cards facing the center. No React, no
// three.js import here: this is plain trigonometry, unit-testable in
// isolation from any renderer.
import type { VehicleListItem } from '../../../api/cardeep'
import type { MakeGroup } from '../derive'

export const MAX_ROWS = 6
export const CARD_W = 1.6
export const CARD_H = 1.2
export const CARD_GAP = 0.35
export const PAVILION_GAP_DEG = 8
export const MIN_RADIUS = 8

export interface CardPlacement {
  vehicle: VehicleListItem
  x: number
  y: number
  z: number
  /** Y-axis rotation (radians) so the card's front face points toward the ring center. */
  rotationY: number
  make: string
}

export interface PavilionLabel {
  make: string
  count: number
  x: number
  y: number
  z: number
}

export interface GarageLayout {
  radius: number
  cards: CardPlacement[]
  labels: PavilionLabel[]
}

/** Y-rotation so a card sitting at angle `theta` on the ring faces the origin (derivation in module comment below). */
export function facingAngle(theta: number): number {
  return -theta - Math.PI / 2
}

/**
 * Lays out every vehicle from `groups` (ordered largest-first, per
 * `groupByMake`) around a ring, one curved pavilion per make. Deterministic —
 * same input always produces the same output, so it's a pure function of the
 * dataset and safe to memoize.
 */
export function computeGarageLayout(groups: readonly MakeGroup[]): GarageLayout {
  if (groups.length === 0) return { radius: MIN_RADIUS, cards: [], labels: [] }

  const pavilions = groups.map(g => ({
    make: g.make,
    vehicles: g.vehicles,
    cols: Math.max(1, Math.ceil(g.vehicles.length / MAX_ROWS)),
  }))

  const totalCols = pavilions.reduce((s, p) => s + p.cols, 0)
  const gapTotalDeg = PAVILION_GAP_DEG * pavilions.length
  const availableDeg = Math.max(60, 360 - gapTotalDeg) // never collapse below a 60° usable arc
  const degPerCol = availableDeg / totalCols

  // Radius large enough that adjacent columns (at CARD_W + CARD_GAP apart)
  // don't need more angular width than degPerCol allows at that radius.
  const neededCircumference = totalCols * (CARD_W + CARD_GAP) * (360 / availableDeg)
  const radius = Math.max(MIN_RADIUS, neededCircumference / (2 * Math.PI))

  const cards: CardPlacement[] = []
  const labels: PavilionLabel[] = []
  let cursorDeg = -90 // start roughly facing the initial camera pose

  for (const pavilion of pavilions) {
    const widthDeg = pavilion.cols * degPerCol
    const startDeg = cursorDeg

    for (let i = 0; i < pavilion.vehicles.length; i++) {
      const col = Math.floor(i / MAX_ROWS)
      const row = i % MAX_ROWS
      const colAngleDeg = startDeg + (col + 0.5) * degPerCol
      const theta = (colAngleDeg * Math.PI) / 180
      cards.push({
        vehicle: pavilion.vehicles[i],
        x: radius * Math.cos(theta),
        y: row * (CARD_H + CARD_GAP),
        z: radius * Math.sin(theta),
        rotationY: facingAngle(theta),
        make: pavilion.make,
      })
    }

    const midDeg = startDeg + widthDeg / 2
    const midTheta = (midDeg * Math.PI) / 180
    labels.push({
      make: pavilion.make,
      count: pavilion.vehicles.length,
      x: radius * Math.cos(midTheta),
      y: MAX_ROWS * (CARD_H + CARD_GAP) + 0.6,
      z: radius * Math.sin(midTheta),
    })

    cursorDeg += widthDeg + PAVILION_GAP_DEG
  }

  return { radius, cards, labels }
}
