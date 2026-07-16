import { lazy, Suspense, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowUpRight, Search } from 'lucide-react'
import CinematicReveal from './CinematicReveal'
import KineticHeadline from './KineticHeadline'
import CountUp from '../../components/landing/CountUp'
import type { Stats } from '../../api/cardeep'

const HeroScene = lazy(() => import('../../components/landing/HeroScene'))

const BODIES = [
  { value: '', label: 'Cualquiera' },
  { value: 'suv', label: 'SUV' },
  { value: 'hatch', label: 'Compacto' },
  { value: 'estate', label: 'Familiar' },
]
const PRICES = [
  { value: '', label: 'Sin límite' },
  { value: '15000', label: '15.000 €' },
  { value: '20000', label: '20.000 €' },
  { value: '25000', label: '25.000 €' },
  { value: '30000', label: '30.000 €' },
]
const BRANDS = ['Audi', 'Hyundai', 'Kia', 'Peugeot', 'Renault', 'Seat', 'Skoda', 'VW']

interface LandingHeroProps {
  stats: Stats | null
}

export default function LandingHero({ stats }: LandingHeroProps) {
  const navigate = useNavigate()
  const [brand, setBrand] = useState('')
  const [body, setBody] = useState('')
  const [priceMax, setPriceMax] = useState('')

  const goExplore = () => {
    const q = new URLSearchParams()
    if (brand) q.set('brand', brand)
    if (body) q.set('body', body)
    if (priceMax) q.set('pmax', priceMax)
    navigate(`/marketplace${q.toString() ? `?${q}` : ''}`)
  }

  return (
    <section className="relative min-h-screen flex flex-col overflow-hidden">
      <Suspense fallback={null}>
        <HeroScene className="!absolute inset-0 z-0" />
      </Suspense>
      <div
        className="absolute inset-0 z-[1] pointer-events-none"
        style={{ background: 'radial-gradient(ellipse 70% 60% at 50% 100%, rgba(10,14,23,0.9) 0%, transparent 60%)' }}
      />

      {/* NAV */}
      <nav className="relative z-10 flex items-center justify-between px-7 md:px-12 py-7">
        <div className="flex items-center gap-2.5">
          <img src="/uploads/cd-icon.png" alt="" className="h-6 w-auto block" />
          <span className="font-bold text-xl tracking-[-0.03em] text-[color:var(--cx-text-1)]">cardeep</span>
        </div>
        <ul className="hidden md:flex items-center gap-9 list-none cx-mono text-[13px] uppercase tracking-[.08em] text-[color:var(--cx-text-2)]">
          <li><a href="/marketplace" className="hover:text-white transition-colors">Marketplace</a></li>
          <li><a href="/inteligencia" className="hover:text-white transition-colors">Inteligencia</a></li>
          <li><a href="/check" className="hover:text-white transition-colors">Historial</a></li>
        </ul>
        <a
          href="/login"
          className="flex items-center gap-2.5 rounded-full pl-2 pr-4 py-1.5 text-sm font-medium text-white"
          style={{ background: 'var(--cx-accent)' }}
        >
          <span className="bg-white/20 p-1.5 rounded-full grid place-items-center">
            <ArrowUpRight size={13} />
          </span>
          Acceder
        </a>
      </nav>

      {/* HEADLINE */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 text-center -mt-10">
        <div className="cx-mono text-[12px] uppercase tracking-[.25em] text-[color:var(--cx-accent-hi)] mb-5">
          El índice vivo de España
        </div>
        <KineticHeadline
          as="h1"
          className="font-black text-[clamp(2.6rem,7vw,6.5rem)] leading-[0.98] tracking-[-0.035em] text-[color:var(--cx-text-1)] max-w-[16ch]"
        >
          El mercado entero, en un índice vivo.
        </KineticHeadline>
        <CinematicReveal delay={0.9}>
          <p className="cx-mono text-sm md:text-base text-[color:var(--cx-text-2)] max-w-[46ch] mt-6 leading-relaxed">
            Indexamos cada plataforma de España y te decimos, en claro, si un coche está bien comprado.
          </p>
        </CinematicReveal>

        <CinematicReveal delay={1.05} className="mt-9 w-full max-w-[880px]">
          <div className="cx-panel flex flex-col sm:flex-row items-stretch gap-1.5 p-1.5 rounded-[26px] sm:rounded-full">
            <div className="flex items-stretch gap-1.5 flex-1 min-w-0">
              <label className="flex-1 min-w-0 flex flex-col justify-center text-left px-4.5 py-2 rounded-full cursor-pointer">
                <span className="cx-mono text-[10px] font-semibold text-[color:var(--cx-text-3)] uppercase tracking-[.1em]">Marca</span>
                <select
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  className="appearance-none border-0 bg-transparent outline-none text-sm font-semibold text-[color:var(--cx-text-1)] cursor-pointer p-0 w-full"
                >
                  <option value="" className="bg-[#121826]">Cualquiera</option>
                  {BRANDS.map((b) => (
                    <option key={b} value={b} className="bg-[#121826]">{b}</option>
                  ))}
                </select>
              </label>
              <div className="w-px my-2" style={{ background: 'var(--cx-line-strong)' }} />
              <label className="flex-1 min-w-0 flex flex-col justify-center text-left px-4.5 py-2 rounded-full cursor-pointer">
                <span className="cx-mono text-[10px] font-semibold text-[color:var(--cx-text-3)] uppercase tracking-[.1em]">Carrocería</span>
                <select
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  className="appearance-none border-0 bg-transparent outline-none text-sm font-semibold text-[color:var(--cx-text-1)] cursor-pointer p-0 w-full"
                >
                  {BODIES.map((b) => (
                    <option key={b.value} value={b.value} className="bg-[#121826]">{b.label}</option>
                  ))}
                </select>
              </label>
              <div className="hidden sm:block w-px my-2" style={{ background: 'var(--cx-line-strong)' }} />
              <label className="hidden sm:flex flex-1 min-w-0 flex-col justify-center text-left px-4.5 py-2 rounded-full cursor-pointer">
                <span className="cx-mono text-[10px] font-semibold text-[color:var(--cx-text-3)] uppercase tracking-[.1em]">Precio máx</span>
                <select
                  value={priceMax}
                  onChange={(e) => setPriceMax(e.target.value)}
                  className="appearance-none border-0 bg-transparent outline-none text-sm font-semibold text-[color:var(--cx-text-1)] cursor-pointer p-0 w-full"
                >
                  {PRICES.map((p) => (
                    <option key={p.value} value={p.value} className="bg-[#121826]">{p.label}</option>
                  ))}
                </select>
              </label>
            </div>
            <button
              onClick={goExplore}
              className="shrink-0 flex items-center justify-center gap-2 rounded-full px-6 py-3 sm:py-0 text-[14.5px] font-semibold text-white transition-transform hover:scale-[1.02]"
              style={{ background: 'var(--cx-accent)' }}
            >
              <Search size={17} />
              <span>Ver coches</span>
            </button>
          </div>
        </CinematicReveal>
      </div>

      {/* KPI ROW */}
      <CinematicReveal delay={1.2} stagger className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-px mx-7 md:mx-12 mb-7 rounded-2xl overflow-hidden" style={{ background: 'var(--cx-line)' }}>
        <div className="cx-panel px-6 py-5">
          {stats ? <CountUp value={stats.dealers} className="font-bold text-[26px] tracking-[-0.02em]" /> : <span className="text-[color:var(--cx-text-3)]">—</span>}
          <div className="cx-mono text-[11px] text-[color:var(--cx-text-3)] uppercase tracking-[.08em] mt-1">puntos de venta</div>
        </div>
        <div className="cx-panel px-6 py-5">
          {stats ? <CountUp value={stats.vehicles_unique_available} className="font-bold text-[26px] tracking-[-0.02em]" /> : <span className="text-[color:var(--cx-text-3)]">—</span>}
          <div className="cx-mono text-[11px] text-[color:var(--cx-text-3)] uppercase tracking-[.08em] mt-1">coches vivos</div>
        </div>
        <div className="cx-panel px-6 py-5">
          <a href="/check" className="font-bold text-[16px]" style={{ color: 'var(--cx-accent-hi)' }}>
            Consultar un vehículo <ArrowUpRight size={14} className="inline" />
          </a>
          <div className="cx-mono text-[11px] text-[color:var(--cx-text-3)] uppercase tracking-[.08em] mt-1">dossier de inteligencia</div>
        </div>
        <div className="cx-panel px-6 py-5">
          <a href="/marketplace" className="font-bold text-[16px]" style={{ color: 'var(--cx-accent-hi)' }}>
            Explorar el índice <ArrowUpRight size={14} className="inline" />
          </a>
          <div className="cx-mono text-[11px] text-[color:var(--cx-text-3)] uppercase tracking-[.08em] mt-1">marketplace completo</div>
        </div>
      </CinematicReveal>
    </section>
  )
}
