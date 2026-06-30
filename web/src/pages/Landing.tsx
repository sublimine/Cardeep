import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { useAuthContext } from '../auth/AuthContext'

// ── Design tokens ──────────────────────────────────────────────────────────
interface Tok {
  bg: string; panel: string; panel2: string
  glass: string; glassBrd: string
  ink: string; ink2: string; ink3: string
  line: string; shadowSm: string; shadow: string
  mint: string; mint2: string
  ctl: string; ctlInk: string
}
const LIGHT: Tok = {
  bg: '#EAECEF', panel: '#FFFFFF', panel2: '#F1F3F6',
  glass: 'rgba(255,255,255,.34)', glassBrd: 'rgba(255,255,255,.55)',
  ink: '#13161B', ink2: '#5E6470', ink3: 'rgba(19,22,27,.4)',
  line: 'rgba(20,28,40,.09)',
  shadowSm: '0 14px 34px -18px rgba(38,46,62,.24)',
  shadow: '0 44px 96px -40px rgba(38,46,62,.46)',
  mint: '#3B82F6', mint2: '#E8F0FE',
  ctl: '#111827', ctlInk: '#FFFFFF',
}
const DARK: Tok = {
  bg: '#0B0D11', panel: '#15181F', panel2: '#1C2129',
  glass: 'rgba(20,24,31,.46)', glassBrd: 'rgba(255,255,255,.12)',
  ink: '#F3F2EC', ink2: 'rgba(243,242,236,.66)', ink3: 'rgba(243,242,236,.42)',
  line: 'rgba(255,255,255,.08)',
  shadowSm: '0 14px 34px -18px rgba(0,0,0,.6)',
  shadow: '0 44px 96px -36px rgba(0,0,0,.74)',
  mint: '#5B96F8', mint2: 'rgba(59,130,246,.18)',
  ctl: '#F3F2EC', ctlInk: '#111827',
}

// ── Mock stock for filter preview ──────────────────────────────────────────
const STOCK: [string, string, number][] = [
  ['Peugeot', 'suv',    23400],
  ['VW',      'hatch',  18450],
  ['Audi',    'estate', 27750],
  ['Kia',     'suv',    21900],
  ['Seat',    'hatch',  21300],
  ['VW',      'estate', 24900],
  ['Hyundai', 'suv',    28750],
  ['Renault', 'hatch',  13200],
  ['Skoda',   'estate', 22100],
]

const EXPO = [0.16, 1, 0.3, 1] as const

// ── Animated count (triggers on viewport entry) ────────────────────────────
function AnimatedCount({ value }: { value: number }) {
  const [count, setCount] = useState(0)
  const spanRef = useRef<HTMLSpanElement>(null)
  const rafRef = useRef<number>(0)
  const reduced = useReducedMotion() === true

  useEffect(() => {
    const el = spanRef.current
    if (!el) return
    const obs = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return
      obs.disconnect()
      if (reduced) { setCount(value); return }
      const start = performance.now()
      const dur = 1500
      const tick = (now: number) => {
        const k = Math.min(1, (now - start) / dur)
        setCount(Math.round(value * (1 - Math.pow(1 - k, 3))))
        if (k < 1) rafRef.current = requestAnimationFrame(tick)
      }
      rafRef.current = requestAnimationFrame(tick)
    }, { threshold: 0.6 })
    obs.observe(el)
    return () => { obs.disconnect(); cancelAnimationFrame(rafRef.current) }
  }, [value, reduced])

  return <span ref={spanRef}>{count.toLocaleString('es-ES')}</span>
}

// ── SVG icons ──────────────────────────────────────────────────────────────
function IconSun() {
  return (
    <svg width={17} height={17} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5 5l1.4 1.4M17.6 17.6L19 19M19 5l-1.4 1.4M6.4 17.6L5 19"/>
    </svg>
  )
}
function IconMoon() {
  return (
    <svg width={17} height={17} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 14.5A8 8 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5z"/>
    </svg>
  )
}
function IconArrow() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 17L17 7M9 7h8v8"/>
    </svg>
  )
}
function IconSearch() {
  return (
    <svg width={17} height={17} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
    </svg>
  )
}
function IconChevron() {
  return (
    <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18l6-6-6-6"/>
    </svg>
  )
}

// ── Feature icons ──────────────────────────────────────────────────────────
function IconLayers() {
  return <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 12l9 4 9-4M3 17l9 4 9-4"/></svg>
}
function IconShield() {
  return <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
}
function IconChart() {
  return <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg>
}
function IconGarage() {
  return <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="8" width="18" height="12" rx="2"/><path d="M7 8V6a5 5 0 0110 0v2"/></svg>
}
function IconDollar() {
  return <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
}

// ── Feature cards data ─────────────────────────────────────────────────────
interface Feature {
  icon: React.ReactNode
  title: string
  desc: string
  highlighted?: boolean
}
const FEATURES: Feature[] = [
  { icon: <IconLayers />, title: 'Índice nacional',  desc: 'Cada punto de venta de España, con su stock y su delta.' },
  { icon: <IconShield />, title: 'Historial',        desc: 'Km, siniestros, titulares y cargas. Scraping propio.' },
  { icon: <IconChart />,  title: 'Inteligencia UE',  desc: 'Valor residual y sweet-spot contra 27 mercados.' },
  { icon: <IconGarage />, title: 'Garaje 360°',      desc: 'Tu stock como activo vivo, moldeable a tu gusto.' },
  { icon: <IconDollar />, title: 'Finanzas',         desc: 'Margen por coche, cashflow y P&L. All-in-one.', highlighted: true },
]

// ── Trust strip stats ──────────────────────────────────────────────────────
interface Stat { value?: number; display?: string; label: string; accent?: boolean }
const STATS: Stat[] = [
  { value: 48213, label: 'fuentes indexadas' },
  { display: '1,92M', label: 'coches vivos' },
  { value: 142, label: 'altas hoy', accent: true },
  { display: '27', label: 'mercados UE cruzados' },
]

// ── Landing ────────────────────────────────────────────────────────────────
export default function Landing() {
  const nav = useNavigate()
  const { isAuthenticated } = useAuthContext()
  const prefersReduced = useReducedMotion()
  const reduced = prefersReduced === true

  const [dark, setDark] = useState(false)
  const [brand, setBrand] = useState('')
  const [body,  setBody]  = useState('')
  const [price, setPrice] = useState('')

  // Hydrate theme from localStorage
  useEffect(() => {
    try { if (localStorage.getItem('cardeep-theme') === 'dark') setDark(true) } catch { /* noop */ }
  }, [])

  // Inject web fonts
  useEffect(() => {
    const ids = ['cd-font-gs', 'cd-font-jb']
    const hrefs = [
      'https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap',
      'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap',
    ]
    ids.forEach((id, i) => {
      if (document.getElementById(id)) return
      const el = document.createElement('link')
      el.id = id; el.rel = 'stylesheet'; el.href = hrefs[i]
      document.head.appendChild(el)
    })
  }, [])

  const toggleTheme = () => {
    setDark(d => {
      const next = !d
      try { localStorage.setItem('cardeep-theme', next ? 'dark' : 'light') } catch { /* noop */ }
      return next
    })
  }

  const t = dark ? DARK : LIGHT
  const dest = isAuthenticated ? '/dashboard' : '/login'

  // Filter counter
  const brands = [...new Set(STOCK.map(s => s[0]))].sort()
  const matched = STOCK.filter(([b, bo, p]) =>
    (!brand || b === brand) && (!body || bo === body) && (!price || p <= Number(price))
  )
  const filterLabel = matched.length
    ? `Ver ${matched.length} coche${matched.length === 1 ? '' : 's'}`
    : 'Sin resultados'

  // Per-mode hero bg
  const heroCardBg  = dark ? '#1C2129' : '#EEF0F3'
  const heroGrad    = dark
    ? 'linear-gradient(180deg,#1C2129 0%,rgba(28,33,41,.9) 20%,rgba(28,33,41,.4) 36%,rgba(28,33,41,.06) 54%,transparent 72%)'
    : 'linear-gradient(180deg,#EEF0F3 0%,rgba(238,240,243,.9) 20%,rgba(238,240,243,.4) 36%,rgba(238,240,243,.06) 54%,transparent 72%)'
  const heroRadial  = dark
    ? 'radial-gradient(ellipse 58% 92% at 50% 32%,#1C2129 0%,rgba(28,33,41,.86) 34%,rgba(28,33,41,.4) 56%,transparent 76%)'
    : 'radial-gradient(ellipse 58% 92% at 50% 32%,#EEF0F3 0%,rgba(238,240,243,.86) 34%,rgba(238,240,243,.4) 56%,transparent 76%)'
  const heroMesh    = dark
    ? 'radial-gradient(ellipse 70% 70% at 62% 38%,rgba(59,130,246,.12) 0%,transparent 60%),radial-gradient(ellipse 55% 55% at 20% 68%,rgba(124,58,237,.08) 0%,transparent 50%)'
    : 'radial-gradient(ellipse 70% 70% at 62% 38%,rgba(147,197,253,.28) 0%,transparent 60%),radial-gradient(ellipse 55% 55% at 20% 68%,rgba(196,181,253,.18) 0%,transparent 50%)'

  // Select text color for dark mode (native select options inherit bg from OS in dark)
  const selStyle: React.CSSProperties = {
    appearance: 'none', WebkitAppearance: 'none', border: 0, background: 'none',
    outline: 'none', fontFamily: 'inherit', fontSize: 14, fontWeight: 600,
    color: t.ink, cursor: 'pointer', padding: '2px 0 0',
  }
  const filterSegStyle: React.CSSProperties = {
    flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
    textAlign: 'left', padding: '9px 18px', borderRadius: 999, cursor: 'pointer',
    background: 'none', transition: 'background .18s',
  }
  const filterLabelStyle: React.CSSProperties = {
    fontSize: 10.5, fontWeight: 600, color: t.ink3,
    textTransform: 'uppercase', letterSpacing: '0.07em',
  }

  return (
    <div style={{
      background: t.bg, color: t.ink, minHeight: '100vh',
      fontFamily: "'General Sans','Segoe UI',system-ui,sans-serif",
      WebkitFontSmoothing: 'antialiased', letterSpacing: '-0.005em',
      overflowX: 'hidden', transition: 'background .4s ease,color .4s ease',
    }}>
      <style>{`
        *{box-sizing:border-box}
        a{color:inherit;text-decoration:none}
        .cd-press{transition:transform .18s cubic-bezier(.16,1,.3,1),box-shadow .2s,background .2s}
        .cd-press:hover{transform:translateY(-2px)}
        .cd-press:active{transform:scale(.98)}
        .cd-link{transition:opacity .2s}
        .cd-link:hover{opacity:.6}
        .cd-fseg:hover{background:${dark ? 'rgba(255,255,255,.06)' : 'rgba(255,255,255,.45)'} !important}
        @media(max-width:680px){.cd-nav-links{display:none!important}}
        @media(max-width:520px){.cd-filter-bar{flex-wrap:wrap;border-radius:20px!important;padding:8px!important}}
      `}</style>

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <div style={{ width: '100%', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
        <motion.section
          initial={reduced ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.9, ease: EXPO }}
          style={{
            position: 'relative', width: '100%', maxWidth: 1536,
            height: 'calc(100dvh - 32px)', minHeight: 600,
            borderRadius: 36, overflow: 'hidden',
            background: heroCardBg,
            display: 'flex', flexDirection: 'column', alignItems: 'center',
          }}
        >
          {/* Ambient mesh — substitutes for hero video */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 0, background: heroMesh }} />
          {/* Top-to-transparent gradient overlay */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 1, background: heroGrad }} />
          {/* Radial spotlight orb top-center */}
          <div style={{ position: 'absolute', top: 64, left: '50%', transform: 'translateX(-50%)', width: 'min(1080px,100%)', height: 420, zIndex: 2, pointerEvents: 'none', background: heroRadial }} />

          {/* Content */}
          <div style={{ position: 'relative', zIndex: 10, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

            {/* NAV */}
            <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '24px 28px', width: '100%' }}>
              {/* Logo */}
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 25, height: 25, borderRadius: 6, background: 'linear-gradient(135deg,#3B82F6,#3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <div style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(255,255,255,.9)' }} />
                </div>
                <span style={{ fontWeight: 700, fontSize: 20, letterSpacing: '-0.035em', color: t.ink }}>cardeep</span>
              </div>

              {/* Nav links */}
              <ul className="cd-nav-links" style={{ display: 'flex', alignItems: 'center', gap: 30, listStyle: 'none', margin: 0, padding: 0, color: t.ink2, fontSize: 14 }}>
                {['Índice', 'Inteligencia', 'Marketplace', 'Garaje 360°'].map(l => (
                  <li key={l} className="cd-link"><a href="#bento">{l}</a></li>
                ))}
              </ul>

              {/* Actions */}
              <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 10 }}>
                <button onClick={toggleTheme} aria-label="Cambiar tema" className="cd-press" style={{ width: 40, height: 40, borderRadius: 999, border: `1px solid ${t.line}`, background: dark ? 'rgba(255,255,255,.06)' : 'rgba(255,255,255,.6)', backdropFilter: 'blur(10px)', WebkitBackdropFilter: 'blur(10px)', color: t.ink, cursor: 'pointer', display: 'grid', placeItems: 'center', padding: 0 }}>
                  {dark ? <IconSun /> : <IconMoon />}
                </button>
                <button onClick={() => nav(dest)} className="cd-press" style={{ display: 'flex', alignItems: 'center', gap: 10, background: t.ctl, color: t.ctlInk, borderRadius: 999, padding: '7px 18px 7px 8px', fontSize: 14, fontWeight: 500, border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}>
                  <span style={{ background: 'rgba(255,255,255,.2)', padding: 6, borderRadius: 999, display: 'grid', placeItems: 'center' }}><IconArrow /></span>
                  Ver demo
                </button>
              </div>
            </nav>

            {/* HERO TEXT + FILTER BAR */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', width: '100%', padding: '6px 24px 30px', textAlign: 'center' }}>
              <motion.h1
                initial={reduced ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: EXPO, delay: 0.15 }}
                style={{ fontWeight: 500, fontSize: 'clamp(34px,5vw,60px)', color: dark ? '#E0DDD6' : '#2f3744', margin: 0, letterSpacing: '-0.035em', lineHeight: 1.02 }}
              >
                El mercado entero,<br />en un índice vivo.
              </motion.h1>

              <motion.p
                initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: EXPO, delay: 0.3 }}
                style={{ fontSize: 'clamp(14px,1.3vw,17px)', color: t.ink2, lineHeight: 1.5, maxWidth: 440, margin: '14px 0 0' }}
              >
                Indexamos cada plataforma de España y te decimos, en claro, si un coche está bien comprado.
              </motion.p>

              {/* GLASS FILTER BAR */}
              <motion.div
                initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: EXPO, delay: 0.42 }}
                style={{ marginTop: 26, width: 'min(880px,100%)' }}
              >
                <div className="cd-filter-bar" style={{
                  display: 'flex', alignItems: 'stretch', gap: 6, padding: 7, borderRadius: 999,
                  background: dark ? 'rgba(20,24,31,.52)' : 'rgba(255,255,255,.42)',
                  backdropFilter: 'blur(26px) saturate(165%)', WebkitBackdropFilter: 'blur(26px) saturate(165%)',
                  border: `1px solid ${dark ? 'rgba(255,255,255,.14)' : 'rgba(255,255,255,.6)'}`,
                  boxShadow: dark
                    ? '0 22px 60px -26px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,255,255,.1)'
                    : '0 22px 60px -26px rgba(38,46,62,.5),inset 0 1px 0 rgba(255,255,255,.7),inset 0 -1px 0 rgba(40,48,64,.06)',
                }}>
                  {/* Marca */}
                  <label className="cd-fseg" style={filterSegStyle}>
                    <span style={filterLabelStyle}>Marca</span>
                    <select value={brand} onChange={e => setBrand(e.target.value)} style={selStyle}>
                      <option value="">Cualquiera</option>
                      {brands.map(b => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </label>
                  <div style={{ width: 1, background: dark ? 'rgba(255,255,255,.1)' : 'rgba(40,48,64,.12)', margin: '9px 0' }} />

                  {/* Carrocería */}
                  <label className="cd-fseg" style={filterSegStyle}>
                    <span style={filterLabelStyle}>Carrocería</span>
                    <select value={body} onChange={e => setBody(e.target.value)} style={selStyle}>
                      <option value="">Cualquiera</option>
                      <option value="suv">SUV</option>
                      <option value="hatch">Compacto</option>
                      <option value="estate">Familiar</option>
                    </select>
                  </label>
                  <div style={{ width: 1, background: dark ? 'rgba(255,255,255,.1)' : 'rgba(40,48,64,.12)', margin: '9px 0' }} />

                  {/* Precio máx */}
                  <label className="cd-fseg" style={filterSegStyle}>
                    <span style={filterLabelStyle}>Precio máx</span>
                    <select value={price} onChange={e => setPrice(e.target.value)} style={selStyle}>
                      <option value="">Sin límite</option>
                      <option value="15000">15.000 €</option>
                      <option value="20000">20.000 €</option>
                      <option value="25000">25.000 €</option>
                      <option value="30000">30.000 €</option>
                    </select>
                  </label>

                  {/* Search CTA */}
                  <button onClick={() => nav(dest)} className="cd-press" style={{ flexShrink: 0, display: 'flex', alignItems: 'center', gap: 9, background: t.ctl, color: t.ctlInk, borderRadius: 999, padding: '0 24px', fontSize: 14.5, fontWeight: 600, border: 'none', cursor: 'pointer', fontFamily: 'inherit', boxShadow: '0 10px 24px -10px rgba(0,0,0,.5)' }}>
                    <IconSearch />
                    <span>{filterLabel}</span>
                  </button>
                </div>
              </motion.div>
            </div>

            {/* BOTTOM-LEFT GLASS CARD */}
            <motion.div
              initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: EXPO, delay: 0.55 }}
              style={{
                position: 'absolute', left: 28, bottom: 28, zIndex: 11,
                padding: 20, borderRadius: 26,
                background: t.glass, backdropFilter: 'blur(26px) saturate(150%)',
                WebkitBackdropFilter: 'blur(26px) saturate(150%)',
                border: `1px solid ${t.glassBrd}`,
                boxShadow: `${t.shadow},inset 0 1px 0 rgba(255,255,255,.6)`,
                display: 'flex', flexDirection: 'column', gap: 14, minWidth: 190,
              }}
            >
              <div>
                <div style={{ fontVariantNumeric: 'tabular-nums', fontSize: 32, fontWeight: 600, letterSpacing: '-0.03em', color: dark ? t.ink : '#1b2330' }}>
                  <AnimatedCount value={48213} />
                </div>
                <div style={{ fontSize: 11, fontWeight: 600, color: t.ink3, textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 3 }}>fuentes vivas</div>
              </div>
              <button onClick={() => nav(dest)} className="cd-press" style={{ display: 'flex', alignItems: 'center', gap: 9, background: t.panel, borderRadius: 999, padding: '7px 16px 7px 7px', alignSelf: 'flex-start', boxShadow: t.shadowSm, border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}>
                <span style={{ background: t.mint2, padding: 6, borderRadius: 999, display: 'grid', placeItems: 'center' }}>
                  <svg width={15} height={15} viewBox="0 0 24 24" fill="none" stroke={t.mint} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg>
                </span>
                <span style={{ fontSize: 14, fontWeight: 500, color: dark ? t.ink : '#1b2330' }}>Explorar el índice</span>
              </button>
            </motion.div>

            {/* BOTTOM-RIGHT CORNER-CUT CARD */}
            <motion.div
              initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: EXPO, delay: 0.65 }}
              style={{ position: 'absolute', bottom: 0, right: 0, zIndex: 11, padding: '28px 28px 28px 56px', background: t.bg, borderTopLeftRadius: 40, display: 'flex', alignItems: 'center', gap: 20 }}
            >
              {/* Corner SVG cut-outs to blend with page bg */}
              <div style={{ position: 'absolute', top: -40, right: 0, width: 40, height: 40, pointerEvents: 'none' }}>
                <svg width="100%" height="100%" viewBox="0 0 56 56" fill="none">
                  <path d="M56 56V0C56 30.9279 30.9279 56 0 56H56Z" fill={t.bg} />
                </svg>
              </div>
              <div style={{ position: 'absolute', bottom: 0, left: -40, width: 40, height: 40, pointerEvents: 'none' }}>
                <svg width="100%" height="100%" viewBox="0 0 56 56" fill="none">
                  <path d="M56 56H0C30.9279 56 56 30.9279 56 0V56Z" fill={t.bg} />
                </svg>
              </div>
              <button onClick={() => nav(dest)} className="cd-press" style={{ width: 54, height: 54, borderRadius: 999, background: t.panel, border: `1px solid ${t.line}`, display: 'grid', placeItems: 'center', color: t.ink, boxShadow: t.shadowSm, cursor: 'pointer', flexShrink: 0 }}>
                <IconArrow />
              </button>
              <div>
                <div style={{ fontSize: 19, fontWeight: 500, color: t.ink }}>Dossier de inteligencia</div>
                <button onClick={() => nav(dest)} className="cd-link" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: t.ink3, marginTop: 3, background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: 0 }}>
                  <span style={{ fontSize: 14, fontWeight: 500 }}>Ver un ejemplo</span>
                  <IconChevron />
                </button>
              </div>
            </motion.div>

          </div>
        </motion.section>
      </div>

      {/* ── TRUST STRIP ──────────────────────────────────────────────────── */}
      <section id="stats" style={{ width: 'min(1200px,calc(100% - 32px))', margin: '30px auto 0' }}>
        <motion.div
          initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: EXPO }}
          style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 1, borderRadius: 22, overflow: 'hidden', background: t.line, border: `1px solid ${t.line}`, boxShadow: t.shadowSm }}
        >
          {STATS.map(({ value, display, label, accent }) => (
            <div key={label} style={{ background: t.panel, padding: '22px 24px' }}>
              <div style={{ fontVariantNumeric: 'tabular-nums', fontSize: 27, fontWeight: 600, letterSpacing: '-0.03em', color: accent ? t.mint : t.ink }}>
                {accent && <span>+</span>}
                {value !== undefined ? <AnimatedCount value={value} /> : <span>{display}</span>}
              </div>
              <div style={{ fontSize: 12.5, color: t.ink3, marginTop: 3 }}>{label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* ── BENTO ────────────────────────────────────────────────────────── */}
      <section id="bento" style={{ width: 'min(1200px,calc(100% - 32px))', margin: '80px auto 0' }}>
        <motion.div
          initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: EXPO }}
          style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 12, letterSpacing: '0.06em', color: t.ink3 }}
        >
          Una plataforma · todo el ciclo
        </motion.div>
        <motion.h2
          initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: EXPO, delay: 0.06 }}
          style={{ fontWeight: 600, fontSize: 'clamp(26px,3.2vw,40px)', letterSpacing: '-0.03em', margin: '12px 0 0', maxWidth: 600, color: t.ink }}
        >
          Lo que hoy vive repartido en seis pestañas, aquí en una.
        </motion.h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(205px,1fr))', gap: 14, marginTop: 34 }}>
          {FEATURES.map(({ icon, title, desc, highlighted }, i) => (
            <motion.button
              key={title}
              initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: EXPO, delay: i * 0.07 }}
              onClick={() => nav(dest)}
              className="cd-press"
              style={{
                background: highlighted ? t.ctl : t.panel,
                border: `1px solid ${highlighted ? t.ctl : t.line}`,
                borderRadius: 24, padding: 22,
                boxShadow: t.shadowSm,
                color: highlighted ? t.ctlInk : t.ink,
                textAlign: 'left', cursor: 'pointer',
                fontFamily: "'General Sans','Segoe UI',system-ui,sans-serif",
                display: 'block', width: '100%',
              }}
            >
              {icon}
              <div style={{ fontWeight: 600, fontSize: 16, marginTop: 15 }}>{title}</div>
              <p style={{ fontSize: 13, lineHeight: 1.5, color: highlighted ? 'rgba(255,255,255,.7)' : t.ink2, margin: '6px 0 0' }}>{desc}</p>
            </motion.button>
          ))}
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────── */}
      <section style={{ width: 'min(1200px,calc(100% - 32px))', margin: '80px auto 90px' }}>
        <motion.div
          initial={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: EXPO }}
          style={{ borderRadius: 34, padding: '64px 40px', textAlign: 'center', background: t.panel, border: `1px solid ${t.line}`, boxShadow: t.shadow }}
        >
          <h2 style={{ fontWeight: 600, fontSize: 'clamp(28px,3.6vw,46px)', letterSpacing: '-0.032em', lineHeight: 1.04, margin: '0 auto', maxWidth: 620, color: t.ink }}>
            El mapa completo de un mercado que hoy nadie tiene entero.
          </h2>
          <p style={{ fontSize: 16.5, lineHeight: 1.55, color: t.ink2, margin: '18px auto 0', maxWidth: 500 }}>
            Opera con el índice nacional y la inteligencia europea de tu lado.
          </p>
          <div style={{ display: 'flex', gap: 11, justifyContent: 'center', marginTop: 28, flexWrap: 'wrap' }}>
            <button onClick={() => nav(dest)} className="cd-press" style={{ fontWeight: 600, fontSize: 15, color: t.ctlInk, background: t.ctl, padding: '16px 30px', borderRadius: 999, border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}>
              Explorar el índice
            </button>
            <button onClick={() => nav(dest)} className="cd-press" style={{ fontWeight: 500, fontSize: 15, color: t.ink, background: t.panel2, padding: '16px 30px', borderRadius: 999, border: `1px solid ${t.line}`, cursor: 'pointer', fontFamily: 'inherit' }}>
              Para dealers
            </button>
          </div>
        </motion.div>

        {/* Footer row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 20, flexWrap: 'wrap', marginTop: 30, color: t.ink3, fontSize: 13 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
            <div style={{ width: 19, height: 19, borderRadius: 4, background: 'linear-gradient(135deg,#3B82F6,#3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <div style={{ width: 7, height: 7, borderRadius: 1.5, background: 'rgba(255,255,255,.9)' }} />
            </div>
            <span style={{ fontWeight: 700, fontSize: 15, color: t.ink, letterSpacing: '-0.035em' }}>cardeep</span>
            <span style={{ marginLeft: 6 }}>Cobertura total. Cero ruido.</span>
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11 }}>© 2026 · España</div>
        </div>
      </section>
    </div>
  )
}
