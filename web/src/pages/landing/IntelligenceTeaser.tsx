import { ArrowUpRight, Check, TrendingDown, Activity, MapPin } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import CinematicGate from './CinematicGate'

/**
 * Public, honest preview of the intelligence layer (`plans/intel-audit/CARDEEP-OFFERING.md`,
 * 109 empresas auditadas → 3 capas). No fabricated valuation calculator: there
 * is no live valuation endpoint (verified against `services/api/routers`), and
 * `Inteligencia.tsx` itself runs on illustrative data. Gates exactly like the
 * app does post-login (`entitlements.ts`, evaluated at the anonymous 'starter'
 * plan) instead of promising a number nobody can back up. Pattern verified at
 * autoDNA ("semáforo" preview) and Motorway/AutoTrader UK (instant tool on home).
 */
export default function IntelligenceTeaser() {
  return (
    <section className="px-7 md:px-12 py-28 max-w-[1200px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="cx-mono text-[12px] uppercase tracking-[.2em] text-[color:var(--cx-accent-hi)]">
          Inteligencia de mercado
        </div>
        <h2 className="font-black text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[18ch] text-[color:var(--cx-text-1)]">
          Lo que 109 empresas de datos venden por separado, aquí sobre el censo entero.
        </h2>
      </CinematicReveal>

      <CinematicReveal stagger className="grid md:grid-cols-3 gap-3.5">
        <div className="cx-panel cx-glow-border rounded-2xl p-6 min-h-[168px] flex flex-col">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide mb-4" style={{ color: 'var(--cx-accent-hi)' }}>
            <Check size={14} /> Incluido
          </div>
          <p className="text-sm text-[color:var(--cx-text-2)] leading-relaxed flex-1">Ficha técnica, VIN e historial básico de cualquier vehículo indexado.</p>
          <a href="/check" className="inline-flex items-center gap-1.5 text-sm font-semibold text-[color:var(--cx-text-1)] mt-4">
            Consultar un vehículo <ArrowUpRight size={14} />
          </a>
        </div>

        <CinematicGate feature="market-position-detail" what="Price-position vs. el mercado real, con distribución completa">
          <div className="cx-panel rounded-2xl p-6 min-h-[168px] flex flex-col justify-center">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide mb-4" style={{ color: 'var(--cx-emerald)' }}>
              <TrendingDown size={14} /> Price-position
            </div>
            <p className="text-sm text-[color:var(--cx-text-2)] leading-relaxed">Dónde cae este coche frente al 100% del inventario comparable vivo — no una muestra.</p>
          </div>
        </CinematicGate>

        <CinematicGate feature="delta-feed-full" what="Feed completo de altas, bajas y bajadas de precio en vivo">
          <div className="cx-panel rounded-2xl p-6 min-h-[168px] flex flex-col justify-center">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide mb-4" style={{ color: 'var(--cx-amber)' }}>
              <Activity size={14} /> Delta en vivo
            </div>
            <p className="text-sm text-[color:var(--cx-text-2)] leading-relaxed">SEEN / GONE / Δ precio por vehículo. Ningún competidor lo audita a censo completo.</p>
          </div>
        </CinematicGate>
      </CinematicReveal>

      <CinematicReveal delay={0.2} className="mt-3.5">
        <CinematicGate feature="micro-geo-detail" what="Desglose de demanda y oferta por provincia, comarca y municipio">
          <div className="cx-panel rounded-2xl p-6 min-h-[168px] flex flex-col items-center justify-center text-center gap-3">
            <MapPin size={22} style={{ color: 'var(--cx-accent-hi)' }} />
            <p className="text-sm text-[color:var(--cx-text-2)] max-w-[440px]">Micro-geografía: demanda y oferta reales por provincia → comarca → municipio, no por país.</p>
          </div>
        </CinematicGate>
      </CinematicReveal>
    </section>
  )
}
