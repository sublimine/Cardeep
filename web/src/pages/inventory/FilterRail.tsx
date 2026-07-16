import { useState } from 'react'
import type { VehicleListItem } from '../../api/cardeep'
import { facetCounts, facetOptions, numericBounds, type InventoryFilters } from './derive'

interface FilterRailProps {
  vehicles: readonly VehicleListItem[]
  filters: InventoryFilters
  onToggleMake: (make: string) => void
  onToggleFuel: (fuel: string) => void
  onToggleTransmission: (t: string) => void
  onYearRange: (min: number | null, max: number | null) => void
  onPriceRange: (min: number | null, max: number | null) => void
  onKmRange: (min: number | null, max: number | null) => void
  now: Date
}

function CheckboxGroup({
  title, options, counts, selected, onToggle,
}: {
  title: string
  options: string[]
  counts: Map<string, number>
  selected: string[]
  onToggle: (v: string) => void
}) {
  if (options.length === 0) return null
  return (
    <div style={{ marginBottom: 18 }}>
      <p style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--t3)', marginBottom: 8 }}>{title}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {options.map(opt => {
          const count = counts.get(opt) ?? 0
          const checked = selected.includes(opt)
          const disabled = count === 0 && !checked
          return (
            <label
              key={opt}
              style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '5px 6px', borderRadius: 8,
                cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.4 : 1,
                background: checked ? 'var(--glass-xs)' : 'transparent',
              }}
            >
              <input
                type="checkbox"
                checked={checked}
                disabled={disabled}
                onChange={() => onToggle(opt)}
                style={{ width: 14, height: 14, accentColor: 'var(--c-blue)', cursor: disabled ? 'not-allowed' : 'pointer' }}
              />
              <span style={{ flex: 1, fontSize: 12.5, color: 'var(--t2)' }}>{opt}</span>
              <span style={{ fontSize: 11, color: 'var(--t4)', fontFamily: 'JetBrains Mono, monospace' }}>{count}</span>
            </label>
          )
        })}
      </div>
    </div>
  )
}

function RangeInputs({
  title, bounds, min, max, onChange, unit,
}: {
  title: string
  bounds: { min: number; max: number } | null
  min: number | null
  max: number | null
  onChange: (min: number | null, max: number | null) => void
  unit?: string
}) {
  const [localMin, setLocalMin] = useState(min?.toString() ?? '')
  const [localMax, setLocalMax] = useState(max?.toString() ?? '')

  if (!bounds) return null

  const commit = () => {
    const parsedMin = localMin === '' ? null : Number(localMin)
    const parsedMax = localMax === '' ? null : Number(localMax)
    onChange(Number.isFinite(parsedMin as number) ? parsedMin : null, Number.isFinite(parsedMax as number) ? parsedMax : null)
  }

  return (
    <div style={{ marginBottom: 18 }}>
      <p style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--t3)', marginBottom: 8 }}>
        {title} {unit && <span style={{ opacity: 0.6 }}>({unit})</span>}
      </p>
      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        <input
          type="number"
          placeholder={String(bounds.min)}
          value={localMin}
          onChange={e => setLocalMin(e.target.value)}
          onBlur={commit}
          onKeyDown={e => e.key === 'Enter' && commit()}
          style={{ width: '50%', padding: '7px 8px', borderRadius: 8, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t1)', fontSize: 12 }}
        />
        <span style={{ color: 'var(--t4)', fontSize: 12 }}>–</span>
        <input
          type="number"
          placeholder={String(bounds.max)}
          value={localMax}
          onChange={e => setLocalMax(e.target.value)}
          onBlur={commit}
          onKeyDown={e => e.key === 'Enter' && commit()}
          style={{ width: '50%', padding: '7px 8px', borderRadius: 8, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t1)', fontSize: 12 }}
        />
      </div>
    </div>
  )
}

export default function FilterRail({
  vehicles, filters, onToggleMake, onToggleFuel, onToggleTransmission,
  onYearRange, onPriceRange, onKmRange, now,
}: FilterRailProps) {
  const makeOptions = facetOptions(vehicles, 'make')
  const fuelOptions = facetOptions(vehicles, 'fuel')
  const transmissionOptions = facetOptions(vehicles, 'transmission')

  const makeCounts = facetCounts(vehicles, filters, 'make', now)
  const fuelCounts = facetCounts(vehicles, filters, 'fuel', now)
  const transmissionCounts = facetCounts(vehicles, filters, 'transmission', now)

  return (
    <aside className="glass-lg" style={{ borderRadius: 16, padding: 18, width: 240, flexShrink: 0, alignSelf: 'flex-start', maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
      <CheckboxGroup title="Marca" options={makeOptions} counts={makeCounts} selected={filters.makes} onToggle={onToggleMake} />
      <CheckboxGroup title="Combustible" options={fuelOptions} counts={fuelCounts} selected={filters.fuels} onToggle={onToggleFuel} />
      <CheckboxGroup title="Cambio" options={transmissionOptions} counts={transmissionCounts} selected={filters.transmissions} onToggle={onToggleTransmission} />
      <RangeInputs title="Año" bounds={numericBounds(vehicles, 'year')} min={filters.yearMin} max={filters.yearMax} onChange={onYearRange} />
      <RangeInputs title="Precio" bounds={numericBounds(vehicles, 'price')} min={filters.priceMin} max={filters.priceMax} onChange={onPriceRange} unit="€" />
      <RangeInputs title="Kilometraje" bounds={numericBounds(vehicles, 'km')} min={filters.kmMin} max={filters.kmMax} onChange={onKmRange} unit="km" />
    </aside>
  )
}
