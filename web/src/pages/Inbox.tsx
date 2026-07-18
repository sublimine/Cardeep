import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageSquare, RefreshCw, Inbox as InboxIcon } from 'lucide-react'
import Card from '../components/Card'
import Avatar from '../components/Avatar'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'
import { Badge } from '../components/Badge'
import { useInbox, useConversation, useInboxMutations } from '../hooks/useInbox'
import { useToast } from '../components/Toast'
import type { Conversation } from '../types'
import { cn } from '../lib/cn'

// 05-multiposting F2 (00-MASTER.md C-10, "regla del primer llegado"): 06-unified-crm-chat
// owns Inbox.tsx/the CRM inbox backend, but had not landed when this pilar's F2 executed
// (plans/cardeep-omni/PROGRESO.md BLOQUE 2 — 06 is scheduled for BLOQUE 3, not started).
// The mock this file used to fall back to (`MOCK_CONVS`: 'mobile.de'/'autoscout24' fake
// conversations, out-of-scope-for-Spain platform, fictional contacts) is retired here per
// the first-arrival rule — replaced with the honest empty-state 06's OWN carta already
// prescribes for this exact case (05-multiposting.md S1.4, 06-unified-crm-chat.md S"Prohibido
// ?? MOCK_* en cualquier pagina CRM"). Registered in 06-unified-crm-chat.md's tracker (S0
// note) so 06 does not re-discover this as a surprise. GET/POST /inbox/* still do not exist
// in services/api (grep -rn "inbox" services/api/routers/ = 0 results) — 06-F4 builds
// crm_inbox.py against the exact paths useInbox.ts already expects.

const STATUS_COLOR: Record<string, NonNullable<Parameters<typeof Badge>[0]['color']>> = {
  open: 'blue', replied: 'green', closed: 'gray', spam: 'red',
}

type Filter = 'all' | 'unread'

function ConvItem({
  conv, selected, onClick,
}: { conv: Conversation; selected: boolean; onClick: () => void }) {
  const date = new Date(conv.lastMessageAt).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short',
  })

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-start gap-3 px-4 py-3.5 text-left border-b border-border-subtle',
        'transition-colors duration-100',
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
          <span className="text-[10px] text-text-muted shrink-0">{date}</span>
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

        <div className="flex items-center gap-1.5 mt-2">
          <Badge color={STATUS_COLOR[conv.status] ?? 'gray'}>{conv.status}</Badge>
          <span className="text-[10px] text-text-muted">{conv.sourcePlatform}</span>
        </div>
      </div>
    </button>
  )
}

export default function Inbox() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [replyBody, setReplyBody]   = useState('')
  const [filter, setFilter]         = useState<Filter>('all')

  const { data, loading, error, reload }             = useInbox()
  // Honest empty array, never a fabricated fleet of conversations (C-10, see file-header
  // note) -- /inbox does not exist in services/api yet, so `error` is always populated
  // until 06-unified-crm-chat's F4 ships a real channel; the list below renders that
  // reality plainly instead of a silently-swapped mock.
  const conversations: Conversation[]                = data?.conversations ?? []
  const { data: thread, loading: threadLoading }    = useConversation(selectedId ?? '')
  const { reply, loading: sending }                 = useInboxMutations()
  const { success, error: toastErr }                = useToast()

  const filtered = filter === 'unread' ? conversations.filter((c) => c.unread) : conversations
  const selected = conversations.find((c) => c.id === selectedId) ?? null
  const unreadCount = conversations.filter((c) => c.unread).length

  async function sendReply() {
    if (!selectedId || !replyBody.trim()) return
    try {
      await reply(selectedId, replyBody.trim())
      setReplyBody('')
      success('Reply sent')
      reload()
    } catch {
      toastErr('Failed to send reply')
    }
  }

  return (
    <div className="p-4 md:p-6 h-full flex flex-col max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div className="flex items-center gap-2.5">
          <h1 className="text-xl font-bold text-text-primary">Inbox</h1>
          {unreadCount > 0 && (
            <span className="px-2 py-0.5 bg-accent-blue text-white text-xs font-bold rounded-full shadow-glow-blue">
              {unreadCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Filter tabs */}
          <div className="flex bg-glass-subtle border border-border-subtle rounded-lg p-0.5">
            {(['all', 'unread'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  'relative px-3 py-1 text-xs font-medium rounded-md transition-colors duration-150 capitalize',
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
                <span className="relative z-10">{f}</span>
              </button>
            ))}
          </div>

          <button
            onClick={reload}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-text-primary hover:bg-glass-medium transition-colors duration-150"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', loading && 'animate-spin')} />
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 flex-1 min-h-0">
        {/* Conversation list */}
        <Card
          padding={false}
          className="md:w-80 shrink-0 overflow-y-auto"
        >
          {filtered.length === 0 ? (
            <EmptyState
              icon={<InboxIcon className="w-6 h-6" />}
              title={error ? 'Bandeja aún no conectada' : 'Sin conversaciones'}
              message={error
                ? 'El canal de mensajería unificado (email/WhatsApp) está en construcción — todavía no hay backend real detrás de esta pantalla.'
                : undefined}
            />
          ) : (
            <AnimatePresence initial={false}>
              {filtered.map((c) => (
                <motion.div
                  key={c.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
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
        {selected ? (
          <Card padding={false} className="flex-1 flex flex-col min-h-0 overflow-hidden">
            {/* Thread header */}
            <div className="px-5 py-4 border-b border-border-subtle shrink-0">
              <p className="text-sm font-semibold text-text-primary">{selected.subject}</p>
              <p className="text-xs text-text-muted mt-0.5">
                {selected.contactName} · {selected.vehicleName} · {selected.sourcePlatform}
              </p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {threadLoading ? (
                <div className="flex justify-center py-12">
                  <LoadingSpinner />
                </div>
              ) : thread?.messages && thread.messages.length > 0 ? (
                thread.messages.map((m) => {
                  const isOut = m.direction === 'outbound'
                  return (
                    <motion.div
                      key={m.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2 }}
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
                        <p className="leading-relaxed">{m.body}</p>
                        <p className={cn('text-[10px] mt-1.5', isOut ? 'text-white/60' : 'text-text-muted')}>
                          {new Date(m.sentAt).toLocaleTimeString('en-GB', {
                            hour: '2-digit', minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </motion.div>
                  )
                })
              ) : (
                <p className="text-center text-sm text-text-muted py-8">No messages yet</p>
              )}
            </div>

            {/* Reply box */}
            <div className="p-3 border-t border-border-subtle shrink-0">
              <div className="flex gap-2 items-end">
                <textarea
                  value={replyBody}
                  onChange={(e) => setReplyBody(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) sendReply() }}
                  placeholder="Write a reply… (⌘+Enter to send)"
                  rows={2}
                  className={cn(
                    'flex-1 resize-none px-3.5 py-2.5 rounded-xl text-sm text-text-primary placeholder:text-text-muted',
                    'bg-glass-subtle border border-border-subtle',
                    'focus:outline-none focus:border-border-active focus:ring-2 focus:ring-accent-blue/20',
                    'transition-all duration-150',
                  )}
                />
                <button
                  onClick={sendReply}
                  disabled={!replyBody.trim() || sending}
                  className={cn(
                    'w-11 h-11 flex items-center justify-center rounded-xl',
                    'bg-accent-blue text-white shadow-glow-blue hover:brightness-110',
                    'disabled:opacity-40 disabled:pointer-events-none',
                    'transition-[filter] duration-150 shrink-0',
                  )}
                >
                  {sending ? (
                    <LoadingSpinner size="sm" className="!border-white/30 !border-t-white" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </Card>
        ) : (
          <Card className="flex-1 hidden md:flex">
            <EmptyState
              icon={<MessageSquare className="w-6 h-6" />}
              title="Select a conversation"
              message="Pick a thread from the list to read and reply."
            />
          </Card>
        )}
      </div>
    </div>
  )
}
