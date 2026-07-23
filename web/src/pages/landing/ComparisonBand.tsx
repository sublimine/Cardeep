import { Fragment } from 'react'
import { CheckCircle2, AlertCircle, Radar, Activity, RefreshCw, Fingerprint } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import type { MarketCoverage } from '../../api/useCardeepStats'

interface Row {
  icon: React.ReactNode
  label: string
  cardeep: string
  rest: string
}

const ROWS: Row[] = [
  { icon: <Radar size={16} />, label: 'Cobertura del mercado', cardeep: 'El censo entero', rest: 'Solo lo publicado en su propia web' },
  { icon: <Activity size={16} />, label: 'Precio de mercado', cardeep: 'Observado en vivo', rest: 'Modelado sobre muestra' },
  { icon: <RefreshCw size={16} />, label: 'Altas y bajas', cardeep: 'Delta continuo', rest: 'Foto fija, sin histórico' },
  { icon: <Fingerprint size={16} />, label: 'Duplicados entre plataformas', cardeep: 'Deduplicado por VIN/foto', rest: 'El mismo coche, varias veces' },
]

/**
 * Reference pattern: 3-col table, shaded label column with icon+text, green
 * check rows for "us" vs. amber warning rows for "them", closing with a
 * 2-button CTA row. `--cx-emerald`/`--cx-amber` are the app's real status
 * hexes (tokens.css), not new colors invented for this page.
 */
export default function ComparisonBand({ coverage }: { coverage: MarketCoverage | null }) {
  return (
    <section className="px-7 md:px-12 py-24 md:py-28 max-w-[1200px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="cx-mono text-[12px] uppercase tracking-[.2em] text-[color:var(--cx-accent-hi)]">Por qué cardeep</div>
        <h2 className="font-black text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[20ch] text-[color:var(--cx-text-1)]">
          Ellos indexan su inventario. Nosotros indexamos el mercado.
        </h2>
      </CinematicReveal>

      <CinematicReveal delay={0.1} className="cx-panel rounded-[24px] overflow-hidden">
        <div className="grid grid-cols-[1.2fr_1fr_1fr]">
          <div className="px-6 md:px-8 py-4" style={{ background: 'var(--cx-surface-2)' }} />
          <div className="px-6 md:px-8 py-4 flex items-center border-b" style={{ borderColor: 'var(--cx-line)' }}>
            <span className="font-bold text-[15px] text-[color:var(--cx-text-1)]">cardeep</span>
          </div>
          <div className="px-6 md:px-8 py-4 flex items-center border-b" style={{ borderColor: 'var(--cx-line)' }}>
            <span className="cx-mono text-[12px] text-[color:var(--cx-text-3)]">El resto del sector</span>
          </div>

          {ROWS.map((row) => (
            <Fragment key={row.label}>
              <div
                className="px-6 md:px-8 py-5 flex items-center gap-3 border-b"
                style={{ background: 'var(--cx-surface-2)', borderColor: 'var(--cx-line)' }}
              >
                <span className="text-[color:var(--cx-text-3)]">{row.icon}</span>
                <span className="text-sm text-[color:var(--cx-text-2)]">{row.label}</span>
              </div>
              <div className="px-6 md:px-8 py-5 flex items-center gap-2.5 border-b" style={{ borderColor: 'var(--cx-line)' }}>
                <CheckCircle2 size={16} style={{ color: 'var(--cx-emerald)' }} className="shrink-0" />
                <span className="text-sm font-semibold text-[color:var(--cx-text-1)]">{row.cardeep}</span>
              </div>
              <div className="px-6 md:px-8 py-5 flex items-center gap-2.5 border-b" style={{ borderColor: 'var(--cx-line)' }}>
                <AlertCircle size={16} style={{ color: 'var(--cx-amber)' }} className="shrink-0" />
                <span className="text-sm text-[color:var(--cx-text-3)]">{row.rest}</span>
              </div>
            </Fragment>
          ))}

          <div className="px-6 md:px-8 py-6 col-span-3 flex flex-wrap items-center justify-between gap-4" style={{ background: 'var(--cx-surface-2)' }}>
            {coverage ? (
              <p className="text-sm text-[color:var(--cx-text-2)] max-w-[48ch]">
                Cobertura verificada hoy: <strong className="text-[color:var(--cx-text-1)]">{coverage.coveragePct.toFixed(1)}%</strong> del
                mercado de compraventa ({coverage.numerator.toLocaleString('es-ES')} de {coverage.denominator.toLocaleString('es-ES')} puntos
                de venta conocidos).
              </p>
            ) : (
              <span />
            )}
            <div className="flex gap-3">
              <a href="/marketplace" className="inline-flex items-center gap-2 rounded-lg bg-[color:var(--cx-ink)] pl-[3px] pr-4 py-[3px] text-[13.5px] font-semibold text-white">
                <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
                  <CheckCircle2 size={13} />
                </span>
                Ver el índice completo
              </a>
              <a href="/inteligencia" className="inline-flex items-center rounded-lg px-4 py-2.5 text-[13.5px] font-semibold cx-panel text-[color:var(--cx-text-1)]">
                Ver inteligencia de mercado
              </a>
            </div>
          </div>
        </div>
      </CinematicReveal>
    </section>
  )
}
