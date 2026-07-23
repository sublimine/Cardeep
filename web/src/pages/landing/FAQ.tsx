import { useState } from 'react'
import { ChevronDown, ArrowUpRight } from 'lucide-react'
import CinematicReveal from './CinematicReveal'

interface QA {
  q: string
  a: string
}

// Real, defensible answers only — sourced from the actual product surface
// (Pricing.tsx plans, entitlements.ts gating, ComparisonBand's real claims).
// No invented capability.
const ITEMS: QA[] = [
  {
    q: '¿Qué es cardeep exactamente?',
    a: 'El índice nacional del mercado de coches de ocasión en España: indexamos cada plataforma y punto de venta, no una muestra, y lo mantenemos vivo con delta continuo (altas, bajas, cambios de precio).',
  },
  {
    q: '¿Puedo consultar un vehículo gratis?',
    a: 'Sí. El plan Starter (gratis, sin tarjeta) incluye ficha técnica, VIN y precio de lista de cualquier vehículo indexado. La inteligencia de mercado completa (price-position, delta en vivo, micro-geografía) es del plan Scale.',
  },
  {
    q: '¿De dónde salen los datos?',
    a: 'Cosecha propia sobre las plataformas reales del mercado español (Coches.net, AutoScout24, Wallapop, Milanuncios, Coches.com, Autocasion, Motor.es y ~50 fuentes más entre grupos, OEM y webs propias de dealer) — no un panel de terceros ni una API revendida.',
  },
  {
    q: '¿En qué se diferencia de un histórico de vehículo?',
    a: 'Un histórico te da el pasado de un coche. Cardeep te da el mercado entero en tiempo real: dónde cae ese coche frente al 100% del inventario comparable vivo, no una muestra ni una foto fija.',
  },
  {
    q: '¿Necesito saber programar para usarlo?',
    a: 'No. Todo es un panel visual. Los planes Scale/Enterprise añaden API con tokens propios para quien sí quiera integrarlo en su stack.',
  },
  {
    q: '¿Cuánto cuesta?',
    a: 'Starter es gratis para operar tu negocio. Scale (el hook de inteligencia de mercado) desde 199€/mes en anual. Enterprise, con arbitrage y sourcing completo, es a medida.',
  },
]

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0)

  return (
    <section className="px-8 py-24 md:py-28 max-w-[1440px] mx-auto">
      <div className="grid gap-10 md:grid-cols-[0.85fr_1.15fr]">
        <div>
          <CinematicReveal>
            <h2 className="font-semibold text-[clamp(2rem,4vw,3rem)] tracking-[-0.03em] leading-[1.05] text-[color:var(--cx-text-1)]">
              Preguntas frecuentes
            </h2>
            <p className="mt-3 text-sm text-[color:var(--cx-text-2)]">
              ¿Más dudas? Escríbenos a{' '}
              <a href="mailto:sales@cardeep.io" className="underline" style={{ color: 'var(--cx-accent-hi)' }}>
                sales@cardeep.io
              </a>
              .
            </p>
          </CinematicReveal>

          <CinematicReveal delay={0.1} className="cx-panel-dark rounded-[20px] p-6 mt-8">
            <div className="font-semibold text-[17px] leading-snug text-white">¿Operas puntos de venta y necesitas el censo entero?</div>
            <p className="mt-2.5 text-[13px] leading-relaxed text-[color:var(--cx-text-on-dark-2)]">
              Starter es gratis para tu inventario y CRM. El resto del mercado, en Scale.
            </p>
            <a href="/pricing" className="mt-4 inline-flex items-center gap-2 rounded-lg bg-black pl-[3px] pr-4 py-[3px] text-[13.5px] font-semibold text-white border border-white/10">
              <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
                <ArrowUpRight size={13} />
              </span>
              Ver planes
            </a>
          </CinematicReveal>
        </div>

        <CinematicReveal delay={0.15} className="cx-panel rounded-[24px] divide-y" style={{ borderColor: 'var(--cx-line)' }}>
          {ITEMS.map((item, i) => {
            const isOpen = open === i
            return (
              <div key={item.q} className="px-6 md:px-7" style={{ borderColor: 'var(--cx-line)' }}>
                <button
                  type="button"
                  onClick={() => setOpen(isOpen ? null : i)}
                  aria-expanded={isOpen}
                  className="w-full flex items-center justify-between gap-4 py-5 text-left cursor-pointer"
                >
                  <span className="font-semibold text-[15px] text-[color:var(--cx-text-1)]">{item.q}</span>
                  <ChevronDown
                    size={18}
                    className="shrink-0 transition-transform duration-300"
                    style={{ color: 'var(--cx-text-3)', transform: isOpen ? 'rotate(180deg)' : 'none' }}
                  />
                </button>
                <div
                  className="grid transition-[grid-template-rows] duration-300 ease-out"
                  style={{ gridTemplateRows: isOpen ? '1fr' : '0fr' }}
                >
                  <div className="overflow-hidden">
                    <p className="pb-5 text-[13.5px] leading-relaxed text-[color:var(--cx-text-2)] max-w-[52ch]">{item.a}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </CinematicReveal>
      </div>
    </section>
  )
}
