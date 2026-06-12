-- 0005_types_and_guards.sql — ENUM type system, extensions, shared append-only guard.
-- Additive, idempotent, reversible. (03-DATA-MODEL §2; MASTER_PLAN C-1.)
-- Replaces the scattered TEXT+CHECK of 0002-0004 with one authoritative ENUM set,
-- the shared mutation-block trigger function, and the search/crypto extensions.

CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- fuzzy name/alias search (GIN trigram)
CREATE EXTENSION IF NOT EXISTS btree_gin;   -- composite GIN (enum + trigram) for filtered search
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- gen_random_uuid fallback / digest if ever needed

-- ---- Entity taxonomy (the full ontology, 01-ENTITY-ONTOLOGY §2 / C-6) ----
-- 'cadena' retained ONLY for migration readability; never newly assigned (D-11).
DO $$ BEGIN
  CREATE TYPE entity_kind AS ENUM (
    'concesionario_oficial', 'agente_oficial', 'compraventa', 'garaje', 'desguace',
    'rent_a_car_vo', 'subasta', 'importador', 'oem_vo_portal', 'plataforma',
    'cadena'  -- DEPRECATED, read-only
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Organization layer types (chains/groups/brands/operators, 03 §3.3).
DO $$ BEGIN
  CREATE TYPE org_type AS ENUM (
    'chain_compraventa', 'dealer_group', 'rentacar_brand',
    'oem', 'auction_operator', 'platform_operator'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE entity_status AS ENUM ('active', 'closed', 'unverified');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Where the authoritative kind came from (precedence ladder, 01-ONTOLOGY §6.5).
-- registral/oem_locator/legal_census/curated_brandlist > classifier > platform_label.
DO $$ BEGIN
  CREATE TYPE kind_source AS ENUM (
    'registral', 'oem_locator', 'legal_census', 'curated_brandlist',
    'classifier', 'platform_label', 'manual'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- WAF / bot-defense posture (00-TIER1-REGISTRY; routes the fetch engine).
DO $$ BEGIN
  CREATE TYPE waf_kind AS ENUM (
    'none', 'cloudflare', 'akamai', 'datadome', 'perimeterx', 'imperva',
    'geetest', 'adevinta_bon', 'app_signed', 'other'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Vehicle lifecycle state (current snapshot).
DO $$ BEGIN
  CREATE TYPE vehicle_status AS ENUM ('available', 'reserved', 'gone');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- The delta event grammar (append-only history).
DO $$ BEGIN
  CREATE TYPE vehicle_event_type AS ENUM (
    'NEW', 'GONE', 'REAPPEARED',
    'PRICE_CHANGE', 'PHOTO_CHANGE', 'KM_CHANGE',
    'STATUS_CHANGE', 'SPEC_CHANGE'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Platform listing membership state (the dual-membership edge, 03 §4.3).
DO $$ BEGIN
  CREATE TYPE listing_status AS ENUM ('listed', 'removed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---- Shared trigger: forbid UPDATE/DELETE on any append-only log (principle #3) ----
-- DETACH/DROP PARTITION are DDL, not row DELETEs, so archival of cold months is NOT
-- blocked; this only forbids application-level UPDATE/DELETE of individual rows.
CREATE OR REPLACE FUNCTION cardeep_block_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'append-only table %: % forbidden (history is immutable)',
    TG_TABLE_NAME, TG_OP USING ERRCODE = 'restrict_violation';
END $$;

-- Rollback:
-- DROP FUNCTION IF EXISTS cardeep_block_mutation();
-- DROP TYPE IF EXISTS listing_status;
-- DROP TYPE IF EXISTS vehicle_event_type;
-- DROP TYPE IF EXISTS vehicle_status;
-- DROP TYPE IF EXISTS waf_kind;
-- DROP TYPE IF EXISTS kind_source;
-- DROP TYPE IF EXISTS entity_status;
-- DROP TYPE IF EXISTS org_type;
-- DROP TYPE IF EXISTS entity_kind;
-- (extensions pg_trgm/btree_gin/pgcrypto left installed: shared, harmless, used by 0006+)
