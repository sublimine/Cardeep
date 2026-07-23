import CinematicReveal from './CinematicReveal'
import CountUp from '../../components/landing/CountUp'
import type { Stats } from '../../api/cardeep'
import type { MarketCoverage } from '../../api/useCardeepStats'

interface StatsBandProps {
  stats: Stats | null
  coverage: MarketCoverage | null
}

/**
 * Reference pattern ("Scaling Successful Companies"): one big featured-stat
 * card next to a stack of smaller supporting numbers, not a flat row — the
 * asymmetry is real weight, not decoration. Coverage% is the featured card
 * since it's cardeep's actual differentiator (censo completo vs. muestra).
 */
export default function StatsBand({ stats, coverage }: StatsBandProps) {
  const small = [
    { node: stats ? <CountUp value={stats.dealers} /> : '—', label: 'puntos de venta indexados' },
    { node: stats ? <CountUp value={stats.vehicles_unique_available} /> : '—', label: 'coches vivos en el índice' },
    { node: stats ? <CountUp value={stats.provinces} /> : '—', label: 'provincias con censo completo' },
  ]

  return (
    <section className="px-7 md:px-12 py-24 md:py-28 max-w-[1200px] mx-auto">
      <div className="grid gap-4 md:grid-cols-[1.3fr_1fr]">
        <CinematicReveal className="cx-panel-dark rounded-[24px] p-8 md:p-10 flex flex-col justify-between min-h-[280px]">
          <div className="cx-mono text-[11px] uppercase tracking-[.16em] text-[color:var(--cx-text-on-dark-3)]">
            Cobertura verificada, no estimada
          </div>
          <div>
            <div className="font-black cx-mono text-[clamp(3.4rem,9vw,6.4rem)] leading-none tracking-[-0.03em] text-white">
              {coverage ? <CountUp value={Math.round(coverage.coveragePct)} /> : '—'}
              <span className="text-[0.4em] align-top">%</span>
            </div>
            <p className="mt-4 max-w-[42ch] text-sm leading-relaxed text-[color:var(--cx-text-on-dark-2)]">
              Donde ellos muestran una muestra, nosotros mostramos el censo entero — auditado provincia a provincia,
              no una proyección.
            </p>
          </div>
        </CinematicReveal>

        <div className="grid gap-4">
          {small.map((item) => (
            <CinematicReveal key={item.label} className="cx-panel rounded-[20px] p-6 flex flex-col justify-center flex-1">
              <div className="cx-mono font-bold text-[clamp(1.8rem,3vw,2.4rem)] tracking-[-0.02em] leading-none text-[color:var(--cx-text-1)]">
                {item.node}
              </div>
              <div className="cx-mono text-[11px] uppercase tracking-[.08em] text-[color:var(--cx-text-3)] mt-2">{item.label}</div>
            </CinematicReveal>
          ))}
        </div>
      </div>
    </section>
  )
}
