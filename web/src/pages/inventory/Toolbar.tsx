import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { Search, List, LayoutGrid, Orbit, Download, SlidersHorizontal, X } from 'lucide-react'
import type { ChipDef, ChipKey, SortKey } from './derive'
import type { ViewMode } from './useInventoryState'

const SORT_OPTIONS: { value: SortKey; label: string }[] = [
  { value: 'recientes', label: 'Más recientes' },
  { value: 'antiguos_stock', label: 'Más antiguos en stock' },
  { value: 'precio_asc', label: 'Precio: menor a mayor' },
  { value: 'precio_desc', label: 'Precio: mayor a menor' },
  { value: 'km_asc', label: 'Km: menor a mayor' },
  { value: 'km_desc', label: 'Km: mayor a menor' },
  { value: 'anio_desc', label: 'Año: más nuevo' },
]

const VIEW_OPTIONS: { value: ViewMode; icon: typeof List; label: string }[] = [
  { value: 'tabla', icon: List, label: 'Tabla' },
  { value: 'tarjetas', icon: LayoutGrid, label: 'Tarjetas' },
  { value: 'garaje', icon: Orbit, label: 'Garaje 3D' },
]

const CHIP_COLOR: Record<ChipDef['color'], { bg: string; border: string; text: string }> = {
  emerald: { bg: 'rgba(5,150,105,0.10)', border: 'rgba(5,150,105,0.30)', text: 'var(--c-emerald)' },
  amber: { bg: 'rgba(217,119,6,0.10)', border: 'rgba(217,119,6,0.30)', text: 'var(--c-amber)' },
  rose: { bg: 'rgba(225,29,72,0.10)', border: 'rgba(225,29,72,0.30)', text: 'var(--c-rose)' },
}

interface ToolbarProps {
  search: string
  onSearchChange: (q: string) => void
  sort: SortKey
  onSortChange: (s: SortKey) => void
  chips: ChipDef[]
  activeChip: ChipKey | null
  onChipToggle: (c: ChipKey) => void
  view: ViewMode
  onViewChange: (v: ViewMode) => void
  visibleCount: number
  loadedCount: number
  totalExpected: number | null
  isComplete: boolean
  onExportCsv: () => void
  freshnessLabel: string
  onToggleFilters: () => void
  hasActiveFilters: boolean
  onClearFilters: () => void
}

export default function Toolbar({
  search, onSearchChange, sort, onSortChange, chips, activeChip, onChipToggle,
  view, onViewChange, visibleCount, loadedCount, totalExpected, isComplete,
  onExportCsv, freshnessLabel, onToggleFilters, hasActiveFilters, onClearFilters,
}: ToolbarProps) {
  const [localSearch, setLocalSearch] = useState(search)

  useEffect(() => setLocalSearch(search), [search])
  useEffect(() => {
    const t = setTimeout(() => { if (localSearch !== search) onSearchChange(localSearch) }, 150)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [localSearch])

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05, duration: 0.3, ease: [0.32, 0.72, 0, 1] }}
      className="glass-md"
      style={{ borderRadius: 16, padding: 14, marginBottom: 12, display: 'flex', flexDirection: 'column', gap: 10 }}
    >
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          onClick={onToggleFilters}
          className="filter-rail-toggle"
          style={{ display: 'none', alignItems: 'center', gap: 6, padding: '9px 12px', borderRadius: 10, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', fontSize: 12.5, fontWeight: 600, cursor: 'pointer' }}
        >
          <SlidersHorizontal style={{ width: 13, height: 13 }} /> Filtros
        </button>

        <div style={{ flex: '1 1 220px', position: 'relative', minWidth: 180 }}>
          <Search style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', width: 14, height: 14, color: 'var(--t3)', pointerEvents: 'none' }} />
          <input
            type="text"
            placeholder="Buscar marca, modelo, título…"
            value={localSearch}
            onChange={e => setLocalSearch(e.target.value)}
            aria-label="Buscar en el inventario"
            style={{
              width: '100%', padding: '9px 12px 9px 34px', borderRadius: 10,
              background: 'var(--bg-input)', border: '1px solid var(--border-subtle)',
              color: 'var(--t1)', fontSize: 13, outline: 'none',
            }}
          />
        </div>

        <select
          value={sort}
          onChange={e => onSortChange(e.target.value as SortKey)}
          aria-label="Ordenar por"
          style={{ padding: '9px 12px', borderRadius: 10, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', fontSize: 12.5, cursor: 'pointer', minWidth: 170 }}
        >
          {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>

        <button
          onClick={onExportCsv}
          title={`Exporta la vista actual (${visibleCount} filas)`}
          style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '9px 14px', borderRadius: 10, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', fontSize: 12.5, fontWeight: 600, cursor: 'pointer' }}
        >
          <Download style={{ width: 13, height: 13 }} /> Exportar CSV
        </button>

        <div style={{ display: 'flex', background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: 3, gap: 2 }}>
          {VIEW_OPTIONS.map(({ value, icon: Icon, label }) => (
            <button
              key={value}
              onClick={() => onViewChange(value)}
              title={label}
              aria-pressed={view === value}
              style={{
                display: 'flex', alignItems: 'center', gap: 6, padding: '7px 11px', borderRadius: 8,
                background: view === value ? 'rgba(37,99,235,0.14)' : 'transparent',
                border: view === value ? '1px solid rgba(37,99,235,0.30)' : '1px solid transparent',
                color: view === value ? 'var(--c-blue)' : 'var(--t3)', fontSize: 12, fontWeight: 600, cursor: 'pointer',
              }}
            >
              <Icon style={{ width: 14, height: 14 }} />
              <span className="view-label">{label}</span>
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        {chips.map(chip => {
          const active = activeChip === chip.key
          const c = CHIP_COLOR[chip.color]
          return (
            <button
              key={chip.key}
              onClick={() => onChipToggle(chip.key)}
              aria-pressed={active}
              style={{
                display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 999,
                background: active ? c.bg.replace('0.10', '0.18') : c.bg,
                border: `1px solid ${active ? c.border.replace('0.30', '0.55') : c.border}`,
                color: c.text, fontSize: 12, fontWeight: 700, cursor: 'pointer',
              }}
            >
              {chip.label} <span style={{ opacity: 0.75 }}>({chip.count})</span>
            </button>
          )
        })}
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 10px', borderRadius: 999, background: 'transparent', border: '1px solid var(--border-subtle)', color: 'var(--t3)', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
          >
            <X style={{ width: 11, height: 11 }} /> Limpiar filtros
          </button>
        )}

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 10, fontSize: 11.5, color: 'var(--t3)' }}>
          <span>
            {visibleCount} / {loadedCount}
            {!isComplete && totalExpected !== null && ` (cargando… ${loadedCount}/${totalExpected})`}
          </span>
          <span style={{ width: 1, height: 12, background: 'var(--border-subtle)' }} />
          <span>{freshnessLabel}</span>
        </div>
      </div>
    </motion.div>
  )
}
