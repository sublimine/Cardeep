import React from 'react'
import { Lock } from 'lucide-react'
import Button from './Button'
import { hasFeature, requiredPlan, PLAN_LABEL, type Feature } from '../lib/entitlements'
import type { Plan } from '../types'
import { useNavigate } from 'react-router-dom'

interface PremiumGateProps {
  feature: Feature
  userPlan: Plan
  /** Short label for the lock CTA, e.g. "distribución completa" */
  what: string
  children: React.ReactNode
}

/**
 * Wraps Capa-1/Capa-2 content (plans/frontend-definitivo/05-MONETIZATION-MAP.md).
 * Unlocked: renders children as-is. Locked: children render blurred underneath
 * a centered upgrade card — the teaser, never the raw data.
 */
export default function PremiumGate({ feature, userPlan, what, children }: PremiumGateProps) {
  const navigate = useNavigate()
  if (hasFeature(userPlan, feature)) return <>{children}</>

  const plan = requiredPlan(feature)

  return (
    <div className="relative h-full">
      {/*
        h-full on both wrappers matters: recharts' ResponsiveContainer sizes
        itself to 100% of its parent chain, so an extra div here without an
        explicit height silently collapses gated charts to 0px.
      */}
      <div className="pointer-events-none h-full select-none blur-[6px] opacity-60" aria-hidden>
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center p-3">
        <div
          className="flex flex-col items-center gap-2 rounded-xl border px-5 py-4 text-center max-w-[220px]"
          style={{
            background: 'var(--glass-lg)',
            borderColor: 'var(--border-default)',
            boxShadow: 'var(--shadow-card)',
          }}
        >
          <div
            className="flex h-8 w-8 items-center justify-center rounded-full"
            style={{ background: 'rgba(59,130,246,0.14)', border: '1px solid rgba(59,130,246,0.28)' }}
          >
            <Lock className="h-3.5 w-3.5" style={{ color: 'var(--c-violet)' }} />
          </div>
          <p className="text-[11.5px] font-medium" style={{ color: 'var(--t2)' }}>{what}</p>
          <Button size="sm" onClick={() => navigate('/pricing')}>
            Desbloquear con {PLAN_LABEL[plan]}
          </Button>
        </div>
      </div>
    </div>
  )
}
