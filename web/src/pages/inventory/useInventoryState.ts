// URL-synced UI state for the Inventory page — filters, sort, active view and
// selection all live in the query string so a view is shareable/deep-linkable
// (web/patterns.md: "URL as state" for filters/sort/tab/search).
import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { VehicleListItem } from '../../api/cardeep'
import {
  applyFilters, applySort, EMPTY_FILTERS,
  type ChipKey, type InventoryFilters, type SortKey,
} from './derive'

export type ViewMode = 'tabla' | 'tarjetas' | 'garaje'

const VALID_VIEWS: ViewMode[] = ['tabla', 'tarjetas', 'garaje']
const VALID_SORTS: SortKey[] = ['recientes', 'antiguos_stock', 'precio_asc', 'precio_desc', 'km_asc', 'km_desc', 'anio_desc']
const VALID_CHIPS: ChipKey[] = ['nuevos', 'stale', 'sin_foto', 'sin_precio']

function parseList(v: string | null): string[] {
  return v ? v.split(',').filter(Boolean) : []
}
function parseNum(v: string | null): number | null {
  if (v === null || v === '') return null
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

export function useInventoryState() {
  const [params, setParams] = useSearchParams()

  const view: ViewMode = (VALID_VIEWS as string[]).includes(params.get('vista') ?? '')
    ? (params.get('vista') as ViewMode) : 'tabla'
  const sort: SortKey = (VALID_SORTS as string[]).includes(params.get('orden') ?? '')
    ? (params.get('orden') as SortKey) : 'recientes'
  const chip: ChipKey | null = (VALID_CHIPS as string[]).includes(params.get('chip') ?? '')
    ? (params.get('chip') as ChipKey) : null
  const selectedUlid = params.get('v')

  const filters: InventoryFilters = useMemo(() => ({
    ...EMPTY_FILTERS,
    makes: parseList(params.get('marca')),
    fuels: parseList(params.get('comb')),
    transmissions: parseList(params.get('cambio')),
    yearMin: parseNum(params.get('anio_min')),
    yearMax: parseNum(params.get('anio_max')),
    priceMin: parseNum(params.get('precio_min')),
    priceMax: parseNum(params.get('precio_max')),
    kmMin: parseNum(params.get('km_min')),
    kmMax: parseNum(params.get('km_max')),
    search: params.get('q') ?? '',
    chip,
  }), [params, chip])

  const patch = useCallback((entries: Record<string, string | null>) => {
    setParams(prev => {
      const next = new URLSearchParams(prev)
      for (const [k, v] of Object.entries(entries)) {
        if (v === null || v === '') next.delete(k)
        else next.set(k, v)
      }
      return next
    }, { replace: true })
  }, [setParams])

  const toggleInList = useCallback((key: string, value: string, current: string[]) => {
    const next = current.includes(value) ? current.filter(v => v !== value) : [...current, value]
    patch({ [key]: next.join(',') || null })
  }, [patch])

  const api = useMemo(() => ({
    view,
    setView: (v: ViewMode) => patch({ vista: v === 'tabla' ? null : v }),
    sort,
    setSort: (s: SortKey) => patch({ orden: s === 'recientes' ? null : s }),
    chip,
    setChip: (c: ChipKey | null) => patch({ chip: c }),
    selectedUlid,
    selectVehicle: (ulid: string | null) => patch({ v: ulid }),
    filters,
    setSearch: (q: string) => patch({ q: q || null }),
    toggleMake: (make: string) => toggleInList('marca', make, filters.makes),
    toggleFuel: (fuel: string) => toggleInList('comb', fuel, filters.fuels),
    toggleTransmission: (t: string) => toggleInList('cambio', t, filters.transmissions),
    setYearRange: (min: number | null, max: number | null) => patch({ anio_min: min?.toString() ?? null, anio_max: max?.toString() ?? null }),
    setPriceRange: (min: number | null, max: number | null) => patch({ precio_min: min?.toString() ?? null, precio_max: max?.toString() ?? null }),
    setKmRange: (min: number | null, max: number | null) => patch({ km_min: min?.toString() ?? null, km_max: max?.toString() ?? null }),
    clearFilters: () => patch({
      marca: null, comb: null, cambio: null, anio_min: null, anio_max: null,
      precio_min: null, precio_max: null, km_min: null, km_max: null, q: null, chip: null,
    }),
  }), [view, sort, chip, selectedUlid, filters, patch, toggleInList])

  return api
}

/** Derives the filtered + sorted list for a given "now" — kept outside the hook so callers control when "now" is stamped. */
export function deriveVisible(vehicles: readonly VehicleListItem[], filters: InventoryFilters, sort: SortKey, now: Date): VehicleListItem[] {
  return applySort(applyFilters(vehicles, filters, now), sort)
}
