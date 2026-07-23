import { Layers, Megaphone, LineChart, Gauge, MapPin, Users } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import type { Stats } from '../../api/cardeep'

interface Tile {
  href: string
  icon: React.ReactNode
  title: string
  copy: string
  dark?: boolean
  featured?: boolean
}

interface BentoProps {
  stats: Stats | null
}

/**
 * Reference shape: a uniform 3-col grid of 6 flat cards, visual rhythm
 * carried by mixing light/dark tiles (not by grid-span asymmetry — the
 * reference's own bento is a plain 3x2 grid). "Cobertura por provincia" is a
 * dark tile with no embedded chart on purpose: the real interactive map
 * (`CoverageMap`) is theme-coupled to the app shell's tokens and would break
 * inside a forced-dark landing tile — same trade the reference itself makes
 * (its dark "Hosting" card is illustrative, not a live embedded widget). The
 * real map lives one click away on /inteligencia.
 */
export default function Bento({ stats }: BentoProps) {
  const tiles: Tile[] = [
    {
      href: '/marketplace',
      icon: <Layers size={22} />,
      title: 'Índice nacional',
      copy: stats
        ? `${stats.dealers.toLocaleString('es-ES')} puntos de venta, con su stock y su delta.`
        : 'Cada punto de venta de España, con su stock y su delta.',
    },
    { href: '/marketing', icon: <Megaphone size={22} />, title: 'Marketing', copy: 'Radar de canales y multiposting real a las plataformas del mercado.' },
    {
      href: '/inteligencia',
      icon: <MapPin size={22} />,
      title: 'Cobertura por provincia',
      copy: 'Demanda y absorción real, provincia a provincia — mapa vivo, no una foto fija.',
      dark: true,
    },
    { href: '/inteligencia', icon: <LineChart size={22} />, title: 'Inteligencia', copy: 'Valor residual y price-position frente al mercado real, no un modelo.' },
    {
      href: '/arbitrage',
      icon: <Gauge size={22} />,
      title: 'Arbitrage',
      copy: 'Chollos y deal-score sobre el 100% del inventario, no una muestra.',
      featured: true,
    },
    { href: '/community', icon: <Users size={22} />, title: 'Comunidad', copy: 'Encargos y demanda real de compradores, en abierto.' },
  ]

  return (
    <section className="px-7 md:px-12 py-24 md:py-28 max-w-[1200px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="cx-mono text-[12px] uppercase tracking-[.2em] text-[color:var(--cx-accent-hi)]">Una plataforma · todo el ciclo</div>
        <h2 className="font-black text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[22ch] text-[color:var(--cx-text-1)]">
          Lo que hoy vive repartido en seis pestañas, aquí en una.
        </h2>
      </CinematicReveal>

      <CinematicReveal stagger className="grid gap-4 md:grid-cols-3">
        {tiles.map((tile) => (
          <a
            key={tile.href + tile.title}
            href={tile.href}
            className={`cx-glow-border block rounded-[20px] p-6 min-h-[190px] flex flex-col transition-transform duration-300 hover:-translate-y-1 ${
              tile.featured ? '' : tile.dark ? 'cx-panel-dark' : 'cx-panel'
            }`}
            style={tile.featured ? { background: 'linear-gradient(150deg, var(--cx-accent) 0%, #1d4ed8 100%)' } : undefined}
          >
            <div style={{ color: tile.featured ? '#fff' : tile.dark ? 'var(--cx-badge)' : 'var(--cx-accent-hi)' }}>{tile.icon}</div>
            <div className={`font-bold text-base mt-4 ${tile.featured || tile.dark ? 'text-white' : 'text-[color:var(--cx-text-1)]'}`}>{tile.title}</div>
            <p className={`text-[13px] leading-relaxed mt-1.5 ${tile.featured ? 'text-white/75' : tile.dark ? 'text-[color:var(--cx-text-on-dark-2)]' : 'text-[color:var(--cx-text-2)]'}`}>
              {tile.copy}
            </p>
          </a>
        ))}
      </CinematicReveal>
    </section>
  )
}
