import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import Timeline, { type TimelineItem } from '../../components/Timeline'
import { CardSkeleton } from '../../components/Skeleton'
import EmptyState from '../../components/EmptyState'
import Button from '../../components/Button'
import { cardeep, CardeepApiError, type DeltaEvent } from '../../api/cardeep'
import { relativeDate, formatPrice } from './derive'

function deltaToTimelineItem(e: DeltaEvent, idx: number, now: Date): TimelineItem {
  const date = relativeDate(e.observed_at, now)
  if (e.event_type === 'PRICE_CHANGE') {
    const oldPrice = typeof e.old_value === 'object' && e.old_value !== null ? (e.old_value as Record<string, unknown>).price : undefined
    const newPrice = typeof e.new_value === 'object' && e.new_value !== null ? (e.new_value as Record<string, unknown>).price : undefined
    const subtitle = typeof oldPrice === 'number' && typeof newPrice === 'number'
      ? `${formatPrice(oldPrice, 'EUR')} → ${formatPrice(newPrice, 'EUR')}`
      : undefined
    return { id: String(idx), date, title: 'Cambio de precio', subtitle, accent: 'yellow' }
  }
  if (e.event_type === 'NEW') return { id: String(idx), date, title: 'Alta de anuncio', accent: 'green' }
  if (e.event_type === 'GONE') return { id: String(idx), date, title: 'Baja de anuncio', accent: 'red' }
  return { id: String(idx), date, title: e.event_type, accent: 'gray' }
}

interface ActivityDrawerProps {
  cdp: string
  open: boolean
  onClose: () => void
  now: Date
  onCountLoaded?: (count7d: number) => void
}

export default function ActivityDrawer({ cdp, open, onClose, now, onCountLoaded }: ActivityDrawerProps) {
  const [events, setEvents] = useState<DeltaEvent[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (!open || loaded) return
    setLoading(true)
    cardeep.entityDelta(cdp, 1, 50)
      .then(res => {
        setEvents(res.items)
        setHasMore(res.has_more)
        setLoaded(true)
        const sevenDaysAgo = now.getTime() - 7 * 86_400_000
        onCountLoaded?.(res.items.filter(e => new Date(e.observed_at).getTime() >= sevenDaysAgo).length)
      })
      .catch((err: unknown) => setError(err instanceof CardeepApiError ? err.message : 'Error al cargar la actividad'))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, loaded, cdp])

  const loadMore = () => {
    setLoading(true)
    const nextPage = page + 1
    cardeep.entityDelta(cdp, nextPage, 50)
      .then(res => { setEvents(e => [...e, ...res.items]); setHasMore(res.has_more); setPage(nextPage) })
      .catch((err: unknown) => setError(err instanceof CardeepApiError ? err.message : 'Error al cargar más actividad'))
      .finally(() => setLoading(false))
  }

  const counts = events.reduce((acc, e) => ({ ...acc, [e.event_type]: (acc[e.event_type] ?? 0) + 1 }), {} as Record<string, number>)

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            style={{ position: 'fixed', inset: 0, zIndex: 190, background: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(4px)' }}
          />
          <motion.aside
            initial={{ x: 440 }} animate={{ x: 0 }} exit={{ x: 440 }}
            transition={{ type: 'spring', stiffness: 340, damping: 34 }}
            className="glass-lg"
            style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: 'min(420px, 100vw)', zIndex: 200, padding: 20, overflowY: 'auto', borderLeft: '1px solid var(--border-active)' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 800, color: 'var(--t1)' }}>Actividad</h2>
                <p style={{ fontSize: 11.5, color: 'var(--t4)', marginTop: 2 }}>Flujo de eventos a nivel de inventario</p>
              </div>
              <button onClick={onClose} aria-label="Cerrar actividad" style={{ padding: 6, borderRadius: 8, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t3)', cursor: 'pointer' }}>
                <X style={{ width: 14, height: 14 }} />
              </button>
            </div>

            {loaded && (
              <div style={{ display: 'flex', gap: 12, fontSize: 11, color: 'var(--t3)', margin: '10px 0 16px', paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
                <span>{counts.NEW ?? 0} altas</span>
                <span>{counts.GONE ?? 0} bajas</span>
                <span>{counts.PRICE_CHANGE ?? 0} cambios de precio</span>
              </div>
            )}

            {error ? (
              <EmptyState title="No se pudo cargar la actividad" message={error} />
            ) : !loaded ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}><CardSkeleton /><CardSkeleton /><CardSkeleton /></div>
            ) : (
              <>
                <Timeline flat items={events.map((e, i) => deltaToTimelineItem(e, i, now))} emptyMessage="Sin actividad reciente registrada." />
                {hasMore && (
                  <div style={{ marginTop: 12, textAlign: 'center' }}>
                    <Button variant="secondary" size="sm" loading={loading} onClick={loadMore}>Cargar más</Button>
                  </div>
                )}
              </>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
