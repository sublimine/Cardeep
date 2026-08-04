import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageSquare, RefreshCw, Inbox as InboxIcon } from 'lucide-react'
import Card from '../components/Card'
import Avatar from '../components/Avatar'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'
import { Skeleton } from '../components/Skeleton'
import Button from '../components/Button'
import { Badge } from '../components/Badge'
import { useInbox, useConversation, useInboxMutations, useInboxStream } from '../hooks/useInbox'
import { useToast } from '../components/Toast'
import type { Conversation, Message } from '../types'
import { cn } from '../lib/cn'

// HISTORY (00-MASTER.md C-10, "regla del primer llegado"): 05-multiposting F2 retired this
// file's original fake-conversations fallback before 06-unified-crm-chat had landed,
// leaving an honest "not connected yet" empty state. 06-F4 now ships the real channel
// (services/api/routers/crm_inbox.py + services/crm/email_ingest.py + email_send.py) against
// the exact paths useInbox.ts already called — the empty state below reflects that reality:
// a real, empty inbox ("conecta tu correo...") is distinct from a request that failed.

const STATUS_COLOR: Record<string, NonNullable<Parameters<typeof Badge>[0]['color']>> = {
  open: 'blue', replied: 'green', closed: 'gray', spam: 'red',
}

const STATUS_LABEL: Record<string, string> = {
  open: 'Abierto', replied: 'Respondido', closed: 'Cerrado', spam: 'Spam',
}

type Filter = 'all' | 'unread'

const FILTER_LABEL: Record<Filter, string> = { all: 'Todas', unread: 'No leídas' }

// Skeleton-friendly stagger cap — beyond ~6 rows the extra delay stops reading as
// "arriving in sequence" and just reads as "slow", so every list clamps to this.
const MAX_STAGGER_DELAY = 0.3
const STAGGER_STEP = 0.03

function ConvItem({
  conv, selected, onClick,
}: { conv: Conversation; selected: boolean; onClick: () => void }) {
  const date = new Date(conv.lastMessageAt).toLocaleDateString('es-ES', {
    day: 'numeric', month: 'short',
  })

  return (
    <motion.button
      type="button"
      onClick={onClick}
      whileTap={{ scale: 0.995 }}
      aria-current={selected ? 'true' : undefined}
      className={cn(
        'w-full flex items-start gap-3 px-4 py-3.5 text-left border-b border-border-subtle',
        'transition-colors duration-100',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent-blue/40',
        selected ? 'bg-accent-blue/10' : 'hover:bg-glass-subtle',
      )}
    >
      <div className="relative mt-0.5">
        <Avatar name={conv.contactName ?? '?'} size="sm" />
        {conv.unread && (
          <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-accent-blue ring-2 ring-bg-primary animate-pulse" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-0.5">
          <span
            className={cn(
              'text-sm truncate',
              conv.unread ? 'font-semibold text-text-primary' : 'font-medium text-text-secondary',
            )}
          >
            {conv.contactName}
          </span>
          <span className="text-[10px] text-text-muted shrink-0 tabular-nums">{date}</span>
        </div>

        <p
          className={cn(
            'text-xs truncate',
            conv.unread ? 'text-text-secondary font-medium' : 'text-text-muted',
          )}
        >
          {conv.subject}
        </p>

        <p className="text-xs text-text-muted truncate mt-0.5">{conv.previewBody}</p>

        {/* F5: census cross-reference chip — carta §6: "BMW 320d 2019 · 18.900 € ·
            34 días en tu stock". Only rendered when it resolved for real. */}
        {conv.vehicleContext && (
          <p className={cn(
            'text-[10px] truncate mt-1 tabular-nums',
            conv.vehicleContext.stillListed ? 'text-accent-blue' : 'text-rose-400 font-semibold',
          )}>
            {conv.vehicleName}
            {conv.vehicleContext.stillListed
              ? ` · ${conv.vehicleContext.daysInStock}d en tu stock`
              : ' · ya no está anunciado'}
          </p>
        )}

        <div className="flex items-center gap-1.5 mt-2">
          <Badge color={STATUS_COLOR[conv.status] ?? 'gray'}>{STATUS_LABEL[conv.status] ?? conv.status}</Badge>
          <span className="text-[10px] text-text-muted">{conv.sourcePlatform}</span>
        </div>
      </div>
    </motion.button>
  )
}

function ConvItemSkeleton({ index }: { index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2, delay: Math.min(index * STAGGER_STEP, MAX_STAGGER_DELAY) }}
      className="flex items-start gap-3 px-4 py-3.5 border-b border-border-subtle"
    >
      <Skeleton rounded="full" className="w-8 h-8 shrink-0" />
      <div className="flex-1 min-w-0 space-y-2 pt-0.5">
        <div className="flex items-center justify-between gap-2">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-2.5 w-8" />
        </div>
        <Skeleton className="h-2.5 w-3/4" />
        <Skeleton className="h-2.5 w-1/2" />
      </div>
    </motion.div>
  )
}

function MessageBubble({ message, index }: { message: Message; index: number }) {
  const isOut = message.direction === 'outbound'
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: Math.min(index * STAGGER_STEP, MAX_STAGGER_DELAY) }}
      className={cn('flex', isOut ? 'justify-end' : 'justify-start')}
    >
      <div
        className={cn(
          'max-w-xs md:max-w-md rounded-2xl px-4 py-3 text-sm',
          isOut
            ? 'bg-accent-blue text-white rounded-br-sm shadow-glow-blue'
            : 'bg-glass-medium text-text-primary rounded-bl-sm border border-border-subtle',
        )}
      >
        <p className="leading-relaxed">{message.body}</p>
        <p className={cn('text-[10px] mt-1.5 tabular-nums', isOut ? 'text-white/60' : 'text-text-muted')}>
          {new Date(message.sentAt).toLocaleTimeString('es-ES', {
            hour: '2-digit', minute: '2-digit',
          })}
        </p>
      </div>
    </motion.div>
  )
}

export default function Inbox() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [replyBody, setReplyBody]   = useState('')
  const [filter, setFilter]         = useState<Filter>('all')

  const { data, loading, error, reload }             = useInbox()
  // Honest empty array on failure — never a fabricated fleet of conversations (carta §4
  // "regla transversal de honestidad de producto").
  const conversations: Conversation[]                = data?.conversations ?? []
  const { data: thread, loading: threadLoading }    = useConversation(selectedId ?? '')
  const { reply, loading: sending }                 = useInboxMutations()
  const { success, error: toastErr }                = useToast()

  // F4: SSE-driven live refresh — a new inbound lead or a status change elsewhere
  // reloads the list without the dealer having to hit refresh manually.
  useInboxStream(reload)

  const filtered = filter === 'unread' ? conversations.filter((c) => c.unread) : conversations
  const selected = conversations.find((c) => c.id === selectedId) ?? null
  const unreadCount = conversations.filter((c) => c.unread).length
  // First paint only — reload() (manual refresh / SSE tick) keeps prior data while
  // loading is true again, so this never flashes a skeleton over a populated list.
  const showListSkeleton = loading && conversations.length === 0 && !error

  async function sendReply() {
    if (!selectedId || !replyBody.trim()) return
    try {
      await reply(selectedId, replyBody.trim())
      setReplyBody('')
      success('Respuesta enviada')
      reload()
    } catch {
      toastErr('No se pudo enviar la respuesta')
    }
  }

  return (
    <div className="p-4 md:p-6 h-full flex flex-col max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-between mb-4 shrink-0"
      >
        <div className="flex items-center gap-2.5">
          <h1 className="text-xl font-bold text-text-primary">Inbox</h1>
          <AnimatePresence mode="popLayout">
            {unreadCount > 0 && (
              <motion.span
                key={unreadCount}
                initial={{ opacity: 0, scale: 0.6 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.6 }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                className="px-2 py-0.5 bg-accent-blue text-white text-xs font-bold rounded-full shadow-glow-blue tabular-nums"
              >
                {unreadCount}
              </motion.span>
            )}
          </AnimatePresence>
        </div>

        <div className="flex items-center gap-2">
          {/* Filter tabs */}
          <div className="flex bg-glass-subtle border border-border-subtle rounded-lg p-0.5">
            {(['all', 'unread'] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                aria-pressed={filter === f}
                className={cn(
                  'relative px-3 py-1 text-xs font-medium rounded-md transition-colors duration-150',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/40',
                  filter === f ? 'text-text-primary' : 'text-text-muted hover:text-text-secondary',
                )}
              >
                {filter === f && (
                  <motion.div
                    layoutId="inbox-filter"
                    className="absolute inset-0 rounded-md bg-glass-medium"
                    transition={{ type: 'spring', stiffness: 420, damping: 36 }}
                  />
                )}
                <span className="relative z-10">{FILTER_LABEL[f]}</span>
              </button>
            ))}
          </div>

          <motion.button
            type="button"
            onClick={reload}
            aria-label="Actualizar bandeja"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.92 }}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            className={cn(
              'w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-text-primary hover:bg-glass-medium transition-colors duration-150',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/40',
            )}
          >
            <RefreshCw className={cn('w-3.5 h-3.5', loading && 'animate-spin')} />
          </motion.button>
        </div>
      </motion.div>

      <div className="flex flex-col md:flex-row gap-4 flex-1 min-h-0">
        {/* Conversation list */}
        <Card
          padding={false}
          className="md:w-80 shrink-0 overflow-y-auto"
        >
          {showListSkeleton ? (
            <div>
              {[...Array(6)].map((_, i) => <ConvItemSkeleton key={i} index={i} />)}
            </div>
          ) : filtered.length === 0 ? (
            error ? (
              <EmptyState
                icon={<InboxIcon className="w-6 h-6" />}
                title="No se pudo cargar la bandeja"
                message="Hubo un error contactando al servidor. Reintenta."
                action={<Button size="sm" icon={<RefreshCw className="w-3.5 h-3.5" />} onClick={reload}>Reintentar</Button>}
              />
            ) : conversations.length === 0 ? (
              <EmptyState
                icon={<InboxIcon className="w-6 h-6" />}
                title="Sin conversaciones"
                message="Conecta tu correo de leads y aquí aparecerán los mensajes de tus clientes."
              />
            ) : (
              <EmptyState
                icon={<InboxIcon className="w-6 h-6" />}
                title="Todo al día"
                message="No tienes conversaciones sin leer."
                action={<Button variant="ghost" size="sm" onClick={() => setFilter('all')}>Ver todas</Button>}
              />
            )
          ) : (
            <AnimatePresence initial={false}>
              {filtered.map((c, i) => (
                <motion.div
                  key={c.id}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15, delay: Math.min(i * STAGGER_STEP, MAX_STAGGER_DELAY) }}
                >
                  <ConvItem
                    conv={c}
                    selected={c.id === selectedId}
                    onClick={() => setSelectedId(c.id)}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </Card>

        {/* Thread pane */}
        <AnimatePresence mode="wait" initial={false}>
          {selected ? (
            <motion.div
              key={selected.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="flex-1 flex min-h-0"
            >
              <Card padding={false} className="flex-1 flex flex-col min-h-0 overflow-hidden">
                {/* Thread header */}
                <div className="px-5 py-4 border-b border-border-subtle shrink-0">
                  <p className="text-sm font-semibold text-text-primary">{selected.subject}</p>
                  <p className="text-xs text-text-muted mt-0.5">
                    {selected.contactName} · {selected.vehicleName} · {selected.sourcePlatform}
                  </p>
                  {/* F5: census cross-reference chip — carta §6 example: "BMW 320d 2019 ·
                      18.900 € · 34 días en tu stock". Only rendered when it resolved for real. */}
                  {selected.vehicleContext && (
                    <p className={cn(
                      'text-xs mt-1 font-medium tabular-nums',
                      selected.vehicleContext.stillListed ? 'text-accent-blue' : 'text-rose-400',
                    )}>
                      {selected.vehicleContext.stillListed ? (
                        <>
                          {selected.vehicleContext.price != null && `€${selected.vehicleContext.price.toLocaleString('es-ES')} · `}
                          {selected.vehicleContext.daysInStock} días en tu stock
                        </>
                      ) : (
                        'Este vehículo ya no está anunciado'
                      )}
                    </p>
                  )}
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {threadLoading ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex flex-col items-center gap-3 py-12"
                    >
                      <LoadingSpinner />
                      <p className="text-xs text-text-muted">Cargando conversación…</p>
                    </motion.div>
                  ) : thread?.messages && thread.messages.length > 0 ? (
                    thread.messages.map((m, i) => <MessageBubble key={m.id} message={m} index={i} />)
                  ) : (
                    <EmptyState
                      icon={<MessageSquare className="w-6 h-6" />}
                      title="Sin mensajes"
                      message="Aún no hay mensajes en esta conversación."
                    />
                  )}
                </div>

                {/* Reply box */}
                <div className="p-3 border-t border-border-subtle shrink-0">
                  <div className="flex gap-2 items-end">
                    <textarea
                      value={replyBody}
                      onChange={(e) => setReplyBody(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) sendReply() }}
                      placeholder="Escribe una respuesta… (⌘+Enter para enviar)"
                      rows={2}
                      className={cn(
                        'flex-1 resize-none px-3.5 py-2.5 rounded-xl text-sm text-text-primary placeholder:text-text-muted',
                        'bg-glass-subtle border border-border-subtle',
                        'focus:outline-none focus:border-border-active focus:ring-2 focus:ring-accent-blue/20',
                        'transition-all duration-150',
                      )}
                    />
                    <motion.button
                      type="button"
                      onClick={sendReply}
                      disabled={!replyBody.trim() || sending}
                      aria-label="Enviar respuesta"
                      whileHover={{ scale: replyBody.trim() && !sending ? 1.04 : 1 }}
                      whileTap={{ scale: replyBody.trim() && !sending ? 0.92 : 1 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                      className={cn(
                        'w-11 h-11 flex items-center justify-center rounded-xl',
                        'bg-accent-blue text-white shadow-glow-blue hover:brightness-110',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary',
                        'disabled:opacity-40 disabled:pointer-events-none',
                        'transition-[filter] duration-150 shrink-0',
                      )}
                    >
                      {sending ? (
                        <LoadingSpinner size="sm" className="!border-white/30 !border-t-white" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </motion.button>
                  </div>
                </div>
              </Card>
            </motion.div>
          ) : (
            <motion.div
              key="empty-thread"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="flex-1 hidden md:flex"
            >
              <Card className="flex-1 flex">
                <EmptyState
                  icon={<MessageSquare className="w-6 h-6" />}
                  title="Selecciona una conversación"
                  message="Elige un hilo de la lista para leer y responder."
                />
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
