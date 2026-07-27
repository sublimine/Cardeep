import CinematicReveal from './CinematicReveal'

/**
 * The reference's "TRUSTED BY..." logo wall, adapted honestly: cardeep has no
 * customer logos to show (no fabricated social proof — see CLAUDE.md
 * antialucinación), so this shows what actually IS true and verifiable — the
 * real marketplaces the harvest registry indexes (`pipeline/ops/registry/es.py`,
 * Tier-1 entries: autocasion, coches.com, coches.net, milanuncios, motor.es,
 * wallapop, autoscout24). The "~50" count is the file's own docstring
 * ("These ~50 entries are 100% ES-specific pack data"), not invented.
 */
const SOURCES = ['Coches.net', 'AutoScout24', 'Wallapop', 'Milanuncios', 'Coches.com', 'Autocasion', 'Motor.es']

export default function TrustStrip() {
  return (
    <section className="px-8 py-14 border-y" style={{ borderColor: 'var(--cx-line)' }}>
      <div className="max-w-[1440px] mx-auto">
        <CinematicReveal className="text-center text-[11px] uppercase tracking-[.18em] text-[color:var(--cx-text-3)] mb-8">
          Fuentes indexadas en vivo · ~50 registros de cosecha
        </CinematicReveal>
        <CinematicReveal stagger className="flex flex-wrap items-center justify-center gap-x-12 gap-y-5">
          {SOURCES.map((s) => (
            <span key={s} className="font-semibold text-lg tracking-[-0.01em] text-[color:var(--cx-text-2)] opacity-70 hover:opacity-100 transition-opacity">
              {s}
            </span>
          ))}
          <span className="text-[13px] text-[color:var(--cx-text-3)]">+ OEM · grupos · cosecha propia</span>
        </CinematicReveal>
      </div>
    </section>
  )
}
