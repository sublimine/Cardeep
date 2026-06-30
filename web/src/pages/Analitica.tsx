import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, Minus, TrendingUp, Target, Globe, MapPin } from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip,
  ResponsiveContainer,
} from 'recharts'

// ── Theme observer ────────────────────────────────────────────────────────────

function useIsDark() {
  const [dark, setDark] = useState(() => !document.documentElement.classList.contains('light'))
  useEffect(() => {
    const obs = new MutationObserver(() => setDark(!document.documentElement.classList.contains('light')))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return dark
}

// ── Types & mock data ─────────────────────────────────────────────────────────

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
  { model: 'BMW 320d Touring',    units: 8, color: '#5b8df8' },
  { model: 'VW Golf 1.5 TSI',    units: 7, color: '#60a5fa' },
  { model: 'Audi A4 2.0 TDI',   units: 5, color: '#0ea5e9' },
  { model: 'Mercedes C220d',     units: 2, color: '#22c55e' },
  { model: 'Ford Kuga 2.5 PHEV', units: 1, color: '#f59e0b' },
]

const STOCK_SEGMENTS = [
  { segment: 'Urbano',    days: 28, target: 30, count: 42, color: '#22c55e' },
  { segment: 'Familiar',  days: 41, target: 35, count: 68, color: '#5b8df8' },
  { segment: 'SUV',       days: 35, target: 35, count: 87, color: '#60a5fa' },
  { segment: 'Premium',   days: 52, target: 40, count: 34, color: '#f87171' },
  { segment: 'Furgoneta', days: 61, target: 45, count: 12, color: '#f87171' },
]

const CHANNELS = [
  { name: 'coches.net',  leads: 142, sales: 12, cpl: 9.40, color: '#5b8df8', pct: 42 },
  { name: 'AutoScout24', leads:  88, sales:  7, cpl: 8.10, color: '#60a5fa', pct: 26 },
  { name: 'Web propia',  leads:  67, sales:  3, cpl: 6.20, color: '#22c55e', pct: 20 },
  { name: 'Particular',  leads:  45, sales:  1, cpl: 3.50, color: '#f59e0b', pct: 12 },
]

const FUNNEL_STAGES = [
  { label: 'Leads',    count: 342, color: '#5b8df8' },
  { label: 'Contacto', count: 218, color: '#60a5fa' },
  { label: 'Oferta',   count:  97, color: '#f59e0b' },
  { label: 'Venta',    count:  23, color: '#22c55e' },
]

const REGION_SALES = [
  { region: 'Madrid',    sales: 8, pct: 35, color: '#5b8df8' },
  { region: 'Cataluña',  sales: 5, pct: 22, color: '#60a5fa' },
  { region: 'Valencia',  sales: 4, pct: 17, color: '#0ea5e9' },
  { region: 'Andalucía', sales: 3, pct: 13, color: '#22c55e' },
  { region: 'Otras',     sales: 3, pct: 13, color: '#f59e0b' },
]

// ── Token helpers ─────────────────────────────────────────────────────────────

function tok(dark: boolean) {
  return {
    t1:       dark ? '#f1f5f9' : '#0f172a',
    t2:       dark ? '#cbd5e1' : '#334155',
    t3:       dark ? '#94a3b8' : '#64748b',
    t4:       dark ? '#475569' : '#94a3b8',
    div:      dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)',
    cardBg:   dark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.82)',
    cardBord: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
    subBg:    dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)',
    subBord:  dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)',
  }
}

// ── Glass card ────────────────────────────────────────────────────────────────

function GCard({ dark, children, style }: { dark: boolean; children: React.ReactNode; style?: React.CSSProperties }) {
  const c = tok(dark)
  return (
    <div style={{
      background: c.cardBg,
      border: `1px solid ${c.cardBord}`,
      borderRadius: 18,
      backdropFilter: 'blur(32px) saturate(180%)',
      WebkitBackdropFilter: 'blur(32px) saturate(180%)',
      boxShadow: dark
        ? '0 4px 24px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.07)'
        : '0 4px 20px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.90)',
      overflow: 'hidden',
      ...style,
    }}>
      {children}
    </div>
  )
}

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

interface KpiCardProps {
  dark: boolean
  label: string
  value: number
  prefix?: string
  suffix?: string
  decimals?: number
  sub: string
  trend: 'up' | 'down' | 'flat' | 'good'
  trendLabel: string
  spark: number[]
  accent: string
  delay?: number
}

function KpiCard({ dark, label, value, prefix, suffix, decimals, sub, trend, trendLabel, spark, accent, delay = 0 }: KpiCardProps) {
  const c = tok(dark)
  const trendColor = trend === 'up' || trend === 'good' ? '#22c55e' : trend === 'down' ? '#f87171' : c.t4
  const TrendIcon  = trend === 'up' || trend === 'good' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : Minus

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
    >
      <GCard dark={dark} style={{ padding: '20px 22px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <span style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.11em', textTransform: 'uppercase', color: c.t3 }}>
            {label}
          </span>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: accent, boxShadow: `0 0 6px ${accent}` }} />
        </div>

        <div style={{ fontSize: 44, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1, color: c.t1, marginBottom: 4 }}>
          <AnimNum to={value} prefix={prefix} suffix={suffix} decimals={decimals} />
        </div>
        <div style={{ fontSize: 11, color: c.t4, marginBottom: 14 }}>{sub}</div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 10, borderTop: `1px solid ${c.div}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <TrendIcon style={{ width: 11, height: 11, color: trendColor }} />
            <span style={{ fontSize: 10.5, fontWeight: 600, color: trendColor }}>{trendLabel}</span>
          </div>
          <Spark values={spark} color={accent} height={22} />
        </div>
      </GCard>
    </motion.div>
  )
}

// ── Sales trend chart ─────────────────────────────────────────────────────────

function SalesTrendChart({ data, dark }: { data: SalesDatum[]; dark: boolean }) {
  const c = tok(dark)
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexShrink: 0 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
              <TrendingUp style={{ width: 12, height: 12, color: '#5b8df8' }} />
              <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>Tendencia de ventas</h2>
            </div>
            <p style={{ fontSize: 10.5, color: c.t4 }}>Ingresos y margen en el período seleccionado</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 10.5, color: c.t4 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 16, height: 2, background: '#5b8df8', display: 'inline-block', borderRadius: 1 }} />
              Ingresos
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 16, height: 2, background: '#22c55e', display: 'inline-block', borderRadius: 1 }} />
              Margen
            </span>
          </div>
        </div>

        <div style={{ flex: 1, minHeight: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="an-rev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor="#5b8df8" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#5b8df8" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="an-mar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor="#22c55e" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
              <XAxis dataKey="label" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(v / 1000).toFixed(0)}k`} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: `1px solid ${c.cardBord}`, borderRadius: 10, fontSize: 11.5, color: c.t1, boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number, name: string) => [`€${v.toLocaleString()}`, name === 'revenue' ? 'Ingresos' : 'Margen']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <Area type="monotone" dataKey="revenue" stroke="#5b8df8" strokeWidth={2} fill="url(#an-rev)" dot={false} activeDot={{ r: 3, fill: '#5b8df8', strokeWidth: 0 }} />
              <Area type="monotone" dataKey="margin"  stroke="#22c55e" strokeWidth={2} fill="url(#an-mar)" dot={false} activeDot={{ r: 3, fill: '#22c55e', strokeWidth: 0 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </GCard>
  )
}

// ── Conversion funnel ─────────────────────────────────────────────────────────

function ConversionFunnel({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const max = FUNNEL_STAGES[0].count

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 18px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
          <Target style={{ width: 12, height: 12, color: '#60a5fa' }} />
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>Embudo de conversión</h2>
        </div>
        <p style={{ fontSize: 10.5, color: c.t4, marginBottom: 16 }}>Lead a venta cerrada</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, flex: 1 }}>
          {FUNNEL_STAGES.map((stage, i) => {
            const barPct = (stage.count / max) * 100
            const convRate = i > 0
              ? ((stage.count / FUNNEL_STAGES[i - 1].count) * 100).toFixed(0)
              : null
            return (
              <motion.div
                key={stage.label}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 + i * 0.08 }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
                  <span style={{ fontSize: 11, fontWeight: 600, color: c.t2 }}>{stage.label}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                    {convRate !== null && (
                      <span style={{ fontSize: 9.5, color: c.t4, fontVariantNumeric: 'tabular-nums' }}>
                        {convRate}%
                      </span>
                    )}
                    <span style={{ fontSize: 11, fontWeight: 700, color: c.t1, fontVariantNumeric: 'tabular-nums' }}>
                      {stage.count}
                    </span>
                  </div>
                </div>
                <div style={{ height: 7, borderRadius: 99, background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barPct}%` }}
                    transition={{ delay: 0.3 + i * 0.09, duration: 0.65, ease: [0.32, 0.72, 0, 1] }}
                    style={{ height: '100%', borderRadius: 99, background: stage.color, boxShadow: `0 0 6px ${stage.color}55` }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>

        <div style={{
          marginTop: 14,
          padding: '8px 10px',
          borderRadius: 9,
          background: 'rgba(34,197,94,0.08)',
          border: '1px solid rgba(34,197,94,0.16)',
        }}>
          <span style={{ fontSize: 10.5, color: '#22c55e', fontWeight: 600 }}>
            Conversión global 6.7% · +0.4 pp vs período anterior
          </span>
        </div>
      </div>
    </GCard>
  )
}

// ── Top models chart ──────────────────────────────────────────────────────────

function TopModelsChart({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 16, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Top modelos vendidos</h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>Unidades en el período</p>
        </div>

        <div style={{ flex: 1, minHeight: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={TOP_MODELS}
              layout="vertical"
              margin={{ top: 0, right: 12, left: 0, bottom: 0 }}
              barSize={11}
            >
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} horizontal={false} />
              <XAxis
                type="number"
                tick={{ fontSize: 9.5, fill: tickColor }}
                axisLine={false}
                tickLine={false}
                tickFormatter={v => `${v}u`}
              />
              <YAxis
                type="category"
                dataKey="model"
                tick={{ fontSize: 9, fill: tickColor }}
                axisLine={false}
                tickLine={false}
                width={90}
              />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: `1px solid ${c.cardBord}`, borderRadius: 10, fontSize: 11.5, color: c.t1, boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number) => [`${v} unidades`, 'Vendidos']}
                cursor={{ fill: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }}
              />
              <Bar dataKey="units" radius={[0, 4, 4, 0]}>
                {TOP_MODELS.map((entry, index) => (
                  <Cell key={`cell-tm-${index}`} fill={entry.color} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </GCard>
  )
}

// ── Channel performance ───────────────────────────────────────────────────────

function ChannelPerfPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 18px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
          <Globe style={{ width: 12, height: 12, color: '#0ea5e9' }} />
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>Rendimiento por canal</h2>
        </div>
        <p style={{ fontSize: 10.5, color: c.t4, marginBottom: 14 }}>coches.net · AutoScout24 · Web · Particular</p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 52px 50px 52px',
          gap: 4,
          padding: '0 2px 8px',
          borderBottom: `1px solid ${c.div}`,
          flexShrink: 0,
        }}>
          {['Canal', 'Leads', 'Ventas', 'CPL'].map(h => (
            <span key={h} style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: c.t4 }}>
              {h}
            </span>
          ))}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 12, flex: 1 }}>
          {CHANNELS.map((ch, i) => (
            <motion.div
              key={ch.name}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.18 + i * 0.07 }}
            >
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 52px 50px 52px',
                gap: 4,
                alignItems: 'center',
                marginBottom: 5,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 7, height: 7, borderRadius: '50%', background: ch.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 11, fontWeight: 600, color: c.t2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {ch.name}
                  </span>
                </div>
                <span style={{ fontSize: 11, fontWeight: 700, color: c.t1, fontVariantNumeric: 'tabular-nums' }}>{ch.leads}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: c.t1, fontVariantNumeric: 'tabular-nums' }}>{ch.sales}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: c.t1, fontVariantNumeric: 'tabular-nums' }}>€{ch.cpl.toFixed(2)}</span>
              </div>
              <div style={{ height: 3, borderRadius: 99, background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)', overflow: 'hidden' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${ch.pct}%` }}
                  transition={{ delay: 0.32 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                  style={{ height: '100%', borderRadius: 99, background: ch.color, opacity: 0.75 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Stock rotation by segment ─────────────────────────────────────────────────

function StockRotationPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const maxDays = Math.max(...STOCK_SEGMENTS.map(s => s.days))

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 18px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 16, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Rotación por segmento</h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>Días en stock · objetivo por tipo</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 11, flex: 1 }}>
          {STOCK_SEGMENTS.map((seg, i) => {
            const overTarget = seg.days > seg.target
            return (
              <motion.div
                key={seg.segment}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 + i * 0.07 }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ fontSize: 11, fontWeight: 600, color: c.t2 }}>{seg.segment}</span>
                    <span style={{ fontSize: 9.5, color: c.t4 }}>({seg.count})</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ fontSize: 9.5, color: c.t4, fontVariantNumeric: 'tabular-nums' }}>obj. {seg.target}d</span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: seg.color, fontVariantNumeric: 'tabular-nums' }}>
                      {seg.days}d
                    </span>
                    {overTarget && (
                      <span style={{ fontSize: 9, color: '#f87171', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
                        +{seg.days - seg.target}
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ height: 5, borderRadius: 99, background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(seg.days / maxDays) * 100}%` }}
                    transition={{ delay: 0.3 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                    style={{ height: '100%', borderRadius: 99, background: seg.color, boxShadow: `0 0 5px ${seg.color}44` }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </GCard>
  )
}

// ── Regional sales ────────────────────────────────────────────────────────────

function RegionSalesPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 18px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
          <MapPin style={{ width: 12, height: 12, color: '#5b8df8' }} />
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>Ventas por región</h2>
        </div>
        <p style={{ fontSize: 10.5, color: c.t4, marginBottom: 14 }}>Madrid y Cataluña concentran el 57%</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, flex: 1 }}>
          {REGION_SALES.map((r, i) => (
            <motion.div
              key={r.region}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.07 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 7, height: 7, borderRadius: '50%', background: r.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 11, fontWeight: 600, color: c.t2 }}>{r.region}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 10.5, color: c.t3, fontVariantNumeric: 'tabular-nums' }}>{r.pct}%</span>
                  <span style={{ fontSize: 11, fontWeight: 700, color: c.t1, fontVariantNumeric: 'tabular-nums' }}>
                    {r.sales}u
                  </span>
                </div>
              </div>
              <div style={{ height: 4, borderRadius: 99, background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)', overflow: 'hidden' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${r.pct}%` }}
                  transition={{ delay: 0.35 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                  style={{ height: '100%', borderRadius: 99, background: r.color }}
                />
              </div>
            </motion.div>
          ))}
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 14 }}>
          {REGION_SALES.map(r => (
            <div key={r.region} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <div style={{ width: 5, height: 5, borderRadius: '50%', background: r.color }} />
              <span style={{ fontSize: 9.5, color: c.t4 }}>{r.region}</span>
            </div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Analitica() {
  const dark = useIsDark()
  const c = tok(dark)
  const [range, setRange] = useState<Range>('30d')

  const kpi = KPI_VALUES[range]
  const salesData = SALES_DATA[range]

  const kpiCards: KpiCardProps[] = [
    {
      dark,
      label: 'Visitas totales',
      value: kpi.visits,
      sub: 'páginas de producto',
      trend: 'up',
      trendLabel: '+18% vs período anterior',
      accent: '#5b8df8',
      spark: [9800, 11200, 12400, 13100, 14000, kpi.visits],
      delay: 0,
    },
    {
      dark,
      label: 'Leads captados',
      value: kpi.leads,
      sub: 'todos los canales',
      trend: 'up',
      trendLabel: '+11% vs período anterior',
      accent: '#60a5fa',
      spark: [280, 295, 310, 325, 336, kpi.leads],
      delay: 0.06,
    },
    {
      dark,
      label: 'Coste por lead',
      value: kpi.cpl,
      prefix: '€',
      decimals: 2,
      sub: 'media ponderada canales',
      trend: 'good',
      trendLabel: '-5% vs período anterior',
      accent: '#22c55e',
      spark: [10.2, 9.8, 9.4, 9.1, 8.9, kpi.cpl],
      delay: 0.12,
    },
    {
      dark,
      label: 'Conversión',
      value: kpi.conversion,
      suffix: '%',
      decimals: 1,
      sub: 'lead a venta cerrada',
      trend: 'up',
      trendLabel: '+0.4 pp vs período anterior',
      accent: '#0ea5e9',
      spark: [5.8, 6.0, 6.2, 6.4, 6.6, kpi.conversion],
      delay: 0.18,
    },
  ]

  return (
    <div style={{ padding: '24px 24px 40px', maxWidth: 1360, margin: '0 auto' }}>

      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        style={{ marginBottom: 22, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}
      >
        <div>
          <div style={{ fontSize: 10.5, fontFamily: 'ui-monospace,monospace', color: c.t4, marginBottom: 6, letterSpacing: '0.04em' }}>
            Analítica · todos los canales
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: '-0.02em', color: c.t1, lineHeight: 1, marginBottom: 4 }}>
            Analítica e informes
          </h1>
          <p style={{ fontSize: 11.5, color: c.t4 }}>
            Ventas, marketing, stock y canales — una sola vista.
          </p>
        </div>

        {/* Range selector */}
        <div style={{ display: 'flex', gap: 3 }}>
          {(['7d', '30d', '90d'] as const).map(r => (
            <button
              key={r}
              onClick={() => setRange(r)}
              style={{
                padding: '4px 10px',
                borderRadius: 7,
                fontSize: 10,
                fontWeight: 700,
                cursor: 'pointer',
                fontFamily: 'Inter, system-ui',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                background: range === r ? 'rgba(91,141,248,0.14)' : 'transparent',
                border: range === r ? '1px solid rgba(91,141,248,0.28)' : '1px solid transparent',
                color: range === r ? '#5b8df8' : c.t4,
                transition: 'all 170ms',
              }}
            >
              {r}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Bento grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>

        {/* Row 1 — KPI marketing cards */}
        {kpiCards.map(card => (
          <KpiCard key={card.label} {...card} />
        ))}

        {/* Row 2 — Sales trend (2 cols) + Funnel (1 col) + Top models (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 3', gridRow: '2', minHeight: 280 }}
        >
          <SalesTrendChart data={salesData} dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '3', gridRow: '2' }}
        >
          <ConversionFunnel dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.32, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '4', gridRow: '2' }}
        >
          <TopModelsChart dark={dark} />
        </motion.div>

        {/* Row 3 — Channel perf (2 cols) + Stock rotation (1 col) + Region sales (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 3', gridRow: '3', minHeight: 280 }}
        >
          <ChannelPerfPanel dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '3', gridRow: '3' }}
        >
          <StockRotationPanel dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.42, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '4', gridRow: '3' }}
        >
          <RegionSalesPanel dark={dark} />
        </motion.div>

      </div>
    </div>
  )
}
