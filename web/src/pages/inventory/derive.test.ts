/**
 * CARDEEP Inventory — derive.ts self-verification module.
 * Same convention as `pages/terminal/indicators.test.ts`: no external test
 * runner. Call `printDeriveChecks()` from a browser console or a Node script.
 */
import type { VehicleListItem } from '../../api/cardeep'
import {
  daysInStock, hostnameOf, formatPrice, formatKm, relativeDate,
  buildChips, applyFilters, applySort, groupByMake, stockStats, toCsv,
  facetCounts, facetOptions, numericBounds,
  EMPTY_FILTERS,
} from './derive'

export interface CheckResult {
  name: string
  pass: boolean
  detail: string
}

function check(name: string, condition: boolean, detail: string): CheckResult {
  return { name, pass: condition, detail }
}

const NOW = new Date('2026-07-16T12:00:00Z')

function iso(daysAgo: number): string {
  return new Date(NOW.getTime() - daysAgo * 86_400_000).toISOString()
}

function makeVehicle(overrides: Partial<VehicleListItem>): VehicleListItem {
  return {
    vehicle_ulid: 'V1',
    deep_link: 'https://example.com/listing/1',
    title: 'Test Car',
    make: 'Ford',
    model: 'Focus',
    year: 2020,
    km: 50_000,
    price: 15_000,
    currency: 'EUR',
    fuel: 'Diésel',
    transmission: 'Manual',
    photo_url: 'https://example.com/photo.jpg',
    status: 'available',
    first_seen: iso(10),
    last_seen: iso(1),
    ...overrides,
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// daysInStock
// ─────────────────────────────────────────────────────────────────────────────

function checkDaysInStock(): CheckResult[] {
  const results: CheckResult[] = []

  results.push(check(
    'daysInStock: 10 days ago = 10',
    daysInStock(iso(10), NOW) === 10,
    `got ${daysInStock(iso(10), NOW)}`,
  ))
  results.push(check(
    'daysInStock: today = 0',
    daysInStock(iso(0), NOW) === 0,
    `got ${daysInStock(iso(0), NOW)}`,
  ))
  results.push(check(
    'daysInStock: future timestamp clamps to 0, never negative',
    daysInStock(iso(-5), NOW) === 0,
    `got ${daysInStock(iso(-5), NOW)}`,
  ))
  results.push(check(
    'daysInStock: invalid date returns 0 without throwing',
    daysInStock('not-a-date', NOW) === 0,
    `got ${daysInStock('not-a-date', NOW)}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// formatters
// ─────────────────────────────────────────────────────────────────────────────

function checkFormatters(): CheckResult[] {
  const results: CheckResult[] = []

  results.push(check(
    'hostnameOf strips www.',
    hostnameOf('https://www.autocasion.com/x') === 'autocasion.com',
    `got ${hostnameOf('https://www.autocasion.com/x')}`,
  ))
  results.push(check(
    'hostnameOf passes through on malformed URL without throwing',
    hostnameOf('not a url') === 'not a url',
    `got ${hostnameOf('not a url')}`,
  ))
  results.push(check(
    'formatPrice(null) = em dash',
    formatPrice(null, 'EUR') === '—',
    `got ${formatPrice(null, 'EUR')}`,
  ))
  results.push(check(
    'formatPrice formats a real EUR amount',
    /15\D?000/.test(formatPrice(15000, 'EUR')),
    `got ${formatPrice(15000, 'EUR')}`,
  ))
  results.push(check(
    'formatKm(null) = em dash',
    formatKm(null) === '—',
    `got ${formatKm(null)}`,
  ))
  results.push(check(
    'relativeDate: today = "hoy"',
    relativeDate(iso(0), NOW) === 'hoy',
    `got ${relativeDate(iso(0), NOW)}`,
  ))
  results.push(check(
    'relativeDate: 1 day = "ayer"',
    relativeDate(iso(1), NOW) === 'ayer',
    `got ${relativeDate(iso(1), NOW)}`,
  ))
  results.push(check(
    'relativeDate: 400 days = years bucket',
    relativeDate(iso(400), NOW).includes('año'),
    `got ${relativeDate(iso(400), NOW)}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// buildChips — must never fabricate a count
// ─────────────────────────────────────────────────────────────────────────────

function checkChips(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: 'a', first_seen: iso(2) }),          // nuevos
    makeVehicle({ vehicle_ulid: 'b', first_seen: iso(120) }),        // stale
    makeVehicle({ vehicle_ulid: 'c', photo_url: null }),             // sin_foto
    makeVehicle({ vehicle_ulid: 'd', price: null }),                 // sin_precio
    makeVehicle({ vehicle_ulid: 'e', first_seen: iso(30) }),         // none of the above
  ]
  const chips = buildChips(fleet, NOW)
  const byKey = Object.fromEntries(chips.map(c => [c.key, c.count]))

  results.push(check(
    'buildChips: nuevos count = 1',
    byKey.nuevos === 1,
    `got ${JSON.stringify(byKey)}`,
  ))
  results.push(check(
    'buildChips: stale count = 1',
    byKey.stale === 1,
    `got ${JSON.stringify(byKey)}`,
  ))
  results.push(check(
    'buildChips: sin_foto count = 1',
    byKey.sin_foto === 1,
    `got ${JSON.stringify(byKey)}`,
  ))
  results.push(check(
    'buildChips: sin_precio count = 1',
    byKey.sin_precio === 1,
    `got ${JSON.stringify(byKey)}`,
  ))
  results.push(check(
    'buildChips: zero-count chips are omitted entirely, not shown as 0',
    buildChips([makeVehicle({ first_seen: iso(30) })], NOW).length === 0,
    `got ${JSON.stringify(buildChips([makeVehicle({ first_seen: iso(30) })], NOW))}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// applyFilters
// ─────────────────────────────────────────────────────────────────────────────

function checkFilters(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: 'ford1', make: 'Ford', price: 10_000, fuel: 'Diésel' }),
    makeVehicle({ vehicle_ulid: 'seat1', make: 'SEAT', price: 20_000, fuel: 'Gasolina' }),
    makeVehicle({ vehicle_ulid: 'ibiza', make: 'SEAT', model: 'Ibérica Ibiza', price: 8_000 }),
  ]

  results.push(check(
    'applyFilters: make filter isolates matching rows',
    applyFilters(fleet, { ...EMPTY_FILTERS, makes: ['Ford'] }, NOW).length === 1,
    `got ${applyFilters(fleet, { ...EMPTY_FILTERS, makes: ['Ford'] }, NOW).length}`,
  ))
  results.push(check(
    'applyFilters: price range excludes out-of-range rows',
    applyFilters(fleet, { ...EMPTY_FILTERS, priceMin: 9_000, priceMax: 15_000 }, NOW).length === 1,
    `got ${applyFilters(fleet, { ...EMPTY_FILTERS, priceMin: 9_000, priceMax: 15_000 }, NOW).map(v => v.vehicle_ulid)}`,
  ))
  results.push(check(
    'applyFilters: search is accent-insensitive and case-insensitive',
    applyFilters(fleet, { ...EMPTY_FILTERS, search: 'iberica' }, NOW).length === 1,
    `got ${applyFilters(fleet, { ...EMPTY_FILTERS, search: 'iberica' }, NOW).length}`,
  ))
  results.push(check(
    'applyFilters: combined make + fuel narrows correctly',
    applyFilters(fleet, { ...EMPTY_FILTERS, makes: ['SEAT'], fuels: ['Gasolina'] }, NOW).length === 1,
    `got ${applyFilters(fleet, { ...EMPTY_FILTERS, makes: ['SEAT'], fuels: ['Gasolina'] }, NOW).length}`,
  ))
  results.push(check(
    'applyFilters: empty filters return everything unchanged',
    applyFilters(fleet, EMPTY_FILTERS, NOW).length === fleet.length,
    `got ${applyFilters(fleet, EMPTY_FILTERS, NOW).length}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// applySort — nulls must never win, in either direction
// ─────────────────────────────────────────────────────────────────────────────

function checkSort(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: 'mid', price: 20_000 }),
    makeVehicle({ vehicle_ulid: 'null', price: null }),
    makeVehicle({ vehicle_ulid: 'low', price: 10_000 }),
    makeVehicle({ vehicle_ulid: 'high', price: 30_000 }),
  ]

  const asc = applySort(fleet, 'precio_asc')
  results.push(check(
    'applySort precio_asc: ascending order, null last',
    asc.map(v => v.vehicle_ulid).join(',') === 'low,mid,high,null',
    `got ${asc.map(v => v.vehicle_ulid).join(',')}`,
  ))

  const desc = applySort(fleet, 'precio_desc')
  results.push(check(
    'applySort precio_desc: descending order, null STILL last (never first)',
    desc.map(v => v.vehicle_ulid).join(',') === 'high,mid,low,null',
    `got ${desc.map(v => v.vehicle_ulid).join(',')}`,
  ))

  results.push(check(
    'applySort does not mutate the input array',
    fleet[0].vehicle_ulid === 'mid',
    `got ${fleet[0].vehicle_ulid}`,
  ))

  const byRecency: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: 'older', first_seen: iso(20) }),
    makeVehicle({ vehicle_ulid: 'newer', first_seen: iso(1) }),
  ]
  results.push(check(
    'applySort recientes: newest first_seen first',
    applySort(byRecency, 'recientes')[0].vehicle_ulid === 'newer',
    `got ${applySort(byRecency, 'recientes')[0].vehicle_ulid}`,
  ))
  results.push(check(
    'applySort antiguos_stock: oldest first_seen first',
    applySort(byRecency, 'antiguos_stock')[0].vehicle_ulid === 'older',
    `got ${applySort(byRecency, 'antiguos_stock')[0].vehicle_ulid}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// groupByMake
// ─────────────────────────────────────────────────────────────────────────────

function checkGroupByMake(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: '1', make: 'Ford' }),
    makeVehicle({ vehicle_ulid: '2', make: 'Ford' }),
    makeVehicle({ vehicle_ulid: '3', make: 'SEAT' }),
    makeVehicle({ vehicle_ulid: '4', make: null }),
  ]
  const groups = groupByMake(fleet)

  results.push(check(
    'groupByMake: largest group first',
    groups[0].make === 'Ford' && groups[0].vehicles.length === 2,
    `got ${JSON.stringify(groups.map(g => [g.make, g.vehicles.length]))}`,
  ))
  results.push(check(
    'groupByMake: null make bucketed as "Sin marca", not dropped',
    groups.some(g => g.make === 'Sin marca' && g.vehicles.length === 1),
    `got ${JSON.stringify(groups.map(g => g.make))}`,
  ))
  results.push(check(
    'groupByMake: total vehicles preserved across groups',
    groups.reduce((s, g) => s + g.vehicles.length, 0) === fleet.length,
    `got ${groups.reduce((s, g) => s + g.vehicles.length, 0)}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// stockStats — nulls excluded from averages, never coerced to 0
// ─────────────────────────────────────────────────────────────────────────────

function checkStockStats(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: '1', price: 10_000, km: 10_000 }),
    makeVehicle({ vehicle_ulid: '2', price: 20_000, km: null }),
    makeVehicle({ vehicle_ulid: '3', price: null, km: 30_000 }),
  ]
  const stats = stockStats(fleet, NOW)

  results.push(check(
    'stockStats: totalValue sums only priced vehicles',
    stats.totalValue === 30_000,
    `got ${stats.totalValue}`,
  ))
  results.push(check(
    'stockStats: pricedCount excludes nulls',
    stats.pricedCount === 2,
    `got ${stats.pricedCount}`,
  ))
  results.push(check(
    'stockStats: avgKm computed only over non-null km',
    stats.avgKm === 20_000,
    `got ${stats.avgKm}`,
  ))
  results.push(check(
    'stockStats: empty fleet returns nulls, not zeros pretending to be data',
    stockStats([], NOW).medianPrice === null && stockStats([], NOW).avgKm === null,
    `got ${JSON.stringify(stockStats([], NOW))}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// facetCounts / facetOptions / numericBounds
// ─────────────────────────────────────────────────────────────────────────────

function checkFacets(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: '1', make: 'Ford', fuel: 'Diésel' }),
    makeVehicle({ vehicle_ulid: '2', make: 'Ford', fuel: 'Gasolina' }),
    makeVehicle({ vehicle_ulid: '3', make: 'SEAT', fuel: 'Diésel' }),
  ]

  results.push(check(
    'facetOptions(make): distinct sorted values across full dataset',
    facetOptions(fleet, 'make').join(',') === 'Ford,SEAT',
    `got ${facetOptions(fleet, 'make').join(',')}`,
  ))

  // With fuel=Diésel active, counting the "make" facet must relax the make
  // filter but KEEP the fuel filter — so SEAT (Diésel) still counts, Ford
  // shows 1 (only its Diésel row), not 2.
  const withFuelFilter = { ...EMPTY_FILTERS, fuels: ['Diésel'] }
  const makeCounts = facetCounts(fleet, withFuelFilter, 'make', NOW)
  results.push(check(
    'facetCounts holds OTHER filters constant while relaxing its own field',
    makeCounts.get('Ford') === 1 && makeCounts.get('SEAT') === 1,
    `got Ford=${makeCounts.get('Ford')} SEAT=${makeCounts.get('SEAT')}`,
  ))

  // Selecting a make and then counting ITS OWN facet must ignore that
  // selection (relaxed), so the count reflects "if I picked this option".
  const withMakeFilter = { ...EMPTY_FILTERS, makes: ['Ford'] }
  const makeCountsRelaxed = facetCounts(fleet, withMakeFilter, 'make', NOW)
  results.push(check(
    'facetCounts relaxes its own field so unselected options keep a real count',
    makeCountsRelaxed.get('SEAT') === 1,
    `got SEAT=${makeCountsRelaxed.get('SEAT')}`,
  ))

  const bounds = numericBounds(fleet, 'year')
  results.push(check(
    'numericBounds returns min/max over non-null values',
    bounds !== null && bounds.min === 2020 && bounds.max === 2020,
    `got ${JSON.stringify(bounds)}`,
  ))
  results.push(check(
    'numericBounds returns null for an empty dataset',
    numericBounds([], 'year') === null,
    `got ${JSON.stringify(numericBounds([], 'year'))}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// toCsv — RFC 4180 escaping
// ─────────────────────────────────────────────────────────────────────────────

function checkCsv(): CheckResult[] {
  const results: CheckResult[] = []

  const fleet: VehicleListItem[] = [
    makeVehicle({ vehicle_ulid: '1', title: 'Car, with comma' }),
    makeVehicle({ vehicle_ulid: '2', title: 'Car "with quotes"' }),
  ]
  const csv = toCsv(fleet, NOW)
  const lines = csv.split('\n')

  results.push(check(
    'toCsv: header row present',
    lines[0].startsWith('vehicle_ulid,'),
    `got ${lines[0]}`,
  ))
  results.push(check(
    'toCsv: comma in field gets quoted',
    lines[1].includes('"Car, with comma"'),
    `got ${lines[1]}`,
  ))
  results.push(check(
    'toCsv: embedded quotes are doubled per RFC 4180',
    lines[2].includes('"Car ""with quotes"""'),
    `got ${lines[2]}`,
  ))
  results.push(check(
    'toCsv: row count = data rows + 1 header',
    lines.length === fleet.length + 1,
    `got ${lines.length}`,
  ))

  return results
}

// ─────────────────────────────────────────────────────────────────────────────
// Public entry point
// ─────────────────────────────────────────────────────────────────────────────

export function runDeriveChecks(): CheckResult[] {
  return [
    ...checkDaysInStock(),
    ...checkFormatters(),
    ...checkChips(),
    ...checkFilters(),
    ...checkSort(),
    ...checkGroupByMake(),
    ...checkStockStats(),
    ...checkFacets(),
    ...checkCsv(),
  ]
}

export function printDeriveChecks(): void {
  const results = runDeriveChecks()
  let pass = 0, fail = 0
  for (const r of results) {
    if (r.pass) { pass++; console.log(`  PASS  ${r.name}`) }
    else { fail++; console.error(`  FAIL  ${r.name} — ${r.detail}`) }
  }
  console.log(`\n${pass} passed, ${fail} failed out of ${results.length} checks`)
}
