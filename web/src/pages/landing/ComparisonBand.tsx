import { Check, Minus } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import type { MarketCoverage } from '../../api/useCardeepStats'

interface Row {
  label: string
  cardeep: string
  rest: string
}

const ROWS: Row[] = [
  { label: 'Cobertura del mercado', cardeep: 'El censo entero', rest: 'Solo lo publicado en su propia web' },
  { label: 'Precio de mercado', cardeep: 'Observado en vivo', rest: 'Modelado sobre muestra' },
  { label: 'Altas y bajas', cardeep: 'Delta continuo', rest: 'Foto fija, sin histórico' },
  { label: 'Duplicados entre plataformas', cardeep: 'Deduplicado por VIN/foto', rest: 'El mismo coche, varias veces' },
]

/** Patrón Carwow validado en `docs/frontend/04-COMPETITIVE-UX-AUDIT.md` §1(a)#9. */
export default function ComparisonBand({ coverage }: { coverage: MarketCoverage | null }) {
  return (
    <section className="px-7 md:px-12 py-28 max-w-[1200px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="cx-mono text-[12px] uppercase tracking-[.2em] text-[color:var(--cx-accent-hi)]">Por qué cardeep</div>
        <h2 className="font-black text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[18ch] text-[color:var(--cx-text-1)]">
          Ellos indexan su inventario. Nosotros indexamos el mercado.
        </h2>
      </CinematicReveal>

      <CinematicReveal delay={0.1} className="cx-panel rounded-[28px] overflow-hidden">
        <div className="grid grid-cols-[1.3fr_1fr_1fr] px-6 md:px-8 py-4 cx-mono text-[11px] font-semibold uppercase tracking-wide border-b" style={{ borderColor: 'var(--cx-line)', color: 'var(--cx-text-3)' }}>
          <span />
          <span style={{ color: 'var(--cx-accent-hi)' }}>cardeep</span>
          <span>El resto del sector</span>
        </div>
        {ROWS.map((row) => (
          <div key={row.label} className="grid grid-cols-[1.3fr_1fr_1fr] px-6 md:px-8 py-5 border-b last:border-b-0 items-center" style={{ borderColor: 'var(--cx-line)' }}>
            <span className="text-sm text-[color:var(--cx-text-2)]">{row.label}</span>
            <span className="flex items-center gap-2 text-sm font-semibold text-[color:var(--cx-text-1)]">
              <Check size={15} style={{ color: 'var(--cx-accent-hi)' }} className="shrink-0" /> {row.cardeep}
            </span>
            <span className="flex items-center gap-2 text-sm text-[color:var(--cx-text-3)]">
              <Minus size={15} className="shrink-0" /> {row.rest}
            </span>
          </div>
        ))}
        {coverage && (
          <div className="px-6 md:px-8 py-5 text-sm text-[color:var(--cx-text-2)]">
            Cobertura verificada hoy: <strong className="text-[color:var(--cx-text-1)]">{coverage.coveragePct.toFixed(1)}%</strong> del
            mercado de compraventa ({coverage.numerator.toLocaleString('es-ES')} de {coverage.denominator.toLocaleString('es-ES')} puntos
            de venta conocidos).
          </div>
        )}
      </CinematicReveal>
    </section>
  )
}
