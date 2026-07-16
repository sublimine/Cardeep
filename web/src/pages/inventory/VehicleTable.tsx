import { useEffect, useRef, useState } from 'react'
import { ExternalLink, MoreVertical, Copy, History, Radar } from 'lucide-react'
import type { VehicleListItem } from '../../api/cardeep'
import { Dropdown } from '../../components/Dropdown'
import { useToast } from '../../components/Toast'
import { daysInStock, formatKm, formatPrice, relativeDate, type SortKey } from './derive'
import { STALE_DAYS } from './config'
import VehiclePhoto from './VehiclePhoto'
import { ROW_BATCH } from './config'

interface SortableColumn {
  label: string
  ascKey: SortKey
  descKey: SortKey
}

const COLUMNS: SortableColumn[] = [
  { label: 'Precio', ascKey: 'precio_asc', descKey: 'precio_desc' },
  { label: 'Km', ascKey: 'km_asc', descKey: 'km_desc' },
  { label: 'Año', ascKey: 'anio_desc', descKey: 'anio_desc' },
]

function AgeBar({ days }: { days: number }) {
  const pct = Math.min(days / 180, 1) * 100
  const color = days < 30 ? 'var(--c-emerald)' : days < STALE_DAYS ? 'var(--c-amber)' : 'var(--c-rose)'
  return (
    <div>
      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--t2)' }}>{days}d</span>
      <div style={{ marginTop: 3, height: 3, width: 56, borderRadius: 999, background: 'var(--border-subtle)', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 999 }} />
      </div>
    </div>
  )
}

interface VehicleTableProps {
  vehicles: readonly VehicleListItem[]
  sort: SortKey
  onSortChange: (s: SortKey) => void
  onSelect: (ulid: string) => void
  now: Date
}

export default function VehicleTable({ vehicles, sort, onSortChange, onSelect, now }: VehicleTableProps) {
  const [visibleCount, setVisibleCount] = useState(ROW_BATCH)
  const sentinelRef = useRef<HTMLDivElement | null>(null)
  const { success } = useToast()

  useEffect(() => setVisibleCount(ROW_BATCH), [vehicles])

  useEffect(() => {
    const el = sentinelRef.current
    if (!el) return
    const obs = new IntersectionObserver(entries => {
      if (entries[0]?.isIntersecting) setVisibleCount(c => Math.min(c + ROW_BATCH, vehicles.length))
    }, { rootMargin: '400px' })
    obs.observe(el)
    return () => obs.disconnect()
  }, [vehicles.length])

  const rows = vehicles.slice(0, visibleCount)

  const headerCell = (col: SortableColumn) => {
    const active = sort === col.ascKey || sort === col.descKey
    const nextSort = sort === col.ascKey ? col.descKey : col.ascKey
    return (
      <button
        key={col.label}
        onClick={() => onSortChange(nextSort)}
        style={{ display: 'flex', alignItems: 'center', gap: 3, background: 'none', border: 'none', cursor: 'pointer', color: active ? 'var(--t1)' : 'var(--t4)', fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', padding: 0 }}
      >
        {col.label} {active && (sort === col.ascKey ? '↑' : '↓')}
      </button>
    )
  }

  return (
    <div className="glass-md" style={{ borderRadius: 16, overflow: 'hidden' }} role="table" aria-rowcount={vehicles.length}>
      <div
        style={{
          display: 'grid', gridTemplateColumns: '64px 2fr 1fr 100px 110px 110px 90px 110px 96px 84px',
          gap: 10, padding: '10px 16px', background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)',
          position: 'sticky', top: 0, zIndex: 2, alignItems: 'center',
        }}
        role="row"
      >
        <span />
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--t4)' }}>Vehículo</span>
        {headerCell(COLUMNS[0])}
        {headerCell(COLUMNS[1])}
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--t4)' }}>Combustible</span>
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--t4)' }}>Cambio</span>
        {headerCell(COLUMNS[2])}
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--t4)' }}>Días en stock</span>
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--t4)' }}>Visto</span>
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--t4)' }}>Acciones</span>
      </div>

      {rows.map(v => {
        const days = daysInStock(v.first_seen, now)
        return (
          <div
            key={v.vehicle_ulid}
            role="row"
            tabIndex={0}
            onClick={() => onSelect(v.vehicle_ulid)}
            onKeyDown={e => e.key === 'Enter' && onSelect(v.vehicle_ulid)}
            style={{
              display: 'grid', gridTemplateColumns: '64px 2fr 1fr 100px 110px 110px 90px 110px 96px 84px',
              gap: 10, padding: '9px 16px', alignItems: 'center', cursor: 'pointer',
              borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.12s',
            }}
            onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-hover)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            <div style={{ width: 56, height: 40, borderRadius: 8, overflow: 'hidden' }}>
              <VehiclePhoto photoUrl={v.photo_url} make={v.make} />
            </div>
            <div style={{ minWidth: 0 }}>
              <p style={{ fontSize: 13, fontWeight: 800, color: 'var(--t1)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {v.title ?? `${v.make} ${v.model}`}
              </p>
              <p style={{ fontSize: 11, color: 'var(--t3)' }}>{v.make} · {v.year ?? '—'}</p>
            </div>
            <p style={{ fontSize: 13, fontWeight: 800, color: 'var(--t1)', fontFamily: 'JetBrains Mono, monospace' }}>{formatPrice(v.price, v.currency)}</p>
            <p style={{ fontSize: 12.5, color: 'var(--t2)' }}>{formatKm(v.km)}</p>
            <p style={{ fontSize: 12.5, color: 'var(--t2)' }}>{v.fuel ?? '—'}</p>
            <p style={{ fontSize: 12.5, color: 'var(--t2)' }}>{v.transmission ?? '—'}</p>
            <p style={{ fontSize: 12.5, color: 'var(--t2)' }}>{v.year ?? '—'}</p>
            <AgeBar days={days} />
            <p style={{ fontSize: 11, color: 'var(--t4)' }}>{relativeDate(v.last_seen, now)}</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }} onClick={e => e.stopPropagation()}>
              <a
                href={v.deep_link} target="_blank" rel="noopener noreferrer"
                title="Anuncio original"
                style={{ display: 'flex', width: 26, height: 26, alignItems: 'center', justifyContent: 'center', borderRadius: 7, color: 'var(--t3)' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'var(--c-blue)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--t3)')}
              >
                <ExternalLink style={{ width: 13, height: 13 }} />
              </a>
              <Dropdown
                solid
                trigger={
                  <button aria-label="Más acciones" style={{ display: 'flex', width: 26, height: 26, alignItems: 'center', justifyContent: 'center', borderRadius: 7, background: 'transparent', border: 'none', color: 'var(--t3)', cursor: 'pointer' }}>
                    <MoreVertical style={{ width: 13, height: 13 }} />
                  </button>
                }
                items={[
                  { label: 'Ver historial', icon: <History style={{ width: 13, height: 13 }} />, onSelect: () => onSelect(v.vehicle_ulid) },
                  { label: 'Ver plataformas', icon: <Radar style={{ width: 13, height: 13 }} />, onSelect: () => onSelect(v.vehicle_ulid) },
                  { label: 'Copiar enlace del anuncio', icon: <Copy style={{ width: 13, height: 13 }} />, onSelect: () => { navigator.clipboard.writeText(v.deep_link); success('Enlace copiado') } },
                  { label: 'Copiar ULID', icon: <Copy style={{ width: 13, height: 13 }} />, onSelect: () => { navigator.clipboard.writeText(v.vehicle_ulid); success('ULID copiado') } },
                ]}
              />
            </div>
          </div>
        )
      })}

      {visibleCount < vehicles.length && <div ref={sentinelRef} style={{ height: 1 }} />}
    </div>
  )
}
