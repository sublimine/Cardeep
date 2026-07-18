import { useCallback, useEffect, useState } from 'react'
import { api, getStoredToken, getStoredTenantId } from '../api/client'
import { useApi } from './useApi'
import type { Conversation, Message } from '../types'

interface ConversationList {
  conversations: Conversation[]
  total: number
}

interface ConvWithMessages {
  conversation: Conversation
  messages: Message[]
}

export function useInbox(status = '') {
  const query = status ? `?status=${status}` : ''
  return useApi<ConversationList>(`/inbox${query}`, [query])
}

export function useConversation(id: string) {
  return useApi<ConvWithMessages>(`/inbox/${id}`, [id])
}

export function useInboxMutations() {
  const [loading, setLoading] = useState(false)

  const reply = useCallback(async (id: string, body: string, templateId?: string) => {
    setLoading(true)
    try {
      return await api.post<Message>(`/inbox/${id}/reply`, {
        body,
        template_id: templateId,
        send_via: 'email',
      })
    } finally {
      setLoading(false)
    }
  }, [])

  const patch = useCallback(async (id: string, data: { status?: string; unread?: boolean }) => {
    setLoading(true)
    try {
      return await api.patch<Conversation>(`/inbox/${id}`, data)
    } finally {
      setLoading(false)
    }
  }, [])

  return { reply, patch, loading }
}

// 06-unified-crm-chat F4: live refresh signal via SSE (services/api/routers/crm_inbox.py's
// GET /inbox/stream). EventSource cannot set an Authorization header, so the session
// token travels as a query param — the endpoint verifies it the same way get_current_session
// does, just sourced from the query string instead of the header.
export function useInboxStream(onUpdate: () => void): void {
  useEffect(() => {
    const token = getStoredToken()
    const tenant = getStoredTenantId()
    if (!token || !tenant) return

    const url = `/api/v1/inbox/stream?token=${encodeURIComponent(token)}&tenant=${encodeURIComponent(tenant)}`
    const source = new EventSource(url)
    source.onmessage = () => onUpdate()
    source.onerror = () => { /* EventSource auto-reconnects; no action needed */ }
    return () => source.close()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
