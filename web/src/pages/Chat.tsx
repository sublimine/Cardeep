import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Plus, Phone, Video, MoreHorizontal,
  Paperclip, Smile, Send, Check, CheckCheck,
  Users, Car,
} from 'lucide-react'
import Avatar from '../components/Avatar'
import Button from '../components/Button'
import Input from '../components/Input'
import { Badge } from '../components/Badge'
import { cn } from '../lib/cn'

// ── Types ─────────────────────────────────────────────────────────────────────

type UserStatus = 'online' | 'away' | 'offline'
type MsgStatus  = 'sent' | 'delivered' | 'read'
type ConvFilter = 'all' | 'unread' | 'groups'

interface InternalUser {
  id: string
  name: string
  role: string
  status: UserStatus
}

interface ChatMessage {
  id: string
  senderId: string
  body: string
  sentAt: string
  msgStatus: MsgStatus
}

interface DateGroup {
  label: string
  messages: ChatMessage[]
}

interface DealCtx {
  vehicle: string
  stage: string
  price: number
}

interface ChatConv {
  id: string
  isGroup: boolean
  peer: InternalUser
  groupName?: string
  groupMembers?: string[]
  lastBody: string
  lastAt: string
  unread: number
  messages: ChatMessage[]
  dealContext?: DealCtx
}

// ── Constants ─────────────────────────────────────────────────────────────────

const ME = 'me'

const USERS: Record<string, InternalUser> = {
  carlos: { id: 'carlos', name: 'Carlos Ruiz',   role: 'Sales Lead', status: 'online'  },
  ana:    { id: 'ana',    name: 'Ana Martínez',   role: 'Finance',    status: 'online'  },
  pedro:  { id: 'pedro',  name: 'Pedro Gómez',   role: 'Logistics',  status: 'away'    },
  sofia:  { id: 'sofia',  name: 'Sofía López',    role: 'Marketing',  status: 'offline' },
  miguel: { id: 'miguel', name: 'Miguel Torres',  role: 'Director',   status: 'online'  },
}

const SEED: ChatConv[] = [
  {
    id: 'cv1', isGroup: false, peer: USERS.carlos,
    lastBody: '¿Confirmamos la cita mañana a las 11?',
    lastAt: '2026-06-30T10:47:00Z', unread: 2,
    messages: [
      { id: 'm1', senderId: 'carlos', body: 'Hola, el lead del BMW 320d está muy caliente.', sentAt: '2026-06-29T09:10:00Z', msgStatus: 'read' },
      { id: 'm2', senderId: ME,       body: '¿Cuánto puede pagar?', sentAt: '2026-06-29T09:15:00Z', msgStatus: 'read' },
      { id: 'm3', senderId: 'carlos', body: 'Dice que máximo 24.500 €, pero creo que hay margen para negociar.', sentAt: '2026-06-29T09:18:00Z', msgStatus: 'read' },
      { id: 'm4', senderId: ME,       body: 'Coste a 22.100 €. A 24k cerramos en positivo. Adelante.', sentAt: '2026-06-29T09:22:00Z', msgStatus: 'read' },
      { id: 'm5', senderId: 'carlos', body: 'Perfecto. Confirmo cita para el testdrive el martes.', sentAt: '2026-06-29T09:25:00Z', msgStatus: 'read' },
      { id: 'm6', senderId: ME,       body: 'De acuerdo. Asegúrate de que el coche esté limpio y con ITV en regla.', sentAt: '2026-06-30T10:30:00Z', msgStatus: 'delivered' },
      { id: 'm7', senderId: 'carlos', body: '¿Confirmamos la cita mañana a las 11?', sentAt: '2026-06-30T10:47:00Z', msgStatus: 'sent' },
    ],
    dealContext: { vehicle: 'BMW 320d xDrive 2021', stage: 'Negotiation', price: 24_500 },
  },
  {
    id: 'cv2', isGroup: false, peer: USERS.ana,
    lastBody: 'El margen Q2 está en el 18,4%, por encima del objetivo.',
    lastAt: '2026-06-30T09:05:00Z', unread: 0,
    messages: [
      { id: 'n1', senderId: ME,    body: 'Ana, ¿tienes el cierre del margen de mayo?', sentAt: '2026-06-29T16:00:00Z', msgStatus: 'read' },
      { id: 'n2', senderId: 'ana', body: 'Sí, dame 5 minutos.', sentAt: '2026-06-29T16:04:00Z', msgStatus: 'read' },
      { id: 'n3', senderId: 'ana', body: 'El margen Q2 está en el 18,4%, por encima del objetivo.', sentAt: '2026-06-30T09:05:00Z', msgStatus: 'read' },
    ],
  },
  {
    id: 'cv3', isGroup: true, peer: USERS.miguel,
    groupName: 'Equipo Ventas',
    groupMembers: ['Carlos Ruiz', 'Ana Martínez', 'Pedro Gómez', 'Miguel Torres', 'Tú'],
    lastBody: 'Pipeline con 8 deals en negociación. Muy confiada.',
    lastAt: '2026-06-30T08:15:00Z', unread: 5,
    messages: [
      { id: 'g1', senderId: 'miguel', body: 'Buenos días equipo. Objetivo: 30 unidades este mes.', sentAt: '2026-06-30T08:00:00Z', msgStatus: 'read' },
      { id: 'g2', senderId: 'carlos', body: 'Llevamos 18, vamos bien encaminados.', sentAt: '2026-06-30T08:10:00Z', msgStatus: 'read' },
      { id: 'g3', senderId: 'ana',    body: 'Pipeline con 8 deals en negociación. Muy confiada.', sentAt: '2026-06-30T08:15:00Z', msgStatus: 'read' },
    ],
  },
  {
    id: 'cv4', isGroup: false, peer: USERS.pedro,
    lastBody: 'El Audi A4 llegará el jueves por la tarde.',
    lastAt: '2026-06-29T14:20:00Z', unread: 0,
    messages: [
      { id: 'p1', senderId: ME,      body: '¿Cuándo llega el Audi A4 de Múnich?', sentAt: '2026-06-29T13:50:00Z', msgStatus: 'read' },
      { id: 'p2', senderId: 'pedro', body: 'El Audi A4 llegará el jueves por la tarde.', sentAt: '2026-06-29T14:20:00Z', msgStatus: 'read' },
    ],
    dealContext: { vehicle: 'Audi A4 Avant 2.0 TDI 2022', stage: 'Incoming', price: 26_300 },
  },
  {
    id: 'cv5', isGroup: false, peer: USERS.sofia,
    lastBody: 'Las fotos del Golf están listas para publicar.',
    lastAt: '2026-06-28T17:45:00Z', unread: 0,
    messages: [
      { id: 's1', senderId: 'sofia', body: 'Las fotos del Golf están listas para publicar.', sentAt: '2026-06-28T17:45:00Z', msgStatus: 'read' },
      { id: 's2', senderId: ME,      body: 'Publícalas en mobile.de y AutoScout24. Buen trabajo.', sentAt: '2026-06-28T17:50:00Z', msgStatus: 'read' },
    ],
    dealContext: { vehicle: 'VW Golf 8 1.5 TSI 2023', stage: 'Listed', price: 27_900 },
  },
]

const FILTERS: { value: ConvFilter; label: string }[] = [
  { value: 'all',    label: 'Todos'      },
  { value: 'unread', label: 'No leídos'  },
  { value: 'groups', label: 'Grupos'     },
]

const STAGE_COLOR: Record<string, NonNullable<Parameters<typeof Badge>[0]['color']>> = {
  Negotiation: 'yellow', Offer: 'orange', Listed: 'blue',
  Incoming: 'gray', Won: 'green', Lost: 'red',
}

// ── Utilities ─────────────────────────────────────────────────────────────────

function fmtTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

function fmtConvDate(iso: string): string {
  const d    = new Date(iso)
  const diff = Date.now() - d.getTime()
  if (diff < 86_400_000)  return d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  if (diff < 172_800_000) return 'Ayer'
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

function groupByDate(msgs: ChatMessage[]): DateGroup[] {
  const result: DateGroup[] = []
  let curLabel = ''
  for (const msg of msgs) {
    const d    = new Date(msg.sentAt)
    const diff = Date.now() - d.getTime()
    const label =
      diff < 86_400_000  ? 'Hoy' :
      diff < 172_800_000 ? 'Ayer' :
      d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
    if (label !== curLabel) {
      curLabel = label
      result.push({ label, messages: [msg] })
    } else {
      result[result.length - 1].messages.push(msg)
    }
  }
  return result
}

// ── Read receipt ──────────────────────────────────────────────────────────────

function ReadReceipt({ status }: { status: MsgStatus }) {
  if (status === 'sent')
    return <Check className="w-3 h-3 text-white/40" />
  if (status === 'delivered')
    return <CheckCheck className="w-3 h-3 text-white/40" />
  return <CheckCheck className="w-3 h-3" style={{ color: '#93c5fd' }} />
}

// ── Date separator ────────────────────────────────────────────────────────────

function DateSep({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3 my-5 px-4">
      <div className="flex-1 h-px" style={{ background: 'var(--border-subtle)' }} />
      <span className="text-[11px] font-medium text-text-muted tracking-wide uppercase select-none">
        {label}
      </span>
      <div className="flex-1 h-px" style={{ background: 'var(--border-subtle)' }} />
    </div>
  )
}

// ── Message bubble ────────────────────────────────────────────────────────────

function MsgBubble({
  msg, isOut, senderName,
}: {
  msg: ChatMessage
  isOut: boolean
  senderName?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.14, ease: 'easeOut' }}
      className={cn('flex px-4', isOut ? 'justify-end' : 'justify-start')}
    >
      <div className={cn('flex flex-col gap-0.5 max-w-[72%]', isOut ? 'items-end' : 'items-start')}>
        {senderName && (
          <span className="text-[10px] font-semibold text-text-muted ml-1 mb-0.5">
            {senderName}
          </span>
        )}
        <div
          className={cn(
            'px-3.5 py-2.5 text-sm leading-relaxed break-words',
            isOut
              ? 'text-white rounded-2xl rounded-br-sm'
              : 'text-text-primary rounded-2xl rounded-bl-sm border border-border-subtle',
          )}
          style={
            isOut
              ? {
                  background: 'rgb(var(--color-blue-ch))',
                  boxShadow: '0 2px 10px rgba(37,99,235,0.28)',
                }
              : { background: 'var(--glass-medium)' }
          }
        >
          {msg.body}
        </div>
        <div className={cn('flex items-center gap-1 px-0.5', isOut ? 'flex-row-reverse' : 'flex-row')}>
          <span className="text-[10px] text-text-muted">{fmtTime(msg.sentAt)}</span>
          {isOut && <ReadReceipt status={msg.msgStatus} />}
        </div>
      </div>
    </motion.div>
  )
}

// ── Conversation list item ────────────────────────────────────────────────────

function ConvItem({
  conv, selected, onClick,
}: {
  conv: ChatConv
  selected: boolean
  onClick: () => void
}) {
  const displayName = conv.isGroup ? (conv.groupName ?? 'Grupo') : conv.peer.name

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-start gap-3 px-3 py-3 text-left',
        'border-b border-border-subtle transition-colors duration-100',
        selected ? 'bg-accent-blue/10' : 'hover:bg-glass-subtle',
      )}
    >
      <div className="relative shrink-0 mt-0.5">
        {conv.isGroup ? (
          <div className="w-8 h-8 rounded-full flex items-center justify-center ring-1 ring-accent-blue/30 bg-accent-blue/15">
            <Users className="w-4 h-4 text-accent-blue" />
          </div>
        ) : (
          <Avatar name={conv.peer.name} size="sm" status={conv.peer.status} />
        )}
        {conv.unread > 0 && (
          <span
            className="absolute -top-0.5 -right-0.5 min-w-[1rem] h-4 px-1 bg-accent-blue text-white text-[10px] font-bold rounded-full flex items-center justify-center leading-none ring-2 ring-bg-primary"
          >
            {conv.unread > 9 ? '9+' : conv.unread}
          </span>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-1 mb-0.5">
          <span
            className={cn(
              'text-sm truncate',
              conv.unread > 0 ? 'font-semibold text-text-primary' : 'font-medium text-text-secondary',
            )}
          >
            {displayName}
          </span>
          <span className="text-[10px] text-text-muted shrink-0">{fmtConvDate(conv.lastAt)}</span>
        </div>

        {!conv.isGroup && (
          <p className="text-[11px] text-text-muted mb-0.5">{conv.peer.role}</p>
        )}

        <p className={cn('text-xs truncate', conv.unread > 0 ? 'text-text-secondary' : 'text-text-muted')}>
          {conv.lastBody}
        </p>
      </div>
    </button>
  )
}

// ── Contact / group info (col-3 header) ───────────────────────────────────────

function ContactPanel({ conv }: { conv: ChatConv }) {
  const statusLabel: Record<UserStatus, string> = {
    online: 'En línea', away: 'Ausente', offline: 'Desconectado',
  }
  const statusColor: Record<UserStatus, NonNullable<Parameters<typeof Badge>[0]['color']>> = {
    online: 'green', away: 'yellow', offline: 'gray',
  }

  return (
    <div className="px-5 py-5 border-b border-border-subtle flex flex-col items-center text-center gap-3 shrink-0">
      {conv.isGroup ? (
        <>
          <div className="w-14 h-14 rounded-full bg-accent-blue/15 ring-2 ring-accent-blue/25 flex items-center justify-center">
            <Users className="w-6 h-6 text-accent-blue" />
          </div>
          <div>
            <p className="text-sm font-semibold text-text-primary">{conv.groupName}</p>
            <p className="text-xs text-text-muted mt-0.5">
              {conv.groupMembers?.length ?? 0} miembros
            </p>
          </div>
          <div className="flex flex-wrap gap-1 justify-center">
            {conv.groupMembers?.map((m) => (
              <Badge key={m} color="gray">{m}</Badge>
            ))}
          </div>
        </>
      ) : (
        <>
          <Avatar name={conv.peer.name} size="lg" status={conv.peer.status} />
          <div>
            <p className="text-sm font-semibold text-text-primary">{conv.peer.name}</p>
            <p className="text-xs text-text-muted">{conv.peer.role}</p>
          </div>
          <Badge color={statusColor[conv.peer.status]}>{statusLabel[conv.peer.status]}</Badge>
          <div className="flex gap-2">
            <button
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-text-secondary border border-border-subtle hover:bg-glass-subtle transition-colors duration-100"
            >
              <Phone className="w-3.5 h-3.5" />
              Llamar
            </button>
            <button
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-text-secondary border border-border-subtle hover:bg-glass-subtle transition-colors duration-100"
            >
              <Video className="w-3.5 h-3.5" />
              Video
            </button>
          </div>
        </>
      )}
    </div>
  )
}

// ── Deal context card ─────────────────────────────────────────────────────────

function DealCard({ ctx }: { ctx: DealCtx }) {
  return (
    <div
      className="rounded-lg border border-border-subtle p-3"
      style={{ background: 'var(--glass-subtle)' }}
    >
      <div className="flex items-center gap-2 mb-2">
        <Car className="w-3.5 h-3.5 text-accent-blue shrink-0" />
        <span className="text-xs font-medium text-text-secondary truncate">{ctx.vehicle}</span>
      </div>
      <div className="flex items-center justify-between">
        <Badge color={STAGE_COLOR[ctx.stage] ?? 'gray'}>{ctx.stage}</Badge>
        <span className="text-xs font-semibold text-text-primary">
          {ctx.price.toLocaleString('es-ES')} €
        </span>
      </div>
    </div>
  )
}

// ── Compose area ──────────────────────────────────────────────────────────────

function ComposeArea({
  draft, onChange, onSend,
}: {
  draft: string
  onChange: (v: string) => void
  onSend: () => void
}) {
  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div className="p-3 border-t border-border-subtle shrink-0">
      <div
        className="rounded-xl border border-border-subtle overflow-hidden"
        style={{ background: 'var(--glass-subtle)' }}
      >
        <textarea
          value={draft}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Escribe un mensaje… (⌘+Enter para enviar)"
          rows={3}
          className={cn(
            'w-full px-4 py-3 text-sm text-text-primary placeholder:text-text-muted',
            'bg-transparent border-none resize-none',
            'focus:outline-none',
          )}
        />
        <div className="flex items-center justify-between px-3 py-2 border-t border-border-subtle">
          <div className="flex items-center gap-0.5">
            <button
              className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-glass-medium transition-colors duration-100"
              title="Adjuntar archivo"
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <button
              className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-glass-medium transition-colors duration-100"
              title="Emoji"
            >
              <Smile className="w-4 h-4" />
            </button>
          </div>
          <Button
            variant="primary"
            size="sm"
            icon={<Send className="w-3 h-3" />}
            onClick={onSend}
            disabled={!draft.trim()}
          >
            Enviar
          </Button>
        </div>
      </div>
    </div>
  )
}

// ── Panel background style ────────────────────────────────────────────────────

const PANEL: React.CSSProperties = {
  background: 'var(--bg-elevated)',
  boxShadow: 'var(--shadow-card)',
}

// ── Chat page ─────────────────────────────────────────────────────────────────

export default function Chat() {
  const [convs, setConvs]           = useState<ChatConv[]>(SEED)
  const [selectedId, setSelectedId] = useState<string>('cv1')
  const [search, setSearch]         = useState('')
  const [filter, setFilter]         = useState<ConvFilter>('all')
  const [draft, setDraft]           = useState('')
  const bottomRef                   = useRef<HTMLDivElement>(null)

  const conv = convs.find((c) => c.id === selectedId) ?? convs[0]

  // Filtered + sorted conversation list
  const sorted = [...convs]
    .filter((c) => {
      if (filter === 'unread' && c.unread === 0) return false
      if (filter === 'groups' && !c.isGroup) return false
      if (search) {
        const q    = search.toLowerCase()
        const name = conv?.isGroup ? (c.groupName ?? '').toLowerCase() : c.peer.name.toLowerCase()
        if (!name.includes(q) && !c.lastBody.toLowerCase().includes(q)) return false
      }
      return true
    })
    .sort((a, b) => new Date(b.lastAt).getTime() - new Date(a.lastAt).getTime())

  const dateGroups = conv ? groupByDate(conv.messages) : []
  const totalUnread = convs.reduce((s, c) => s + c.unread, 0)

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conv?.messages.length, selectedId])

  function selectConv(id: string) {
    setSelectedId(id)
    setConvs((prev) => prev.map((c) => (c.id === id ? { ...c, unread: 0 } : c)))
    setDraft('')
  }

  function sendMessage() {
    if (!draft.trim() || !conv) return
    const msg: ChatMessage = {
      id: `msg-${Date.now()}`,
      senderId: ME,
      body: draft.trim(),
      sentAt: new Date().toISOString(),
      msgStatus: 'sent',
    }
    setConvs((prev) =>
      prev.map((c) =>
        c.id === selectedId
          ? { ...c, messages: [...c.messages, msg], lastBody: msg.body, lastAt: msg.sentAt }
          : c,
      ),
    )
    setDraft('')
  }

  return (
    <div className="flex h-full overflow-hidden">

      {/* ── Column 1: Conversation list ── */}
      <aside
        className="w-[17rem] shrink-0 flex flex-col border-r border-border-subtle"
        style={PANEL}
      >
        {/* Header */}
        <div className="px-4 pt-4 pb-3 border-b border-border-subtle shrink-0">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h2 className="text-[15px] font-bold text-text-primary tracking-tight">Mensajes</h2>
              {totalUnread > 0 && (
                <span
                  className="px-1.5 py-px bg-accent-blue text-white text-[10px] font-bold rounded-full leading-none"
                  style={{ boxShadow: '0 0 10px rgba(37,99,235,0.38)' }}
                >
                  {totalUnread}
                </span>
              )}
            </div>
            <button
              className="w-7 h-7 flex items-center justify-center rounded-md text-text-muted hover:text-accent-blue hover:bg-accent-blue/10 transition-colors duration-100"
              title="Nueva conversación"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <Input
            icon={<Search className="w-3.5 h-3.5" />}
            placeholder="Buscar…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Filter tabs */}
        <div className="flex gap-0.5 px-3 py-2 border-b border-border-subtle shrink-0">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={cn(
                'relative flex-1 py-1.5 text-xs font-medium rounded-md transition-colors duration-150',
                filter === f.value ? 'text-accent-blue' : 'text-text-muted hover:text-text-secondary',
              )}
            >
              {filter === f.value && (
                <motion.div
                  layoutId="chat-filter"
                  className="absolute inset-0 rounded-md bg-accent-blue/10"
                  transition={{ type: 'spring', stiffness: 420, damping: 36 }}
                />
              )}
              <span className="relative z-10">{f.label}</span>
            </button>
          ))}
        </div>

        {/* Conv list */}
        <div className="flex-1 overflow-y-auto">
          <AnimatePresence initial={false}>
            {sorted.map((c) => (
              <motion.div
                key={c.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.12 }}
              >
                <ConvItem
                  conv={c}
                  selected={c.id === selectedId}
                  onClick={() => selectConv(c.id)}
                />
              </motion.div>
            ))}
          </AnimatePresence>
          {sorted.length === 0 && (
            <p className="text-center text-xs text-text-muted py-8">Sin resultados</p>
          )}
        </div>
      </aside>

      {/* ── Column 2: Message thread ── */}
      <div className="flex-1 flex flex-col min-w-0 border-r border-border-subtle" style={PANEL}>
        {conv ? (
          <>
            {/* Thread header */}
            <div
              className="flex items-center justify-between px-5 py-3 border-b border-border-subtle shrink-0"
              style={{ background: 'var(--bg-elevated)' }}
            >
              <div className="flex items-center gap-3 min-w-0">
                {conv.isGroup ? (
                  <div className="w-8 h-8 rounded-full bg-accent-blue/15 ring-1 ring-accent-blue/25 flex items-center justify-center shrink-0">
                    <Users className="w-4 h-4 text-accent-blue" />
                  </div>
                ) : (
                  <Avatar name={conv.peer.name} size="sm" status={conv.peer.status} />
                )}
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-text-primary truncate">
                    {conv.isGroup ? conv.groupName : conv.peer.name}
                  </p>
                  <p className="text-[11px] text-text-muted">
                    {conv.isGroup
                      ? `${conv.groupMembers?.length ?? 0} miembros`
                      : conv.peer.role}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-0.5 shrink-0">
                {(['phone', 'video', 'more'] as const).map((action) => (
                  <button
                    key={action}
                    className="w-8 h-8 flex items-center justify-center rounded-md text-text-muted hover:text-text-primary hover:bg-glass-subtle transition-colors duration-100"
                  >
                    {action === 'phone'  && <Phone className="w-4 h-4" />}
                    {action === 'video'  && <Video className="w-4 h-4" />}
                    {action === 'more'   && <MoreHorizontal className="w-4 h-4" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto py-2">
              {dateGroups.map((group) => (
                <React.Fragment key={group.label}>
                  <DateSep label={group.label} />
                  <div className="flex flex-col gap-2 pb-1">
                    {group.messages.map((msg) => {
                      const isOut      = msg.senderId === ME
                      const sender     = USERS[msg.senderId]
                      const showName   = conv.isGroup && !isOut
                      return (
                        <MsgBubble
                          key={msg.id}
                          msg={msg}
                          isOut={isOut}
                          senderName={showName ? (sender?.name ?? msg.senderId) : undefined}
                        />
                      )
                    })}
                  </div>
                </React.Fragment>
              ))}
              <div ref={bottomRef} className="h-2" />
            </div>

            {/* Compose — only on non-xl screens (col 3 is hidden there) */}
            <div className="xl:hidden">
              <ComposeArea draft={draft} onChange={setDraft} onSend={sendMessage} />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-sm text-text-muted">Selecciona una conversación</p>
          </div>
        )}
      </div>

      {/* ── Column 3: Contact info + Compose ── */}
      <aside
        className="hidden xl:flex w-[19rem] shrink-0 flex-col border-l border-border-subtle"
        style={PANEL}
      >
        {conv ? (
          <>
            <ContactPanel conv={conv} />

            {/* Scrollable context area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {conv.dealContext && (
                <>
                  <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider">
                    Contexto del deal
                  </p>
                  <DealCard ctx={conv.dealContext} />
                </>
              )}
            </div>

            <ComposeArea draft={draft} onChange={setDraft} onSend={sendMessage} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center p-6 text-center">
            <p className="text-sm text-text-muted">
              Selecciona una conversación para ver los detalles
            </p>
          </div>
        )}
      </aside>

    </div>
  )
}
