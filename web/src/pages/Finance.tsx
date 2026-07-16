// Finance — Fleet P&L · Cashflow · Expenses · 6-month view (dealer's own data,
// no gating per 05-MONETIZATION-MAP.md).

import React, { useEffect } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { TrendingDown, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { Badge } from '../components'
import Card from '../components/Card'
import { useIsDark } from '../hooks/useIsDark'
import { ACCENT, GOOD, BAD } from '../lib/theme'
import type { FinanceRow } from '../types'

function AnimNum({ to, prefix = '', suffix = '', decimals = 0 }: { to: number; prefix?: string; suffix?: string; decimals?: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d = useTransform(sp, v => `${prefix}${decimals > 0 ? v.toFixed(decimals) : Math.round(v).toLocaleString()}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

function Spark({ values, color, height = 28 }: { values: number[]; color: string; height?: number }) {
  if (values.length < 2) return null
  const max = Math.max(...values), min = Math.min(...values), range = max - min || 1
  const W = 64, H = height
  const pts = values.map((v, i): [number, number] => [(i / (values.length - 1)) * W, H - ((v - min) / range) * (H - 4) + 2])
  const line = pts.map(([x, y]) => `${x},${y}`).join(' ')
  const last = pts[pts.length - 1]
  const area = `M${pts[0][0]},${H} ` + pts.map(([x, y]) => `L${x},${y}`).join(' ') + ` L${last[0]},${H} Z`
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: 'block' }}>
      <path d={area} fill={color} fillOpacity={0.12} />
      <polyline points={line} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
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

const EXPENSE_COLORS = [ACCENT, '#0891b2', GOOD, '#d97706', BAD, '#94a3b8']

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

const ALERTS = TOP_VEHICLES.filter(r => r.margin < 0)

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Finance() {
  const dark = useIsDark()

  const totalRevenue  = MONTHLY.reduce((s, m) => s + m.revenue,  0)
  const totalCost     = MONTHLY.reduce((s, m) => s + m.cost,     0)
  const totalMargin   = MONTHLY.reduce((s, m) => s + m.margin,   0)
  const totalCashflow = MONTHLY.reduce((s, m) => s + m.cashflow, 0)
  const avgMarginPct  = (totalMargin / totalRevenue) * 100

  const tickColor  = dark ? '#475569' : '#94a3b8'
  const gridColor  = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'
  const tooltipBg  = dark ? '#0e0e1a' : '#fff'
  const tooltipFg  = dark ? '#f1f5f9' : '#0f172a'
  const cursorFill = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'

  const kpis = [
    { label: 'Revenue (6mo)', value: totalRevenue / 1000, prefix: '€', suffix: 'k', sub: `Cost base €${(totalCost / 1_000_000).toFixed(2)}M`, trendUp: true, trendLabel: '+14% vs prior', spark: MONTHLY.map(m => m.revenue / 1000), accent: ACCENT },
    { label: 'Gross Margin', value: totalMargin / 1000, prefix: '€', suffix: 'k', sub: `Avg ${avgMarginPct.toFixed(1)}% rate`, trendUp: true, trendLabel: '+8% vs prior', spark: MONTHLY.map(m => m.margin / 1000), accent: GOOD },
    { label: 'Net Cashflow', value: totalCashflow / 1000, prefix: '€', suffix: 'k', sub: 'After all operating costs', trendUp: true, trendLabel: '+11% vs prior', spark: MONTHLY.map(m => m.cashflow / 1000), accent: '#0891b2' },
    { label: 'Margin Alerts', value: ALERTS.length, prefix: '', suffix: ' vehicles', sub: 'Sold below purchase cost', trendUp: false, trendLabel: ALERTS.length > 0 ? 'Action needed' : 'All clear', spark: [0, 1, 2, 1, 2, ALERTS.length], accent: ALERTS.length > 0 ? BAD : GOOD },
  ]

  return (
    <div className="mx-auto flex flex-col gap-5" style={{ padding: 'clamp(16px, 3vw, 24px)', maxWidth: 1200 }}>

      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className="flex items-end justify-between">
        <div>
          <h1 className="text-[22px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>Finance</h1>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>Fleet P&L · Cashflow · Expenses · 6-month view</p>
        </div>
        <div className="rounded-lg px-3 py-1.5 text-[11px] font-bold" style={{ background: `${ACCENT}1a`, border: `1px solid ${ACCENT}38`, color: ACCENT }}>Apr 2026</div>
      </motion.div>

      <div className="grid grid-cols-4 gap-3.5">
        {kpis.map(({ label, value, prefix, suffix, sub, trendUp, trendLabel, spark, accent }, i) => (
          <motion.div key={label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}>
            <Card hover className="!p-[18px_20px_14px]">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-[9.5px] font-bold uppercase tracking-[0.11em]" style={{ color: 'var(--text-secondary)' }}>{label}</span>
                <span className="inline-block h-1.5 w-1.5 rounded-full" style={{ background: accent, boxShadow: `0 0 6px ${accent}` }} />
              </div>
              <div className="mb-[3px] text-4xl font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>
                <AnimNum to={value} prefix={prefix} suffix={suffix} />
              </div>
              <div className="mb-3 text-[10px]" style={{ color: 'var(--text-muted)' }}>{sub}</div>
              <div className="flex items-center justify-between border-t pt-2.5" style={{ borderColor: 'var(--border-subtle)' }}>
                <div className="flex items-center gap-1">
                  {trendUp ? <ArrowUpRight style={{ width: 10, height: 10, color: GOOD }} /> : <ArrowDownRight style={{ width: 10, height: 10, color: BAD }} />}
                  <span className="text-[10px] font-semibold" style={{ color: trendUp ? GOOD : BAD }}>{trendLabel}</span>
                </div>
                <Spark values={spark} color={accent} height={22} />
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-3.5" style={{ gridTemplateColumns: '3fr 2fr' }}>
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.30, duration: 0.38 }}>
          <Card className="!p-[18px_20px_14px]">
            <div className="mb-3.5 flex items-center justify-between">
              <div>
                <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Revenue vs Cost — P&L</h2>
                <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>6-month trend</p>
              </div>
              <div className="flex items-center gap-3 text-[10px]" style={{ color: 'var(--text-muted)' }}>
                {([[ACCENT, 'Revenue'], [BAD, 'Cost'], [GOOD, 'Margin']] as [string, string][]).map(([col, lbl]) => (
                  <span key={lbl} className="flex items-center gap-1">
                    <span className="inline-block h-0.5 w-2.5 rounded-sm" style={{ background: col }} />
                    {lbl}
                  </span>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={MONTHLY} margin={{ top: 4, right: 0, left: -24, bottom: 0 }}>
                <defs>
                  <linearGradient id="fgRev" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={ACCENT} stopOpacity={0.22} /><stop offset="100%" stopColor={ACCENT} stopOpacity={0} /></linearGradient>
                  <linearGradient id="fgCost" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={BAD} stopOpacity={0.14} /><stop offset="100%" stopColor={BAD} stopOpacity={0} /></linearGradient>
                  <linearGradient id="fgMar" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={GOOD} stopOpacity={0.22} /><stop offset="100%" stopColor={GOOD} stopOpacity={0} /></linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
                <XAxis dataKey="month" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `€${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ background: tooltipBg, border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: tooltipFg, boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                  formatter={(v: number, name: string) => [`€${v.toLocaleString()}`, name === 'revenue' ? 'Revenue' : name === 'cost' ? 'Cost' : 'Margin']}
                  cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
                />
                <Area type="monotone" dataKey="revenue" stroke={ACCENT} strokeWidth={2} fill="url(#fgRev)" dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} />
                <Area type="monotone" dataKey="cost" stroke={BAD} strokeWidth={1.5} strokeDasharray="4 4" fill="url(#fgCost)" dot={false} activeDot={{ r: 3, fill: BAD, strokeWidth: 0 }} />
                <Area type="monotone" dataKey="margin" stroke={GOOD} strokeWidth={2} fill="url(#fgMar)" dot={false} activeDot={{ r: 3, fill: GOOD, strokeWidth: 0 }} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35, duration: 0.38 }} className="flex">
          <Card className="flex-1 !p-[18px_18px_16px]">
            <div className="mb-3.5">
              <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Expense Breakdown</h2>
              <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>6mo · €{(totalCost / 1_000_000).toFixed(2)}M total</p>
            </div>
            <div className="flex flex-col gap-2.5">
              {EXPENSES.map((exp, i) => (
                <motion.div key={exp.category} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.45 + i * 0.06 }}>
                  <div className="mb-1 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="inline-block h-1.5 w-1.5 shrink-0 rounded-sm" style={{ background: EXPENSE_COLORS[i] }} />
                      <span className="text-[11px]" style={{ color: 'var(--text-secondary)' }}>{exp.category}</span>
                    </div>
                    <div className="flex items-baseline gap-1.5">
                      <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>€{(exp.amount / 1000).toFixed(0)}k</span>
                      <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>{exp.pct}%</span>
                    </div>
                  </div>
                  <div className="h-1 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                    <motion.div initial={{ width: 0 }} animate={{ width: `${exp.pct}%` }} transition={{ delay: 0.55 + i * 0.07, duration: 0.6, ease: [0.32, 0.72, 0, 1] }} className="h-full rounded-full" style={{ background: EXPENSE_COLORS[i] }} />
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.40, duration: 0.38 }}>
        <Card className="!p-[18px_20px_14px]">
          <div className="mb-3.5 flex items-center justify-between">
            <div>
              <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Net Cashflow</h2>
              <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Monthly net after all operating expenses</p>
            </div>
            <div className="rounded-lg px-2.5 py-1 text-[10.5px] font-bold" style={{ background: 'rgba(8,145,178,0.12)', border: '1px solid rgba(8,145,178,0.22)', color: '#0891b2' }}>
              €{(totalCashflow / 1000).toFixed(0)}k YTD
            </div>
          </div>
          <ResponsiveContainer width="100%" height={130}>
            <BarChart data={MONTHLY} margin={{ top: 0, right: 0, left: -24, bottom: 0 }} barSize={22}>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `€${(v / 1000).toFixed(0)}k`} />
              <Tooltip contentStyle={{ background: tooltipBg, border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: tooltipFg }} formatter={(v: number) => [`€${v.toLocaleString()}`, 'Cashflow']} cursor={{ fill: cursorFill }} />
              <Bar dataKey="cashflow" fill="#0891b2" radius={[4, 4, 0, 0]} fillOpacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </motion.div>

      {ALERTS.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.44, duration: 0.38 }}>
          <Card className="!p-[16px_18px]">
            <div className="mb-3 flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg" style={{ background: `${BAD}1f` }}>
                <TrendingDown style={{ width: 13, height: 13, color: BAD }} />
              </div>
              <span className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Negative Margin Alerts</span>
              <Badge color="red">{ALERTS.length}</Badge>
            </div>
            <div className="flex flex-col gap-2">
              {ALERTS.map(r => (
                <div key={r.vehicleId} className="flex items-center justify-between rounded-[10px] p-[10px_13px]" style={{ background: `${BAD}0f`, border: `1px solid ${BAD}2e` }}>
                  <div>
                    <p className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>{r.vehicleName}</p>
                    <p className="mt-0.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>Sold {r.soldAt ?? '—'} · Buy €{r.buyPrice.toLocaleString()} → Sell €{r.sellPrice.toLocaleString()}</p>
                  </div>
                  <Badge color="red">−€{Math.abs(r.margin).toLocaleString()} ({r.marginPct.toFixed(1)}%)</Badge>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      )}

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.48, duration: 0.38 }}>
        <Card className="!p-0">
          <div className="flex items-baseline justify-between p-[14px_18px]" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
            <div>
              <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Vehicle Margin Detail</h2>
              <p className="mt-px text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Last 10 sold · sorted by margin</p>
            </div>
            <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>10 records</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-xs" style={{ minWidth: 540 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  {['Vehicle', 'Buy price', 'Sell price', 'Margin', 'Rate', 'Sold'].map(h => (
                    <th key={h} className="p-[9px_16px] text-left text-[9.5px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-muted)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TOP_VEHICLES.map((r, i) => (
                  <tr key={r.vehicleId} style={{ borderBottom: i < TOP_VEHICLES.length - 1 ? '1px solid var(--border-subtle)' : 'none', background: r.margin < 0 ? `${BAD}0a` : 'transparent' }}>
                    <td className="p-[10px_16px] font-semibold" style={{ color: 'var(--text-primary)' }}>{r.vehicleName}</td>
                    <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>€{r.buyPrice.toLocaleString()}</td>
                    <td className="p-[10px_16px] tabular-nums" style={{ color: 'var(--text-secondary)' }}>€{r.sellPrice.toLocaleString()}</td>
                    <td className="p-[10px_16px] font-bold tabular-nums" style={{ color: r.margin < 0 ? BAD : GOOD }}>{r.margin < 0 ? '−' : '+'}€{Math.abs(r.margin).toLocaleString()}</td>
                    <td className="p-[10px_16px] text-[10.5px] tabular-nums" style={{ color: r.marginPct < 0 ? BAD : 'var(--text-muted)' }}>{r.marginPct.toFixed(1)}%</td>
                    <td className="p-[10px_16px] text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{r.soldAt ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
