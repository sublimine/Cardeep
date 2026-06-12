-- 0006_entity_evolve.sql — evolve the live entity table to the full ontology.
-- Additive + IN-PLACE (12,862 live rows preserved, never recreated). 03-DATA-MODEL §3.1-3.2.
-- Pre-flight verified 2026-06-12: kind in {compraventa,concesionario_oficial,desguace,garaje},
-- status in {active}, website_waf all NULL -> every legacy value is valid for the new ENUMs.

-- (a) Drop the legacy 0002 CHECK constraints. The TEXT->ENUM swap below would FAIL while
--     these CHECKs reference the old TEXT column, so they must go first. The ENUM itself is
--     now the authoritative domain (self-documenting, additively widenable via ALTER TYPE).
ALTER TABLE entity DROP CONSTRAINT IF EXISTS entity_kind_check;
ALTER TABLE entity DROP CONSTRAINT IF EXISTS entity_status_check;
ALTER TABLE entity DROP CONSTRAINT IF EXISTS entity_website_waf_check;

-- (b) Pin the ULID shape so a malformed id cannot enter (26 Crockford chars).
--     NOT VALID: enforced on new rows immediately; legacy rows validated after audit (0006b).
ALTER TABLE entity
  ADD CONSTRAINT entity_ulid_shape CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$') NOT VALID;

-- (c) Swap kind/status/website_waf TEXT -> ENUM (USING cast; COALESCE waf NULL -> 'none').
--     A TEXT column default cannot auto-cast to the ENUM during the TYPE swap, so drop the
--     defaults FIRST, swap the types, then re-establish the defaults as ENUM literals.
ALTER TABLE entity ALTER COLUMN status DROP DEFAULT;
ALTER TABLE entity
  ALTER COLUMN kind        TYPE entity_kind   USING kind::entity_kind,
  ALTER COLUMN status      TYPE entity_status USING status::entity_status,
  ALTER COLUMN website_waf TYPE waf_kind      USING COALESCE(website_waf, 'none')::waf_kind;
ALTER TABLE entity ALTER COLUMN status SET DEFAULT 'unverified';
ALTER TABLE entity ALTER COLUMN website_waf SET DEFAULT 'none';

-- (d) Organization layer FK column (chain vs branch). NULL = standalone POS.
--     The FK constraint itself is added in 0007, once organization exists.
ALTER TABLE entity ADD COLUMN IF NOT EXISTS org_id TEXT;

-- (e) Sells-cars gate (D-4): NULL=unknown, FALSE=pure taller (filtered out of the numerator).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS sells_cars BOOLEAN;

-- (f) Which precedence rung decided the kind (D-6 / §6.5). Legacy default = 'manual'.
ALTER TABLE entity ADD COLUMN IF NOT EXISTS kind_source kind_source NOT NULL DEFAULT 'manual';

-- (g) Geocode provenance + quality (no PostGIS: plain lat/lon doubles already exist).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS geocode_source TEXT;     -- 'ine'|'osm'|'google'|'derived'
ALTER TABLE entity ADD COLUMN IF NOT EXISTS geocode_precision TEXT   -- 'rooftop'|'street'|...
  CONSTRAINT entity_geocode_precision_check
  CHECK (geocode_precision IS NULL OR geocode_precision IN
         ('rooftop','street','postcode','municipality','province'));

-- (h) Defense detail beyond the WAF enum (raw fingerprint the fetch engine recorded).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS defense_detail JSONB;    -- {server, cf_ray, x_cdn, challenge, ...}

-- (i) Soft-close audit (mutation doctrine: closure is a state, not a delete).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS closed_at TIMESTAMPTZ;
ALTER TABLE entity ADD COLUMN IF NOT EXISTS close_reason TEXT;

-- (j) Data-quality / dedup helpers.
ALTER TABLE entity ADD COLUMN IF NOT EXISTS canonical_key TEXT;      -- the exact key cdp_code hashed (audit)
ALTER TABLE entity ADD COLUMN IF NOT EXISTS attest_count INT NOT NULL DEFAULT 1; -- # orthogonal sources

-- (k) Index set (the live 0002 indexes are kept; these are the additions, 03 §3.1).
CREATE INDEX IF NOT EXISTS idx_entity_org           ON entity (org_id) WHERE org_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entity_sells         ON entity (kind) WHERE sells_cars IS NOT FALSE;
CREATE INDEX IF NOT EXISTS idx_entity_kind_prov     ON entity (kind, province_code);
CREATE INDEX IF NOT EXISTS idx_entity_latlon        ON entity (lat, lon) WHERE lat IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entity_tradename_trgm ON entity USING gin (trade_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_entity_legalname_trgm ON entity USING gin (legal_name gin_trgm_ops);

-- (l) The platform facet extension table (1:1 with platform-kind entities, 03 §3.2).
--     Avoids widening entity with columns NULL for 99.99% of rows.
CREATE TABLE IF NOT EXISTS platform_meta (
    entity_ulid     TEXT PRIMARY KEY REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    listing_counter BIGINT,             -- last re-derived live inventory counter
    counter_at      TIMESTAMPTZ,        -- when (counters drift daily)
    data_surface    TEXT,               -- 'next_data'|'graphql'|'json_ld'|'internal_api'|'sitemap'|'es_facet'|'app_api'
    surface_detail  JSONB,              -- endpoint, payload template, header profile ref
    requires_creds  BOOLEAN NOT NULL DEFAULT FALSE,   -- B2B login (BCA/Autorola)
    is_platform_like BOOLEAN NOT NULL DEFAULT FALSE,  -- subasta that also aggregates (D-7)
    CHECK (data_surface IS NULL OR data_surface IN
      ('next_data','graphql','json_ld','internal_api','sitemap','es_facet','app_api'))
);

-- (m) The platform facet view: a platform IS an entity of platform-kind (never a 2nd table).
CREATE OR REPLACE VIEW platform AS
  SELECT e.entity_ulid, e.cdp_code, e.trade_name, e.website, e.is_tier1, e.website_waf,
         e.kind, pm.listing_counter, pm.counter_at, pm.data_surface, pm.requires_creds,
         pm.is_platform_like
    FROM entity e
    LEFT JOIN platform_meta pm USING (entity_ulid)
   WHERE e.kind IN ('plataforma','oem_vo_portal')
      OR pm.is_platform_like;

-- Rollback:
-- DROP VIEW IF EXISTS platform;
-- DROP TABLE IF EXISTS platform_meta;
-- DROP INDEX IF EXISTS idx_entity_legalname_trgm;
-- DROP INDEX IF EXISTS idx_entity_tradename_trgm;
-- DROP INDEX IF EXISTS idx_entity_latlon;
-- DROP INDEX IF EXISTS idx_entity_kind_prov;
-- DROP INDEX IF EXISTS idx_entity_sells;
-- DROP INDEX IF EXISTS idx_entity_org;
-- ALTER TABLE entity DROP COLUMN IF EXISTS attest_count;
-- ALTER TABLE entity DROP COLUMN IF EXISTS canonical_key;
-- ALTER TABLE entity DROP COLUMN IF EXISTS close_reason;
-- ALTER TABLE entity DROP COLUMN IF EXISTS closed_at;
-- ALTER TABLE entity DROP COLUMN IF EXISTS defense_detail;
-- ALTER TABLE entity DROP CONSTRAINT IF EXISTS entity_geocode_precision_check;
-- ALTER TABLE entity DROP COLUMN IF EXISTS geocode_precision;
-- ALTER TABLE entity DROP COLUMN IF EXISTS geocode_source;
-- ALTER TABLE entity DROP COLUMN IF EXISTS kind_source;
-- ALTER TABLE entity DROP COLUMN IF EXISTS sells_cars;
-- ALTER TABLE entity DROP COLUMN IF EXISTS org_id;
-- ALTER TABLE entity ALTER COLUMN website_waf DROP DEFAULT;
-- ALTER TABLE entity ALTER COLUMN status DROP DEFAULT;
-- ALTER TABLE entity
--   ALTER COLUMN kind        TYPE TEXT USING kind::text,
--   ALTER COLUMN status      TYPE TEXT USING status::text,
--   ALTER COLUMN website_waf TYPE TEXT USING website_waf::text;
-- ALTER TABLE entity ALTER COLUMN status SET DEFAULT 'unverified';
-- ALTER TABLE entity DROP CONSTRAINT IF EXISTS entity_ulid_shape;
-- ALTER TABLE entity ADD CONSTRAINT entity_kind_check
--   CHECK (kind IN ('concesionario_oficial','compraventa','garaje','desguace','plataforma','cadena'));
-- ALTER TABLE entity ADD CONSTRAINT entity_status_check
--   CHECK (status IN ('active','closed','unverified'));
-- ALTER TABLE entity ADD CONSTRAINT entity_website_waf_check
--   CHECK (website_waf IS NULL OR website_waf IN
--          ('none','cloudflare','akamai','datadome','perimeterx','imperva','other'));
