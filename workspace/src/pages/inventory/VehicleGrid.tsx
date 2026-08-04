import { motion } from 'framer-motion'
import type { VehicleListItem } from '../../api/cardeep'
import { daysInStock, formatKm, formatPrice } from './derive'
import { STAGGER_CAP, STALE_DAYS } from './config'
import VehiclePhoto from './VehiclePhoto'

function AgePill({ days }: { days: number }) {
  const tone = days < 30 ? { bg: 'rgba(5,150,105,0.85)', text: '#fff' }
    : days < STALE_DAYS ? { bg: 'rgba(217,119,6,0.85)', text: '#fff' }
    : { bg: 'rgba(225,29,72,0.85)', text: '#fff' }
  return (
    <span style={{ position: 'absolute', top: 10, left: 10, padding: '3px 9px', borderRadius: 999, background: tone.bg, color: tone.text, fontSize: 10.5, fontWeight: 800 }}>
      {days}d en stock
    </span>
  )
}

interface VehicleGridProps {
  vehicles: readonly VehicleListItem[]
  onSelect: (ulid: string) => void
  now: Date
}

export default function VehicleGrid({ vehicles, onSelect, now }: VehicleGridProps) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
      {vehicles.map((v, i) => {
        const days = daysInStock(v.first_seen, now)
        return (
          <motion.div
            key={v.vehicle_ulid}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(i, STAGGER_CAP) * 0.03, duration: 0.25, ease: [0.32, 0.72, 0, 1] }}
            onClick={() => onSelect(v.vehicle_ulid)}
            className="vehicle-grid-card"
            style={{
              background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)',
              borderRadius: 14, overflow: 'hidden', cursor: 'pointer', boxShadow: 'var(--shadow-card)',
              transition: 'border-color 0.2s, box-shadow 0.2s, transform 0.2s',
            }}
          >
            <div style={{ aspectRatio: '16/10', position: 'relative', overflow: 'hidden' }}>
              <VehiclePhoto photoUrl={v.photo_url} make={v.make} className="vehicle-grid-photo" />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.60) 0%, transparent 55%)' }} />
              <AgePill days={days} />
              <div style={{ position: 'absolute', bottom: 10, left: 12, right: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <span style={{ fontSize: 13, fontWeight: 800, color: '#fff', textShadow: '0 1px 4px rgba(0,0,0,0.5)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '65%' }}>
                  {v.title ?? `${v.make} ${v.model}`}
                </span>
                <span style={{ fontSize: 16, fontWeight: 900, color: '#fff', textShadow: '0 1px 4px rgba(0,0,0,0.5)' }}>
                  {formatPrice(v.price, v.currency)}
                </span>
              </div>
            </div>
            <div style={{ padding: '10px 12px', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {[v.year, formatKm(v.km), v.fuel, v.transmission].filter(Boolean).map((tag, ti) => (
                <span key={ti} style={{ fontSize: 10.5, fontWeight: 600, padding: '2px 8px', borderRadius: 6, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', color: 'var(--t4)' }}>
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        )
      })}

      <style>{`
        .vehicle-grid-card:hover { transform: translateY(-3px); border-color: rgba(37,99,235,0.30); box-shadow: var(--shadow-card-hover); }
        .vehicle-grid-card:hover .vehicle-grid-photo { transform: scale(1.03); }
        .vehicle-grid-photo { transition: transform 0.3s ease; }
      `}</style>
    </div>
  )
}
