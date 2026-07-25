import { motion } from 'framer-motion'
import React, { useCallback, useEffect, useState } from 'react'
import {
  TrendingUp, Target, Globe, MapPin,
  AlertTriangle, Building2, RotateCw,
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip,
  ResponsiveContainer,
} from 'recharts'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import { Skeleton } from '../components/Skeleton'
import ProgressMetricCard, { type SeriesPoint } from '../components/progress-metric-card'
import { useIsDark } from '../hooks/useIsDark'
import { useAuthContext } from '../auth/AuthContext'
import { cardeep, CardeepApiError, type ChannelRadar } from '../api/cardeep'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'

// Shared focus-visible ring — mirrors Button.tsx's own focus treatment and Api.tsx's
// local copy, so every ad-hoc interactive element on this page (range toggle, retry,
// "view full radar" link) matches house style.
const FOCUS_RING = 'outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary'

// Sales chart's two series (revenue/margin) previously used brand ACCENT + the
// status-reserved GOOD — a plain second series is not itself a good/bad status, so
// it must not borrow a status color (dataviz collision rule), and pairing brand blue
// with it isn't validated either: `validate_palette.js "#3b82f6,#0891b2" --mode dark`
// FAILs the normal-vision floor (worst-pair ΔE 12.3, below the 15 hard gate). Indigo
// + teal (tokens.css --c-indigo/--c-teal — the exact pair Api.tsx's consumption chart
// already ships) is the validated categorical pair: `validate_palette.js
// "#4f46e5,#0891b2"` passes every hard check in both modes (dark ships a sub-3:1
// contrast WARN on indigo, mitigated by the chart's own legend + tooltip labels).
const INDIGO = '#4f46e5'
const TEAL = '#0891b2'

// ── Types & mock data ─────────────────────────────────────────────────────────
// Analítica = datos propios del dealer (05-MONETIZATION-MAP.md): ninguna cifra
// aquí viene del censo de mercado, así que no hay gating — todo es libre.

type Range = '7d' | '30d' | '90d'

interface SalesDatum { label: string; revenue: number; margin: number; units: number }

const SALES_DATA: Record<Range, SalesDatum[]> = {
  '7d': [
    { label: 'Lun', revenue:  58000, margin: 12200, units: 3 },
    { label: 'Mar', revenue:  72000, margin: 15400, units: 4 },
    { label: 'Mié', revenue:  31000, margin:  6800, units: 2 },
    { label: 'Jue', revenue:  89000, margin: 19200, units: 5 },
    { label: 'Vie', revenue:  94000, margin: 20800, units: 5 },
    { label: 'Sáb', revenue:  42000, margin:  9100, units: 2 },
    { label: 'Dom', revenue:  18000, margin:  3800, units: 1 },
  ],
  '30d': [
    { label: 'S1', revenue: 210000, margin:  44500, units: 12 },
    { label: 'S2', revenue: 285000, margin:  61000, units: 16 },
    { label: 'S3', revenue: 198000, margin:  42000, units: 11 },
    { label: 'S4', revenue: 312000, margin:  67200, units: 18 },
  ],
  '90d': [
    { label: 'Feb', revenue: 395000, margin:  79000, units: 22 },
    { label: 'Mar', revenue: 475000, margin:  95000, units: 27 },
    { label: 'Abr', revenue: 437000, margin:  87400, units: 23 },
  ],
}

interface KpiValues { visits: number; leads: number; cpl: number; conversion: number }

const KPI_VALUES: Record<Range, KpiValues> = {
  '7d':  { visits:  2840, leads:  67, cpl: 8.70, conversion: 6.7 },
  '30d': { visits: 14820, leads: 342, cpl: 8.70, conversion: 6.7 },
  '90d': { visits: 44200, leads: 1024, cpl: 8.40, conversion: 6.2 },
}

const TOP_MODELS = [
  { model: 'BMW 320d Touring',   units: 8 },
  { model: 'VW Golf 1.5 TSI',    units: 7 },
  { model: 'Audi A4 2.0 TDI',    units: 5 },
  { model: 'Mercedes C220d',     units: 2 },
  { model: 'Ford Kuga 2.5 PHEV', units: 1 },
]

const STOCK_SEGMENTS = [
  { segment: 'Urbano',    days: 28, target: 30, count: 42 },
  { segment: 'Familiar',  days: 41, target: 35, count: 68 },
  { segment: 'SUV',       days: 35, target: 35, count: 87 },
  { segment: 'Premium',   days: 52, target: 40, count: 34 },
  { segment: 'Furgoneta', days: 61, target: 45, count: 12 },
]

// 07-marketing F4 (00-MASTER.md §5.1: "01 decide el destino de la página; 07 posee
// SOLO el panel CHANNELS"): la constante CHANNELS mock (leads/ventas/CPL inventados)
// y su panel de abajo quedaron reemplazados por el radar real (cobertura C3 +
// divergencia de precio C4, MISMO cálculo que la página Marketing consume via
// GET /entities/{cdp}/channel-radar) — 01-F6 (dueño de la página) aún no ha
// ejecutado, así que el resto de paneles (SALES_DATA/KPI_VALUES/TOP_MODELS/
// STOCK_SEGMENTS/FUNNEL_STAGES/REGION_SALES) permanece exactamente como estaba,
// fuera de este pilar's alcance.
//
// Restyle pass (this turn): the VALUES in these mocks are unchanged — only the
// per-row `color` field was removed, which mixed ACCENT/GOOD/a stray amber as
// decorative filler by position/rank. Fixed per dataviz's color rule: TOP_MODELS/
// REGION_SALES are nominal categoricals of a single measure (already direct-labeled
// per row) → one hue, no legend; FUNNEL_STAGES is ordinal (order changes meaning) →
// an opacity ramp on one hue; STOCK_SEGMENTS does have a real status (rotation
// within/outside target) → color derived from days/target in StockRotationPanel,
// never a static hue baked per segment.

const FUNNEL_STAGES = [
  { label: 'Leads',    count: 342 },
  { label: 'Contacto', count: 218 },
  { label: 'Oferta',   count:  97 },
  { label: 'Venta',    count:  23 },
]

const REGION_SALES = [
  { region: 'Madrid',    sales: 8, pct: 35 },
  { region: 'Cataluña',  sales: 5, pct: 22 },
  { region: 'Valencia',  sales: 4, pct: 17 },
  { region: 'Andalucía', sales: 3, pct: 13 },
  { region: 'Otras',     sales: 3, pct: 13 },
]

// ── Metric card (KPI row) ──────────────────────────────────────────────────────
// Sparkline+footer KpiCard replaced by the shared ProgressMetricCard — same
// numbers, a real interactive background chart (scrub/hover) instead of a static
// 64x28 sparkline. `spark: number[]` values have no per-point real dates
// (arbitrary 6-step mock progressions, per kpiCards below), so period labels stay
// relative ("P-5" ... "Now") rather than inventing specific calendar dates.

function sparkToSeries(values: number[]): SeriesPoint[] {
  return values.map((value, i) => ({
    value,
    date: i === values.length - 1 ? 'Now' : `P-${values.length - 1 - i}`,
  }))
}

// ── Sales trend chart ─────────────────────────────────────────────────────────

function SalesTrendChart({ data, dark }: { data: SalesDatum[]; dark: boolean }) {
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 flex shrink-0 items-center justify-between">
          <div>
            <div className="mb-0.5 flex items-center gap-1.5">
              <TrendingUp style={{ width: 12, height: 12, color: ACCENT }} />
              <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Tendencia de ventas</h2>
            </div>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Ingresos y margen en el período seleccionado</p>
          </div>
          <div className="flex items-center gap-3.5 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
            <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-4 rounded-sm" style={{ background: INDIGO }} />Ingresos</span>
            <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-4 rounded-sm" style={{ background: TEAL }} />Margen</span>
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="an-rev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={INDIGO} stopOpacity={0.22} />
                  <stop offset="100%" stopColor={INDIGO} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="an-mar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={TEAL} stopOpacity={0.22} />
                  <stop offset="100%" stopColor={TEAL} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
              <XAxis dataKey="label" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(v / 1000).toFixed(0)}k`} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number, name: string) => [`€${v.toLocaleString()}`, name === 'revenue' ? 'Ingresos' : 'Margen']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <Area type="monotone" dataKey="revenue" stroke={INDIGO} strokeWidth={2} fill="url(#an-rev)" dot={false} activeDot={{ r: 3, fill: INDIGO, strokeWidth: 0 }} />
              <Area type="monotone" dataKey="margin"  stroke={TEAL} strokeWidth={2} fill="url(#an-mar)" dot={false} activeDot={{ r: 3, fill: TEAL, strokeWidth: 0 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  )
}

// ── Conversion funnel ─────────────────────────────────────────────────────────

function ConversionFunnel() {
  const max = FUNNEL_STAGES[0].count

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-0.5 flex items-center gap-1.5">
          <Target style={{ width: 12, height: 12, color: ACCENT }} />
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Embudo de conversión</h2>
        </div>
        <p className="mb-4 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Lead a venta cerrada</p>

        <div className="flex flex-1 flex-col gap-2.5">
          {FUNNEL_STAGES.map((stage, i) => {
            const barPct = (stage.count / max) * 100
            const convRate = i > 0 ? ((stage.count / FUNNEL_STAGES[i - 1].count) * 100).toFixed(0) : null
            // Ordinal ramp: the funnel is one measure (count) flowing through ordered
            // stages, so order lives in a single hue's opacity — never a per-stage
            // categorical/status color (dataviz: "if swapping order changes meaning,
            // it's ordinal, one hue, monotone steps").
            const barOpacity = 1 - (i / (FUNNEL_STAGES.length - 1)) * 0.5
            return (
              <motion.div key={stage.label} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 + i * 0.08 }}>
                <div className="mb-[5px] flex items-center justify-between">
                  <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>{stage.label}</span>
                  <div className="flex items-center gap-[7px]">
                    {convRate !== null && <span className="text-[9.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>{convRate}%</span>}
                    <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{stage.count}</span>
                  </div>
                </div>
                <div className="h-[7px] overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barPct}%` }}
                    transition={{ delay: 0.3 + i * 0.09, duration: 0.65, ease: [0.32, 0.72, 0, 1] }}
                    className="h-full rounded-full"
                    style={{ background: ACCENT, opacity: barOpacity, boxShadow: `0 0 6px ${ACCENT}55` }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>

        <div className="mt-3.5 rounded-[9px] p-[8px_10px]" style={{ background: `${GOOD}14`, border: `1px solid ${GOOD}28` }}>
          <span className="text-[10.5px] font-semibold" style={{ color: GOOD }}>Conversión global 6.7% · +0.4 pp vs período anterior</span>
        </div>
      </div>
    </Card>
  )
}

// ── Top models chart ──────────────────────────────────────────────────────────

function TopModelsChart({ dark }: { dark: boolean }) {
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Top modelos vendidos</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Unidades en el período</p>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={TOP_MODELS} layout="vertical" margin={{ top: 0, right: 12, left: 0, bottom: 0 }} barSize={11}>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `${v}u`} />
              <YAxis type="category" dataKey="model" tick={{ fontSize: 9, fill: tickColor }} axisLine={false} tickLine={false} width={90} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number) => [`${v} unidades`, 'Vendidos']}
                cursor={{ fill: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }}
              />
              {/* Single measure across nominal categories (model names, already
                  direct-labeled on the Y axis) — one hue for every bar, never a
                  color split by rank (dataviz: "never color nominal bars by value"). */}
              <Bar dataKey="units" radius={[0, 4, 4, 0]} fill={ACCENT} fillOpacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  )
}

// ── Channel performance (07-marketing F4: real radar, replaces the CHANNELS mock) ──
// C3 (cobertura) + C4 (divergencia) vía GET /entities/{cdp}/channel-radar — el MISMO
// cálculo que la página Marketing usa (00-MASTER.md C-1: un solo cálculo). Sin dealer
// reclamado o sin datos aún: empty-state honesto, nunca el mock que vivía aquí antes.

function ChannelPerfPanel() {
  const { user } = useAuthContext()
  const cdp = user?.tenantId || null
  const [radar, setRadar] = useState<ChannelRadar | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    if (!cdp) { setLoading(false); return }
    setLoading(true)
    setError(null)
    cardeep.channelRadar(cdp)
      .then(setRadar)
      .catch((e: unknown) => setError(e instanceof CardeepApiError ? e.message : 'Error al cargar el radar de canales'))
      .finally(() => setLoading(false))
  }, [cdp])

  useEffect(() => { load() }, [load])

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-0.5 flex items-center gap-1.5">
          <Globe style={{ width: 12, height: 12, color: ACCENT }} />
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Rendimiento por canal</h2>
        </div>
        <p className="mb-3.5 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Cobertura y divergencia de precio reales, por plataforma</p>

        {!cdp ? (
          <EmptyState
            icon={<Building2 className="h-6 w-6" />}
            title="Reclama tu ficha de dealer"
            message="Necesitas reclamar tu ficha de dealer para ver tu radar de canales."
            className="flex-1 !py-8"
          />
        ) : loading ? (
          <div className="flex flex-1 flex-col gap-2.5 pt-1" role="status" aria-live="polite" aria-label="Cargando radar de canales">
            {[0, 1, 2, 3].map(i => <Skeleton key={i} className="h-9 w-full" />)}
          </div>
        ) : error ? (
          <div role="alert" className="flex-1">
            <EmptyState
              icon={<AlertTriangle className="h-6 w-6" style={{ color: BAD }} />}
              title="No se pudo cargar el radar"
              message={error}
              className="!py-8"
              action={
                <motion.button
                  onClick={load}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.96 }}
                  className={`flex items-center gap-1.5 rounded-[8px] border px-3 py-1.5 text-[11px] font-semibold transition-colors hover:bg-[var(--bg-hover)] ${FOCUS_RING}`}
                  style={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}
                >
                  <RotateCw style={{ width: 11, height: 11 }} />
                  Reintentar
                </motion.button>
              }
            />
          </div>
        ) : !radar || radar.platforms.length === 0 ? (
          <EmptyState
            title="Sin cross-listing todavía"
            message="Ningún coche cross-listado en otra plataforma todavía."
            className="flex-1 !py-8"
          />
        ) : (
          <>
            <div className="grid shrink-0 gap-1 border-b pb-2" style={{ gridTemplateColumns: '1fr 60px 60px', borderColor: 'var(--border-subtle)' }}>
              {['Plataforma', 'Cobertura', 'Diverg.'].map(h => (
                <span key={h} className="text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>{h}</span>
              ))}
            </div>
            <div className="mt-3 flex flex-1 flex-col gap-2.5">
              {radar.platforms.slice(0, 6).map((p, i) => {
                const bandColor = p.band === 'verde' ? GOOD : p.band === 'ambar' ? WARN : BAD
                return (
                  <motion.div key={p.cdp_code} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.18 + i * 0.07 }}>
                    <div className="mb-[5px] grid items-center gap-1" style={{ gridTemplateColumns: '1fr 60px 60px' }}>
                      <div className="flex items-center gap-1.5">
                        <div className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: bandColor }} />
                        <span className="truncate text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>{p.trade_name ?? p.cdp_code}</span>
                      </div>
                      <span className="text-[11px] font-bold tabular-nums" style={{ color: bandColor }}>{Math.round(p.coverage_pct * 100)}%</span>
                      <span className="text-[11px] font-bold tabular-nums" style={{ color: p.n_divergent > 0 ? BAD : 'var(--text-primary)' }}>{p.n_divergent}</span>
                    </div>
                    <div className="h-[3px] overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${p.coverage_pct * 100}%` }}
                        transition={{ delay: 0.32 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                        className="h-full rounded-full"
                        style={{ background: bandColor, opacity: 0.75 }}
                      />
                    </div>
                  </motion.div>
                )
              })}
            </div>
            <motion.a
              href="/marketing"
              whileHover={{ x: 2 }}
              whileTap={{ scale: 0.98 }}
              className={`mt-2 inline-block text-[10.5px] font-medium transition-[filter] hover:brightness-125 hover:underline ${FOCUS_RING}`}
              style={{ color: ACCENT }}
            >
              Ver radar completo en Marketing →
            </motion.a>
          </>
        )}
      </div>
    </Card>
  )
}

// ── Stock rotation by segment ─────────────────────────────────────────────────

// Rotation health is a real status (on-target vs over-target), derived from the
// existing days/target relationship — not a static per-segment hue. A measure that
// itself means good/bad wears status tokens computed from its real values (dataviz
// collision rule), never a color baked into the mock row; text stays in text tokens,
// the status color lives on the dot + bar (icon + label), never bare on the figure.
function stockStatusColor(days: number, target: number): string {
  const overPct = (days - target) / target
  if (overPct <= 0) return GOOD
  if (overPct <= 0.2) return WARN
  return BAD
}

function StockRotationPanel() {
  const maxDays = Math.max(...STOCK_SEGMENTS.map(s => s.days))

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Rotación por segmento</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Días en stock · objetivo por tipo</p>
        </div>

        <div className="flex flex-1 flex-col gap-[11px]">
          {STOCK_SEGMENTS.map((seg, i) => {
            const overTarget = seg.days > seg.target
            const statusColor = stockStatusColor(seg.days, seg.target)
            return (
              <motion.div key={seg.segment} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.07 }}>
                <div className="mb-[5px] flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: statusColor }} />
                    <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>{seg.segment}</span>
                    <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>({seg.count})</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[9.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>obj. {seg.target}d</span>
                    <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{seg.days}d</span>
                    {overTarget && <span className="text-[9px] font-bold tabular-nums" style={{ color: statusColor }}>+{seg.days - seg.target}</span>}
                  </div>
                </div>
                <div className="h-[5px] overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(seg.days / maxDays) * 100}%` }}
                    transition={{ delay: 0.3 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                    className="h-full rounded-full"
                    style={{ background: statusColor, boxShadow: `0 0 5px ${statusColor}44` }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </Card>
  )
}

// ── Regional sales ────────────────────────────────────────────────────────────

function RegionSalesPanel() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-0.5 flex items-center gap-1.5">
          <MapPin style={{ width: 12, height: 12, color: ACCENT }} />
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Ventas por región</h2>
        </div>
        <p className="mb-3.5 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Madrid y Cataluña concentran el 57%</p>

        {/* Nominal categories (region names, already direct-labeled per row) sharing
            one measure — same hue for every bar; no legend needed (dataviz: a lone
            series is named by the title, not a swatch strip), so the previous
            per-region rank coloring and its now-redundant legend are gone. */}
        <div className="flex flex-1 flex-col gap-2.5">
          {REGION_SALES.map((r, i) => (
            <motion.div key={r.region} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 + i * 0.07 }}>
              <div className="mb-[5px] flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <div className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: ACCENT }} />
                  <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>{r.region}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10.5px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>{r.pct}%</span>
                  <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{r.sales}u</span>
                </div>
              </div>
              <div className="h-1 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${r.pct}%` }}
                  transition={{ delay: 0.35 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                  className="h-full rounded-full"
                  style={{ background: ACCENT }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Analitica() {
  const dark = useIsDark()
  const [range, setRange] = useState<Range>('30d')

  const kpi = KPI_VALUES[range]
  const salesData = SALES_DATA[range]

  const kpiCards: (React.ComponentProps<typeof ProgressMetricCard> & { key: string })[] = [
    {
      key: 'Visitas totales',
      title: 'Visitas totales',
      total: `${kpi.visits}`,
      sub: 'páginas de producto',
      trend: 'up',
      delta: '+18% vs período anterior',
      deltaLabel: '',
      accent: 'emerald',
      data: sparkToSeries([9800, 11200, 12400, 13100, 14000, kpi.visits]),
    },
    {
      key: 'Leads captados',
      title: 'Leads captados',
      total: `${kpi.leads}`,
      sub: 'todos los canales',
      trend: 'up',
      delta: '+11% vs período anterior',
      deltaLabel: '',
      accent: 'emerald',
      data: sparkToSeries([280, 295, 310, 325, 336, kpi.leads]),
    },
    {
      key: 'Coste por lead',
      title: 'Coste por lead',
      total: `€${kpi.cpl.toFixed(2)}`,
      sub: 'media ponderada canales',
      trend: 'down',
      delta: '-5% vs período anterior',
      deltaLabel: '',
      accent: 'emerald',
      data: sparkToSeries([10.2, 9.8, 9.4, 9.1, 8.9, kpi.cpl]),
    },
    {
      key: 'Conversión',
      title: 'Conversión',
      total: `${kpi.conversion.toFixed(1)}%`,
      sub: 'lead a venta cerrada',
      trend: 'up',
      delta: '+0.4 pp vs período anterior',
      deltaLabel: '',
      accent: 'emerald',
      data: sparkToSeries([5.8, 6.0, 6.2, 6.4, 6.6, kpi.conversion]),
    },
  ]

  return (
    <div className="mx-auto p-[24px_24px_40px]" style={{ maxWidth: 1360 }}>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        className="mb-[22px] flex flex-wrap items-end justify-between gap-4"
      >
        <div>
          <div className="mb-1.5 font-mono text-[10.5px] tracking-[0.04em]" style={{ color: 'var(--text-muted)' }}>Analítica · todos los canales</div>
          <h1 className="mb-1 text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>Analítica e informes</h1>
          <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>Ventas, marketing, stock y canales — una sola vista.</p>
        </div>

        <div className="flex gap-[3px]" role="group" aria-label="Rango de tiempo">
          {(['7d', '30d', '90d'] as const).map(r => (
            <motion.button
              key={r}
              onClick={() => setRange(r)}
              aria-pressed={range === r}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.94 }}
              className={`rounded-[7px] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.04em] transition-colors ${range === r ? '' : 'hover:bg-[var(--bg-hover)]'} ${FOCUS_RING}`}
              style={{
                background: range === r ? `${ACCENT}22` : 'transparent',
                border: `1px solid ${range === r ? `${ACCENT}48` : 'transparent'}`,
                color: range === r ? ACCENT : 'var(--text-muted)',
              }}
            >
              {r}
            </motion.button>
          ))}
        </div>
      </motion.div>

      <div className="grid grid-cols-4 gap-3.5">

        {kpiCards.map(({ key, ...card }, i) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}
          >
            <ProgressMetricCard size="sm" showStats={false} {...card} />
          </motion.div>
        ))}

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '2', minHeight: 280 }}>
          <SalesTrendChart data={salesData} dark={dark} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3', gridRow: '2' }}>
          <ConversionFunnel />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.32, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '4', gridRow: '2' }}>
          <TopModelsChart dark={dark} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '3', minHeight: 280 }}>
          <ChannelPerfPanel />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3', gridRow: '3' }}>
          <StockRotationPanel />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.42, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '4', gridRow: '3' }}>
          <RegionSalesPanel />
        </motion.div>

      </div>
    </div>
  )
}
