// 03-garage-fleet F3 — vehicle-pipeline board state (§6.2, K13). Lives under the
// dealer's own "Mi flota" surface (`/vehicles`, view=tablero) — NOT `/kanban`,
// which 00-MASTER.md C-5 assigns to pilar 06's DEAL pipeline. Same route, two
// different products; this one's cards are real vehicle_ulid rows.
import { useCallback, useEffect, useState } from 'react'
import type { VehicleListItem } from '../../api/cardeep'
import { dealerOps, FLEET_OPS_STATUSES, type FleetOpsState, type FleetOpsStatus } from '../../api/dealerOps'

export type FleetBoard = Record<FleetOpsStatus, VehicleListItem[]>

function emptyOpsMap(): Map<string, FleetOpsState> {
  return new Map()
}

function buildBoard(vehicles: readonly VehicleListItem[], opsByVehicle: Map<string, FleetOpsState>): FleetBoard {
  const board = Object.fromEntries(FLEET_OPS_STATUSES.map(s => [s, [] as VehicleListItem[]])) as FleetBoard
  for (const v of vehicles) {
    const status = opsByVehicle.get(v.vehicle_ulid)?.status ?? 'entrada'
    board[status].push(v)
  }
  return board
}

export function useFleetBoard(cdp: string, vehicles: readonly VehicleListItem[]) {
  const [opsByVehicle, setOpsByVehicle] = useState<Map<string, FleetOpsState>>(emptyOpsMap)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    dealerOps.listFleetOps(cdp)
      .then(rows => { setOpsByVehicle(new Map(rows.map(r => [r.vehicle_ulid, r]))); setError(null) })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Error al cargar el tablero'))
      .finally(() => setLoading(false))
  }, [cdp])

  useEffect(() => { load() }, [load])

  const board = buildBoard(vehicles, opsByVehicle)

  const moveVehicle = useCallback(async (vehicleUlid: string, toStatus: FleetOpsStatus) => {
    const prevOps = opsByVehicle.get(vehicleUlid)
    setOpsByVehicle(prev => {
      const next = new Map(prev)
      next.set(vehicleUlid, {
        vehicle_ulid: vehicleUlid,
        purchase_cost: prevOps?.purchase_cost ?? null,
        target_price: prevOps?.target_price ?? null,
        notes: prevOps?.notes ?? null,
        updated_at: prevOps?.updated_at ?? null,
        updated_by_user_ulid: prevOps?.updated_by_user_ulid ?? null,
        status: toStatus,
      })
      return next
    })
    try {
      const { data } = await dealerOps.setStatus(vehicleUlid, toStatus)
      setOpsByVehicle(prev => { const next = new Map(prev); next.set(vehicleUlid, data); return next })
    } catch (e) {
      setOpsByVehicle(prev => {
        const next = new Map(prev)
        if (prevOps) next.set(vehicleUlid, prevOps)
        else next.delete(vehicleUlid)
        return next
      })
      throw e
    }
  }, [opsByVehicle])

  const priceOverride = useCallback(async (vehicleUlid: string, targetPrice: number, reasonCategory: string) => {
    const { data } = await dealerOps.priceOverride(vehicleUlid, targetPrice, reasonCategory)
    setOpsByVehicle(prev => { const next = new Map(prev); next.set(vehicleUlid, data); return next })
    return data
  }, [])

  return { board, opsByVehicle, loading, error, moveVehicle, priceOverride, reload: load }
}
