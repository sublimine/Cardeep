// 08-forum-community F5: VehicleAnchorCard + DealerAnchorCard (carta §6.3).
// Badge "DATO VERIFICADO" shows ONLY when BOTH carta §4.2 conditions hold: (1) the target
// still exists in the live census AND (2) the live price matches the independent
// reconstruction from vehicle_event (services/api/routers/forum.py::_verify_anchor).
// Three distinct render states, never conflated:
//   - snapshot empty            -> condition (1) failed: "dato retirado del mercado"
//   - snapshot present, verified=false -> condition (2) failed: price shown with an
//     "última observación" mark, no badge (a real ops alert was already filed server-side)
//   - verified=true             -> full badge
import { ExternalLink, ShieldCheck, AlertTriangle, Store } from 'lucide-react'
import type { PostAnchor } from '../../api/forum'
import { PriceSparkline } from './PriceSparkline'

function VehicleAnchorCard({ anchor }: { anchor: PostAnchor }) {
  const s = anchor.snapshot as {
    make?: string; model?: string; year?: number; price?: number; status?: string
    photo_url?: string; deep_link?: string; last_seen?: string; price_confirmed?: boolean
  }

  const exists = Object.keys(s).length > 0
  if (!exists) {
    return (
      <div className="rounded-lg p-3 text-[12px]" style={{ border: '1px dashed var(--border-subtle)', color: 'var(--text-muted)' }}>
        Dato retirado del mercado — este anuncio ya no existe en el censo.
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 rounded-lg p-3" style={{ border: '1px solid var(--border-subtle)' }}>
      {s.photo_url
        ? <img src={s.photo_url} alt="" className="h-14 w-20 shrink-0 rounded object-cover" style={{ background: 'var(--bg-surface)' }} />
        : <div className="h-14 w-20 shrink-0 rounded" style={{ background: 'var(--bg-surface)' }} />}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <span className="truncate text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>{s.make} {s.model}</span>
          {anchor.verified ? (
            <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[9.5px] font-bold" style={{ background: 'rgba(16,185,129,0.14)', color: '#10b981' }}>
              <ShieldCheck className="h-2.5 w-2.5" /> DATO VERIFICADO
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[9.5px] font-bold" style={{ background: 'rgba(245,158,11,0.14)', color: '#f59e0b' }} title="El precio en vivo no coincide con el histórico registrado">
              <AlertTriangle className="h-2.5 w-2.5" /> última observación
            </span>
          )}
        </div>
        <div className="mt-0.5 flex items-center gap-2 text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          <span>
            {s.year ?? '—'} · {s.price != null ? `${s.price.toLocaleString('es-ES')} €` : 'sin precio'} ·{' '}
            {s.status === 'available' ? 'sigue a la venta' : 'retirado'}
          </span>
          <PriceSparkline vehicleUlid={anchor.anchor_ref} />
        </div>
      </div>
      {s.deep_link && (
        <a href={s.deep_link} target="_blank" rel="noreferrer" className="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-[11px]" style={{ border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}>
          Ver <ExternalLink className="h-3 w-3" />
        </a>
      )}
    </div>
  )
}

function DealerAnchorCard({ anchor }: { anchor: PostAnchor }) {
  const s = anchor.snapshot as { cdp_code?: string; trade_name?: string; stock_available?: number }

  if (!anchor.verified) {
    return (
      <div className="rounded-lg p-3 text-[12px]" style={{ border: '1px dashed var(--border-subtle)', color: 'var(--text-muted)' }}>
        Dealer no encontrado en el censo.
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 rounded-lg p-3" style={{ border: '1px solid var(--border-subtle)' }}>
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md" style={{ background: 'var(--bg-surface)' }}>
        <Store className="h-4 w-4" style={{ color: 'var(--text-muted)' }} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>{s.trade_name ?? s.cdp_code}</div>
        <div className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          {s.cdp_code} · {s.stock_available ?? 0} coches disponibles ahora
        </div>
      </div>
    </div>
  )
}

function ProvinceAnchorChip({ anchor }: { anchor: PostAnchor }) {
  const s = anchor.snapshot as { name?: string }
  return (
    <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px]" style={{ background: 'var(--bg-surface)', color: 'var(--text-secondary)' }}>
      {anchor.verified ? s.name : anchor.anchor_ref}
    </span>
  )
}

export function AnchorCard({ anchor }: { anchor: PostAnchor }) {
  if (anchor.anchor_type === 'vehicle') return <VehicleAnchorCard anchor={anchor} />
  if (anchor.anchor_type === 'entity') return <DealerAnchorCard anchor={anchor} />
  return <ProvinceAnchorChip anchor={anchor} />
}
