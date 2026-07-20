import { AnimatePresence, motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, ExternalLink, Maximize2, RotateCw, X } from 'lucide-react'
import type { VehicleListItem } from '../../../api/cardeep'
import { daysInStock, formatKm, formatPrice } from '../derive'
import VehiclePhoto from '../VehiclePhoto'

interface GarageHudProps {
  selected: VehicleListItem | null
  selectedIndex: number
  total: number
  onPrev: () => void
  onNext: () => void
  onOpenDetail: () => void
  onDeselect: () => void
  onResetCamera: () => void
  autoRotate: boolean
  onToggleAutoRotate: () => void
  showHint: boolean
  now: Date
}

export default function GarageHud({
  selected, selectedIndex, total, onPrev, onNext, onOpenDetail, onDeselect,
  onResetCamera, autoRotate, onToggleAutoRotate, showHint, now,
}: GarageHudProps) {
  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
      {/* Camera controls, top-right */}
      <div style={{ position: 'absolute', top: 14, right: 14, display: 'flex', gap: 6, pointerEvents: 'auto' }}>
        <button
          onClick={onToggleAutoRotate}
          aria-pressed={autoRotate}
          title="Rotación automática"
          className="glass-md hud-btn"
          style={{ width: 34, height: 34, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: 'pointer', color: autoRotate ? 'var(--c-blue)' : 'var(--t3)' }}
        >
          <RotateCw style={{ width: 14, height: 14 }} />
        </button>
        <button
          onClick={onResetCamera}
          title="Reset cámara"
          className="glass-md hud-btn"
          style={{ width: 34, height: 34, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: 'pointer', color: 'var(--t3)' }}
        >
          <Maximize2 style={{ width: 14, height: 14 }} />
        </button>
      </div>

      {/* First-interaction hint */}
      <AnimatePresence>
        {showHint && !selected && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'absolute', top: 14, left: 14, fontSize: 11.5, color: 'var(--t4)', padding: '6px 12px', borderRadius: 999 }}
            className="glass-md"
          >
            Arrastra para orbitar · rueda para zoom
          </motion.div>
        )}
      </AnimatePresence>

      {/* Selection mini-card + prev/next, bottom */}
      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 16 }}
            transition={{ type: 'spring', stiffness: 360, damping: 32 }}
            className="glass-md glass-edge"
            style={{
              position: 'absolute', bottom: 16, left: '50%', transform: 'translateX(-50%)',
              display: 'flex', alignItems: 'center', gap: 12, padding: 10, borderRadius: 16,
              pointerEvents: 'auto', maxWidth: 'min(560px, 92vw)',
            }}
          >
            <button onClick={onPrev} title="Anterior" className="hud-btn" style={{ width: 30, height: 30, borderRadius: 9, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <ChevronLeft style={{ width: 15, height: 15 }} />
            </button>

            <div style={{ width: 52, height: 40, borderRadius: 8, overflow: 'hidden', flexShrink: 0 }}>
              <VehiclePhoto photoUrl={selected.photo_url} make={selected.make} />
            </div>

            <div style={{ minWidth: 0, flex: 1 }}>
              <p style={{ fontSize: 12.5, fontWeight: 800, color: 'var(--t1)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {selected.title ?? `${selected.make} ${selected.model}`}
              </p>
              <p className="tabular-nums" style={{ fontSize: 11, color: 'var(--t3)' }}>
                {formatPrice(selected.price, selected.currency)} · {formatKm(selected.km)} · {daysInStock(selected.first_seen, now)}d en stock
              </p>
            </div>

            <span className="tabular-nums" style={{ fontSize: 10.5, color: 'var(--t4)', fontFamily: 'JetBrains Mono, monospace', flexShrink: 0 }}>
              n.º {selectedIndex + 1} de {total}
            </span>

            <button onClick={onOpenDetail} title="Abrir ficha" className="hud-btn-primary" style={{ padding: '7px 12px', borderRadius: 9, background: 'var(--c-blue)', color: '#fff', border: 'none', fontSize: 12, fontWeight: 700, cursor: 'pointer', flexShrink: 0 }}>
              Abrir ficha
            </button>
            <a href={selected.deep_link} target="_blank" rel="noopener noreferrer" title="Anuncio original" className="hud-btn" style={{ width: 30, height: 30, borderRadius: 9, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <ExternalLink style={{ width: 13, height: 13 }} />
            </a>

            <button onClick={onNext} title="Siguiente" className="hud-btn" style={{ width: 30, height: 30, borderRadius: 9, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t2)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <ChevronRight style={{ width: 15, height: 15 }} />
            </button>
            <button onClick={onDeselect} title="Deseleccionar" className="hud-btn" style={{ width: 30, height: 30, borderRadius: 9, background: 'transparent', border: 'none', color: 'var(--t4)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <X style={{ width: 14, height: 14 }} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .hud-btn { transition: background 0.15s, color 0.15s, transform 0.1s; }
        .hud-btn:hover { background: var(--glass-lg); color: var(--t1); }
        .hud-btn:active { transform: scale(0.94); }
        .hud-btn-primary { transition: filter 0.15s, transform 0.1s; }
        .hud-btn-primary:hover { filter: brightness(1.1); }
        .hud-btn-primary:active { transform: scale(0.96); }
      `}</style>
    </div>
  )
}
