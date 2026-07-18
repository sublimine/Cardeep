// CARDEEP Inventory — pure data-derivation functions.
//
// No React, no fetch, no Date.now()/Math.random() side effects hidden inside —
// `now` is always passed in explicitly so these stay unit-testable and so a
// single consistent "now" is used across a render pass (chips, sort, stats).
import type { VehicleListItem } from '../../api/cardeep'
import { FRESH_DAYS, STALE_DAYS } from './config'

export type SortKey =
  | 'recientes' | 'antiguos_stock'
  | 'precio_asc' | 'precio_desc'
  | 'km_asc' | 'km_desc'
  | 'anio_desc'

export type ChipKey = 'nuevos' | 'stale' | 'sin_foto' | 'sin_precio'

export interface InventoryFilters {
  makes: string[]
  fuels: string[]
  transmissions: string[]
  yearMin: number | null
  yearMax: number | null
  priceMin: number | null
  priceMax: number | null
  kmMin: number | null
  kmMax: number | null
  search: string
  chip: ChipKey | null
}

export const EMPTY_FILTERS: InventoryFilters = {
  makes: [],
  fuels: [],
  transmissions: [],
  yearMin: null,
  yearMax: null,
  priceMin: null,
  priceMax: null,
  kmMin: null,
  kmMax: null,
  search: '',
  chip: null,
}

export interface ChipDef {
  key: ChipKey
  label: string
  count: number
  color: 'emerald' | 'rose' | 'amber'
}

export interface StockStats {
  count: number
  totalValue: number
  pricedCount: number
  medianPrice: number | null
  avgAgeDays: number | null
  avgKm: number | null
}

const MS_PER_DAY = 1000 * 60 * 60 * 24

/** Days between `first_seen` (ISO timestamp from the API) and `now`. Floored, never negative. */
export function daysInStock(firstSeen: string, now: Date): number {
  const seen = new Date(firstSeen).getTime()
  if (Number.isNaN(seen)) return 0
  return Math.max(0, Math.floor((now.getTime() - seen) / MS_PER_DAY))
}

// K3 — aging semaphore, single canonical definition (carta 03-garage-fleet §4 row K3):
// verde <=30d · ambar 31-60d · rojo 61-90d (STALE_DAYS) · negro +90d. Cuts are
// [RESEARCH-US, pendiente calibración ES] per the carta's own F0 note; this is the
// ONE place they are encoded — VehicleTable's row indicator and VehicleDetailModal's
// stock badge both call this instead of re-deriving their own thresholds.
export type AgingBand = 'fresco' | 'normal' | 'envejecido' | 'critico'

export const AGING_GREEN_MAX_DAYS = 30
export const AGING_AMBER_MAX_DAYS = 60
// AGING_RED_MAX_DAYS === STALE_DAYS (config.ts) — imported by callers that need both.

export function agingBand(days: number, staleDays: number): AgingBand {
  if (days <= AGING_GREEN_MAX_DAYS) return 'fresco'
  if (days <= AGING_AMBER_MAX_DAYS) return 'normal'
  if (days <= staleDays) return 'envejecido'
  return 'critico'
}

export function agingColor(band: AgingBand): string {
  switch (band) {
    case 'fresco': return 'var(--c-emerald)'
    case 'normal': return 'var(--c-amber)'
    case 'envejecido': return 'var(--c-rose)'
    case 'critico': return '#3f3f46' // negro (zinc-700 — legible en tema claro y oscuro)
  }
}

/** Strips a leading "www." from a URL's hostname for a clean display label. */
export function hostnameOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

export function formatPrice(price: number | null, currency: string | null): string {
  if (price === null) return '—'
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: currency ?? 'EUR',
    maximumFractionDigits: 0,
  }).format(price)
}

export function formatKm(km: number | null): string {
  if (km === null) return '—'
  return `${km.toLocaleString('es-ES')} km`
}

/** Relative "hace X" label from an ISO timestamp, Spanish, coarse buckets. */
export function relativeDate(iso: string, now: Date): string {
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return '—'
  const diffMs = now.getTime() - then
  const days = Math.floor(diffMs / MS_PER_DAY)
  if (days <= 0) return 'hoy'
  if (days === 1) return 'ayer'
  if (days < 30) return `hace ${days} días`
  const months = Math.floor(days / 30)
  if (months < 12) return `hace ${months} ${months === 1 ? 'mes' : 'meses'}`
  const years = Math.floor(months / 12)
  return `hace ${years} ${years === 1 ? 'año' : 'años'}`
}

/** Exception chips (vAuto/CDK pattern) — only ever built from real fields, never fabricated. */
export function buildChips(vehicles: readonly VehicleListItem[], now: Date): ChipDef[] {
  let nuevos = 0
  let stale = 0
  let sinFoto = 0
  let sinPrecio = 0

  for (const v of vehicles) {
    const days = daysInStock(v.first_seen, now)
    if (days <= FRESH_DAYS) nuevos++
    if (days >= STALE_DAYS) stale++
    if (!v.photo_url) sinFoto++
    if (v.price === null) sinPrecio++
  }

  const chips: ChipDef[] = [
    { key: 'nuevos', label: 'Nuevos', count: nuevos, color: 'emerald' },
    { key: 'stale', label: `+${STALE_DAYS} días en stock`, count: stale, color: 'rose' },
    { key: 'sin_foto', label: 'Sin foto', count: sinFoto, color: 'amber' },
    { key: 'sin_precio', label: 'Sin precio', count: sinPrecio, color: 'amber' },
  ]
  return chips.filter(c => c.count > 0)
}

function normalize(s: string): string {
  return s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

function matchesChip(v: VehicleListItem, chip: ChipKey | null, now: Date): boolean {
  if (chip === null) return true
  const days = daysInStock(v.first_seen, now)
  switch (chip) {
    case 'nuevos': return days <= FRESH_DAYS
    case 'stale': return days >= STALE_DAYS
    case 'sin_foto': return !v.photo_url
    case 'sin_precio': return v.price === null
  }
}

/** 100% client-side filter — the real API has no server-side filter beyond page/size. */
export function applyFilters(
  vehicles: readonly VehicleListItem[],
  filters: InventoryFilters,
  now: Date,
): VehicleListItem[] {
  const q = normalize(filters.search.trim())

  return vehicles.filter(v => {
    if (filters.makes.length > 0 && (v.make === null || !filters.makes.includes(v.make))) return false
    if (filters.fuels.length > 0 && (v.fuel === null || !filters.fuels.includes(v.fuel))) return false
    if (filters.transmissions.length > 0 && (v.transmission === null || !filters.transmissions.includes(v.transmission))) return false
    if (filters.yearMin !== null && (v.year === null || v.year < filters.yearMin)) return false
    if (filters.yearMax !== null && (v.year === null || v.year > filters.yearMax)) return false
    if (filters.priceMin !== null && (v.price === null || v.price < filters.priceMin)) return false
    if (filters.priceMax !== null && (v.price === null || v.price > filters.priceMax)) return false
    if (filters.kmMin !== null && (v.km === null || v.km < filters.kmMin)) return false
    if (filters.kmMax !== null && (v.km === null || v.km > filters.kmMax)) return false
    if (!matchesChip(v, filters.chip, now)) return false
    if (q.length > 0) {
      const haystack = normalize(`${v.title ?? ''} ${v.make ?? ''} ${v.model ?? ''}`)
      if (!haystack.includes(q)) return false
    }
    return true
  })
}

/** Nulls always sort last, regardless of direction — never let a missing field win a sort. */
function compareNullable(a: number | null, b: number | null, dir: 1 | -1): number {
  if (a === null && b === null) return 0
  if (a === null) return 1
  if (b === null) return -1
  return (a - b) * dir
}

export function applySort(vehicles: readonly VehicleListItem[], sort: SortKey): VehicleListItem[] {
  const copy = [...vehicles]
  switch (sort) {
    case 'recientes':
      return copy.sort((a, b) => new Date(b.first_seen).getTime() - new Date(a.first_seen).getTime())
    case 'antiguos_stock':
      return copy.sort((a, b) => new Date(a.first_seen).getTime() - new Date(b.first_seen).getTime())
    case 'precio_asc':
      return copy.sort((a, b) => compareNullable(a.price, b.price, 1))
    case 'precio_desc':
      return copy.sort((a, b) => compareNullable(a.price, b.price, -1))
    case 'km_asc':
      return copy.sort((a, b) => compareNullable(a.km, b.km, 1))
    case 'km_desc':
      return copy.sort((a, b) => compareNullable(a.km, b.km, -1))
    case 'anio_desc':
      return copy.sort((a, b) => compareNullable(a.year, b.year, -1))
  }
}

export interface MakeGroup {
  make: string
  vehicles: VehicleListItem[]
}

/** Groups by make, ordered by count desc (largest pavilion first) — stable order for the 3D layout. */
export function groupByMake(vehicles: readonly VehicleListItem[]): MakeGroup[] {
  const map = new Map<string, VehicleListItem[]>()
  for (const v of vehicles) {
    const key = v.make ?? 'Sin marca'
    const bucket = map.get(key)
    if (bucket) bucket.push(v)
    else map.set(key, [v])
  }
  return [...map.entries()]
    .map(([make, list]) => ({ make, vehicles: list }))
    .sort((a, b) => b.vehicles.length - a.vehicles.length)
}

function median(sorted: readonly number[]): number | null {
  if (sorted.length === 0) return null
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

/** Real aggregates over whatever has been loaded — callers must label partial loads themselves. */
export function stockStats(vehicles: readonly VehicleListItem[], now: Date): StockStats {
  const prices = vehicles.map(v => v.price).filter((p): p is number => p !== null)
  const kms = vehicles.map(v => v.km).filter((k): k is number => k !== null)
  const ages = vehicles.map(v => daysInStock(v.first_seen, now))
  const sortedPrices = [...prices].sort((a, b) => a - b)

  return {
    count: vehicles.length,
    totalValue: prices.reduce((s, p) => s + p, 0),
    pricedCount: prices.length,
    medianPrice: median(sortedPrices),
    avgAgeDays: ages.length > 0 ? ages.reduce((s, d) => s + d, 0) / ages.length : null,
    avgKm: kms.length > 0 ? kms.reduce((s, k) => s + k, 0) / kms.length : null,
  }
}

export type FacetField = 'make' | 'fuel' | 'transmission'

const FACET_FILTER_KEY: Record<FacetField, keyof InventoryFilters> = {
  make: 'makes',
  fuel: 'fuels',
  transmission: 'transmissions',
}

/**
 * Live per-option counts for a facet, holding every OTHER active filter
 * constant (the facet's own selection is cleared before counting) — the
 * "1,243 results" pattern verified in the vAuto/AutoScout24 audit, adapted to
 * a client-side dataset instead of a server aggregation.
 */
export function facetCounts(
  vehicles: readonly VehicleListItem[],
  filters: InventoryFilters,
  field: FacetField,
  now: Date,
): Map<string, number> {
  const relaxed: InventoryFilters = { ...filters, [FACET_FILTER_KEY[field]]: [] }
  const pool = applyFilters(vehicles, relaxed, now)
  const counts = new Map<string, number>()
  for (const v of pool) {
    const value = v[field]
    if (value === null) continue
    counts.set(value, (counts.get(value) ?? 0) + 1)
  }
  return counts
}

/** Distinct option list for a facet across the FULL loaded dataset (not filtered) — the checkbox universe never shrinks away. */
export function facetOptions(vehicles: readonly VehicleListItem[], field: FacetField): string[] {
  const set = new Set<string>()
  for (const v of vehicles) {
    const value = v[field]
    if (value !== null) set.add(value)
  }
  return [...set].sort()
}

export interface NumericBounds {
  min: number
  max: number
}

export function numericBounds(vehicles: readonly VehicleListItem[], field: 'year' | 'price' | 'km'): NumericBounds | null {
  const values = vehicles.map(v => v[field]).filter((n): n is number => n !== null)
  if (values.length === 0) return null
  return { min: Math.min(...values), max: Math.max(...values) }
}

/** Client-side CSV of exactly what's visible — quotes/escapes per RFC 4180. */
export function toCsv(vehicles: readonly VehicleListItem[], now: Date): string {
  const headers = [
    'vehicle_ulid', 'titulo', 'marca', 'modelo', 'anio', 'km', 'precio', 'divisa',
    'combustible', 'cambio', 'dias_en_stock', 'primera_deteccion', 'ultima_vez_visto', 'enlace',
  ]
  const escape = (v: string | number | null): string => {
    const s = v === null ? '' : String(v)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const rows = vehicles.map(v => [
    v.vehicle_ulid, v.title, v.make, v.model, v.year, v.km, v.price, v.currency,
    v.fuel, v.transmission, daysInStock(v.first_seen, now), v.first_seen, v.last_seen, v.deep_link,
  ].map(escape).join(','))
  return [headers.join(','), ...rows].join('\n')
}
