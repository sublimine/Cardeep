// 09-trading-terminal F3: real-data hook for one symbol's chart+census state.
// Mirrors web/src/pages/inventory/useDealerInventory.ts's pattern: independent async legs,
// a generation guard against stale responses on rapid symbol switches, honest errors —
// never a silently-swapped placeholder series.
import { useCallback, useEffect, useRef, useState } from 'react'
import {
  cardeep, CardeepApiError,
  type TerminalRange, type TerminalStats, type TerminalStatsInsufficient,
} from '../../api/cardeep'
import type { Bar } from '../../components/chart-engine/types'

interface TerminalSymbolState {
  bars: Bar[]
  stats: TerminalStats | TerminalStatsInsufficient | null
  loading: boolean
  error: string | null
}

const INITIAL_STATE: TerminalSymbolState = { bars: [], stats: null, loading: true, error: null }

function errorMessage(err: unknown): string {
  if (err instanceof CardeepApiError) return err.message
  if (err instanceof Error) return err.message
  return 'Error desconocido al consultar la API de CARDEEP'
}

export function useTerminalSymbol(symbolKey: string | null, range: TerminalRange) {
  const [state, setState] = useState<TerminalSymbolState>(INITIAL_STATE)
  const generationRef = useRef(0)

  const reload = useCallback(() => {
    if (!symbolKey) {
      setState(INITIAL_STATE)
      return
    }
    const generation = ++generationRef.current
    const isCurrent = () => generationRef.current === generation
    setState({ ...INITIAL_STATE, loading: true })

    cardeep.terminalOhlc(symbolKey, range)
      .then(bars => { if (isCurrent()) setState(s => ({ ...s, bars })) })
      .catch((err: unknown) => { if (isCurrent()) setState(s => ({ ...s, error: s.error ?? errorMessage(err) })) })

    cardeep.terminalStats(symbolKey)
      .then(stats => { if (isCurrent()) setState(s => ({ ...s, stats })) })
      .catch((err: unknown) => { if (isCurrent()) setState(s => ({ ...s, error: s.error ?? errorMessage(err) })) })
      .finally(() => { if (isCurrent()) setState(s => ({ ...s, loading: false })) })
  }, [symbolKey, range])

  useEffect(() => { reload() }, [reload])

  return { ...state, reload }
}
