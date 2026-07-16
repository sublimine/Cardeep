import CinematicReveal from './CinematicReveal'
import CountUp from '../../components/landing/CountUp'
import type { Stats } from '../../api/cardeep'
import type { MarketCoverage } from '../../api/useCardeepStats'

interface TrustStripProps {
  stats: Stats | null
  coverage: MarketCoverage | null
}

/**
 * Deliberately does NOT repeat dealers/vehicles (already the hero's KPI row —
 * see `LandingHero.tsx`). Surfaces the two real numbers that live only here:
 * verified market coverage and province reach, as a "command readout" band
 * instead of a second copy of the same stat strip.
 */
export default function TrustStrip({ stats, coverage }: TrustStripProps) {
  return (
    <section className="px-7 md:px-12 py-24 border-y" style={{ borderColor: 'var(--cx-line)' }}>
      <div className="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_auto] gap-10 items-center">
        <CinematicReveal>
          <div className="cx-mono text-[12px] uppercase tracking-[.2em] text-[color:var(--cx-accent-hi)] mb-4">
            Cobertura verificada, no estimada
          </div>
          <p className="font-medium text-[clamp(1.3rem,2.4vw,2rem)] leading-[1.25] max-w-[26ch] text-[color:var(--cx-text-1)]">
            Donde ellos muestran una muestra, nosotros mostramos el censo entero — auditado provincia a provincia.
          </p>
        </CinematicReveal>

        <CinematicReveal delay={0.15} stagger className="flex gap-10 md:gap-14">
          <div>
            <div className="font-black text-[clamp(2.2rem,4vw,3.4rem)] tracking-[-0.03em] leading-none" style={{ color: 'var(--cx-accent-hi)' }}>
              {coverage ? <CountUp value={Math.round(coverage.coveragePct)} className="cx-mono" /> : '—'}
              <span className="text-[0.5em] align-top">%</span>
            </div>
            <div className="cx-mono text-[11px] uppercase tracking-[.1em] text-[color:var(--cx-text-3)] mt-2">cobertura del mercado</div>
          </div>
          <div>
            <div className="font-black text-[clamp(2.2rem,4vw,3.4rem)] tracking-[-0.03em] leading-none text-[color:var(--cx-text-1)]">
              {stats ? <CountUp value={stats.provinces} className="cx-mono" /> : '—'}
            </div>
            <div className="cx-mono text-[11px] uppercase tracking-[.1em] text-[color:var(--cx-text-3)] mt-2">provincias auditadas</div>
          </div>
        </CinematicReveal>
      </div>
    </section>
  )
}
