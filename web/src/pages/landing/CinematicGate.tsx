import { Lock } from 'lucide-react'
import { hasFeature, requiredPlan, PLAN_LABEL, type Feature } from '../../lib/entitlements'

interface CinematicGateProps {
  feature: Feature
  what: string
  children: React.ReactNode
}

/**
 * Same gating logic as `components/PremiumGate.tsx` (reuses `entitlements.ts`
 * verbatim — one source of truth for what's Capa 0/1/2) but styled for the
 * dark cinematic landing instead of the light app shell. `PremiumGate` itself
 * reads `var(--glass-lg)`/`var(--border-default)` — the light app's tokens —
 * so reusing it as-is here would render a light glass card floating inside a
 * dark page. Always evaluated at the anonymous-visitor plan ('starter'), same
 * as the app shows a logged-out user.
 */
export default function CinematicGate({ feature, what, children }: CinematicGateProps) {
  if (hasFeature('starter', feature)) return <>{children}</>
  const plan = requiredPlan(feature)

  return (
    <div className="relative">
      <div className="pointer-events-none select-none blur-[7px] opacity-50" aria-hidden>
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center p-3">
        <div
          className="cx-panel flex flex-col items-center gap-2.5 rounded-xl px-5 py-4 text-center max-w-[220px]"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ background: 'rgba(59,130,246,0.16)', border: '1px solid rgba(59,130,246,0.3)' }}>
            <Lock className="h-3.5 w-3.5" style={{ color: 'var(--cx-accent-hi)' }} />
          </div>
          <p className="text-[11.5px] font-medium text-[color:var(--cx-text-2)]">{what}</p>
          <a
            href="/pricing"
            className="text-xs font-semibold text-white rounded-full px-4 py-2"
            style={{ background: 'var(--cx-accent)' }}
          >
            Desbloquear con {PLAN_LABEL[plan]}
          </a>
        </div>
      </div>
    </div>
  )
}
