// CARDEEP API types — mirror the verified contract in services/api (deps.py + routers).
// Envelope: ok()/err() in deps.py. Auth: X-API-Key header (public mode if CARDEEP_API_KEY unset).

export interface Envelope<T> {
  ok: boolean;
  data: T | null;
  error: string | null;
  meta:
    | (Record<string, unknown> & {
        page?: number;
        size?: number;
        returned?: number;
        has_more?: boolean;
        count?: number;
      })
    | null;
}

export type EntityKind =
  | 'compraventa'
  | 'concesionario_oficial'
  | 'desguace'
  | 'garaje'
  | 'plataforma'
  | 'particular'
  | 'subasta'
  | 'oem_vo_portal'
  | 'importador'
  | 'rent_a_car_vo'
  | 'cadena';

export type SealVerdict = 'SELLADO' | 'PARCIAL' | 'GAP' | 'NO_DENOM';

// GET /stats  -> { counts: Stats }
export interface Stats {
  dealers: number;
  vehicles_unique_available: number;
  events: number;
  provinces: number;
  municipalities: number;
}

// GET /geo/seal -> { segments: { venta?, desguace? } }
export interface ProvinceSeal {
  province_code: string;
  denominator: number | null;
  numerator: number;
  coverage_pct: number | null;
  verdict: SealVerdict;
}
export interface SealSegment {
  method: string;
  national: { numerator: number; denominator: number; coverage_pct: number };
  distribution: Record<string, number>;
  provinces: ProvinceSeal[];
}
export interface GeoSeal {
  segments: { venta?: SealSegment; desguace?: SealSegment };
}

// GET /geo/{prov}/entities  (+ /municipalities/{muni}/entities) -> EntitySummary[]
export interface EntitySummary {
  cdp_code: string;
  kind: EntityKind;
  trade_name: string | null;
  legal_name: string | null;
  municipality_code: string | null;
  is_tier1: boolean;
  status: string;
}

// GET /entities/{cdp} -> EntityDetail (entity row + aggregates)
export interface EntityDetail {
  entity_ulid: string;
  cdp_code: string;
  kind: EntityKind;
  legal_name: string | null;
  trade_name: string | null;
  cif: string | null;
  province_code: string | null;
  municipality_code: string | null;
  comarca_id: number | null;
  address: string | null;
  postcode: string | null;
  lat: number | null;
  lon: number | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  is_tier1: boolean;
  status: string;
  available_inventory: number;
  canonical_cdp_code: string;
  n_aliases: number;
  queried_cdp_code: string;
}

// GET /entities/{cdp}/inventory -> VehicleListItem[]
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

// GET /entities/{cdp}/delta -> DeltaEvent[]
export interface DeltaEvent {
  event_type: 'NEW' | 'GONE' | 'PRICE_CHANGE' | 'KM_CHANGE' | 'PHOTO_CHANGE' | string;
  old_value: unknown;
  new_value: unknown;
  observed_at: string;
  entity_ulid: string;
}

// GET /vehicles/{ulid} -> VehicleDetail
export interface VehicleDetail {
  vehicle_ulid: string;
  make: string | null;
  model: string | null;
  year: number | null;
  km: number | null;
  price: number | null;
  currency: string | null;
  photo_url: string | null;
  deep_link: string;
  title: string | null;
  fuel: string | null;
  transmission: string | null;
  status: string;
  first_seen: string;
  last_seen: string;
  is_canonical: boolean;
  canonical_vehicle_ulid: string;
}

export interface Paginated<T> {
  items: T[];
  page: number;
  size: number;
  returned: number;
  has_more: boolean;
}
