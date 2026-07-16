import { Layers, FileText, LineChart, Gauge, Wallet } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import type { Stats } from '../../api/cardeep'

interface Tile {
  href: string
  icon: React.ReactNode
  title: string
  copy: string
  featured?: boolean
}

interface BentoProps {
  stats: Stats | null
}

/**
 * "Garaje 360°" (original static tile) had no real destination — no `/garage`
 * route exists in `App.tsx`. Replaced with Arbitrage, a real gated route that
 * completes the 3-layer intelligence story started by the teaser above
 * (Capa 0 free / Capa 1 Inteligencia / Capa 2 Arbitrage).
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
    { href: '/check', icon: <FileText size={22} />, title: 'Historial', copy: 'Km, siniestros, titulares y cargas. Scraping propio.' },
    { href: '/inteligencia', icon: <LineChart size={22} />, title: 'Inteligencia', copy: 'Valor residual y price-position frente al mercado real.' },
    { href: '/arbitrage', icon: <Gauge size={22} />, title: 'Arbitrage', copy: 'Chollos y deal-score sobre el 100% del inventario, no una muestra.' },
    { href: '/finance', icon: <Wallet size={22} />, title: 'Finanzas', copy: 'Margen por coche, cashflow y P&L. All-in-one.', featured: true },
  ]

  return (
    <section className="px-7 md:px-12 py-28 max-w-[1200px] mx-auto">
      <CinematicReveal className="mb-14">
        <div className="cx-mono text-[12px] uppercase tracking-[.2em] text-[color:var(--cx-accent-hi)]">Una plataforma · todo el ciclo</div>
        <h2 className="font-black text-[clamp(2rem,4.2vw,3.6rem)] tracking-[-0.03em] leading-[1.05] mt-4 max-w-[20ch] text-[color:var(--cx-text-1)]">
          Lo que hoy vive repartido en seis pestañas, aquí en una.
        </h2>
      </CinematicReveal>

      <CinematicReveal stagger className="grid gap-3.5" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))' }}>
        {tiles.map((tile) => (
          <a
            key={tile.href}
            href={tile.href}
            className={`cx-glow-border block rounded-2xl p-6 transition-transform duration-300 hover:-translate-y-1 ${tile.featured ? '' : 'cx-panel'}`}
            style={tile.featured ? { background: 'linear-gradient(150deg, var(--cx-accent) 0%, #1d4ed8 100%)' } : undefined}
          >
            <div style={{ color: tile.featured ? '#fff' : 'var(--cx-accent-hi)' }}>{tile.icon}</div>
            <div className={`font-bold text-base mt-4 ${tile.featured ? 'text-white' : 'text-[color:var(--cx-text-1)]'}`}>{tile.title}</div>
            <p className={`text-[13px] leading-relaxed mt-1.5 ${tile.featured ? 'text-white/75' : 'text-[color:var(--cx-text-2)]'}`}>{tile.copy}</p>
          </a>
        ))}
      </CinematicReveal>
    </section>
  )
}
