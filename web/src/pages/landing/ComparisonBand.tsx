import { Fragment } from 'react'
import { CheckCircle2, AlertCircle, Radar, Activity, RefreshCw, Fingerprint, ShieldCheck, Code2 } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import type { MarketCoverage } from '../../api/useCardeepStats'

interface Row {
  icon: React.ReactNode
  label: string
  cardeep: string
  rest: string
}

// Rows 5-6 added round 2 (owner-directed exhaustive pass, 2026-07-24): grounded
// in real Pricing.tsx Scale/Enterprise features (VAM provenance, API & Tokens),
// not invented — see Pricing.tsx PLANS. Reference has 7 comparison rows; we
// stop at 6 because no further real, defensible differentiator was found
// (declared gap, not an oversight — see scratch/landing-fidelity-spec.md).
const ROWS: Row[] = [
  { icon: <Radar size={16} />, label: 'Cobertura del mercado', cardeep: 'El censo entero', rest: 'Solo lo publicado en su propia web' },
  { icon: <Activity size={16} />, label: 'Precio de mercado', cardeep: 'Observado en vivo', rest: 'Modelado sobre muestra' },
  { icon: <RefreshCw size={16} />, label: 'Altas y bajas', cardeep: 'Delta continuo', rest: 'Foto fija, sin histórico' },
  { icon: <Fingerprint size={16} />, label: 'Duplicados entre plataformas', cardeep: 'Deduplicado por VIN/foto', rest: 'El mismo coche, varias veces' },
  { icon: <ShieldCheck size={16} />, label: 'Verificación de origen', cardeep: 'Provenance auditable (VAM)', rest: 'Dato opaco, sin auditar' },
  { icon: <Code2 size={16} />, label: 'Acceso programático', cardeep: 'API con tokens propios', rest: 'Solo interfaz cerrada' },
]

function CoverageCTA({ coverage }: { coverage: MarketCoverage | null }) {
  return (
    <div className="px-6 md:px-8 py-6 flex flex-col md:flex-row flex-wrap items-start md:items-center justify-between gap-4" style={{ background: 'var(--cx-surface-2)' }}>
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
        <a href="/marketplace" className="inline-flex items-center gap-2 rounded-lg bg-[color:var(--cx-ink)] pl-[3px] pr-4 py-[3px] text-[13.5px] font-medium text-white">
          <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
            <CheckCircle2 size={13} />
          </span>
          Ver el índice completo
        </a>
        <a href="/inteligencia" className="inline-flex items-center rounded-lg px-4 py-2.5 text-[13.5px] font-medium cx-panel text-[color:var(--cx-text-1)]">
          Ver inteligencia de mercado
        </a>
      </div>
    </div>
  )
}

/**
 * Reference pattern: 3-col table, shaded label column with icon+text, green
 * check rows for "us" vs. amber warning rows for "them", closing with a
 * 2-button CTA row. `--cx-emerald`/`--cx-amber` are the app's real status
 * hexes (tokens.css), not new colors invented for this page.
 *
 * Mobile (<md, round 2 fix): the reference has no documented mobile layout
 * for this table, and a naive 3-equal-column grid below ~640px squeezes each
 * cell to ~110px, wrapping and clipping words mid-string (verified via
 * Playwright at 375px). Below `md` this switches to a stacked per-row card
 * (label, then cardeep line, then "resto" line) instead — same content, no
 * horizontal scroll hack, nothing clipped.
 */
export default function ComparisonBand({ coverage }: { coverage: MarketCoverage | null }) {
  return (
    <section className="px-8 py-24 md:py-28 max-w-[1440px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="text-[13px] text-[color:var(--cx-text-3)]">Por qué cardeep</div>
        <h2 className="font-semibold text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[20ch] text-[color:var(--cx-text-1)]">
          Ellos indexan su inventario. Nosotros indexamos el mercado.
        </h2>
      </CinematicReveal>

      <CinematicReveal delay={0.1} className="cx-panel rounded-[24px] overflow-hidden">
        {/* Desktop / tablet: 3-col table */}
        <div className="hidden md:grid md:grid-cols-3">
          <div className="px-8 py-4" style={{ background: 'var(--cx-surface-2)' }} />
          <div className="px-8 py-4 flex items-center border-b" style={{ borderColor: 'var(--cx-line)' }}>
            <span className="font-semibold text-[15px] text-[color:var(--cx-text-1)]">cardeep</span>
          </div>
          <div className="px-8 py-4 flex items-center border-b" style={{ borderColor: 'var(--cx-line)' }}>
            <span className="text-[13px] text-[color:var(--cx-text-3)]">El resto del sector</span>
          </div>

          {ROWS.map((row) => (
            <Fragment key={row.label}>
              <div
                className="px-8 py-8 flex items-center gap-3 border-b"
                style={{ background: 'var(--cx-surface-2)', borderColor: 'var(--cx-line)' }}
              >
                <span className="text-[color:var(--cx-text-3)]">{row.icon}</span>
                <span className="text-sm text-[color:var(--cx-text-2)]">{row.label}</span>
              </div>
              <div className="px-8 py-8 flex items-center gap-2.5 border-b" style={{ borderColor: 'var(--cx-line)' }}>
                <CheckCircle2 size={16} style={{ color: 'var(--cx-emerald)' }} className="shrink-0" />
                <span className="text-sm font-semibold text-[color:var(--cx-text-1)]">{row.cardeep}</span>
              </div>
              <div className="px-8 py-8 flex items-center gap-2.5 border-b" style={{ borderColor: 'var(--cx-line)' }}>
                <AlertCircle size={16} style={{ color: 'var(--cx-amber)' }} className="shrink-0" />
                <span className="text-sm text-[color:var(--cx-text-3)]">{row.rest}</span>
              </div>
            </Fragment>
          ))}

          <div className="col-span-3">
            <CoverageCTA coverage={coverage} />
          </div>
        </div>

        {/* Mobile: stacked per-row cards */}
        <div className="md:hidden divide-y" style={{ borderColor: 'var(--cx-line)' }}>
          {ROWS.map((row) => (
            <div key={row.label} className="px-6 py-6" style={{ borderColor: 'var(--cx-line)' }}>
              <div className="flex items-center gap-2.5 text-[color:var(--cx-text-3)]">
                {row.icon}
                <span className="text-sm text-[color:var(--cx-text-2)]">{row.label}</span>
              </div>
              <div className="mt-3 flex items-center gap-2.5">
                <CheckCircle2 size={16} style={{ color: 'var(--cx-emerald)' }} className="shrink-0" />
                <span className="text-sm font-semibold text-[color:var(--cx-text-1)]">{row.cardeep}</span>
              </div>
              <div className="mt-2 flex items-center gap-2.5">
                <AlertCircle size={16} style={{ color: 'var(--cx-amber)' }} className="shrink-0" />
                <span className="text-sm text-[color:var(--cx-text-3)]">{row.rest}</span>
              </div>
            </div>
          ))}
          <CoverageCTA coverage={coverage} />
        </div>
      </CinematicReveal>
    </section>
  )
}
