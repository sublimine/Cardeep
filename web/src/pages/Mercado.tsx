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
import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { AlertTriangle, HelpCircle, Info, Minus, PackageX, TrendingDown, TrendingUp } from 'lucide-react'
import Card from '../components/Card'
import Table from '../components/Table'
import Button from '../components/Button'
import { Badge } from '../components/Badge'
import EmptyState from '../components/EmptyState'
import { Skeleton } from '../components/Skeleton'
import { PageSkeleton } from '../components/LoadingSpinner'
import { useAuthContext } from '../auth/AuthContext'
import { useDealerInventory } from './inventory/useDealerInventory'
import ClaimDealerPrompt from './inventory/ClaimDealerPrompt'
import { daysInStock, formatPrice } from './inventory/derive'
import { fetchPricePosition, getCachedPricePosition } from './inventory/pricePositionCache'
import { cardeep, type MarketSegmentStats, type PricePosition, type PricePositionBand, type VehicleListItem } from '../api/cardeep'
import { ACCENT, GOOD, WARN } from '../lib/theme'

// K12 — "aged" frontier [RESEARCH §2.2-2], same threshold already used for the
// STALE_DAYS chip elsewhere — recalibration against the real ES census is a
// declared future step (carta §9 F4 close criterion), not silently invented here.
const CAPITAL_PARADO_THRESHOLD_DAYS = 45

// Reference turn benchmark cited in the carta (§2.2-4) — shown as CONTEXT for K11,
// never substituted for the real per-segment number.
const REFERENCE_TURN_DAYS = [43, 48] as const

interface SegmentKey { make: string; model: string; year: number; fuel: string }
type SegmentRow = { key: SegmentKey; count: number }

function segmentKeyOf(v: VehicleListItem): SegmentKey | null {
  if (!v.make || !v.model || !v.year || !v.fuel) return null
  return { make: v.make, model: v.model, year: v.year, fuel: v.fuel }
}

function segmentCacheKey(k: SegmentKey): string {
  return `${k.make}::${k.model}::${k.year}::${k.fuel}`
}

// ── Animated total — mirrors the house AnimNum pattern (Inteligencia/Api/
// Analitica/Arbitrage/Motor) but formats through `formatPrice` instead of a raw
// prefix/suffix, so grouping + currency placement (es-ES: "12.345 €") stays
// correct for capital-parado totals that can run into six figures. Counts up
// from 0 on first real mount, then smoothly re-interpolates as more inventory
// pages stream in and the total grows — never mounted while `nPriced === 0`
// (caller shows the honest "—" instead, per the CountUp doctrine).
function AnimatedEuro({ value }: { value: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 16 })
  const display = useTransform(sp, v => formatPrice(Math.round(v), 'EUR'))
  useEffect(() => { mv.set(value) }, [value, mv])
  return <motion.span className="tabular-nums">{display}</motion.span>
}

// K9 bands — status is reserved and ships with an icon + label, never color
// alone (dataviz rule). below/above market reuse the house GOOD/WARN status
// tokens (exact hex match to the old local BELOW_MARKET_COLOR/#d97706
// literals); at-market/sin-datos stay in neutral text tokens — they are not a
// status, just "nothing to flag".
const K9_BANDS: { key: PricePositionBand | 'sin_datos'; label: string; color: string; Icon: typeof TrendingDown }[] = [
  { key: 'below_market', label: 'Bajo mercado', color: GOOD, Icon: TrendingDown },
  { key: 'at_market', label: 'En mercado', color: 'var(--text-secondary)', Icon: Minus },
  { key: 'above_market', label: 'Sobre mercado', color: WARN, Icon: TrendingUp },
  { key: 'sin_datos', label: 'Muestra insuficiente / sin dato', color: 'var(--text-muted)', Icon: HelpCircle },
]

// Per-segment row state for the K10/K11 table — one place for the "loading vs
// insufficient sample vs real" branch so all three data columns (K10/K11/
// Muestra) agree on it instead of re-deriving the condition three times.
type SegmentRowState = 'loading' | 'insufficient' | MarketSegmentStats

function segmentRowState(ck: string, stats: Map<string, MarketSegmentStats | 'error'>): SegmentRowState {
  const stat = stats.get(ck)
  if (stat === undefined) return 'loading'
  if (stat === 'error') return 'insufficient'
  if (!stat.metrics.M4 && !stat.metrics.M3) return 'insufficient'
  return stat
}

export default function Mercado() {
  const { user } = useAuthContext()
  const cdp = user?.tenantId || null
  if (!cdp) return <ClaimDealerPrompt />
  return <MercadoForDealer cdp={cdp} />
}

function MercadoForDealer({ cdp }: { cdp: string }) {
  const { entity, vehicles, isComplete, loading, error, reload } = useDealerInventory(cdp)
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
    const map = new Map<string, SegmentRow>()
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
    return (
      <div className="p-6">
        <EmptyState
          icon={<AlertTriangle className="h-6 w-6" />}
          title="No se pudo cargar el mercado"
          message={error}
          action={<Button onClick={reload}>Reintentar</Button>}
        />
      </div>
    )
  }

  const k9Total = available.length
  const k9Pct = (n: number) => (k9Total > 0 ? Math.round((n / k9Total) * 100) : 0)
  const scanning = available.length > 0 && positionsScanned < available.length

  return (
    <div className="mx-auto flex flex-col gap-5" style={{ padding: 'clamp(16px, 3vw, 24px)', maxWidth: 1200 }}>
      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <h1 className="text-[22px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>Mercado</h1>
        <p className="mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
          {entity?.trade_name ?? 'Tu flota'} vs la mediana del censo cross-platform — sin que nadie comparta datos
        </p>
      </motion.div>

      {/* K12 — Capital parado */}
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}>
        <Card hover className="!p-[18px_20px]">
          <div className="flex items-center gap-2 mb-1">
            <PackageX style={{ width: 15, height: 15, color: 'var(--text-secondary)' }} />
            <span className="text-[11px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-secondary)' }}>
              Capital parado (+{CAPITAL_PARADO_THRESHOLD_DAYS}d en stock)
            </span>
          </div>
          <p className="text-3xl font-extrabold" style={{ color: 'var(--text-primary)' }}>
            {capitalParado.nPriced > 0 ? <AnimatedEuro value={capitalParado.total} /> : '—'}
          </p>
          <p className="text-[11px] mt-1" style={{ color: 'var(--text-muted)' }}>
            <span className="tabular-nums">{capitalParado.nAged}</span> coche(s) con más de {CAPITAL_PARADO_THRESHOLD_DAYS} días en stock
            {capitalParado.nExcluded > 0 && <> · <span className="tabular-nums">{capitalParado.nExcluded}</span> sin precio (excluidos de la suma)</>}
          </p>
        </Card>
      </motion.div>

      {/* K9 — Distribución de posición de precio */}
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}>
        <Card className="!p-[18px_20px]">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Posición de precio de tu flota (K9)</h2>
              <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                vs la mediana de comparables del censo (make+modelo+año±1+combustible+provincia) — <span className="tabular-nums">{positionsScanned}</span>/<span className="tabular-nums">{available.length}</span> analizados
              </p>
            </div>
            {scanning && (
              <motion.div
                className="h-1.5 w-1.5 shrink-0 rounded-full"
                style={{ background: ACCENT }}
                animate={{ boxShadow: [`0 0 0 3px ${ACCENT}33`, `0 0 0 7px ${ACCENT}00`, `0 0 0 3px ${ACCENT}33`] }}
                transition={{ duration: 2, repeat: Infinity }}
                title="Analizando posición de precio…"
              />
            )}
          </div>
          <div className="flex flex-col gap-2.5">
            {K9_BANDS.map(({ key, label, color, Icon }, i) => {
              const count = k9Distribution[key]
              const pct = k9Pct(count)
              return (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.08 + i * 0.06, duration: 0.3 }}
                  className="-mx-1.5 rounded-lg px-1.5 py-1 transition-colors hover:bg-[var(--bg-hover)]"
                >
                  <div className="mb-1 flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-[11.5px]" style={{ color: 'var(--text-secondary)' }}>
                      <Icon style={{ width: 11, height: 11, color }} />
                      {label}
                    </span>
                    <span className="text-[11.5px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                    <motion.div
                      className="h-full rounded-full"
                      style={{ background: color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ delay: 0.14 + i * 0.06, duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
                    />
                  </div>
                </motion.div>
              )
            })}
          </div>
        </Card>
      </motion.div>

      {/* K10/K11 — Oferta provincial + rotación por segmento */}
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.19, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}>
        <Card className="!p-0">
          <div className="p-[14px_18px]" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Oferta y rotación por segmento (K10/K11)</h2>
            <p className="text-[10.5px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
              Market Days Supply (ventana 45d) y días medianos hasta retirada (ventana 90d) — censo total,
              algo que ningún rival mono-plataforma puede calcular. Turn de referencia del sector: {REFERENCE_TURN_DAYS[0]}-{REFERENCE_TURN_DAYS[1]}d.
            </p>
          </div>
          <div className="px-5 py-3.5">
            {distinctSegments.length === 0 ? (
              <EmptyState title="Sin segmentos suficientes" message="Necesitas make/modelo/año/combustible completos en tu inventario." />
            ) : (
              <Table
                columns={[
                  {
                    key: 'segment',
                    header: 'Segmento',
                    render: (row: SegmentRow) => (
                      <span style={{ color: 'var(--text-primary)', fontSize: 11.5 }}>
                        {`${row.key.make} ${row.key.model} (${row.key.year - 1}-${row.key.year + 1}) · ${row.key.fuel}`}
                      </span>
                    ),
                  },
                  {
                    key: 'fleet_count',
                    header: 'En tu flota',
                    className: 'tabular-nums whitespace-nowrap',
                    render: (row: SegmentRow) => (
                      <span style={{ color: 'var(--text-secondary)', fontSize: 11.5 }}>{row.count}</span>
                    ),
                  },
                  {
                    key: 'k10',
                    header: 'Oferta provincial (K10)',
                    render: (row: SegmentRow) => {
                      const state = segmentRowState(segmentCacheKey(row.key), segmentStats)
                      if (state === 'loading') return <Skeleton className="h-3 w-28" />
                      if (state === 'insufficient') return <span style={{ color: 'var(--text-muted)', fontSize: 11.5 }}>muestra insuficiente (n&lt;8)</span>
                      const m4 = state.metrics.M4
                      return (
                        <span className="tabular-nums" style={{ color: 'var(--text-primary)', fontSize: 11.5 }}>
                          {m4?.value !== undefined ? `${m4.value.toFixed(0)} días de stock` : 'sin rotación observada'}
                          {m4?.fallback_to_national && <Badge color="gray" className="ml-1.5">nacional</Badge>}
                        </span>
                      )
                    },
                  },
                  {
                    key: 'k11',
                    header: 'Rotación (K11)',
                    className: 'tabular-nums whitespace-nowrap',
                    render: (row: SegmentRow) => {
                      const state = segmentRowState(segmentCacheKey(row.key), segmentStats)
                      if (state === 'loading') return <Skeleton className="h-3 w-16" />
                      if (state === 'insufficient') return <span style={{ color: 'var(--text-muted)', fontSize: 11.5 }}>—</span>
                      const m3 = state.metrics.M3
                      return (
                        <span style={{ color: 'var(--text-primary)', fontSize: 11.5 }}>
                          {m3?.value !== undefined ? `${m3.value.toFixed(0)}d mediana` : '—'}
                        </span>
                      )
                    },
                  },
                  {
                    key: 'sample',
                    header: 'Muestra',
                    className: 'tabular-nums whitespace-nowrap',
                    render: (row: SegmentRow) => {
                      const state = segmentRowState(segmentCacheKey(row.key), segmentStats)
                      if (state === 'loading') return <Skeleton className="h-3 w-10" />
                      if (state === 'insufficient') return <span style={{ color: 'var(--text-muted)', fontSize: 11.5 }}>—</span>
                      const m4 = state.metrics.M4
                      const m3 = state.metrics.M3
                      return <span style={{ color: 'var(--text-muted)', fontSize: 11.5 }}>n={m4?.n ?? m3?.n ?? '—'}</span>
                    },
                  },
                ]}
                data={distinctSegments}
                keyExtractor={row => segmentCacheKey(row.key)}
              />
            )}
          </div>
        </Card>
      </motion.div>

      {/* T1 — transparencia (parcial, hueco declarado) */}
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.26, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}>
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
      </motion.div>

      <AnimatePresence>
        {!isComplete && (
          <motion.p
            key="loading-banner"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.25 }}
            className="text-[10.5px] flex items-center gap-1.5"
            style={{ color: 'var(--text-muted)' }}
          >
            <AlertTriangle style={{ width: 11, height: 11 }} /> Cargando inventario completo — los números de arriba crecerán a medida que se cargue el resto de la flota.
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}
