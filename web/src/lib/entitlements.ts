import type { Plan } from '../types'

/**
 * Feature gating derived from plans/frontend-definitivo/05-MONETIZATION-MAP.md.
 * Capa 0 (dealer's own data) is never gated. Capa 1 features require 'scale'
 * (the hook — market intelligence). Capa 2 features require 'enterprise'
 * (the recurring premium — arbitrage/sourcing).
 */
export type Feature =
  | 'market-position-detail'   // Capa 1 — distribución completa, tendencia histórica
  | 'delta-feed-full'          // Capa 1 — feed completo de SEEN/GONE/Δprecio + export
  | 'micro-geo-detail'         // Capa 1 — desglose provincia/comarca/municipio
  | 'cross-border-compare'     // Capa 1 — comparativa residual cross-country
  | 'deal-score-breakdown'     // Capa 2 — desglose del deal-score
  | 'sourcing-ranking'         // Capa 2 — ranking completo de chollos + filtros
  | 'arbitrage-alerts'         // Capa 2 — alertas push
  | 'flip-calculator'          // Capa 2 — calculadora de ROI

const PLAN_RANK: Record<Plan, number> = { starter: 0, scale: 1, enterprise: 2 }

const REQUIRED_PLAN: Record<Feature, Plan> = {
  'market-position-detail': 'scale',
  'delta-feed-full':        'scale',
  'micro-geo-detail':       'scale',
  'cross-border-compare':   'scale',
  'deal-score-breakdown':   'enterprise',
  'sourcing-ranking':       'enterprise',
  'arbitrage-alerts':       'enterprise',
  'flip-calculator':        'enterprise',
}

export function hasFeature(userPlan: Plan, feature: Feature): boolean {
  return PLAN_RANK[userPlan] >= PLAN_RANK[REQUIRED_PLAN[feature]]
}

export function requiredPlan(feature: Feature): Plan {
  return REQUIRED_PLAN[feature]
}

export const PLAN_LABEL: Record<Plan, string> = {
  starter: 'Starter',
  scale: 'Scale',
  enterprise: 'Enterprise',
}
