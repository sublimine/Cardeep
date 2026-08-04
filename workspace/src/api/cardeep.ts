// CARDEEP API client — typed wrapper over the live FastAPI service (services/api).
// Envelope: { ok, data, error, meta }. Public mode (no key) in dev; X-API-Key when configured.
// Base: VITE_API_BASE (default the canonical local API on :8090). This REPLACES the CARDEX
// /api/v1 Bearer client for all CARDEEP-data wiring; pages import from here.

import type { Bar } from '../components/chart-engine/types';

const RAW_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ?? 'http://127.0.0.1:8090';
// `new URL(BASE + path)` below requires an ABSOLUTE URL. A same-origin relative base
// (e.g. "/api", what web/nginx.conf proxies to the api service in production — see
// docs/runbook/DEPLOY_OPENSHIP.md) is valid for fetch() but throws "Invalid URL" if
// used as-is here. Resolve it against the current origin so every call site below
// keeps working unchanged in both dev (absolute default) and same-origin prod (relative).
const BASE = /^https?:\/\//.test(RAW_BASE) ? RAW_BASE : window.location.origin + RAW_BASE;
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

/** Like getPaged, but preserves the FULL `meta` object (page/size/returned/has_more
 * PLUS any endpoint-specific extras, e.g. listing-audit's avg_score/incoherent_price_count)
 * instead of stripping it down to the four standard pagination fields. Use when a
 * paginated endpoint's meta carries a page-independent summary the caller needs. */
interface PagedWithMeta<T> extends Paginated<T> { meta: Record<string, unknown> }

async function getPagedWithMeta<T>(path: string, params?: Params, signal?: AbortSignal): Promise<PagedWithMeta<T>> {
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
    meta: m,
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
/** A marque the census actually lists, with its live count. */
export interface CensusMake {
  /** The census spelling — the value every count query must be keyed by. */
  make: string;
  /** What to show a human: the canonical name with its real diacritics
   *  ("Citroën", "Škoda"). Absent on the older `/market/makes` route. */
  display?: string;
  slug: string;
  n: number;
}
/** A model listed under one marque. */
export interface CensusModel {
  model: string;
  n: number;
}
export interface CensusSubmodel {
  submodel: string;
  n: number;
}
/** A real, currently-listed vehicle, as served to the public landing by /market/showcase. */
export interface ShowcaseVehicle {
  id: string;
  make: string;
  model: string;
  year: number;
  km: number;
  price: number;
  currency: string;
  fuel: string | null;
  photo: string;
  province: string | null;
  days_listed: number;
  /** Cardeep's own valuation against the segment, or null when the cohort was too small to judge. */
  band: 'below_market' | 'at_market' | 'above_market' | null;
}

/**
 * A vehicle the deal-score run judged underpriced against its own cohort.
 *
 * Distinct from ShowcaseVehicle on purpose: a showcase car is a random sample of
 * the index, this one carries a verdict. The extra fields ARE the verdict —
 * how far under the cohort median it sits, in euros and as a share — and the
 * strip must never show one without the other, because 3.000 € off a 12.000 €
 * median and 3.000 € off a 90.000 € one are not the same claim.
 */
export interface OpportunityVehicle extends Omit<ShowcaseVehicle, 'band'> {
  band: 'chollo_fuerte' | 'bajo_mercado';
  band_label: string;
  savings_eur: number;
  savings_pct: number | null;
  cohort_n: number;
  /** When the deal-score run that reached this verdict was computed. */
  as_of: string | null;
}

/**
 * A written query resolved into filters.
 *
 * `unresolved` is not an error list — it is the honest half of the answer. A word
 * the parser could not place is reported rather than dropped, because dropping it
 * silently widens the search into results the visitor did not ask for.
 */
export interface ParsedQuery {
  make?: string;
  model?: string;
  submodel?: string;
  province_code?: string;
  province_name?: string;
  fuel?: string;
  body_type?: string;
  is_family?: boolean;
  color?: string;
  seats_min?: number;
  transmission?: string;
  price_max?: number;
  price_min?: number;
  km_max?: number;
  km_min?: number;
  year_min?: number;
  year_max?: number;
  unresolved?: string[];
}

export interface SearchCountParams {
  make?: string;
  model?: string;
  submodel?: string;
  color?: string;
  body_type?: string;
  is_family?: boolean;
  fuel?: string;
  seats_min?: number;
  price_min?: number;
  price_max?: number;
  province?: string;
  year_min?: number;
  year_max?: number;
  km_min_bucket?: number;
  km_max_bucket?: number;
}

export interface SearchCount {
  count: number;
  /** Always true — this endpoint never estimates. Present so a future estimated
   *  path could not be mistaken for this one. */
  exact: boolean;
  /** Listings set aside because the source never published their mileage and a
   *  kilometre bound was set. Reported so the UI can say so rather than hide it. */
  unknown_km_excluded: number;
  /** Listings set aside because no colour was ever published for them. Colour is
   *  known for 11% of the index, so a colour filter narrows the search for a
   *  reason that has nothing to do with the cars — and that has to be said. */
  unknown_color_excluded: number;
  as_of: string;
  age_seconds: number;
}
export interface ProvinceSeal {
  province_code: string;
  denominator: number | null;
  numerator: number;
  coverage_pct: number | null;
  verdict: SealVerdict;
}
export interface ProvinceMeta {
  code: string;
  name: string;
}
/** A province plus how many cars it holds for the filters currently in play. */
export interface CountedProvince extends ProvinceMeta {
  n: number;
}
export interface ProvinceDemand {
  province_code: string;
  n_available: number;
  absorption_rate: number | null;
  detail: { n_gone: number; n_avail: number; window_days: number } | null;
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
  // 03-garage-fleet F2: exposed for the first time in the OWN dealer's detail view
  // (services/api/routers/entities.py get_inventory + vehicles.py vehicle_detail).
  // Captured since migrations/0003_vehicles_events.sql:19 but never served until now.
  vin_ref: string | null;
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
export interface DeltaEvent extends VehicleHistoryEvent {
  entity_ulid: string;
}
export interface VehiclePlatformListing {
  cdp_code: string;
  trade_name: string | null;
  website: string | null;
  is_tier1: boolean;
  listing_ref: string | null;
  listing_url: string | null;
  platform_price: number | null;
  status: string;
  first_seen: string;
  last_seen: string;
}
export interface VehiclePlatforms {
  vehicle: {
    vehicle_ulid: string;
    make: string | null;
    model: string | null;
    year: number | null;
    deep_link: string;
    owning_dealer: { cdp_code: string; name: string | null; kind: EntityKind };
  };
  platforms: VehiclePlatformListing[];
}

// ---- 03-garage-fleet (F4): /market/* consumption for K9/K10/K11 ----
// Ownership: 00-MASTER.md C-1 — services/api/routers/market.py and the whole
// /market/* namespace belong to pilar 01-market-intelligence exclusively. 03
// CONSUMES these endpoints for "Mi flota"'s K9 badge and the "Mercado" screen;
// it never re-derives a median/cohort/percentile of its own (a second
// implementation would be exactly the duplication C-1 forbids).
export interface MarketSegmentMetric {
  n: number;
  p25?: number;
  p50?: number;
  p75?: number;
  value?: number;
  detail?: Record<string, unknown>;
  scope: 'prov' | 'nat';
  fallback_to_national: boolean;
}
export interface MarketSegmentStats {
  make: string;
  model: string;
  year: number;
  fuel: string;
  province_requested: string | null;
  metrics: Record<string, MarketSegmentMetric>;
}
export type PricePositionBand = 'below_market' | 'at_market' | 'above_market';
export interface PricePosition {
  vehicle_ulid: string;
  price?: number;
  segment?: { make: string | null; model: string | null; year: number | null; fuel: string | null; province_code: string | null };
  position: {
    ratio: number;
    band: PricePositionBand;
    cuts: { below_market_lt: number; above_market_gt: number };
    segment_p50: number;
    segment_n: number;
    scope: 'prov' | 'nat';
    fallback_to_national: boolean;
  } | null;
  reason?: string;
}

// ---- 05-multiposting (F1): /publishing/* — Frente A, cross-portal publication state ----
// Ownership: plans/cardeep-omni/05-multiposting.md. Read-only: coverage semaphore +
// per-vehicle-per-platform matrix (divergence/anomaly/frescura). Zero credentials, zero
// outbound write (Frente B/C are gated, out of scope here).
export type CoverageBand = 'verde' | 'ambar' | 'rojo';
export interface PublishingPlatform {
  cdp_code: string;
  trade_name: string | null;
  kind: EntityKind;
  n_listed: number;
  coverage_pct: number;
  band: CoverageBand;
}
export interface PublishingCoverage {
  dealer: { cdp_code: string; trade_name: string | null };
  total_available: number;
  platforms: PublishingPlatform[];
}
export type ListingAnomaly = 'sold_still_listed' | 'available_removed' | null;
export interface PublishingDivergence {
  delta: number;
  flag: boolean;
}
export interface PublishingMatrixPlatform {
  cdp_code: string;
  trade_name: string | null;
  listing_ref: string | null;
  listing_url: string;
  platform_price: number | null;
  status: 'listed' | 'removed';
  first_seen: string;
  last_seen: string;
  removed_at: string | null;
  divergence: PublishingDivergence | null;
  anomaly: ListingAnomaly;
  old_listing: boolean | null;
}
export interface PublishingMatrixRow {
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
  status: 'available' | 'gone';
  first_seen: string;
  last_seen: string;
  platforms: PublishingMatrixPlatform[];
}

// ---- 04-arbitrage (F2-F5): /arbitrage/* — deal-score, desync, time/geo-arbitrage, methodology ----
// Ownership: 00-MASTER.md C-2 — this pilar owns /arbitrage/* and the "chollo" concept.
export type DealBand = 'chollo_fuerte' | 'bajo_mercado';
export interface DealScoreItem {
  vehicle_ulid: string;
  title: string | null;
  make: string | null;
  model: string | null;
  year: number | null;
  km: number | null;
  price: number | null;
  currency: string | null;
  deep_link: string;
  dealer: { cdp_code: string; trade_name: string | null };
  province_code: string | null;
  z: number;
  band: DealBand;
  savings_eur: number;
  cohort: { n: number; median_price: number; make: string; model: string | null; year: number; tier: 'A' | 'B' };
  days_on_market: number;
  fresh: boolean;
  last_seen: string;
}
export interface DesyncItem {
  vehicle_ulid: string;
  make: string | null;
  model: string | null;
  year: number | null;
  dealer: { cdp_code: string; trade_name: string | null; price: number; url: string; last_seen: string };
  platform: { cdp_code: string; trade_name: string | null; price: number; url: string; last_seen: string };
  delta_eur: number;
  delta_pct: number | null;
}
export interface ArbitrageMethodology {
  methodology_version: string;
  deal_score: {
    cohort: { tier_a_min_n: number; tier_b_min_n: number; tier_b_key: string; mad_floor_ln_price: number; z_formula: string };
    bands: { price_trap_frontier_z: number; chollo_fuerte_max_z: number; bajo_mercado_max_z: number; description: string };
    freshness: { fresh_hours: number; max_age_days: number; rule: string };
  };
  desync: { min_relative_pct: number; min_absolute_eur: number; freshness_hours: number; rule: string };
  time_arbitrage: { min_cycles_per_cohort: number; min_observations_per_bucket: number; cycle_lookback_months: number; age_buckets_days: string[]; rule: string };
  geo_arbitrage: { cell_min_n: number; gap_significance_factor: number; rule: string };
  disclaimers: string[];
}
export interface ArbitrageSummary {
  chollos_activos: number;
  ahorro_mediano_eur: number | null;
  desyncs_activos: number;
  mediana_dias_a_salida: number | null;
  mediana_dias_a_salida_reason: string | null;
}
export interface CycleStats {
  n_cycles: number;
  median_days_to_gone: number;
  p25_days_to_gone: number;
  p75_days_to_gone: number;
  pct_price_drop_before_gone: number;
}
export interface DecayBucket {
  bucket_label: string;
  bucket_min_days: number;
  n: number;
  median_relative_price: number;
}
export interface TimeCurves {
  make: string;
  model: string;
  year_band_start: number;
  cycle_stats: CycleStats | null;
  cycle_stats_reason: string | null;
  buckets: DecayBucket[];
  buckets_reason: string | null;
  disclaimer: string;
}
export interface GeoCell {
  province_code: string;
  n: number;
  median_price: number;
}
export interface GeoGap {
  province_cheap: string;
  province_expensive: string;
  median_cheap: number;
  median_expensive: number;
  gap_eur: number;
  n_cheap: number;
  n_expensive: number;
}
export interface GeoArbitrageResponse {
  make: string;
  model: string;
  year_band_start: number;
  cells: GeoCell[];
  cells_reason: string | null;
  gaps: GeoGap[];
  disclaimer: string;
}

// ---------------------------------------------------------------------------
// 00-marketplace-engine F5/F6 — engine status ("Sala de máquinas") + ops surface.
// Append-only section (00-MASTER.md §5.1): do not reorder/rename methods above.
// ---------------------------------------------------------------------------
export type SourceHealthStatus = 'healthy' | 'degraded' | 'down' | 'unknown';
export interface SourceHealthRow {
  source_key: string;
  status: SourceHealthStatus;
  consecutive_fails: number;
  last_ok: string | null;
  last_fail: string | null;
  is_tier1: boolean;
}
export type AlertSeverity = 'info' | 'warning' | 'critical';
export interface AlertRow {
  id: number;
  origin: string;
  severity: AlertSeverity;
  message: string;
  payload: Record<string, unknown> | null;
  created_at: string;
}
export type EngineBadge = 'LATIENDO' | 'DEGRADADO' | 'PARADO';
export interface EngineLease {
  holder: string | null;
  pid: number | null;
  started_at: string | null;
  last_heartbeat: string | null;
  age_seconds: number | null;
}
export interface EngineJob {
  id: string;
  next_run_time: string | null;
}
export interface EngineReplayProgress {
  sources_total: number;
  sources_harvested_since_holder_started: number | null;
  note: string;
}
export interface EngineUptimeWindow {
  requested_days: number;
  full_window_available: boolean;
  observed_from: string;
  observed_to: string;
  bucket_minutes: number;
  buckets_total: number;
  buckets_with_beat: number;
  uptime_pct: number | null;
}
export interface EngineStatus {
  badge: EngineBadge;
  lease: EngineLease;
  jobs: EngineJob[];
  replay_progress: EngineReplayProgress;
  uptime: { '30d': EngineUptimeWindow; '90d': EngineUptimeWindow };
}

// ---- 09-trading-terminal (F2): /terminal/* — real market_bucket_daily aggregation ----
// Ownership: 00-MASTER.md C-1 — this pilar owns services/api/routers/terminal.py and the
// /terminal/* namespace exclusively (SEPARATE from 01's market.py/market.py). C1 symbol =
// make+model+province_code (NULL province = national roll-up), no fuel/year axis.
export interface TerminalSymbol {
  symbol_key: string;
  make: string;
  model: string;
  province_code: string | null;
  level: 'model_prov' | 'model_nat';
  first_bucket: string;
  last_bucket: string;
}
export type TerminalRange = '1M' | '3M' | '6M' | '1Y' | 'ALL';
export interface TerminalPricePressure {
  n_active: number;
  n_with_price_cut: number;
  pct: number | null;
  window_days: number;
  alert: boolean;
}
export interface TerminalLatestBucket {
  bucket_date: string;
  new_count: number;
  gone_count: number;
  dom_p50_days: number | null;
  computed_at: string;
}
export interface TerminalStatsInsufficient {
  symbol_key: string;
  insufficient_sample: true;
  active_count: number;
  min_required: number;
  reason: string;
}
export interface TerminalStats {
  symbol_key: string;
  insufficient_sample: false;
  active_count: number;
  n_dealers: number;
  n_dealers_on_platform: number;
  top5_stock: number;
  concentration_top5_pct: number | null;
  price_pressure: TerminalPricePressure;
  dealers_new_30d: number;
  latest_bucket: TerminalLatestBucket | null;
  sample_vehicles: TerminalSampleVehicle[];
}
export interface TerminalSampleVehicle {
  vehicle_ulid: string;
  year: number | null;
  km: number | null;
  price: number | null;
  deep_link: string;
  cdp_code: string;
}
export interface TerminalRating {
  vehicle_ulid: string;
  symbol_key: string;
  price?: number;
  segment?: { make: string | null; model: string | null; year: number | null; fuel: string | null; province_code: string | null };
  position: {
    ratio: number;
    band: PricePositionBand;
    cuts: { below_market_lt: number; above_market_gt: number };
    segment_p50: number;
    segment_n: number;
    scope: 'prov' | 'nat';
    fallback_to_national: boolean;
  } | null;
  reason?: string;
}
export interface TerminalScreenerRow {
  symbol_key: string;
  make: string;
  model: string;
  province_code: string | null;
  bucket_date: string;
  active_count: number;
  median_price: number | null;
  new_count: number;
  gone_count: number;
  price_change_down_count: number;
  price_change_up_count: number;
  dom_p50_days: number | null;
}
export interface TerminalSaleInferenceBucket { n: number; avg_confidence: number | null }
export interface TerminalSaleInference {
  symbol_key: string;
  probable_sale: TerminalSaleInferenceBucket;
  relisted: TerminalSaleInferenceBucket;
  delisted: TerminalSaleInferenceBucket;
  badge: 'verificado' | 'sin_verificar';
  false_positive_rate_pct: number | null;
  latest_audit_at: string | null;
  audit_freshness_days: number;
}
export interface TerminalNewsItem {
  news_ulid: string;
  source_name: string;
  source_url: string;
  title: string;
  published_at: string | null;
  verified_at: string;
  symbol_keys: string[];
}

// ---------------------------------------------------------------------------
// 07-marketing F1-F4 — listing audit (C1), channel radar (C3/C4/C5), feed export (C6).
// Append-only section (00-MASTER.md S5.1): do not reorder/rename methods above.
// ---------------------------------------------------------------------------
export interface ListingAuditCheck {
  check_id: string;
  label: string;
  passed: boolean;
  points_awarded: number;
  points_possible: number;
  message: string;
  evidence: Record<string, unknown>;
}
export interface ListingAuditItem {
  vehicle_ulid: string;
  deep_link: string;
  title: string | null;
  make: string | null;
  model: string | null;
  year: number | null;
  price: number | null;
  currency: string | null;
  photo_url: string | null;
  score: number;
  checks: ListingAuditCheck[];
  computed_at: string;
  price_position?: PricePosition['position'] | { position: null; reason?: string };
}
export type ChannelCoverageBand = 'verde' | 'ambar' | 'rojo';
export interface ChannelRadarPlatform {
  cdp_code: string;
  trade_name: string | null;
  kind: EntityKind;
  n_listed: number;
  coverage_pct: number;
  band: ChannelCoverageBand;
  n_divergent: number;
  median_days_to_gone: number | null;
  median_days_to_gone_n: number;
  median_days_to_gone_reason: string | null;
}
export interface ChannelRadar {
  dealer: { cdp_code: string };
  total_available: number;
  platforms: ChannelRadarPlatform[];
}
export type MarketingFeedTarget = 'google_vehicle_ads' | 'meta_aia' | 'schema_org_jsonld';
export interface FeedInvalidRow {
  vehicle_ulid: string;
  missing_fields: string[];
}
export interface ListingAuditMeta {
  page: number;
  size: number;
  returned: number;
  has_more: boolean;
  dealer: { cdp_code: string };
  total_available: number;
  audited_count: number;
  avg_score: number | null;
  incoherent_price_count: number;
  latest_run_id: string | null;
  latest_run_finished_at: string | null;
  price_position_included: boolean;
}
export interface FeedReport {
  export_ulid: string;
  item_count: number;
  valid_count: number;
  valid_pct: number;
  invalid_report: FeedInvalidRow[];
  content_hash: string;
  created_at: string;
}
export type AdCopyStatus = 'grounded' | 'rejected';
export interface AdCopyClaim {
  claim_id: string;
  text: string;
  provenance: string;
}
export interface AdCopyResult {
  gen_ulid: string;
  vehicle_ulid: string;
  status: AdCopyStatus;
  output_text: string | null;
  claims: AdCopyClaim[];
  unbacked_numerals: string[];
  model_used: string;
}

export const cardeep = {
  stats: (signal?: AbortSignal) => getData<{ counts: Stats }>('/stats', undefined, signal).then((d) => d.counts),
  geoSeal: (signal?: AbortSignal) => getData<GeoSeal>('/geo/seal', undefined, signal),
  provinceEntities: (prov: string, page = 1, size = 50) =>
    getPaged<EntitySummary>(`/geo/${prov}/entities`, { page, size }),
  metaProvinces: (signal?: AbortSignal) => getData<ProvinceMeta[]>('/wanted/meta/provinces', undefined, signal),
  entity: (cdp: string) => getData<EntityDetail>(`/entities/${cdp}`),
  entityInventory: (cdp: string, page = 1, size = 50) =>
    getPaged<VehicleListItem>(`/entities/${cdp}/inventory`, { page, size }),
  entityDelta: (cdp: string, page = 1, size = 50, since?: string) =>
    getPaged<DeltaEvent>(`/entities/${cdp}/delta`, { page, size, since }),
  vehicleHistory: (ulid: string, page = 1, size = 100) =>
    getPaged<VehicleHistoryEvent>(`/vehicles/${ulid}/history`, { page, size }),
  vehiclePlatforms: (ulid: string) => getData<VehiclePlatforms>(`/vehicles/${ulid}/platforms`),
  // 05-multiposting F1
  publishingCoverage: (cdp: string, signal?: AbortSignal) =>
    getData<PublishingCoverage>(`/publishing/${cdp}/coverage`, undefined, signal),
  publishingMatrix: (cdp: string, page = 1, size = 50) =>
    getPaged<PublishingMatrixRow>(`/publishing/${cdp}/matrix`, { page, size }),
  // 04-arbitrage F2-F5
  arbitrageDeals: (
    opts: { page?: number; size?: number; make?: string; province?: string; band?: DealBand; minSavings?: number } = {},
  ) =>
    getPaged<DealScoreItem>('/arbitrage/deals', {
      page: opts.page ?? 1, size: opts.size ?? 50, make: opts.make, province: opts.province,
      band: opts.band, min_savings: opts.minSavings,
    }),
  arbitrageDesync: (opts: { page?: number; size?: number } = {}) =>
    getPaged<DesyncItem>('/arbitrage/desync', { page: opts.page ?? 1, size: opts.size ?? 20 }),
  arbitrageMethodology: () => getData<ArbitrageMethodology>('/arbitrage/methodology'),
  arbitrageSummary: (signal?: AbortSignal) => getData<ArbitrageSummary>('/arbitrage/summary', undefined, signal),
  arbitrageTimeCurves: (make: string, model: string, year: number) =>
    getData<TimeCurves>(`/arbitrage/time-curves/${encodeURIComponent(make)}/${encodeURIComponent(model)}`, { year }),
  arbitrageGeo: (make: string, model: string, year: number) =>
    getData<GeoArbitrageResponse>(`/arbitrage/geo/${encodeURIComponent(make)}/${encodeURIComponent(model)}`, { year }),
  // 03-garage-fleet F4
  marketSegmentStats: (make: string, model: string, year: number, fuel: string, province?: string | null) =>
    getData<MarketSegmentStats>(
      `/market/segments/${encodeURIComponent(make)}/${encodeURIComponent(model)}/stats`,
      { year, fuel, province: province ?? undefined },
    ),
  marketPricePosition: (ulid: string) => getData<PricePosition>(`/market/price-position/${ulid}`),
  marketProvincesDemand: (signal?: AbortSignal) =>
    getData<ProvinceDemand[]>('/market/provinces/demand', undefined, signal),
  /** Every marque the census lists, canonicalised, most-listed first. */
  marketMakes: (signal?: AbortSignal) => getData<CensusMake[]>('/market/makes', undefined, signal),
  /** The models the census lists under one canonical marque. */
  marketModels: (make: string, signal?: AbortSignal) =>
    getData<CensusModel[]>('/market/models', { make }, signal),
  /** Rotating slice of real listed vehicles for the public landing strip. */
  marketShowcase: (limit = 12, signal?: AbortSignal) =>
    getData<ShowcaseVehicle[]>('/market/showcase', { limit }, signal),
  /** Vehicles the deal-score run banded as underpriced against their own cohort. */
  marketOpportunities: (limit = 10, signal?: AbortSignal) =>
    getData<OpportunityVehicle[]>('/market/opportunities', { limit }, signal),
  /** Exact number of listings matching a filter combination, from `search_cube`. */
  searchCount: ({ is_family, ...rest }: SearchCountParams, signal?: AbortSignal) =>
    // The query-string layer carries strings and numbers; the one boolean is
    // serialised here rather than widening that contract for a single flag.
    getData<SearchCount>(
      '/search/count',
      { ...rest, ...(is_family === undefined ? {} : { is_family: String(is_family) }) },
      signal,
    ),
  /** Marques for the picker, counted from the same table as `searchCount`. */
  searchMakes: (signal?: AbortSignal) => getData<CensusMake[]>('/search/makes', undefined, signal),
  /** Models under one marque, counted from the same table as `searchCount`. */
  searchModels: (make: string, signal?: AbortSignal) =>
    getData<CensusModel[]>('/search/models', { make }, signal),
  /** Versions filed under one model — the picker's third level. */
  searchSubmodels: (make: string, model: string, signal?: AbortSignal) =>
    getData<CensusSubmodel[]>('/search/submodels', { make, model }, signal),
  /** Resolve a written sentence into structured filters. */
  searchParse: (q: string, signal?: AbortSignal) =>
    getData<ParsedQuery>('/search/parse', { q }, signal),
  /** Provinces with their live counts, narrowed by the marque/model in play. */
  searchProvinces: (params: { make?: string; model?: string } = {}, signal?: AbortSignal) =>
    getData<CountedProvince[]>('/search/provinces', { ...params }, signal),
  // 00-marketplace-engine F5/F6
  engineStatus: (signal?: AbortSignal) => getData<EngineStatus>('/engine/status', undefined, signal),
  sources: (signal?: AbortSignal) => getData<SourceHealthRow[]>('/sources', undefined, signal),
  alerts: (page = 1, size = 50, signal?: AbortSignal) =>
    getPaged<AlertRow>('/alerts', { page, size }, signal),
  // 09-trading-terminal F2
  terminalSymbols: (q: string, opts: { province?: string; limit?: number } = {}, signal?: AbortSignal) =>
    getData<TerminalSymbol[]>('/terminal/symbols', { q, province: opts.province, limit: opts.limit }, signal),
  terminalOhlc: (symbolKey: string, range: TerminalRange = 'ALL', signal?: AbortSignal) =>
    getData<Bar[]>(`/terminal/${encodeURIComponent(symbolKey)}/ohlc`, { range }, signal),
  terminalStats: (symbolKey: string, signal?: AbortSignal) =>
    getData<TerminalStats | TerminalStatsInsufficient>(`/terminal/${encodeURIComponent(symbolKey)}/stats`, undefined, signal),
  terminalRating: (symbolKey: string, vehicleUlid: string, signal?: AbortSignal) =>
    getData<TerminalRating>(`/terminal/${encodeURIComponent(symbolKey)}/rating/${vehicleUlid}`, undefined, signal),
  terminalMethodology: (signal?: AbortSignal) =>
    getData<Record<string, unknown>>('/terminal/methodology', undefined, signal),
  terminalScreener: (
    opts: { province?: string; make?: string; sort?: string; limit?: number } = {},
    signal?: AbortSignal,
  ) =>
    getData<TerminalScreenerRow[]>(
      '/terminal/screener',
      { province: opts.province, make: opts.make, sort: opts.sort, limit: opts.limit },
      signal,
    ),
  terminalSaleInference: (symbolKey: string, signal?: AbortSignal) =>
    getData<TerminalSaleInference>(`/terminal/${encodeURIComponent(symbolKey)}/sale-inference`, undefined, signal),
  // 07-marketing F1-F4
  listingAudit: (
    cdp: string,
    opts: { page?: number; size?: number; includePricePosition?: boolean } = {},
    signal?: AbortSignal,
  ) =>
    getPagedWithMeta<ListingAuditItem>(`/entities/${cdp}/listing-audit`, {
      page: opts.page ?? 1, size: opts.size ?? 50,
      include_price_position: opts.includePricePosition ? 'true' : undefined,
    }, signal),
  channelRadar: (cdp: string, signal?: AbortSignal) =>
    getData<ChannelRadar>(`/entities/${cdp}/channel-radar`, undefined, signal),
  // Feed download deliberately bypasses getData (the response is CSV/JSON-LD text,
  // not the {ok,data,error,meta} envelope) — returns the raw Blob + export headers so
  // the caller can trigger a browser download.
  feedDownloadUrl: (cdp: string, target: MarketingFeedTarget) => `${BASE}/entities/${cdp}/feed/${target}`,
  feedReport: (cdp: string, target: MarketingFeedTarget, signal?: AbortSignal) =>
    getData<FeedReport>(`/entities/${cdp}/feed/${target}/report`, undefined, signal),
  // 09-trading-terminal F5 — real sector news (C10), V5-fresh-verified only.
  terminalNews: (opts: { symbolKey?: string; limit?: number } = {}, signal?: AbortSignal) =>
    getData<TerminalNewsItem[]>('/terminal/news', { symbol_key: opts.symbolKey, limit: opts.limit }, signal),
};
