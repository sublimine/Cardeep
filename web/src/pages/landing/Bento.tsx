import { Layers, Megaphone, LineChart, Gauge, MapPin, Users } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import type { Stats } from '../../api/cardeep'

interface RegularTile {
  href: string
  icon: React.ReactNode
  title: string
  copy: string
  dark?: boolean
}

interface BentoProps {
  stats: Stats | null
}

function RegularCard({ tile }: { tile: RegularTile }) {
  return (
    <a
      href={tile.href}
      className={`cx-glow-border block rounded-[20px] p-6 flex flex-col transition-transform duration-300 hover:-translate-y-1 ${
        tile.dark ? 'cx-panel-dark' : 'cx-panel'
      }`}
    >
      <div style={{ color: tile.dark ? 'var(--cx-badge)' : 'var(--cx-accent-hi)' }}>{tile.icon}</div>
      <div className={`font-semibold text-base mt-4 ${tile.dark ? 'text-white' : 'text-[color:var(--cx-text-1)]'}`}>{tile.title}</div>
      <p className={`text-[13px] leading-relaxed mt-1.5 ${tile.dark ? 'text-[color:var(--cx-text-on-dark-2)]' : 'text-[color:var(--cx-text-2)]'}`}>
        {tile.copy}
      </p>
    </a>
  )
}

/**
 * Reference shape (round 4, re-verified visually — a plain screenshot, not
 * just computed-style sampling): NOT a uniform 3×2 grid, that was an
 * unverified Round 1 assumption. The real bento is asymmetric — one TALL
 * card (image up top, dark text panel below, spanning both rows in col 1)
 * next to a 2×2 grid of 4 regular cards. We have 6 real capabilities to
 * cardeep's 5 reference slots; rather than drop a real one to force-fit the
 * slot count, the 6th (Arbitrage, already our "featured" gradient tile)
 * becomes a full-width banner row underneath — keeps every real capability,
 * still reads as an intentional asymmetric bento rather than a flat grid.
 */
export default function Bento({ stats }: BentoProps) {
  const hero = {
    href: '/marketplace',
    icon: <Layers size={22} />,
    title: 'Índice nacional',
    copy: stats
      ? `${stats.dealers.toLocaleString('es-ES')} puntos de venta, con su stock y su delta.`
      : 'Cada punto de venta de España, con su stock y su delta.',
  }

  const regular: RegularTile[] = [
    { href: '/marketing', icon: <Megaphone size={22} />, title: 'Marketing', copy: 'Radar de canales y multiposting real a las plataformas del mercado.' },
    {
      href: '/inteligencia',
      icon: <MapPin size={22} />,
      title: 'Cobertura por provincia',
      copy: 'Demanda y absorción real, provincia a provincia — mapa vivo, no una foto fija.',
      dark: true,
    },
    { href: '/inteligencia', icon: <LineChart size={22} />, title: 'Inteligencia', copy: 'Valor residual y price-position frente al mercado real, no un modelo.' },
    { href: '/community', icon: <Users size={22} />, title: 'Comunidad', copy: 'Encargos y demanda real de compradores, en abierto.' },
  ]

  return (
    <section className="px-8 py-24 md:py-28 max-w-[1440px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="text-[13px] text-[color:var(--cx-text-3)]">Una plataforma · todo el ciclo</div>
        <h2 className="font-semibold text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[22ch] text-[color:var(--cx-text-1)]">
          Lo que hoy vive repartido en seis pestañas, aquí en una.
        </h2>
      </CinematicReveal>

      <CinematicReveal stagger className="grid gap-4 md:grid-cols-3 md:grid-rows-2">
        <a
          href={hero.href}
          className="cx-glow-border cx-panel-dark group flex flex-col overflow-hidden rounded-[20px] md:row-span-2"
        >
          <div className="flex items-center gap-1.5 px-4 py-3 border-b" style={{ borderColor: 'var(--cx-line-on-dark)' }}>
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--cx-line-strong)' }} />
          </div>
          <div className="h-[200px] overflow-hidden">
            <img
              src="/screens/marketplace.png"
              alt="Marketplace de cardeep"
              loading="lazy"
              className="h-full w-full object-cover object-top transition-transform duration-500 group-hover:scale-[1.03]"
            />
          </div>
          <div className="p-6 flex flex-col flex-1">
            <div style={{ color: 'var(--cx-badge)' }}>{hero.icon}</div>
            <div className="font-semibold text-base mt-4 text-white">{hero.title}</div>
            <p className="text-[13px] leading-relaxed mt-1.5 text-[color:var(--cx-text-on-dark-2)]">{hero.copy}</p>
          </div>
        </a>

        {regular.map((tile) => (
          <RegularCard key={tile.href + tile.title} tile={tile} />
        ))}

        <a
          href="/arbitrage"
          className="cx-glow-border md:col-span-3 flex flex-col md:flex-row md:items-center gap-4 rounded-[20px] p-6 min-h-[140px] transition-transform duration-300 hover:-translate-y-1"
          style={{ background: 'linear-gradient(150deg, var(--cx-accent) 0%, #1d4ed8 100%)' }}
        >
          <div style={{ color: '#fff' }}>
            <Gauge size={22} />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-base text-white">Arbitrage</div>
            <p className="text-[13px] leading-relaxed mt-1.5 text-white/75 max-w-[52ch]">
              Chollos y deal-score sobre el 100% del inventario, no una muestra.
            </p>
          </div>
        </a>
      </CinematicReveal>
    </section>
  )
}
