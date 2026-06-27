-- 0057_country_proof_guard.sql — COUNTRY-PROOF served-layer diagnostic guard.
--
-- WHAT. A single diagnostic VIEW, v_country_proof_violations, that returns any
-- SERVED cluster whose members span more than one country_code. It is the SQL
-- "mechanical belt" of the COUNTRY-PROOF invariant
-- (docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md §1 "Guard"): a build with
-- a country-blind bug that cross-merges two countries shows up here as >0 rows,
-- so the violation is detectable in CI / health checks instead of degrading the
-- served census in silence. Empty view == the invariant holds in what is served.
--
-- DUAL COVERAGE (the invariant demands BOTH served surfaces, not one):
--   * DEALER  — v_dealer_resolved (0028): the two-layer resolved dealer identity
--     (B1 v_canonical ∘ canonical_dedup Layer-2). country_code is reached by
--     JOIN entity ON entity.cdp_code = v_dealer_resolved.cdp_code (the member
--     entity's own cdp_code), grouped by resolved_cdp_code.
--   * VEHICLE — v_canonical_vehicle (0023): the served physical-car resolution of
--     the latest vam_verified vehicle-cluster run. vehicle has NO country_code
--     (mig 0003); the country is reached by JOIN vehicle -> entity (mig 0052),
--     grouped by canonical_vehicle_ulid.
--
-- COLUMNS:
--   layer        'dealer' | 'vehicle'  — which served surface the violation is on.
--   cluster_key  the offending cluster id (resolved_cdp_code | canonical_vehicle_ulid).
--   n_countries  COUNT(DISTINCT country_code) for that cluster (always > 1 here).
--   countries    the sorted distinct country_codes in the cluster (audit detail).
--
-- WHY ZERO-RISK / ADDITIVE: a VIEW is a saved query — it creates no table, touches
-- no row, breaks no FK, and alters nothing existing. CREATE OR REPLACE is
-- idempotent. It reads only pre-existing served views/tables (v_dealer_resolved,
-- v_canonical_vehicle, entity, vehicle). Reversible: DROP VIEW (see Rollback).

CREATE OR REPLACE VIEW v_country_proof_violations AS
-- DEALER layer: any resolved dealer (v_dealer_resolved) whose member entities
-- carry more than one country_code. >0 rows = cross-border dealer false-merge served.
SELECT
    'dealer'::text                                            AS layer,
    d.resolved_cdp_code                                       AS cluster_key,
    COUNT(DISTINCT e.country_code)                            AS n_countries,
    ARRAY_AGG(DISTINCT e.country_code ORDER BY e.country_code) AS countries
FROM v_dealer_resolved d
JOIN entity e ON e.cdp_code = d.cdp_code
GROUP BY d.resolved_cdp_code
HAVING COUNT(DISTINCT e.country_code) > 1

UNION ALL

-- VEHICLE layer: any served canonical vehicle whose member listings resolve (via
-- entity) to more than one country_code. >0 rows = cross-border vehicle false-merge.
SELECT
    'vehicle'::text                                           AS layer,
    vc.canonical_vehicle_ulid                                 AS cluster_key,
    COUNT(DISTINCT e.country_code)                            AS n_countries,
    ARRAY_AGG(DISTINCT e.country_code ORDER BY e.country_code) AS countries
FROM v_canonical_vehicle vc
JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
JOIN entity  e ON e.entity_ulid  = v.entity_ulid
GROUP BY vc.canonical_vehicle_ulid
HAVING COUNT(DISTINCT e.country_code) > 1;

COMMENT ON VIEW v_country_proof_violations IS
    'COUNTRY-PROOF served-layer guard: every row is a served cluster (dealer via '
    'v_dealer_resolved, or vehicle via v_canonical_vehicle) spanning >1 country_code. '
    'MUST be empty; >0 rows is a cross-border false-merge in what is served. See '
    'docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md.';

-- Rollback:
-- DROP VIEW IF EXISTS v_country_proof_violations;
