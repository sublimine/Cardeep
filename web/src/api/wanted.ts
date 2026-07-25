// web/src/api/wanted.ts — 08-forum-community F3: the "Se busca" board API client.
//
// Uses `api` from `./client` (Bearer session auth, AUTH-0) — NOT `cardeep.ts`'s getData
// (X-API-Key only, no session concept). `/wanted/*` (services/api/routers/wanted.py) wraps
// responses in the standard {ok, data, error, meta} envelope (entities/geo/vehicles
// precedent), unlike auth.py/crm_*.py's plain-JSON contract — so this module unwraps it
// itself, the same shape cardeep.ts's getData decodes, just over the Bearer client.
import { api, ApiError } from './client'

export interface Envelope<T> {
  ok: boolean
  data: T | null
  error: string | null
  meta: Record<string, unknown> | null
}

async function unwrap<T>(promise: Promise<Envelope<T>>): Promise<{ data: T; meta: Record<string, unknown> }> {
  const body = await promise
  if (!body.ok || body.data === null) {
    throw new ApiError(200, body.error ?? 'unknown error')
  }
  return { data: body.data, meta: body.meta ?? {} }
}

export interface WantedListing {
  wanted_ulid: string
  make: string
  model: string | null
  year_min: number | null
  year_max: number | null
  km_max: number | null
  price_max: number | null
  fuel: string | null
  transmission: string | null
  province_code: string
  free_text: string | null
  ttl_days: number
  status: 'open' | 'matched' | 'closed' | 'expired'
  closed_reason: string | null
  created_at: string
  expires_at: string
}

export interface WantedMatch {
  wanted_match_ulid: string
  vehicle_ulid: string
  match_score: number
  matched_at: string
  notified_at: string | null
  clicked_at: string | null
  make: string | null
  model: string | null
  year: number | null
  km: number | null
  price: number | null
  photo_url: string | null
  deep_link: string | null
  entity_ulid: string | null
  vehicle_status: string | null
}

export interface WantedCreatePayload {
  make: string
  model?: string | null
  year_min?: number | null
  year_max?: number | null
  km_max?: number | null
  price_max?: number | null
  fuel?: string | null
  transmission?: string | null
  province_code: string
  free_text?: string | null
  ttl_days: 7 | 14 | 30 | 60
}

export interface Pulse {
  threads_active_24h: number
  wanted_open: number
  matches_served_7d: number
}

export interface Liveness {
  match_liveness_rate: number | null
  live_at_click: number
  total_clicks: number
  window_days: number
}

export interface DemandRow {
  province_code: string
  province_name: string
  make: string
  fuel: string | null
  buyers: number
}

export interface DealerReviewAggregate {
  cdp_code: string
  n_reviews_12m: number
  pct_positive_12m: number | null
  axis_averages: {
    trato: number | null
    anuncio_veraz: number | null
    disponibilidad_real: number | null
    agilidad: number | null
  }
}

export interface ReviewPayload {
  axis_trato: number
  axis_anuncio_veraz: number
  axis_disponibilidad_real: number
  axis_agilidad: number
  overall: number
  comment?: string | null
  reviewer_role?: 'buyer' | 'dealer'
}

export interface ProvinceOption {
  code: string
  name: string
}

export const wantedApi = {
  provinces: () => unwrap<ProvinceOption[]>(api.get<Envelope<ProvinceOption[]>>('/wanted/meta/provinces')),
  create: (payload: WantedCreatePayload) =>
    unwrap<WantedListing>(api.post<Envelope<WantedListing>>('/wanted', payload)),
  listMine: (status?: WantedListing['status']) =>
    unwrap<WantedListing[]>(api.get<Envelope<WantedListing[]>>(`/wanted${status ? `?status=${status}` : ''}`)),
  get: (wantedUlid: string) => unwrap<WantedListing>(api.get<Envelope<WantedListing>>(`/wanted/${wantedUlid}`)),
  matches: (wantedUlid: string, page = 1, size = 50) =>
    unwrap<WantedMatch[]>(api.get<Envelope<WantedMatch[]>>(`/wanted/${wantedUlid}/matches?page=${page}&size=${size}`)),
  close: (wantedUlid: string, reason: 'bought_via_cardeep' | 'bought_elsewhere' | 'no_longer_interested') =>
    unwrap<WantedListing>(api.post<Envelope<WantedListing>>(`/wanted/${wantedUlid}/close`, { reason })),
  clickMatch: (matchUlid: string) =>
    unwrap<{ wanted_match_ulid: string; clicked: boolean }>(
      api.post<Envelope<{ wanted_match_ulid: string; clicked: boolean }>>(`/wanted/matches/${matchUlid}/click`, {}),
    ),
  submitReview: (matchUlid: string, payload: ReviewPayload) =>
    unwrap<{ review_ulid: string; reviewer_role: string; revealed: boolean; submitted_at: string }>(
      api.post(`/wanted/matches/${matchUlid}/review`, payload),
    ),
  pulse: () => unwrap<Pulse>(api.get<Envelope<Pulse>>('/wanted/pulse')),
  liveness: () => unwrap<Liveness>(api.get<Envelope<Liveness>>('/wanted/liveness')),
  demand: () => unwrap<DemandRow[]>(api.get<Envelope<DemandRow[]>>('/wanted/demand')),
  dealerReviews: (cdpCode: string) =>
    unwrap<DealerReviewAggregate>(api.get<Envelope<DealerReviewAggregate>>(`/wanted/reviews/${cdpCode}`)),
}
