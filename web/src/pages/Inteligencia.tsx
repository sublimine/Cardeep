import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, Cell, ReferenceLine,
  XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip,
  ResponsiveContainer,
} from 'recharts'
import Card from '../components/Card'
import CoverageMap from '../components/CoverageMap'
import PremiumGate from '../components/PremiumGate'
import { useIsDark } from '../hooks/useIsDark'
import { useAuthContext } from '../auth/AuthContext'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'
import type { Plan } from '../types'

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
  { id: 'd1', type: 'SEEN',  label: 'BMW 320d Touring · 27.750 €',  sub: 'alta demanda',       color: GOOD },
  { id: 'd2', type: 'GONE',  label: 'Renault Clio TCe 100',          sub: 'vendido en 14 días', color: BAD },
  { id: 'd3', type: 'DELTA', label: 'Audi Q3 35 TDI · −1.100 €',    sub: 'bajada de precio',   color: WARN },
  { id: 'd4', type: 'SEEN',  label: 'VW Passat Variant · 24.900 €',  sub: 'alta demanda',       color: GOOD },
  { id: 'd5', type: 'GONE',  label: 'Seat León 2.0 TDI FR',          sub: 'vendido en 8 días',  color: BAD },
]
const DELTA_FREE_COUNT = 3

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
  delay?: number
}

function KpiCard({ label, value, prefix, suffix, decimals, textValue, sub, trend, trendLabel, spark, delay = 0 }: KpiCardProps) {
  const trendColor = trend === 'up' || trend === 'good' ? GOOD : trend === 'down' ? BAD : 'var(--text-muted)'
  const TrendIcon  = trend === 'up' || trend === 'good' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : Minus

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}
    >
      <Card hover className="!p-5">
        <div className="mb-3.5 flex items-center justify-between">
          <span className="text-[9.5px] font-bold uppercase tracking-[0.11em]" style={{ color: 'var(--text-secondary)' }}>{label}</span>
          <div className="h-1.5 w-1.5 rounded-full" style={{ background: ACCENT, boxShadow: `0 0 6px ${ACCENT}` }} />
        </div>

        <div className="mb-1 text-[44px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: textValue ? ACCENT : 'var(--text-primary)' }}>
          {textValue ? <span>{textValue}</span> : <AnimNum to={value} prefix={prefix} suffix={suffix} decimals={decimals} />}
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

// ── Residual value chart — Capa 1: España siempre libre, vs-UE gateado ────────

function ResidualChart({ dark, plan }: { dark: boolean; plan: Plan }) {
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'
  const unlocked = plan !== 'starter'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Valor residual</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Depreciación observada en mercado real</p>
          </div>
          <div className="flex items-center gap-3.5 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
            <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-4 rounded-sm" style={{ background: ACCENT }} />España</span>
            {unlocked && <span className="flex items-center gap-1.5"><span className="inline-block w-4 border-t-2 border-dashed" style={{ borderColor: 'rgba(148,163,184,0.6)' }} />Media UE</span>}
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={RESIDUAL_DATA} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="ig-spain" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={ACCENT} stopOpacity={0.25} />
                  <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
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
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number, name: string) => [`€${v.toLocaleString()}`, name === 'spain' ? 'España' : 'Media UE']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <Area type="monotone" dataKey="spain" stroke={ACCENT} strokeWidth={2} fill="url(#ig-spain)" dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} />
              {unlocked && <Area type="monotone" dataKey="eu" stroke="#94a3b8" strokeWidth={1.5} strokeDasharray="5 5" fill="url(#ig-eu)" dot={false} activeDot={{ r: 3, fill: '#94a3b8', strokeWidth: 0 }} />}
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {!unlocked && (
          <div className="mt-2 shrink-0">
            <PremiumGate feature="cross-border-compare" userPlan={plan} what="Comparativa completa vs media UE, cross-border">
              <div className="h-8 rounded-lg" style={{ background: 'var(--bg-surface)' }} />
            </PremiumGate>
          </div>
        )}
      </div>
    </Card>
  )
}

// ── Sweet-spot card ───────────────────────────────────────────────────────────

function SweetSpotCard() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px]">
        <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Sweet-spot de precio</h2>
        <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Rango óptimo de venta</p>

        <div className="mt-auto pt-7">
          <div className="relative h-3.5 rounded-full" style={{ background: `linear-gradient(90deg, ${BAD}, ${WARN}, ${GOOD}, ${WARN}, ${BAD})` }}>
            <div className="absolute rounded-sm" style={{ left: '47%', top: -8, width: 4, height: 30, background: 'var(--text-primary)', boxShadow: '0 0 0 3px var(--bg-elevated)' }} />
          </div>
          <div className="mt-2.5 flex justify-between font-mono text-[10.5px] tabular-nums">
            <span style={{ color: 'var(--text-muted)' }}>17.800 €</span>
            <span className="font-bold" style={{ color: GOOD }}>óptimo 18.450 €</span>
            <span style={{ color: 'var(--text-muted)' }}>19.500 €</span>
          </div>
        </div>

        <p className="mb-0 mt-[18px] text-xs leading-[1.55]" style={{ color: 'var(--text-secondary)' }}>
          A <strong style={{ color: GOOD }}>18.450 €</strong> el vehículo rota en ~23 días con margen óptimo. Por encima de 19.100 € la demanda cae un <strong style={{ color: BAD }}>38%</strong>.
        </p>
      </div>
    </Card>
  )
}

// ── Price distribution card ───────────────────────────────────────────────────

function PriceDistCard() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px]">
        <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Distribución de precio</h2>
        <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Mercado vivo · 100% de anuncios comparables</p>

        <div className="mt-auto pt-7">
          <div className="relative h-2.5 rounded-full" style={{ background: 'var(--border-subtle)' }}>
            <div className="absolute inset-y-0 rounded-full" style={{ left: '25%', right: '25%', background: `${ACCENT}33` }} />
            <div className="absolute rounded-sm" style={{ left: '25%', top: -5, width: 2, height: 20, background: 'var(--text-secondary)' }} />
            <div className="absolute rounded" style={{ left: '50%', top: -7, width: 3, height: 24, background: ACCENT, boxShadow: `0 0 6px ${ACCENT}80` }} />
            <div className="absolute rounded-sm" style={{ left: '75%', top: -5, width: 2, height: 20, background: 'var(--text-secondary)' }} />
          </div>
          <div className="mt-2.5 flex justify-between font-mono text-[10.5px] tabular-nums">
            <span style={{ color: 'var(--text-muted)' }}>p25 · 17.200</span>
            <span className="font-bold" style={{ color: ACCENT }}>med · 18.450</span>
            <span style={{ color: 'var(--text-muted)' }}>p75 · 19.900</span>
          </div>
        </div>

        <p className="mb-0 mt-[18px] text-xs leading-[1.55]" style={{ color: 'var(--text-secondary)' }}>
          A 18.450 € estás en el p50 real del mercado vivo. <strong style={{ color: 'var(--text-primary)' }}>Observado, no estimado.</strong>
        </p>
      </div>
    </Card>
  )
}

// ── Days in stock chart — Capa 1: "tu dealer" libre, comparativa gateada ──────

function DaysStockChart({ dark, plan }: { dark: boolean; plan: Plan }) {
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'
  const mine = DAYS_DATA.find(d => d.mine)!

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Días en stock vs mercado</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
            Tu dealer <span className="font-bold" style={{ color: BAD }}>{mine.days} d</span>
          </p>
        </div>
        <div className="min-h-0 flex-1">
          <PremiumGate feature="market-position-detail" userPlan={plan} what="Comparativa completa: top 10%, mediana, competidores, cola del mercado">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={DAYS_DATA} margin={{ top: 4, right: 16, left: -24, bottom: 0 }} barSize={22}>
                <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `${v}d`} />
                <ChartTooltip
                  contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                  formatter={(v: number) => [`${v} días`, 'Días en stock']}
                  cursor={{ fill: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }}
                />
                <ReferenceLine y={39} stroke={GOOD} strokeDasharray="4 4" strokeWidth={1.5} />
                <Bar dataKey="days" radius={[4, 4, 0, 0]}>
                  {DAYS_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.mine ? BAD : (dark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.10)')} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </PremiumGate>
        </div>
      </div>
    </Card>
  )
}

// ── Delta en vivo — Capa 1: 3 eventos libres, resto + export gateado ──────────

function DeltaLive({ plan }: { plan: Plan }) {
  const free = DELTA_DATA.slice(0, DELTA_FREE_COUNT)
  const rest = DELTA_DATA.slice(DELTA_FREE_COUNT)

  function Row({ item, i }: { item: DeltaItem; i: number }) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -6 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 + i * 0.07, duration: 0.3 }}
        className="flex items-baseline gap-2 rounded-[10px] p-[8px_10px]"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
      >
        <span className="w-[46px] shrink-0 font-mono text-[9.5px] font-bold tracking-[0.07em]" style={{ color: item.color }}>
          {item.type === 'DELTA' ? 'Δprecio' : item.type}
        </span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-[11.5px] font-medium" style={{ color: 'var(--text-secondary)' }}>{item.label}</div>
          <div className="mt-px text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.sub}</div>
        </div>
      </motion.div>
    )
  }

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Delta en vivo</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>SEEN · GONE · Δprecio · tiempo real</p>
          </div>
          <motion.div
            className="h-1.5 w-1.5 rounded-full"
            style={{ background: GOOD }}
            animate={{ boxShadow: [`0 0 0 3px ${GOOD}33`, `0 0 0 7px ${GOOD}00`, `0 0 0 3px ${GOOD}33`] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>

        <div className="flex flex-1 flex-col gap-[9px] overflow-y-auto">
          {free.map((item, i) => <Row key={item.id} item={item} i={i} />)}
          {rest.length > 0 && (
            <PremiumGate feature="delta-feed-full" userPlan={plan} what="Feed completo + históricos + export">
              <div className="flex flex-col gap-[9px]">
                {rest.map((item, i) => <Row key={item.id} item={item} i={i + DELTA_FREE_COUNT} />)}
              </div>
            </PremiumGate>
          )}
        </div>
      </div>
    </Card>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Inteligencia() {
  const dark = useIsDark()
  const { user } = useAuthContext()
  const plan = user?.plan ?? 'starter'
  const [selectedModel, setSelectedModel] = useState(MODELS[0])
  const [selectedMarket, setSelectedMarket] = useState(MARKETS[0])

  const kpiCards: KpiCardProps[] = [
    { label: 'Precio óptimo', value: 18450, prefix: '€', sub: 'sweet-spot de venta', trend: 'good', trendLabel: 'margen máximo', spark: [18800, 18650, 18500, 18450, 18450, 18450], delay: 0 },
    { label: 'vs media UE', value: -4.2, suffix: '%', decimals: 1, sub: 'posición competitiva', trend: 'good', trendLabel: '4,2% bajo mercado UE', spark: [-2.1, -2.8, -3.5, -3.9, -4.1, -4.2], delay: 0.06 },
    { label: 'Días en stock', value: 39, suffix: ' d', sub: 'mediana del mercado', trend: 'flat', trendLabel: 'estable', spark: [42, 41, 40, 39, 39, 39], delay: 0.12 },
    { label: 'Demanda', value: 0, textValue: 'Alta', sub: `${selectedModel} · España`, trend: 'up', trendLabel: '+12% vs mes anterior', spark: [60, 65, 72, 78, 84, 90], delay: 0.18 },
  ]

  return (
    <div className="mx-auto p-[24px_24px_40px]" style={{ maxWidth: 1360 }}>

      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        className="mb-[22px] flex flex-wrap items-end justify-between gap-4"
      >
        <div>
          <div className="mb-1.5 font-mono text-[10.5px] tracking-[0.04em]" style={{ color: 'var(--text-muted)' }}>Inteligencia europea · 27 mercados</div>
          <h1 className="mb-1 text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>Inteligencia de mercado</h1>
          <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>Datos observados en tiempo real — no muestras, no modelos.</p>
        </div>

        <div className="flex gap-2">
          <select
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="cursor-pointer rounded-[11px] p-[8px_12px] text-[12.5px] font-semibold outline-none"
            style={{ color: 'var(--text-primary)', background: 'var(--bg-elevated)', border: '1px solid var(--border-default)' }}
          >
            {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <select
            value={selectedMarket}
            onChange={e => setSelectedMarket(e.target.value)}
            className="cursor-pointer rounded-[11px] p-[8px_12px] text-[12.5px] font-semibold outline-none"
            style={{ color: 'var(--text-primary)', background: 'var(--bg-elevated)', border: '1px solid var(--border-default)' }}
          >
            {MARKETS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
      </motion.div>

      {/* Bento grid */}
      <div className="grid grid-cols-4 gap-3.5">

        {kpiCards.map(card => (
          <KpiCard key={card.label} {...card} />
        ))}

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '2', minHeight: 260 }}>
          <ResidualChart dark={dark} plan={plan} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3', gridRow: '2' }}>
          <SweetSpotCard />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.32, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '4', gridRow: '2' }}>
          <PriceDistCard />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '3', minHeight: 240 }}>
          <DaysStockChart dark={dark} plan={plan} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.42, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3 / 5', gridRow: '3', minHeight: 420 }}>
          <Card className="!p-0 h-full">
            <div className="p-[18px_20px] h-full flex flex-col">
              <CoverageMap />
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3', gridRow: '4' }}>
          <DeltaLive plan={plan} />
        </motion.div>

      </div>
    </div>
  )
}
