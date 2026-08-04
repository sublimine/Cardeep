-- 0099_make_canon.sql — canonical marque registry, alias table, and the immutable
-- text helpers the search layer depends on.
--
-- The problem this closes: `vehicle.make` is a free-text field written by ~90
-- different connectors, and it fragments the primary search axis. Measured before
-- the 2026-08-03 backfill, MERCEDES (9,673 rows) sat beside MERCEDES-BENZ (148,015)
-- — a 6.1% silent leak on the largest premium marque — and the census held 3,501
-- distinct spellings against roughly 130 real marques. scripts/backfill_make.py
-- already collapses the cases it knows, but it matches on EXACT lowercased keys, so
-- 'Mercedes Benz' (with a space) survives it. A normalisation FUNCTION fixes the
-- whole class instead of enumerating its members.
--
-- Design note — why a registry and not just a bigger dictionary in Python: the
-- picker needs display names with real diacritics (Citroën, Škoda), logo assets with
-- recorded provenance, rebrand chains (SsangYong -> KGM) and a listable flag. That
-- is data with its own lifecycle, and it has to be joinable from SQL at MV-build
-- time. A Python dict cannot be joined.
--
-- Additive and reversible; touches no existing object.

CREATE EXTENSION IF NOT EXISTS unaccent;

-- unaccent() is STABLE, not IMMUTABLE, because it depends on a dictionary that could
-- in principle be redefined. That makes it unusable in a generated column or a
-- functional index — PostgreSQL rejects it outright. Pinning the dictionary by name
-- makes the call deterministic, which is what the IMMUTABLE label then asserts.
-- The search layer's tsvector will need exactly this wrapper.
CREATE OR REPLACE FUNCTION imm_unaccent(text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
$$ SELECT unaccent('public.unaccent'::regdictionary, $1) $$;

-- make_norm — the join key between a dirty census spelling and a canonical marque.
-- Everything that is not a letter or a digit is discarded, so 'Mercedes-Benz',
-- 'MERCEDES_BENZ', 'Mercedes Benz' and 'mercedesbenz' all collapse onto one key.
-- Two HTML artefacts are decoded FIRST, because stripping them blind would corrupt
-- the name rather than clean it: '&amp;' would leave LYNKAMPCO instead of LYNKCO,
-- and the numeric en-dash '&#8211;' (seen in ~42 rows) would leave a literal 8211
-- embedded in the key.
CREATE OR REPLACE FUNCTION make_norm(text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
$$
  SELECT upper(regexp_replace(
           imm_unaccent(
             replace(
               regexp_replace(lower($1), '&#821[12];|&ndash;|&mdash;', '-', 'g'),
               '&amp;', '&')),
           '[^a-zA-Z0-9]', '', 'g'))
$$;

CREATE TABLE IF NOT EXISTS make_canon (
    slug            text PRIMARY KEY,          -- ascii-lowercase, url-safe: 'mercedes-benz'
    norm_key        text        NOT NULL,      -- make_norm(display_name): 'MERCEDESBENZ'
    display_name    text        NOT NULL,      -- with real diacritics: 'Citroën', 'Škoda'
    country_iso     char(2),
    legal_group     text,                      -- 'Stellantis', 'VW AG', 'Geely', 'Chery'
    vehicle_class   text        NOT NULL DEFAULT 'car',
    status          text        NOT NULL DEFAULT 'active',
    successor_slug  text        REFERENCES make_canon(slug),  -- ssangyong -> kgm
    is_listable     boolean     NOT NULL DEFAULT true,        -- false = searchable tail, never a logo tile
    logo_asset      text,                      -- filename under web public/logos
    logo_ar         numeric(6,3),              -- measured aspect ratio, drives optical-area scaling
    logo_variant    text,                      -- 'emblem' | 'wordmark' | 'lockup'
    logo_source_url text,                      -- provenance is mandatory for a shipped trademark
    logo_license    text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT make_canon_class_check CHECK (
        vehicle_class = ANY (ARRAY['car','van','truck','motorcycle','motorhome','other'])),
    CONSTRAINT make_canon_status_check CHECK (
        status = ANY (ARRAY['active','defunct','rebranded'])),
    CONSTRAINT make_canon_logo_variant_check CHECK (
        logo_variant IS NULL OR logo_variant = ANY (ARRAY['emblem','wordmark','lockup']))
);

CREATE UNIQUE INDEX IF NOT EXISTS make_canon_norm_key ON make_canon (norm_key);

-- make_alias — every spelling the census has ever produced, mapped onto a marque.
-- `kind` records WHY the mapping exists, which matters because the three kinds carry
-- different risk: an exact alias is a fact, a normalised one is mechanical, and a
-- model-as-make ('GOLF' typed into the brand field, 431 rows) is an inference that
-- also tells us the model. Those rows must be reassigned, never deleted — a listing
-- with make='GOLF' is a Volkswagen Golf, and dropping it loses a real car.
CREATE TABLE IF NOT EXISTS make_alias (
    alias_norm    text PRIMARY KEY,            -- make_norm(alias_raw)
    alias_raw     text NOT NULL,               -- the spelling as the census recorded it
    canon_slug    text NOT NULL REFERENCES make_canon(slug) ON DELETE CASCADE,
    kind          text NOT NULL,
    implied_model text,                        -- set only when kind = 'model_as_make'
    n_seen        integer NOT NULL DEFAULT 0,  -- rows carrying this spelling at curation time
    created_at    timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT make_alias_kind_check CHECK (
        kind = ANY (ARRAY['exact','normalized','model_as_make'])),
    CONSTRAINT make_alias_implied_model_check CHECK (
        implied_model IS NULL OR kind = 'model_as_make')
);

CREATE INDEX IF NOT EXISTS idx_make_alias_canon ON make_alias (canon_slug);

-- Rollback:
--   DROP INDEX IF EXISTS idx_make_alias_canon;
--   DROP TABLE IF EXISTS make_alias;
--   DROP INDEX IF EXISTS make_canon_norm_key;
--   DROP TABLE IF EXISTS make_canon;
--   DROP FUNCTION IF EXISTS make_norm(text);
--   DROP FUNCTION IF EXISTS imm_unaccent(text);
