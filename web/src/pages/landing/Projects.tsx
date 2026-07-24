import { ArrowUpRight } from 'lucide-react'
import CinematicReveal from './CinematicReveal'

interface Screen {
  src: string
  alt: string
  title: string
  href: string
  widthFr: number
}

// The reference's "Projects" showcase shows real client work in device
// frames — cardeep has no client portfolio, so this shows real screenshots of
// the actual live product (captured directly from this app, not mockups or
// stock UI kits) instead of fabricating a portfolio that doesn't exist.
//
// Masonry rhythm (round 2, 2026-07-24): sampled the reference's own grid via
// computed styles — 6 images, fixed 440px row height, object-fit cover,
// alternating widths (~876/476/676px at 1600px viewport), 24px gap. We only
// have 3 real screens (not 6) — rather than fabricate 3 more, the same
// alternating-width/fixed-height/cover idiom is applied across our 3 real
// screens instead of the previous plain 2-col/natural-height grid.
const SCREENS: Screen[] = [
  { src: '/screens/marketplace.png', alt: 'Marketplace de cardeep', title: 'Marketplace — índice nacional en vivo', href: '/marketplace', widthFr: 1.7 },
  { src: '/screens/dashboard.png', alt: 'Dashboard de cardeep', title: 'Dashboard del dealer', href: '/login', widthFr: 1 },
  { src: '/screens/inteligencia.png', alt: 'Inteligencia de mercado de cardeep', title: 'Inteligencia de mercado', href: '/login', widthFr: 1.3 },
]

function DeviceFrame({ screen }: { screen: Screen }) {
  return (
    <a
      href={screen.href}
      style={{ '--cx-w-fr': screen.widthFr } as React.CSSProperties}
      className="cx-panel cx-device-frame group flex min-w-[240px] flex-col overflow-hidden rounded-[18px]"
    >
      <div className="flex items-center gap-1.5 px-4 py-3 border-b" style={{ borderColor: 'var(--cx-line)' }}>
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
      </div>
      <div className="h-[260px] md:h-[360px] overflow-hidden">
        <img
          src={screen.src}
          alt={screen.alt}
          loading="lazy"
          className="h-full w-full object-cover object-top transition-transform duration-500 group-hover:scale-[1.03]"
        />
      </div>
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <span className="text-[13px] font-medium text-[color:var(--cx-text-2)]">{screen.title}</span>
        <ArrowUpRight
          size={14}
          className="shrink-0 text-[color:var(--cx-text-3)] transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
        />
      </div>
    </a>
  )
}

export default function Projects() {
  return (
    <section className="px-8 pt-4 pb-24 md:pb-28 max-w-[1440px] mx-auto overflow-hidden">
      <div className="select-none leading-none mb-6" aria-hidden>
        <div
          className="font-semibold tracking-[-0.04em]"
          style={{ fontSize: 'clamp(3.5rem, 14vw, 10rem)', color: 'var(--cx-surface-3)' }}
        >
          Producto
        </div>
      </div>

      <CinematicReveal stagger className="flex flex-col md:flex-row gap-6">
        {SCREENS.map((screen) => (
          <DeviceFrame key={screen.href + screen.title} screen={screen} />
        ))}
      </CinematicReveal>
    </section>
  )
}
