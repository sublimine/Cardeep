// Finance — Fleet P&L · Cashflow · Expenses · 6-month view
// Pattern: tok() + GCard + AnimNum + Spark (mirrors Dashboard.tsx)

import React, { useEffect, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { TrendingDown, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { Badge } from '../components'
import type { FinanceRow } from '../types'

// ── Theme helpers ─────────────────────────────────────────────────────────────

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

function tok(dark: boolean) {
  return {
    t1:       dark ? '#f1f5f9' : '#0f172a',
    t2:       dark ? '#cbd5e1' : '#334155',
    t3:       dark ? '#94a3b8' : '#64748b',
    t4:       dark ? '#475569' : '#94a3b8',
    div:      dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)',
    cardBg:   dark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.82)',
    cardBord: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
    subBg:    dark ? 'rgba(255,255,255,0.03)'  : 'rgba(0,0,0,0.03)',
    subBord:  dark ? 'rgba(255,255,255,0.06)'  : 'rgba(0,0,0,0.07)',
  }
}

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
        borderRadius: 14,
        backdropFilter: 'blur(24px) saturate(180%)',
        WebkitBackdropFilter: 'blur(24px) saturate(180%)',
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
  const d = useTransform(sp, (v) =>
    `${prefix}${decimals > 0 ? v.toFixed(decimals) : Math.round(v).toLocaleString()}${suffix}`,
  )
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

function Spark({
  values,
  color,
  height = 28,
}: {
  values: number[]
  color: string
  height?: number
}) {
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
  const last = pts[pts.length - 1]
  const area =
    `M${pts[0][0]},${H} ` +
    pts.map(([x, y]) => `L${x},${y}`).join(' ') +
    ` L${last[0]},${H} Z`
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

// ── Static data ───────────────────────────────────────────────────────────────

const MONTHLY = [
  { month: 'Nov', revenue: 310000, cost: 249000, margin: 61000,  cashflow: 41000 },
  { month: 'Dec', revenue: 360000, cost: 288000, margin: 72000,  cashflow: 54000 },
  { month: 'Jan', revenue: 270000, cost: 216000, margin: 54000,  cashflow: 32000 },
  { month: 'Feb', revenue: 395000, cost: 316000, margin: 79000,  cashflow: 58000 },
  { month: 'Mar', revenue: 475000, cost: 380000, margin: 95000,  cashflow: 71000 },
  { month: 'Apr', revenue: 437000, cost: 349600, margin: 87400,  cashflow: 64000 },
]

const EXPENSES = [
  { category: 'Acquisition',      amount: 1_798_600, pct: 68.2 },
  { category: 'Transport & Prep', amount:   182_400, pct:  6.9 },
  { category: 'Staff & Ops',      amount:   198_000, pct:  7.5 },
  { category: 'Marketing',        amount:    95_200, pct:  3.6 },
  { category: 'Platform fees',    amount:    94_800, pct:  3.6 },
  { category: 'Other',            amount:   265_900, pct: 10.1 },
]

const EXPENSE_COLORS = ['#3b82f6', '#0891b2', '#059669', '#d97706', '#e11d48', '#94a3b8']

const TOP_VEHICLES: FinanceRow[] = [
  { vehicleId: 'v1',  vehicleName: 'BMW X5 2021',        buyPrice: 38000, sellPrice: 46500, margin:  8500, marginPct: 22.4, soldAt: '2026-04-15' },
  { vehicleId: 'v2',  vehicleName: 'Porsche Macan 2020',  buyPrice: 44000, sellPrice: 52000, margin:  8000, marginPct: 18.2, soldAt: '2026-04-12' },
  { vehicleId: 'v3',  vehicleName: 'Audi Q5 2021',        buyPrice: 32000, sellPrice: 38500, margin:  6500, marginPct: 20.3, soldAt: '2026-04-10' },
  { vehicleId: 'v4',  vehicleName: 'Mercedes GLC 2020',   buyPrice: 36000, sellPrice: 42000, margin:  6000, marginPct: 16.7, soldAt: '2026-04-08' },
  { vehicleId: 'v5',  vehicleName: 'BMW 530d 2020',       buyPrice: 28000, sellPrice: 33500, margin:  5500, marginPct: 19.6, soldAt: '2026-04-06' },
  { vehicleId: 'v6',  vehicleName: 'VW Tiguan 2022',      buyPrice: 24000, sellPrice: 29000, margin:  5000, marginPct: 20.8, soldAt: '2026-04-04' },
  { vehicleId: 'v7',  vehicleName: 'Skoda Octavia 2021',  buyPrice: 14000, sellPrice: 17500, margin:  3500, marginPct: 25.0, soldAt: '2026-04-02' },
  { vehicleId: 'v8',  vehicleName: 'Toyota Yaris 2022',   buyPrice: 10500, sellPrice: 13500, margin:  3000, marginPct: 28.6, soldAt: '2026-03-30' },
  { vehicleId: 'v9',  vehicleName: 'Renault Clio 2020',   buyPrice:  9000, sellPrice:  8200, margin:  -800, marginPct:  -8.9, soldAt: '2026-04-14' },
  { vehicleId: 'v10', vehicleName: 'Citroën C3 2019',     buyPrice:  7500, sellPrice:  7100, margin:  -400, marginPct:  -5.3, soldAt: '2026-04-11' },
]

const ALERTS = TOP_VEHICLES.filter((r) => r.margin < 0)

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Finance() {
  const dark = useIsDark()
  const c = tok(dark)

  const totalRevenue  = MONTHLY.reduce((s, m) => s + m.revenue,  0)
  const totalCost     = MONTHLY.reduce((s, m) => s + m.cost,     0)
  const totalMargin   = MONTHLY.reduce((s, m) => s + m.margin,   0)
  const totalCashflow = MONTHLY.reduce((s, m) => s + m.cashflow, 0)
  const avgMarginPct  = (totalMargin / totalRevenue) * 100

  const tickColor  = dark ? '#475569' : '#94a3b8'
  const gridColor  = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'
  const tooltipBg  = dark ? '#0e0e1a' : '#fff'
  const cursorFill = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'

  const kpis = [
    {
      label: 'Revenue (6mo)',
      value: totalRevenue / 1000,
      prefix: '€', suffix: 'k',
      sub: `Cost base €${(totalCost / 1_000_000).toFixed(2)}M`,
      trendUp: true,
      trendLabel: '+14% vs prior',
      spark: MONTHLY.map((m) => m.revenue / 1000),
      accent: '#3b82f6',
    },
    {
      label: 'Gross Margin',
      value: totalMargin / 1000,
      prefix: '€', suffix: 'k',
      sub: `Avg ${avgMarginPct.toFixed(1)}% rate`,
      trendUp: true,
      trendLabel: '+8% vs prior',
      spark: MONTHLY.map((m) => m.margin / 1000),
      accent: '#059669',
    },
    {
      label: 'Net Cashflow',
      value: totalCashflow / 1000,
      prefix: '€', suffix: 'k',
      sub: 'After all operating costs',
      trendUp: true,
      trendLabel: '+11% vs prior',
      spark: MONTHLY.map((m) => m.cashflow / 1000),
      accent: '#0891b2',
    },
    {
      label: 'Margin Alerts',
      value: ALERTS.length,
      prefix: '', suffix: ' vehicles',
      sub: 'Sold below purchase cost',
      trendUp: false,
      trendLabel: ALERTS.length > 0 ? 'Action needed' : 'All clear',
      spark: [0, 1, 2, 1, 2, ALERTS.length],
      accent: ALERTS.length > 0 ? '#e11d48' : '#059669',
    },
  ]

  return (
    <div
      style={{
        padding: 'clamp(16px, 3vw, 24px)',
        maxWidth: 1200,
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
      }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}
      >
        <div>
          <h1
            style={{
              fontSize: 22,
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: c.t1,
              lineHeight: 1,
            }}
          >
            Finance
          </h1>
          <p style={{ fontSize: 12, color: c.t3, marginTop: 4 }}>
            Fleet P&L · Cashflow · Expenses · 6-month view
          </p>
        </div>
        <div
          style={{
            padding: '5px 12px',
            borderRadius: 8,
            background: 'rgba(59,130,246,0.10)',
            border: '1px solid rgba(59,130,246,0.22)',
            fontSize: 11,
            fontWeight: 700,
            color: '#3b82f6',
          }}
        >
          Apr 2026
        </div>
      </motion.div>

      {/* KPI cards — 4 columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
        {kpis.map(({ label, value, prefix, suffix, sub, trendUp, trendLabel, spark, accent }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.40, ease: [0.32, 0.72, 0, 1] }}
            whileHover={{ y: -2, transition: { duration: 0.18 } }}
          >
            <GCard dark={dark} style={{ padding: '18px 20px 14px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 12,
                }}
              >
                <span
                  style={{
                    fontSize: 9.5,
                    fontWeight: 700,
                    letterSpacing: '0.11em',
                    textTransform: 'uppercase',
                    color: c.t3,
                  }}
                >
                  {label}
                </span>
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    background: accent,
                    boxShadow: `0 0 6px ${accent}`,
                    display: 'inline-block',
                  }}
                />
              </div>
              <div
                style={{
                  fontSize: 36,
                  fontWeight: 800,
                  letterSpacing: '-0.03em',
                  lineHeight: 1,
                  color: c.t1,
                  marginBottom: 3,
                }}
              >
                <AnimNum to={value} prefix={prefix} suffix={suffix} />
              </div>
              <div style={{ fontSize: 10, color: c.t4, marginBottom: 12 }}>{sub}</div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: 10,
                  borderTop: `1px solid ${c.div}`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  {trendUp ? (
                    <ArrowUpRight style={{ width: 10, height: 10, color: '#22c55e' }} />
                  ) : (
                    <ArrowDownRight style={{ width: 10, height: 10, color: '#f87171' }} />
                  )}
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 600,
                      color: trendUp ? '#22c55e' : '#f87171',
                    }}
                  >
                    {trendLabel}
                  </span>
                </div>
                <Spark values={spark} color={accent} height={22} />
              </div>
            </GCard>
          </motion.div>
        ))}
      </div>

      {/* P&L chart + Expense breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 14 }}>
        {/* AreaChart */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.30, duration: 0.38 }}
        >
          <GCard dark={dark} style={{ padding: '18px 20px 14px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 14,
              }}
            >
              <div>
                <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
                  Revenue vs Cost — P&L
                </h2>
                <p style={{ fontSize: 10.5, color: c.t4 }}>6-month trend</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 10, color: c.t4 }}>
                {(
                  [
                    ['#3b82f6', 'Revenue'],
                    ['#f87171', 'Cost'],
                    ['#22c55e', 'Margin'],
                  ] as [string, string][]
                ).map(([col, lbl]) => (
                  <span key={lbl} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span
                      style={{
                        width: 10,
                        height: 2,
                        background: col,
                        display: 'inline-block',
                        borderRadius: 1,
                      }}
                    />
                    {lbl}
                  </span>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={MONTHLY} margin={{ top: 4, right: 0, left: -24, bottom: 0 }}>
                <defs>
                  <linearGradient id="fgRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.22} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fgCost" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f87171" stopOpacity={0.14} />
                    <stop offset="100%" stopColor="#f87171" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fgMar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22c55e" stopOpacity={0.22} />
                    <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 9.5, fill: tickColor }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 9.5, fill: tickColor }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: number) => `€${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    background: tooltipBg,
                    border: `1px solid ${c.cardBord}`,
                    borderRadius: 10,
                    fontSize: 11.5,
                    color: c.t1,
                    boxShadow: '0 8px 24px rgba(0,0,0,0.18)',
                  }}
                  formatter={(v: number, name: string) => [
                    `€${v.toLocaleString()}`,
                    name === 'revenue' ? 'Revenue' : name === 'cost' ? 'Cost' : 'Margin',
                  ]}
                  cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#fgRev)"
                  dot={false}
                  activeDot={{ r: 3, fill: '#3b82f6', strokeWidth: 0 }}
                />
                <Area
                  type="monotone"
                  dataKey="cost"
                  stroke="#f87171"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  fill="url(#fgCost)"
                  dot={false}
                  activeDot={{ r: 3, fill: '#f87171', strokeWidth: 0 }}
                />
                <Area
                  type="monotone"
                  dataKey="margin"
                  stroke="#22c55e"
                  strokeWidth={2}
                  fill="url(#fgMar)"
                  dot={false}
                  activeDot={{ r: 3, fill: '#22c55e', strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </GCard>
        </motion.div>

        {/* Expense breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.38 }}
          style={{ display: 'flex' }}
        >
          <GCard dark={dark} style={{ padding: '18px 18px 16px', flex: 1 }}>
            <div style={{ marginBottom: 14 }}>
              <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
                Expense Breakdown
              </h2>
              <p style={{ fontSize: 10.5, color: c.t4 }}>
                6mo · €{(totalCost / 1_000_000).toFixed(2)}M total
              </p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
              {EXPENSES.map((exp, i) => (
                <motion.div
                  key={exp.category}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.45 + i * 0.06 }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: 4,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span
                        style={{
                          width: 6,
                          height: 6,
                          borderRadius: 2,
                          background: EXPENSE_COLORS[i],
                          display: 'inline-block',
                          flexShrink: 0,
                        }}
                      />
                      <span style={{ fontSize: 11, color: c.t2 }}>{exp.category}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          color: c.t1,
                          fontVariantNumeric: 'tabular-nums',
                        }}
                      >
                        €{(exp.amount / 1000).toFixed(0)}k
                      </span>
                      <span style={{ fontSize: 9.5, color: c.t4 }}>{exp.pct}%</span>
                    </div>
                  </div>
                  <div
                    style={{
                      height: 4,
                      borderRadius: 99,
                      background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)',
                      overflow: 'hidden',
                    }}
                  >
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${exp.pct}%` }}
                      transition={{
                        delay: 0.55 + i * 0.07,
                        duration: 0.6,
                        ease: [0.32, 0.72, 0, 1],
                      }}
                      style={{
                        height: '100%',
                        borderRadius: 99,
                        background: EXPENSE_COLORS[i],
                      }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          </GCard>
        </motion.div>
      </div>

      {/* Cashflow bar chart */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.40, duration: 0.38 }}
      >
        <GCard dark={dark} style={{ padding: '18px 20px 14px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 14,
            }}
          >
            <div>
              <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>
                Net Cashflow
              </h2>
              <p style={{ fontSize: 10.5, color: c.t4 }}>
                Monthly net after all operating expenses
              </p>
            </div>
            <div
              style={{
                padding: '4px 10px',
                borderRadius: 7,
                background: 'rgba(8,145,178,0.12)',
                border: '1px solid rgba(8,145,178,0.22)',
                fontSize: 10.5,
                fontWeight: 700,
                color: '#0891b2',
              }}
            >
              €{(totalCashflow / 1000).toFixed(0)}k YTD
            </div>
          </div>
          <ResponsiveContainer width="100%" height={130}>
            <BarChart
              data={MONTHLY}
              margin={{ top: 0, right: 0, left: -24, bottom: 0 }}
              barSize={22}
            >
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 9.5, fill: tickColor }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 9.5, fill: tickColor }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => `€${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                contentStyle={{
                  background: tooltipBg,
                  border: `1px solid ${c.cardBord}`,
                  borderRadius: 10,
                  fontSize: 11.5,
                  color: c.t1,
                }}
                formatter={(v: number) => [`€${v.toLocaleString()}`, 'Cashflow']}
                cursor={{ fill: cursorFill }}
              />
              <Bar dataKey="cashflow" fill="#0891b2" radius={[4, 4, 0, 0]} fillOpacity={0.80} />
            </BarChart>
          </ResponsiveContainer>
        </GCard>
      </motion.div>

      {/* Negative margin alerts */}
      {ALERTS.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.44, duration: 0.38 }}
        >
          <GCard dark={dark} style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 8,
                  background: 'rgba(225,29,72,0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <TrendingDown style={{ width: 13, height: 13, color: '#e11d48' }} />
              </div>
              <span style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>
                Negative Margin Alerts
              </span>
              <Badge color="red">{ALERTS.length}</Badge>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {ALERTS.map((r) => (
                <div
                  key={r.vehicleId}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 13px',
                    borderRadius: 10,
                    background: 'rgba(225,29,72,0.06)',
                    border: '1px solid rgba(225,29,72,0.18)',
                  }}
                >
                  <div>
                    <p style={{ fontSize: 12, fontWeight: 600, color: c.t1 }}>{r.vehicleName}</p>
                    <p style={{ fontSize: 10, color: c.t4, marginTop: 2 }}>
                      Sold {r.soldAt ?? '—'} · Buy €{r.buyPrice.toLocaleString()} → Sell €
                      {r.sellPrice.toLocaleString()}
                    </p>
                  </div>
                  <Badge color="red">
                    −€{Math.abs(r.margin).toLocaleString()} ({r.marginPct.toFixed(1)}%)
                  </Badge>
                </div>
              ))}
            </div>
          </GCard>
        </motion.div>
      )}

      {/* Vehicle margin table */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.48, duration: 0.38 }}
      >
        <GCard dark={dark} style={{ padding: 0 }}>
          <div
            style={{
              padding: '14px 18px',
              borderBottom: `1px solid ${c.div}`,
              display: 'flex',
              alignItems: 'baseline',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1 }}>Vehicle Margin Detail</h2>
              <p style={{ fontSize: 10.5, color: c.t4, marginTop: 1 }}>
                Last 10 sold · sorted by margin
              </p>
            </div>
            <span style={{ fontSize: 10, color: c.t4 }}>10 records</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table
              style={{ width: '100%', minWidth: 540, fontSize: 12, borderCollapse: 'collapse' }}
            >
              <thead>
                <tr style={{ borderBottom: `1px solid ${c.div}` }}>
                  {['Vehicle', 'Buy price', 'Sell price', 'Margin', 'Rate', 'Sold'].map((h) => (
                    <th
                      key={h}
                      style={{
                        padding: '9px 16px',
                        textAlign: 'left',
                        fontSize: 9.5,
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.09em',
                        color: c.t4,
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TOP_VEHICLES.map((r, i) => (
                  <tr
                    key={r.vehicleId}
                    style={{
                      borderBottom:
                        i < TOP_VEHICLES.length - 1 ? `1px solid ${c.div}` : 'none',
                      background: r.margin < 0 ? 'rgba(225,29,72,0.04)' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '10px 16px', fontWeight: 600, color: c.t1 }}>
                      {r.vehicleName}
                    </td>
                    <td
                      style={{
                        padding: '10px 16px',
                        color: c.t3,
                        fontVariantNumeric: 'tabular-nums',
                      }}
                    >
                      €{r.buyPrice.toLocaleString()}
                    </td>
                    <td
                      style={{
                        padding: '10px 16px',
                        color: c.t3,
                        fontVariantNumeric: 'tabular-nums',
                      }}
                    >
                      €{r.sellPrice.toLocaleString()}
                    </td>
                    <td
                      style={{
                        padding: '10px 16px',
                        fontWeight: 700,
                        fontVariantNumeric: 'tabular-nums',
                        color: r.margin < 0 ? '#e11d48' : '#22c55e',
                      }}
                    >
                      {r.margin < 0 ? '−' : '+'}€{Math.abs(r.margin).toLocaleString()}
                    </td>
                    <td
                      style={{
                        padding: '10px 16px',
                        fontSize: 10.5,
                        color: r.marginPct < 0 ? '#e11d48' : c.t4,
                        fontVariantNumeric: 'tabular-nums',
                      }}
                    >
                      {r.marginPct.toFixed(1)}%
                    </td>
                    <td style={{ padding: '10px 16px', color: c.t4, fontSize: 10.5 }}>
                      {r.soldAt ?? '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GCard>
      </motion.div>
    </div>
  )
}
