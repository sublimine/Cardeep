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

// ── Types ─────────────────────────────────────────────────────────────────────

interface Endpoint {
  id: string
  path: string
  description: string
  tokens: string
  type: 'INFO' | 'INVENTORY'
}

interface ApiKey {
  id: string
  name: string
  masked: string
  created: string
  lastUsed: string
  status: 'active' | 'revoked'
}

interface Plan {
  id: string
  name: string
  price: string
  period: string
  tokens: number
  features: string[]
  current: boolean
  accent: string
}

// ── Constants & mock data ─────────────────────────────────────────────────────

const TOKEN_BALANCE  = 84_200
const MONTH_CONSUMED = 115_800
const MONTH_LIMIT    = 200_000
const CALLS_TODAY    = 1_847

const ENDPOINTS: Endpoint[] = [
  {
    id: 'val', path: 'GET /v1/valuation/{vin}', type: 'INFO',
    description: 'Retail, trade & residual value with confidence score',
    tokens: '5 tokens',
  },
  {
    id: 'his', path: 'GET /v1/history/{vin}', type: 'INFO',
    description: 'Mileage history, accident records & ownership chain',
    tokens: '8 tokens',
  },
  {
    id: 'mkt', path: 'GET /v1/market/{model}', type: 'INFO',
    description: 'Price-position vs live market, days-to-sell, p25 / p75 distribution',
    tokens: '3 tokens',
  },
  {
    id: 'ds', path: 'GET /v1/deal-score/{listing}', type: 'INFO',
    description: 'Deal score 0–100 with margin, rotation & arbitrage breakdown',
    tokens: '4 tokens',
  },
  {
    id: 'inv', path: 'GET /v1/inventory', type: 'INVENTORY',
    description: 'Live stock feed — filterable by make, model, region & price range',
    tokens: '1 / 100 results',
  },
  {
    id: 'inv1', path: 'GET /v1/inventory/{id}', type: 'INVENTORY',
    description: 'Full listing detail with VAM-verified multi-source provenance',
    tokens: '1 token',
  },
]

const INITIAL_KEYS: ApiKey[] = [
  { id: 'k1', name: 'Production',    masked: 'cdp_live_••••3f9a', created: '15 Mar 2026', lastUsed: 'just now',    status: 'active'  },
  { id: 'k2', name: 'Staging',       masked: 'cdp_test_••••7b2e', created: '1 May 2026',  lastUsed: '28 Jun 2026', status: 'active'  },
  { id: 'k3', name: 'Deprecated v1', masked: 'cdp_live_••••1a4d', created: '1 Dec 2025',  lastUsed: '30 Apr 2026', status: 'revoked' },
]

const PLANS: Plan[] = [
  {
    id: 'starter', name: 'Starter', price: '€49', period: '/mo', tokens: 50_000, current: false, accent: '#64748b',
    features: ['All INFO endpoints', 'No INVENTORY feed', '100 req / min', 'Email support'],
  },
  {
    id: 'scale', name: 'Scale', price: '€149', period: '/mo', tokens: 200_000, current: true, accent: '#3b82f6',
    features: ['All endpoints', 'INVENTORY feed', '500 req / min', 'Webhook alerts', 'Priority support'],
  },
  {
    id: 'enterprise', name: 'Enterprise', price: 'Custom', period: '', tokens: 0, current: false, accent: '#7c3aed',
    features: ['Unlimited tokens', 'SLA 99.9 %', 'Dedicated ingestion', 'EU data residency', 'SSO / SAML'],
  },
]

// 30 days of token consumption, [market, valuation, history, dealScore, inventory]
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
const CONSUMPTION_DATA = C_RAW.map((d, i) => ({
  day: String(i + 1),
  market: d[0], valuation: d[1], history: d[2], dealScore: d[3], inventory: d[4],
}))

const CURL_EXAMPLE = `curl -s -X GET \\
  "https://api.cardeep.eu/v1/valuation/WVWZZZ3CZME123456" \\
  -H "Authorization: Bearer cdp_live_••••3f9a" \\
  -H "Accept: application/json"`

const RESPONSE_EXAMPLE = `{
  "vin": "WVWZZZ3CZME123456",
  "make": "Volkswagen",
  "model": "Golf",
  "year": 2021,
  "retail": 18450,
  "trade": 16200,
  "residual": { "1yr": 15200, "2yr": 12400, "3yr": 10100 },
  "price_position": -4.2,
  "confidence": 0.94,
  "tokens_used": 5,
  "tokens_remaining": 84195
}`

const ENDPOINT_COLORS: Record<string, string> = {
  market:    '#3b82f6',
  valuation: '#f59e0b',
  history:   '#a78bfa',
  dealScore: '#22c55e',
  inventory: '#0ea5e9',
}

const ENDPOINT_LABELS: Record<string, string> = {
  market:    'Market',
  valuation: 'Valuation',
  history:   'History',
  dealScore: 'Deal Score',
  inventory: 'Inventory',
}

// ── useIsDark ─────────────────────────────────────────────────────────────────

function useIsDark() {
  const [dark, setDark] = useState(() => !document.documentElement.classList.contains('light'))
  useEffect(() => {
    const obs = new MutationObserver(() => setDark(!document.documentElement.classList.contains('light')))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return dark
}

// ── tok ───────────────────────────────────────────────────────────────────────

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

// ── GCard ─────────────────────────────────────────────────────────────────────

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

// ── Endpoint catalog ──────────────────────────────────────────────────────────

function EndpointCatalog({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 14, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Endpoint Catalog</h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>Tokens deducted on success only — no charge on error</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 7, flex: 1, overflowY: 'auto' }}>
          {ENDPOINTS.map((ep, i) => (
            <motion.div
              key={ep.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.14 + i * 0.07, duration: 0.3 }}
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr auto',
                alignItems: 'start',
                gap: '6px 12px',
                padding: '9px 11px',
                borderRadius: 10,
                background: c.subBg,
                border: `1px solid ${c.subBord}`,
              }}
            >
              <div style={{ minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
                  <span style={{
                    fontSize: 8.5, fontWeight: 700, letterSpacing: '0.06em',
                    padding: '1px 6px', borderRadius: 4, flexShrink: 0,
                    background: ep.type === 'INFO' ? 'rgba(59,130,246,0.12)' : 'rgba(124,58,237,0.12)',
                    border:     `1px solid ${ep.type === 'INFO' ? 'rgba(59,130,246,0.25)' : 'rgba(124,58,237,0.25)'}`,
                    color:      ep.type === 'INFO' ? '#3b82f6' : '#7c3aed',
                  }}>
                    {ep.type}
                  </span>
                  <code style={{
                    fontSize: 10.5, fontFamily: 'ui-monospace, monospace',
                    color: c.t1, fontWeight: 500,
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}>
                    {ep.path}
                  </code>
                </div>
                <p style={{ fontSize: 10.5, color: c.t3, margin: 0, lineHeight: 1.45 }}>{ep.description}</p>
              </div>

              <span style={{
                fontSize: 9.5, fontWeight: 700, fontVariantNumeric: 'tabular-nums',
                padding: '2px 8px', borderRadius: 99, whiteSpace: 'nowrap',
                background: 'rgba(34,197,94,0.10)',
                border: '1px solid rgba(34,197,94,0.22)',
                color: '#16a34a',
              }}>
                {ep.tokens}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Consumption chart ─────────────────────────────────────────────────────────

function ConsumptionChart({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const tickColor = dark ? '#3f3f5a' : '#94a3b8'
  const gridColor = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)'

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 12, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Token Consumption</h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>Last 30 days — stacked by endpoint</p>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 14px', marginBottom: 12, flexShrink: 0 }}>
          {Object.entries(ENDPOINT_COLORS).map(([key, color]) => (
            <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 7, height: 7, borderRadius: 2, background: color, display: 'inline-block' }} />
              <span style={{ fontSize: 9.5, color: c.t4 }}>{ENDPOINT_LABELS[key]}</span>
            </div>
          ))}
        </div>

        <div style={{ flex: 1, minHeight: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={CONSUMPTION_DATA} margin={{ top: 4, right: 0, left: -24, bottom: 0 }} barSize={7} barCategoryGap="18%">
              <CartesianGrid strokeDasharray="1 8" stroke={gridColor} vertical={false} />
              <XAxis
                dataKey="day"
                tick={{ fontSize: 8.5, fill: tickColor }}
                axisLine={false} tickLine={false}
                interval={4}
              />
              <YAxis
                tick={{ fontSize: 8.5, fill: tickColor }}
                axisLine={false} tickLine={false}
                tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
              />
              <ChartTooltip
                contentStyle={{
                  background: dark ? '#0e0e1a' : '#fff',
                  border: `1px solid ${c.cardBord}`,
                  borderRadius: 10, fontSize: 11, color: c.t1,
                  boxShadow: '0 8px 24px rgba(0,0,0,0.18)',
                }}
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
    </GCard>
  )
}

// ── API Keys panel ────────────────────────────────────────────────────────────

function ApiKeysPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)
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
    setKeys(prev => [
      ...prev,
      {
        id: `k${ts}`,
        name: `Key ${prev.length + 1}`,
        masked: `cdp_test_••••${ts.slice(-4)}`,
        created: 'just now',
        lastUsed: '—',
        status: 'active' as const,
      },
    ])
  }

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexShrink: 0 }}>
          <div>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>API Keys</h2>
            <p style={{ fontSize: 10.5, color: c.t4 }}>Use Bearer tokens to authenticate API calls</p>
          </div>
          <motion.button
            onClick={handleCreate}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            style={{
              display: 'flex', alignItems: 'center', gap: 5,
              padding: '6px 12px', borderRadius: 9,
              background: '#3b82f6', border: 'none',
              color: '#fff', fontSize: 11, fontWeight: 700,
              fontFamily: 'Inter, system-ui', cursor: 'pointer',
            }}
          >
            <Plus style={{ width: 11, height: 11 }} />
            New key
          </motion.button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1, overflowY: 'auto' }}>
          {keys.map((k, i) => (
            <motion.div
              key={k.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 12px', borderRadius: 10,
                background: c.subBg,
                border: `1px solid ${k.status === 'revoked' ? 'rgba(248,113,113,0.15)' : c.subBord}`,
                opacity: k.status === 'revoked' ? 0.62 : 1,
              }}
            >
              {/* Icon */}
              <div style={{
                width: 30, height: 30, borderRadius: 9, flexShrink: 0,
                background: k.status === 'revoked' ? 'rgba(248,113,113,0.10)' : 'rgba(59,130,246,0.10)',
                border: `1px solid ${k.status === 'revoked' ? 'rgba(248,113,113,0.20)' : 'rgba(59,130,246,0.18)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Key style={{ width: 13, height: 13, color: k.status === 'revoked' ? '#f87171' : '#3b82f6' }} />
              </div>

              {/* Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
                  <span style={{ fontSize: 11.5, fontWeight: 600, color: c.t1 }}>{k.name}</span>
                  <span style={{
                    fontSize: 8, fontWeight: 700, letterSpacing: '0.06em',
                    padding: '1px 6px', borderRadius: 99,
                    background: k.status === 'active' ? 'rgba(34,197,94,0.12)' : 'rgba(248,113,113,0.12)',
                    border: `1px solid ${k.status === 'active' ? 'rgba(34,197,94,0.22)' : 'rgba(248,113,113,0.22)'}`,
                    color: k.status === 'active' ? '#16a34a' : '#ef4444',
                  }}>
                    {k.status.toUpperCase()}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <code style={{ fontSize: 10.5, fontFamily: 'ui-monospace, monospace', color: c.t3 }}>{k.masked}</code>
                  <span style={{ fontSize: 9.5, color: c.t4 }}>created {k.created}</span>
                  <span style={{ fontSize: 9.5, color: c.t4 }}>used {k.lastUsed}</span>
                </div>
              </div>

              {/* Actions */}
              {k.status === 'active' && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
                  <motion.button
                    onClick={() => handleCopy(k.id)}
                    whileTap={{ scale: 0.88 }}
                    title="Copy key"
                    style={{
                      width: 26, height: 26, borderRadius: 7,
                      border: `1px solid ${c.subBord}`,
                      background: 'transparent', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                  >
                    {copiedId === k.id
                      ? <Check style={{ width: 11, height: 11, color: '#22c55e' }} />
                      : <Copy style={{ width: 11, height: 11, color: c.t3 }} />
                    }
                  </motion.button>
                  <motion.button
                    whileTap={{ scale: 0.88 }}
                    title="Rotate key"
                    style={{
                      width: 26, height: 26, borderRadius: 7,
                      border: `1px solid ${c.subBord}`,
                      background: 'transparent', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                  >
                    <RotateCw style={{ width: 11, height: 11, color: c.t3 }} />
                  </motion.button>
                  <motion.button
                    onClick={() => handleRevoke(k.id)}
                    whileTap={{ scale: 0.88 }}
                    title="Revoke key"
                    style={{
                      width: 26, height: 26, borderRadius: 7,
                      border: '1px solid rgba(248,113,113,0.22)',
                      background: 'transparent', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                  >
                    <Trash2 style={{ width: 11, height: 11, color: '#f87171' }} />
                  </motion.button>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Plans panel ───────────────────────────────────────────────────────────────

function PlansPanel({ dark }: { dark: boolean }) {
  const c = tok(dark)

  return (
    <GCard dark={dark} style={{ height: '100%' }}>
      <div style={{ padding: '18px 20px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: 14, flexShrink: 0 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Plans & Top-up</h2>
          <p style={{ fontSize: 10.5, color: c.t4 }}>Switch plan or buy additional token packs</p>
        </div>

        <div style={{ display: 'flex', gap: 12, flex: 1 }}>
          {PLANS.map((plan, i) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.18 + i * 0.08 }}
              style={{
                flex: 1,
                padding: '14px 14px 12px',
                borderRadius: 12,
                background: plan.current
                  ? `linear-gradient(145deg, ${plan.accent}12, ${plan.accent}06)`
                  : c.subBg,
                border: `1px solid ${plan.current ? `${plan.accent}28` : c.subBord}`,
                display: 'flex', flexDirection: 'column',
              }}
            >
              {/* Name + price */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 2 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: c.t1 }}>{plan.name}</span>
                    {plan.current && (
                      <span style={{
                        fontSize: 7.5, fontWeight: 700, letterSpacing: '0.05em',
                        padding: '1px 5px', borderRadius: 99,
                        background: `${plan.accent}18`,
                        border: `1px solid ${plan.accent}28`,
                        color: plan.accent,
                      }}>NOW</span>
                    )}
                  </div>
                  {plan.tokens > 0 && (
                    <span style={{ fontSize: 9.5, color: c.t4 }}>
                      {plan.tokens.toLocaleString()} tokens / mo
                    </span>
                  )}
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.02em', color: plan.current ? plan.accent : c.t1, lineHeight: 1 }}>
                    {plan.price}
                  </div>
                  {plan.period && (
                    <div style={{ fontSize: 9.5, color: c.t4 }}>{plan.period}</div>
                  )}
                </div>
              </div>

              {/* Features */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
                {plan.features.map(f => (
                  <div key={f} style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                    <span style={{ width: 3, height: 3, borderRadius: '50%', background: plan.accent, flexShrink: 0 }} />
                    <span style={{ fontSize: 10, color: c.t2, lineHeight: 1.35 }}>{f}</span>
                  </div>
                ))}
              </div>

              {/* CTA */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                style={{
                  marginTop: 12,
                  padding: '7px 0', width: '100%', borderRadius: 8,
                  background: plan.current ? plan.accent : 'transparent',
                  border: `1px solid ${plan.current ? plan.accent : c.subBord}`,
                  color: plan.current ? '#fff' : c.t2,
                  fontSize: 10.5, fontWeight: 700,
                  fontFamily: 'Inter, system-ui', cursor: 'pointer',
                  transition: 'all 130ms',
                }}
              >
                {plan.current ? 'Active' : plan.id === 'enterprise' ? 'Contact Sales' : 'Upgrade'}
              </motion.button>
            </motion.div>
          ))}
        </div>
      </div>
    </GCard>
  )
}

// ── Code example ──────────────────────────────────────────────────────────────

function CodeExample({ dark }: { dark: boolean }) {
  const c = tok(dark)
  const [copied, setCopied] = useState(false)
  const codeBg = dark ? '#090912' : '#0f172a'

  return (
    <GCard dark={dark}>
      <div style={{ padding: '18px 20px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <div>
            <h2 style={{ fontSize: 13, fontWeight: 700, color: c.t1, marginBottom: 2 }}>Quick Start</h2>
            <p style={{ fontSize: 10.5, color: c.t4 }}>Call the valuation endpoint in under 60 seconds</p>
          </div>
          <motion.button
            onClick={() => { setCopied(true); setTimeout(() => setCopied(false), 2200) }}
            whileTap={{ scale: 0.95 }}
            style={{
              display: 'flex', alignItems: 'center', gap: 5,
              padding: '6px 12px', borderRadius: 9,
              background: 'transparent',
              border: `1px solid ${c.subBord}`,
              color: c.t3, fontSize: 11, fontWeight: 600,
              fontFamily: 'Inter, system-ui', cursor: 'pointer',
            }}
          >
            {copied
              ? <><Check style={{ width: 10, height: 10, color: '#22c55e' }} /><span style={{ color: '#22c55e' }}>Copied</span></>
              : <><Copy style={{ width: 10, height: 10 }} /><span>Copy</span></>
            }
          </motion.button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <div style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: c.t4, marginBottom: 6 }}>
              Request
            </div>
            <pre style={{
              margin: 0, padding: '14px 16px', borderRadius: 10,
              background: codeBg,
              fontSize: 11.5,
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
              lineHeight: 1.7, color: '#e2e8f0', overflowX: 'auto',
            }}>
              {CURL_EXAMPLE}
            </pre>
          </div>
          <div>
            <div style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: c.t4, marginBottom: 6 }}>
              Response · 200 OK · 5 tokens
            </div>
            <pre style={{
              margin: 0, padding: '14px 16px', borderRadius: 10,
              background: codeBg,
              fontSize: 11.5,
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
              lineHeight: 1.7, color: '#e2e8f0', overflowX: 'auto',
            }}>
              {RESPONSE_EXAMPLE}
            </pre>
          </div>
        </div>
      </div>
    </GCard>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Api() {
  const dark = useIsDark()
  const c = tok(dark)

  const kpiCards: KpiCardProps[] = [
    {
      dark,
      label: 'Token Balance',
      value: TOKEN_BALANCE,
      sub: `${MONTH_LIMIT.toLocaleString()} token monthly limit`,
      trend: 'flat',
      trendLabel: `${Math.round((TOKEN_BALANCE / MONTH_LIMIT) * 100)}% remaining`,
      accent: '#3b82f6',
      spark: [96400, 92100, 89300, 87800, 86100, TOKEN_BALANCE],
      delay: 0,
    },
    {
      dark,
      label: 'Consumed This Month',
      value: MONTH_CONSUMED,
      sub: `${Math.round((MONTH_CONSUMED / MONTH_LIMIT) * 100)}% of ${(MONTH_LIMIT / 1000).toFixed(0)}k limit used`,
      trend: 'up',
      trendLabel: '+23% vs last month',
      accent: '#f59e0b',
      spark: [78400, 88200, 96500, 102800, 110100, MONTH_CONSUMED],
      delay: 0.06,
    },
    {
      dark,
      label: 'Current Plan',
      value: 0,
      textValue: 'Scale',
      sub: '€149 / month · 200k tokens',
      trend: 'good',
      trendLabel: 'active subscription',
      accent: '#7c3aed',
      spark: [1, 1, 1, 1, 1, 1],
      delay: 0.12,
    },
    {
      dark,
      label: 'API Calls Today',
      value: CALLS_TODAY,
      sub: 'across all endpoints',
      trend: 'up',
      trendLabel: '+18% vs yesterday',
      accent: '#0ea5e9',
      spark: [1240, 1390, 1510, 1680, 1760, CALLS_TODAY],
      delay: 0.18,
    },
  ]

  return (
    <div style={{ padding: '24px 24px 40px', maxWidth: 1360, margin: '0 auto' }}>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
        style={{ marginBottom: 22 }}
      >
        <div style={{ fontSize: 10.5, fontFamily: 'ui-monospace, monospace', color: c.t4, marginBottom: 6, letterSpacing: '0.04em' }}>
          cardeep.eu · API v1
        </div>
        <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: '-0.02em', color: c.t1, lineHeight: 1, marginBottom: 4 }}>
          API & Tokens
        </h1>
        <p style={{ fontSize: 11.5, color: c.t4 }}>
          Sell and consume cardeep data via API — billed per token, deducted on success only.
        </p>
      </motion.div>

      {/* Bento grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>

        {/* Row 1 — KPI cards */}
        {kpiCards.map(card => (
          <KpiCard key={card.label} {...card} />
        ))}

        {/* Row 2 — Endpoints (2 cols) + Consumption chart (2 cols) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 3', gridRow: '2', minHeight: 320 }}
        >
          <EndpointCatalog dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.28, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '3 / 5', gridRow: '2', minHeight: 320 }}
        >
          <ConsumptionChart dark={dark} />
        </motion.div>

        {/* Row 3 — API Keys (2 cols) + Plans (2 cols) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.34, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 3', gridRow: '3' }}
        >
          <ApiKeysPanel dark={dark} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.38, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '3 / 5', gridRow: '3' }}
        >
          <PlansPanel dark={dark} />
        </motion.div>

        {/* Row 4 — Code example (full width) */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.44, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
          style={{ gridColumn: '1 / 5', gridRow: '4' }}
        >
          <CodeExample dark={dark} />
        </motion.div>

      </div>
    </div>
  )
}
