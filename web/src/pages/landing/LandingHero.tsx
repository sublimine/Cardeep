import { lazy, Suspense } from 'react'
import { ArrowUpRight } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import KineticHeadline from './KineticHeadline'

const HeroScene = lazy(() => import('../../components/landing/HeroScene'))

/**
 * Dark hero shape sampled from the reference: black canvas, faint grid,
 * bottom-anchored glow, badge pill, LEFT-aligned headline with the
 * subcopy+CTA offset to the right, giant editorial wordmark bleeding at the
 * fold. The reference's glow is warm amber — kept as brand-blue here instead
 * (the app's single-hue rule from tokens.css v3.1: no second competing hue),
 * and `HeroScene`'s real WebGL "índice vivo" core replaces the reference's
 * decorative dust motes with something that actually means what it shows.
 */
export default function LandingHero() {
  return (
    <section className="relative min-h-screen flex flex-col overflow-hidden bg-[color:var(--cx-ink)]">
      <Suspense fallback={null}>
        <HeroScene className="!absolute inset-0 z-0" />
      </Suspense>

      {/* Faint grid, fading toward the top */}
      <div
        className="absolute inset-0 z-[1] pointer-events-none"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)',
          backgroundSize: '56px 56px',
          maskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 75%, transparent 100%)',
        }}
      />
      {/* Bottom-anchored brand glow (blue, not the reference's amber — single-hue rule) */}
      <div
        className="absolute inset-x-0 bottom-0 h-[60vh] z-[1] pointer-events-none"
        style={{ background: 'radial-gradient(ellipse 60% 100% at 50% 100%, rgba(37,99,235,0.28) 0%, transparent 70%)' }}
      />

      {/* NAV */}
      <nav className="relative z-10 flex items-center justify-between px-7 md:px-12 py-7">
        <div className="flex items-center gap-2.5">
          <img src="/uploads/cd-icon.png" alt="" className="h-6 w-auto block" />
          <span className="font-bold text-xl tracking-[-0.03em] text-white">cardeep</span>
        </div>
        <ul className="hidden md:flex items-center gap-9 list-none cx-mono text-[13px] uppercase tracking-[.08em] text-white/55">
          <li><a href="/marketplace" className="hover:text-white transition-colors">Marketplace</a></li>
          <li><a href="/inteligencia" className="hover:text-white transition-colors">Inteligencia</a></li>
          <li><a href="/arbitrage" className="hover:text-white transition-colors">Arbitrage</a></li>
        </ul>
        <a href="/login" className="flex items-center gap-2.5 rounded-lg bg-black pl-[3px] pr-4 py-[3px] text-sm font-medium text-white border border-white/10">
          <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
            <ArrowUpRight size={14} />
          </span>
          Acceder
        </a>
      </nav>

      {/* HEADLINE BLOCK */}
      <div className="relative z-10 flex-1 flex flex-col justify-center px-7 md:px-12 pb-16">
        <CinematicReveal>
          <span className="inline-flex items-center gap-2 rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 cx-mono text-[11px] uppercase tracking-[.14em] text-white/65">
            cardeep · el índice vivo de España
          </span>
        </CinematicReveal>

        <div className="mt-7 grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
          <KineticHeadline
            as="h1"
            className="font-black text-[clamp(2.6rem,6.4vw,5.6rem)] leading-[0.98] tracking-[-0.03em] text-white max-w-[16ch]"
          >
            El mercado entero, en un índice vivo.
          </KineticHeadline>

          <CinematicReveal delay={0.9} className="max-w-[38ch] lg:pb-2">
            <p className="text-[15px] md:text-base leading-relaxed text-white/60">
              Indexamos cada plataforma de España y te decimos, en claro, si un coche está bien comprado. Censo
              completo, no una muestra.
            </p>
            <a
              href="/marketplace"
              className="mt-5 inline-flex items-center gap-2.5 rounded-lg bg-black pl-[3px] pr-5 py-[3px] text-[15px] font-semibold text-white border border-white/10 transition-transform hover:scale-[1.02]"
            >
              <span className="cx-badge-chip flex h-9 w-9 items-center justify-center text-[color:var(--cx-ink)]">
                <ArrowUpRight size={15} />
              </span>
              Explorar el índice
            </a>
          </CinematicReveal>
        </div>
      </div>

      {/* Editorial wordmark bleed */}
      <div className="relative z-[1] select-none leading-none pb-[6vw]" aria-hidden>
        <div
          className="font-black tracking-[-0.04em]"
          style={{ fontSize: 'clamp(4.5rem, 18vw, 15rem)', color: 'rgba(255,255,255,0.055)' }}
        >
          cardeep
        </div>
      </div>
    </section>
  )
}
