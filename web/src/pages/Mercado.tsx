// Mercado — 03-garage-fleet F4 (K9/K10/K11/K12). REPLACES the old Finance.tsx mock
// (100% hardcoded MONTHLY/EXPENSES/TOP_VEHICLES arrays — no P&L exists without
// purchase cost in fleet_ops, carta §6.3: "Sin P&L completo hasta que exista coste
// de compra"). Route/nav label rename is the one atomic touch to App.tsx/Shell.tsx
// this fase makes (00-MASTER.md §5.1 rule 6).
//
// Ownership: K9 (price-to-market) and K10/K11 (Market Days Supply / rotation) are
// COMPUTED BY PILAR 01 (services/api/routers/market.py, M2/M4/M3) — this page only
// consumes them (00-MASTER.md C-1: "un solo cálculo... prohibido un tercer cálculo
// independiente"). K12 (capital parado) is a genuinely NEW, dealer-scoped local
// aggregate (not a segment/cohort metric — it is this dealer's own aged stock).
import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Info, PackageX } from 'lucide-react'
import Card from '../components/Card'
import { Badge } from '../components/Badge'
import EmptyState from '../components/EmptyState'
import { PageSkeleton } from '../components/LoadingSpinner'
import { useAuthContext } from '../auth/AuthContext'
import { useDealerInventory } from './inventory/useDealerInventory'
import ClaimDealerPrompt from './inventory/ClaimDealerPrompt'
import { daysInStock, formatPrice } from './inventory/derive'
import { fetchPricePosition, getCachedPricePosition } from './inventory/pricePositionCache'
import { cardeep, type MarketSegmentStats, type PricePosition, type PricePositionBand, type VehicleListItem } from '../api/cardeep'

// K12 — "aged" frontier [RESEARCH §2.2-2], same threshold already used for the
// STALE_DAYS chip elsewhere — recalibration against the real ES census is a
// declared future step (carta §9 F4 close criterion), not silently invented here.
const CAPITAL_PARADO_THRESHOLD_DAYS = 45

// Reference turn benchmark cited in the carta (§2.2-4) — shown as CONTEXT for K11,
// never substituted for the real per-segment number.
const REFERENCE_TURN_DAYS = [43, 48] as const

const BELOW_MARKET_COLOR = '#059669'

interface SegmentKey { make: string; model: string; year: number; fuel: string }

function segmentKeyOf(v: VehicleListItem): SegmentKey | null {
  if (!v.make || !v.model || !v.year || !v.fuel) return null
  return { make: v.make, model: v.model, year: v.year, fuel: v.fuel }
}

function segmentCacheKey(k: SegmentKey): string {
  return `${k.make}::${k.model}::${k.year}::${k.fuel}`
}

export default function Mercado() {
  const { user } = useAuthContext()
  const cdp = user?.tenantId || null
  if (!cdp) return <ClaimDealerPrompt />
  return <MercadoForDealer cdp={cdp} />
}

function MercadoForDealer({ cdp }: { cdp: string }) {
  const { entity, vehicles, isComplete, loading, error } = useDealerInventory(cdp)
  const [now] = useState(() => new Date())

  const available = useMemo(() => vehicles.filter(v => v.status === 'available'), [vehicles])

  // K12 — capital parado: real aggregate over the dealer's OWN loaded fleet.
  const capitalParado = useMemo(() => {
    const aged = available.filter(v => daysInStock(v.first_seen, now) > CAPITAL_PARADO_THRESHOLD_DAYS)
    const priced = aged.filter(v => v.price !== null)
    const total = priced.reduce((s, v) => s + (v.price ?? 0), 0)
    return { total, nPriced: priced.length, nExcluded: aged.length - priced.length, nAged: aged.length }
  }, [available, now])

  // K9 — fleet-wide price-position distribution. Fetches every AVAILABLE vehicle's
  // position ONCE (shared cache with the Mi Flota table badge — a vehicle already
  // viewed there is never re-fetched here), bounded concurrency so a 468-car fleet
  // doesn't fire 468 simultaneous requests.
  const [positions, setPositions] = useState<Map<string, PricePosition>>(new Map())
  const [positionsScanned, setPositionsScanned] = useState(0)
  useEffect(() => {
    if (available.length === 0) return
    let cancelled = false
    const CONCURRENCY = 6
    let idx = 0
    async function worker() {
      for (;;) {
        if (cancelled) return
        const i = idx++
        if (i >= available.length) return
        const v = available[i]
        const cached = getCachedPricePosition(v.vehicle_ulid)
        if (cached) {
          if (!cancelled) { setPositions(prev => new Map(prev).set(v.vehicle_ulid, cached)); setPositionsScanned(n => n + 1) }
          continue
        }
        try {
          const data = await fetchPricePosition(v.vehicle_ulid)
          if (!cancelled) setPositions(prev => new Map(prev).set(v.vehicle_ulid, data))
        } catch {
          // Honest skip: a failed lookup is absent from the distribution, never fabricated.
        } finally {
          if (!cancelled) setPositionsScanned(n => n + 1)
        }
      }
    }
    const workers = Array.from({ length: Math.min(CONCURRENCY, available.length) }, () => worker())
    void workers
    return () => { cancelled = true }
  }, [available])

  const k9Distribution = useMemo(() => {
    const counts: Record<PricePositionBand | 'sin_datos', number> = { below_market: 0, at_market: 0, above_market: 0, sin_datos: 0 }
    for (const v of available) {
      const pos = positions.get(v.vehicle_ulid)
      if (!pos || pos.position === null) counts.sin_datos += 1
      else counts[pos.position.band] += 1
    }
    return counts
  }, [available, positions])

  // K10/K11 — per DISTINCT segment present in the fleet (never per-vehicle: this
  // is a segment-level aggregate, so the call count is bounded by how many
  // distinct make+model+year+fuel combos the dealer actually stocks, not by
  // fleet size — the "sin N+1" requirement of carta §9 F4).
  const distinctSegments = useMemo(() => {
    const map = new Map<string, { key: SegmentKey; count: number }>()
    for (const v of available) {
      const key = segmentKeyOf(v)
      if (!key) continue
      const ck = segmentCacheKey(key)
      const existing = map.get(ck)
      if (existing) existing.count += 1
      else map.set(ck, { key, count: 1 })
    }
    return [...map.values()].sort((a, b) => b.count - a.count)
  }, [available])

  const [segmentStats, setSegmentStats] = useState<Map<string, MarketSegmentStats | 'error'>>(new Map())
  useEffect(() => {
    if (distinctSegments.length === 0 || !entity) return
    const provinceCode = entity.province_code
    let cancelled = false
    const CONCURRENCY = 4
    let idx = 0
    async function worker() {
      for (;;) {
        if (cancelled) return
        const i = idx++
        if (i >= distinctSegments.length) return
        const { key } = distinctSegments[i]
        const ck = segmentCacheKey(key)
        try {
          const data = await cardeep.marketSegmentStats(key.make, key.model, key.year, key.fuel, provinceCode)
          if (!cancelled) setSegmentStats(prev => new Map(prev).set(ck, data))
        } catch {
          if (!cancelled) setSegmentStats(prev => new Map(prev).set(ck, 'error'))
        }
      }
    }
    const workers = Array.from({ length: Math.min(CONCURRENCY, distinctSegments.length) }, () => worker())
    void workers
    return () => { cancelled = true }
  }, [distinctSegments, entity])

  if (loading && vehicles.length === 0 && !error) return <PageSkeleton />
  if (error && vehicles.length === 0) {
    return <div className="p-6"><EmptyState title="No se pudo cargar el mercado" message={error} /></div>
  }

  const k9Total = available.length
  const k9Pct = (n: number) => (k9Total > 0 ? Math.round((n / k9Total) * 100) : 0)

  return (
    <div className="mx-auto flex flex-col gap-5" style={{ padding: 'clamp(16px, 3vw, 24px)', maxWidth: 1200 }}>
      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <h1 className="text-[22px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>Mercado</h1>
        <p className="mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
          {entity?.trade_name ?? 'Tu flota'} vs la mediana del censo cross-platform — sin que nadie comparta datos
        </p>
      </motion.div>

      {/* K12 — Capital parado */}
      <Card className="!p-[18px_20px]">
        <div className="flex items-center gap-2 mb-1">
          <PackageX style={{ width: 15, height: 15, color: 'var(--text-secondary)' }} />
          <span className="text-[11px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-secondary)' }}>
            Capital parado (+{CAPITAL_PARADO_THRESHOLD_DAYS}d en stock)
          </span>
        </div>
        <p className="text-3xl font-extrabold" style={{ color: 'var(--text-primary)' }}>
          {capitalParado.nPriced > 0 ? formatPrice(capitalParado.total, 'EUR') : '—'}
        </p>
        <p className="text-[11px] mt-1" style={{ color: 'var(--text-muted)' }}>
          {capitalParado.nAged} coche(s) con más de {CAPITAL_PARADO_THRESHOLD_DAYS} días en stock
          {capitalParado.nExcluded > 0 && ` · ${capitalParado.nExcluded} sin precio (excluidos de la suma)`}
        </p>
      </Card>

      {/* K9 — Distribución de posición de precio */}
      <Card className="!p-[18px_20px]">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Posición de precio de tu flota (K9)</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
              vs la mediana de comparables del censo (make+modelo+año±1+combustible+provincia) — {positionsScanned}/{available.length} analizados
            </p>
          </div>
        </div>
        <div className="flex flex-col gap-2.5">
          {([
            ['below_market', 'Bajo mercado', BELOW_MARKET_COLOR],
            ['at_market', 'En mercado', 'var(--text-secondary)'],
            ['above_market', 'Sobre mercado', '#d97706'],
            ['sin_datos', 'Muestra insuficiente / sin dato', 'var(--text-muted)'],
          ] as [keyof typeof k9Distribution, string, string][]).map(([key, label, color]) => (
            <div key={key}>
              <div className="mb-1 flex items-center justify-between">
                <span className="text-[11.5px]" style={{ color: 'var(--text-secondary)' }}>{label}</span>
                <span className="text-[11.5px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>
                  {k9Distribution[key]} ({k9Pct(k9Distribution[key])}%)
                </span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                <div className="h-full rounded-full" style={{ width: `${k9Pct(k9Distribution[key])}%`, background: color }} />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* K10/K11 — Oferta provincial + rotación por segmento */}
      <Card className="!p-0">
        <div className="p-[14px_18px]" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Oferta y rotación por segmento (K10/K11)</h2>
          <p className="text-[10.5px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Market Days Supply (ventana 45d) y días medianos hasta retirada (ventana 90d) — censo total,
            algo que ningún rival mono-plataforma puede calcular. Turn de referencia del sector: {REFERENCE_TURN_DAYS[0]}-{REFERENCE_TURN_DAYS[1]}d.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-xs" style={{ minWidth: 640 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                {['Segmento', 'En tu flota', 'Oferta provincial (K10)', 'Rotación (K11)', 'Muestra'].map(h => (
                  <th key={h} className="p-[9px_16px] text-left text-[9.5px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-muted)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {distinctSegments.map(({ key, count }) => {
                const ck = segmentCacheKey(key)
                const stat = segmentStats.get(ck)
                const label = `${key.make} ${key.model} (${key.year - 1}-${key.year + 1}) · ${key.fuel}`
                if (stat === undefined) {
                  return (
                    <tr key={ck} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td className="p-[10px_16px]" style={{ color: 'var(--text-primary)' }}>{label}</td>
                      <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>{count}</td>
                      <td className="p-[10px_16px]" colSpan={3} style={{ color: 'var(--text-muted)' }}>cargando…</td>
                    </tr>
                  )
                }
                if (stat === 'error' || !stat.metrics.M4 && !stat.metrics.M3) {
                  return (
                    <tr key={ck} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td className="p-[10px_16px]" style={{ color: 'var(--text-primary)' }}>{label}</td>
                      <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>{count}</td>
                      <td className="p-[10px_16px]" colSpan={3} style={{ color: 'var(--text-muted)' }}>muestra insuficiente (n&lt;8)</td>
                    </tr>
                  )
                }
                const m4 = stat.metrics.M4
                const m3 = stat.metrics.M3
                return (
                  <tr key={ck} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td className="p-[10px_16px]" style={{ color: 'var(--text-primary)' }}>{label}</td>
                    <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>{count}</td>
                    <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-primary)' }}>
                      {m4?.value !== undefined ? `${m4.value.toFixed(0)} días de stock` : 'sin rotación observada'}
                      {m4?.fallback_to_national && <Badge color="gray" className="ml-1.5">nacional</Badge>}
                    </td>
                    <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-primary)' }}>
                      {m3?.value !== undefined ? `${m3.value.toFixed(0)}d mediana` : '—'}
                    </td>
                    <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
                      n={m4?.n ?? m3?.n ?? '—'}
                    </td>
                  </tr>
                )
              })}
              {distinctSegments.length === 0 && (
                <tr><td colSpan={5} className="p-[16px]"><EmptyState title="Sin segmentos suficientes" message="Necesitas make/modelo/año/combustible completos en tu inventario." /></td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* T1 — transparencia (parcial, hueco declarado) */}
      <Card className="!p-[16px_18px]">
        <div className="flex items-start gap-2.5">
          <Info style={{ width: 14, height: 14, color: 'var(--text-muted)', marginTop: 1, flexShrink: 0 }} />
          <div>
            <p className="text-[11.5px] font-semibold" style={{ color: 'var(--text-secondary)' }}>Cómo se calcula (T1)</p>
            <p className="text-[10.5px] mt-1 leading-relaxed" style={{ color: 'var(--text-muted)' }}>
              Comparable = mismo make+modelo, año±1, mismo combustible, misma provincia (o nacional si la
              provincia no tiene muestra suficiente). n≥8 obligatorio o el dato no se muestra. K9 = tu precio ÷
              mediana del comparable (01-market-intelligence, M2). K10 = coches disponibles ÷ (bajas/90d) del
              segmento en 45 días (M4). K11 = mediana de días hasta retirada del segmento en 90 días (M3).
              <br />
              <strong>Hueco declarado:</strong> la muestra enlazable de coches reales de comparación (deep_links)
              aún no la sirve el motor de mercado (services/api/routers/market.py, propiedad de
              01-market-intelligence) — pendiente de una fase futura de ese pilar, no de este.
            </p>
          </div>
        </div>
      </Card>

      {!isComplete && (
        <p className="text-[10.5px] flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
          <AlertTriangle style={{ width: 11, height: 11 }} /> Cargando inventario completo — los números de arriba crecerán a medida que se cargue el resto de la flota.
        </p>
      )}
    </div>
  )
}
