// CARDEEP API client — typed wrapper over the live FastAPI service (services/api).
// Envelope: { ok, data, error, meta }. Public mode (no key) in dev; X-API-Key when configured.
// Base: VITE_API_BASE (default the canonical local API on :8090). This REPLACES the CARDEX
// /api/v1 Bearer client for all CARDEEP-data wiring; pages import from here.

const BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ?? 'http://127.0.0.1:8090';
const API_KEY = (import.meta.env.VITE_API_KEY as string | undefined) ?? '';

export interface Envelope<T> {
  ok: boolean;
  data: T | null;
  error: string | null;
  meta: (Record<string, unknown> & { page?: number; size?: number; returned?: number; has_more?: boolean }) | null;
}

export class CardeepApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = 'CardeepApiError';
  }
}

type Params = Record<string, string | number | undefined>;

async function getData<T>(path: string, params?: Params, signal?: AbortSignal): Promise<T> {
  const url = new URL(BASE + path);
  if (params) for (const [k, v] of Object.entries(params)) if (v !== undefined) url.searchParams.set(k, String(v));
  const res = await fetch(url.toString(), { headers: API_KEY ? { 'X-API-Key': API_KEY } : undefined, signal });
  let body: Envelope<T>;
  try {
    body = (await res.json()) as Envelope<T>;
  } catch {
    throw new CardeepApiError(res.status, `non-JSON response (HTTP ${res.status}) from ${path}`);
  }
  if (!res.ok || !body.ok || body.data === null) {
    throw new CardeepApiError(res.status, body.error ?? `HTTP ${res.status} on ${path}`);
  }
  return body.data;
}

export interface Paginated<T> {
  items: T[];
  page: number;
  size: number;
  returned: number;
  has_more: boolean;
}

async function getPaged<T>(path: string, params?: Params, signal?: AbortSignal): Promise<Paginated<T>> {
  const url = new URL(BASE + path);
  if (params) for (const [k, v] of Object.entries(params)) if (v !== undefined) url.searchParams.set(k, String(v));
  const res = await fetch(url.toString(), { headers: API_KEY ? { 'X-API-Key': API_KEY } : undefined, signal });
  const body = (await res.json()) as Envelope<T[]>;
  if (!res.ok || !body.ok || body.data === null) throw new CardeepApiError(res.status, body.error ?? `HTTP ${res.status}`);
  const m = body.meta ?? {};
  return {
    items: body.data,
    page: (m.page as number) ?? 1,
    size: (m.size as number) ?? body.data.length,
    returned: (m.returned as number) ?? body.data.length,
    has_more: (m.has_more as boolean) ?? false,
  };
}

// ---- Types (mirror the verified API contract) ----
export type EntityKind =
  | 'compraventa' | 'concesionario_oficial' | 'desguace' | 'garaje' | 'plataforma'
  | 'particular' | 'subasta' | 'oem_vo_portal' | 'importador' | 'rent_a_car_vo' | 'cadena';
export type SealVerdict = 'SELLADO' | 'PARCIAL' | 'GAP' | 'NO_DENOM';

export interface Stats {
  dealers: number;
  vehicles_unique_available: number;
  events: number;
  provinces: number;
  municipalities: number;
}
export interface ProvinceSeal {
  province_code: string;
  denominator: number | null;
  numerator: number;
  coverage_pct: number | null;
  verdict: SealVerdict;
}
export interface SealSegment {
  national: { numerator: number; denominator: number; coverage_pct: number };
  distribution: Record<string, number>;
  provinces: ProvinceSeal[];
}
export interface GeoSeal {
  segments: { venta?: SealSegment; desguace?: SealSegment };
}
export interface EntitySummary {
  cdp_code: string;
  kind: EntityKind;
  trade_name: string | null;
  legal_name: string | null;
  municipality_code: string | null;
  is_tier1: boolean;
  status: string;
}
export interface EntityDetail extends EntitySummary {
  entity_ulid: string;
  province_code: string | null;
  address: string | null;
  postcode: string | null;
  phone: string | null;
  website: string | null;
  available_inventory: number;
}
export interface VehicleListItem {
  vehicle_ulid: string;
  deep_link: string;
  title: string | null;
  make: string | null;
  model: string | null;
  year: number | null;
  km: number | null;
  price: number | null;
  currency: string | null;
  fuel: string | null;
  transmission: string | null;
  photo_url: string | null;
  status: string;
  first_seen: string;
  last_seen: string;
}
export interface VehicleHistoryEvent {
  event_type: string;
  old_value: unknown;
  new_value: unknown;
  observed_at: string;
}

export const cardeep = {
  stats: (signal?: AbortSignal) => getData<{ counts: Stats }>('/stats', undefined, signal).then((d) => d.counts),
  geoSeal: (signal?: AbortSignal) => getData<GeoSeal>('/geo/seal', undefined, signal),
  provinceEntities: (prov: string, page = 1, size = 50) =>
    getPaged<EntitySummary>(`/geo/${prov}/entities`, { page, size }),
  entity: (cdp: string) => getData<EntityDetail>(`/entities/${cdp}`),
  entityInventory: (cdp: string, page = 1, size = 50) =>
    getPaged<VehicleListItem>(`/entities/${cdp}/inventory`, { page, size }),
  vehicleHistory: (ulid: string, page = 1, size = 100) =>
    getPaged<VehicleHistoryEvent>(`/vehicles/${ulid}/history`, { page, size }),
};
