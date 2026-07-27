import { useCallback, useState } from 'react'
import { api } from '../api/client'
import { useApi } from './useApi'
import type { Note } from '../types'

interface NoteList { notes: Note[] }

export function useNotes() {
  return useApi<NoteList>('/notes')
}

export function useNoteMutations() {
  const [loading, setLoading] = useState(false)

  const createNote = useCallback(
    async (data: { title: string; body: string; color: Note['color']; pinned?: boolean }) => {
      setLoading(true)
      try {
        return await api.post<Note>('/notes', data)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const updateNote = useCallback(
    async (id: string, patch: Partial<Pick<Note, 'title' | 'body' | 'color' | 'pinned'>>) => {
      setLoading(true)
      try {
        return await api.patch<Note>(`/notes/${id}`, patch)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const deleteNote = useCallback(async (id: string) => {
    setLoading(true)
    try {
      await api.delete(`/notes/${id}`)
    } finally {
      setLoading(false)
    }
  }, [])

  return { createNote, updateNote, deleteNote, loading }
}
