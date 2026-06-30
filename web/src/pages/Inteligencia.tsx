import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, Minus, MapPin } from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, Cell, ReferenceLine,
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

// ── Constants & mock data ─────────────────────────────────────────────────────

const MODELS = ['Audi Q3 35 TDI', 'VW Golf 1.5 TSI', 'Peugeot 3008 1.5 BlueHDi']
const MARKETS = ['España vs UE', 'Solo España', 'España vs DE']

const RESIDUAL_DATA = [
  { year: '0 km',   spain: 18450, eu: 18100 },
  { year: '1 año',  spain: 15200, eu: 14800 },
  { year: '2 años', spain: 12400, eu: 11900 },
  { year: '3 años', spain: 10100, eu:  9600 },
  { year: '4 años', spain:  8300, eu:  7800 },
]

interface DaysDatum { label: string; days: number; mine: boolean }
const DAYS_DATA: DaysDatum[] = [
  { label: 'Top 10%',     days: 23, mine: false },
  { label: 'Mediana',     days: 39, mine: false },
  { label: 'Tu dealer',   days: 47, mine: true  },
  { label: 'Comp. A',     days: 52, mine: false },
  { label: 'Cola',        days: 68, mine: false },
]

interface DeltaItem { id: string; type: 'SEEN' | 'GONE' | 'DELTA'; label: string; sub: string; color: string }
const DELTA_DATA: DeltaItem[] = [
  { id: 'd1', type: 'SEEN',  label: 'BMW 320d Touring · 27.750 €',  sub: 'alta demanda',       color: '#22c55e' },
  { id: 'd2', type: 'GONE',  label: 'Renault Clio TCe 100',          sub: 'vendido en 14 días', color: '#f87171' },
  { id: 'd3', type: 'DELTA', label: 'Audi Q3 35 TDI · −1.100 €',    sub: 'bajada de precio',   color: '#f59e0b' },
  { id: 'd4', type: 'SEEN',  label: 'VW Passat Variant · 24.900 €',  sub: 'alta demanda',       color: '#22c55e' },
  { id: 'd5', type: 'GONE',  label: 'Seat León 2.0 TDI FR',          sub: 'vendido en 8 días',  color: '#f87171' },
]

interface Region { name: string; pct: number; x: string; y: string; size: number }
const REGIONS: Region[] = [
  { name: 'Madrid',    pct: 28, x: '34%', y: '42%', size: 14 },
  { name: 'Levante',   pct: 26, x: '62%', y: '54%', size: 13 },
  { name: 'Cataluña',  pct: 18, x: '80%', y: '26%', size: 10 },
  { name: 'Andalucía', pct: 16, x: '42%', y: '72%', size:  9 },
  { name: 'Norte',     pct: 12, x: '18%', y: '22%', size:  7 },
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

// ── Glass card wrapper ────────────────────────────────────────────────────────

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

// ── KPI card ──────────────────────────────────────────────────────────────────

interface KpiCardProps {
  dark: boolean
  label: string
  value: number
  prefix?: string
  suffix?: string
  decimals?: number
  textValue?: string
  sub: string
  trend: 'up' | 'down' | 'flat' | 'good'
  trendLabel: string
  spark: number[]
  accent: string
  delay?: number
}

function KpiCard({ dark, label, value, prefix, suffix, decimals, textValue, sub, trend, trendLabel, spark, accent, delay = 0 }: KpiCardProps) {
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

        <div style={{ fontSize: 44, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1, color: textValue ? accent : c.t1, marginBottom: 4 }}>
          {textValue
            ? <span>{textValue}</span>
            : <AnimNum to={value} prefix={prefix} suffix={suffix} decimals={decimals} />
          }
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

// ── Residual value chart ──────────────────────────────────────────────────────

function ResidualChart({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexShrink: 0 }}>
          <div>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Valor residual</h2>
            <p style={{ fontSize: 10.5, color: c.t4 }}>Depreciación observada en mercado real</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 10.5, color: c.t4 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 16, height: 2, background: '#5b8df8', display: 'inline-block', borderRadius: 1 }} />
              España
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 16, borderTop: '2px dashed rgba(148,163,184,0.6)', display: 'inline-block' }} />
              Media UE
            </span>
          </div>
        </div>

        <div style={{ flex: 1, minHeight: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={RESIDUAL_DATA} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="ig-spain" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor="#5b8df8" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#5b8df8" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="ig-eu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor="#94a3b8" stopOpacity={0.10} />
                  <stop offset="100%" stopColor="#94a3b8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
              <XAxis dataKey="year" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(v / 1000).toFixed(0)}k`} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: `1px solid ${c.cardBord}`, borderRadius: 10, fontSize: 11.5, color: c.t1, boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number, name: string) => [`€${v.toLocaleString()}`, name === 'spain' ? 'España' : 'Media UE']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <Area type="monotone" dataKey="spain" stroke="#5b8df8" strokeWidth={2} fill="url(#ig-spain)" dot={false} activeDot={{ r: 3, fill: '#5b8df8', strokeWidth: 0 }} />
              <Area type="monotone" dataKey="eu" stroke="#94a3b8" strokeWidth={1.5} strokeDasharray="5 5" fill="url(#ig-eu)" dot={false} activeDot={{ r: 3, fill: '#94a3b8', strokeWidth: 0 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </GCard>
  )
}

// ── Sweet-spot card ───────────────────────────────────────────────────────────

function SweetSpotCard({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Sweet-spot de precio</h2>
        <p style={{ fontSize: 10.5, color: c.t4 }}>Rango óptimo de venta</p>

        <div style={{ marginTop: 'auto', paddingTop: 28 }}>
          <div style={{ position: 'relative', height: 14, borderRadius: 999, background: 'linear-gradient(90deg, #f87171, #fb923c, #22c55e, #fb923c, #f87171)' }}>
            <div style={{
              position: 'absolute', left: '47%', top: -8,
              width: 4, height: 30, borderRadius: 2,
              background: c.t1,
              boxShadow: `0 0 0 3px ${c.cardBg}`,
            }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10.5, fontFamily: 'ui-monospace,monospace', fontVariantNumeric: 'tabular-nums', marginTop: 10 }}>
            <span style={{ color: c.t4 }}>17.800 €</span>
            <span style={{ color: '#22c55e', fontWeight: 700 }}>óptimo 18.450 €</span>
            <span style={{ color: c.t4 }}>19.500 €</span>
          </div>
        </div>

        <p style={{ fontSize: 12, lineHeight: 1.55, color: c.t2, marginTop: 18, marginBottom: 0 }}>
          A <strong style={{ color: '#22c55e' }}>18.450 €</strong> el vehículo rota en ~23 días con margen óptimo. Por encima de 19.100 € la demanda cae un <strong style={{ color: '#f87171' }}>38%</strong>.
        </p>
      </div>
    </GCard>
  )
}

// ── Price distribution card ───────────────────────────────────────────────────

function PriceDistCard({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Distribución de precio</h2>
        <p style={{ fontSize: 10.5, color: c.t4 }}>Mercado vivo · 100% de anuncios comparables</p>

        <div style={{ marginTop: 'auto', paddingTop: 28 }}>
          <div style={{ position: 'relative', height: 10, borderRadius: 999, background: dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)' }}>
            {/* IQR fill */}
            <div style={{ position: 'absolute', left: '25%', right: '25%', top: 0, bottom: 0, borderRadius: 999, background: 'rgba(91,141,248,0.20)' }} />
            {/* p25 tick */}
            <div style={{ position: 'absolute', left: '25%', top: -5, width: 2, height: 20, background: c.t3, borderRadius: 1 }} />
            {/* median tick */}
            <div style={{ position: 'absolute', left: '50%', top: -7, width: 3, height: 24, background: '#5b8df8', borderRadius: 2, boxShadow: '0 0 6px rgba(91,141,248,0.50)' }} />
            {/* p75 tick */}
            <div style={{ position: 'absolute', left: '75%', top: -5, width: 2, height: 20, background: c.t3, borderRadius: 1 }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10.5, fontFamily: 'ui-monospace,monospace', fontVariantNumeric: 'tabular-nums', marginTop: 10 }}>
            <span style={{ color: c.t4 }}>p25 · 17.200</span>
            <span style={{ color: '#5b8df8', fontWeight: 700 }}>med · 18.450</span>
            <span style={{ color: c.t4 }}>p75 · 19.900</span>
          </div>
        </div>

        <p style={{ fontSize: 12, lineHeight: 1.55, color: c.t2, marginTop: 18, marginBottom: 0 }}>
          A 18.450 € estás en el p50 real del mercado vivo.{' '}
          <strong style={{ color: c.t1 }}>Observado, no estimado.</strong>
        </p>
      </div>
    </GCard>
  )
}

// ── Days in stock chart ───────────────────────────────────────────────────────

function DaysStockChart({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 16, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Días en stock vs mercado</h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>
            Tu dealer <span style={{ color: '#f87171', fontWeight: 700 }}>47 d</span>
            {' · '}
            mediana mercado <span style={{ color: '#22c55e', fontWeight: 700 }}>39 d</span>
          </p>
        </div>
        <div style={{ flex: 1, minHeight: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={DAYS_DATA} margin={{ top: 4, right: 16, left: -24, bottom: 0 }} barSize={22}>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `${v}d`} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: `1px solid ${c.cardBord}`, borderRadius: 10, fontSize: 11.5, color: c.t1, boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number) => [`${v} días`, 'Días en stock']}
                cursor={{ fill: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }}
              />
              <ReferenceLine y={39} stroke="#22c55e" strokeDasharray="4 4" strokeWidth={1.5} />
              <Bar dataKey="days" radius={[4, 4, 0, 0]}>
                {DAYS_DATA.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.mine
                      ? '#f87171'
                      : dark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.10)'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </GCard>
  )
}

// ── Delta en vivo ─────────────────────────────────────────────────────────────

function DeltaLive({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 18px 14px', display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexShrink: 0 }}>
          <div>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Delta en vivo</h2>
            <p style={{ fontSize: 10.5, color: c.t4 }}>SEEN · GONE · Δprecio · tiempo real</p>
          </div>
          <motion.div
            style={{ width: 7, height: 7, borderRadius: '50%', background: '#22c55e' }}
            animate={{ boxShadow: ['0 0 0 3px rgba(34,197,94,0.20)', '0 0 0 7px rgba(34,197,94,0.00)', '0 0 0 3px rgba(34,197,94,0.20)'] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 9, flex: 1, overflowY: 'auto' }}>
          {DELTA_DATA.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.07, duration: 0.3 }}
              style={{
                display: 'flex', alignItems: 'baseline', gap: 8,
                padding: '8px 10px', borderRadius: 10,
                background: c.subBg, border: `1px solid ${c.subBord}`,
              }}
            >
              <span style={{
                fontSize: 9.5, fontWeight: 700, letterSpacing: '0.07em',
                fontFamily: 'ui-monospace,monospace',
                color: item.color, flexShrink: 0, minWidth: 46,
              }}>
                {item.type === 'DELTA' ? 'Δprecio' : item.type}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 11.5, fontWeight: 500, color: c.t2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {item.label}
                </div>
                <div style={{ fontSize: 10, color: c.t4, marginTop: 1 }}>{item.sub}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Regional demand ───────────────────────────────────────────────────────────

function RegionalDemand({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
          <MapPin style={{ width: 12, height: 12, color: '#5b8df8' }} />
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>Demanda por región</h2>
        </div>
        <p style={{ fontSize: 10.5, color: c.t4, marginBottom: 14 }}>Madrid y Levante concentran el 54% de la demanda</p>

        <div style={{
          position: 'relative', flex: 1, minHeight: 100,
          borderRadius: 12,
          background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)',
          border: `1px solid ${c.subBord}`,
          overflow: 'hidden',
        }}>
          <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }} preserveAspectRatio="none">
            <line x1="0" y1="33%" x2="100%" y2="33%" stroke={dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'} />
            <line x1="0" y1="66%" x2="100%" y2="66%" stroke={dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'} />
            <line x1="33%" y1="0" x2="33%" y2="100%" stroke={dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'} />
            <line x1="66%" y1="0" x2="66%" y2="100%" stroke={dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'} />
          </svg>

          {REGIONS.map((r, i) => (
            <motion.div
              key={r.name}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 + i * 0.1, type: 'spring', stiffness: 300, damping: 20 }}
              style={{ position: 'absolute', left: r.x, top: r.y, transform: 'translate(-50%, -50%)' }}
            >
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {r.pct >= 20 && (
                  <motion.div
                    style={{
                      position: 'absolute',
                      width: r.size * 2.4, height: r.size * 2.4,
                      borderRadius: '50%', background: 'rgba(91,141,248,0.14)',
                    }}
                    animate={{ scale: [1, 1.45, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ duration: 2.6, repeat: Infinity, delay: i * 0.4 }}
                  />
                )}
                <div style={{
                  width: r.size, height: r.size, borderRadius: '50%',
                  background: '#5b8df8',
                  opacity: 0.4 + (r.pct / 28) * 0.6,
                  boxShadow: `0 0 ${r.size}px rgba(91,141,248,0.40)`,
                }} />
              </div>
              <div style={{
                position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)',
                marginTop: 3, fontSize: 8.5, fontWeight: 600, color: c.t4, whiteSpace: 'nowrap',
              }}>
                {r.name}
              </div>
            </motion.div>
          ))}
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
          {REGIONS.map(r => (
            <div key={r.name} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#5b8df8', opacity: 0.4 + (r.pct / 28) * 0.6 }} />
              <span style={{ fontSize: 10, color: c.t4 }}>{r.name} {r.pct}%</span>
            </div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Inteligencia() {
  const dark = useIsDark()
  const c = tok(dark)
  const [selectedModel, setSelectedModel] = useState(MODELS[0])
  const [selectedMarket, setSelectedMarket] = useState(MARKETS[0])

  const kpiCards: KpiCardProps[] = [
    {
      dark,
      label: 'Precio óptimo',
      value: 18450,
      prefix: '€',
      sub: 'sweet-spot de venta',
      trend: 'good',
      trendLabel: 'margen máximo',
      accent: '#5b8df8',
      spark: [18800, 18650, 18500, 18450, 18450, 18450],
      delay: 0,
    },
    {
      dark,
      label: 'vs media UE',
      value: -4.2,
      suffix: '%',
      decimals: 1,
      sub: 'posición competitiva',
      trend: 'good',
      trendLabel: '4,2% bajo mercado UE',
      accent: '#22c55e',
      spark: [-2.1, -2.8, -3.5, -3.9, -4.1, -4.2],
      delay: 0.06,
    },
    {
      dark,
      label: 'Días en stock',
      value: 39,
      suffix: ' d',
      sub: 'mediana del mercado',
      trend: 'flat',
      trendLabel: 'estable',
      accent: '#f59e0b',
      spark: [42, 41, 40, 39, 39, 39],
      delay: 0.12,
    },
    {
      dark,
      label: 'Demanda',
      value: 0,
      textValue: 'Alta',
      sub: `${selectedModel} · España`,
      trend: 'up',
      trendLabel: '+12% vs mes anterior',
      accent: '#0ea5e9',
      spark: [60, 65, 72, 78, 84, 90],
      delay: 0.18,
    },
  ]

  const selStyle: React.CSSProperties = {
    cursor: 'pointer',
    fontSize: 12.5,
    fontWeight: 600,
    fontFamily: 'Inter, system-ui',
    color: c.t1,
    background: c.cardBg,
    border: `1px solid ${c.cardBord}`,
    borderRadius: 11,
    padding: '8px 12px',
    outline: 'none',
    backdropFilter: 'blur(16px)',
    WebkitBackdropFilter: 'blur(16px)',
  }

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
            Inteligencia europea · 27 mercados
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: '-0.02em', color: c.t1, lineHeight: 1, marginBottom: 4 }}>
            Inteligencia de mercado
          </h1>
          <p style={{ fontSize: 11.5, color: c.t4 }}>
            Datos observados en tiempo real — no muestras, no modelos.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)} style={selStyle}>
            {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <select value={selectedMarket} onChange={e => setSelectedMarket(e.target.value)} style={selStyle}>
            {MARKETS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
      </motion.div>

      {/* Bento grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>

        {/* Row 1 — KPI cards */}
        {kpiCards.map(card => (
          <KpiCard key={card.label} {...card} />
        ))}

        {/* Row 2 — Residual (2 cols) + Sweet-spot (1 col) + Price dist (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 3', gridRow: '2', minHeight: 260 }}
        >
          <ResidualChart dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '3', gridRow: '2' }}
        >
          <SweetSpotCard dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.32, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '4', gridRow: '2' }}
        >
          <PriceDistCard dark={dark} />
        </motion.div>

        {/* Row 3 — Days stock (2 cols) + Delta live (1 col) + Regional demand (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 3', gridRow: '3', minHeight: 240 }}
        >
          <DaysStockChart dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '3', gridRow: '3' }}
        >
          <DeltaLive dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.42, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '4', gridRow: '3' }}
        >
          <RegionalDemand dark={dark} />
        </motion.div>

      </div>
    </div>
  )
}
