-- 0053_country_onboarding.sql — promote the geo identity to (country_code, code) and
-- rewrite every referencing FK to composite, eliminating the proven PK collision that
-- blocks a 2nd tenant (live probe: INSERT geo_province(code='28',...,country_code='DE')
-- fails on geo_province_pkey(code) even with ccaa_code supplied). This is the FK-breaking
-- half deferred by 0052_country.sql:25-31 (items (a), (b), (c)).
--
-- THE INVARIANT (non-negotiable): every existing ES row stays byte-identical. ALL rows are
-- country_code='ES' today (entity non-ES=0, geo_province=52, geo_municipality=8,132 — all ES),
-- so the swap from PK(code) to PK(country_code='ES',code) is a pure 1:1 relabel: no row is
-- renumbered, no FK target changes for ES, no cdp_code/canonical_key is touched (this migration
-- never UPDATEs a code-bearing column). ES queries stay byte-identical because every geo lookup
-- resolves the same ES row via the composite key (all ES rows carry country_code='ES'), and the
-- API resolve/serve queries key on cdp_code/entity_ulid, not on geo PKs.
--
-- VERIFIED LIVE against the running cardeep DB (2026-06-23) before writing:
--   * geo_province_pkey = PRIMARY KEY (code); geo_municipality_pkey = PRIMARY KEY (code).
--   * Composite UNIQUEs from 0052 present: uq_geo_province_country_code (country_code, code),
--     uq_geo_municipality_country_code (country_code, code).
--   * Exactly 6 FKs target the geo single-column PKs (5 -> geo_province, 1 -> geo_municipality):
--       entity_province_code_fkey, entity_municipality_code_fkey, geo_comarca_province_code_fkey,
--       geo_municipality_province_code_fkey, denominator_estimate_province_code_fkey,
--       organization_hq_province_code_fkey.  (entity_completion_cdp_code_fkey is NOT a geo FK —
--       cdp_code stays globally unique via the CDP-{cc}- prefix; left untouched.)
--   * denominator_estimate.country_code and organization.country_code DO NOT EXIST yet — added here.
--   * entity.country_code / geo_comarca.country_code / geo_municipality.country_code exist (0052).
--   * Nullable FK cols: entity.province_code, entity.municipality_code,
--     denominator_estimate.province_code, organization.hq_province_code -> MATCH SIMPLE is required.
--   * Two ES-shaped CHECKs assume INE <prov2><muni3> coding:
--       geo_municipality.municipality_province_prefix = CHECK (left(code,2) = province_code)
--         [origin 0001_geo.sql:26]
--       entity.chk_entity_muni_province =
--         CHECK (municipality_code IS NULL OR province_code IS NULL
--                OR left(municipality_code,2) = province_code)  [origin 0041:14-17]
--
-- RUNNER CONSTRAINT (scripts/migrate.py:117-124): up() opens `async with conn.transaction():`
-- and executes each split statement separately. A literal BEGIN;/COMMIT; would be emitted as a
-- standalone statement inside the already-open transaction and asyncpg would error. THEREFORE
-- THIS FILE OMITS BEGIN/COMMIT — the runner's own transaction gives all-or-nothing atomicity
-- (any exception auto-aborts the whole migration; the ledger insert at :121 commits only on
-- success). A manual psql apply must wrap this file in its own external BEGIN; ... ROLLBACK;.
--
-- IDEMPOTENCE: the schema_migrations ledger (PK on version, migrate.py:122) skips an already-
-- applied 0053, so `migrate up` never re-runs it (same guard 0052 relies on). For belt-and-braces
-- safety against a manual partial apply, every DROP CONSTRAINT uses IF EXISTS and every ADD
-- CONSTRAINT is guarded by a DO-block presence check (mirrors 0052:61-77). Re-running is a no-op.
--
-- ORDERING (matters): for each geo table we ADD the composite PRIMARY KEY FIRST, then DROP the
-- now-redundant composite UNIQUE — so a unique surface always exists (never momentarily unguarded).
-- The 6 FKs are dropped before the PK swap and re-added (composite) after it, all inside one txn.

-- (item b) Add country_code to the two tables 0052 skipped. DEFAULT 'ES' backfills every existing
--   row atomically (denominator_estimate / organization are all-ES today). Naturally idempotent.
ALTER TABLE denominator_estimate ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE organization         ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

-- 1. Drop the 6 child FKs that target the single-column geo PKs (IF EXISTS = idempotent).
ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_province_code_fkey;
ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_municipality_code_fkey;
ALTER TABLE geo_comarca          DROP CONSTRAINT IF EXISTS geo_comarca_province_code_fkey;
ALTER TABLE geo_municipality     DROP CONSTRAINT IF EXISTS geo_municipality_province_code_fkey;
ALTER TABLE denominator_estimate DROP CONSTRAINT IF EXISTS denominator_estimate_province_code_fkey;
ALTER TABLE organization         DROP CONSTRAINT IF EXISTS organization_hq_province_code_fkey;

-- 2. Swap the geo PKs to composite (country_code, code). ADD composite PK FIRST (uniqueness
--    never lapses — the 0052 composite UNIQUE still covers the data until the PK exists), THEN
--    drop the old single-column PK, THEN drop the now-redundant composite UNIQUE. Each ADD is
--    guarded so a re-run is a no-op.
ALTER TABLE geo_province     DROP CONSTRAINT IF EXISTS geo_province_pkey;
ALTER TABLE geo_municipality DROP CONSTRAINT IF EXISTS geo_municipality_pkey;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'geo_province_pkey'
                 AND conrelid = 'geo_province'::regclass) THEN
    ALTER TABLE geo_province ADD CONSTRAINT geo_province_pkey PRIMARY KEY (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'geo_municipality_pkey'
                 AND conrelid = 'geo_municipality'::regclass) THEN
    ALTER TABLE geo_municipality ADD CONSTRAINT geo_municipality_pkey PRIMARY KEY (country_code, code);
  END IF;
END
$$;

-- Drop the redundant composite UNIQUEs (the composite PK now enforces the same uniqueness).
ALTER TABLE geo_province     DROP CONSTRAINT IF EXISTS uq_geo_province_country_code;
ALTER TABLE geo_municipality DROP CONSTRAINT IF EXISTS uq_geo_municipality_country_code;

-- 3. Re-add the 6 FKs as COMPOSITE (country_code, <col>) -> (country_code, code). Every child
--    table now carries country_code (entity/geo_comarca/geo_municipality from 0052,
--    denominator_estimate/organization added above), all 'ES', so each (ES, fk_col) pair resolves
--    1:1 to the existing (ES, code) parent — no orphan, no new rejection. MATCH SIMPLE (the
--    default; do NOT write MATCH FULL) so a NULL province/municipality component leaves the row
--    unenforced exactly as today (preserves NULL-province gap-dealer behavior). Each guarded.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'geo_comarca_province_code_fkey'
                 AND conrelid = 'geo_comarca'::regclass) THEN
    ALTER TABLE geo_comarca ADD CONSTRAINT geo_comarca_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'geo_municipality_province_code_fkey'
                 AND conrelid = 'geo_municipality'::regclass) THEN
    ALTER TABLE geo_municipality ADD CONSTRAINT geo_municipality_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'entity_province_code_fkey'
                 AND conrelid = 'entity'::regclass) THEN
    ALTER TABLE entity ADD CONSTRAINT entity_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'entity_municipality_code_fkey'
                 AND conrelid = 'entity'::regclass) THEN
    ALTER TABLE entity ADD CONSTRAINT entity_municipality_code_fkey
      FOREIGN KEY (country_code, municipality_code) REFERENCES geo_municipality (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'denominator_estimate_province_code_fkey'
                 AND conrelid = 'denominator_estimate'::regclass) THEN
    ALTER TABLE denominator_estimate ADD CONSTRAINT denominator_estimate_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'organization_hq_province_code_fkey'
                 AND conrelid = 'organization'::regclass) THEN
    ALTER TABLE organization ADD CONSTRAINT organization_hq_province_code_fkey
      FOREIGN KEY (country_code, hq_province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

-- 4. (item c) Relax the two ES-shaped geo CHECKs to per-country. Gate the ORIGINAL predicate on
--    country_code='ES' so it stays BINDING and byte-identical for every ES row (for an ES row,
--    country_code='ES' makes the `country_code <> 'ES'` disjunct FALSE, forcing PG to evaluate the
--    original left(...)=... predicate verbatim — every ES row that passed before still passes, any
--    ES violation is still rejected), while a non-ES municipality scheme is unconstrained. Done in
--    THIS atomic migration so geo integrity is never momentarily unguarded. The entity CHECK
--    preserves 0041's NULL-tolerant shape EXACTLY for ES.
ALTER TABLE geo_municipality DROP CONSTRAINT IF EXISTS municipality_province_prefix;
ALTER TABLE geo_municipality ADD CONSTRAINT municipality_province_prefix
  CHECK (country_code <> 'ES' OR left(code, 2) = province_code);

ALTER TABLE entity DROP CONSTRAINT IF EXISTS chk_entity_muni_province;
ALTER TABLE entity ADD CONSTRAINT chk_entity_muni_province
  CHECK (country_code <> 'ES'
         OR municipality_code IS NULL OR province_code IS NULL
         OR left(municipality_code, 2) = province_code);

-- Rollback:
-- (Reverse of the forward DDL. CLEAN ONLY while NO non-ES geo rows exist — a single-column PK on
--  `code` cannot hold ES-28 and DE-28 simultaneously; any pilot/onboarding MUST delete all
--  country_code <> 'ES' geo rows BEFORE rolling this back. Mirror the forward ordering in reverse:
--  restore the original CHECKs, drop the composite FKs, restore the single-column PKs from the
--  composite UNIQUEs, re-add the single-column FKs, then drop the two added country_code columns.)
--
-- -- 4'. Restore the original ES CHECKs (0001_geo.sql:26 / 0041:14-17 verbatim).
-- ALTER TABLE entity DROP CONSTRAINT IF EXISTS chk_entity_muni_province;
-- ALTER TABLE entity ADD CONSTRAINT chk_entity_muni_province
--   CHECK (municipality_code IS NULL OR province_code IS NULL
--          OR left(municipality_code, 2) = province_code);
-- ALTER TABLE geo_municipality DROP CONSTRAINT IF EXISTS municipality_province_prefix;
-- ALTER TABLE geo_municipality ADD CONSTRAINT municipality_province_prefix
--   CHECK (left(code, 2) = province_code);
--
-- -- 3'. Drop the 6 composite FKs.
-- ALTER TABLE organization         DROP CONSTRAINT IF EXISTS organization_hq_province_code_fkey;
-- ALTER TABLE denominator_estimate DROP CONSTRAINT IF EXISTS denominator_estimate_province_code_fkey;
-- ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_municipality_code_fkey;
-- ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_province_code_fkey;
-- ALTER TABLE geo_municipality     DROP CONSTRAINT IF EXISTS geo_municipality_province_code_fkey;
-- ALTER TABLE geo_comarca          DROP CONSTRAINT IF EXISTS geo_comarca_province_code_fkey;
--
-- -- 2'. Restore single-column PKs, then re-create the 0052 composite UNIQUEs.
-- ALTER TABLE geo_municipality DROP CONSTRAINT IF EXISTS geo_municipality_pkey;
-- ALTER TABLE geo_province     DROP CONSTRAINT IF EXISTS geo_province_pkey;
-- ALTER TABLE geo_province     ADD CONSTRAINT geo_province_pkey     PRIMARY KEY (code);
-- ALTER TABLE geo_municipality ADD CONSTRAINT geo_municipality_pkey PRIMARY KEY (code);
-- ALTER TABLE geo_province     ADD CONSTRAINT uq_geo_province_country_code     UNIQUE (country_code, code);
-- ALTER TABLE geo_municipality ADD CONSTRAINT uq_geo_municipality_country_code UNIQUE (country_code, code);
--
-- -- 1'. Re-add the 6 single-column FKs (REFERENCES geo_*(code)).
-- ALTER TABLE geo_comarca          ADD CONSTRAINT geo_comarca_province_code_fkey          FOREIGN KEY (province_code)    REFERENCES geo_province (code);
-- ALTER TABLE geo_municipality     ADD CONSTRAINT geo_municipality_province_code_fkey     FOREIGN KEY (province_code)    REFERENCES geo_province (code);
-- ALTER TABLE entity               ADD CONSTRAINT entity_province_code_fkey               FOREIGN KEY (province_code)    REFERENCES geo_province (code);
-- ALTER TABLE entity               ADD CONSTRAINT entity_municipality_code_fkey           FOREIGN KEY (municipality_code) REFERENCES geo_municipality (code);
-- ALTER TABLE denominator_estimate ADD CONSTRAINT denominator_estimate_province_code_fkey FOREIGN KEY (province_code)    REFERENCES geo_province (code);
-- ALTER TABLE organization         ADD CONSTRAINT organization_hq_province_code_fkey      FOREIGN KEY (hq_province_code) REFERENCES geo_province (code);
--
-- -- (item b'). Drop the two added country_code columns.
-- ALTER TABLE organization         DROP COLUMN IF EXISTS country_code;
-- ALTER TABLE denominator_estimate DROP COLUMN IF EXISTS country_code;
