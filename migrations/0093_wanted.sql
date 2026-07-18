-- 0093_wanted.sql — 08-forum-community F2: the "Se busca" board (PRIORITY 1 of the pilar,
-- plans/cardeep-omni/08-forum-community.md §3/§4.4/§5.2/§6.1).
--
-- The pilar's own research (carta §2.4/§2.6) names ONE real moat: matching a buyer's demand
-- in near-real-time against the ENTIRE cross-platform census (`vehicle`/`vehicle_event`),
-- something none of the 17 studied references do (AutoTrader alerts batch/once-a-day on its
-- own inventory; CarWow matches only its closed dealer pool; eBay "Want It Now" died for lack
-- of an automatic matcher; Craigslist's "wanted" is unmatched text). This migration opens the
-- schema for that matcher. Auth prerequisite (carta F1) is ALREADY SATISFIED by AUTH-0
-- (migrations/0073_auth.sql: app_user/dealer_membership/user_session/user_notification) —
-- this migration mints NO second user/session schema (00-MASTER.md "Reglas operativas" #4).
--
-- Four tables:
--   wanted_listing        — the structured request (carta §4.4: "la petición ES el filtro",
--                            no free-text-required form, patrón AutoModerator §2.5).
--   wanted_match          — one row per (wanted_listing, vehicle) pairing with its match_score,
--                            notified_at (>=70 threshold) and clicked_at (feeds the dealer_review
--                            gate below AND the match_liveness_rate KPI, carta §4.10).
--   dealer_review         — post-match valoración of the dealer. FK to wanted_match is NOT NULL
--                            BY CONSTRAINT (carta §4.6: "sin match probado no hay fila posible —
--                            constraint, no convención"), 4 named axes (OfferUp pattern, carta
--                            §2.3 exact), double-blind reveal fields (Airbnb pattern, carta §2.3
--                            exact, REVIEW_REVEAL_DAYS=14 lives in pipeline/wanted/matcher.py).
--   geo_province_adjacency — static geo data (schema only, see NOTE below) for the §4.4 "geo"
--                            match component: REAL province-to-province land borders, verified
--                            by TWO independent paths (carta §5.2 requirement):
--                              (1) cartographic: computed from a real IGN-derived province-
--                                  boundary polygon dataset (codeforgermany/click_that_hood,
--                                  spain-provinces.geojson, cod_prov = the same INE 2-digit code
--                                  as geo_province.code) via shapely polygon-touch detection,
--                                  STABLE across buffer tolerances from 0 to 550m (111 pairs,
--                                  unchanged) — a pair that only appears at a >=1km buffer
--                                  (Cáceres–Ciudad Real, tested at 1.1km) was excluded as a
--                                  near-tripoint artifact, not a real shared border.
--                              (2) graph consistency: sum of per-province degrees = 222 =
--                                  2 x 111 pairs (every edge counted from both ends).
--                            Manually cross-checked against well-known Spanish geography for
--                            Madrid (5 neighbours: Ávila/Cuenca/Guadalajara/Segovia/Toledo),
--                            Zaragoza (8), Cuenca (7) and Toledo (6) — all match. The 5 island/
--                            exclave provinces (Balears, Las Palmas, Santa Cruz de Tenerife,
--                            Ceuta, Melilla) correctly resolve to ZERO land neighbours.
--
-- NOTE (2026-07-19, real CI bug fixed at the root): the 222-row INSERT that used to live here
-- broke `migrate up` on any empty database — its FK into geo_province (populated only by
-- scripts/load_geo.py, never by a migration) violates on a fresh DB with no seed step, which is
-- exactly what the country-proof-invariant and bring-up-smoke CI jobs run (deliberately: see
-- .github/workflows/ci.yml's "DO NOT add a census/geo seed step" comment on that job — those
-- goldens self-seed inside rolled-back transactions and MUST NOT see prior seed data). The DATA
-- now lives in scripts/load_geo_adjacency.py (idempotent, ON CONFLICT DO NOTHING, same pattern as
-- load_geo.py), run from CI's "Seed geo backbone" step alongside load_geo/seed_geo_centroides.
-- This migration keeps only the DDL (CREATE TABLE + FKs), which is schema and belongs here.
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section (strip_rollback).

-- ---------------------------------------------------------------------------
-- wanted_listing
-- ---------------------------------------------------------------------------

-- NOTE (live-schema correction, verified against pg_constraint on cardeep-pg before writing this
-- migration — same class of bug 01-market-intelligence F4 already hit once): geo_province's real
-- PRIMARY KEY is the COMPOSITE (country_code, code) added by migrations/0052+0059, not the single
-- `code` column that 0001_geo.sql's original comment describes. Every FK into geo_province in this
-- migration is therefore the composite (country_code, code) form, matching entity/geo_comarca's
-- own FKs (0059_geo_code_width.sql §4) — country_code carried explicitly (default 'ES') rather than
-- hardcoded away, per the program's ES-only-today-but-country-parametrized convention (auth.py's
-- _primary_tenant_cdp docstring states the same rule for this exact reason).

CREATE TABLE IF NOT EXISTS wanted_listing (
    wanted_ulid     TEXT PRIMARY KEY,
    user_ulid       TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    country_code    CHAR(2) NOT NULL DEFAULT 'ES',
    make            TEXT NOT NULL,
    model           TEXT,                          -- nullable = "any model of this make" (carta
                                                     -- form lists it as a field; a wildcard on an
                                                     -- optional field is a product decision, not a
                                                     -- fuzzy match — make_model scoring still exact)
    year_min        INT,
    year_max        INT,
    km_max          INT,
    price_max       NUMERIC(12,2),
    fuel            TEXT,
    transmission    TEXT,
    province_code   VARCHAR(8) NOT NULL,
    free_text       TEXT,
    ttl_days        INT NOT NULL CHECK (ttl_days IN (7, 14, 30, 60)),
    status          TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'matched', 'closed', 'expired')),
    closed_reason   TEXT
        CHECK (closed_reason IN ('bought_via_cardeep', 'bought_elsewhere', 'no_longer_interested')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL,
    CHECK (year_min IS NULL OR year_max IS NULL OR year_min <= year_max),
    FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code)
);

CREATE INDEX IF NOT EXISTS idx_wanted_listing_user ON wanted_listing (user_ulid);
CREATE INDEX IF NOT EXISTS idx_wanted_listing_open
    ON wanted_listing (make, status) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_wanted_listing_province ON wanted_listing (country_code, province_code);
CREATE INDEX IF NOT EXISTS idx_wanted_listing_expires
    ON wanted_listing (expires_at) WHERE status = 'open';

-- ---------------------------------------------------------------------------
-- wanted_match
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS wanted_match (
    wanted_match_ulid TEXT PRIMARY KEY,
    wanted_ulid       TEXT NOT NULL REFERENCES wanted_listing(wanted_ulid) ON DELETE CASCADE,
    vehicle_ulid      TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    match_score       NUMERIC(5,2) NOT NULL CHECK (match_score >= 0 AND match_score <= 100),
    matched_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at       TIMESTAMPTZ,
    clicked_at        TIMESTAMPTZ,
    UNIQUE (wanted_ulid, vehicle_ulid)
);

CREATE INDEX IF NOT EXISTS idx_wanted_match_wanted ON wanted_match (wanted_ulid, match_score DESC);
CREATE INDEX IF NOT EXISTS idx_wanted_match_vehicle ON wanted_match (vehicle_ulid);
-- KPI §4.10 (match_liveness_rate) and the "coincidencias servidas 7d" hero number (§4.9c)
-- both scan by notified_at over a rolling window.
CREATE INDEX IF NOT EXISTS idx_wanted_match_notified ON wanted_match (notified_at) WHERE notified_at IS NOT NULL;

-- ---------------------------------------------------------------------------
-- dealer_review — gate transaccional (eBay §2.3) + double-blind (Airbnb §2.3)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dealer_review (
    review_ulid       TEXT PRIMARY KEY,
    -- NOT NULL, no ON DELETE SET NULL: a review literally cannot exist without its enabling
    -- match — this IS the "constraint, not convention" the carta demands (§4.6).
    wanted_match_ulid TEXT NOT NULL REFERENCES wanted_match(wanted_match_ulid) ON DELETE CASCADE,
    reviewer_user_ulid TEXT NOT NULL REFERENCES app_user(user_ulid) ON DELETE CASCADE,
    entity_ulid       TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    -- carta §4.6: "el dealer, SI es usuario de la plataforma, contra-valora" — the reciprocal
    -- direction reuses this same table (reviewer_role='dealer') rather than a second schema.
    reviewer_role     TEXT NOT NULL DEFAULT 'buyer' CHECK (reviewer_role IN ('buyer', 'dealer')),
    axis_trato              SMALLINT NOT NULL CHECK (axis_trato BETWEEN 1 AND 5),
    axis_anuncio_veraz       SMALLINT NOT NULL CHECK (axis_anuncio_veraz BETWEEN 1 AND 5),
    axis_disponibilidad_real SMALLINT NOT NULL CHECK (axis_disponibilidad_real BETWEEN 1 AND 5),
    axis_agilidad            SMALLINT NOT NULL CHECK (axis_agilidad BETWEEN 1 AND 5),
    overall           SMALLINT NOT NULL CHECK (overall BETWEEN 1 AND 5),
    comment           TEXT,
    submitted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- NULL until BOTH sides have submitted OR REVIEW_REVEAL_DAYS (14, Airbnb-exact) elapses,
    -- whichever first (pipeline/wanted/matcher.py::reveal_eligible). Immutable once set — the
    -- API contract test (tests/test_wanted_router.py) asserts no revealed_at IS NULL row is
    -- ever served (carta §7.7 invariant).
    revealed_at       TIMESTAMPTZ,
    UNIQUE (wanted_match_ulid, reviewer_role)
);

CREATE INDEX IF NOT EXISTS idx_dealer_review_entity
    ON dealer_review (entity_ulid) WHERE revealed_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_dealer_review_match ON dealer_review (wanted_match_ulid);

-- ---------------------------------------------------------------------------
-- geo_province_adjacency — static, real, dual-verified (see header)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS geo_province_adjacency (
    country_code           CHAR(2) NOT NULL DEFAULT 'ES',
    province_code          VARCHAR(8) NOT NULL,
    adjacent_province_code VARCHAR(8) NOT NULL,
    PRIMARY KEY (country_code, province_code, adjacent_province_code),
    CHECK (province_code <> adjacent_province_code),
    FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code),
    FOREIGN KEY (country_code, adjacent_province_code) REFERENCES geo_province (country_code, code)
);

-- Data (222 rows / 111 real land-border pairs) moved to scripts/load_geo_adjacency.py — see
-- NOTE above. Run: python -m scripts.load_geo_adjacency

-- Rollback:
-- DROP TABLE IF EXISTS geo_province_adjacency;
-- DROP TABLE IF EXISTS dealer_review;
-- DROP TABLE IF EXISTS wanted_match;
-- DROP TABLE IF EXISTS wanted_listing;
