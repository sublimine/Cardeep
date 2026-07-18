import { motion, AnimatePresence } from 'framer-motion'
import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  MessageSquare, FileText, Search, Send, Plus, ChevronRight, ArrowRight,
} from 'lucide-react'
import Card from '../components/Card'
import { useAuthContext } from '../auth/AuthContext'
import { ACCENT, GOOD } from '../lib/theme'

// ── renderBold — **text** → <strong> ──────────────────────────────────────────
function renderBold(text: string): React.ReactNode {
  return text.split(/\*\*(.*?)\*\*/g).map((part, i) =>
    i % 2 === 1 ? <strong key={i} className="font-bold" style={{ color: 'var(--text-primary)' }}>{part}</strong> : <span key={i}>{part}</span>
  )
}

// ── Types ──────────────────────────────────────────────────────────────────────
// 07-marketing F0: mode 'image' REMOVED (demolition, not renamed). It rendered
// Math.floor(Math.random() * CAR_IMAGES.length) over 5 hardcoded Unsplash stock
// photos, labeled "Imagen generada" — a fabricated-capability lie the project's own
// antialucinación doctrine forbids (plans/cardeep-omni/07-marketing.md S1.1/S6
// "Demoliciones ligadas" (a)). No car-image generation exists anywhere in Cardeep;
// pretending otherwise client-side is worse than having no feature at all.
type Mode = 'ask' | 'listing' | 'vin'

interface ChatMsg { id: string; role: 'user' | 'bot'; text: string }
interface Conversation { id: string; title: string; mode: Mode; messages: ChatMsg[]; updatedAt: string }

const MODES: { id: Mode; label: string; desc: string }[] = [
  { id: 'ask',     label: 'Preguntar',              desc: 'Stock · precios · mercado EU'  },
  { id: 'listing', label: 'Descripción de anuncio', desc: 'Genera texto de venta'          },
  { id: 'vin',     label: 'Valorar VIN',             desc: 'Tasación por VIN o matrícula'  },
]

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
}

const EMPTY: Record<Mode, { heading: string; body: string }> = {
  ask:     { heading: 'Pregunta sobre tu negocio',           body: 'Consulta stock, márgenes, pipeline y alertas del mercado EU en tiempo real.' },
  listing: { heading: 'Genera una descripción de anuncio',   body: 'Indica marca, modelo, año y km. Obtendrás un texto profesional listo para publicar.' },
  vin:     { heading: 'Valora un VIN o matrícula',           body: 'Pega el VIN de 17 dígitos para historial completo y tasación EU al instante.' },
}

const NEW_TITLE: Record<Mode, string> = { ask: 'Nueva consulta', listing: 'Nuevo anuncio', vin: 'Nueva valoración' }

function botReply(mode: Mode, text: string): { text: string } {
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

  // mode === 'listing' has no branch here: 07-marketing F5 redirects that mode to
  // Marketing.tsx's Bloque 4 (ListingRedirectPanel below) before `send()` is ever
  // reachable — see plans/cardeep-omni/07-marketing.md S6 "(b) Assistant.tsx modo
  // listing redirige al Bloque 4". The old fake copy-generation text this branch used
  // to return is gone, not merely unreachable.

  if (mode === 'vin') {
    const vinMatch = text.match(/[A-HJ-NPR-Z0-9]{17}/i)
    const vin = vinMatch ? vinMatch[0].toUpperCase() : text.trim().toUpperCase().slice(0, 17)
    return {
      text: `**VIN analizado:** \`${vin || 'N/D'}\`\n\n📋 **Historial:** Sin siniestros registrados · 2 propietarios anteriores · ITV en vigor\n\n💰 **Valoración CARDEEP:** **€24.200 – €26.800** (mediana EU: €25.400)\n\n📊 **Posición de mercado:** −4.2% bajo mediana → precio competitivo\n\n⚠️ Kilometraje declarado coherente con desgaste mecánico. Sin anomalías detectadas.`,
    }
  }

  return { text: 'No entendí la consulta. Intenta de nuevo.' }
}

function ModeIcon({ mode, size = 13 }: { mode: Mode; size?: number }) {
  const p = { width: size, height: size }
  if (mode === 'ask')     return <MessageSquare {...p} />
  if (mode === 'listing') return <FileText {...p} />
  return <Search {...p} />
}

// 07-marketing F5 (plans/cardeep-omni/07-marketing.md S6, demolición (b)): el modo
// "Descripción de anuncio" ya no fabrica texto con regex+plantilla — redirige al
// Bloque 4 de Marketing ("Descripción con pruebas"), donde el copy se genera desde
// hechos verificados del censo, con cada cifra trazada a su fuente.
function ListingRedirectPanel() {
  const navigate = useNavigate()
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3.5 p-[40px_24px]">
      <div className="flex h-[54px] w-[54px] items-center justify-center rounded-2xl" style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}2e`, color: ACCENT }}>
        <FileText style={{ width: 22, height: 22 }} />
      </div>
      <div className="text-center">
        <div className="mb-1.5 text-sm font-bold" style={{ color: 'var(--text-primary)' }}>Ahora con pruebas, no con plantillas</div>
        <div className="mx-auto max-w-[340px] text-xs leading-[1.65]" style={{ color: 'var(--text-muted)' }}>
          La descripción de anuncio se mudó a Marketing → "Descripción con pruebas": eliges un coche real de
          tu inventario y cada afirmación del texto trae su fuente (posición de precio, kilometraje, presencia
          en plataformas) — nunca una plantilla genérica rellenada con lo que escribas aquí.
        </div>
      </div>
      <button
        onClick={() => navigate('/marketing')}
        className="flex items-center gap-1.5 rounded-full px-4 py-2 text-[12px] font-semibold transition-colors"
        style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}38`, color: ACCENT }}
      >
        Ir a Marketing <ArrowRight style={{ width: 13, height: 13 }} />
      </button>
    </div>
  )
}

function BotAvatar({ size = 24 }: { size?: number }) {
  return (
    <div
      className="flex shrink-0 items-center justify-center self-start"
      style={{ width: size, height: size, borderRadius: Math.round(size * 0.29), background: `linear-gradient(135deg, ${ACCENT}, #2563eb)`, boxShadow: `0 2px 8px ${ACCENT}4d` }}
    >
      <svg width={size * 0.42} height={size * 0.42} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
    </div>
  )
}

function timeAgo(iso: string): string {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000)
  if (m < 1)  return 'ahora'
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  return h < 24 ? `${h}h` : `${Math.floor(h / 24)}d`
}

// ── Assistant page ─────────────────────────────────────────────────────────────
export default function Assistant() {
  const { user } = useAuthContext()

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

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [msgs.length, typing])

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`
  }, [input])

  function handleModeChange(m: Mode) {
    setMode(m)
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
      const botMsg: ChatMsg = { id: `b-${Date.now()}`, role: 'bot', text: reply.text }
      setConversations(prev => prev.map(cv =>
        cv.id === activeConvId ? { ...cv, messages: [...cv.messages, botMsg], updatedAt: new Date().toISOString() } : cv
      ))
      setTyping(false)
    }, 720 + Math.random() * 380)
  }

  const username = user?.name?.split(' ')[0] ?? 'Usuario'

  return (
    <div className="mx-auto flex flex-col gap-4" style={{ padding: '24px 24px 32px', maxWidth: 1360 }}>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.36, ease: [0.32, 0.72, 0, 1] }} className="flex shrink-0 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-[38px] w-[38px] shrink-0 items-center justify-center rounded-[11px]" style={{ background: `linear-gradient(135deg, ${ACCENT}, #2563eb)`, boxShadow: `0 0 20px ${ACCENT}4d` }}>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-extrabold leading-none tracking-[-0.02em]" style={{ color: 'var(--text-primary)' }}>CARDEEP AI</h1>
            <p className="mt-[3px] text-[11px]" style={{ color: 'var(--text-muted)' }}>Asistente inteligente para dealers · mercado EU</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <motion.span className="inline-block h-1.5 w-1.5 rounded-full" style={{ background: GOOD }} animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 2, repeat: Infinity }} />
          <span className="text-[11px] font-semibold" style={{ color: GOOD }}>Online · {username}</span>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.07, duration: 0.32, ease: [0.32, 0.72, 0, 1] }} className="flex shrink-0 flex-wrap gap-2">
        {MODES.map(m => {
          const active = mode === m.id
          return (
            <button
              key={m.id}
              onClick={() => handleModeChange(m.id)}
              className="flex items-center gap-[7px] rounded-full px-4 py-2 text-[12.5px] transition-colors"
              style={{
                background: active ? `${ACCENT}21` : 'var(--bg-surface)',
                border: `1px solid ${active ? `${ACCENT}5c` : 'var(--border-subtle)'}`,
                color: active ? ACCENT : 'var(--text-secondary)',
                fontWeight: active ? 700 : 500,
              }}
            >
              <ModeIcon mode={m.id} size={12} />
              <span>{m.label}</span>
              <span className="text-[10px] font-normal" style={{ color: active ? `${ACCENT}a6` : 'var(--text-muted)' }}>{m.desc}</span>
            </button>
          )
        })}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.13, duration: 0.44, ease: [0.32, 0.72, 0, 1] }}
        className="grid gap-3.5"
        style={{ gridTemplateColumns: '1fr 276px', minHeight: 580 }}
      >

        <Card className="!p-0 flex flex-col">

          <div className="flex shrink-0 items-center justify-between p-[14px_18px_12px]" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
            <div className="flex items-center gap-[9px]">
              <div className="flex h-[30px] w-[30px] items-center justify-center rounded-[9px]" style={{ background: `${ACCENT}1c`, border: `1px solid ${ACCENT}38`, color: ACCENT }}>
                <ModeIcon mode={mode} size={13} />
              </div>
              <div>
                <div className="text-[12.5px] font-bold" style={{ color: 'var(--text-primary)' }}>{MODES.find(m => m.id === mode)?.label}</div>
                <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{MODES.find(m => m.id === mode)?.desc}</div>
              </div>
            </div>
            <button
              onClick={startNew}
              className="flex items-center gap-[5px] rounded-lg px-3 py-1 text-[11px] font-semibold transition-colors"
              style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}38`, color: ACCENT }}
            >
              <Plus style={{ width: 11, height: 11 }} />
              Nueva
            </button>
          </div>

          {mode === 'listing' ? (
            <ListingRedirectPanel />
          ) : (
          <>
          <div ref={scrollRef} className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-[18px_18px_10px]">
            {msgs.length === 0 && !typing && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-1 flex-col items-center justify-center gap-3.5 p-[40px_24px]">
                <div className="flex h-[54px] w-[54px] items-center justify-center rounded-2xl" style={{ background: `${ACCENT}17`, border: `1px solid ${ACCENT}2e`, color: ACCENT }}>
                  <ModeIcon mode={mode} size={22} />
                </div>
                <div className="text-center">
                  <div className="mb-1.5 text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{EMPTY[mode].heading}</div>
                  <div className="mx-auto max-w-[300px] text-xs leading-[1.65]" style={{ color: 'var(--text-muted)' }}>{EMPTY[mode].body}</div>
                </div>
                <div className="flex max-w-[400px] flex-wrap justify-center gap-1.5">
                  {SUGGESTIONS[mode].slice(0, 3).map((s, i) => (
                    <button
                      key={i}
                      onClick={() => send(s)}
                      className="rounded-full px-3 py-1.5 text-[11px] transition-colors"
                      style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}
                    >
                      {s.length > 36 ? s.slice(0, 34) + '…' : s}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            <AnimatePresence initial={false}>
              {msgs.map(msg => (
                <motion.div key={msg.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22 }} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'bot' && <BotAvatar size={26} />}

                  <div className="flex max-w-[78%] flex-col gap-[7px]">
                    <div
                      className="whitespace-pre-wrap p-[9px_13px] text-[12.5px] leading-[1.62]"
                      style={{
                        borderRadius: msg.role === 'user' ? '14px 14px 4px 14px' : '4px 14px 14px 14px',
                        background: msg.role === 'user' ? `linear-gradient(135deg, ${ACCENT}, #2563eb)` : 'var(--bg-surface)',
                        border: msg.role === 'bot' ? '1px solid var(--border-subtle)' : 'none',
                        color: msg.role === 'user' ? '#fff' : 'var(--text-primary)',
                        boxShadow: msg.role === 'user' ? `0 3px 12px ${ACCENT}48` : 'none',
                      }}
                    >
                      {msg.role === 'bot' ? renderBold(msg.text) : msg.text}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            <AnimatePresence>
              {typing && (
                <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex items-center gap-2">
                  <BotAvatar size={26} />
                  <div className="flex items-center gap-1 rounded-[4px_14px_14px_14px] p-[10px_14px]" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
                    {[0, 1, 2].map(i => (
                      <motion.span key={i} className="block h-[5px] w-[5px] rounded-full" style={{ background: 'var(--text-secondary)' }} animate={{ y: [0, -5, 0] }} transition={{ duration: 0.55, repeat: Infinity, delay: i * 0.14 }} />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="shrink-0 p-[10px_14px_14px]" style={{ borderTop: '1px solid var(--border-subtle)' }}>
            <div
              className="flex items-end gap-2.5 rounded-2xl p-[8px_8px_8px_14px] transition-colors"
              style={{ background: 'var(--bg-input)', border: `1px solid ${composerFocused ? `${ACCENT}61` : 'var(--border-default)'}` }}
            >
              <textarea
                ref={textareaRef}
                value={input}
                rows={1}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) } }}
                onFocus={() => setComposerFocused(true)}
                onBlur={() => setComposerFocused(false)}
                placeholder={
                  // 'listing' never reaches this composer — see the mode==='listing'
                  // branch above (ListingRedirectPanel) that replaces this whole area.
                  mode === 'ask' ? 'Pregunta sobre stock, márgenes, mercado EU…' : 'Pega el VIN de 17 dígitos o matrícula…'
                }
                className="flex-1 resize-none overflow-y-hidden border-0 bg-transparent text-[12.5px] leading-[1.55] outline-none"
                style={{ color: 'var(--text-primary)' }}
              />
              <motion.button
                onClick={() => send(input)}
                disabled={!input.trim() || typing}
                whileTap={{ scale: 0.89 }}
                className="flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-[10px] border-0 transition-colors"
                style={{
                  background: input.trim() && !typing ? `linear-gradient(135deg, ${ACCENT}, #2563eb)` : 'var(--bg-surface)',
                  cursor: input.trim() && !typing ? 'pointer' : 'default',
                  boxShadow: input.trim() && !typing ? `0 3px 10px ${ACCENT}48` : 'none',
                }}
              >
                <Send style={{ width: 14, height: 14, color: input.trim() && !typing ? '#fff' : 'var(--text-muted)' }} />
              </motion.button>
            </div>
            <div className="mt-1.5 flex justify-end">
              <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Enter para enviar · Shift+Enter nueva línea</span>
            </div>
          </div>
          </>
          )}
        </Card>

        <div className="flex flex-col gap-3">

          <Card className="shrink-0">
            <div className="mb-[11px] text-[9.5px] font-bold uppercase tracking-[0.10em]" style={{ color: 'var(--text-muted)' }}>Sugerencias</div>
            <div className="flex flex-col gap-[5px]">
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
                    className="flex w-full items-start gap-[7px] rounded-lg p-[7px_10px] text-left text-[11px] leading-[1.45] transition-colors"
                    style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', cursor: typing ? 'default' : 'pointer' }}
                  >
                    <ChevronRight style={{ width: 10, height: 10, color: ACCENT, flexShrink: 0, marginTop: 2 }} />
                    <span>{s}</span>
                  </motion.button>
                ))}
              </AnimatePresence>
            </div>
          </Card>

          <Card className="min-h-0 flex-1 overflow-hidden">
            <div className="flex h-full min-h-0 flex-col">
              <div className="mb-[11px] flex shrink-0 items-center justify-between">
                <div className="text-[9.5px] font-bold uppercase tracking-[0.10em]" style={{ color: 'var(--text-muted)' }}>Historial</div>
                <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{conversations.length}</span>
              </div>

              <div className="flex min-h-0 flex-1 flex-col gap-[5px] overflow-y-auto">
                {conversations.map((conv, i) => {
                  const isActive = conv.id === activeConvId
                  return (
                    <motion.button
                      key={conv.id}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.04 }}
                      onClick={() => { setActiveConvId(conv.id); setMode(conv.mode) }}
                      className="flex w-full flex-col gap-[3px] rounded-lg p-[8px_10px] text-left transition-colors"
                      style={{ background: isActive ? `${ACCENT}17` : 'var(--bg-surface)', border: `1px solid ${isActive ? `${ACCENT}38` : 'var(--border-subtle)'}` }}
                    >
                      <div className="flex items-center justify-between gap-1.5">
                        <div className="flex min-w-0 items-center gap-1.5">
                          <span className="shrink-0" style={{ color: isActive ? ACCENT : 'var(--text-muted)' }}><ModeIcon mode={conv.mode} size={10} /></span>
                          <span className="truncate text-[11px]" style={{ fontWeight: isActive ? 700 : 500, color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{conv.title}</span>
                        </div>
                        <span className="shrink-0 text-[9.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>{timeAgo(conv.updatedAt)}</span>
                      </div>
                      <div className="pl-[15px] text-[10px]" style={{ color: 'var(--text-muted)' }}>{conv.messages.length} {conv.messages.length === 1 ? 'mensaje' : 'mensajes'}</div>
                    </motion.button>
                  )
                })}
              </div>
            </div>
          </Card>

        </div>
      </motion.div>
    </div>
  )
}
