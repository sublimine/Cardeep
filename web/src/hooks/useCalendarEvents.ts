import { useCallback, useState } from 'react'
import { api } from '../api/client'
import { useApi } from './useApi'
import type { CalEvent } from '../types'

interface EventList { events: CalEvent[] }

export function useCalendarEvents(startIso?: string, endIso?: string) {
  const query = startIso && endIso ? `?start=${encodeURIComponent(startIso)}&end=${encodeURIComponent(endIso)}` : ''
  return useApi<EventList>(`/calendar/events${query}`, [query])
}

export function useCalendarEventMutations() {
  const [loading, setLoading] = useState(false)

  const createEvent = useCallback(
    async (data: {
      title: string; startsAt: string; endsAt?: string; type: CalEvent['type']
      location?: string; contactId?: string
    }) => {
      setLoading(true)
      try {
        return await api.post<CalEvent>('/calendar/events', data)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const deleteEvent = useCallback(async (id: string) => {
    setLoading(true)
    try {
      await api.delete(`/calendar/events/${id}`)
    } finally {
      setLoading(false)
    }
  }, [])

  return { createEvent, deleteEvent, loading }
}

export function icsDownloadUrl(eventId: string): string {
  return `/api/v1/calendar/events/${eventId}/ics`
}
