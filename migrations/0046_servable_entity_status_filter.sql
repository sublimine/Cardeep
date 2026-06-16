-- 0046_servable_entity_status_filter.sql — make servable_entity exclude evicted/closed dealers:
-- the entity-level companion to 0045 (which fixed servable_vehicle). Coherence audit pass-4 D5 — and
-- the parallel I explicitly flagged when fixing /geo through servable_entity (commit 3f7b456).
--
-- The publish-gate view 0031 declares ("the API reads through these views, never the raw tables ...
-- the subject vanishes from every served surface, mechanically, not by promise") guarded ONLY the
-- quarantine subquery, NOT status. evict.py tombstones a dealer via UPDATE status='evicted' (correct,
-- no hard-delete), but this view passed it through — so the first evict run would leak an evicted
-- dealer onto the served surface. Same dead-promise the vehicle side had before 0045.
--
-- Fix: add `status NOT IN ('evicted','closed')`. Today (verified): 0 evicted, 0 closed (380,622
-- active + 11,322 unverified) -> servable_entity stays 391,944, zero regression. Forward/defence-in-
-- depth: the instant evict.py flips a dealer to 'evicted', it vanishes from every served surface.
-- The 37-column projection is reproduced verbatim from the live view (no served column drifts).
-- Additive, idempotent (CREATE OR REPLACE), reversible (restore the quarantine-only definition).

CREATE OR REPLACE VIEW servable_entity AS
  SELECT entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae, province_code,
         municipality_code, comarca_id, address, postcode, lat, lon, phone, email, website,
         website_waf, is_tier1, status, recipe_version, first_discovered_source, created_at,
         last_seen, org_id, sells_cars, kind_source, geocode_source, geocode_precision,
         defense_detail, closed_at, close_reason, canonical_key, attest_count, defense_tier,
         source_group, role
    FROM entity e
   WHERE e.status NOT IN ('evicted', 'closed')          -- NEW: a tombstoned/closed dealer is not servable
     AND NOT (EXISTS ( SELECT 1
            FROM gestion_item g
           WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'entity'::text
             AND g.subject_key = e.cdp_code));

-- Rollback (restore the 0031 quarantine-only definition — same 37-column projection, no status guard):
-- CREATE OR REPLACE VIEW servable_entity AS
--   SELECT entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae, province_code,
--          municipality_code, comarca_id, address, postcode, lat, lon, phone, email, website,
--          website_waf, is_tier1, status, recipe_version, first_discovered_source, created_at,
--          last_seen, org_id, sells_cars, kind_source, geocode_source, geocode_precision,
--          defense_detail, closed_at, close_reason, canonical_key, attest_count, defense_tier,
--          source_group, role
--     FROM entity e
--    WHERE NOT (EXISTS ( SELECT 1 FROM gestion_item g
--            WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'entity'::text
--              AND g.subject_key = e.cdp_code));
