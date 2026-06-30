import { motion, AnimatePresence } from 'framer-motion'
import React, { useEffect, useRef, useState } from 'react'
import {
  MessageSquare, FileText, Search, Image as ImageIcon, Send, Plus, ChevronRight,
} from 'lucide-react'
import { useAuthContext } from '../auth/AuthContext'

// ── Theme observer ─────────────────────────────────────────────────────────────
function useIsDark() {
  const [dark, setDark] = useState(() => !document.documentElement.classList.contains('light'))
  useEffect(() => {
    const obs = new MutationObserver(() => setDark(!document.documentElement.classList.contains('light')))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return dark
}

// ── Token helper ───────────────────────────────────────────────────────────────
function tok(dark: boolean) {
  return {
    t1:        dark ? '#f1f5f9'                    : '#0f172a',
    t2:        dark ? '#cbd5e1'                    : '#334155',
    t3:        dark ? '#94a3b8'                    : '#64748b',
    t4:        dark ? '#475569'                    : '#94a3b8',
    div:       dark ? 'rgba(255,255,255,0.07)'     : 'rgba(0,0,0,0.07)',
    cardBg:    dark ? 'rgba(255,255,255,0.04)'     : 'rgba(255,255,255,0.82)',
    cardBord:  dark ? 'rgba(255,255,255,0.08)'     : 'rgba(0,0,0,0.08)',
    subBg:     dark ? 'rgba(255,255,255,0.03)'     : 'rgba(0,0,0,0.03)',
    subBord:   dark ? 'rgba(255,255,255,0.06)'     : 'rgba(0,0,0,0.07)',
    inputBg:   dark ? 'rgba(255,255,255,0.06)'     : 'rgba(0,0,0,0.05)',
    inputBord: dark ? 'rgba(255,255,255,0.10)'     : 'rgba(0,0,0,0.10)',
    botBubble: dark ? 'rgba(255,255,255,0.07)'     : 'rgba(0,0,0,0.05)',
  }
}

// ── Glass card ─────────────────────────────────────────────────────────────────
function GCard({
  dark, children, style,
}: { dark: boolean; children: React.ReactNode; style?: React.CSSProperties }) {
  const c = tok(dark)
  return (
    <div style={{
      background: c.cardBg,
      border: `1px solid ${c.cardBord}`,
      borderRadius: 18,
      backdropFilter: 'blur(32px) saturate(180%)',
      WebkitBackdropFilter: 'blur(32px) saturate(180%)',
      boxShadow: dark
        ? '0 4px 24px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.07)'
        : '0 4px 20px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.90)',
      overflow: 'hidden',
      ...style,
    }}>
      {children}
    </div>
  )
}

// ── renderBold — **text** → <strong> ──────────────────────────────────────────
function renderBold(text: string, color: string): React.ReactNode {
  return text.split(/\*\*(.*?)\*\*/g).map((part, i) =>
    i % 2 === 1
      ? <strong key={i} style={{ fontWeight: 700, color }}>{part}</strong>
      : <span key={i}>{part}</span>
  )
}

// ── Types ──────────────────────────────────────────────────────────────────────
type Mode = 'ask' | 'listing' | 'vin' | 'image'

interface ChatMsg {
  id: string
  role: 'user' | 'bot'
  text: string
  imageUrl?: string
}

interface Conversation {
  id: string
  title: string
  mode: Mode
  messages: ChatMsg[]
  updatedAt: string
}

// ── Mode config ────────────────────────────────────────────────────────────────
const MODES: { id: Mode; label: string; desc: string }[] = [
  { id: 'ask',     label: 'Preguntar',              desc: 'Stock · precios · mercado EU'  },
  { id: 'listing', label: 'Descripción de anuncio', desc: 'Genera texto de venta'          },
  { id: 'vin',     label: 'Valorar VIN',             desc: 'Tasación por VIN o matrícula'  },
  { id: 'image',   label: 'Imagen de coche',         desc: 'Genera imagen desde descripción'},
]

// ── Suggested prompts per mode ─────────────────────────────────────────────────
const SUGGESTIONS: Record<Mode, string[]> = {
  ask: [
    '¿Cuántos coches tengo en stock?',
    '¿Cuál es mi margen bruto este mes?',
    '¿Qué vehículos llevan más de 60 días?',
    '¿Cómo están mis precios vs el mercado EU?',
    '¿Qué deals están cerca de cerrarse?',
  ],
  listing: [
    'BMW 320d 2021, 68.000 km, automático, blanco',
    'VW Golf 1.5 TSI 2020, 45.000 km, negro, impecable',
    'Audi A4 Avant 2.0 TDI 2019, 95.000 km, navegación',
    'Mercedes C220d 2022, 32.000 km, AMG Line',
    'Seat León FR 2021, 55.000 km, DSG, rojo',
  ],
  vin: [
    'WBA3A5C50DF595785',
    'WAUZZZ8K8BA123456',
    'VSSZZZ5FZJR012345',
    'WDD2050422F312345',
    'TMBJP7NE4J0012345',
  ],
  image: [
    'BMW Serie 3 azul marino, exterior día, fondo neutro',
    'SUV compacto blanco, interior premium, luz natural',
    'Deportivo rojo vista lateral, ángulo 3/4 trasero',
    'Berlina gris marengo, frontal limpio, sin fondo',
    'Todoterreno negro mate, vista aérea, carretera',
  ],
}

// ── Empty-state copy ───────────────────────────────────────────────────────────
const EMPTY: Record<Mode, { heading: string; body: string }> = {
  ask:     { heading: 'Pregunta sobre tu negocio',           body: 'Consulta stock, márgenes, pipeline y alertas del mercado EU en tiempo real.' },
  listing: { heading: 'Genera una descripción de anuncio',   body: 'Indica marca, modelo, año y km. Obtendrás un texto profesional listo para publicar.' },
  vin:     { heading: 'Valora un VIN o matrícula',           body: 'Pega el VIN de 17 dígitos para historial completo y tasación EU al instante.' },
  image:   { heading: 'Describe el coche a visualizar',      body: 'Marca, color y ángulo. Recibirás una imagen optimizada para anuncio.' },
}

const NEW_TITLE: Record<Mode, string> = {
  ask: 'Nueva consulta', listing: 'Nuevo anuncio', vin: 'Nueva valoración', image: 'Nueva imagen',
}

// ── Car images for mock image generation ───────────────────────────────────────
const CAR_IMAGES = [
  'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=480&h=270&fit=crop',
  'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=480&h=270&fit=crop',
  'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=480&h=270&fit=crop',
  'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=480&h=270&fit=crop',
  'https://images.unsplash.com/photo-1620891549027-942fdc95d3f5?w=480&h=270&fit=crop',
]

// ── Mock bot replies ───────────────────────────────────────────────────────────
function botReply(mode: Mode, text: string): { text: string; imageUrl?: string } {
  const q = text.toLowerCase()

  if (mode === 'ask') {
    if (q.match(/stock|coches|inventario|veh/))
      return { text: 'Tienes **270 vehículos** en stock con valor total **€2.14M**. Los 3 más críticos superan los **60 días** — el BMW 320d lleva 72 días y necesita una rebaja del 6%.' }
    if (q.match(/margen|beneficio|profit|margin/))
      return { text: 'Margen bruto de **€87.4k** este mes (**+8%** vs mes anterior). Revenue total **€437k**. En línea con el objetivo anual de **€1.05M**.' }
    if (q.match(/60|stale|viejos|antiguos|días/))
      return { text: '**3 vehículos** llevan más de 60 días: BMW 320d (**72d**), Audi A4 (**68d**), VW Golf (**61d**). Recomiendo **reducir precio un 5-8%** en los dos primeros.' }
    if (q.match(/precio|mercado|market|competitiv/))
      return { text: 'Tu precio medio está **3.8% por debajo de la mediana EU** — buena posición competitiva. Tus días en stock (47d) superan la mediana del mercado (39d); optimiza la rotación.' }
    if (q.match(/deal|operacion|clos|cerrar|negoci/))
      return { text: '**8 deals** cerca de cierre esta semana. En etapa Negociación hay **10 operaciones**. Prioridad: **Maria S.** (BMW 320d) y **Peter K.** (C220d) — ambos con oferta pendiente más de 48h.' }
    return { text: 'Puedo ayudarte con **stock**, **márgenes**, **vehículos estancados**, **precios de mercado** y **estado del pipeline**. ¿Qué necesitas saber?' }
  }

  if (mode === 'listing') {
    const make = q.match(/bmw|volkswagen|vw|audi|mercedes|seat|skoda|opel|ford|peugeot|renault/)?.[0]?.toUpperCase() ?? 'Este vehículo'
    const kmMatch = text.match(/(\d[\d.,]*)\s*km/)
    const km = kmMatch ? kmMatch[1] : '60.000'
    return {
      text: `Descripción generada:\n\n"**${text}** — un ${make} de referencia en su segmento. Con ${km} km en excelente estado de conservación, revisiones al día y equipamiento completo. Interior impecable, carrocería sin golpes ni rayones. Disponible para prueba inmediata y financiación a medida. Garantía mecánica incluida. ¡Oportunidad única al mejor precio del mercado!"\n\n**Palabras clave sugeridas:** ${make} ocasión · coches segunda mano · comprar ${make} España · precio justo EU.`,
    }
  }

  if (mode === 'vin') {
    const vinMatch = text.match(/[A-HJ-NPR-Z0-9]{17}/i)
    const vin = vinMatch ? vinMatch[0].toUpperCase() : text.trim().toUpperCase().slice(0, 17)
    return {
      text: `**VIN analizado:** \`${vin || 'N/D'}\`\n\n📋 **Historial:** Sin siniestros registrados · 2 propietarios anteriores · ITV en vigor\n\n💰 **Valoración CARDEEP:** **€24.200 – €26.800** (mediana EU: €25.400)\n\n📊 **Posición de mercado:** −4.2% bajo mediana → precio competitivo\n\n⚠️ Kilometraje declarado coherente con desgaste mecánico. Sin anomalías detectadas.`,
    }
  }

  if (mode === 'image') {
    const idx = Math.floor(Math.random() * CAR_IMAGES.length)
    return {
      text: `Imagen generada para:\n*"${text}"*\n\nResolución **1920×1080** · Fondo neutro · Optimizada para anuncio. Lista para descargar.`,
      imageUrl: CAR_IMAGES[idx],
    }
  }

  return { text: 'No entendí la consulta. Intenta de nuevo.' }
}

// ── Mode icon ──────────────────────────────────────────────────────────────────
function ModeIcon({ mode, size = 13 }: { mode: Mode; size?: number }) {
  const p = { width: size, height: size }
  if (mode === 'ask')     return <MessageSquare {...p} />
  if (mode === 'listing') return <FileText {...p} />
  if (mode === 'vin')     return <Search {...p} />
  return <ImageIcon {...p} />
}

// ── Bot avatar SVG ─────────────────────────────────────────────────────────────
function BotAvatar({ size = 24 }: { size?: number }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: Math.round(size * 0.29), flexShrink: 0,
      background: 'linear-gradient(135deg, #3B82F6, #2563eb)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      boxShadow: '0 2px 8px rgba(59,130,246,0.30)',
      alignSelf: 'flex-start',
    }}>
      <svg width={size * 0.42} height={size * 0.42} viewBox="0 0 24 24" fill="none"
        stroke="white" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
    </div>
  )
}

// ── timeAgo ────────────────────────────────────────────────────────────────────
function timeAgo(iso: string): string {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000)
  if (m < 1)  return 'ahora'
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  return h < 24 ? `${h}h` : `${Math.floor(h / 24)}d`
}

// ── Assistant page ─────────────────────────────────────────────────────────────
export default function Assistant() {
  const dark = useIsDark()
  const { user } = useAuthContext()
  const c = tok(dark)
  const BLUE = '#3B82F6'

  const [mode, setMode] = useState<Mode>('ask')
  const [conversations, setConversations] = useState<Conversation[]>([{
    id: 'conv-0', title: 'Nueva consulta', mode: 'ask', messages: [], updatedAt: new Date().toISOString(),
  }])
  const [activeConvId, setActiveConvId] = useState<string>('conv-0')
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [composerFocused, setComposerFocused] = useState(false)

  const scrollRef   = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const activeConv = conversations.find(cv => cv.id === activeConvId) ?? conversations[0]
  const msgs = activeConv?.messages ?? []

  // Scroll to bottom on new messages or typing indicator
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [msgs.length, typing])

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`
  }, [input])

  function handleModeChange(m: Mode) {
    setMode(m)
    // Reuse existing empty conversation for this mode, else create one
    const existing = conversations.find(cv => cv.mode === m && cv.messages.length === 0)
    if (existing) { setActiveConvId(existing.id); return }
    const id = `conv-${Date.now()}`
    setConversations(prev => [{ id, title: NEW_TITLE[m], mode: m, messages: [], updatedAt: new Date().toISOString() }, ...prev])
    setActiveConvId(id)
  }

  function startNew() {
    const id = `conv-${Date.now()}`
    setConversations(prev => [{ id, title: NEW_TITLE[mode], mode, messages: [], updatedAt: new Date().toISOString() }, ...prev])
    setActiveConvId(id)
  }

  function send(text: string) {
    const t = text.trim()
    if (!t || typing) return
    const userMsg: ChatMsg = { id: `u-${Date.now()}`, role: 'user', text: t }
    setConversations(prev => prev.map(cv =>
      cv.id === activeConvId
        ? { ...cv, title: cv.messages.length === 0 ? t.slice(0, 42) : cv.title, messages: [...cv.messages, userMsg], updatedAt: new Date().toISOString() }
        : cv
    ))
    setInput('')
    setTyping(true)
    setTimeout(() => {
      const reply = botReply(mode, t)
      const botMsg: ChatMsg = { id: `b-${Date.now()}`, role: 'bot', text: reply.text, imageUrl: reply.imageUrl }
      setConversations(prev => prev.map(cv =>
        cv.id === activeConvId
          ? { ...cv, messages: [...cv.messages, botMsg], updatedAt: new Date().toISOString() }
          : cv
      ))
      setTyping(false)
    }, 720 + Math.random() * 380)
  }

  const username = user?.name?.split(' ')[0] ?? 'Usuario'

  return (
    <div style={{ padding: '24px 24px 32px', maxWidth: 1360, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* ── Page header ── */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.36, ease: [0.32, 0.72, 0, 1] }}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 11, background: `linear-gradient(135deg, ${BLUE}, #2563eb)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 20px rgba(59,130,246,0.30)', flexShrink: 0,
          }}>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
          </div>
          <div>
            <h1 style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.02em', color: c.t1, lineHeight: 1 }}>CARDEEP AI</h1>
            <p style={{ fontSize: 11, color: c.t4, marginTop: 3 }}>Asistente inteligente para dealers · mercado EU</p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <motion.span
            style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }}
            animate={{ opacity: [1, 0.4, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span style={{ fontSize: 11, color: '#22c55e', fontWeight: 600 }}>Online · {username}</span>
        </div>
      </motion.div>

      {/* ── Mode chips ── */}
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.07, duration: 0.32, ease: [0.32, 0.72, 0, 1] }}
        style={{ display: 'flex', gap: 8, flexShrink: 0, flexWrap: 'wrap' }}
      >
        {MODES.map(m => {
          const active = mode === m.id
          return (
            <button
              key={m.id}
              onClick={() => handleModeChange(m.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: 7,
                padding: '8px 16px', borderRadius: 99,
                background: active ? 'rgba(59,130,246,0.13)' : (dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)'),
                border: active ? '1px solid rgba(59,130,246,0.36)' : `1px solid ${c.cardBord}`,
                color: active ? BLUE : c.t3,
                fontSize: 12.5, fontWeight: active ? 700 : 500,
                fontFamily: 'General Sans, Inter, system-ui',
                cursor: 'pointer', transition: 'all 140ms',
                backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
              }}
            >
              <ModeIcon mode={m.id} size={12} />
              <span>{m.label}</span>
              <span style={{ fontSize: 10, color: active ? 'rgba(59,130,246,0.65)' : c.t4, fontWeight: 400 }}>
                {m.desc}
              </span>
            </button>
          )
        })}
      </motion.div>

      {/* ── Main layout: chat + sidebar ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.13, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
        style={{ display: 'grid', gridTemplateColumns: '1fr 276px', gap: 14, minHeight: 580 }}
      >

        {/* ── Chat panel ── */}
        <GCard dark={dark} style={{ display: 'flex', flexDirection: 'column' }}>

          {/* Chat header */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '14px 18px 12px', borderBottom: `1px solid ${c.div}`, flexShrink: 0,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
              <div style={{
                width: 30, height: 30, borderRadius: 9,
                background: 'rgba(59,130,246,0.11)', border: '1px solid rgba(59,130,246,0.22)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', color: BLUE,
              }}>
                <ModeIcon mode={mode} size={13} />
              </div>
              <div>
                <div style={{ fontSize: 12.5, fontWeight: 700, color: c.t1 }}>
                  {MODES.find(m => m.id === mode)?.label}
                </div>
                <div style={{ fontSize: 10, color: c.t4 }}>
                  {MODES.find(m => m.id === mode)?.desc}
                </div>
              </div>
            </div>
            <button
              onClick={startNew}
              style={{
                display: 'flex', alignItems: 'center', gap: 5,
                padding: '5px 12px', borderRadius: 8,
                background: 'rgba(59,130,246,0.09)', border: '1px solid rgba(59,130,246,0.22)',
                color: BLUE, fontSize: 11, fontWeight: 600,
                fontFamily: 'General Sans, Inter, system-ui', cursor: 'pointer', transition: 'all 130ms',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(59,130,246,0.17)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(59,130,246,0.09)' }}
            >
              <Plus style={{ width: 11, height: 11 }} />
              Nueva
            </button>
          </div>

          {/* Messages area */}
          <div
            ref={scrollRef}
            style={{
              flex: 1, overflowY: 'auto', padding: '18px 18px 10px',
              display: 'flex', flexDirection: 'column', gap: 12, minHeight: 0,
            }}
          >
            {/* Empty state */}
            {msgs.length === 0 && !typing && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center',
                  justifyContent: 'center', flex: 1, gap: 14, padding: '40px 24px',
                }}
              >
                <div style={{
                  width: 54, height: 54, borderRadius: 16,
                  background: 'rgba(59,130,246,0.09)', border: '1px solid rgba(59,130,246,0.18)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', color: BLUE,
                }}>
                  <ModeIcon mode={mode} size={22} />
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: c.t1, marginBottom: 6 }}>
                    {EMPTY[mode].heading}
                  </div>
                  <div style={{ fontSize: 12, color: c.t4, maxWidth: 300, lineHeight: 1.65 }}>
                    {EMPTY[mode].body}
                  </div>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, justifyContent: 'center', maxWidth: 400 }}>
                  {SUGGESTIONS[mode].slice(0, 3).map((s, i) => (
                    <button
                      key={i}
                      onClick={() => send(s)}
                      style={{
                        padding: '6px 12px', borderRadius: 99, fontSize: 11, cursor: 'pointer',
                        background: c.subBg, border: `1px solid ${c.subBord}`, color: c.t3,
                        fontFamily: 'General Sans, Inter, system-ui', transition: 'all 120ms',
                      }}
                      onMouseEnter={e => { e.currentTarget.style.background = 'rgba(59,130,246,0.08)'; e.currentTarget.style.color = BLUE; e.currentTarget.style.borderColor = 'rgba(59,130,246,0.22)' }}
                      onMouseLeave={e => { e.currentTarget.style.background = c.subBg; e.currentTarget.style.color = c.t3; e.currentTarget.style.borderColor = c.subBord }}
                    >
                      {s.length > 36 ? s.slice(0, 34) + '…' : s}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Message list */}
            <AnimatePresence initial={false}>
              {msgs.map(msg => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.22 }}
                  style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', gap: 8 }}
                >
                  {msg.role === 'bot' && <BotAvatar size={26} />}

                  <div style={{ maxWidth: '78%', display: 'flex', flexDirection: 'column', gap: 7 }}>
                    <div style={{
                      padding: '9px 13px',
                      borderRadius: msg.role === 'user' ? '14px 14px 4px 14px' : '4px 14px 14px 14px',
                      background: msg.role === 'user' ? `linear-gradient(135deg, ${BLUE}, #2563eb)` : c.botBubble,
                      border: msg.role === 'bot' ? `1px solid ${c.subBord}` : 'none',
                      fontSize: 12.5, lineHeight: 1.62, color: msg.role === 'user' ? '#fff' : c.t1,
                      boxShadow: msg.role === 'user' ? '0 3px 12px rgba(59,130,246,0.28)' : 'none',
                      whiteSpace: 'pre-wrap',
                    }}>
                      {msg.role === 'bot' ? renderBold(msg.text, c.t1) : msg.text}
                    </div>

                    {msg.imageUrl && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.96 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.12, duration: 0.32 }}
                        style={{
                          borderRadius: 12, overflow: 'hidden',
                          border: `1px solid ${c.cardBord}`, maxWidth: 400,
                        }}
                      >
                        <img src={msg.imageUrl} alt="Imagen generada" style={{ width: '100%', display: 'block' }} />
                        <div style={{
                          padding: '7px 12px', background: c.subBg, borderTop: `1px solid ${c.subBord}`,
                          fontSize: 10, color: c.t4, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        }}>
                          <span>Imagen generada · CARDEEP AI</span>
                          <span style={{
                            padding: '2px 7px', borderRadius: 99, fontSize: 9.5, fontWeight: 600,
                            background: 'rgba(59,130,246,0.10)', color: BLUE, border: '1px solid rgba(59,130,246,0.20)',
                          }}>
                            1920×1080
                          </span>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing indicator */}
            <AnimatePresence>
              {typing && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  style={{ display: 'flex', gap: 8, alignItems: 'center' }}
                >
                  <BotAvatar size={26} />
                  <div style={{
                    padding: '10px 14px', borderRadius: '4px 14px 14px 14px',
                    background: c.botBubble, border: `1px solid ${c.subBord}`,
                    display: 'flex', gap: 4, alignItems: 'center',
                  }}>
                    {[0, 1, 2].map(i => (
                      <motion.span
                        key={i}
                        style={{ width: 5, height: 5, borderRadius: '50%', background: c.t3, display: 'block' }}
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 0.55, repeat: Infinity, delay: i * 0.14 }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* ── Composer ── */}
          <div style={{ padding: '10px 14px 14px', borderTop: `1px solid ${c.div}`, flexShrink: 0 }}>
            <div style={{
              display: 'flex', gap: 10, alignItems: 'flex-end',
              background: c.inputBg,
              border: `1px solid ${composerFocused ? 'rgba(59,130,246,0.38)' : c.inputBord}`,
              borderRadius: 14, padding: '8px 8px 8px 14px',
              transition: 'border-color 150ms',
            }}>
              <textarea
                ref={textareaRef}
                value={input}
                rows={1}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) } }}
                onFocus={() => setComposerFocused(true)}
                onBlur={() => setComposerFocused(false)}
                placeholder={
                  mode === 'ask'     ? 'Pregunta sobre stock, márgenes, mercado EU…' :
                  mode === 'listing' ? 'Ej: BMW 320d 2021, 68.000 km, automático, blanco…' :
                  mode === 'vin'     ? 'Pega el VIN de 17 dígitos o matrícula…' :
                                       'Describe el coche: marca, color, ángulo, fondo…'
                }
                style={{
                  flex: 1, resize: 'none', outline: 'none', border: 'none',
                  background: 'transparent', color: c.t1, fontSize: 12.5,
                  fontFamily: 'General Sans, Inter, system-ui', lineHeight: 1.55,
                  overflowY: 'hidden',
                }}
              />
              <motion.button
                onClick={() => send(input)}
                disabled={!input.trim() || typing}
                whileTap={{ scale: 0.89 }}
                style={{
                  width: 34, height: 34, borderRadius: 10, flexShrink: 0, border: 'none',
                  background: input.trim() && !typing
                    ? `linear-gradient(135deg, ${BLUE}, #2563eb)`
                    : (dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.07)'),
                  cursor: input.trim() && !typing ? 'pointer' : 'default',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 140ms',
                  boxShadow: input.trim() && !typing ? '0 3px 10px rgba(59,130,246,0.28)' : 'none',
                }}
              >
                <Send style={{ width: 14, height: 14, color: input.trim() && !typing ? '#fff' : c.t4, transition: 'color 140ms' }} />
              </motion.button>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 5 }}>
              <span style={{ fontSize: 10, color: c.t4 }}>Enter para enviar · Shift+Enter nueva línea</span>
            </div>
          </div>
        </GCard>

        {/* ── Right sidebar ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {/* Suggested prompts */}
          <GCard dark={dark} style={{ flexShrink: 0 }}>
            <div style={{ padding: '14px 16px' }}>
              <div style={{
                fontSize: 9.5, fontWeight: 700, letterSpacing: '0.10em',
                textTransform: 'uppercase', color: c.t4, marginBottom: 11,
              }}>
                Sugerencias
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                <AnimatePresence mode="wait">
                  {SUGGESTIONS[mode].map((s, i) => (
                    <motion.button
                      key={`${mode}-${i}`}
                      initial={{ opacity: 0, x: 8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -6 }}
                      transition={{ delay: i * 0.04, duration: 0.20 }}
                      onClick={() => send(s)}
                      disabled={typing}
                      style={{
                        textAlign: 'left', width: '100%', display: 'flex', alignItems: 'flex-start', gap: 7,
                        padding: '7px 10px', borderRadius: 9,
                        background: c.subBg, border: `1px solid ${c.subBord}`,
                        color: c.t2, fontSize: 11,
                        fontFamily: 'General Sans, Inter, system-ui',
                        cursor: typing ? 'default' : 'pointer',
                        lineHeight: 1.45, transition: 'all 120ms',
                      }}
                      onMouseEnter={e => {
                        if (!typing) {
                          e.currentTarget.style.background = dark ? 'rgba(59,130,246,0.08)' : 'rgba(59,130,246,0.06)'
                          e.currentTarget.style.borderColor = 'rgba(59,130,246,0.20)'
                          e.currentTarget.style.color = c.t1
                        }
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.background = c.subBg
                        e.currentTarget.style.borderColor = c.subBord
                        e.currentTarget.style.color = c.t2
                      }}
                    >
                      <ChevronRight style={{ width: 10, height: 10, color: BLUE, flexShrink: 0, marginTop: 2 }} />
                      <span>{s}</span>
                    </motion.button>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </GCard>

          {/* Conversation history */}
          <GCard dark={dark} style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <div style={{ padding: '14px 16px', height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                marginBottom: 11, flexShrink: 0,
              }}>
                <div style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: c.t4 }}>
                  Historial
                </div>
                <span style={{ fontSize: 10, color: c.t4 }}>{conversations.length}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 5, overflowY: 'auto', flex: 1, minHeight: 0 }}>
                {conversations.map((conv, i) => {
                  const isActive = conv.id === activeConvId
                  return (
                    <motion.button
                      key={conv.id}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.04 }}
                      onClick={() => { setActiveConvId(conv.id); setMode(conv.mode) }}
                      style={{
                        textAlign: 'left', width: '100%', padding: '8px 10px', borderRadius: 9,
                        background: isActive ? 'rgba(59,130,246,0.09)' : c.subBg,
                        border: isActive ? '1px solid rgba(59,130,246,0.22)' : `1px solid ${c.subBord}`,
                        cursor: 'pointer', fontFamily: 'General Sans, Inter, system-ui',
                        transition: 'all 120ms', display: 'flex', flexDirection: 'column', gap: 3,
                      }}
                      onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)' }}
                      onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = c.subBg }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 5 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 5, minWidth: 0 }}>
                          <span style={{ color: isActive ? BLUE : c.t4, flexShrink: 0 }}>
                            <ModeIcon mode={conv.mode} size={10} />
                          </span>
                          <span style={{
                            fontSize: 11, fontWeight: isActive ? 700 : 500,
                            color: isActive ? c.t1 : c.t2,
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                          }}>
                            {conv.title}
                          </span>
                        </div>
                        <span style={{ fontSize: 9.5, color: c.t4, flexShrink: 0, fontVariantNumeric: 'tabular-nums' }}>
                          {timeAgo(conv.updatedAt)}
                        </span>
                      </div>
                      <div style={{ fontSize: 10, color: c.t4, paddingLeft: 15 }}>
                        {conv.messages.length}{' '}
                        {conv.messages.length === 1 ? 'mensaje' : 'mensajes'}
                      </div>
                    </motion.button>
                  )
                })}
              </div>
            </div>
          </GCard>

        </div>
      </motion.div>
    </div>
  )
}
