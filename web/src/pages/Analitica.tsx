import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, Minus, TrendingUp, Target, Globe, MapPin } from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip,
  ResponsiveContainer,
} from 'recharts'
import Card from '../components/Card'
import { useIsDark } from '../hooks/useIsDark'
import { ACCENT, GOOD, BAD } from '../lib/theme'

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
  { model: 'BMW 320d Touring',   units: 8, color: ACCENT },
  { model: 'VW Golf 1.5 TSI',    units: 7, color: ACCENT },
  { model: 'Audi A4 2.0 TDI',    units: 5, color: ACCENT },
  { model: 'Mercedes C220d',     units: 2, color: GOOD },
  { model: 'Ford Kuga 2.5 PHEV', units: 1, color: GOOD },
]

const STOCK_SEGMENTS = [
  { segment: 'Urbano',    days: 28, target: 30, count: 42, color: GOOD },
  { segment: 'Familiar',  days: 41, target: 35, count: 68, color: ACCENT },
  { segment: 'SUV',       days: 35, target: 35, count: 87, color: ACCENT },
  { segment: 'Premium',   days: 52, target: 40, count: 34, color: BAD },
  { segment: 'Furgoneta', days: 61, target: 45, count: 12, color: BAD },
]

// 07-marketing F0 (00-MASTER.md §5.1: "01 decide el destino de la página; 07 posee
// SOLO el panel CHANNELS"): esta constante y ChannelPerfPanel de abajo son mock
// (leads/ventas/CPL inventados), igual que el resto de esta página — pero es la
// única sección que este pilar POSEE, así que se etiqueta honestamente aquí y ahora
// en vez de esperar a F4. F4 la sustituye por el radar real (cobertura C3 +
// divergencia de precio C4, consumidos de 05-multiposting's /publishing/*, más
// días-hasta-baja C5 nuevo) — 01-F6 (dueño de la página) aún no ha ejecutado, así
// que el resto de paneles (SALES_DATA/KPI_VALUES/TOP_MODELS/STOCK_SEGMENTS/
// FUNNEL_STAGES/REGION_SALES) permanece exactamente como estaba, fuera de este
// pilar's alcance.
const CHANNELS = [
  { name: 'coches.net',  leads: 142, sales: 12, cpl: 9.40, color: ACCENT, pct: 42 },
  { name: 'AutoScout24', leads:  88, sales:  7, cpl: 8.10, color: ACCENT, pct: 26 },
  { name: 'Web propia',  leads:  67, sales:  3, cpl: 6.20, color: GOOD,   pct: 20 },
  { name: 'Particular',  leads:  45, sales:  1, cpl: 3.50, color: '#d97706', pct: 12 },
]

const FUNNEL_STAGES = [
  { label: 'Leads',    count: 342, color: ACCENT },
  { label: 'Contacto', count: 218, color: ACCENT },
  { label: 'Oferta',   count:  97, color: '#d97706' },
  { label: 'Venta',    count:  23, color: GOOD },
]

const REGION_SALES = [
  { region: 'Madrid',    sales: 8, pct: 35, color: ACCENT },
  { region: 'Cataluña',  sales: 5, pct: 22, color: ACCENT },
  { region: 'Valencia',  sales: 4, pct: 17, color: ACCENT },
  { region: 'Andalucía', sales: 3, pct: 13, color: GOOD },
  { region: 'Otras',     sales: 3, pct: 13, color: '#d97706' },
]

// ── AnimNum ───────────────────────────────────────────────────────────────────

function AnimNum({ to, prefix = '', suffix = '', decimals = 0 }: { to: number; prefix?: string; suffix?: string; decimals?: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(sp, v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

// ── Spark ─────────────────────────────────────────────────────────────────────

function Spark({ values, color, height = 28 }: { values: number[]; color: string; height?: number }) {
  if (values.length < 2) return null
  const max = Math.max(...values), min = Math.min(...values), range = max - min || 1
  const W = 64, H = height
  const pts = values.map((v, i): [number, number] => [
    (i / (values.length - 1)) * W,
    H - ((v - min) / range) * (H - 4) + 2,
  ])
  const line = pts.map(([x, y]) => `${x},${y}`).join(' ')
  const area = `M${pts[0][0]},${H} ` + pts.map(([x, y]) => `L${x},${y}`).join(' ') + ` L${pts.at(-1)![0]},${H} Z`
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: 'block' }}>
      <path d={area} fill={color} fillOpacity={0.12} />
      <polyline points={line} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// ── KpiCard ───────────────────────────────────────────────────────────────────

interface KpiCardProps { label: string; value: number; prefix?: string; suffix?: string; decimals?: number; sub: string; trend: 'up' | 'down' | 'flat' | 'good'; trendLabel: string; spark: number[]; delay?: number }

function KpiCard({ label, value, prefix, suffix, decimals, sub, trend, trendLabel, spark, delay = 0 }: KpiCardProps) {
  const trendColor = trend === 'up' || trend === 'good' ? GOOD : trend === 'down' ? BAD : 'var(--text-muted)'
  const TrendIcon  = trend === 'up' || trend === 'good' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : Minus

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}>
      <Card hover className="!p-5">
        <div className="mb-3.5 flex items-center justify-between">
          <span className="text-[9.5px] font-bold uppercase tracking-[0.11em]" style={{ color: 'var(--text-secondary)' }}>{label}</span>
          <div className="h-1.5 w-1.5 rounded-full" style={{ background: ACCENT, boxShadow: `0 0 6px ${ACCENT}` }} />
        </div>
        <div className="mb-1 text-[44px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>
          <AnimNum to={value} prefix={prefix} suffix={suffix} decimals={decimals} />
        </div>
        <div className="mb-3.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>{sub}</div>
        <div className="flex items-center justify-between border-t pt-2.5" style={{ borderColor: 'var(--border-subtle)' }}>
          <div className="flex items-center gap-1">
            <TrendIcon style={{ width: 11, height: 11, color: trendColor }} />
            <span className="text-[10.5px] font-semibold" style={{ color: trendColor }}>{trendLabel}</span>
          </div>
          <Spark values={spark} color={ACCENT} height={22} />
        </div>
      </Card>
    </motion.div>
  )
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
            <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-4 rounded-sm" style={{ background: ACCENT }} />Ingresos</span>
            <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-4 rounded-sm" style={{ background: GOOD }} />Margen</span>
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="an-rev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={ACCENT} stopOpacity={0.22} />
                  <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="an-mar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={GOOD} stopOpacity={0.22} />
                  <stop offset="100%" stopColor={GOOD} stopOpacity={0} />
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
              <Area type="monotone" dataKey="revenue" stroke={ACCENT} strokeWidth={2} fill="url(#an-rev)" dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} />
              <Area type="monotone" dataKey="margin"  stroke={GOOD} strokeWidth={2} fill="url(#an-mar)" dot={false} activeDot={{ r: 3, fill: GOOD, strokeWidth: 0 }} />
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
                    style={{ background: stage.color, boxShadow: `0 0 6px ${stage.color}55` }}
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
              <Bar dataKey="units" radius={[0, 4, 4, 0]}>
                {TOP_MODELS.map((entry, index) => <Cell key={`cell-tm-${index}`} fill={entry.color} fillOpacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  )
}

// ── Channel performance ───────────────────────────────────────────────────────

function ChannelPerfPanel() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-0.5 flex items-center gap-1.5">
          <Globe style={{ width: 12, height: 12, color: ACCENT }} />
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Rendimiento por canal</h2>
          <span
            className="ml-1 rounded-full px-[7px] py-[1px] text-[8.5px] font-bold uppercase tracking-[0.06em]"
            style={{ background: 'rgba(217,119,6,0.14)', border: '1px solid rgba(217,119,6,0.32)', color: '#d97706' }}
            title="Datos ilustrativos: leads/ventas/CPL de ejemplo. El radar real (cobertura y divergencia de precio verificadas) llega en la página Marketing."
          >
            Ilustrativo
          </span>
        </div>
        <p className="mb-3.5 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>coches.net · AutoScout24 · Web · Particular — datos de ejemplo, ver Marketing para el radar real</p>

        <div className="grid shrink-0 gap-1 border-b pb-2" style={{ gridTemplateColumns: '1fr 52px 50px 52px', borderColor: 'var(--border-subtle)' }}>
          {['Canal', 'Leads', 'Ventas', 'CPL'].map(h => (
            <span key={h} className="text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>{h}</span>
          ))}
        </div>

        <div className="mt-3 flex flex-1 flex-col gap-2.5">
          {CHANNELS.map((ch, i) => (
            <motion.div key={ch.name} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.18 + i * 0.07 }}>
              <div className="mb-[5px] grid items-center gap-1" style={{ gridTemplateColumns: '1fr 52px 50px 52px' }}>
                <div className="flex items-center gap-1.5">
                  <div className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: ch.color }} />
                  <span className="truncate text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>{ch.name}</span>
                </div>
                <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{ch.leads}</span>
                <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{ch.sales}</span>
                <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>€{ch.cpl.toFixed(2)}</span>
              </div>
              <div className="h-[3px] overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${ch.pct}%` }}
                  transition={{ delay: 0.32 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                  className="h-full rounded-full"
                  style={{ background: ch.color, opacity: 0.75 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Stock rotation by segment ─────────────────────────────────────────────────

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
            return (
              <motion.div key={seg.segment} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.07 }}>
                <div className="mb-[5px] flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>{seg.segment}</span>
                    <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>({seg.count})</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[9.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>obj. {seg.target}d</span>
                    <span className="text-[11px] font-bold tabular-nums" style={{ color: seg.color }}>{seg.days}d</span>
                    {overTarget && <span className="text-[9px] font-bold tabular-nums" style={{ color: BAD }}>+{seg.days - seg.target}</span>}
                  </div>
                </div>
                <div className="h-[5px] overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(seg.days / maxDays) * 100}%` }}
                    transition={{ delay: 0.3 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                    className="h-full rounded-full"
                    style={{ background: seg.color, boxShadow: `0 0 5px ${seg.color}44` }}
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

        <div className="flex flex-1 flex-col gap-2.5">
          {REGION_SALES.map((r, i) => (
            <motion.div key={r.region} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 + i * 0.07 }}>
              <div className="mb-[5px] flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <div className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: r.color }} />
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
                  style={{ background: r.color }}
                />
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-3.5 flex flex-wrap gap-1.5">
          {REGION_SALES.map(r => (
            <div key={r.region} className="flex items-center gap-1">
              <div className="h-1 w-1 rounded-full" style={{ background: r.color }} />
              <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>{r.region}</span>
            </div>
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

  const kpiCards: KpiCardProps[] = [
    { label: 'Visitas totales', value: kpi.visits, sub: 'páginas de producto', trend: 'up', trendLabel: '+18% vs período anterior', spark: [9800, 11200, 12400, 13100, 14000, kpi.visits], delay: 0 },
    { label: 'Leads captados', value: kpi.leads, sub: 'todos los canales', trend: 'up', trendLabel: '+11% vs período anterior', spark: [280, 295, 310, 325, 336, kpi.leads], delay: 0.06 },
    { label: 'Coste por lead', value: kpi.cpl, prefix: '€', decimals: 2, sub: 'media ponderada canales', trend: 'good', trendLabel: '-5% vs período anterior', spark: [10.2, 9.8, 9.4, 9.1, 8.9, kpi.cpl], delay: 0.12 },
    { label: 'Conversión', value: kpi.conversion, suffix: '%', decimals: 1, sub: 'lead a venta cerrada', trend: 'up', trendLabel: '+0.4 pp vs período anterior', spark: [5.8, 6.0, 6.2, 6.4, 6.6, kpi.conversion], delay: 0.18 },
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

        <div className="flex gap-[3px]">
          {(['7d', '30d', '90d'] as const).map(r => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className="rounded-[7px] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.04em] transition-colors"
              style={{
                background: range === r ? `${ACCENT}22` : 'transparent',
                border: `1px solid ${range === r ? `${ACCENT}48` : 'transparent'}`,
                color: range === r ? ACCENT : 'var(--text-muted)',
              }}
            >
              {r}
            </button>
          ))}
        </div>
      </motion.div>

      <div className="grid grid-cols-4 gap-3.5">

        {kpiCards.map(card => <KpiCard key={card.label} {...card} />)}

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
