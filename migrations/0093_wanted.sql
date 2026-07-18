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
--   geo_province_adjacency — static geo data for the §4.4 "geo" match component. Populated below
--                            with REAL province-to-province land borders, verified by TWO
--                            independent paths (carta §5.2 requirement):
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

INSERT INTO geo_province_adjacency (country_code, province_code, adjacent_province_code) VALUES
    ('ES', '01', '09'), ('ES', '09', '01'),
    ('ES', '01', '20'), ('ES', '20', '01'),
    ('ES', '01', '26'), ('ES', '26', '01'),
    ('ES', '01', '31'), ('ES', '31', '01'),
    ('ES', '01', '48'), ('ES', '48', '01'),
    ('ES', '02', '03'), ('ES', '03', '02'),
    ('ES', '02', '13'), ('ES', '13', '02'),
    ('ES', '02', '16'), ('ES', '16', '02'),
    ('ES', '02', '18'), ('ES', '18', '02'),
    ('ES', '02', '23'), ('ES', '23', '02'),
    ('ES', '02', '46'), ('ES', '46', '02'),
    ('ES', '03', '46'), ('ES', '46', '03'),
    ('ES', '04', '18'), ('ES', '18', '04'),
    ('ES', '04', '30'), ('ES', '30', '04'),
    ('ES', '05', '10'), ('ES', '10', '05'),
    ('ES', '05', '28'), ('ES', '28', '05'),
    ('ES', '05', '37'), ('ES', '37', '05'),
    ('ES', '05', '40'), ('ES', '40', '05'),
    ('ES', '05', '45'), ('ES', '45', '05'),
    ('ES', '05', '47'), ('ES', '47', '05'),
    ('ES', '06', '10'), ('ES', '10', '06'),
    ('ES', '06', '13'), ('ES', '13', '06'),
    ('ES', '06', '14'), ('ES', '14', '06'),
    ('ES', '06', '21'), ('ES', '21', '06'),
    ('ES', '06', '41'), ('ES', '41', '06'),
    ('ES', '06', '45'), ('ES', '45', '06'),
    ('ES', '08', '25'), ('ES', '25', '08'),
    ('ES', '08', '43'), ('ES', '43', '08'),
    ('ES', '09', '26'), ('ES', '26', '09'),
    ('ES', '09', '34'), ('ES', '34', '09'),
    ('ES', '09', '40'), ('ES', '40', '09'),
    ('ES', '09', '42'), ('ES', '42', '09'),
    ('ES', '09', '47'), ('ES', '47', '09'),
    ('ES', '09', '48'), ('ES', '48', '09'),
    ('ES', '10', '37'), ('ES', '37', '10'),
    ('ES', '10', '45'), ('ES', '45', '10'),
    ('ES', '11', '21'), ('ES', '21', '11'),
    ('ES', '11', '41'), ('ES', '41', '11'),
    ('ES', '12', '43'), ('ES', '43', '12'),
    ('ES', '12', '44'), ('ES', '44', '12'),
    ('ES', '12', '46'), ('ES', '46', '12'),
    ('ES', '13', '14'), ('ES', '14', '13'),
    ('ES', '13', '16'), ('ES', '16', '13'),
    ('ES', '13', '23'), ('ES', '23', '13'),
    ('ES', '13', '45'), ('ES', '45', '13'),
    ('ES', '14', '18'), ('ES', '18', '14'),
    ('ES', '14', '41'), ('ES', '41', '14'),
    ('ES', '15', '27'), ('ES', '27', '15'),
    ('ES', '15', '36'), ('ES', '36', '15'),
    ('ES', '16', '19'), ('ES', '19', '16'),
    ('ES', '16', '28'), ('ES', '28', '16'),
    ('ES', '16', '44'), ('ES', '44', '16'),
    ('ES', '16', '45'), ('ES', '45', '16'),
    ('ES', '16', '46'), ('ES', '46', '16'),
    ('ES', '17', '08'), ('ES', '08', '17'),
    ('ES', '17', '25'), ('ES', '25', '17'),
    ('ES', '19', '28'), ('ES', '28', '19'),
    ('ES', '19', '40'), ('ES', '40', '19'),
    ('ES', '19', '42'), ('ES', '42', '19'),
    ('ES', '19', '44'), ('ES', '44', '19'),
    ('ES', '19', '50'), ('ES', '50', '19'),
    ('ES', '20', '31'), ('ES', '31', '20'),
    ('ES', '20', '48'), ('ES', '48', '20'),
    ('ES', '21', '41'), ('ES', '41', '21'),
    ('ES', '22', '25'), ('ES', '25', '22'),
    ('ES', '22', '31'), ('ES', '31', '22'),
    ('ES', '22', '50'), ('ES', '50', '22'),
    ('ES', '23', '14'), ('ES', '14', '23'),
    ('ES', '23', '18'), ('ES', '18', '23'),
    ('ES', '24', '27'), ('ES', '27', '24'),
    ('ES', '24', '34'), ('ES', '34', '24'),
    ('ES', '24', '47'), ('ES', '47', '24'),
    ('ES', '24', '49'), ('ES', '49', '24'),
    ('ES', '25', '43'), ('ES', '43', '25'),
    ('ES', '25', '50'), ('ES', '50', '25'),
    ('ES', '26', '31'), ('ES', '31', '26'),
    ('ES', '26', '42'), ('ES', '42', '26'),
    ('ES', '26', '50'), ('ES', '50', '26'),
    ('ES', '28', '40'), ('ES', '40', '28'),
    ('ES', '28', '45'), ('ES', '45', '28'),
    ('ES', '29', '11'), ('ES', '11', '29'),
    ('ES', '29', '14'), ('ES', '14', '29'),
    ('ES', '29', '18'), ('ES', '18', '29'),
    ('ES', '29', '41'), ('ES', '41', '29'),
    ('ES', '30', '02'), ('ES', '02', '30'),
    ('ES', '30', '03'), ('ES', '03', '30'),
    ('ES', '30', '18'), ('ES', '18', '30'),
    ('ES', '31', '50'), ('ES', '50', '31'),
    ('ES', '32', '24'), ('ES', '24', '32'),
    ('ES', '32', '27'), ('ES', '27', '32'),
    ('ES', '32', '49'), ('ES', '49', '32'),
    ('ES', '33', '24'), ('ES', '24', '33'),
    ('ES', '33', '27'), ('ES', '27', '33'),
    ('ES', '33', '39'), ('ES', '39', '33'),
    ('ES', '34', '47'), ('ES', '47', '34'),
    ('ES', '36', '27'), ('ES', '27', '36'),
    ('ES', '36', '32'), ('ES', '32', '36'),
    ('ES', '37', '47'), ('ES', '47', '37'),
    ('ES', '37', '49'), ('ES', '49', '37'),
    ('ES', '39', '09'), ('ES', '09', '39'),
    ('ES', '39', '24'), ('ES', '24', '39'),
    ('ES', '39', '34'), ('ES', '34', '39'),
    ('ES', '39', '48'), ('ES', '48', '39'),
    ('ES', '40', '47'), ('ES', '47', '40'),
    ('ES', '42', '40'), ('ES', '40', '42'),
    ('ES', '42', '50'), ('ES', '50', '42'),
    ('ES', '43', '44'), ('ES', '44', '43'),
    ('ES', '43', '50'), ('ES', '50', '43'),
    ('ES', '44', '46'), ('ES', '46', '44'),
    ('ES', '44', '50'), ('ES', '50', '44'),
    ('ES', '47', '49'), ('ES', '49', '47')
ON CONFLICT DO NOTHING;

-- Rollback:
-- DROP TABLE IF EXISTS geo_province_adjacency;
-- DROP TABLE IF EXISTS dealer_review;
-- DROP TABLE IF EXISTS wanted_match;
-- DROP TABLE IF EXISTS wanted_listing;
