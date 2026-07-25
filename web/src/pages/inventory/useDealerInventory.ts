// Fetches one dealer's real profile + full paginated inventory from the live
// CARDEEP API. No mocks, no fallback data — a failed request surfaces as
// `error`, never as a silently-swapped placeholder fleet.
import { useCallback, useEffect, useRef, useState } from 'react'
import { cardeep, CardeepApiError, type EntityDetail, type VehicleListItem } from '../../api/cardeep'
import { PAGE_SIZE } from './config'

interface DealerInventoryState {
  entity: EntityDetail | null
  vehicles: VehicleListItem[]
  loadedCount: number
  isComplete: boolean
  loading: boolean
  error: string | null
}

const INITIAL_STATE: DealerInventoryState = {
  entity: null,
  vehicles: [],
  loadedCount: 0,
  isComplete: false,
  loading: true,
  error: null,
}

function errorMessage(err: unknown): string {
  if (err instanceof CardeepApiError) return err.message
  if (err instanceof Error) return err.message
  return 'Error desconocido al consultar la API de CARDEEP'
}

// 03-garage-fleet F1: `cdp` is now REQUIRED, sourced from the logged-in dealer's
// session tenant (`useAuthContext().user.tenantId`) — never a hardcoded default.
// Callers with no tenant yet (particular account, or dealer who hasn't claimed
// an entity) must not call this hook; render a claim/onboarding state instead.
export function useDealerInventory(cdp: string) {
  const [state, setState] = useState<DealerInventoryState>(INITIAL_STATE)
  const generationRef = useRef(0)

  const load = useCallback(() => {
    const generation = ++generationRef.current
    const isCurrent = () => generationRef.current === generation

    setState({ ...INITIAL_STATE, loading: true })

    // Entity profile and the first page load independently — a slow/failed
    // header must not block the vehicle list from rendering, and vice versa.
    cardeep.entity(cdp)
      .then(entity => { if (isCurrent()) setState(s => ({ ...s, entity })) })
      .catch((err: unknown) => {
        if (isCurrent()) setState(s => ({ ...s, error: s.error ?? errorMessage(err) }))
      })

    async function loadAllPages() {
      let page = 1
      let all: VehicleListItem[] = []
      for (;;) {
        const batch = await cardeep.entityInventory(cdp, page, PAGE_SIZE)
        if (!isCurrent()) return
        all = [...all, ...batch.items]
        setState(s => ({ ...s, vehicles: all, loadedCount: all.length, loading: false }))
        if (!batch.has_more) break
        page += 1
      }
      if (isCurrent()) setState(s => ({ ...s, isComplete: true }))
    }

    loadAllPages().catch((err: unknown) => {
      if (isCurrent()) setState(s => ({ ...s, loading: false, error: errorMessage(err) }))
    })
  }, [cdp])

  useEffect(() => {
    load()
    return () => { generationRef.current += 1 }
  }, [load])

  return { ...state, reload: load }
}
