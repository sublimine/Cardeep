-- 0052_country.sql — FASE-0 country dimension: make the census country-parametrizable
-- WITHOUT changing ANY Spain (ES) behavior. THE INVARIANT (non-negotiable): every existing
-- row stays ES and every cdp_code is byte-identical to today (cdp_code is NOT touched here at
-- all — the mint is parametrized in code with country_code defaulting to 'ES'). This migration
-- only ADDS a country_code dimension to the geo backbone + entity so a future 2nd country can
-- coexist; it DROPS NOTHING and breaks NO foreign key.
--
-- WHY ADDITIVE-ONLY / FK-SAFE (verified live against the running cardeep DB, 2026-06-23):
--   * geo_province.code  (CHAR(2) PK geo_province_pkey)  is referenced by 5 FKs:
--       entity.province_code, geo_comarca.province_code, geo_municipality.province_code,
--       denominator_estimate.province_code, organization.hq_province_code.
--   * geo_municipality.code (CHAR(5) PK geo_municipality_pkey) is referenced by 1 FK:
--       entity.municipality_code.
--   * entity.cdp_code (UNIQUE index uq_entity_cdp_code) is referenced by 1 FK:
--       entity_completion.cdp_code.
--   Adding a column and adding a composite UNIQUE never invalidates an existing FK that targets
--   a still-present PK/UNIQUE. We LEAVE the single-column PKs in place, so all 7 FKs keep
--   resolving. We do NOT touch entity.cdp_code (no value changes => entity_completion FK intact).
--
-- WHY NOT NULL DEFAULT 'ES': the DEFAULT stamps every existing row (431,211 entity / 52 province
--   / 8,132 municipality / 323 comarca) as 'ES' atomically, so the backfill is implicit, complete,
--   and zero-NULL — no NOT NULL or FK violation is possible on existing rows. 'ES' is exactly 2
--   chars, so CHAR(2) carries no blank-padding ambiguity.
--
-- DELIBERATELY NOT DONE in FASE-0 (deferred to the country-onboarding migration, when ES is no
--   longer the sole tenant — all are FK-breaking or country-specific and unnecessary while every
--   row is ES, so they are out of scope by design):
--     (a) swapping geo_province/geo_municipality PK to (country_code, code) — would force
--         composite-rewriting all 7 FKs; the composite UNIQUE added below makes that swap
--         mechanical later but it stays a separate, reviewed migration.
--     (b) adding country_code to denominator_estimate / organization and rewriting their FKs.
--     (c) relaxing the ES-specific CHECKs municipality_province_prefix (geo_municipality:
--         left(code,2)=province_code) and chk_entity_muni_province (entity) to per-country —
--         every row is ES today so both are satisfied; a country whose municipality codes are
--         not <prov2><muni3> must relax them at onboarding, NOT here.
--     (d) country_code on vehicle (2,311,202 rows) — vehicle.country is derivable via
--         vehicle.entity_ulid -> entity.country_code, so FASE-0 keeps the geo backbone + entity
--         as the single source of the country dimension (YAGNI; avoids a 2.3M-row rewrite).
--     (e) geo_comarca composite UNIQUE — geo_comarca has no `code` column (PK is `id`, UNIQUE is
--         (province_code,name)); it still gets country_code for consistency but no (country,code)
--         surface applies. Extend to (country_code,province_code,name) at onboarding if needed.
--
-- Idempotent: ADD COLUMN IF NOT EXISTS, CREATE INDEX IF NOT EXISTS, and each named composite
-- UNIQUE is guarded by a DO-block that adds it only when absent — so re-running is a no-op.
-- Reversible: a commented rollback section follows the forward DDL (per the runner convention;
-- the runner strips everything from the LAST rollback marker onward, so that marker appears
-- exactly once in this file — here, at the bottom).

-- 1. Add the country dimension to the geo backbone + entity. CHAR(2), NOT NULL, DEFAULT 'ES'.
--    DEFAULT 'ES' implicitly backfills every existing row as Spain.
ALTER TABLE geo_province     ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE geo_comarca      ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE geo_municipality ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE entity           ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

-- 2. Composite UNIQUE constraints — the per-country identity surface for a future PK swap.
--    DO NOT drop or replace the existing single-column PKs: geo_province_pkey(code) and
--    geo_municipality_pkey(code) STAY so all referencing FKs remain valid. We only ADD a
--    composite UNIQUE (country_code, code). PG has no ADD CONSTRAINT IF NOT EXISTS, so each is
--    guarded by a presence check to keep the migration idempotent.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_geo_province_country_code') THEN
    ALTER TABLE geo_province
      ADD CONSTRAINT uq_geo_province_country_code UNIQUE (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_geo_municipality_country_code') THEN
    ALTER TABLE geo_municipality
      ADD CONSTRAINT uq_geo_municipality_country_code UNIQUE (country_code, code);
  END IF;
END
$$;

-- 3. Indexes for country-scoped queries (cheap, additive).
CREATE INDEX IF NOT EXISTS idx_entity_country           ON entity (country_code);
CREATE INDEX IF NOT EXISTS idx_geo_municipality_country ON geo_municipality (country_code);

-- Rollback:
-- DROP INDEX IF EXISTS idx_geo_municipality_country;
-- DROP INDEX IF EXISTS idx_entity_country;
-- ALTER TABLE geo_municipality DROP CONSTRAINT IF EXISTS uq_geo_municipality_country_code;
-- ALTER TABLE geo_province     DROP CONSTRAINT IF EXISTS uq_geo_province_country_code;
-- ALTER TABLE entity           DROP COLUMN IF EXISTS country_code;
-- ALTER TABLE geo_municipality DROP COLUMN IF EXISTS country_code;
-- ALTER TABLE geo_comarca      DROP COLUMN IF EXISTS country_code;
-- ALTER TABLE geo_province     DROP COLUMN IF EXISTS country_code;
