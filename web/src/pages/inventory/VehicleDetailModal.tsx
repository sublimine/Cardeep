import { useEffect, useState, type ReactNode } from 'react'
import { ExternalLink, Copy, ShieldCheck } from 'lucide-react'
import Modal from '../../components/Modal'
import { Tabs } from '../../components/Tabs'
import Timeline, { type TimelineItem } from '../../components/Timeline'
import { VehicleStatusBadge } from '../../components/Badge'
import { useToast } from '../../components/Toast'
import { CardSkeleton } from '../../components/Skeleton'
import EmptyState from '../../components/EmptyState'
import {
  cardeep, CardeepApiError,
  type VehicleListItem, type VehicleHistoryEvent, type VehiclePlatforms,
} from '../../api/cardeep'
import { daysInStock, formatKm, formatPrice, hostnameOf, relativeDate } from './derive'

// Session-level cache — avoids re-fetching history/platforms when the user
// re-opens the same vehicle (e.g. via the 3D garage HUD's prev/next).
const historyCache = new Map<string, VehicleHistoryEvent[]>()
const platformsCache = new Map<string, VehiclePlatforms>()

type TabKey = 'ficha' | 'historial' | 'plataformas'

function priceChangeLabel(oldValue: unknown, newValue: unknown): { text: string; positive: boolean | null } {
  const oldPrice = typeof oldValue === 'object' && oldValue !== null ? (oldValue as Record<string, unknown>).price : undefined
  const newPrice = typeof newValue === 'object' && newValue !== null ? (newValue as Record<string, unknown>).price : undefined
  if (typeof oldPrice === 'number' && typeof newPrice === 'number') {
    const pct = ((newPrice - oldPrice) / oldPrice) * 100
    const text = `${formatPrice(oldPrice, 'EUR')} → ${formatPrice(newPrice, 'EUR')} (${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%)`
    return { text, positive: newPrice < oldPrice }
  }
  return { text: JSON.stringify(newValue ?? oldValue), positive: null }
}

function eventToTimelineItem(e: VehicleHistoryEvent, idx: number, now: Date): TimelineItem {
  const date = relativeDate(e.observed_at, now)
  if (e.event_type === 'PRICE_CHANGE') {
    const { text, positive } = priceChangeLabel(e.old_value, e.new_value)
    return { id: String(idx), date, title: 'Cambio de precio', subtitle: text, accent: positive === true ? 'green' : positive === false ? 'red' : 'yellow' }
  }
  if (e.event_type === 'NEW') return { id: String(idx), date, title: 'Anuncio detectado', accent: 'blue' }
  if (e.event_type === 'GONE') return { id: String(idx), date, title: 'Anuncio retirado', accent: 'red' }
  return { id: String(idx), date, title: e.event_type, accent: 'gray' }
}

interface VehicleDetailModalProps {
  vehicle: VehicleListItem
  onClose: () => void
  initialTab?: TabKey
  now: Date
}

export default function VehicleDetailModal({ vehicle, onClose, initialTab = 'ficha', now }: VehicleDetailModalProps) {
  const [tab, setTab] = useState<TabKey>(initialTab)
  const [history, setHistory] = useState<VehicleHistoryEvent[] | null>(historyCache.get(vehicle.vehicle_ulid) ?? null)
  const [historyError, setHistoryError] = useState<string | null>(null)
  const [platforms, setPlatforms] = useState<VehiclePlatforms | null>(platformsCache.get(vehicle.vehicle_ulid) ?? null)
  const [platformsError, setPlatformsError] = useState<string | null>(null)
  const { success } = useToast()

  useEffect(() => {
    if (tab !== 'historial' || history !== null) return
    let live = true
    cardeep.vehicleHistory(vehicle.vehicle_ulid)
      .then(page => { if (live) { historyCache.set(vehicle.vehicle_ulid, page.items); setHistory(page.items) } })
      .catch((err: unknown) => { if (live) setHistoryError(err instanceof CardeepApiError ? err.message : 'Error al cargar el historial') })
    return () => { live = false }
  }, [tab, vehicle.vehicle_ulid, history])

  useEffect(() => {
    if (tab !== 'plataformas' || platforms !== null) return
    let live = true
    cardeep.vehiclePlatforms(vehicle.vehicle_ulid)
      .then(data => { if (live) { platformsCache.set(vehicle.vehicle_ulid, data); setPlatforms(data) } })
      .catch((err: unknown) => { if (live) setPlatformsError(err instanceof CardeepApiError ? err.message : 'Error al cargar las plataformas') })
    return () => { live = false }
  }, [tab, vehicle.vehicle_ulid, platforms])

  const copy = (text: string, label: string) => { navigator.clipboard.writeText(text); success(label) }
  const days = daysInStock(vehicle.first_seen, now)
  const [photoFailed, setPhotoFailed] = useState(false)
  const showPhoto = vehicle.photo_url !== null && !photoFailed

  return (
    <Modal open onClose={onClose} size="full" title={vehicle.title ?? `${vehicle.make} ${vehicle.model} (${vehicle.year ?? '—'})`}>
      <div style={{ position: 'relative', aspectRatio: '16/9', borderRadius: 12, overflow: 'hidden', marginBottom: 16 }}>
        {showPhoto && (
          <img
            src={vehicle.photo_url ?? undefined}
            alt=""
            referrerPolicy="no-referrer"
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
            onError={() => setPhotoFailed(true)}
          />
        )}
        {!showPhoto && (
          <div style={{ width: '100%', height: '100%', background: 'var(--bg-elevated)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--t4)', fontSize: 13 }}>
            Sin foto disponible
          </div>
        )}
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.55) 0%, transparent 45%)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: 14, left: 16, display: 'flex', alignItems: 'baseline', gap: 12 }}>
          <span style={{ fontSize: 28, fontWeight: 900, color: '#fff', textShadow: '0 2px 6px rgba(0,0,0,0.5)' }}>{formatPrice(vehicle.price, vehicle.currency)}</span>
          <span style={{ fontSize: 12, fontWeight: 700, color: '#fff', background: days >= 90 ? 'rgba(225,29,72,0.75)' : 'rgba(5,150,105,0.75)', padding: '3px 10px', borderRadius: 999 }}>
            {days} días en stock
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 18, flexWrap: 'wrap' }}>
        <a
          href={vehicle.deep_link} target="_blank" rel="noopener noreferrer"
          style={{ display: 'flex', flexDirection: 'column', gap: 1, padding: '10px 18px', borderRadius: 10, background: 'var(--c-blue)', color: '#fff', textDecoration: 'none' }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 700 }}><ExternalLink style={{ width: 13, height: 13 }} /> Ver anuncio original</span>
          <span style={{ fontSize: 10.5, opacity: 0.85 }}>{hostnameOf(vehicle.deep_link)}</span>
        </a>
        <button onClick={() => copy(vehicle.deep_link, 'Enlace copiado')} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderRadius: 10, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
          <Copy style={{ width: 13, height: 13 }} /> Copiar enlace
        </button>
        <button onClick={() => copy(vehicle.vehicle_ulid, 'ULID copiado')} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', borderRadius: 10, background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
          <Copy style={{ width: 13, height: 13 }} /> Copiar ULID
        </button>
      </div>

      <Tabs
        value={tab}
        onValueChange={v => setTab(v as TabKey)}
        items={[
          {
            value: 'ficha',
            label: 'Ficha',
            content: (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                {([
                  { k: 'Año', v: vehicle.year ?? '—' },
                  { k: 'Kilometraje', v: formatKm(vehicle.km) },
                  { k: 'Combustible', v: vehicle.fuel ?? '—' },
                  { k: 'Cambio', v: vehicle.transmission ?? '—' },
                  { k: 'Precio', v: formatPrice(vehicle.price, vehicle.currency) },
                  { k: 'Estado', v: <VehicleStatusBadge status={vehicle.status === 'available' ? 'listed' : vehicle.status} /> },
                  { k: 'En stock (detectado)', v: `${days} días`, tip: 'Días desde que CARDEEP detectó este anuncio por primera vez' },
                  { k: 'Primera detección', v: new Date(vehicle.first_seen).toLocaleDateString('es-ES') },
                  { k: 'Última vez visto', v: new Date(vehicle.last_seen).toLocaleDateString('es-ES') },
                ] satisfies { k: string; v: ReactNode; tip?: string }[]).map(({ k, v, tip }) => (
                  <div key={k} title={tip} style={{ padding: '12px 14px', background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', borderRadius: 10 }}>
                    <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--t3)', marginBottom: 5 }}>{k}</p>
                    <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--t1)' }}>{v}</p>
                  </div>
                ))}
              </div>
            ),
          },
          {
            value: 'historial',
            label: 'Historial',
            content: historyError
              ? <EmptyState title="No se pudo cargar el historial" message={historyError} />
              : history === null
                ? <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}><CardSkeleton /><CardSkeleton /></div>
                : <Timeline flat items={history.map((e, i) => eventToTimelineItem(e, i, now))} emptyMessage="Sin eventos registrados para este vehículo." />,
          },
          {
            value: 'plataformas',
            label: 'Plataformas',
            content: platformsError
              ? <EmptyState title="No se pudo cargar las plataformas" message={platformsError} />
              : platforms === null
                ? <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}><CardSkeleton /><CardSkeleton /></div>
                : platforms.platforms.length === 0
                  ? <EmptyState title="Sin publicaciones cruzadas detectadas" />
                  : (
                    <div>
                      <p style={{ fontSize: 12, color: 'var(--t3)', marginBottom: 10 }}>
                        Publicado en {platforms.platforms.length} plataforma{platforms.platforms.length === 1 ? '' : 's'} · dealer: {platforms.vehicle.owning_dealer.name}
                      </p>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {platforms.platforms.map((p, i) => {
                          const diff = p.platform_price !== null && vehicle.price !== null ? p.platform_price - vehicle.price : null
                          return (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', borderRadius: 10 }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--t1)' }}>{p.trade_name ?? p.cdp_code}</span>
                                {p.is_tier1 && <span style={{ display: 'flex', alignItems: 'center', gap: 3, fontSize: 10, fontWeight: 700, color: 'var(--c-blue)' }}><ShieldCheck style={{ width: 10, height: 10 }} /> Tier 1</span>}
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                {p.platform_price !== null && (
                                  <span style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--t1)' }}>
                                    {formatPrice(p.platform_price, 'EUR')}
                                    {diff !== null && diff !== 0 && (
                                      <span style={{ marginLeft: 5, fontSize: 11, color: diff > 0 ? 'var(--c-amber)' : 'var(--c-emerald)' }}>
                                        ({diff > 0 ? '+' : ''}{formatPrice(diff, 'EUR')})
                                      </span>
                                    )}
                                  </span>
                                )}
                                {p.listing_url && (
                                  <a href={p.listing_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--t3)', display: 'flex' }}>
                                    <ExternalLink style={{ width: 13, height: 13 }} />
                                  </a>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  ),
          },
        ]}
      />
    </Modal>
  )
}
