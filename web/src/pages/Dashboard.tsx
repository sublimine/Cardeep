import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion'
import React, { useEffect, useRef, useState } from 'react'
import { ArrowUpRight, ArrowDownRight, AlertTriangle, Clock, ChevronRight } from 'lucide-react'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts'
import { PageSkeleton } from '../components/LoadingSpinner'
import Card from '../components/Card'
import PremiumGate from '../components/PremiumGate'
import EngineFreshnessStamp from '../components/EngineFreshnessStamp'
import EmptyState from '../components/EmptyState'
import ProgressMetricCard, { type SeriesPoint } from '../components/progress-metric-card'
import { useApi } from '../hooks/useApi'
import { useIsDark } from '../hooks/useIsDark'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../auth/AuthContext'
import type { KpiData } from '../types'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'
import { cn } from '../lib/cn'

// ── Mock data ─────────────────────────────────────────────────────────────────

const MOCK_KPI: KpiData = {
  stockCount: 270,
  activeDeals: 55,
  monthMargin: 87400,
  pendingAlerts: 3,
  marginHistory: [
    { month: 'Nov', margin: 61000, revenue: 310000, cost: 249000 },
    { month: 'Dec', margin: 72000, revenue: 360000, cost: 288000 },
    { month: 'Jan', margin: 54000, revenue: 270000, cost: 216000 },
    { month: 'Feb', margin: 79000, revenue: 395000, cost: 316000 },
    { month: 'Mar', margin: 95000, revenue: 475000, cost: 380000 },
    { month: 'Apr', margin: 87400, revenue: 437000, cost: 349600 },
  ],
  recentActivities: [
    { id: '1', tenantId: 't', dealId: 'd1', type: 'inquiry',  body: 'New inquiry — BMW 320d, Maria S.',      createdAt: '2026-04-18T10:15:00Z' },
    { id: '2', tenantId: 't', dealId: 'd2', type: 'call',     body: 'Test drive scheduled — John D.',        createdAt: '2026-04-18T09:42:00Z' },
    { id: '3', tenantId: 't', dealId: 'd3', type: 'reply',    body: 'Offer sent — Audi A4 €26,500',         createdAt: '2026-04-18T09:10:00Z' },
    { id: '4', tenantId: 't', dealId: 'd4', type: 'note',     body: 'Client wants black interior',           createdAt: '2026-04-17T16:55:00Z' },
    { id: '5', tenantId: 't', dealId: 'd5', type: 'reminder', body: 'Follow up — Peter K., C220d',          createdAt: '2026-04-17T14:30:00Z' },
  ],
}

const DEALER = {
  avgDaysInStock: 38,
  stockValue: 2_140_000,
  soldThisMonth: 23,
  targetSoldMonth: 30,
  dealStages: [
    { label: 'New',         count: 15, color: ACCENT },
    { label: 'Contacted',   count: 12, color: ACCENT },
    { label: 'Offer Sent',  count: 10, color: WARN },
    { label: 'Negotiation', count: 10, color: WARN },
    { label: 'Closed',      count:  8, color: GOOD },
  ],
  staleStock: [
    { id: 's1', make: 'BMW',       model: '320d xDrive',  year: 2021, days: 72, price: 24_900 },
    { id: 's2', make: 'Audi',      model: 'A4 2.0 TDI',   year: 2020, days: 68, price: 22_500 },
    { id: 's3', make: 'Volkswagen',model: 'Golf 2.0 TDI', year: 2019, days: 61, price: 16_800 },
  ],
  followUps: [
    { id: 'f1', name: 'Maria S.',  vehicle: 'BMW 320d',   time: '11:00', type: 'call' },
    { id: 'f2', name: 'John D.',   vehicle: 'VW Tiguan',  time: '14:30', type: 'drive' },
    { id: 'f3', name: 'Peter K.', vehicle: 'Mercedes C220d', time: '16:00', type: 'offer' },
  ],
}

const TOP_DEALS = [
  { id: 'td1', model: 'Peugeot 3008 1.5 BlueHDi', location: 'Madrid',   price: 21_900, marketPrice: 24_100, score: 94, daysListed:  3, delta: -800   },
  { id: 'td2', model: 'VW Golf 1.5 TSI',           location: 'Toledo',   price: 17_300, marketPrice: 18_900, score: 88, daysListed:  6, delta: -500   },
  { id: 'td3', model: 'Audi A4 Avant 2.0 TDI',     location: 'Valencia', price: 26_300, marketPrice: 28_750, score: 86, daysListed: 18, delta: -1_100 },
]

const MARKET_POS = {
  priceVsMkt: -3.8, // % below market median — good
  myDays:     47,
  mktDays:    39,
}

const TOP_MODELS = [
  { model: 'VW Golf',      sold: 7, revenue: 121_000 },
  { model: 'BMW 320d',     sold: 5, revenue: 142_500 },
  { model: 'Audi A4',      sold: 4, revenue: 114_000 },
  { model: 'Seat León',    sold: 4, revenue:  76_000 },
  { model: 'Peugeot 3008', sold: 3, revenue:  69_000 },
]

const MAX_MODELS_SOLD = Math.max(...TOP_MODELS.map(m => m.sold))

// ── Helpers ───────────────────────────────────────────────────────────────────

function AnimNum({ to, prefix = '', suffix = '', decimals = 0 }: { to: number; prefix?: string; suffix?: string; decimals?: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(sp, v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to])
  return <motion.span>{d}</motion.span>
}

function timeAgo(iso: string) {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  return h < 24 ? `${h}h ago` : `${Math.floor(h / 24)}d ago`
}

function renderBold(text: string): React.ReactNode {
  return text.split(/\*\*(.*?)\*\*/g).map((p, i) =>
    i % 2 === 1 ? <strong key={i} className="font-bold" style={{ color: 'var(--text-primary)' }}>{p}</strong> : <span key={i}>{p}</span>
  )
}

function scoreColor(score: number): string {
  if (score >= 85) return ACCENT
  if (score >= 70) return WARN
  return '#94a3b8'
}

// ── Panel nav link (chevron-only or text+chevron "see more" affordance) ───────
// Inline color is set via style (matches this file's convention), so hover feedback
// is driven by framer-motion — its imperative style write on hover overrides the
// static inline value, same mechanism Card.tsx already relies on for its own hover.

interface PanelLinkProps {
  onClick: () => void
  ariaLabel?: string
  children: React.ReactNode
  className?: string
  /** Brand-tinted link (e.g. "ver todo") keeps its accent color on hover; the
   * default muted link brightens to primary text on hover. */
  accent?: boolean
}

function PanelLink({ onClick, ariaLabel, children, className, accent }: PanelLinkProps) {
  const base = accent ? ACCENT : 'var(--text-muted)'
  const hover = accent ? ACCENT : 'var(--text-primary)'
  return (
    <motion.button
      onClick={onClick}
      aria-label={ariaLabel}
      whileHover={{ color: hover, backgroundColor: 'var(--glass-medium)' }}
      whileTap={{ scale: 0.94 }}
      transition={{ type: 'spring', stiffness: 460, damping: 30 }}
      className={cn('rounded-[7px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50', className)}
      style={{ color: base }}
    >
      {children}
    </motion.button>
  )
}

// ── Metric card (KPI row) ──────────────────────────────────────────────────────
// v3.1: sparkline+footer MetricCard replaced by the shared ProgressMetricCard —
// same numbers, a real interactive background chart (scrub/hover) instead of a
// static 64x28 sparkline. `spark: number[]` values have no per-point real dates
// (arbitrary 6-step mock progressions, per kpiCards below), so period labels
// stay relative ("P-5" ... "Now") rather than inventing specific calendar dates.

function sparkToSeries(values: number[]): SeriesPoint[] {
  return values.map((value, i) => ({
    value,
    date: i === values.length - 1 ? 'Now' : `P-${values.length - 1 - i}`,
  }))
}

// ── Margin chart ──────────────────────────────────────────────────────────────

function MarginChart({ data, dark }: { data: KpiData['marginHistory']; dark: boolean }) {
  const [tab, setTab] = useState<'area' | 'bar'>('area')
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 flex items-center justify-between shrink-0">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Gross Margin</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>6-month trend</p>
          </div>
          <div className="flex gap-[3px]" role="tablist" aria-label="Tipo de gráfico">
            {(['area', 'bar'] as const).map(t => (
              <motion.button
                key={t}
                onClick={() => setTab(t)}
                role="tab"
                aria-selected={tab === t}
                whileHover={{ backgroundColor: tab === t ? `${ACCENT}22` : 'var(--glass-medium)' }}
                whileTap={{ scale: 0.94 }}
                transition={{ type: 'spring', stiffness: 460, damping: 30 }}
                className="rounded-[7px] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.04em] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
                style={{
                  background: tab === t ? `${ACCENT}22` : 'transparent',
                  border: `1px solid ${tab === t ? `${ACCENT}48` : 'transparent'}`,
                  color: tab === t ? ACCENT : 'var(--text-muted)',
                }}
              >{t}</motion.button>
            ))}
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            {tab === 'area' ? (
              <AreaChart data={data} margin={{ top: 4, right: 0, left: -24, bottom: 0 }}>
                <defs>
                  <linearGradient id="gm" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor={ACCENT} stopOpacity={0.28} />
                    <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
                <XAxis dataKey="month" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(v/1000).toFixed(0)}k`} />
                <ChartTooltip
                  contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                  formatter={(v: number) => [`€${v.toLocaleString()}`, 'Margin']}
                  cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
                />
                <Area type="monotone" dataKey="margin" stroke={ACCENT} strokeWidth={2} fill="url(#gm)" dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} />
              </AreaChart>
            ) : (
              <BarChart data={data} margin={{ top: 4, right: 0, left: -24, bottom: 0 }} barSize={26}>
                <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(v/1000).toFixed(0)}k`} />
                <ChartTooltip
                  contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                  formatter={(v: number) => [`€${v.toLocaleString()}`, 'Margin']}
                  cursor={{ fill: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }}
                />
                <Bar dataKey="margin" fill={ACCENT} radius={[4, 4, 0, 0]} />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  )
}

// ── Pipeline stages ───────────────────────────────────────────────────────────

function PipelinePanel() {
  const total = DEALER.dealStages.reduce((s, d) => s + d.count, 0)

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_16px]">
        <div className="mb-4 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Pipeline</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{total} deals total</p>
        </div>

        <div className="flex flex-1 flex-col gap-2.5">
          {DEALER.dealStages.map((stage, i) => {
            const pct = (stage.count / total) * 100
            return (
              <motion.div key={stage.label} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 + i * 0.07 }}>
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-[11px] font-medium" style={{ color: 'var(--text-secondary)' }}>{stage.label}</span>
                  <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{stage.count}</span>
                </div>
                <div className="h-1 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ delay: 0.3 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                    className="h-full rounded-full"
                    style={{ background: stage.color, boxShadow: `0 0 6px ${stage.color}66` }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>

        <div className="mt-3.5 rounded-[9px] px-2.5 py-2" style={{ background: `${GOOD}18`, border: `1px solid ${GOOD}30` }}>
          <span className="text-[10.5px] font-semibold" style={{ color: GOOD }}>8 deals closing this week ↗</span>
        </div>
      </div>
    </Card>
  )
}

// ── Stale stock panel ─────────────────────────────────────────────────────────

function StalePanel({ onNavigate }: { onNavigate: () => void }) {
  function staleColor(days: number) {
    if (days >= 70) return BAD
    if (days >= 60) return WARN
    return '#eab308'
  }

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <div>
            <div className="mb-0.5 flex items-center gap-1.5">
              <AlertTriangle style={{ width: 12, height: 12, color: BAD }} />
              <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Stale Stock</h2>
            </div>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Vehicles over 60 days</p>
          </div>
          <PanelLink onClick={onNavigate} ariaLabel="View all stock" className="p-1">
            <ChevronRight style={{ width: 14, height: 14 }} />
          </PanelLink>
        </div>

        <div className="flex flex-1 flex-col gap-2">
          {DEALER.staleStock.map((v, i) => (
            <motion.div
              key={v.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.08 }}
              className="flex items-center gap-2.5 rounded-[10px] p-[9px_10px]"
              style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderLeft: `2px solid ${staleColor(v.days)}` }}
            >
              <div className="min-w-0 flex-1">
                <div className="truncate text-[11.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{v.make} {v.model}</div>
                <div className="mt-px text-[10px] tabular-nums" style={{ color: 'var(--text-muted)' }}>{v.year} · €{v.price.toLocaleString()}</div>
              </div>
              <div className="flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5" style={{ background: `${staleColor(v.days)}14`, border: `1px solid ${staleColor(v.days)}30` }}>
                <Clock style={{ width: 9, height: 9, color: staleColor(v.days) }} />
                <span className="text-[10px] font-bold" style={{ color: staleColor(v.days) }}>{v.days}d</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Follow-ups today ──────────────────────────────────────────────────────────

const TYPE_COLOR: Record<string, string> = {
  inquiry: ACCENT, call: GOOD, reply: ACCENT, note: WARN, reminder: WARN,
  drive: '#0891b2', offer: ACCENT,
}

function FollowUpsPanel({ onNavigate }: { onNavigate: () => void }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Today's Follow-ups</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{DEALER.followUps.length} scheduled</p>
          </div>
          <PanelLink onClick={onNavigate} ariaLabel="View all follow-ups" className="p-1">
            <ChevronRight style={{ width: 14, height: 14 }} />
          </PanelLink>
        </div>

        <div className="flex flex-1 flex-col gap-2">
          {DEALER.followUps.map((f, i) => (
            <motion.div
              key={f.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.08 }}
              className="flex items-center gap-2.5 rounded-[10px] p-[9px_10px]"
              style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
            >
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-[8px]" style={{ background: `${TYPE_COLOR[f.type]}18`, border: `1px solid ${TYPE_COLOR[f.type]}28` }}>
                <span className="text-xs">{f.type === 'call' ? '📞' : f.type === 'drive' ? '🚗' : '📋'}</span>
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-[11.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{f.name}</div>
                <div className="mt-px truncate text-[10px]" style={{ color: 'var(--text-muted)' }}>{f.vehicle}</div>
              </div>
              <div className="shrink-0 text-[10.5px] font-semibold tabular-nums" style={{ color: 'var(--text-secondary)' }}>{f.time}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Activity feed ─────────────────────────────────────────────────────────────

function ActivityFeed({ activities }: { activities: KpiData['recentActivities'] }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_18px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Recent Activity</h2>
          <span className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{activities.length} events</span>
        </div>

        {activities.length === 0 ? (
          <EmptyState
            className="flex-1 py-8"
            title="No recent activity"
            message="Events from your deals will show up here as they happen."
          />
        ) : (
          <div className="flex flex-1 flex-col gap-px overflow-y-auto">
            {activities.map((a, i) => (
              <motion.div
                key={a.id}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 + i * 0.06, duration: 0.32 }}
                className="flex items-center gap-2.5 py-2"
                style={{ borderBottom: i < activities.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}
              >
                <div className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: TYPE_COLOR[a.type] ?? ACCENT }} />
                <span className="w-14 shrink-0 text-[9.5px] font-bold uppercase tracking-[0.07em]" style={{ color: TYPE_COLOR[a.type] ?? ACCENT }}>{a.type}</span>
                <span className="flex-1 truncate text-[11.5px]" style={{ color: 'var(--text-secondary)' }}>{a.body}</span>
                <span className="shrink-0 text-[10px] tabular-nums" style={{ color: 'var(--text-muted)' }}>{timeAgo(a.createdAt)}</span>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}

// ── Compact AI chat ───────────────────────────────────────────────────────────

interface ChatMsg { id: string; role: 'user' | 'bot'; text: string }

function botReply(text: string, kpi: KpiData, name: string): string {
  const q = text.toLowerCase()
  if (q.match(/stock|vehicles|inventory/)) return `You have **${kpi.stockCount} vehicles** in stock — total value **€${(DEALER.stockValue / 1_000_000).toFixed(2)}M**. ${kpi.stockCount > 200 ? '✅ Healthy inventory.' : '⚠️ Consider sourcing more.'}`
  if (q.match(/deal|pipeline|active/))    return `**${kpi.activeDeals} deals** in the pipeline. **8 closing this week** — prioritize Negotiation stage. 💼`
  if (q.match(/stale|old|slow|days/))     return `**3 vehicles over 60 days** in stock. BMW 320d at 72 days is the most critical — consider a **price reduction of 5-8%**. ⏱️`
  if (q.match(/alert|warning/))           return `**${kpi.pendingAlerts} alerts** pending. Main issue: 3 stale vehicles and 1 expired listing. ⚠️`
  if (q.match(/margin|profit|revenue/))   return `Gross margin this month: **€${(kpi.monthMargin / 1000).toFixed(1)}k** (+8% vs last month). On track to hit target. 📈`
  if (q.match(/hi|hello|hey/))            return `Hey ${name}! Ask me about stock levels, pipeline, stale vehicles, or margin performance.`
  return `I can help with stock, deals, stale vehicles, alerts, and margins. What do you need, ${name}?`
}

function proactiveInsight(kpi: KpiData): string {
  if (kpi.pendingAlerts > 0) return `⚠️ **${kpi.pendingAlerts} alerts** — 3 vehicles over 60 days. BMW 320d at 72d needs repricing.`
  if (kpi.stockCount < 200) return `📦 Stock at **${kpi.stockCount}** vehicles. Below healthy threshold — consider sourcing.`
  return `✅ All metrics healthy. Gross margin +8% this month. Keep it up!`
}

function ChatCompact({ kpi, username }: { kpi: KpiData; username: string }) {
  const [msgs, setMsgs] = useState<ChatMsg[]>([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  function send(text: string) {
    const t = text.trim()
    if (!t || typing) return
    setMsgs(m => [...m, { id: Date.now().toString(), role: 'user', text: t }])
    setInput('')
    setTyping(true)
    setTimeout(() => {
      setTyping(false)
      setMsgs(m => [...m, { id: (Date.now() + 1).toString(), role: 'bot', text: botReply(t, kpi, username.split(' ')[0]) }])
    }, 600 + Math.random() * 300)
  }

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [msgs, typing])

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col">
        <div className="flex shrink-0 items-center gap-2 p-[14px_14px_10px]" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
          <div className="flex h-6.5 w-6.5 shrink-0 items-center justify-center rounded-[8px]" style={{ background: `linear-gradient(135deg, ${ACCENT}, #2563eb)`, boxShadow: `0 0 10px ${ACCENT}4d` }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
          </div>
          <div className="flex-1 text-xs font-bold" style={{ color: 'var(--text-primary)' }}>CARDEEP AI</div>
          <div className="flex items-center gap-1">
            <motion.span className="inline-block h-[5px] w-[5px] rounded-full" style={{ background: GOOD }} animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 2, repeat: Infinity }} />
            <span className="text-[9.5px] font-semibold" style={{ color: GOOD }}>Online</span>
          </div>
        </div>

        {msgs.length === 0 && (
          <div className="shrink-0 p-[10px_12px]">
            <div className="rounded-[10px] p-[9px_11px] text-[11.5px] leading-normal" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>
              {renderBold(proactiveInsight(kpi))}
            </div>
          </div>
        )}

        <div ref={scrollRef} className="flex min-h-0 flex-1 flex-col gap-1.5 overflow-y-auto p-[8px_12px]">
          <AnimatePresence initial={false}>
            {msgs.map(msg => (
              <motion.div key={msg.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className="max-w-[88%] rounded-xl p-[7px_10px] text-[11.5px] leading-normal"
                  style={{
                    borderRadius: msg.role === 'user' ? '12px 12px 3px 12px' : '12px 12px 12px 3px',
                    background: msg.role === 'user' ? `linear-gradient(135deg, ${ACCENT}, #2563eb)` : 'var(--bg-surface)',
                    color: msg.role === 'user' ? '#fff' : 'var(--text-primary)',
                    boxShadow: msg.role === 'user' ? `0 3px 10px ${ACCENT}48` : 'none',
                  }}
                >
                  {msg.role === 'bot' ? renderBold(msg.text) : msg.text}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          <AnimatePresence>
            {typing && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex">
                <div className="flex items-center gap-[3px] rounded-[12px_12px_12px_3px] p-[8px_12px]" style={{ background: 'var(--bg-surface)' }}>
                  {[0,1,2].map(i => (
                    <motion.span key={i} className="block h-1 w-1 rounded-full" style={{ background: 'var(--text-secondary)' }} animate={{ y: [0, -4, 0] }} transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.13 }} />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex shrink-0 items-center gap-1.5 p-[8px_10px]" style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) } }}
            placeholder="Ask about stock, deals…"
            className="flex-1 rounded-[9px] p-[6px_10px] text-[11.5px] outline-none transition-shadow focus:ring-2 focus:ring-accent-blue/40"
            style={{ background: 'var(--bg-input)', border: '1px solid var(--border-default)', color: 'var(--text-primary)' }}
          />
          <motion.button
            onClick={() => send(input)}
            disabled={!input.trim() || typing}
            aria-label="Send message"
            whileHover={{ scale: !input.trim() || typing ? 1 : 1.06 }}
            whileTap={{ scale: !input.trim() || typing ? 1 : 0.92 }}
            transition={{ type: 'spring', stiffness: 460, damping: 30 }}
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-[8px] border-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:ring-offset-1"
            style={{ background: `linear-gradient(135deg, ${ACCENT}, #2563eb)`, opacity: !input.trim() || typing ? 0.35 : 1 }}
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </motion.button>
        </div>
      </div>
    </Card>
  )
}

// ── Oportunidades (top chollos · deal-score) — Capa 2, gated ──────────────────

function OportunidadesPanel({ onNavigate, plan }: { onNavigate: () => void; plan: import('../types').Plan }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Oportunidades</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>{TOP_DEALS.length} chollos detectados hoy · deal-score en vivo</p>
          </div>
          <PanelLink onClick={onNavigate} accent className="flex items-center gap-1 px-2 py-1 text-[10.5px] font-semibold">
            ver todo <ChevronRight style={{ width: 11, height: 11 }} />
          </PanelLink>
        </div>

        <PremiumGate feature="sourcing-ranking" userPlan={plan} what="Ranking completo de chollos, filtros por margen/zona/segmento">
          <div className="grid flex-1 grid-cols-3 gap-2.5">
            {TOP_DEALS.map((deal, i) => {
              const sc = scoreColor(deal.score)
              const pctUnder = Math.round(((deal.marketPrice - deal.price) / deal.marketPrice) * 100)
              return (
                <motion.div
                  key={deal.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.18 + i * 0.08, duration: 0.34 }}
                  className="flex flex-col gap-2 rounded-xl p-[13px_13px_11px]"
                  style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderLeft: `2px solid ${sc}` }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[9px]" style={{ background: `${sc}16`, border: `1px solid ${sc}28` }}>
                      <span className="text-[13px] font-extrabold tabular-nums tracking-[-0.02em]" style={{ color: sc }}>{deal.score}</span>
                    </div>
                    <span className="text-[10px] font-bold" style={{ color: sc }}>−{pctUnder}% mkt</span>
                  </div>
                  <div>
                    <div className="truncate text-[11.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{deal.model}</div>
                    <div className="mt-0.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>
                      {deal.location} · {deal.daysListed}d{deal.delta < 0 ? ` · −€${Math.abs(deal.delta).toLocaleString()}` : ''}
                    </div>
                  </div>
                  <div className="text-sm font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>€{deal.price.toLocaleString()}</div>
                </motion.div>
              )
            })}
          </div>
        </PremiumGate>
      </div>
    </Card>
  )
}

// ── Posición de mercado · mini (Capa 1 — la métrica agregada YA es el teaser) ──

function MarketPositionMini({ onNavigate }: { onNavigate: () => void }) {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_16px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Posición mercado</h2>
          <PanelLink onClick={onNavigate} ariaLabel="Ver inteligencia de mercado completa" className="p-1">
            <ChevronRight style={{ width: 13, height: 13 }} />
          </PanelLink>
        </div>

        <div className="flex flex-1 flex-col gap-2.5">
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.22, duration: 0.34 }}
            className="rounded-[11px] p-3"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
          >
            <div className="mb-[7px] text-[9.5px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-muted)' }}>Precio vs mercado</div>
            <div className="mb-[3px] text-[28px] font-extrabold leading-none tracking-[-0.03em] tabular-nums" style={{ color: GOOD }}>{MARKET_POS.priceVsMkt.toFixed(1)}%</div>
            <div className="mb-[7px] text-[10px]" style={{ color: 'var(--text-muted)' }}>bajo la mediana UE</div>
            <div className="flex items-center gap-[3px]">
              <ArrowUpRight style={{ width: 10, height: 10, color: GOOD }} />
              <span className="text-[10px] font-semibold" style={{ color: GOOD }}>posición competitiva</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.30, duration: 0.34 }}
            className="flex-1 rounded-[11px] p-3"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
          >
            <div className="mb-[7px] text-[9.5px] font-bold uppercase tracking-[0.09em]" style={{ color: 'var(--text-muted)' }}>Días stock vs mkt</div>
            <div className="mb-2 flex items-baseline gap-[5px]">
              <span className="text-2xl font-extrabold leading-none tracking-[-0.02em] tabular-nums" style={{ color: BAD }}>{MARKET_POS.myDays}d</span>
              <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>tu dealer</span>
            </div>
            <div className="mb-1 flex justify-between text-[9.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
              <span>Tu dealer</span><span>Mediana {MARKET_POS.mktDays}d</span>
            </div>
            <div className="relative h-1.5 overflow-visible rounded-full" style={{ background: 'var(--border-subtle)' }}>
              <div className="absolute top-[-3px] h-3 w-0.5 rounded-sm" style={{ left: `${(MARKET_POS.mktDays / 70) * 100}%`, background: GOOD }} />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(MARKET_POS.myDays / 70) * 100}%` }}
                transition={{ duration: 0.7, delay: 0.45, ease: [0.32, 0.72, 0, 1] }}
                className="h-full rounded-full"
                style={{ background: BAD, opacity: 0.85 }}
              />
            </div>
            <div className="mt-1.5 flex items-center gap-[3px]">
              <ArrowDownRight style={{ width: 10, height: 10, color: BAD }} />
              <span className="text-[10px] font-semibold tabular-nums" style={{ color: BAD }}>+{MARKET_POS.myDays - MARKET_POS.mktDays}d sobre mediana</span>
            </div>
          </motion.div>
        </div>
      </div>
    </Card>
  )
}

// ── Revenue & Coste chart ─────────────────────────────────────────────────────

function RevenueChart({ data, dark, onNavigate }: { data: KpiData['marginHistory']; dark: boolean; onNavigate: () => void }) {
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Revenue & Coste</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>6 meses · ingresos vs coste</p>
          </div>
          <div className="flex items-center gap-3.5">
            <div className="flex items-center gap-2.5 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
              <span className="flex items-center gap-1"><span className="inline-block h-0.5 w-3 rounded-sm" style={{ background: ACCENT }} />Revenue</span>
              <span className="flex items-center gap-1"><span className="inline-block w-3 border-t-2 border-dashed" style={{ borderColor: `${BAD}a6` }} />Coste</span>
            </div>
            <PanelLink onClick={onNavigate} className="flex items-center gap-0.5 px-1.5 py-1 text-[10.5px]">
              Finance <ChevronRight style={{ width: 11, height: 11 }} />
            </PanelLink>
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 0, left: -24, bottom: 0 }}>
              <defs>
                <linearGradient id="gr-rev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={ACCENT} stopOpacity={0.22} />
                  <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gr-cost" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={BAD} stopOpacity={0.14} />
                  <stop offset="100%" stopColor={BAD} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} />
              <XAxis dataKey="month" tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={v => `€${(v / 1000).toFixed(0)}k`} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11.5, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number, name: string) => [`€${v.toLocaleString()}`, name === 'revenue' ? 'Revenue' : 'Coste']}
                cursor={{ stroke: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}
              />
              <Area type="monotone" dataKey="revenue" stroke={ACCENT} strokeWidth={2} fill="url(#gr-rev)" dot={false} activeDot={{ r: 3, fill: ACCENT, strokeWidth: 0 }} />
              <Area type="monotone" dataKey="cost" stroke={BAD} strokeWidth={1.5} strokeDasharray="4 4" fill="url(#gr-cost)" dot={false} activeDot={{ r: 3, fill: BAD, strokeWidth: 0 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  )
}

// ── Top modelos vendidos ───────────────────────────────────────────────────────

function TopModelsPanel({ onNavigate }: { onNavigate: () => void }) {
  const totalSold = TOP_MODELS.reduce((s, m) => s + m.sold, 0)

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Top modelos vendidos</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>este mes · {totalSold} unidades</p>
          </div>
          <PanelLink onClick={onNavigate} ariaLabel="Ver todos los modelos vendidos" className="p-1">
            <ChevronRight style={{ width: 13, height: 13 }} />
          </PanelLink>
        </div>

        <div className="flex flex-1 flex-col gap-2.5">
          {TOP_MODELS.map((item, i) => {
            const barW = Math.round((item.sold / MAX_MODELS_SOLD) * 100)
            return (
              <motion.div key={item.model} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22 + i * 0.07 }}>
                <div className="mb-[5px] flex items-baseline justify-between">
                  <span className="text-[11.5px] font-medium" style={{ color: 'var(--text-secondary)' }}>{item.model}</span>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-[11px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{item.sold} ud.</span>
                    <span className="text-[10px] tabular-nums" style={{ color: 'var(--text-muted)' }}>€{(item.revenue / 1000).toFixed(0)}k</span>
                  </div>
                </div>
                <div className="h-[5px] overflow-hidden rounded-[5px]" style={{ background: 'var(--border-subtle)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barW}%` }}
                    transition={{ delay: 0.36 + i * 0.08, duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
                    className="h-full rounded-[5px]"
                    style={{ background: `linear-gradient(90deg, ${ACCENT}, #60a5fa)`, boxShadow: `0 0 6px ${ACCENT}48` }}
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

// ── Dashboard ─────────────────────────────────────────────────────────────────

export default function Dashboard() {
  const dark = useIsDark()
  const { data, loading } = useApi<KpiData>('/kpi')
  const { user } = useAuthContext()
  const navigate = useNavigate()
  const kpi = data ? { ...MOCK_KPI, ...data } : MOCK_KPI

  if (loading && !data) return <PageSkeleton />

  const username = user?.name ?? 'User'
  const plan = user?.plan ?? 'starter'

  // Real month-over-month delta from the SAME marginHistory array the chart below
  // renders — the previous hardcoded "+8% vs last month" claimed an increase while
  // the mock series actually shows a decrease, contradicting the chart right under it.
  const marginSeries = kpi.marginHistory
  const lastMargin = marginSeries.at(-1)?.margin ?? kpi.monthMargin
  const prevMargin = marginSeries.at(-2)?.margin ?? lastMargin
  const marginDeltaPct = prevMargin !== 0 ? ((lastMargin - prevMargin) / prevMargin) * 100 : 0
  const marginTrend: 'up' | 'down' | 'flat' = marginDeltaPct > 0.5 ? 'up' : marginDeltaPct < -0.5 ? 'down' : 'flat'
  const marginTrendLabel = `${marginDeltaPct >= 0 ? '+' : ''}${marginDeltaPct.toFixed(0)}% vs last month`

  const kpiCards: (React.ComponentProps<typeof ProgressMetricCard> & { key: string })[] = [
    {
      key: 'In Stock',
      title: 'In Stock',
      total: `${kpi.stockCount}`,
      sub: `€${(DEALER.stockValue / 1_000_000).toFixed(2)}M capital`,
      trend: 'up',
      delta: '+12',
      deltaLabel: 'this month',
      accent: 'emerald',
      data: sparkToSeries([220, 232, 245, 258, 264, kpi.stockCount]),
    },
    {
      key: 'Active Deals',
      title: 'Active Deals',
      total: `${kpi.activeDeals}`,
      sub: '8 closing this week',
      trend: 'flat',
      delta: 'Stable',
      deltaLabel: '',
      accent: 'neutral',
      data: sparkToSeries([42, 48, 51, 53, 54, kpi.activeDeals]),
    },
    {
      key: 'Month Margin',
      title: 'Month Margin',
      total: `€${(kpi.monthMargin / 1000).toFixed(1)}k`,
      sub: new Date().toLocaleDateString('en-GB', { month: 'long', year: 'numeric' }),
      trend: marginTrend,
      delta: marginTrendLabel,
      deltaLabel: '',
      accent: marginTrend === 'up' ? 'emerald' : marginTrend === 'down' ? 'rose' : 'neutral',
      data: sparkToSeries(kpi.marginHistory.map(m => m.margin / 1000)),
    },
    {
      key: 'Avg Days In Stock',
      title: 'Avg Days In Stock',
      total: `${DEALER.avgDaysInStock}d`,
      sub: 'target < 45d',
      trend: 'down',
      delta: 'Healthy',
      deltaLabel: '',
      accent: 'emerald',
      data: sparkToSeries([52, 48, 44, 41, 39, DEALER.avgDaysInStock]),
    },
  ]

  return (
    <div className="mx-auto p-[24px_24px_40px]" style={{ maxWidth: 1360 }}>

      {/* F5 (00-marketplace-engine.md §6a): real freshness/coverage stamp — no-op when the
          user has no claimed dealer profile or the read fails, so the mock sections below are
          never blocked by it. */}
      <EngineFreshnessStamp />

      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        className="mb-[22px] flex items-end justify-between"
      >
        <div>
          <h1 className="mb-1 text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>Overview</h1>
          <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
            {new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="text-right">
            <div className="mb-1 text-[10.5px] font-semibold uppercase tracking-[0.06em]" style={{ color: 'var(--text-muted)' }}>Units Sold</div>
            <div className="text-xs font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{DEALER.soldThisMonth} / {DEALER.targetSoldMonth}</div>
          </div>
          <div className="h-1.5 w-20 overflow-hidden rounded-full" style={{ background: 'var(--border-subtle)' }}>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(DEALER.soldThisMonth / DEALER.targetSoldMonth) * 100}%` }}
              transition={{ duration: 0.8, delay: 0.3, ease: [0.32, 0.72, 0, 1] }}
              className="h-full rounded-full"
              style={{ background: GOOD, boxShadow: `0 0 6px ${GOOD}80` }}
            />
          </div>
        </div>
      </motion.div>

      {/* Bento grid — dealer-first order (PLAN.md B4): KPIs → oportunidades/mercado → margen/pipeline/AI → revenue/modelos → stale/actividad */}
      <div className="grid grid-cols-4 gap-3.5">

        {/* KPI row: back to 4-across — `sm` is a genuinely compact/landscape card
            now (~300x160, ~1.9:1), not the old near-square tile. */}
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

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 4', gridRow: '2', minHeight: 200 }}>
          <OportunidadesPanel plan={plan} onNavigate={() => navigate('/arbitrage')} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '4', gridRow: '2' }}>
          <MarketPositionMini onNavigate={() => navigate('/inteligencia')} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.30, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '3', minHeight: 260 }}>
          <MarginChart data={kpi.marginHistory} dark={dark} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3', gridRow: '3' }}>
          <PipelinePanel />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '4', gridRow: '3' }}>
          <ChatCompact kpi={kpi} username={username} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.40, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '4', minHeight: 240 }}>
          <RevenueChart data={kpi.marginHistory} dark={dark} onNavigate={() => navigate('/finance')} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.44, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3 / 5', gridRow: '4' }}>
          <TopModelsPanel onNavigate={() => navigate('/finance')} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.46, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1', gridRow: '5' }}>
          <StalePanel onNavigate={() => navigate('/vehicles')} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.48, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '2 / 4', gridRow: '5' }}>
          <ActivityFeed activities={kpi.recentActivities} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.50, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '4', gridRow: '5' }}>
          <FollowUpsPanel onNavigate={() => navigate('/inbox')} />
        </motion.div>

      </div>
    </div>
  )
}
