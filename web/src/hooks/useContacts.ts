import { useCallback, useState } from 'react'
import { api } from '../api/client'
import type { Contact } from '../types'

export function useContactMutations() {
  const [loading, setLoading] = useState(false)

  const createContact = useCallback(
    async (data: { name: string; email?: string; phone?: string }) => {
      setLoading(true)
      try {
        return await api.post<Contact>('/contacts', data)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  return { createContact, loading }
}
