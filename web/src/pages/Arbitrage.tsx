import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, Minus, TrendingDown } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip as ChartTooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import ScoreGauge from '../components/ScoreGauge'
import Card from '../components/Card'
import PremiumGate from '../components/PremiumGate'
import { useIsDark } from '../hooks/useIsDark'
import { useAuthContext } from '../auth/AuthContext'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'
import type { Plan } from '../types'

// ── Animated number ────────────────────────────────────────────────────────────

function AnimNum({ to, prefix = '', suffix = '', decimals = 0 }: { to: number; prefix?: string; suffix?: string; decimals?: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(sp, v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

// ── Spark line ─────────────────────────────────────────────────────────────────

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

// ── Data types ─────────────────────────────────────────────────────────────────

interface Chollo { id: string; model: string; location: string; price: number; marketPrice: number; score: number; daysListed: number; delta: number }
interface CrossGap { id: string; model: string; platformA: string; priceA: number; platformB: string; priceB: number; gap: number }
interface SpreadItem { model: string; spreadPct: number; spreadEur: number }
interface TimePricePoint { day: string; actual?: number; floor?: number }

// ── Mock data ──────────────────────────────────────────────────────────────────

const CHOLLOS: Chollo[] = [
  { id: 'c1', model: 'Peugeot 3008 1.5 BlueHDi', location: 'Madrid',   price: 21_900, marketPrice: 24_100, score: 94, daysListed:  3, delta: -800  },
  { id: 'c2', model: 'VW Golf 1.5 TSI',           location: 'Toledo',   price: 17_300, marketPrice: 18_900, score: 88, daysListed:  6, delta: -500  },
  { id: 'c3', model: 'Audi A4 Avant 2.0 TDI',     location: 'Valencia', price: 26_300, marketPrice: 28_750, score: 86, daysListed: 18, delta: -1_100},
  { id: 'c4', model: 'Seat León FR',               location: 'Sevilla',  price: 19_800, marketPrice: 21_300, score: 81, daysListed:  9, delta: 0     },
  { id: 'c5', model: 'Kia Sportage 1.6 CRDi',      location: 'Bilbao',   price: 20_600, marketPrice: 21_900, score: 76, daysListed: 12, delta: -300  },
]

const CROSS_GAPS: CrossGap[] = [
  { id: 'g1', model: 'BMW 320d Touring',  platformA: 'AutoScout24', priceA: 27_750, platformB: 'coches.net',  priceB: 29_400, gap: 1_650 },
  { id: 'g2', model: 'Renault Clio TCe',  platformA: 'Wallapop',    priceA: 12_900, platformB: 'Milanuncios', priceB: 13_800, gap:   900 },
  { id: 'g3', model: 'Mercedes A 200',    platformA: 'coches.net',  priceA: 24_100, platformB: 'mobile.de',   priceB: 25_600, gap: 1_500 },
]

const SPREAD: SpreadItem[] = [
  { model: 'VW Golf',      spreadPct: 62, spreadEur: 1_860 },
  { model: 'Peugeot 3008', spreadPct: 78, spreadEur: 2_340 },
  { model: 'Audi A4',      spreadPct: 88, spreadEur: 2_640 },
  { model: 'Seat León',    spreadPct: 54, spreadEur: 1_620 },
  { model: 'Kia Sportage', spreadPct: 46, spreadEur: 1_380 },
]

const MAX_SPREAD_PCT = Math.max(...SPREAD.map(s => s.spreadPct))

const TIME_DATA: TimePricePoint[] = [
  { day: 'D+0',  actual: 28_500 },
  { day: 'D+3',  actual: 28_200 },
  { day: 'D+7',  actual: 27_800 },
  { day: 'D+10', actual: 27_400 },
  { day: 'D+14', actual: 26_800 },
  { day: 'D+18', actual: 26_300, floor: 26_300 },
  { day: 'D+21', floor: 26_100 },
  { day: 'D+25', floor: 25_900 },
]

function scoreColor(score: number): string {
  if (score >= 85) return ACCENT
  if (score >= 70) return WARN
  return '#94a3b8'
}

// ── MetricCard ─────────────────────────────────────────────────────────────────

interface MetricCardProps { label: string; value: number; prefix?: string; suffix?: string; decimals?: number; sub: string; trend: 'up' | 'down' | 'flat' | 'good'; trendLabel: string; spark: number[]; delay?: number }

function MetricCard({ label, value, prefix, suffix, decimals, sub, trend, trendLabel, spark, delay = 0 }: MetricCardProps) {
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

// ── ChollosPanel — top score visible (teaser), ranked list is the paid product

function ChollosPanel() {
  const top = CHOLLOS[0]

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 flex shrink-0 items-start justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Chollos ahora · deal-score</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>precio vs mercado vivo</p>
          </div>
          <div className="mt-[-4px] shrink-0">
            <ScoreGauge score={top.score} size={80} label="Top deal" />
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-[7px]">
          {CHOLLOS.map((deal, i) => {
            const sc = scoreColor(deal.score)
            const pctUnder = Math.round(((deal.marketPrice - deal.price) / deal.marketPrice) * 100)
            return (
              <motion.div
                key={deal.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.18 + i * 0.07, duration: 0.32 }}
                className="flex items-center gap-[11px] rounded-xl p-[9px_11px]"
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderLeft: `2px solid ${sc}` }}
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[9px]" style={{ background: `${sc}16`, border: `1px solid ${sc}28` }}>
                  <span className="text-[13px] font-extrabold tabular-nums tracking-[-0.02em]" style={{ color: sc }}>{deal.score}</span>
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>{deal.model}</div>
                  <div className="mt-px text-[10px]" style={{ color: 'var(--text-muted)' }}>
                    {deal.location} · {deal.daysListed}d{deal.delta < 0 ? ` · −€${Math.abs(deal.delta).toLocaleString()}` : ''}
                  </div>
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-[13px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>€{deal.price.toLocaleString()}</div>
                  <div className="mt-px text-[10px] font-bold" style={{ color: sc }}>−{pctUnder}% mkt</div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </Card>
  )
}

// ── CrossPlatformPanel ─────────────────────────────────────────────────────────

function CrossPlatformPanel() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Gap cross-platform</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>mismo coche, distinto precio</p>
        </div>

        <div className="flex flex-1 flex-col">
          {CROSS_GAPS.map((gap, i) => (
            <motion.div key={gap.id} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 + i * 0.08, duration: 0.34 }}>
              <div className="mb-[7px] text-[12.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{gap.model}</div>

              <div className="mb-1 flex items-center justify-between rounded-lg p-[6px_10px]" style={{ background: `${ACCENT}14`, border: `1px solid ${ACCENT}30` }}>
                <span className="text-[11px] font-semibold" style={{ color: ACCENT }}>{gap.platformA}</span>
                <span className="text-[12.5px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>€{gap.priceA.toLocaleString()}</span>
              </div>

              <div className="mb-2 flex items-center justify-between rounded-lg p-[6px_10px]" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
                <span className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>{gap.platformB}</span>
                <span className="text-[12.5px] font-semibold tabular-nums" style={{ color: 'var(--text-secondary)' }}>€{gap.priceB.toLocaleString()}</span>
              </div>

              <div className="flex items-center gap-[5px]" style={{ marginBottom: i < CROSS_GAPS.length - 1 ? 16 : 0 }}>
                <TrendingDown style={{ width: 10, height: 10, color: GOOD }} />
                <span className="text-[11.5px] font-bold" style={{ color: GOOD }}>gap €{gap.gap.toLocaleString()}</span>
              </div>

              {i < CROSS_GAPS.length - 1 && <div className="mb-4 border-t" style={{ borderColor: 'var(--border-subtle)' }} />}
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── SpreadPanel — honest gap: needs a wholesale partner feed, not just a plan

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

// ── TimeArbitragePanel — the "suelo" number is the free teaser, chart is Enterprise

function TimeArbitragePanel({ dark }: { dark: boolean }) {
  const gridColor = dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 flex shrink-0 items-start justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Time-arbitrage</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>trayectoria de precio · suelo estimado</p>
          </div>
          <div className="shrink-0 rounded-full px-2.5 py-[3px]" style={{ background: `${ACCENT}1f`, border: `1px solid ${ACCENT}3d` }}>
            <span className="text-[10px] font-bold" style={{ color: ACCENT }}>suelo ~21d</span>
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={TIME_DATA} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
              <XAxis dataKey="day" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(Number(v) / 1000).toFixed(0)}k`} domain={['dataMin - 300', 'dataMax + 300']} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number) => [`€${v.toLocaleString()}`, '']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <ReferenceLine x="D+18" stroke={`${ACCENT}61`} strokeDasharray="3 5" strokeWidth={1} />
              <Line type="monotone" dataKey="actual" stroke={ACCENT} strokeWidth={2.2} dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} connectNulls={false} name="Actual" />
              <Line type="monotone" dataKey="floor" stroke={ACCENT} strokeWidth={2.2} strokeDasharray="4 5" dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} connectNulls={false} name="Estimado" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-2 shrink-0 text-[10.5px] leading-[1.4]" style={{ color: 'var(--text-muted)' }}>
          <span className="font-medium" style={{ color: 'var(--text-secondary)' }}>Audi A4 Avant</span>
          {' '}· bajó €1.100 en 18 días · suelo estimado <span className="font-bold" style={{ color: ACCENT }}>€26.300</span> a ~21 días
        </div>
      </div>
    </Card>
  )
}

// ── Arbitrage ──────────────────────────────────────────────────────────────────

export default function Arbitrage() {
  const dark = useIsDark()
  const { user } = useAuthContext()
  const plan: Plan = user?.plan ?? 'starter'
  const [zona, setZona]         = useState('Toda España')
  const [segmento, setSegmento] = useState('Todos los segmentos')
  const [margen, setMargen]     = useState('Margen ≥ 1.500 €')

  const kpiCards: MetricCardProps[] = [
    { label: 'Chollos hoy',          value: 37,  sub: 'precio < mercado real',          trend: 'up',   trendLabel: '+5 vs ayer',        spark: [28, 30, 32, 33, 35, 37], delay: 0 },
    { label: 'Margen medio',         value: 2_140, prefix: '€', sub: 'spread estimado',  trend: 'up',   trendLabel: '+€240 vs media',    spark: [1_800, 1_950, 2_000, 2_050, 2_100, 2_140], delay: 0.06 },
    { label: 'Mejor deal-score',     value: 94,  sub: 'Peugeot 3008 · Madrid',           trend: 'flat', trendLabel: 'estable',           spark: [90, 92, 89, 93, 91, 94], delay: 0.12 },
    { label: 'Gaps cross-platform',  value: 12,  sub: 'mismo coche, precio distinto',    trend: 'up',   trendLabel: '+2 nuevos',         spark: [8, 9, 10, 10, 11, 12], delay: 0.18 },
  ]

  const selectClass = "cursor-pointer rounded-[10px] p-[8px_12px] text-[12.5px] font-semibold outline-none"
  const selectStyle: React.CSSProperties = { color: 'var(--text-secondary)', background: 'var(--bg-elevated)', border: '1px solid var(--border-default)' }

  return (
    <div className="mx-auto p-[24px_24px_40px]" style={{ maxWidth: 1360 }}>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        className="mb-[22px] flex flex-wrap items-end justify-between gap-3.5"
      >
        <div>
          <p className="mb-[5px] font-mono text-[11px] tracking-[0.03em]" style={{ color: 'var(--text-muted)' }}>Censo vivo · oportunidades en tu radio</p>
          <h1 className="text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>Arbitrage</h1>
        </div>

        <div className="flex flex-wrap gap-2">
          <select value={zona} onChange={e => setZona(e.target.value)} className={selectClass} style={selectStyle}>
            <option>Toda España</option><option>Madrid</option><option>Cataluña</option><option>Levante</option>
          </select>
          <select value={segmento} onChange={e => setSegmento(e.target.value)} className={selectClass} style={selectStyle}>
            <option>Todos los segmentos</option><option>Compacto</option><option>SUV</option><option>Berlina</option>
          </select>
          <select value={margen} onChange={e => setMargen(e.target.value)} className={selectClass} style={selectStyle}>
            <option>Margen ≥ 1.500 €</option><option>Margen ≥ 1.000 €</option><option>Margen ≥ 500 €</option>
          </select>
        </div>
      </motion.div>

      <div className="mb-4 grid grid-cols-4 gap-3.5">
        {kpiCards.map(card => <MetricCard key={card.label} {...card} />)}
      </div>

      {/* Capa 2 completa (ARBITRAGE.md): un solo unlock para todo el bundle Enterprise,
          en vez de 4 candados repetidos — es un producto, no 4 features sueltas. */}
      <PremiumGate feature="sourcing-ranking" userPlan={plan} what="Ranking de chollos, gaps cross-platform y time-arbitrage completos">
        <div className="grid grid-cols-[3fr_2fr] gap-4">
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ minHeight: 320 }}>
            <ChollosPanel />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}>
            <CrossPlatformPanel />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ minHeight: 260 }}>
            <SpreadPanel />
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.40, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}>
            <TimeArbitragePanel dark={dark} />
          </motion.div>
        </div>
      </PremiumGate>
    </div>
  )
}
