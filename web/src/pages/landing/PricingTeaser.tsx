import { Check, ArrowUpRight } from 'lucide-react'
import CinematicReveal from './CinematicReveal'

// Reference pattern ("Extensive Pricing Plans"): 2-col equal grid, one light
// card + one dark/featured card, gap-24/radius-24. Round 2 addition
// (2026-07-24) — Round 1's spec flagged this section as "omitted so far,
// could add a compact teaser" and it never got built. Numbers and feature
// copy are pulled 1:1 from Pricing.tsx's real PLANS (Starter/Scale/
// Enterprise) — no new claim invented here, just a shorter cut of the real
// plan copy for a landing-page teaser. Full detail lives at /pricing.
const STARTER_FEATURES = [
  'Inventario, CRM, pipeline, facturas — sin límite',
  'Ficha de vehículo: specs, VIN, precio de lista',
  'Asistente IA, chat, calendario',
]

const SCALE_FEATURES = [
  'Precio de mercado REAL — p25/p75, no un punto modelado',
  'Delta en vivo (SEEN/GONE/Δprecio) + histórico + export',
  'Micro-geo: provincia · comarca · municipio (INE)',
]

export default function PricingTeaser() {
  return (
    <section className="px-8 py-24 md:py-28 max-w-[1440px] mx-auto">
      <CinematicReveal className="mb-14 flex flex-wrap items-end justify-between gap-6">
        <div>
          <div className="text-[13px] text-[color:var(--cx-text-3)]">Precios</div>
          <h2 className="font-semibold text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[20ch] text-[color:var(--cx-text-1)]">
            Starter es gratis. Scale es el diferencial.
          </h2>
        </div>
        <a
          href="/pricing"
          className="inline-flex items-center gap-2.5 rounded-lg bg-[color:var(--cx-ink)] pl-[3px] pr-4 py-[3px] text-[14px] font-medium text-white"
        >
          <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
            <ArrowUpRight size={14} />
          </span>
          Ver los 3 planes
        </a>
      </CinematicReveal>

      <CinematicReveal stagger className="grid gap-6 md:grid-cols-2">
        <div className="cx-panel rounded-[24px] p-8 flex flex-col gap-6">
          <div>
            <div className="font-semibold text-lg text-[color:var(--cx-text-1)]">Starter</div>
            <p className="mt-1.5 text-[13px] leading-relaxed text-[color:var(--cx-text-2)]">
              El CRM completo del dealer + ficha básica de vehículo. Entrada sin fricción.
            </p>
          </div>
          <div className="font-semibold text-[2.4rem] tracking-[-0.02em] leading-none text-[color:var(--cx-text-1)]">
            0€ <span className="text-sm font-medium text-[color:var(--cx-text-3)]">/mes, sin tarjeta</span>
          </div>
          <ul className="flex flex-col gap-2.5">
            {STARTER_FEATURES.map((f) => (
              <li key={f} className="flex items-start gap-2.5 text-[13px] leading-relaxed text-[color:var(--cx-text-2)]">
                <Check size={15} style={{ color: 'var(--cx-emerald)' }} className="shrink-0 mt-0.5" />
                {f}
              </li>
            ))}
          </ul>
          <a href="/register" className="mt-auto text-[13.5px] font-medium underline" style={{ color: 'var(--cx-accent-hi)' }}>
            Empezar gratis
          </a>
        </div>

        <div className="cx-panel-dark relative rounded-[24px] p-8 flex flex-col gap-6">
          <span
            className="absolute -top-3 left-8 rounded-full px-2.5 py-1 text-[11px] font-bold text-[color:var(--cx-ink)]"
            style={{ background: 'var(--cx-badge)' }}
          >
            El hook
          </span>
          <div>
            <div className="font-semibold text-lg text-white">Scale</div>
            <p className="mt-1.5 text-[13px] leading-relaxed text-[color:var(--cx-text-on-dark-2)]">
              El diferencial que cardeep puede poseer y nadie más: censo vivo, no muestra.
            </p>
          </div>
          <div className="font-semibold text-[2.4rem] tracking-[-0.02em] leading-none text-white">
            199€ <span className="text-sm font-medium text-[color:var(--cx-text-on-dark-3)]">/mes en anual</span>
          </div>
          <ul className="flex flex-col gap-2.5">
            {SCALE_FEATURES.map((f) => (
              <li key={f} className="flex items-start gap-2.5 text-[13px] leading-relaxed text-[color:var(--cx-text-on-dark-2)]">
                <Check size={15} style={{ color: 'var(--cx-badge)' }} className="shrink-0 mt-0.5" />
                {f}
              </li>
            ))}
          </ul>
          <a
            href="/pricing"
            className="mt-auto inline-flex items-center gap-2.5 self-start rounded-lg bg-black pl-[3px] pr-4 py-[3px] text-[13.5px] font-medium text-white border border-white/10"
          >
            <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
              <ArrowUpRight size={13} />
            </span>
            Empezar prueba
          </a>
        </div>
      </CinematicReveal>

      <p className="mt-6 text-[13px] text-[color:var(--cx-text-3)]">
        Enterprise (arbitrage y sourcing completo, a medida) —{' '}
        <a href="/pricing" className="underline" style={{ color: 'var(--cx-accent-hi)' }}>
          ver detalle
        </a>
        .
      </p>
    </section>
  )
}
