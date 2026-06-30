import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, Minus, TrendingDown } from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import ScoreGauge from '../components/ScoreGauge'

// ── Theme observer ─────────────────────────────────────────────────────────────

function useIsDark() {
  const [dark, setDark] = useState(() => !document.documentElement.classList.contains('light'))
  useEffect(() => {
    const obs = new MutationObserver(() =>
      setDark(!document.documentElement.classList.contains('light'))
    )
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return dark
}

// ── Token helpers ──────────────────────────────────────────────────────────────

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

// ── Glass card wrapper ─────────────────────────────────────────────────────────

function GCard({
  dark,
  children,
  style,
}: {
  dark: boolean
  children: React.ReactNode
  style?: React.CSSProperties
}) {
  const c = tok(dark)
  return (
    <div
      style={{
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
      }}
    >
      {children}
    </div>
  )
}

// ── Animated number ────────────────────────────────────────────────────────────

function AnimNum({
  to,
  prefix = '',
  suffix = '',
  decimals = 0,
}: {
  to: number
  prefix?: string
  suffix?: string
  decimals?: number
}) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(
    sp,
    v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`,
  )
  useEffect(() => { mv.set(to) }, [to]) // eslint-disable-line react-hooks/exhaustive-deps
  return <motion.span>{d}</motion.span>
}

// ── Spark line ─────────────────────────────────────────────────────────────────

function Spark({ values, color, height = 28 }: { values: number[]; color: string; height?: number }) {
  if (values.length < 2) return null
  const max = Math.max(...values)
  const min = Math.min(...values)
  const range = max - min || 1
  const W = 64
  const H = height
  const pts = values.map((v, i): [number, number] => [
    (i / (values.length - 1)) * W,
    H - ((v - min) / range) * (H - 4) + 2,
  ])
  const line = pts.map(([x, y]) => `${x},${y}`).join(' ')
  const area =
    `M${pts[0][0]},${H} ` +
    pts.map(([x, y]) => `L${x},${y}`).join(' ') +
    ` L${pts.at(-1)![0]},${H} Z`
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: 'block' }}>
      <path d={area} fill={color} fillOpacity={0.12} />
      <polyline
        points={line}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

// ── Data types ─────────────────────────────────────────────────────────────────

interface Chollo {
  id: string
  model: string
  location: string
  price: number
  marketPrice: number
  score: number
  daysListed: number
  delta: number
}

interface CrossGap {
  id: string
  model: string
  platformA: string
  priceA: number
  platformB: string
  priceB: number
  gap: number
}

interface SpreadItem {
  model: string
  spreadPct: number
  spreadEur: number
}

interface TimePricePoint {
  day: string
  actual?: number
  floor?: number
}

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

// ── Score badge color ──────────────────────────────────────────────────────────

function scoreColor(score: number): string {
  if (score >= 85) return '#5b8df8'
  if (score >= 70) return '#f59e0b'
  return '#94a3b8'
}

// ── MetricCard ─────────────────────────────────────────────────────────────────

interface MetricCardProps {
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

function MetricCard({
  dark, label, value, prefix, suffix, decimals, sub,
  trend, trendLabel, spark, accent, delay = 0,
}: MetricCardProps) {
  const c = tok(dark)
  const trendColor =
    trend === 'up' || trend === 'good' ? '#22c55e' :
    trend === 'down' ? '#f87171' : c.t4
  const TrendIcon =
    trend === 'up' || trend === 'good' ? ArrowUpRight :
    trend === 'down' ? ArrowDownRight : Minus

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

// ── ChollosPanel ───────────────────────────────────────────────────────────────

function ChollosPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const top = CHOLLOS[0]

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>

        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
          marginBottom: 14, flexShrink: 0,
        }}>
          <div>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
              Chollos ahora · deal-score
            </h2>
            <p style={{ fontSize: 10.5, color: c.t4 }}>precio vs mercado vivo</p>
          </div>
          {/* ScoreGauge: top deal spotlight */}
          <div style={{ flexShrink: 0, marginTop: -4 }}>
            <ScoreGauge score={top.score} size={80} label="Top deal" />
          </div>
        </div>

        {/* Ranked rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 7, flex: 1 }}>
          {CHOLLOS.map((deal, i) => {
            const sc = scoreColor(deal.score)
            const pctUnder = Math.round(((deal.marketPrice - deal.price) / deal.marketPrice) * 100)
            return (
              <motion.div
                key={deal.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.18 + i * 0.07, duration: 0.32 }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 11,
                  padding: '9px 11px',
                  borderRadius: 12,
                  background: c.subBg,
                  border: `1px solid ${c.subBord}`,
                  borderLeft: `2px solid ${sc}`,
                }}
              >
                {/* Score badge */}
                <div style={{
                  width: 36, height: 36, borderRadius: 9, flexShrink: 0,
                  background: `${sc}16`,
                  border: `1px solid ${sc}28`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <span style={{
                    fontSize: 13, fontWeight: 800, color: sc,
                    fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em',
                  }}>
                    {deal.score}
                  </span>
                </div>

                {/* Model + meta */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontSize: 12, fontWeight: 600, color: c.t1,
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}>
                    {deal.model}
                  </div>
                  <div style={{ fontSize: 10, color: c.t4, marginTop: 1 }}>
                    {deal.location} · {deal.daysListed}d
                    {deal.delta < 0 ? ` · −€${Math.abs(deal.delta).toLocaleString()}` : ''}
                  </div>
                </div>

                {/* Price + discount */}
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{
                    fontSize: 13, fontWeight: 700, color: c.t1,
                    fontVariantNumeric: 'tabular-nums',
                  }}>
                    €{deal.price.toLocaleString()}
                  </div>
                  <div style={{ fontSize: 10, color: sc, fontWeight: 700, marginTop: 1 }}>
                    −{pctUnder}% mkt
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </GCard>
  )
}

// ── CrossPlatformPanel ─────────────────────────────────────────────────────────

function CrossPlatformPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 18px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 16, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
            Gap cross-platform
          </h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>mismo coche, distinto precio</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 0, flex: 1 }}>
          {CROSS_GAPS.map((gap, i) => (
            <motion.div
              key={gap.id}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.08, duration: 0.34 }}
            >
              {/* Model name */}
              <div style={{ fontSize: 12.5, fontWeight: 600, color: c.t1, marginBottom: 7 }}>
                {gap.model}
              </div>

              {/* Platform A — buy (cheaper) */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '6px 10px', borderRadius: 8,
                background: 'rgba(91,141,248,0.08)',
                border: '1px solid rgba(91,141,248,0.18)',
                marginBottom: 4,
              }}>
                <span style={{ fontSize: 11, color: '#5b8df8', fontWeight: 600 }}>
                  {gap.platformA}
                </span>
                <span style={{
                  fontSize: 12.5, fontWeight: 700, color: c.t1,
                  fontVariantNumeric: 'tabular-nums',
                }}>
                  €{gap.priceA.toLocaleString()}
                </span>
              </div>

              {/* Platform B — higher (proof of market) */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '6px 10px', borderRadius: 8,
                background: c.subBg,
                border: `1px solid ${c.subBord}`,
                marginBottom: 8,
              }}>
                <span style={{ fontSize: 11, color: c.t3 }}>{gap.platformB}</span>
                <span style={{
                  fontSize: 12.5, fontWeight: 600, color: c.t2,
                  fontVariantNumeric: 'tabular-nums',
                }}>
                  €{gap.priceB.toLocaleString()}
                </span>
              </div>

              {/* Gap badge */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: i < CROSS_GAPS.length - 1 ? 16 : 0 }}>
                <TrendingDown style={{ width: 10, height: 10, color: '#22c55e' }} />
                <span style={{ fontSize: 11.5, fontWeight: 700, color: '#22c55e' }}>
                  gap €{gap.gap.toLocaleString()}
                </span>
              </div>

              {i < CROSS_GAPS.length - 1 && (
                <div style={{ borderTop: `1px solid ${c.div}`, marginBottom: 16 }} />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── SpreadPanel ────────────────────────────────────────────────────────────────

function SpreadPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 16, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
            Spread retail vs wholesale
          </h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>margen de flip por modelo</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, flex: 1 }}>
          {SPREAD.map((item, i) => {
            const barWidth = Math.round((item.spreadPct / MAX_SPREAD_PCT) * 100)
            return (
              <motion.div
                key={item.model}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.18 + i * 0.07 }}
              >
                <div style={{
                  display: 'flex', justifyContent: 'space-between', marginBottom: 6,
                }}>
                  <span style={{ fontSize: 12, fontWeight: 500, color: c.t2 }}>
                    {item.model}
                  </span>
                  <span style={{
                    fontSize: 12, fontWeight: 700, color: '#5b8df8',
                    fontVariantNumeric: 'tabular-nums',
                  }}>
                    +€{item.spreadEur.toLocaleString()}
                  </span>
                </div>
                <div style={{
                  height: 7, borderRadius: 5,
                  background: dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)',
                  overflow: 'hidden',
                }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barWidth}%` }}
                    transition={{ delay: 0.32 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                    style={{
                      height: '100%', borderRadius: 5,
                      background: 'linear-gradient(90deg, #3b82f6, #5b8df8)',
                      boxShadow: '0 0 6px rgba(91,141,248,0.35)',
                    }}
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

// ── TimeArbitragePanel ─────────────────────────────────────────────────────────

function TimeArbitragePanel({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const gridColor = dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>

        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
          marginBottom: 14, flexShrink: 0,
        }}>
          <div>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
              Time-arbitrage
            </h2>
            <p style={{ fontSize: 10.5, color: c.t4 }}>trayectoria de precio · suelo estimado</p>
          </div>
          <div style={{
            padding: '3px 10px', borderRadius: 99,
            background: 'rgba(91,141,248,0.12)',
            border: '1px solid rgba(91,141,248,0.24)',
            flexShrink: 0,
          }}>
            <span style={{ fontSize: 10, fontWeight: 700, color: '#5b8df8' }}>suelo ~21d</span>
          </div>
        </div>

        {/* Chart */}
        <div style={{ flex: 1, minHeight: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={TIME_DATA} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
              <XAxis
                dataKey="day"
                tick={{ fontSize: 9.5, fill: tickColor }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 9.5, fill: tickColor }}
                axisLine={false}
                tickLine={false}
                tickFormatter={v => `€${(Number(v) / 1000).toFixed(0)}k`}
                domain={['dataMin - 300', 'dataMax + 300']}
              />
              <ChartTooltip
                contentStyle={{
                  background: dark ? '#0e0e1a' : '#fff',
                  border: `1px solid ${c.cardBord}`,
                  borderRadius: 10,
                  fontSize: 11.5,
                  color: c.t1,
                  boxShadow: '0 8px 24px rgba(0,0,0,0.18)',
                }}
                formatter={(v: number) => [`€${v.toLocaleString()}`, '']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <ReferenceLine
                x="D+18"
                stroke="rgba(91,141,248,0.38)"
                strokeDasharray="3 5"
                strokeWidth={1}
              />
              {/* Actual price trajectory */}
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#5b8df8"
                strokeWidth={2.2}
                dot={false}
                activeDot={{ r: 3, fill: '#5b8df8', strokeWidth: 0 }}
                connectNulls={false}
                name="Actual"
              />
              {/* Estimated floor projection */}
              <Line
                type="monotone"
                dataKey="floor"
                stroke="#5b8df8"
                strokeWidth={2.2}
                strokeDasharray="4 5"
                dot={false}
                activeDot={{ r: 3, fill: '#5b8df8', strokeWidth: 0 }}
                connectNulls={false}
                name="Estimado"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Footer note */}
        <div style={{ fontSize: 10.5, color: c.t4, marginTop: 8, flexShrink: 0, lineHeight: 1.4 }}>
          <span style={{ color: c.t2, fontWeight: 500 }}>Audi A4 Avant</span>
          {' '}· bajó €1.100 en 18 días · suelo estimado{' '}
          <span style={{ color: '#5b8df8', fontWeight: 700 }}>€26.300</span>
          {' '}a ~21 días
        </div>
      </div>
    </GCard>
  )
}

// ── Arbitrage ──────────────────────────────────────────────────────────────────

export default function Arbitrage() {
  const dark = useIsDark()
  const [zona, setZona]         = useState('Toda España')
  const [segmento, setSegmento] = useState('Todos los segmentos')
  const [margen, setMargen]     = useState('Margen ≥ 1.500 €')

  const c = tok(dark)

  const kpiCards = [
    {
      label:      'Chollos hoy',
      value:      37,
      sub:        'precio < mercado real',
      trend:      'up' as const,
      trendLabel: '+5 vs ayer',
      accent:     '#5b8df8',
      spark:      [28, 30, 32, 33, 35, 37],
      delay:      0,
    },
    {
      label:      'Margen medio',
      value:      2_140,
      prefix:     '€',
      sub:        'spread estimado',
      trend:      'up' as const,
      trendLabel: '+€240 vs media',
      accent:     '#22c55e',
      spark:      [1_800, 1_950, 2_000, 2_050, 2_100, 2_140],
      delay:      0.06,
    },
    {
      label:      'Mejor deal-score',
      value:      94,
      sub:        'Peugeot 3008 · Madrid',
      trend:      'flat' as const,
      trendLabel: 'estable',
      accent:     '#5b8df8',
      spark:      [90, 92, 89, 93, 91, 94],
      delay:      0.12,
    },
    {
      label:      'Gaps cross-platform',
      value:      12,
      sub:        'mismo coche, precio distinto',
      trend:      'up' as const,
      trendLabel: '+2 nuevos',
      accent:     '#f59e0b',
      spark:      [8, 9, 10, 10, 11, 12],
      delay:      0.18,
    },
  ]

  const selectStyle: React.CSSProperties = {
    cursor:        'pointer',
    fontSize:      12.5,
    fontWeight:    600,
    color:         c.t2,
    background:    c.cardBg,
    border:        `1px solid ${c.cardBord}`,
    borderRadius:  10,
    padding:       '8px 12px',
    outline:       'none',
    fontFamily:    'inherit',
    backdropFilter:'blur(12px)',
  }

  return (
    <div style={{ padding: '24px 24px 40px', maxWidth: 1360, margin: '0 auto' }}>

      {/* ── Page header ──────────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        style={{
          marginBottom: 22,
          display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between',
          flexWrap: 'wrap', gap: 14,
        }}
      >
        <div>
          <p style={{
            fontFamily: '"JetBrains Mono","Fira Code",monospace',
            fontSize: 11, color: c.t4, marginBottom: 5,
            fontVariantNumeric: 'tabular-nums', letterSpacing: '0.03em',
          }}>
            Censo vivo · oportunidades en tu radio
          </p>
          <h1 style={{
            fontSize: 22, fontWeight: 800, letterSpacing: '-0.02em',
            color: c.t1, lineHeight: 1,
          }}>
            Arbitrage
          </h1>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <select value={zona}     onChange={e => setZona(e.target.value)}     style={selectStyle}>
            <option>Toda España</option>
            <option>Madrid</option>
            <option>Cataluña</option>
            <option>Levante</option>
          </select>
          <select value={segmento} onChange={e => setSegmento(e.target.value)} style={selectStyle}>
            <option>Todos los segmentos</option>
            <option>Compacto</option>
            <option>SUV</option>
            <option>Berlina</option>
          </select>
          <select value={margen}   onChange={e => setMargen(e.target.value)}   style={selectStyle}>
            <option>Margen ≥ 1.500 €</option>
            <option>Margen ≥ 1.000 €</option>
            <option>Margen ≥ 500 €</option>
          </select>
        </div>
      </motion.div>

      {/* ── KPI band — 4 metric cards ────────────────────────────────────────── */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 14, marginBottom: 16,
      }}>
        {kpiCards.map(card => (
          <MetricCard key={card.label} dark={dark} {...card} />
        ))}
      </div>

      {/* ── Content grid — 2 rows × (3fr : 2fr) ─────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 16 }}>

        {/* Row 1 col 1 — Chollos ahora · deal-score */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ minHeight: 320 }}
        >
          <ChollosPanel dark={dark} />
        </motion.div>

        {/* Row 1 col 2 — Gap cross-platform */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
        >
          <CrossPlatformPanel dark={dark} />
        </motion.div>

        {/* Row 2 col 1 — Spread retail vs wholesale */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ minHeight: 260 }}
        >
          <SpreadPanel dark={dark} />
        </motion.div>

        {/* Row 2 col 2 — Time-arbitrage */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.40, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
        >
          <TimeArbitragePanel dark={dark} />
        </motion.div>

      </div>
    </div>
  )
}
