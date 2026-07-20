import { useState } from 'react'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'
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
  /** Only rendered/wired on the mobile full-screen overlay (see `.filter-rail-close` in index.tsx). */
  onClose?: () => void
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
              className={disabled ? undefined : checked ? 'filter-option filter-option-checked' : 'filter-option'}
              style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '5px 6px', borderRadius: 8,
                cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.4 : 1,
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
              <span className="tabular-nums" style={{ fontSize: 11, color: 'var(--t4)', fontFamily: 'JetBrains Mono, monospace' }}>{count}</span>
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
          onBlur={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; commit() }}
          onFocus={e => (e.currentTarget.style.borderColor = 'var(--border-focus)')}
          onKeyDown={e => e.key === 'Enter' && commit()}
          className="tabular-nums"
          style={{ width: '50%', padding: '7px 8px', borderRadius: 8, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t1)', fontSize: 12, outline: 'none', transition: 'border-color 0.12s' }}
        />
        <span style={{ color: 'var(--t4)', fontSize: 12 }}>–</span>
        <input
          type="number"
          placeholder={String(bounds.max)}
          value={localMax}
          onChange={e => setLocalMax(e.target.value)}
          onBlur={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; commit() }}
          onFocus={e => (e.currentTarget.style.borderColor = 'var(--border-focus)')}
          onKeyDown={e => e.key === 'Enter' && commit()}
          className="tabular-nums"
          style={{ width: '50%', padding: '7px 8px', borderRadius: 8, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t1)', fontSize: 12, outline: 'none', transition: 'border-color 0.12s' }}
        />
      </div>
    </div>
  )
}

export default function FilterRail({
  vehicles, filters, onToggleMake, onToggleFuel, onToggleTransmission,
  onYearRange, onPriceRange, onKmRange, now, onClose,
}: FilterRailProps) {
  const makeOptions = facetOptions(vehicles, 'make')
  const fuelOptions = facetOptions(vehicles, 'fuel')
  const transmissionOptions = facetOptions(vehicles, 'transmission')

  const makeCounts = facetCounts(vehicles, filters, 'make', now)
  const fuelCounts = facetCounts(vehicles, filters, 'fuel', now)
  const transmissionCounts = facetCounts(vehicles, filters, 'transmission', now)

  return (
    <motion.aside
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.08, duration: 0.3, ease: [0.32, 0.72, 0, 1] }}
      className="glass-lg"
      style={{ borderRadius: 16, padding: 18, width: 240, flexShrink: 0, alignSelf: 'flex-start', maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}
    >
      <div className="filter-rail-close" style={{ justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span style={{ fontSize: 13, fontWeight: 800, color: 'var(--t1)' }}>Filtros</span>
        <button
          onClick={onClose}
          aria-label="Cerrar filtros"
          className="filter-close-btn"
          style={{ display: 'flex', width: 28, height: 28, borderRadius: 8, alignItems: 'center', justifyContent: 'center', background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t3)', cursor: 'pointer' }}
        >
          <X style={{ width: 13, height: 13 }} />
        </button>
      </div>
      <CheckboxGroup title="Marca" options={makeOptions} counts={makeCounts} selected={filters.makes} onToggle={onToggleMake} />
      <CheckboxGroup title="Combustible" options={fuelOptions} counts={fuelCounts} selected={filters.fuels} onToggle={onToggleFuel} />
      <CheckboxGroup title="Cambio" options={transmissionOptions} counts={transmissionCounts} selected={filters.transmissions} onToggle={onToggleTransmission} />
      <RangeInputs title="Año" bounds={numericBounds(vehicles, 'year')} min={filters.yearMin} max={filters.yearMax} onChange={onYearRange} />
      <RangeInputs title="Precio" bounds={numericBounds(vehicles, 'price')} min={filters.priceMin} max={filters.priceMax} onChange={onPriceRange} unit="€" />
      <RangeInputs title="Kilometraje" bounds={numericBounds(vehicles, 'km')} min={filters.kmMin} max={filters.kmMax} onChange={onKmRange} unit="km" />

      <style>{`
        .filter-option { transition: background 0.12s; }
        .filter-option:hover { background: var(--bg-hover); }
        .filter-option-checked, .filter-option-checked:hover { background: var(--glass-xs); }
        .filter-close-btn { transition: background 0.12s, color 0.12s; }
        .filter-close-btn:hover { background: var(--glass-sm); color: var(--t1); }
      `}</style>
    </motion.aside>
  )
}
