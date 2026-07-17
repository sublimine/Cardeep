import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect, useState } from 'react'
import {
  Key, RotateCw, Trash2, Plus, Copy, Check,
  ArrowUpRight, ArrowDownRight, Minus,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as ChartTooltip, ResponsiveContainer,
} from 'recharts'
import Card from '../components/Card'
import { useIsDark } from '../hooks/useIsDark'
import { ACCENT, GOOD, BAD, WARN } from '../lib/theme'

// ── Types ─────────────────────────────────────────────────────────────────────

interface Endpoint { id: string; path: string; description: string; tokens: string; type: 'INFO' | 'INVENTORY' }
interface ApiKey { id: string; name: string; masked: string; created: string; lastUsed: string; status: 'active' | 'revoked' }
interface TokenPlan { id: string; name: string; price: string; period: string; tokens: number; features: string[]; current: boolean; accent: string }

// ── Constants & mock data ─────────────────────────────────────────────────────

const TOKEN_BALANCE  = 84_200
const MONTH_CONSUMED = 115_800
const MONTH_LIMIT    = 200_000
const CALLS_TODAY    = 1_847

// Real, live endpoints only (services/api/routers/*.py, re-verified line-by-line
// 2026-07-18 against `grep -rn "@router\.get" services/api/routers/`). The prior
// catalog listed /v1/valuation, /v1/history, /v1/market/{model} and /v1/deal-score —
// none of which exist; "valuation by VIN" stays PROHIBITED until a validated pricing
// model exists (01-market-intelligence.md §4), and "deal-score" has no backing
// endpoint at all. This list is a curated subset of the real catalog (26 endpoints
// total across entities/geo/market/platforms/vehicles/auth/ops) — the ones with
// direct external-consumer value; /health, /auth/*, /ops/* are platform-internal.
const ENDPOINTS: Endpoint[] = [
  { id: 'mkt', path: 'GET /market/segments/{make}/{model}/stats', type: 'INFO',      description: 'Price distribution (p25/p50/p75), rotation, momentum & seller-pressure for a market segment', tokens: '3 tokens' },
  { id: 'dmd', path: 'GET /market/provinces/demand',              type: 'INFO',      description: 'Provincial demand ranking — absorption rate (removed listings vs. available stock)', tokens: '2 tokens' },
  { id: 'his', path: 'GET /vehicles/{ulid}/history',              type: 'INFO',      description: 'Full event history for one physical vehicle (NEW / GONE / PRICE_CHANGE / PHOTO_CHANGE / KM_CHANGE)', tokens: '2 tokens' },
  { id: 'lif', path: 'GET /vehicles/{ulid}/lifetime',             type: 'INFO',      description: 'Verified cross-platform lifetime chain plus C1-C10 market-life aggregates', tokens: '4 tokens' },
  { id: 'inv', path: 'GET /entities/{cdp_code}/inventory',        type: 'INVENTORY', description: 'Live, canonically-deduped stock feed for one dealer or platform', tokens: '1 / 100 results' },
  { id: 'delta', path: 'GET /entities/{cdp_code}/delta',          type: 'INVENTORY', description: 'Append-only delta feed: new listings, removals, price/photo/km changes', tokens: '1 token' },
]

const INITIAL_KEYS: ApiKey[] = [
  { id: 'k1', name: 'Production',    masked: 'cdp_live_••••3f9a', created: '15 Mar 2026', lastUsed: 'just now',    status: 'active'  },
  { id: 'k2', name: 'Staging',       masked: 'cdp_test_••••7b2e', created: '1 May 2026',  lastUsed: '28 Jun 2026', status: 'active'  },
  { id: 'k3', name: 'Deprecated v1', masked: 'cdp_live_••••1a4d', created: '1 Dec 2025',  lastUsed: '30 Apr 2026', status: 'revoked' },
]

// Prices match pages/Pricing.tsx exactly (05-MONETIZATION-MAP.md) — API access
// is the same 3 plans as the product, not a separate pricing surface.
const PLANS: TokenPlan[] = [
  {
    id: 'starter', name: 'Starter', price: '€0', period: '/mo', tokens: 2_000, current: false, accent: '#64748b',
    features: ['INFO endpoints — sandbox quota', 'No INVENTORY feed', '30 req / min', 'Community support'],
  },
  {
    id: 'scale', name: 'Scale', price: '€199', period: '/mo', tokens: 200_000, current: true, accent: ACCENT,
    features: ['All INFO endpoints', 'INVENTORY feed', '500 req / min', 'Webhook alerts', 'Priority support'],
  },
  {
    id: 'enterprise', name: 'Enterprise', price: 'Custom', period: '', tokens: 0, current: false, accent: GOOD,
    features: ['Unlimited tokens', 'SLA 99.9 %', 'Dedicated ingestion', 'EU data residency', 'SSO / SAML'],
  },
]

const C_RAW: [number, number, number, number, number][] = [
  [1520, 880, 610, 400, 320],[1640, 760, 540, 370, 210],[1480, 940, 720, 450, 280],
  [1840,1100, 880, 560, 190],[1360, 700, 540, 350, 120],[1620, 760, 630, 440, 170],
  [1740,1020, 790, 510, 210],[1520, 860, 680, 410, 140],[1660, 950, 750, 480, 200],
  [1900,1140, 920, 590, 230],[1400, 740, 580, 370, 130],[1580, 820, 660, 430, 160],
  [1770,1060, 840, 530, 220],[1600, 900, 710, 450, 180],[1700,1000, 790, 500, 190],
  [1960,1180, 940, 620, 240],[1440, 770, 610, 390, 140],[1620, 880, 690, 460, 176],
  [1800,1090, 860, 550, 216],[1670, 930, 740, 490, 196],[1730,1010, 800, 516, 204],
  [2000,1210, 960, 640, 250],[1470, 800, 630, 400, 150],[1650, 910, 720, 476, 184],
  [1830,1120, 880, 570, 224],[1690, 950, 750, 500, 200],[1760,1040, 830, 536, 212],
  [2040,1250, 980, 660, 260],[1496, 820, 650, 416, 156],[1720, 940, 750, 496, 196],
]
const CONSUMPTION_DATA = C_RAW.map((d, i) => ({ day: String(i + 1), market: d[0], valuation: d[1], history: d[2], dealScore: d[3], inventory: d[4] }))

// Real endpoint, real segment, real numbers — captured from the live published
// market_stat run (01-market-intelligence F2, run_id 01KXS6Q4TJKCWM19KKQN2SJ2J1,
// re-verified 2026-07-18). No "valuation by VIN" example: that endpoint is
// PROHIBITED until a validated pricing model exists (01-market-intelligence.md §4).
const CURL_EXAMPLE = `curl -s -X GET \\
  "https://api.cardeep.eu/market/segments/Peugeot/208/stats?year=2024&fuel=Gasolina" \\
  -H "X-API-Key: cdp_live_••••3f9a" \\
  -H "Accept: application/json"`

const RESPONSE_EXAMPLE = `{
  "ok": true,
  "data": {
    "make": "Peugeot",
    "model": "208",
    "year": 2024,
    "fuel": "Gasolina",
    "metrics": {
      "M1": { "n": 7026, "p25": 11990, "p50": 13500, "p75": 14770, "scope": "nat" },
      "M3": { "n": 451, "value": 10.2, "scope": "nat",
              "detail": { "unit": "days_to_listing_removal", "window_days": 35.2 } },
      "M4": { "n": 7026, "value": 547.7, "scope": "nat",
              "detail": { "gone_n": 451, "available_n": 7026 } },
      "M9": { "n": 7026, "value": 17.9, "scope": "nat",
              "detail": { "n_cut": 1261, "median_cut_pct": 2.1 } }
    }
  },
  "error": null,
  "meta": { "run_id": "01KXS6Q4TJKCWM19KKQN2SJ2J1", "window_description": "..." }
}`

const ENDPOINT_COLORS: Record<string, string> = { market: ACCENT, valuation: WARN, history: '#60a5fa', dealScore: GOOD, inventory: '#0891b2' }
const ENDPOINT_LABELS: Record<string, string> = { market: 'Market', valuation: 'Valuation', history: 'History', dealScore: 'Deal Score', inventory: 'Inventory' }

// ── AnimNum / Spark ────────────────────────────────────────────────────────────

function AnimNum({ to, prefix = '', suffix = '', decimals = 0 }: { to: number; prefix?: string; suffix?: string; decimals?: number }) {
  const mv = useMotionValue(0)
  const sp = useSpring(mv, { stiffness: 55, damping: 14 })
  const d  = useTransform(sp, v => `${prefix}${decimals ? v.toFixed(decimals) : Math.round(v)}${suffix}`)
  useEffect(() => { mv.set(to) }, [to, mv])
  return <motion.span>{d}</motion.span>
}

function Spark({ values, color, height = 28 }: { values: number[]; color: string; height?: number }) {
  if (values.length < 2) return null
  const max = Math.max(...values), min = Math.min(...values), range = max - min || 1
  const W = 64, H = height
  const pts = values.map((v, i): [number, number] => [(i / (values.length - 1)) * W, H - ((v - min) / range) * (H - 4) + 2])
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

interface KpiCardProps { label: string; value: number; prefix?: string; suffix?: string; decimals?: number; textValue?: string; sub: string; trend: 'up' | 'down' | 'flat' | 'good'; trendLabel: string; spark: number[]; delay?: number }

function KpiCard({ label, value, prefix, suffix, decimals, textValue, sub, trend, trendLabel, spark, delay = 0 }: KpiCardProps) {
  const trendColor = trend === 'up' || trend === 'good' ? GOOD : trend === 'down' ? BAD : 'var(--text-muted)'
  const TrendIcon  = trend === 'up' || trend === 'good' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : Minus

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.42, ease: [0.32, 0.72, 0, 1] }}>
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

// ── Endpoint catalog ──────────────────────────────────────────────────────────

function EndpointCatalog() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Endpoint Catalog</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Tokens deducted on success only — no charge on error</p>
        </div>

        <div className="flex flex-1 flex-col gap-[7px] overflow-y-auto">
          {ENDPOINTS.map((ep, i) => (
            <motion.div
              key={ep.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.14 + i * 0.07, duration: 0.3 }}
              className="grid items-start gap-x-3 gap-y-1.5 rounded-[10px] p-[9px_11px]"
              style={{ gridTemplateColumns: '1fr auto', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
            >
              <div className="min-w-0">
                <div className="mb-[3px] flex items-center gap-1.5">
                  <span
                    className="shrink-0 rounded px-1.5 py-px text-[8.5px] font-bold tracking-[0.06em]"
                    style={{ background: `${ACCENT}1f`, border: `1px solid ${ACCENT}40`, color: ACCENT }}
                  >
                    {ep.type}
                  </span>
                  <code className="truncate font-mono text-[10.5px] font-medium" style={{ color: 'var(--text-primary)' }}>{ep.path}</code>
                </div>
                <p className="m-0 text-[10.5px] leading-[1.45]" style={{ color: 'var(--text-secondary)' }}>{ep.description}</p>
              </div>

              <span
                className="whitespace-nowrap rounded-full px-2 py-0.5 text-[9.5px] font-bold tabular-nums"
                style={{ background: `${GOOD}1a`, border: `1px solid ${GOOD}38`, color: GOOD }}
              >
                {ep.tokens}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Consumption chart ─────────────────────────────────────────────────────────

function ConsumptionChart({ dark }: { dark: boolean }) {
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Token Consumption</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Last 30 days — stacked by endpoint</p>
        </div>

        <div className="mb-3 flex shrink-0 flex-wrap gap-x-3.5 gap-y-1">
          {Object.entries(ENDPOINT_COLORS).map(([key, color]) => (
            <div key={key} className="flex items-center gap-[5px]">
              <span className="inline-block h-[7px] w-[7px] rounded-sm" style={{ background: color }} />
              <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>{ENDPOINT_LABELS[key]}</span>
            </div>
          ))}
        </div>

        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={CONSUMPTION_DATA} margin={{ top: 4, right: 0, left: -24, bottom: 0 }} barSize={7} barCategoryGap="18%">
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
              <XAxis dataKey="day" tick={{ fontSize: 8.5, fill: tickColor }} axisLine={false} tickLine={false} interval={4} />
              <YAxis tick={{ fontSize: 8.5, fill: tickColor }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`} />
              <ChartTooltip
                contentStyle={{ background: dark ? '#0e0e1a' : '#fff', border: '1px solid var(--border-default)', borderRadius: 10, fontSize: 11, color: dark ? '#f1f5f9' : '#0f172a', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
                formatter={(v: number, name: string) => [`${v.toLocaleString()} tokens`, ENDPOINT_LABELS[name] ?? name]}
                cursor={{ fill: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }}
                labelFormatter={(label: string) => `Day ${label}`}
              />
              {Object.entries(ENDPOINT_COLORS).map(([key, color]) => (
                <Bar key={key} dataKey={key} stackId="a" fill={color} fillOpacity={0.88} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  )
}

// ── API Keys panel ────────────────────────────────────────────────────────────

function ApiKeysPanel() {
  const [keys, setKeys] = useState<ApiKey[]>(INITIAL_KEYS)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  function handleRevoke(id: string) {
    setKeys(prev => prev.map(k => k.id === id ? { ...k, status: 'revoked' as const } : k))
  }
  function handleCopy(id: string) {
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }
  function handleCreate() {
    const ts = Date.now().toString().slice(-6)
    setKeys(prev => [...prev, { id: `k${ts}`, name: `Key ${prev.length + 1}`, masked: `cdp_test_••••${ts.slice(-4)}`, created: 'just now', lastUsed: '—', status: 'active' as const }])
  }

  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-4 flex shrink-0 items-center justify-between">
          <div>
            <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>API Keys</h2>
            <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Use Bearer tokens to authenticate API calls</p>
          </div>
          <motion.button
            onClick={handleCreate}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            className="flex items-center gap-[5px] rounded-[9px] px-3 py-1.5 text-[11px] font-bold text-white"
            style={{ background: ACCENT }}
          >
            <Plus style={{ width: 11, height: 11 }} />
            New key
          </motion.button>
        </div>

        <div className="flex flex-1 flex-col gap-2 overflow-y-auto">
          {keys.map((k, i) => (
            <motion.div
              key={k.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              className="flex items-center gap-2.5 rounded-[10px] p-[10px_12px]"
              style={{ background: 'var(--bg-surface)', border: `1px solid ${k.status === 'revoked' ? `${BAD}26` : 'var(--border-subtle)'}`, opacity: k.status === 'revoked' ? 0.62 : 1 }}
            >
              <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-[9px]" style={{ background: k.status === 'revoked' ? `${BAD}1a` : `${ACCENT}1a`, border: `1px solid ${k.status === 'revoked' ? `${BAD}33` : `${ACCENT}2e`}` }}>
                <Key style={{ width: 13, height: 13, color: k.status === 'revoked' ? BAD : ACCENT }} />
              </div>

              <div className="min-w-0 flex-1">
                <div className="mb-[3px] flex items-center gap-1.5">
                  <span className="text-[11.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{k.name}</span>
                  <span
                    className="rounded-full px-1.5 py-px text-[8px] font-bold tracking-[0.06em]"
                    style={{ background: k.status === 'active' ? `${GOOD}1f` : `${BAD}1f`, border: `1px solid ${k.status === 'active' ? `${GOOD}38` : `${BAD}38`}`, color: k.status === 'active' ? GOOD : BAD }}
                  >
                    {k.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center gap-2.5">
                  <code className="font-mono text-[10.5px]" style={{ color: 'var(--text-secondary)' }}>{k.masked}</code>
                  <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>created {k.created}</span>
                  <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>used {k.lastUsed}</span>
                </div>
              </div>

              {k.status === 'active' && (
                <div className="flex shrink-0 items-center gap-1">
                  <button onClick={() => handleCopy(k.id)} title="Copy key" className="flex h-[26px] w-[26px] items-center justify-center rounded-[7px] border bg-transparent" style={{ borderColor: 'var(--border-subtle)' }}>
                    {copiedId === k.id ? <Check style={{ width: 11, height: 11, color: GOOD }} /> : <Copy style={{ width: 11, height: 11, color: 'var(--text-secondary)' }} />}
                  </button>
                  <button title="Rotate key" className="flex h-[26px] w-[26px] items-center justify-center rounded-[7px] border bg-transparent" style={{ borderColor: 'var(--border-subtle)' }}>
                    <RotateCw style={{ width: 11, height: 11, color: 'var(--text-secondary)' }} />
                  </button>
                  <button onClick={() => handleRevoke(k.id)} title="Revoke key" className="flex h-[26px] w-[26px] items-center justify-center rounded-[7px] border bg-transparent" style={{ borderColor: `${BAD}38` }}>
                    <Trash2 style={{ width: 11, height: 11, color: BAD }} />
                  </button>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Plans panel ───────────────────────────────────────────────────────────────

function PlansPanel() {
  return (
    <Card className="!p-0 h-full">
      <div className="flex h-full flex-col p-[18px_20px_14px]">
        <div className="mb-3.5 shrink-0">
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Plans & Top-up</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Switch plan or buy additional token packs</p>
        </div>

        <div className="flex flex-1 gap-3">
          {PLANS.map((plan, i) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.18 + i * 0.08 }}
              className="flex flex-1 flex-col rounded-xl p-[14px_14px_12px]"
              style={{ background: plan.current ? `linear-gradient(145deg, ${plan.accent}1f, ${plan.accent}0a)` : 'var(--bg-surface)', border: `1px solid ${plan.current ? `${plan.accent}48` : 'var(--border-subtle)'}` }}
            >
              <div className="mb-2.5 flex items-start justify-between">
                <div>
                  <div className="mb-0.5 flex items-center gap-1.5">
                    <span className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>{plan.name}</span>
                    {plan.current && (
                      <span className="rounded-full px-[5px] py-px text-[7.5px] font-bold tracking-[0.05em]" style={{ background: `${plan.accent}2e`, border: `1px solid ${plan.accent}48`, color: plan.accent }}>NOW</span>
                    )}
                  </div>
                  {plan.tokens > 0 && <span className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>{plan.tokens.toLocaleString()} tokens / mo</span>}
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-xl font-extrabold leading-none tracking-[-0.02em]" style={{ color: plan.current ? plan.accent : 'var(--text-primary)' }}>{plan.price}</div>
                  {plan.period && <div className="text-[9.5px]" style={{ color: 'var(--text-muted)' }}>{plan.period}</div>}
                </div>
              </div>

              <div className="flex flex-1 flex-col gap-1">
                {plan.features.map(f => (
                  <div key={f} className="flex items-center gap-[7px]">
                    <span className="h-[3px] w-[3px] shrink-0 rounded-full" style={{ background: plan.accent }} />
                    <span className="text-[10px] leading-[1.35]" style={{ color: 'var(--text-secondary)' }}>{f}</span>
                  </div>
                ))}
              </div>

              <button
                className="mt-3 w-full rounded-lg py-[7px] text-[10.5px] font-bold transition-colors"
                style={{ background: plan.current ? plan.accent : 'transparent', border: `1px solid ${plan.current ? plan.accent : 'var(--border-subtle)'}`, color: plan.current ? '#fff' : 'var(--text-secondary)' }}
              >
                {plan.current ? 'Active' : plan.id === 'enterprise' ? 'Contact Sales' : 'Upgrade'}
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}

// ── Code example ──────────────────────────────────────────────────────────────

function CodeExample() {
  const [copied, setCopied] = useState(false)

  return (
    <Card>
      <div className="mb-3.5 flex items-center justify-between">
        <div>
          <h2 className="text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>Quick Start</h2>
          <p className="text-[10.5px]" style={{ color: 'var(--text-muted)' }}>Call the market segment endpoint in under 60 seconds</p>
        </div>
        <button
          onClick={() => { setCopied(true); setTimeout(() => setCopied(false), 2200) }}
          className="flex items-center gap-[5px] rounded-[9px] px-3 py-1.5 text-[11px] font-semibold"
          style={{ border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}
        >
          {copied
            ? <><Check style={{ width: 10, height: 10, color: GOOD }} /><span style={{ color: GOOD }}>Copied</span></>
            : <><Copy style={{ width: 10, height: 10 }} /><span>Copy</span></>
          }
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="mb-1.5 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>Request</div>
          <pre className="m-0 overflow-x-auto rounded-[10px] p-[14px_16px] font-mono text-[11.5px] leading-[1.7]" style={{ background: '#0f172a', color: '#e2e8f0' }}>{CURL_EXAMPLE}</pre>
        </div>
        <div>
          <div className="mb-1.5 text-[9.5px] font-bold uppercase tracking-[0.08em]" style={{ color: 'var(--text-muted)' }}>Response · 200 OK · 3 tokens</div>
          <pre className="m-0 overflow-x-auto rounded-[10px] p-[14px_16px] font-mono text-[11.5px] leading-[1.7]" style={{ background: '#0f172a', color: '#e2e8f0' }}>{RESPONSE_EXAMPLE}</pre>
        </div>
      </div>
    </Card>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Api() {
  const dark = useIsDark()

  const kpiCards: KpiCardProps[] = [
    { label: 'Token Balance', value: TOKEN_BALANCE, sub: `${MONTH_LIMIT.toLocaleString()} token monthly limit`, trend: 'flat', trendLabel: `${Math.round((TOKEN_BALANCE / MONTH_LIMIT) * 100)}% remaining`, spark: [96400, 92100, 89300, 87800, 86100, TOKEN_BALANCE], delay: 0 },
    { label: 'Consumed This Month', value: MONTH_CONSUMED, sub: `${Math.round((MONTH_CONSUMED / MONTH_LIMIT) * 100)}% of ${(MONTH_LIMIT / 1000).toFixed(0)}k limit used`, trend: 'up', trendLabel: '+23% vs last month', spark: [78400, 88200, 96500, 102800, 110100, MONTH_CONSUMED], delay: 0.06 },
    { label: 'Current Plan', value: 0, textValue: 'Scale', sub: '€199 / month · 200k tokens', trend: 'good', trendLabel: 'active subscription', spark: [1, 1, 1, 1, 1, 1], delay: 0.12 },
    { label: 'API Calls Today', value: CALLS_TODAY, sub: 'across all endpoints', trend: 'up', trendLabel: '+18% vs yesterday', spark: [1240, 1390, 1510, 1680, 1760, CALLS_TODAY], delay: 0.18 },
  ]

  return (
    <div className="mx-auto p-[24px_24px_40px]" style={{ maxWidth: 1360 }}>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }} className="mb-[22px]">
        <div className="mb-1.5 font-mono text-[10.5px] tracking-[0.04em]" style={{ color: 'var(--text-muted)' }}>cardeep.eu · API v1</div>
        <h1 className="mb-1 text-[22px] font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>API & Tokens</h1>
        <p className="text-[11.5px]" style={{ color: 'var(--text-muted)' }}>Sell and consume cardeep data via API — billed per token, deducted on success only.</p>
      </motion.div>

      <div className="grid grid-cols-4 gap-3.5">

        {kpiCards.map(card => <KpiCard key={card.label} {...card} />)}

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '2', minHeight: 320 }}>
          <EndpointCatalog />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3 / 5', gridRow: '2', minHeight: 320 }}>
          <ConsumptionChart dark={dark} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 3', gridRow: '3' }}>
          <ApiKeysPanel />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '3 / 5', gridRow: '3' }}>
          <PlansPanel />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.44, duration: 0.44, ease: [0.32, 0.72, 0, 1] }} style={{ gridColumn: '1 / 5', gridRow: '4' }}>
          <CodeExample />
        </motion.div>

      </div>
    </div>
  )
}
