import { ArrowUpRight } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import KineticHeadline from './KineticHeadline'

// Real routes only, verified against App.tsx's Route table — no invented
// destinations. Auth-gated app routes (inteligencia, arbitrage, marketing,
// community, pricing) redirect an anonymous visitor to /login, same as any
// "sign in to use this feature" marketing-site pattern.
const COLUMNS = [
  { h: 'Producto', links: [
    { l: 'Marketplace', href: '/marketplace' },
    { l: 'Inteligencia', href: '/inteligencia' },
    { l: 'Arbitrage', href: '/arbitrage' },
    { l: 'Marketing', href: '/marketing' },
  ] },
  { h: 'Cuenta', links: [
    { l: 'Iniciar sesión', href: '/login' },
    { l: 'Crear cuenta', href: '/register' },
    { l: 'Precios', href: '/pricing' },
    { l: 'Soporte', href: '/support' },
  ] },
  { h: 'Comunidad', links: [
    { l: 'Foro', href: '/community' },
    { l: 'Encargos', href: '/community/wanted' },
  ] },
]

export default function CTAFooter() {
  return (
    <section className="px-7 md:px-12 pt-10 pb-16 max-w-[1200px] mx-auto">
      <CinematicReveal className="cx-panel-dark relative overflow-hidden rounded-[28px]">
        <div className="relative z-10 flex items-start justify-between gap-6 px-8 md:px-12 pt-12 md:pt-16">
          <KineticHeadline
            as="h2"
            className="font-black text-[clamp(2rem,4.6vw,3.6rem)] tracking-[-0.03em] leading-[1.05] text-white max-w-[16ch]"
          >
            El mapa completo de un mercado que hoy nadie tiene entero.
          </KineticHeadline>
          <a
            href="/marketplace"
            aria-label="Explorar el índice"
            className="shrink-0 grid place-items-center h-14 w-14 rounded-full bg-white text-[color:var(--cx-ink)] transition-transform hover:scale-105"
          >
            <ArrowUpRight size={22} />
          </a>
        </div>

        {/* Editorial wordmark bleeding at the bottom of the panel */}
        <div className="relative z-0 select-none leading-none mt-8 md:mt-2" aria-hidden>
          <div
            className="font-black tracking-[-0.04em] px-8 md:px-12"
            style={{ fontSize: 'clamp(3.5rem, 15vw, 11rem)', color: 'rgba(255,255,255,0.06)' }}
          >
            cardeep
          </div>
        </div>
      </CinematicReveal>

      <div className="flex flex-wrap gap-10 justify-between mt-16">
        <div className="max-w-[220px]">
          <div className="flex items-center gap-2.5">
            <img src="/uploads/cd-icon.png" alt="" className="h-6 w-auto block" />
            <span className="font-bold text-lg tracking-[-0.03em] text-[color:var(--cx-text-1)]">cardeep</span>
          </div>
          <p className="mt-3 text-[13px] leading-relaxed text-[color:var(--cx-text-3)]">
            El índice vivo del mercado de coches de ocasión en España.
          </p>
          <a
            href="/register"
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-[color:var(--cx-ink)] pl-[3px] pr-4 py-[3px] text-[13px] font-semibold text-white"
          >
            <span className="cx-badge-chip flex h-8 w-8 items-center justify-center text-[color:var(--cx-ink)]">
              <ArrowUpRight size={13} />
            </span>
            Crear cuenta
          </a>
        </div>

        <div className="flex flex-wrap gap-10 md:gap-16">
          {COLUMNS.map((col) => (
            <div key={col.h}>
              <div className="cx-mono text-[11px] font-semibold uppercase tracking-[.1em] text-[color:var(--cx-text-3)]">{col.h}</div>
              <div className="mt-3.5 flex flex-col gap-2.5">
                {col.links.map((link) => (
                  <a key={link.href} href={link.href} className="text-[13.5px] font-medium text-[color:var(--cx-text-2)] hover:text-[color:var(--cx-text-1)] transition-colors">
                    {link.l}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div
        className="flex justify-between items-center gap-5 flex-wrap mt-12 pt-6 border-t text-[12px] cx-mono"
        style={{ borderColor: 'var(--cx-line)', color: 'var(--cx-text-3)' }}
      >
        <span>© 2026 cardeep · España</span>
        <span>Cobertura total. Cero ruido.</span>
      </div>
    </section>
  )
}
