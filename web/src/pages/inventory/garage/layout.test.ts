/**
 * CARDEEP Garage — layout.ts self-verification module.
 * Same convention as `pages/terminal/indicators.test.ts` and
 * `pages/inventory/derive.test.ts`: no external test runner.
 */
import type { VehicleListItem } from '../../../api/cardeep'
import type { MakeGroup } from '../derive'
import { computeGarageLayout, facingAngle, MAX_ROWS } from './layout'

export interface CheckResult {
  name: string
  pass: boolean
  detail: string
}

function check(name: string, condition: boolean, detail: string): CheckResult {
  return { name, pass: condition, detail }
}

function makeVehicle(ulid: string, make: string): VehicleListItem {
  return {
    vehicle_ulid: ulid, deep_link: 'https://x', title: `${make} test`, make, model: 'X',
    year: 2020, km: 1000, price: 10000, currency: 'EUR', fuel: 'Diésel', transmission: 'Manual',
    photo_url: null, status: 'available',
    first_seen: '2026-01-01T00:00:00Z', last_seen: '2026-01-01T00:00:00Z',
  }
}

function makeGroup(make: string, count: number): MakeGroup {
  return { make, vehicles: Array.from({ length: count }, (_, i) => makeVehicle(`${make}-${i}`, make)) }
}

function checkEmpty(): CheckResult[] {
  const layout = computeGarageLayout([])
  return [
    check('computeGarageLayout([]) returns no cards, no labels', layout.cards.length === 0 && layout.labels.length === 0, `got ${layout.cards.length} cards, ${layout.labels.length} labels`),
    check('computeGarageLayout([]) returns a finite positive radius', Number.isFinite(layout.radius) && layout.radius > 0, `got ${layout.radius}`),
  ]
}

function checkAllVehiclesPlaced(): CheckResult[] {
  const results: CheckResult[] = []
  const groups = [makeGroup('Ford', 57), makeGroup('SEAT', 20), makeGroup('BMW', 3)]
  const total = groups.reduce((s, g) => s + g.vehicles.length, 0)
  const layout = computeGarageLayout(groups)

  results.push(check('every vehicle across all groups gets exactly one card', layout.cards.length === total, `got ${layout.cards.length}, expected ${total}`))
  results.push(check('one pavilion label per group', layout.labels.length === groups.length, `got ${layout.labels.length}`))

  const placedUlids = new Set(layout.cards.map(c => c.vehicle.vehicle_ulid))
  const allUlids = groups.flatMap(g => g.vehicles.map(v => v.vehicle_ulid))
  results.push(check('no vehicle is dropped or duplicated', placedUlids.size === allUlids.length && allUlids.every(u => placedUlids.has(u)), `placed ${placedUlids.size}, expected ${allUlids.length}`))

  return results
}

function checkNoOverlap(): CheckResult[] {
  const results: CheckResult[] = []
  const groups = [makeGroup('Ford', 57), makeGroup('SEAT', 20), makeGroup('BMW', 12), makeGroup('Fiat', 8)]
  const layout = computeGarageLayout(groups)

  // No two cards occupy the identical (x, y, z) — the hard floor for "no overlap".
  const seen = new Set<string>()
  let duplicates = 0
  for (const c of layout.cards) {
    const key = `${c.x.toFixed(4)},${c.y.toFixed(4)},${c.z.toFixed(4)}`
    if (seen.has(key)) duplicates++
    seen.add(key)
  }
  results.push(check('no two cards share the exact same position', duplicates === 0, `${duplicates} exact-position collisions`))

  // Rows never exceed MAX_ROWS within a column (height stays bounded).
  const maxY = Math.max(...layout.cards.map(c => c.y))
  const expectedMaxY = (MAX_ROWS - 1) * 1.55 // (CARD_H + CARD_GAP), approx
  results.push(check('card height never exceeds MAX_ROWS worth of stacking', maxY <= expectedMaxY + 0.01, `max y=${maxY}, expected <= ~${expectedMaxY}`))

  return results
}

function checkFitsLargeFleet(): CheckResult[] {
  const results: CheckResult[] = []
  // Mirrors the real GYATA fleet shape: ~9 makes, 468 total, one dominant make.
  const groups = [
    makeGroup('Ford', 220), makeGroup('Fiat', 90), makeGroup('SEAT', 55),
    makeGroup('BMW', 40), makeGroup('DS Automobiles', 25), makeGroup('Citroen', 18),
    makeGroup('Peugeot', 12), makeGroup('Renault', 6), makeGroup('Skoda', 2),
  ]
  const total = groups.reduce((s, g) => s + g.vehicles.length, 0)
  const start = Date.now()
  const layout = computeGarageLayout(groups)
  const elapsedMs = Date.now() - start

  results.push(check('468-vehicle layout places every card', layout.cards.length === total, `got ${layout.cards.length}, expected ${total}`))
  results.push(check('468-vehicle layout computes in well under a frame budget', elapsedMs < 100, `took ${elapsedMs}ms`))
  results.push(check('radius grows to accommodate a larger fleet, never fixed/tiny', layout.radius > 15, `got radius=${layout.radius}`))

  return results
}

function checkOrderWithinPavilion(): CheckResult[] {
  const group = makeGroup('Ford', 14) // 3 columns of up to 6 rows
  const layout = computeGarageLayout([group])
  // Vehicle at index i must land at column floor(i/MAX_ROWS), row i%MAX_ROWS —
  // verify first and 7th (start of column 2) land at the expected row/column.
  const first = layout.cards[0]
  const seventh = layout.cards[6] // first vehicle of the second column (row 0 again)
  return [
    check('first vehicle in a pavilion sits at row 0 (y=0)', first.y === 0, `got y=${first.y}`),
    check('7th vehicle (start of column 2) also sits at row 0', seventh.y === 0, `got y=${seventh.y}`),
    check('7th vehicle is NOT at the same (x,z) as the 1st (different column)', first.x !== seventh.x || first.z !== seventh.z, 'columns collapsed onto each other'),
  ]
}

function checkFacingAngle(): CheckResult[] {
  const results: CheckResult[] = []
  // facingAngle should be a pure, deterministic function of theta.
  const a = facingAngle(0)
  const b = facingAngle(0)
  results.push(check('facingAngle is deterministic', a === b, `${a} !== ${b}`))
  results.push(check('facingAngle returns a finite number for any theta', Number.isFinite(facingAngle(Math.PI * 3.7)), 'got non-finite'))
  return results
}

export function runLayoutChecks(): CheckResult[] {
  return [
    ...checkEmpty(),
    ...checkAllVehiclesPlaced(),
    ...checkNoOverlap(),
    ...checkFitsLargeFleet(),
    ...checkOrderWithinPavilion(),
    ...checkFacingAngle(),
  ]
}

export function printLayoutChecks(): void {
  const results = runLayoutChecks()
  let pass = 0, fail = 0
  for (const r of results) {
    if (r.pass) { pass++; console.log(`  PASS  ${r.name}`) }
    else { fail++; console.error(`  FAIL  ${r.name} — ${r.detail}`) }
  }
  console.log(`\n${pass} passed, ${fail} failed out of ${results.length} checks`)
}
