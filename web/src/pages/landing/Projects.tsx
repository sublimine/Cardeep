import CinematicReveal from './CinematicReveal'

interface Screen {
  src: string
  alt: string
  title: string
  href: string
  span?: 'wide' | 'normal'
}

// The reference's "Projects" showcase shows real client work in device
// frames — cardeep has no client portfolio, so this shows real screenshots of
// the actual live product (captured directly from this app, not mockups or
// stock UI kits) instead of fabricating a portfolio that doesn't exist.
const SCREENS: Screen[] = [
  { src: '/screens/marketplace.png', alt: 'Marketplace de cardeep', title: 'Marketplace — índice nacional en vivo', href: '/marketplace', span: 'wide' },
  { src: '/screens/dashboard.png', alt: 'Dashboard de cardeep', title: 'Dashboard del dealer', href: '/login' },
  { src: '/screens/inteligencia.png', alt: 'Inteligencia de mercado de cardeep', title: 'Inteligencia de mercado', href: '/login' },
]

function DeviceFrame({ screen }: { screen: Screen }) {
  return (
    <a
      href={screen.href}
      className={`cx-panel group block overflow-hidden rounded-[18px] ${screen.span === 'wide' ? 'md:col-span-2' : ''}`}
    >
      <div className="flex items-center gap-1.5 px-4 py-3 border-b" style={{ borderColor: 'var(--cx-line)' }}>
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
      </div>
      <div className="overflow-hidden">
        <img
          src={screen.src}
          alt={screen.alt}
          loading="lazy"
          className="w-full h-auto block transition-transform duration-500 group-hover:scale-[1.02]"
        />
      </div>
      <div className="px-4 py-3 text-[13px] font-medium text-[color:var(--cx-text-2)]">{screen.title}</div>
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

      <CinematicReveal stagger className="grid gap-4 md:grid-cols-2">
        {SCREENS.map((screen) => (
          <DeviceFrame key={screen.href + screen.title} screen={screen} />
        ))}
      </CinematicReveal>
    </section>
  )
}
