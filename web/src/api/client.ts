// CARDEEP API client — typed wrapper over the FastAPI service.
//
// Base URL + key from Vite env (dev). SECURITY NOTE: VITE_* vars ship in the bundle, so the API key
// here is for LOCAL/INTERNAL dev only. For a public deployment the frontend must go through a BFF /
// proxy (or the API must expose unauthenticated read endpoints) — never ship a real key client-side.
import type {
  DeltaEvent,
  EntityDetail,
  EntitySummary,
  Envelope,
  GeoSeal,
  Paginated,
  Stats,
  VehicleDetail,
  VehicleListItem,
} from './types';

const BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ?? 'http://127.0.0.1:8000';
const API_KEY = (import.meta.env.VITE_API_KEY as string | undefined) ?? '';

export class ApiError extends Error {
  readonly status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

type Params = Record<string, string | number | undefined>;

async function getData<T>(path: string, params?: Params): Promise<T> {
  const url = new URL(BASE + path);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }
  let res: Response;
  try {
    res = await fetch(url.toString(), {
      headers: API_KEY ? { 'X-API-Key': API_KEY } : undefined,
    });
  } catch (e) {
    throw new ApiError(`network error reaching the CARDEEP API at ${BASE}`, 0);
  }
  let body: Envelope<T>;
  try {
    body = (await res.json()) as Envelope<T>;
  } catch {
    throw new ApiError(`non-JSON response (HTTP ${res.status}) from ${path}`, res.status);
  }
  if (!res.ok || !body.ok || body.data === null) {
    throw new ApiError(body.error ?? `HTTP ${res.status} on ${path}`, res.status);
  }
  return body.data;
}

// Same as getData but also returns the pagination meta (for list endpoints).
async function getPaged<T>(path: string, params?: Params): Promise<Paginated<T>> {
  const url = new URL(BASE + path);
  if (params) for (const [k, v] of Object.entries(params)) if (v !== undefined) url.searchParams.set(k, String(v));
  const res = await fetch(url.toString(), { headers: API_KEY ? { 'X-API-Key': API_KEY } : undefined });
  const body = (await res.json()) as Envelope<T[]>;
  if (!res.ok || !body.ok || body.data === null) throw new ApiError(body.error ?? `HTTP ${res.status} on ${path}`, res.status);
  const m = body.meta ?? {};
  return {
    items: body.data,
    page: (m.page as number) ?? 1,
    size: (m.size as number) ?? body.data.length,
    returned: (m.returned as number) ?? body.data.length,
    has_more: (m.has_more as boolean) ?? false,
  };
}

export const api = {
  stats: () => getData<{ counts: Stats }>('/stats').then((d) => d.counts),
  geoSeal: () => getData<GeoSeal>('/geo/seal'),
  provinceEntities: (province: string, page = 1, size = 50) =>
    getPaged<EntitySummary>(`/geo/${province}/entities`, { page, size }),
  municipalityEntities: (province: string, muni: string, page = 1, size = 50) =>
    getPaged<EntitySummary>(`/geo/${province}/municipalities/${muni}/entities`, { page, size }),
  provinceTree: (province: string) => getData<unknown>(`/geo/${province}/tree`),
  entity: (cdp: string) => getData<EntityDetail>(`/entities/${cdp}`),
  entityInventory: (cdp: string, page = 1, size = 50) =>
    getPaged<VehicleListItem>(`/entities/${cdp}/inventory`, { page, size }),
  entityDelta: (cdp: string, page = 1, size = 50, since?: string) =>
    getPaged<DeltaEvent>(`/entities/${cdp}/delta`, { page, size, since }),
  vehicle: (ulid: string) => getData<VehicleDetail>(`/vehicles/${ulid}`),
};
