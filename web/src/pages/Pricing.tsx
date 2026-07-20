// Pricing — plans reflect the real product (05-MONETIZATION-MAP.md's Capa 0/1/2
// model, from the 109-company intelligence audit), not generic per-seat SaaS
// tiers. 3 plans, matching types.ts' Plan exactly: starter/scale/enterprise.

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, Zap, BarChart2, Building, ArrowRight } from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import { ACCENT, GOOD } from '../lib/theme'

interface PricingPlan {
  id: 'starter' | 'scale' | 'enterprise'
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

const PLANS: PricingPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    Icon: Zap,
    monthlyPrice: 0,
    annualPrice: 0,
    description: 'El CRM completo del dealer + ficha básica de vehículo. Entrada sin fricción.',
    features: [
      'Inventario, CRM, pipeline, facturas — sin límite',
      'Ficha de vehículo: specs, VIN, precio de lista',
      '1 métrica de mercado agregada (precio vs mediana, días en stock)',
      'Historial resumen (nº de eventos, sin detalle)',
      'Asistente IA, chat, calendario',
      '1 puesto de usuario',
    ],
    cta: 'Empezar gratis',
    highlighted: false,
    badge: null,
    accent: '#64748b',
  },
  {
    id: 'scale',
    name: 'Scale',
    Icon: BarChart2,
    monthlyPrice: 249,
    annualPrice: 199,
    description: 'El diferencial que cardeep puede poseer y nadie más: censo vivo, no muestra.',
    features: [
      'Todo lo de Starter',
      'Precio de mercado REAL — distribución completa p25/p75, no un punto modelado',
      'Delta en vivo completo (SEEN/GONE/Δprecio) + histórico + export',
      'Micro-geo: provincia · comarca · municipio (INE)',
      'Comparativa cross-border (España vs UE / DE)',
      'Dossier VIN completo con histórico detallado',
      'Provenance verificado (VAM) — dato auditable, no opaco',
      '5 puestos de usuario',
    ],
    cta: 'Empezar prueba',
    highlighted: true,
    badge: 'El hook',
    accent: ACCENT,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    Icon: Building,
    monthlyPrice: null,
    annualPrice: null,
    description: 'Arbitrage completo — el billete recurrente. Compra-venta con inteligencia accionable.',
    features: [
      'Todo lo de Scale',
      'Deal-score desglosado por anuncio (vs mercado/días/Δ/cross-platform)',
      'Sourcing: ranking completo de chollos, filtros margen/zona/segmento',
      'Alertas push de chollos en tiempo real',
      'Spread wholesale→retail (en cuanto exista feed de partner)',
      'API & Tokens — cuota alta, INFO + INVENTORY',
      'Cuenta manager dedicado',
      'Puestos de usuario ilimitados',
    ],
    cta: 'Hablar con ventas',
    highlighted: false,
    badge: 'A medida',
    accent: GOOD,
  },
]

const ANNUAL_SAVING_PCT = Math.round(((249 - 199) / 249) * 100)

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Pricing() {
  const [annual, setAnnual] = useState(true)

  return (
    <div className="mx-auto flex flex-col gap-7" style={{ padding: 'clamp(16px, 3vw, 28px)', maxWidth: 1200 }}>

      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.38 }}
        className="mx-auto text-center"
        style={{ maxWidth: 620 }}
      >
        <div
          className="mb-4 inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[11px] font-semibold"
          style={{ background: `${ACCENT}1a`, border: `1px solid ${ACCENT}38`, color: ACCENT }}
        >
          Inteligencia de mercado, no software de asientos
        </div>
        <h1 className="mb-2.5 text-[28px] font-extrabold leading-[1.15] tracking-[-0.04em]" style={{ color: 'var(--text-primary)' }}>
          El censo vivo del mercado, verificado — no estimado
        </h1>
        <p className="text-[13px] leading-[1.6]" style={{ color: 'var(--text-secondary)' }}>
          Starter es gratis para operar tu negocio. Se paga por lo que ningún competidor tiene: precio de
          mercado real, delta en vivo, y arbitrage sobre el 100% del censo — no una muestra.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.10, duration: 0.35 }}
        className="flex items-center justify-center gap-3"
      >
        <span className="text-xs font-semibold" style={{ color: !annual ? 'var(--text-primary)' : 'var(--text-muted)' }}>Mensual</span>

        <motion.button
          onClick={() => setAnnual(a => !a)}
          whileTap={{ scale: 0.94 }}
          aria-label="Cambiar periodo de facturación"
          className="relative h-6 w-11 shrink-0 cursor-pointer rounded-full border-0 p-0 transition-colors"
          style={{ background: annual ? ACCENT : 'var(--border-active)' }}
        >
          <motion.span
            animate={{ x: annual ? 22 : 2 }}
            transition={{ type: 'spring', stiffness: 380, damping: 28 }}
            className="absolute block h-[18px] w-[18px] rounded-full bg-white"
            style={{ top: 3, boxShadow: '0 1px 4px rgba(0,0,0,0.22)' }}
          />
        </motion.button>

        <div className="flex items-center gap-[7px]">
          <span className="text-xs font-semibold" style={{ color: annual ? 'var(--text-primary)' : 'var(--text-muted)' }}>Anual</span>
          {annual && (
            <motion.span
              key="saving"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.22 }}
              className="rounded-full px-2 py-0.5 text-[10px] font-bold"
              style={{ background: `${GOOD}24`, border: `1px solid ${GOOD}40`, color: GOOD }}
            >
              Ahorra {ANNUAL_SAVING_PCT}%
            </motion.span>
          )}
        </div>
      </motion.div>

      <div className="grid items-start gap-4" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        {PLANS.map((plan, i) => {
          const { Icon } = plan
          const price = annual ? plan.annualPrice : plan.monthlyPrice
          const hl = plan.highlighted

          return (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.16 + i * 0.08, duration: 0.4, ease: [0.32, 0.72, 0, 1] }}
              className="relative"
            >
              {plan.badge && (
                <div
                  className="absolute left-1/2 z-10 whitespace-nowrap rounded-full px-2.5 py-[3px] text-[10px] font-bold"
                  style={{
                    top: -11, transform: 'translateX(-50%)',
                    background: hl ? ACCENT : 'var(--bg-elevated)',
                    color: hl ? '#fff' : 'var(--text-secondary)',
                    border: hl ? 'none' : '1px solid var(--border-default)',
                  }}
                >
                  {plan.badge}
                </div>
              )}

              <Card
                hover
                glow={hl}
                className="flex flex-col gap-5"
                style={hl ? { borderColor: `${ACCENT}73`, borderWidth: 1.5, boxShadow: `0 8px 32px ${ACCENT}2e` } as React.CSSProperties : undefined}
              >
                <div>
                  <div className="mb-3 flex items-center gap-2.5">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px]" style={{ background: `${plan.accent}18`, border: `1px solid ${plan.accent}28` }}>
                      <Icon style={{ width: 16, height: 16, color: plan.accent }} />
                    </div>
                    <span className="text-[15px] font-bold" style={{ color: 'var(--text-primary)' }}>{plan.name}</span>
                  </div>
                  <p className="text-[11.5px] leading-[1.55]" style={{ color: 'var(--text-secondary)' }}>{plan.description}</p>
                </div>

                <div>
                  {price !== null ? (
                    <>
                      <div className="flex items-baseline gap-0.5">
                        <span className="self-start text-[13px] font-bold" style={{ color: 'var(--text-secondary)', marginTop: 7 }}>€</span>
                        <motion.span
                          key={price}
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.2 }}
                          className="text-[40px] font-extrabold leading-none tracking-[-0.04em] tabular-nums"
                          style={{ color: 'var(--text-primary)' }}
                        >
                          {price}
                        </motion.span>
                        <span className="ml-[3px] text-xs" style={{ color: 'var(--text-muted)' }}>/mes</span>
                      </div>
                      {annual && price > 0 && (
                        <p className="mt-1 text-[10px] tabular-nums" style={{ color: 'var(--text-muted)' }}>Facturado €{(price * 12).toLocaleString()} / año</p>
                      )}
                      {price === 0 && <p className="mt-1 text-[10px]" style={{ color: 'var(--text-muted)' }}>Gratis, sin tarjeta</p>}
                    </>
                  ) : (
                    <div className="text-[26px] font-extrabold leading-none tracking-[-0.03em]" style={{ color: 'var(--text-primary)' }}>A medida</div>
                  )}
                </div>

                <div className="flex flex-1 flex-col gap-[7px]">
                  {plan.features.map(feat => (
                    <div key={feat} className="flex items-start gap-2">
                      <Check style={{ width: 12, height: 12, color: plan.accent, marginTop: 2, flexShrink: 0 }} />
                      <span className="text-[11.5px] leading-[1.45]" style={{ color: 'var(--text-secondary)' }}>{feat}</span>
                    </div>
                  ))}
                </div>

                <Button variant={hl ? 'primary' : 'secondary'} className="w-full">
                  {plan.cta}
                  <ArrowRight className="h-3 w-3" />
                </Button>
              </Card>
            </motion.div>
          )
        })}
      </div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.55, duration: 0.35 }}
        className="text-center text-[11.5px] leading-[1.6]"
        style={{ color: 'var(--text-muted)' }}
      >
        Scale y Enterprise incluyen 14 días de prueba. Sin tarjeta para Starter. ¿Dudas?{' '}
        <a href="mailto:sales@cardeep.io" style={{ color: ACCENT, textDecoration: 'none' }}>sales@cardeep.io</a>
      </motion.p>
    </div>
  )
}
