import { lazy, Suspense } from 'react'
import { ArrowUpRight } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import KineticHeadline from './KineticHeadline'

const HeroScene = lazy(() => import('../../components/landing/HeroScene'))

/**
 * Dark hero shape sampled from the reference: black canvas, faint grid,
 * bottom-anchored AMBER glow (matches the reference's horizon-arc color
 * exactly — owner correction 2026-07-23, a prior pass swapped it for brand
 * blue unasked), badge pill, LEFT-aligned headline with the subcopy+CTA
 * offset to the right, giant editorial wordmark bleeding at the fold.
 * `HeroScene`'s real WebGL "índice vivo" core is now receded/scaled down to
 * a background detail (also recolored amber) instead of a dominant
 * hero-centered object, so the atmosphere reads sparse like the reference.
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
      {/* Bottom-anchored horizon glow — warm amber, sampled from the reference */}
      <div
        className="absolute inset-x-0 bottom-0 h-[62vh] z-[1] pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 65% 85% at 50% 100%, rgba(245,166,35,0.4) 0%, rgba(245,133,35,0.18) 45%, transparent 72%)',
        }}
      />
      <div
        className="absolute inset-x-0 bottom-0 h-[3px] z-[1] pointer-events-none"
        style={{ background: 'linear-gradient(to right, transparent, rgba(245,166,35,0.55) 50%, transparent)' }}
      />

      {/* NAV */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-7">
        <div className="flex items-center gap-2.5">
          <img src="/uploads/cd-icon.png" alt="" className="h-6 w-auto block" />
          <span className="font-bold text-xl tracking-[-0.03em] text-white">cardeep</span>
        </div>
        <ul className="hidden md:flex items-center gap-9 list-none text-[14px] font-medium text-white/80">
          <li><a href="/marketplace" className="hover:text-white transition-colors">Marketplace</a></li>
          <li><a href="/inteligencia" className="hover:text-white transition-colors">Inteligencia</a></li>
          <li><a href="/arbitrage" className="hover:text-white transition-colors">Arbitrage</a></li>
          <li><a href="/pricing" className="hover:text-white transition-colors">Precios</a></li>
        </ul>
        <a href="/login" className="flex items-center gap-2.5 rounded-lg bg-black pl-[3px] pr-4 py-[3px] text-sm font-medium text-white border border-white/10">
          <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
            <ArrowUpRight size={14} />
          </span>
          Acceder
        </a>
      </nav>

      {/* HEADLINE BLOCK */}
      <div className="relative z-10 flex-1 flex flex-col justify-center px-8 pb-16">
        <CinematicReveal>
          <span className="inline-flex items-center gap-2 rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 text-[13px] font-medium text-white/65">
            cardeep · el índice vivo de España
          </span>
        </CinematicReveal>

        <div className="mt-7 grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
          <KineticHeadline
            as="h1"
            className="font-semibold text-[clamp(2.6rem,6.4vw,4.5rem)] leading-[0.98] tracking-[-0.03em] text-white max-w-[16ch]"
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
              className="mt-5 inline-flex items-center gap-2.5 rounded-lg bg-black pl-[3px] pr-5 py-[3px] text-[15px] font-medium text-white border border-white/10 transition-transform hover:scale-[1.02]"
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
          className="font-semibold tracking-[-0.04em]"
          style={{ fontSize: 'clamp(4.5rem, 18vw, 15rem)', color: 'rgba(255,255,255,0.055)' }}
        >
          cardeep
        </div>
      </div>
    </section>
  )
}
