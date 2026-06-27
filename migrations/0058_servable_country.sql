-- 0058_servable_country.sql — expose the country_code dimension on the served census views so the
-- SERVING layer can be scoped per tenant (generic-engine vector #5, SERVING country-scope).
--
-- WHY. entity.country_code exists since 0052 and the geo backbone is composite-keyed (country_code,
-- code) since 0053, but the two views the public API reads through — servable_entity (0046) and
-- v_servable_dealer (0056, "the single source of truth ... stats.py, geo.py and the seal all read
-- from here") — never projected country_code. So a served query for the Spanish census could not
-- exclude a German dealer reusing the same numeric province_code / municipality_code (0053 puts DE
-- province '28' next to ES Madrid '28'): asking for country='ES' would leak DE rows. This migration
-- adds the missing dimension so /geo, /stats and the dealer surface can filter `country_code = $pais`.
--
-- WHY ZERO-RISK. Both are CREATE OR REPLACE VIEW, APPEND-ONLY: every pre-existing column keeps its
-- name, order and type (PostgreSQL requires this for REPLACE), and country_code is added at the END.
-- All existing consumers select named columns, so the extra trailing column is invisible to them. A
-- view touches no row, no FK, no served cdp_code; idempotent; reversible (restore the prior defs in
-- Rollback). servable_entity's 37-column projection is reproduced verbatim from the live view
-- (0046) + `e.country_code`. Order matters: servable_entity first (so v_servable_dealer can read
-- se.country_code), then v_servable_dealer.

CREATE OR REPLACE VIEW servable_entity AS
  SELECT entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae, province_code,
         municipality_code, comarca_id, address, postcode, lat, lon, phone, email, website,
         website_waf, is_tier1, status, recipe_version, first_discovered_source, created_at,
         last_seen, org_id, sells_cars, kind_source, geocode_source, geocode_precision,
         defense_detail, closed_at, close_reason, canonical_key, attest_count, defense_tier,
         source_group, role,
         country_code                                       -- NEW: tenant dimension (append-only)
    FROM entity e
   WHERE e.status NOT IN ('evicted', 'closed')
     AND NOT (EXISTS ( SELECT 1
            FROM gestion_item g
           WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'entity'::text
             AND g.subject_key = e.cdp_code));

CREATE OR REPLACE VIEW v_servable_dealer AS
SELECT se.entity_ulid,
       se.cdp_code,
       se.kind,
       vdr.resolved_cdp_code,
       EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid) AS has_inventory,
       se.country_code                                      -- NEW: tenant dimension (append-only)
  FROM servable_entity se
  JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
 WHERE se.status = 'active'
   AND se.kind::text NOT IN ('particular', 'desguace')
   AND (se.kind::text <> 'garaje'
        OR EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid));

-- Rollback (restore the pre-0058 definitions WITHOUT country_code — drop v_servable_dealer's column
-- first since it reads se.country_code, then servable_entity's):
-- CREATE OR REPLACE VIEW v_servable_dealer AS
-- SELECT se.entity_ulid, se.cdp_code, se.kind, vdr.resolved_cdp_code,
--        EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid) AS has_inventory
--   FROM servable_entity se
--   JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
--  WHERE se.status = 'active' AND se.kind::text NOT IN ('particular', 'desguace')
--    AND (se.kind::text <> 'garaje' OR EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid));
-- CREATE OR REPLACE VIEW servable_entity AS
--   SELECT entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae, province_code,
--          municipality_code, comarca_id, address, postcode, lat, lon, phone, email, website,
--          website_waf, is_tier1, status, recipe_version, first_discovered_source, created_at,
--          last_seen, org_id, sells_cars, kind_source, geocode_source, geocode_precision,
--          defense_detail, closed_at, close_reason, canonical_key, attest_count, defense_tier,
--          source_group, role
--     FROM entity e
--    WHERE e.status NOT IN ('evicted', 'closed')
--      AND NOT (EXISTS ( SELECT 1 FROM gestion_item g
--             WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'entity'::text
--               AND g.subject_key = e.cdp_code));
