import { useCallback, useState } from 'react'
import { api } from '../api/client'
import { useApi } from './useApi'
import type { Deal } from '../types'

interface DealList {
  deals: Deal[]
  total: number
}

// 06-unified-crm-chat F2/F3: pipeline expected value (Sigma amount x probability) + 90-day
// rolling lead time — computed ONCE on the backend (services/api/routers/crm_deals.py)
// so Deals.tsx and Kanban.tsx never run two divergent client-side formulas for the same
// number (00-MASTER.md doctrine: "un solo cálculo").
export interface DealsSummary {
  expectedValue: number
  avgLeadTimeDays: number | null
  byStage: Record<string, number>
}

export function useDeals(stage?: string) {
  const query = stage ? `?stage=${stage}` : ''
  return useApi<DealList>(`/deals${query}`, [query])
}

export function useDeal(id: string) {
  return useApi<Deal>(`/deals/${id}`, [id])
}

export function useDealsSummary() {
  return useApi<DealsSummary>('/deals/summary')
}

export function useDealMutations() {
  const [loading, setLoading] = useState(false)

  const moveStage = useCallback(async (id: string, stage: Deal['stage']) => {
    setLoading(true)
    try {
      return await api.patch<Deal>(`/deals/${id}`, { stage })
    } finally {
      setLoading(false)
    }
  }, [])

  const createDeal = useCallback(async (data: Partial<Deal>) => {
    setLoading(true)
    try {
      return await api.post<Deal>('/deals', data)
    } finally {
      setLoading(false)
    }
  }, [])

  return { moveStage, createDeal, loading }
}
