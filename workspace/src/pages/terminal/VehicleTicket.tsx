// 09-trading-terminal F3 — "Ficha de anuncio": a single vehicle's full history
// (/vehicles/{ulid}/history) + its deal-rating (C7, /terminal/{symbol}/rating/{ulid}) — the
// Bloomberg GIP pattern (carta §2.1): the life of THIS car against its market, on click.
import { useEffect, useState } from 'react'
import { AlertTriangle, ExternalLink, History } from 'lucide-react'
import { cardeep, CardeepApiError, type VehicleHistoryEvent, type TerminalRating } from '../../api/cardeep'
import Modal from '../../components/Modal'
import Timeline, { type TimelineItem } from '../../components/Timeline'
import EmptyState from '../../components/EmptyState'
import { Skeleton } from '../../components/Skeleton'
import { GOOD, BAD, WARN } from '../../lib/theme'

interface VehicleTicketProps {
  /** Mount is always live (parent never unmounts this) so Modal's own enter/exit
   * spring animation can actually play — see Terminal.tsx. */
  open: boolean
  symbolKey: string
  vehicleUlid: string
  deepLink: string
  onClose: () => void
}

const BAND_LABEL: Record<string, string> = {
  below_market: 'Por debajo de mercado',
  at_market: 'En mercado',
  above_market: 'Por encima de mercado',
}
const BAND_COLOR: Record<string, string> = { below_market: GOOD, at_market: WARN, above_market: BAD }

export default function VehicleTicket({ open, symbolKey, vehicleUlid, deepLink, onClose }: VehicleTicketProps) {
  const [history, setHistory] = useState<VehicleHistoryEvent[] | null>(null)
  const [rating, setRating] = useState<TerminalRating | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!open || !vehicleUlid) return
    let cancelled = false
    setHistory(null); setRating(null); setError(null)
    cardeep.vehicleHistory(vehicleUlid, 1, 100)
      .then(page => { if (!cancelled) setHistory(page.items) })
      .catch((err: unknown) => { if (!cancelled) setError(err instanceof CardeepApiError ? err.message : 'Error al cargar el historial') })
    cardeep.terminalRating(symbolKey, vehicleUlid)
      .then(r => { if (!cancelled) setRating(r) })
      .catch(() => { /* rating is best-effort — history is the primary content */ })
    return () => { cancelled = true }
  }, [open, symbolKey, vehicleUlid])

  const timelineItems: TimelineItem[] = (history ?? []).map((ev, i) => ({
    id: `${ev.event_type}-${ev.observed_at}-${i}`,
    date: new Date(ev.observed_at).toLocaleDateString('es-ES'),
    title: eventLabel(ev.event_type),
    subtitle: formatDelta(ev) ?? undefined,
    accent: eventAccent(ev.event_type),
  }))

  return (
    <Modal open={open} onClose={onClose} title="Historial del anuncio" size="lg">
      <div className="space-y-4">
        {rating?.position && (
          <div
            className="flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-lg"
            style={{ background: `${BAND_COLOR[rating.position.band]}14`, border: `1px solid ${BAND_COLOR[rating.position.band]}30` }}
          >
            <span className="text-xs text-text-muted">Posición de precio (C7)</span>
            <span className="text-sm font-semibold tabular-nums" style={{ color: BAND_COLOR[rating.position.band] }}>
              {BAND_LABEL[rating.position.band]} ({((rating.position.ratio - 1) * 100).toFixed(1)}%)
            </span>
          </div>
        )}

        <a
          href={deepLink}
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-md text-xs font-medium text-accent-blue glass hover:bg-glass-strong transition-colors duration-150 focus-visible:bg-glass-strong"
        >
          Ver anuncio original <ExternalLink className="w-3.5 h-3.5" />
        </a>

        {error && (
          <EmptyState icon={<AlertTriangle className="w-6 h-6" />} title="No se pudo cargar el historial" message={error} />
        )}

        {!error && history === null && (
          <div className="space-y-3 py-1">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="w-3.5 h-3.5 shrink-0 mt-1.5" rounded="full" />
                <Skeleton className="h-14 flex-1" rounded="md" />
              </div>
            ))}
          </div>
        )}

        {!error && history && history.length === 0 && (
          <EmptyState icon={<History className="w-6 h-6" />} title="Sin eventos" message="Este anuncio no tiene eventos registrados todavía." />
        )}

        {!error && history && history.length > 0 && (
          <Timeline items={timelineItems} flat />
        )}
      </div>
    </Modal>
  )
}

function eventLabel(t: string): string {
  switch (t) {
    case 'NEW': return 'Alta (nuevo anuncio)'
    case 'GONE': return 'Salida del mercado'
    case 'PRICE_CHANGE': return 'Cambio de precio'
    case 'PHOTO_CHANGE': return 'Cambio de foto'
    case 'KM_CHANGE': return 'Cambio de kilometraje'
    default: return t
  }
}

function eventAccent(t: string): NonNullable<TimelineItem['accent']> {
  switch (t) {
    case 'NEW': return 'green'
    case 'GONE': return 'red'
    case 'PRICE_CHANGE': return 'yellow'
    default: return 'gray'
  }
}

/** Renders "old → new" only for the two event types that carry a numeric delta AND
 * only when both values actually parse as finite numbers — never guesses at a shape
 * the API didn't send. */
function formatDelta(ev: VehicleHistoryEvent): string | null {
  if (ev.event_type !== 'PRICE_CHANGE' && ev.event_type !== 'KM_CHANGE') return null
  const a = toFiniteNumber(ev.old_value)
  const b = toFiniteNumber(ev.new_value)
  if (a == null || b == null) return null
  const fmt = (n: number) => Math.round(n).toLocaleString('es-ES')
  return ev.event_type === 'PRICE_CHANGE' ? `€${fmt(a)} → €${fmt(b)}` : `${fmt(a)} km → ${fmt(b)} km`
}

function toFiniteNumber(v: unknown): number | null {
  if (typeof v === 'number' && Number.isFinite(v)) return v
  if (typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v))) return Number(v)
  return null
}
