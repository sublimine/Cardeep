// 04-arbitrage F3: real backend wiring (F0-F2 sealed the mock — see plans/cardeep-omni/04-arbitrage.md).
// Every number on this page is either fetched live from /arbitrage/* or a client-side transform of a
// fetched number (e.g. a 0-100 gauge derived from a real z-score) — zero hardcoded business literals.
// The /terminal cross-border mock this carta's §9 F0 targeted was already demolished by 09-Fase0
// (verified: web/src/pages/terminal/ does not exist, no /terminal route in App.tsx) — F0 needed no
// further action here.
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import {
  ArrowUpRight, ArrowDownRight, ExternalLink, MapPin, Info,
} from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip as ChartTooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import Card from '../components/Card'
import PremiumGate from '../components/PremiumGate'
import EmptyState from '../components/EmptyState'
import { TableSkeleton } from '../components/Skeleton'
import { useIsDark } from '../hooks/useIsDark'
import { useAuthContext } from '../auth/AuthContext'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'
import type { Plan } from '../types'
import {
  cardeep, CardeepApiError,
  type DealScoreItem, type DesyncItem, type ArbitrageSummary,
  type TimeCurves, type GeoArbitrageResponse, type DealBand,
} from '../api/cardeep'

// ── Animated number ────────────────────────────────────────────────────────────

function AnimNum({ to, prefix = '', suffix = '', decimals = 0 }: { to: number; prefix?: string; suffix?: string; decimals?: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(sp, v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

function fmtEur(n: number): string {
  return `€${Math.round(n).toLocaleString('es-ES')}`
}

// ── MetricCard ─────────────────────────────────────────────────────────────────

interface MetricCardProps {
  label: string; value: number | null; prefix?: string; suffix?: string; decimals?: number
  sub: string; loading: boolean; emptyReason?: string | null; delay?: number
}

function MetricCard({ label, value, prefix, suffix, decimals, sub, loading, emptyReason, delay = 0 }: MetricCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}>
      <Card hover className="!p-5">
        <div className="mb-3.5 flex items-center justify-between">
          <span className="text-[9.5px] font-bold uppercase tracking-[0.11em]" style={{ color: 'var(--text-secondary)' }}>{label}</span>
          <div className="h-1.5 w-1.5 rounded-full" style={{ background: ACCENT, boxShadow: `0 0 6px ${ACCENT}` }} />
        </div>
        <div className="mb-1 text-[40px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>
          {loading ? (
            <span className="inline-block h-9 w-20 animate-pulse rounded-md" style={{ background: 'var(--glass-medium)' }} />
          ) : value === null ? (
            <span className="text-[16px] font-semibold" style={{ color: 'var(--text-muted)' }}>—</span>
          ) : (
            <AnimNum to={value} prefix={prefix} suffix={suffix} decimals={decimals} />
          )}
        </div>
        <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
          {value === null && !loading && emptyReason ? emptyReason : sub}
        </div>
      </Card>
    </motion.div>
  )
}

// ── ChollosPanel — real deal-score ranking ──────────────────────────────────────

function dealScoreGauge(z: number): number {
  // Transparent client-side transform of the real z the API returns (never an
  // invented number): |z| relative to the price_trap frontier (6.0), clamped 0-100.
  return Math.min(100, Math.round((Math.abs(z) / 6) * 100))
}

function ChollosPanel({ deals, loading, error }: { deals: DealScoreItem[] | null; loading: boolean; error: string | null }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 flex shrink-0 items-start justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Chollos de reposición</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>precio vs mediana de su cohorte, ahorro € descendente</p>
          </div>
        </div>

        {loading && <TableSkeleton rows={5} />}
        {!loading && error && (
          <EmptyState title="No se pudo cargar" message={error} />
        )}
        {!loading && !error && deals !== null && deals.length === 0 && (
          <EmptyState
            title="Sin chollos ahora mismo"
            message="Ningún vehículo del censo servible supera el umbral z ≤ −2.0 con datos frescos (≤7 días) en este momento."
          />
        )}
        {!loading && !error && deals !== null && deals.length > 0 && (
          <div className="flex flex-1 flex-col gap-[7px] overflow-y-auto">
            {deals.map((deal, i) => {
              const sc = deal.band === 'chollo_fuerte' ? GOOD : WARN
              const gauge = dealScoreGauge(deal.z)
              return (
                <motion.a
                  key={deal.vehicle_ulid}
                  href={deal.deep_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.05 + i * 0.04, duration: 0.3 }}
                  className="flex items-center gap-[11px] rounded-xl p-[9px_11px] no-underline"
                  style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderLeft: `2px solid ${sc}` }}
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[9px]" style={{ background: `${sc}16`, border: `1px solid ${sc}28` }}>
                    <span className="text-[12px] font-extrabold tabular-nums tracking-[-0.02em]" style={{ color: sc }}>{gauge}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {deal.title ?? `${deal.make} ${deal.model} (${deal.year ?? '—'})`}
                    </div>
                    <div className="mt-px flex items-center gap-1 text-[10px]" style={{ color: 'var(--text-muted)' }}>
                      <MapPin className="h-2.5 w-2.5" />
                      {deal.province_code ?? '—'} · {deal.days_on_market.toFixed(0)}d · frente a {deal.cohort.n} iguales
                      {!deal.fresh && <span style={{ color: WARN }}> · sin re-verificar</span>}
                    </div>
                  </div>
                  <div className="shrink-0 text-right">
                    <div className="text-[13px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>
                      {deal.price !== null ? fmtEur(deal.price) : '—'}
                    </div>
                    <div className="mt-px text-[10px] font-bold" style={{ color: sc }}>
                      −{fmtEur(deal.savings_eur)} margen
                    </div>
                  </div>
                  <ExternalLink className="h-3 w-3 shrink-0" style={{ color: 'var(--text-muted)' }} />
                </motion.a>
              )
            })}
          </div>
        )}
      </div>
    </Card>
  )
}

// ── DesyncPanel — dealer<->platform price desync (honest rename of the old "gap
// cross-platform" mock, per §4.2: real cross-platform gap stays gated until F6) ──

function DesyncPanel({ items, loading, error }: { items: DesyncItem[] | null; loading: boolean; error: string | null }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Desync dealer↔plataforma</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
            mismo coche, precio distinto en su web vs el portal
          </p>
        </div>

        {loading && <TableSkeleton rows={3} />}
        {!loading && error && <EmptyState title="No se pudo cargar" message={error} />}
        {!loading && !error && items !== null && items.length === 0 && (
          <EmptyState
            title="Sin desyncs frescos"
            message="Ningún par dealer↔plataforma con delta ≥1% y ≥100€ verificado en las últimas 72h."
          />
        )}
        {!loading && !error && items !== null && items.length > 0 && (
          <div className="flex flex-1 flex-col overflow-y-auto">
            {items.map((it, i) => (
              <motion.div key={it.vehicle_ulid} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 + i * 0.06, duration: 0.3 }}>
                <div className="mb-[7px] text-[12.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {it.make} {it.model} {it.year ? `(${it.year})` : ''}
                </div>
                <a href={it.dealer.url} target="_blank" rel="noopener noreferrer"
                   className="mb-1 flex items-center justify-between rounded-lg p-[6px_10px] no-underline"
                   style={{ background: `${ACCENT}14`, border: `1px solid ${ACCENT}30` }}>
                  <span className="text-[11px] font-semibold" style={{ color: ACCENT }}>{it.dealer.trade_name ?? it.dealer.cdp_code}</span>
                  <span className="text-[12.5px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{fmtEur(it.dealer.price)}</span>
                </a>
                <a href={it.platform.url} target="_blank" rel="noopener noreferrer"
                   className="mb-2 flex items-center justify-between rounded-lg p-[6px_10px] no-underline"
                   style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
                  <span className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>{it.platform.trade_name ?? it.platform.cdp_code}</span>
                  <span className="text-[12.5px] font-semibold tabular-nums" style={{ color: 'var(--text-secondary)' }}>{fmtEur(it.platform.price)}</span>
                </a>
                <div className="flex items-center gap-[5px]" style={{ marginBottom: i < items.length - 1 ? 16 : 0 }}>
                  {it.dealer.price < it.platform.price
                    ? <ArrowDownRight style={{ width: 10, height: 10, color: GOOD }} />
                    : <ArrowUpRight style={{ width: 10, height: 10, color: BAD }} />}
                  <span className="text-[11.5px] font-bold" style={{ color: GOOD }}>
                    gap {fmtEur(it.delta_eur)}{it.delta_pct !== null ? ` (${it.delta_pct.toFixed(1)}%)` : ''}
                  </span>
                </div>
                {i < items.length - 1 && <div className="mb-4 border-t" style={{ borderColor: 'var(--border-subtle)' }} />}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}

// ── SpreadPanel — honest gap: needs a wholesale partner feed, not just a plan ───
// Unchanged since 01-market-intelligence/04 audit (§4.5 "sin cambio").

function SpreadPanel() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Spread retail vs wholesale</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>margen de flip por modelo</p>
        </div>

        <div className="flex flex-1 flex-col justify-center gap-3 text-center">
          <p className="text-xs leading-[1.6]" style={{ color: 'var(--text-secondary)' }}>
            Requiere un feed de datos de subasta/remate (MMR, BCA, AUTO1…) de un socio wholesale.
            cardeep ya tiene la pata retail — el spread se activa en cuanto exista ese feed.
          </p>
          <span
            className="mx-auto rounded-full px-3 py-1 text-[10.5px] font-semibold"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}
          >
            Pendiente de partnership — no es un dato inventado
          </span>
        </div>
      </div>
    </Card>
  )
}

// ── Cohort selector (shared by TimeArbitrage + Geo panels) ─────────────────────

interface CohortInputProps { make: string; model: string; year: number; onChange: (m: string, mo: string, y: number) => void }

function CohortSelector({ make, model, year, onChange }: CohortInputProps) {
  return (
    <div className="flex shrink-0 flex-wrap gap-1.5">
      <input
        value={make} onChange={e => onChange(e.target.value, model, year)}
        placeholder="Marca" aria-label="Marca"
        className="w-[84px] rounded-lg p-[5px_8px] text-[11px] font-medium outline-none"
        style={{ color: 'var(--text-secondary)', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
      />
      <input
        value={model} onChange={e => onChange(make, e.target.value, year)}
        placeholder="Modelo" aria-label="Modelo"
        className="w-[84px] rounded-lg p-[5px_8px] text-[11px] font-medium outline-none"
        style={{ color: 'var(--text-secondary)', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
      />
      <input
        value={year} type="number" onChange={e => onChange(make, model, Number(e.target.value))}
        aria-label="Año ancla"
        className="w-[64px] rounded-lg p-[5px_8px] text-[11px] font-medium outline-none"
        style={{ color: 'var(--text-secondary)', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
      />
    </div>
  )
}

// ── TimeArbitragePanel — "Ritmo de mercado" (F4, real cycle/decay data) ─────────

function TimeArbitragePanel({ dark, curves, loading, error }: { dark: boolean; curves: TimeCurves | null; loading: boolean; error: string | null }) {
  const gridColor = dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const chartData = curves?.buckets.map(b => ({ bucket: b.bucket_label, relative: Math.round(b.median_relative_price * 100) })) ?? []

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Ritmo de mercado</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>días a salida · curva de decaimiento empírica</p>
        </div>

        {loading && <TableSkeleton rows={3} />}
        {!loading && error && <EmptyState title="No se pudo cargar" message={error} />}

        {!loading && !error && curves && (
          <>
            {curves.cycle_stats ? (
              <div className="mb-2.5 text-[11.5px] leading-[1.5]" style={{ color: 'var(--text-secondary)' }}>
                La mitad de los <strong>{curves.make} {curves.model}</strong> ({curves.year_band_start}-{curves.year_band_start + 1})
                salen del mercado en <strong style={{ color: ACCENT }}>{curves.cycle_stats.median_days_to_gone.toFixed(0)} días</strong>
                {' '}(P25 {curves.cycle_stats.p25_days_to_gone.toFixed(0)}d · P75 {curves.cycle_stats.p75_days_to_gone.toFixed(0)}d) ·{' '}
                {(curves.cycle_stats.pct_price_drop_before_gone * 100).toFixed(0)}% baja de precio antes de salir
                {' '}(n={curves.cycle_stats.n_cycles} ciclos)
              </div>
            ) : (
              <EmptyState
                className="!py-6"
                title="Aún no hay historial suficiente"
                message={curves.cycle_stats_reason ?? undefined}
              />
            )}

            {chartData.length > 0 ? (
              <div className="min-h-0 flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
                    <XAxis dataKey="bucket" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} domain={['dataMin - 5', 'dataMax + 5']} />
                    <ChartTooltip
                      contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                      formatter={(v: number) => [`${v}% del precio inicial`, '']}
                    />
                    <ReferenceLine y={100} stroke={`${ACCENT}61`} strokeDasharray="3 5" strokeWidth={1} />
                    <Line type="monotone" dataKey="relative" stroke={ACCENT} strokeWidth={2.2} dot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} activeDot={{ r: 4 }} name="Precio relativo" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyState className="!py-6" title="Sin curva de decaimiento" message={curves.buckets_reason ?? undefined} />
            )}

            <div className="mt-2 shrink-0 text-[10px] leading-[1.4]" style={{ color: 'var(--text-muted)' }}>{curves.disclaimer}</div>
          </>
        )}
      </div>
    </Card>
  )
}

// ── GeoPanel — "Mapa de precio por provincia" (F5, real cell/gap data) ──────────

function GeoPanel({ geo, loading, error }: { geo: GeoArbitrageResponse | null; loading: boolean; error: string | null }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Mapa de precio por provincia</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>mediana por provincia · rutas de compra significativas</p>
        </div>

        {loading && <TableSkeleton rows={4} />}
        {!loading && error && <EmptyState title="No se pudo cargar" message={error} />}

        {!loading && !error && geo && (
          <div className="flex flex-1 flex-col gap-3 overflow-y-auto">
            {geo.cells.length === 0 ? (
              <EmptyState className="!py-6" title="Sin celdas suficientes" message={geo.cells_reason ?? undefined} />
            ) : (
              <div className="space-y-[3px]">
                {geo.cells.map(c => {
                  const maxPrice = Math.max(...geo.cells.map(x => x.median_price))
                  const pct = (c.median_price / maxPrice) * 100
                  return (
                    <div key={c.province_code} className="flex items-center gap-2 text-[10.5px]">
                      <span className="w-7 shrink-0 font-mono font-semibold" style={{ color: 'var(--text-secondary)' }}>{c.province_code}</span>
                      <div className="h-[14px] flex-1 overflow-hidden rounded-full" style={{ background: 'var(--bg-surface)' }}>
                        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: ACCENT }} />
                      </div>
                      <span className="w-16 shrink-0 text-right font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{fmtEur(c.median_price)}</span>
                      <span className="w-10 shrink-0 text-right" style={{ color: 'var(--text-muted)' }}>n={c.n}</span>
                    </div>
                  )
                })}
              </div>
            )}

            {geo.gaps.length > 0 && (
              <div className="mt-1 border-t pt-2.5" style={{ borderColor: 'var(--border-subtle)' }}>
                <p className="mb-1.5 text-[10px] font-bold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Rutas significativas</p>
                {geo.gaps.slice(0, 5).map((g, i) => (
                  <div key={i} className="mb-1 text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                    <strong style={{ color: GOOD }}>{fmtEur(g.gap_eur)}</strong> más barato en <strong>{g.province_cheap}</strong> que
                    en <strong>{g.province_expensive}</strong> ({g.n_cheap} vs {g.n_expensive} anuncios)
                  </div>
                ))}
              </div>
            )}

            <div className="mt-auto shrink-0 pt-1 text-[10px]" style={{ color: 'var(--text-muted)' }}>{geo.disclaimer}</div>
          </div>
        )}
      </div>
    </Card>
  )
}

// ── Arbitrage ──────────────────────────────────────────────────────────────────

export default function Arbitrage() {
  const dark = useIsDark()
  const { user } = useAuthContext()
  const plan: Plan = user?.plan ?? 'starter'

  const [make, setMake] = useState('')
  const [province, setProvince] = useState('')
  const [band, setBand] = useState<DealBand | ''>('')
  const [minSavings, setMinSavings] = useState<number | ''>('')

  const [summary, setSummary] = useState<ArbitrageSummary | null>(null)
  const [summaryError, setSummaryError] = useState<string | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(true)

  const [deals, setDeals] = useState<DealScoreItem[] | null>(null)
  const [dealsError, setDealsError] = useState<string | null>(null)
  const [dealsLoading, setDealsLoading] = useState(true)

  const [desync, setDesync] = useState<DesyncItem[] | null>(null)
  const [desyncError, setDesyncError] = useState<string | null>(null)
  const [desyncLoading, setDesyncLoading] = useState(true)

  // Cohort selector shared by time-arbitrage + geo panels — default to a real,
  // high-volume segment (Peugeot 208, confirmed n>5000 in the F1 verification log),
  // never a fabricated one; the user can change it freely.
  const [cohortMake, setCohortMake] = useState('Peugeot')
  const [cohortModel, setCohortModel] = useState('208')
  const [cohortYear, setCohortYear] = useState(2024)

  const [curves, setCurves] = useState<TimeCurves | null>(null)
  const [curvesError, setCurvesError] = useState<string | null>(null)
  const [curvesLoading, setCurvesLoading] = useState(true)

  const [geo, setGeo] = useState<GeoArbitrageResponse | null>(null)
  const [geoError, setGeoError] = useState<string | null>(null)
  const [geoLoading, setGeoLoading] = useState(true)

  useEffect(() => {
    let live = true
    setSummaryLoading(true)
    cardeep.arbitrageSummary()
      .then(d => { if (live) setSummary(d) })
      .catch((e: unknown) => { if (live) setSummaryError(e instanceof CardeepApiError ? e.message : 'Error al cargar el resumen') })
      .finally(() => { if (live) setSummaryLoading(false) })
    return () => { live = false }
  }, [])

  useEffect(() => {
    let live = true
    setDealsLoading(true)
    cardeep.arbitrageDeals({
      size: 30,
      make: make || undefined,
      province: province || undefined,
      band: band || undefined,
      minSavings: minSavings === '' ? undefined : minSavings,
    })
      .then(p => { if (live) { setDeals(p.items); setDealsError(null) } })
      .catch((e: unknown) => { if (live) setDealsError(e instanceof CardeepApiError ? e.message : 'Error al cargar los chollos') })
      .finally(() => { if (live) setDealsLoading(false) })
    return () => { live = false }
  }, [make, province, band, minSavings])

  useEffect(() => {
    let live = true
    setDesyncLoading(true)
    cardeep.arbitrageDesync({ size: 6 })
      .then(p => { if (live) { setDesync(p.items); setDesyncError(null) } })
      .catch((e: unknown) => { if (live) setDesyncError(e instanceof CardeepApiError ? e.message : 'Error al cargar los desyncs') })
      .finally(() => { if (live) setDesyncLoading(false) })
    return () => { live = false }
  }, [])

  useEffect(() => {
    let live = true
    if (!cohortMake || !cohortModel || !cohortYear) return
    setCurvesLoading(true)
    cardeep.arbitrageTimeCurves(cohortMake, cohortModel, cohortYear)
      .then(d => { if (live) { setCurves(d); setCurvesError(null) } })
      .catch((e: unknown) => { if (live) setCurvesError(e instanceof CardeepApiError ? e.message : 'Error al cargar el ritmo de mercado') })
      .finally(() => { if (live) setCurvesLoading(false) })
    return () => { live = false }
  }, [cohortMake, cohortModel, cohortYear])

  useEffect(() => {
    let live = true
    if (!cohortMake || !cohortModel || !cohortYear) return
    setGeoLoading(true)
    cardeep.arbitrageGeo(cohortMake, cohortModel, cohortYear)
      .then(d => { if (live) { setGeo(d); setGeoError(null) } })
      .catch((e: unknown) => { if (live) setGeoError(e instanceof CardeepApiError ? e.message : 'Error al cargar el mapa geo') })
      .finally(() => { if (live) setGeoLoading(false) })
    return () => { live = false }
  }, [cohortMake, cohortModel, cohortYear])

  const selectClass = "cursor-pointer rounded-[10px] p-[8px_12px] text-[12.5px] font-semibold outline-none"
  const selectStyle: React.CSSProperties = { color: 'var(--text-secondary)', background: 'var(--bg-elevated)', border: '1px solid var(--border-default)' }

  return (
    <div className="mx-auto p-[24px_24px_40px]" style={{ maxWidth: 1360 }}>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        className="mb-[10px] flex flex-wrap items-end justify-between gap-3.5"
      >
        <div>
          <p className="mb-[5px] font-mono text-[11px] tracking-[0.03em]" style={{ color: 'var(--text-muted)' }}>Censo vivo · oportunidades de reposición</p>
          <h1 className="text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>Reposición</h1>
        </div>

        <div className="flex flex-wrap gap-2">
          <input
            value={make} onChange={e => setMake(e.target.value)} placeholder="Marca" aria-label="Filtrar por marca"
            className={selectClass} style={{ ...selectStyle, width: 100 }}
          />
          <input
            value={province} onChange={e => setProvince(e.target.value)} placeholder="Provincia (28)" aria-label="Filtrar por provincia"
            maxLength={2}
            className={selectClass} style={{ ...selectStyle, width: 110 }}
          />
          <select value={band} onChange={e => setBand(e.target.value as DealBand | '')} className={selectClass} style={selectStyle}>
            <option value="">Todos los badges</option>
            <option value="chollo_fuerte">Chollo fuerte</option>
            <option value="bajo_mercado">Bajo mercado</option>
          </select>
          <select
            value={minSavings} onChange={e => setMinSavings(e.target.value ? Number(e.target.value) : '')}
            className={selectClass} style={selectStyle}
          >
            <option value="">Cualquier margen</option>
            <option value="500">Margen ≥ 500 €</option>
            <option value="1500">Margen ≥ 1.500 €</option>
            <option value="3000">Margen ≥ 3.000 €</option>
          </select>
        </div>
      </motion.div>

      <div className="mb-4 flex items-center gap-1.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>
        <Info className="h-3 w-3 shrink-0" />
        Precios de oferta del censo, verificados a ≤72h. No son precios de transacción.
      </div>

      <div className="mb-4 grid grid-cols-4 gap-3.5">
        <MetricCard label="Chollos activos" value={summary?.chollos_activos ?? null} sub="z ≤ −2.0, datos frescos" loading={summaryLoading} delay={0} />
        <MetricCard label="Ahorro mediano" value={summary?.ahorro_mediano_eur ?? null} prefix="€" sub="mediana de savings_eur" loading={summaryLoading} delay={0.06} />
        <MetricCard label="Desyncs activos" value={summary?.desyncs_activos ?? null} sub="dealer↔plataforma, ≤72h" loading={summaryLoading} delay={0.12} />
        <MetricCard
          label="Mediana días a salida" value={summary?.mediana_dias_a_salida ?? null} suffix="d"
          sub="mediana entre cohortes con historial" loading={summaryLoading}
          emptyReason={summary?.mediana_dias_a_salida_reason} delay={0.18}
        />
      </div>
      {summaryError && <p className="mb-4 text-[11px]" style={{ color: BAD }}>{summaryError}</p>}

      {/* Capa 2 completa (ARBITRAGE.md): un solo unlock para todo el bundle Enterprise. */}
      <PremiumGate feature="sourcing-ranking" userPlan={plan} what="Ranking de chollos, desync y ritmo de mercado completos">
        <div className="grid grid-cols-[3fr_2fr] gap-4">
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ minHeight: 320 }}>
            <ChollosPanel deals={deals} loading={dealsLoading} error={dealsError} />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}>
            <DesyncPanel items={desync} loading={desyncLoading} error={desyncError} />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ minHeight: 280 }}>
            <div className="mb-1.5 flex justify-end">
              <CohortSelector make={cohortMake} model={cohortModel} year={cohortYear} onChange={(m, mo, y) => { setCohortMake(m); setCohortModel(mo); setCohortYear(y) }} />
            </div>
            <TimeArbitragePanel dark={dark} curves={curves} loading={curvesLoading} error={curvesError} />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.40, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ minHeight: 280 }}>
            <GeoPanel geo={geo} loading={geoLoading} error={geoError} />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.46, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ minHeight: 220 }}>
            <SpreadPanel />
          </motion.div>
        </div>
      </PremiumGate>
    </div>
  )
}
