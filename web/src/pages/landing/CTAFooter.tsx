import CinematicReveal from './CinematicReveal'
import KineticHeadline from './KineticHeadline'

export default function CTAFooter() {
  return (
    <section className="px-7 md:px-12 pt-28 pb-14 max-w-[1200px] mx-auto">
      <CinematicReveal className="text-center">
        <KineticHeadline
          as="h2"
          className="font-black text-[clamp(2.2rem,5.5vw,4.6rem)] tracking-[-0.035em] leading-[1.05] text-[color:var(--cx-text-1)] max-w-[18ch] mx-auto"
        >
          El mapa completo de un mercado que hoy nadie tiene entero.
        </KineticHeadline>
      </CinematicReveal>

      <CinematicReveal delay={0.3} className="text-center">
        <p className="cx-mono text-sm md:text-base text-[color:var(--cx-text-2)] max-w-[46ch] mx-auto mt-6">
          Opera con el índice nacional y la inteligencia de mercado de tu lado.
        </p>
        <div className="flex gap-3 justify-center mt-9 flex-wrap">
          <a
            href="/marketplace"
            className="font-semibold text-[15px] text-white px-8 py-4 rounded-full transition-transform hover:scale-[1.03]"
            style={{ background: 'var(--cx-accent)' }}
          >
            Explorar el índice
          </a>
          <a
            href="/login"
            className="font-medium text-[15px] px-8 py-4 rounded-full cx-panel text-[color:var(--cx-text-1)]"
          >
            Para dealers
          </a>
        </div>
      </CinematicReveal>

      {/* Editorial closer — huge wordmark, Antinomy/Vide Infra pattern */}
      <div className="mt-32 text-center select-none" aria-hidden>
        <div
          className="font-black tracking-[-0.04em] leading-none"
          style={{ fontSize: 'clamp(3.5rem, 16vw, 13rem)', color: 'var(--cx-surface-3)' }}
        >
          cardeep
        </div>
      </div>

      <div className="flex justify-between items-center gap-5 flex-wrap mt-10 pt-8 border-t text-[13px]" style={{ borderColor: 'var(--cx-line)', color: 'var(--cx-text-3)' }}>
        <div className="flex items-center gap-2.5">
          <img src="/uploads/cd-icon.png" alt="" className="h-[19px] w-auto block" />
          <span className="font-bold text-[15px] tracking-[-0.03em] text-[color:var(--cx-text-1)]">cardeep</span>
          <span className="ml-1.5 cx-mono">Cobertura total. Cero ruido.</span>
        </div>
        <div className="cx-mono text-[11px]">© 2026 · España</div>
      </div>
    </section>
  )
}
