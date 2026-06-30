// Pricing — Subscription plan selector with monthly/annual toggle
// Pattern: tok() + GCard (mirrors Dashboard.tsx)

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Check, Zap, Star, BarChart2, Building, ArrowRight } from 'lucide-react'

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

// ── Plan data ─────────────────────────────────────────────────────────────────

interface Plan {
  id: string
  name: string
  Icon: React.ElementType
  monthlyPrice: number | null
  annualPrice: number | null
  description: string
  features: string[]
  cta: string
  highlighted: boolean
  badge: string | null
  accent: string
}

const PLANS: Plan[] = [
  {
    id: 'starter',
    name: 'Starter',
    Icon: Zap,
    monthlyPrice: 49,
    annualPrice: 39,
    description: 'For small dealers getting started with smart vehicle intelligence.',
    features: [
      'Up to 50 vehicles in stock',
      '100 VIN / plate checks per month',
      'Basic P&L tracking',
      'Deal pipeline (Kanban)',
      '1 user seat',
      'Email support',
      'Mobile-ready dashboard',
    ],
    cta: 'Start free trial',
    highlighted: false,
    badge: null,
    accent: '#64748b',
  },
  {
    id: 'pro',
    name: 'Pro',
    Icon: Star,
    monthlyPrice: 129,
    annualPrice: 99,
    description: 'The go-to plan for growing dealers with active multi-source pipelines.',
    features: [
      'Up to 250 vehicles in stock',
      '500 VIN / plate checks per month',
      'Full P&L, cashflow & margin reports',
      'Invoice management',
      '5 user seats',
      'Priority support (4h SLA)',
      'API access',
      'Multi-portal integrations',
    ],
    cta: 'Get started',
    highlighted: true,
    badge: 'Most popular',
    accent: '#3b82f6',
  },
  {
    id: 'scale',
    name: 'Scale',
    Icon: BarChart2,
    monthlyPrice: 249,
    annualPrice: 199,
    description: 'For high-volume dealers and groups needing advanced analytics.',
    features: [
      'Up to 1,000 vehicles in stock',
      'Unlimited VIN / plate checks',
      'Advanced analytics & benchmarking',
      'Multi-location support',
      '20 user seats',
      'Dedicated account manager',
      'Custom integrations',
      'Audit logs & compliance exports',
    ],
    cta: 'Get started',
    highlighted: false,
    badge: null,
    accent: '#0891b2',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    Icon: Building,
    monthlyPrice: null,
    annualPrice: null,
    description: 'Custom solutions for dealer groups, OEMs, and leasing operators.',
    features: [
      'Unlimited vehicles & checks',
      'Unlimited user seats',
      'Custom data feeds & ETL',
      'On-premise deployment option',
      'SLA up to 99.99% uptime',
      'Custom AI model training',
      'Legal & compliance support',
      'Dedicated infrastructure',
    ],
    cta: 'Contact sales',
    highlighted: false,
    badge: 'Custom',
    accent: '#059669',
  },
]

// Annual saving on the Pro plan (most visible): (129 - 99) / 129 ≈ 23%
const ANNUAL_SAVING_PCT = Math.round(((129 - 99) / 129) * 100)

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Pricing() {
  const dark = useIsDark()
  const c = tok(dark)
  const [annual, setAnnual] = useState(true)

  return (
    <div
      style={{
        padding: 'clamp(16px, 3vw, 28px)',
        maxWidth: 1200,
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 28,
      }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.38 }}
        style={{ textAlign: 'center', maxWidth: 560, margin: '0 auto' }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 12px',
            borderRadius: 99,
            background: 'rgba(59,130,246,0.10)',
            border: '1px solid rgba(59,130,246,0.22)',
            fontSize: 11,
            fontWeight: 600,
            color: '#3b82f6',
            marginBottom: 16,
          }}
        >
          Subscription plans
        </div>
        <h1
          style={{
            fontSize: 28,
            fontWeight: 800,
            letterSpacing: '-0.04em',
            color: c.t1,
            lineHeight: 1.15,
            marginBottom: 10,
          }}
        >
          The intelligence layer for EU car dealers
        </h1>
        <p style={{ fontSize: 13, color: c.t3, lineHeight: 1.6 }}>
          From small garages to large dealer groups — pick the plan that matches your operation
          and scale at any time.
        </p>
      </motion.div>

      {/* Monthly / Annual toggle */}
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.10, duration: 0.35 }}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}
      >
        <span
          style={{ fontSize: 12, fontWeight: 600, color: !annual ? c.t1 : c.t4 }}
        >
          Monthly
        </span>

        <button
          onClick={() => setAnnual((a) => !a)}
          aria-label="Toggle billing period"
          style={{
            width: 44,
            height: 24,
            borderRadius: 99,
            border: 'none',
            cursor: 'pointer',
            background: annual
              ? '#3b82f6'
              : dark
              ? 'rgba(255,255,255,0.12)'
              : 'rgba(0,0,0,0.12)',
            position: 'relative',
            transition: 'background 200ms',
            padding: 0,
            flexShrink: 0,
          }}
        >
          <motion.span
            animate={{ x: annual ? 22 : 2 }}
            transition={{ type: 'spring', stiffness: 380, damping: 28 }}
            style={{
              display: 'block',
              width: 18,
              height: 18,
              borderRadius: '50%',
              background: '#fff',
              position: 'absolute',
              top: 3,
              boxShadow: '0 1px 4px rgba(0,0,0,0.22)',
            }}
          />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: annual ? c.t1 : c.t4 }}>
            Annual
          </span>
          {annual && (
            <motion.span
              key="saving"
              initial={{ opacity: 0, scale: 0.80 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.80 }}
              transition={{ duration: 0.22 }}
              style={{
                padding: '2px 8px',
                borderRadius: 99,
                background: 'rgba(5,150,105,0.14)',
                border: '1px solid rgba(5,150,105,0.25)',
                fontSize: 10,
                fontWeight: 700,
                color: '#059669',
              }}
            >
              Save {ANNUAL_SAVING_PCT}%
            </motion.span>
          )}
        </div>
      </motion.div>

      {/* Plan cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 16,
          alignItems: 'start',
        }}
      >
        {PLANS.map((plan, i) => {
          const { Icon } = plan
          const price = annual ? plan.annualPrice : plan.monthlyPrice
          const hl = plan.highlighted

          return (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.16 + i * 0.08, duration: 0.40, ease: [0.32, 0.72, 0, 1] }}
              whileHover={{ y: -3, transition: { duration: 0.20 } }}
              style={{ position: 'relative' }}
            >
              {/* Badge */}
              {plan.badge && (
                <div
                  style={{
                    position: 'absolute',
                    top: -11,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    padding: '3px 10px',
                    borderRadius: 99,
                    zIndex: 1,
                    background: hl
                      ? '#3b82f6'
                      : dark
                      ? 'rgba(255,255,255,0.12)'
                      : 'rgba(0,0,0,0.09)',
                    fontSize: 10,
                    fontWeight: 700,
                    color: hl ? '#fff' : c.t3,
                    border: hl
                      ? 'none'
                      : `1px solid ${dark ? 'rgba(255,255,255,0.14)' : 'rgba(0,0,0,0.10)'}`,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {plan.badge}
                </div>
              )}

              {/* Card body */}
              <div
                style={{
                  background: hl
                    ? dark
                      ? 'rgba(59,130,246,0.09)'
                      : 'rgba(255,255,255,0.96)'
                    : dark
                    ? 'rgba(255,255,255,0.04)'
                    : 'rgba(255,255,255,0.82)',
                  border: hl
                    ? '1.5px solid rgba(59,130,246,0.45)'
                    : `1px solid ${dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
                  borderRadius: 16,
                  backdropFilter: 'blur(24px) saturate(180%)',
                  WebkitBackdropFilter: 'blur(24px) saturate(180%)',
                  boxShadow: hl
                    ? '0 8px 32px rgba(59,130,246,0.18), inset 0 1px 0 rgba(255,255,255,0.10)'
                    : dark
                    ? '0 4px 24px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.07)'
                    : '0 4px 20px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.90)',
                  padding: '24px 22px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 20,
                }}
              >
                {/* Plan identity */}
                <div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      marginBottom: 12,
                    }}
                  >
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: 10,
                        background: `${plan.accent}18`,
                        border: `1px solid ${plan.accent}28`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <Icon style={{ width: 16, height: 16, color: plan.accent }} />
                    </div>
                    <span style={{ fontSize: 15, fontWeight: 700, color: c.t1 }}>
                      {plan.name}
                    </span>
                  </div>
                  <p style={{ fontSize: 11.5, color: c.t3, lineHeight: 1.55 }}>
                    {plan.description}
                  </p>
                </div>

                {/* Price */}
                <div>
                  {price !== null ? (
                    <>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
                        <span
                          style={{
                            fontSize: 13,
                            fontWeight: 700,
                            color: c.t3,
                            alignSelf: 'flex-start',
                            marginTop: 7,
                          }}
                        >
                          €
                        </span>
                        <motion.span
                          key={price}
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.20 }}
                          style={{
                            fontSize: 40,
                            fontWeight: 800,
                            letterSpacing: '-0.04em',
                            color: c.t1,
                            lineHeight: 1,
                            fontVariantNumeric: 'tabular-nums',
                          }}
                        >
                          {price}
                        </motion.span>
                        <span style={{ fontSize: 12, color: c.t4, marginLeft: 3 }}>/mo</span>
                      </div>
                      {annual && (
                        <p style={{ fontSize: 10, color: c.t4, marginTop: 4 }}>
                          Billed €{(price * 12).toLocaleString()} / year
                        </p>
                      )}
                    </>
                  ) : (
                    <div
                      style={{
                        fontSize: 26,
                        fontWeight: 800,
                        letterSpacing: '-0.03em',
                        color: c.t1,
                        lineHeight: 1,
                      }}
                    >
                      Custom
                    </div>
                  )}
                </div>

                {/* Feature list */}
                <div
                  style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 7,
                  }}
                >
                  {plan.features.map((feat) => (
                    <div
                      key={feat}
                      style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}
                    >
                      <Check
                        style={{
                          width: 12,
                          height: 12,
                          color: plan.accent,
                          marginTop: 2,
                          flexShrink: 0,
                        }}
                      />
                      <span style={{ fontSize: 11.5, color: c.t2, lineHeight: 1.45 }}>
                        {feat}
                      </span>
                    </div>
                  ))}
                </div>

                {/* CTA button */}
                <PlanButton highlighted={hl} dark={dark} c={c} label={plan.cta} />
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Footer note */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.55, duration: 0.35 }}
        style={{
          textAlign: 'center',
          fontSize: 11.5,
          color: c.t4,
          lineHeight: 1.6,
        }}
      >
        All plans include a 14-day free trial. No credit card required. Questions?{' '}
        <a
          href="mailto:sales@cardeep.io"
          style={{ color: '#3b82f6', textDecoration: 'none' }}
        >
          sales@cardeep.io
        </a>
      </motion.p>
    </div>
  )
}

// ── Sub-component: plan CTA button ────────────────────────────────────────────

function PlanButton({
  highlighted,
  dark,
  c,
  label,
}: {
  highlighted: boolean
  dark: boolean
  c: ReturnType<typeof tok>
  label: string
}) {
  const [hovered, setHovered] = useState(false)

  const bg = highlighted
    ? hovered
      ? '#2563eb'
      : '#3b82f6'
    : hovered
    ? dark
      ? 'rgba(255,255,255,0.08)'
      : 'rgba(0,0,0,0.05)'
    : 'transparent'

  return (
    <button
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: '100%',
        padding: '9px 16px',
        borderRadius: 9,
        fontSize: 12,
        fontWeight: 700,
        cursor: 'pointer',
        fontFamily: 'General Sans, Inter, system-ui',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        background: bg,
        border: highlighted
          ? 'none'
          : `1.5px solid ${dark ? 'rgba(255,255,255,0.14)' : 'rgba(0,0,0,0.14)'}`,
        color: highlighted ? '#fff' : hovered ? c.t1 : c.t2,
        boxShadow: highlighted ? '0 4px 14px rgba(59,130,246,0.32)' : 'none',
        transition: 'background 160ms, color 160ms',
      }}
    >
      {label}
      <ArrowRight style={{ width: 12, height: 12 }} />
    </button>
  )
}
