// 03-garage-fleet F3 — client for /dealer/* (the FIRST authenticated write surface
// of the whole product). Goes through `client.ts`'s Bearer-token `api`, never
// through `cardeep.ts` (that client is the unauthenticated public census read API,
// X-API-Key only — writes to a dealer's OWN fleet must prove session ownership).
import { api } from './client'

export type FleetOpsStatus = 'entrada' | 'preparacion' | 'publicado' | 'reservado' | 'vendido' | 'entregado'

export const FLEET_OPS_STATUSES: FleetOpsStatus[] = [
  'entrada', 'preparacion', 'publicado', 'reservado', 'vendido', 'entregado',
]

export const FLEET_OPS_STATUS_LABELS: Record<FleetOpsStatus, string> = {
  entrada: 'Entrada',
  preparacion: 'Preparación',
  publicado: 'Publicado',
  reservado: 'Reservado',
  vendido: 'Vendido',
  entregado: 'Entregado',
}

export interface FleetOpsState {
  vehicle_ulid: string
  status: FleetOpsStatus
  purchase_cost: number | null
  target_price: number | null
  notes: string | null
  updated_at: string | null
  updated_by_user_ulid: string | null
}

export interface FleetOpsEvent {
  event_ulid: string
  actor_user_ulid: string
  event_type: 'STATUS_CHANGE' | 'COST_SET' | 'PRICE_OVERRIDE' | 'NOTE_SET'
  from_value: Record<string, unknown> | null
  to_value: Record<string, unknown> | null
  reason_category: string | null
  delta_vs_median: number | null
  observed_at: string
}

interface Envelope<T> { ok: boolean; data: T; error: string | null; meta: Record<string, unknown> | null }

async function unwrap<T>(p: Promise<Envelope<T> | T>): Promise<{ data: T; meta: Record<string, unknown> }> {
  // api.get/patch/post already unwraps to the raw JSON body (see client.ts apiRequest) —
  // the dealer_ops router returns the SAME {ok,data,error,meta} envelope every other
  // router uses, so we unwrap it here rather than growing a second envelope contract.
  const body = (await p) as Envelope<T>
  return { data: body.data, meta: body.meta ?? {} }
}

export const dealerOps = {
  getOps: (vehicleUlid: string) =>
    unwrap<FleetOpsState>(api.get(`/dealer/vehicles/${vehicleUlid}/ops`)).then(r => r.data),

  listFleetOps: (cdp: string) =>
    unwrap<FleetOpsState[]>(api.get(`/dealer/entities/${cdp}/fleet-ops`)).then(r => r.data),

  setStatus: (vehicleUlid: string, status: FleetOpsStatus, note?: string) =>
    unwrap<FleetOpsState>(api.patch(`/dealer/vehicles/${vehicleUlid}/status`, { status, note })),

  setCost: (vehicleUlid: string, purchaseCost: number, note?: string) =>
    unwrap<FleetOpsState>(api.patch(`/dealer/vehicles/${vehicleUlid}/cost`, { purchase_cost: purchaseCost, note })),

  priceOverride: (vehicleUlid: string, targetPrice: number, reasonCategory: string, note?: string) =>
    unwrap<FleetOpsState>(api.post(`/dealer/vehicles/${vehicleUlid}/price-override`, {
      target_price: targetPrice, reason_category: reasonCategory, note,
    })),

  opsHistory: (vehicleUlid: string) =>
    unwrap<FleetOpsEvent[]>(api.get(`/dealer/vehicles/${vehicleUlid}/ops-history`)).then(r => r.data),
}
