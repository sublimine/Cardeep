// 09-trading-terminal F3 — "Ficha de anuncio": a single vehicle's full history
// (/vehicles/{ulid}/history) + its deal-rating (C7, /terminal/{symbol}/rating/{ulid}) — the
// Bloomberg GIP pattern (carta §2.1): the life of THIS car against its market, on click.
import { useEffect, useState } from 'react'
import { X, ExternalLink } from 'lucide-react'
import { cardeep, CardeepApiError, type VehicleHistoryEvent, type TerminalRating } from '../../api/cardeep'
import { GOOD, BAD, WARN } from '../../lib/theme'

interface VehicleTicketProps {
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

export default function VehicleTicket({ symbolKey, vehicleUlid, deepLink, onClose }: VehicleTicketProps) {
  const [history, setHistory] = useState<VehicleHistoryEvent[] | null>(null)
  const [rating, setRating] = useState<TerminalRating | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setHistory(null); setRating(null); setError(null)
    cardeep.vehicleHistory(vehicleUlid, 1, 100)
      .then(page => { if (!cancelled) setHistory(page.items) })
      .catch((err: unknown) => { if (!cancelled) setError(err instanceof CardeepApiError ? err.message : 'Error') })
    cardeep.terminalRating(symbolKey, vehicleUlid)
      .then(r => { if (!cancelled) setRating(r) })
      .catch(() => { /* rating is best-effort — history is the primary content */ })
    return () => { cancelled = true }
  }, [symbolKey, vehicleUlid])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div
        className="w-full max-w-lg max-h-[80vh] overflow-auto rounded-lg bg-glass-heavy border border-border-subtle shadow-card-hover"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
          <h3 className="text-sm font-semibold">Historial del anuncio</h3>
          <button onClick={onClose} className="p-1 rounded hover:bg-glass-medium"><X className="w-4 h-4" /></button>
        </div>

        {rating?.position && (
          <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
            <span className="text-xs text-text-muted">Posición de precio (C7)</span>
            <span className="text-sm font-semibold" style={{ color: BAND_COLOR[rating.position.band] }}>
              {BAND_LABEL[rating.position.band]} ({((rating.position.ratio - 1) * 100).toFixed(1)}%)
            </span>
          </div>
        )}

        {error && <div className="px-4 py-6 text-sm text-text-muted">{error}</div>}
        {!error && history === null && <div className="px-4 py-6 text-sm text-text-muted">Cargando…</div>}
        {!error && history && history.length === 0 && (
          <div className="px-4 py-6 text-sm text-text-muted">Sin eventos registrados.</div>
        )}
        {!error && history && history.length > 0 && (
          <ul className="divide-y divide-border-subtle/50">
            {history.map((ev, i) => (
              <li key={i} className="px-4 py-2 text-xs flex items-center justify-between">
                <span className="font-medium">{eventLabel(ev.event_type)}</span>
                <span className="text-text-muted">{new Date(ev.observed_at).toLocaleDateString('es-ES')}</span>
              </li>
            ))}
          </ul>
        )}

        <a
          href={deepLink} target="_blank" rel="noreferrer"
          className="flex items-center gap-1 px-4 py-3 text-xs text-accent border-t border-border-subtle hover:underline"
        >
          Ver anuncio original <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
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
