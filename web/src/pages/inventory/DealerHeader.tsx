import { motion } from 'framer-motion'
import { useState } from 'react'
import { MapPin, Phone, Globe, Copy, Check, Activity, ShieldCheck, AlertTriangle } from 'lucide-react'
import type { EntityDetail, EntityKind } from '../../api/cardeep'
import { useToast } from '../../components/Toast'
import { formatPrice, formatKm, hostnameOf, type StockStats } from './derive'

const KIND_LABELS: Record<EntityKind, string> = {
  concesionario_oficial: 'Concesionario oficial',
  compraventa: 'Compraventa',
  desguace: 'Desguace',
  garaje: 'Garaje',
  plataforma: 'Plataforma',
  particular: 'Particular',
  subasta: 'Subasta',
  oem_vo_portal: 'Portal OEM VO',
  importador: 'Importador',
  rent_a_car_vo: 'Rent-a-car VO',
  cadena: 'Cadena',
}

interface StatTileProps {
  label: string
  value: string
  pending?: boolean
  tone?: 'default' | 'emerald' | 'amber' | 'rose'
}

const TONE_COLOR: Record<NonNullable<StatTileProps['tone']>, string> = {
  default: 'var(--t1)',
  emerald: 'var(--c-emerald)',
  amber: 'var(--c-amber)',
  rose: 'var(--c-rose)',
}

function StatTile({ label, value, pending, tone = 'default' }: StatTileProps) {
  return (
    <div style={{
      padding: '10px 16px',
      borderRadius: 12,
      background: 'var(--glass-xs)',
      border: '1px solid var(--border-subtle)',
      minWidth: 128,
    }}>
      <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--t3)', marginBottom: 4 }}>
        {label}
      </p>
      {pending ? (
        <div className="skeleton" style={{ height: 20, width: '70%', borderRadius: 6 }} />
      ) : (
        <p style={{ fontSize: 19, fontWeight: 800, letterSpacing: '-0.01em', color: TONE_COLOR[tone] }}>{value}</p>
      )}
    </div>
  )
}

interface DealerHeaderProps {
  entity: EntityDetail | null
  loading: boolean
  stats: StockStats
  isComplete: boolean
  loadedCount: number
  recentEventCount: number | null
  onOpenActivity: () => void
}

export default function DealerHeader({
  entity, loading, stats, isComplete, loadedCount, recentEventCount, onOpenActivity,
}: DealerHeaderProps) {
  const [copied, setCopied] = useState(false)
  const { success } = useToast()

  const copyCdp = () => {
    if (!entity) return
    navigator.clipboard.writeText(entity.cdp_code).then(() => {
      setCopied(true)
      success('Código CDP copiado')
      setTimeout(() => setCopied(false), 1600)
    })
  }

  const avgAge = stats.avgAgeDays
  const ageTone: StatTileProps['tone'] = avgAge === null ? 'default' : avgAge < 30 ? 'emerald' : avgAge < 90 ? 'amber' : 'rose'

  // K14 §7 protocol — vía 1: entity.available_inventory (server aggregate). vía 2: the
  // real count of rows the client paginated through. Only comparable once isComplete
  // (loadedCount grows monotonically until every page is fetched); a mismatch does not
  // hide the number, it flags it — never silently pick one side.
  const countDiverges = isComplete && entity !== null && loadedCount !== entity.available_inventory

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.32, 0.72, 0, 1] }}
      className="glass-md glass-edge"
      style={{ borderRadius: 18, padding: '20px 24px', marginBottom: 16, display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'center', justifyContent: 'space-between' }}
    >
      <div style={{ minWidth: 0, flex: '1 1 320px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 6 }}>
          <h1 style={{ fontSize: 22, fontWeight: 900, letterSpacing: '-0.02em', color: 'var(--t1)' }}>
            {loading && !entity ? 'Cargando dealer…' : entity?.trade_name ?? 'Dealer'}
          </h1>
          {entity && (
            <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t3)' }}>
              {KIND_LABELS[entity.kind]}
            </span>
          )}
          {entity?.is_tier1 && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999, background: 'rgba(37,99,235,0.12)', border: '1px solid rgba(37,99,235,0.28)', color: 'var(--c-blue)' }}>
              <ShieldCheck style={{ width: 11, height: 11 }} /> Tier 1
            </span>
          )}
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 14, fontSize: 12.5, color: 'var(--t3)' }}>
          {entity?.address && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              <MapPin style={{ width: 12, height: 12 }} /> {entity.address}
            </span>
          )}
          {entity?.phone && (
            <a href={`tel:${entity.phone}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: 'inherit', textDecoration: 'none' }}
               onMouseEnter={e => (e.currentTarget.style.color = 'var(--c-blue)')}
               onMouseLeave={e => (e.currentTarget.style.color = 'var(--t3)')}>
              <Phone style={{ width: 12, height: 12 }} /> {entity.phone}
            </a>
          )}
          {entity?.website && (
            <a href={entity.website} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: 'inherit', textDecoration: 'none' }}
               onMouseEnter={e => (e.currentTarget.style.color = 'var(--c-blue)')}
               onMouseLeave={e => (e.currentTarget.style.color = 'var(--t3)')}>
              <Globe style={{ width: 12, height: 12 }} /> {hostnameOf(entity.website)}
            </a>
          )}
          {entity && (
            <button
              onClick={copyCdp}
              title="Copiar código CDP"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontFamily: 'JetBrains Mono, monospace', fontSize: 11.5, color: 'var(--t4)', background: 'transparent', border: 'none', cursor: 'pointer', padding: 0 }}
            >
              {copied ? <Check style={{ width: 11, height: 11, color: 'var(--c-emerald)' }} /> : <Copy style={{ width: 11, height: 11 }} />}
              {entity.cdp_code}
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative' }}>
          <StatTile
            label="Anuncios"
            value={entity ? String(countDiverges ? Math.min(entity.available_inventory, loadedCount) : entity.available_inventory) : '—'}
            pending={loading && !entity}
            tone={countDiverges ? 'amber' : 'default'}
          />
          {countDiverges && (
            <span
              title={`Divergencia entre vías de verificación: API=${entity!.available_inventory} · paginación=${loadedCount}. Se muestra el menor.`}
              style={{ position: 'absolute', top: -5, right: -5, display: 'flex', width: 16, height: 16, borderRadius: '50%', background: 'var(--c-amber)', alignItems: 'center', justifyContent: 'center' }}
            >
              <AlertTriangle style={{ width: 10, height: 10, color: '#000' }} />
            </span>
          )}
        </div>
        <StatTile
          label="Valor del stock"
          value={stats.pricedCount > 0 ? `${formatPrice(stats.totalValue, 'EUR')}${stats.pricedCount < stats.count ? ` (${stats.pricedCount})` : ''}` : '—'}
          pending={!isComplete && stats.count === 0}
        />
        <StatTile
          label="Precio mediano"
          value={formatPrice(stats.medianPrice, 'EUR')}
          pending={!isComplete && stats.count === 0}
        />
        <StatTile
          label="Antigüedad media"
          value={avgAge === null ? '—' : `${Math.round(avgAge)} días`}
          tone={ageTone}
          pending={!isComplete && stats.count === 0}
        />

        <motion.button
          whileTap={{ scale: 0.96 }}
          onClick={onOpenActivity}
          style={{
            display: 'flex', alignItems: 'center', gap: 8, padding: '10px 16px', borderRadius: 12,
            background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t1)',
            fontSize: 13, fontWeight: 700, cursor: 'pointer', position: 'relative',
          }}
        >
          <Activity style={{ width: 14, height: 14 }} />
          Actividad
          {recentEventCount !== null && recentEventCount > 0 && (
            <span style={{
              position: 'absolute', top: -6, right: -6, minWidth: 18, height: 18, borderRadius: 999,
              background: 'var(--c-blue)', color: '#fff', fontSize: 10, fontWeight: 800,
              display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 4px',
            }}>
              {recentEventCount > 99 ? '99+' : recentEventCount}
            </span>
          )}
        </motion.button>
      </div>

      {!isComplete && (
        <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: 'var(--t4)' }}>
          <span className="skeleton" style={{ width: 12, height: 12, borderRadius: '50%' }} />
          Cargando inventario… {loadedCount}
          {entity ? ` / ${entity.available_inventory}` : ''}
        </div>
      )}
    </motion.div>
  )
}
