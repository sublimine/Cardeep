// EngineFreshnessStamp — F5 (00-marketplace-engine.md §6a): the dealer-facing freshness/coverage
// stamp. Answers the two questions the carta names explicitly: "¿estos datos son de verdad y son
// de hoy?" and "¿está toda mi competencia aquí o me enseñáis media provincia?". Every number here
// is a real API read (vehicle_event via /entities/{cdp}/delta, /geo/seal) — zero MOCK_*, zero
// hardcoded constant, per the carta's own anti-atrezzo mandate for this pillar.
//
// Self-contained on purpose: Dashboard.tsx is already at the file-size ceiling
// (coding-style.md: ~800 lines typical) — this ships as its own small file, imported with a
// single line, rather than growing that file further.
import { useEffect, useState } from 'react'
import { CheckCircle2, Clock, MapPin } from 'lucide-react'
import Card from './Card'
import { useAuthContext } from '../auth/AuthContext'
import { cardeep, CardeepApiError, type EntityDetail, type ProvinceSeal } from '../api/cardeep'
import { GOOD, WARN, BAD } from '../lib/theme'

function errorMessage(err: unknown): string {
  if (err instanceof CardeepApiError) return err.message
  if (err instanceof Error) return err.message
  return 'Error desconocido al consultar la API de CARDEEP'
}

function freshnessLabel(iso: string | null, now: Date): { text: string; stale: boolean } {
  if (!iso) return { text: 'Sin comprobaciones registradas todavía', stale: true }
  const h = (now.getTime() - new Date(iso).getTime()) / 3_600_000
  const stale = h > 24
  if (h < 1) return { text: 'Inventario comprobado hace unos minutos', stale }
  if (h < 24) return { text: `Inventario comprobado hace ${Math.round(h)} h`, stale }
  const d = Math.floor(h / 24)
  return {
    text: `Última comprobación: ${new Date(iso).toLocaleDateString('es-ES', { day: 'numeric', month: 'long' })} (hace ${d} d)`,
    stale,
  }
}

interface StampData {
  entity: EntityDetail
  lastObservedAt: string | null
  provinceSeal: ProvinceSeal | null
}

function useFreshnessStamp(cdp: string | null) {
  const [data, setData] = useState<StampData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(!!cdp)

  useEffect(() => {
    if (!cdp) { setLoading(false); return }
    let cancelled = false
    setLoading(true); setError(null); setData(null)

    Promise.all([
      cardeep.entity(cdp),
      cardeep.entityDelta(cdp, 1, 1), // most recent event, DESC-ordered by the API
      cardeep.geoSeal(),
    ])
      .then(([entity, delta, seal]) => {
        if (cancelled) return
        const lastObservedAt = delta.items[0]?.observed_at ?? null
        const provinceSeal = entity.province_code
          ? seal.segments.venta?.provinces.find(p => p.province_code === entity.province_code) ?? null
          : null
        setData({ entity, lastObservedAt, provinceSeal })
        setLoading(false)
      })
      .catch((e: unknown) => { if (!cancelled) { setError(errorMessage(e)); setLoading(false) } })

    return () => { cancelled = true }
  }, [cdp])

  return { data, error, loading }
}

export default function EngineFreshnessStamp() {
  const { user } = useAuthContext()
  const cdp = user?.tenantId || null
  const { data, error, loading } = useFreshnessStamp(cdp)
  const [now] = useState(() => new Date())

  if (!cdp) return null // no dealer profile claimed — nothing honest to show here yet
  if (loading) return null // avoid a skeleton flash for a small supplementary strip
  if (error || !data) return null // fails open: the rest of the Dashboard still renders

  const fresh = freshnessLabel(data.lastObservedAt, now)
  const seal = data.provinceSeal

  return (
    <Card className="!p-3.5 mb-3.5">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
        <div className="flex items-center gap-2">
          <Clock className="h-3.5 w-3.5 shrink-0" style={{ color: fresh.stale ? WARN : GOOD }} />
          <span className="text-[11.5px] font-medium" style={{ color: fresh.stale ? WARN : 'var(--text-primary)' }}>
            {fresh.text}
          </span>
        </div>
        {seal && (
          <div className="flex items-center gap-2">
            <MapPin className="h-3.5 w-3.5 shrink-0" style={{ color: 'var(--text-muted)' }} />
            <span className="text-[11.5px]" style={{ color: 'var(--text-secondary)' }}>
              Tu provincia: {seal.numerator}
              {seal.denominator != null ? ` de ${seal.denominator}` : ''} vendedores profesionales
              indexados
              {seal.coverage_pct != null && (
                <> · <strong style={{ color: seal.verdict === 'SELLADO' ? GOOD : seal.verdict === 'PARCIAL' ? WARN : BAD }}>
                  {seal.verdict} al {seal.coverage_pct.toFixed(1)}%
                </strong></>
              )}
            </span>
          </div>
        )}
        {!seal && (
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 shrink-0" style={{ color: 'var(--text-muted)' }} />
            <span className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
              Cobertura de tu provincia aún sin calcular para esta ficha.
            </span>
          </div>
        )}
      </div>
    </Card>
  )
}
