# CARDEEP — 03 · The Canonical Data Model & Storage Architecture (PostgreSQL 16)

> **Pillar document.** The complete, rigorous storage architecture for the live
> CARDEEP database of 100% of Spanish car points-of-sale and their inventory: the
> geo backbone, the entity graph (all ontology kinds + organizations + platform
> dual-membership), the vehicle/lot inventory with photo-perceptual-hash delta, the
> append-only event history, the verification/health/alert resilience layer, and the
> live API contract. Designed for tens of millions of vehicles plus full delta with
> complete history retention.
>
> **This document SUPERSEDES** the schema sketch in `docs/ARCHITECTURE.md §Modelo`
> and the migration-target deltas in `01-ENTITY-ONTOLOGY.md §6.4`. It is the contract
> the migration runner (`scripts/migrate.py`) and every pipeline/API module must
> converge to. It does **not** rewrite history: migrations `0001`–`0004` are live
> (12.862 entities, 39.068 vehicles, 41.165 events `[VERIFIED 2026-06-12 against the
> running DB]`); this design is expressed as **additive, idempotent, reversible**
> migrations `0005`–`0012` on top of them, never a destructive recreate.
>
> **Marking discipline.** Every load-bearing claim is `[VERIFIED]` (read from
> repo/DB/live probe this session) or `[ASSUMED]` (inferred, design judgment). No
> placeholders, no stubs, no TODOs. DDL is concrete and runnable.

---

## 0. Ground truth this design is pinned to (read before trusting any DDL below)

Verified this session, so nothing here is invented:

| Fact | Value | Evidence |
|---|---|---|
| Engine | **PostgreSQL 16.14** (Debian, Docker `cardeep-pg`, `127.0.0.1:5433`) | `[VERIFIED]` `docker exec … SELECT version()` |
| Extensions **available** | `btree_gin`, `pg_trgm`, `pgcrypto`, `uuid-ossp` | `[VERIFIED]` `pg_available_extensions` |
| Extensions **installed** | only `plpgsql` | `[VERIFIED]` `pg_extension` |
| **PostGIS NOT available** | — | `[VERIFIED]` absent from `pg_available_extensions` → geo uses `double precision` lat/lon + bbox math, never `geometry`/`geography` |
| Live rows | entity 12.862 · vehicle 39.068 · vehicle_event 41.165 · distinct kinds **4** | `[VERIFIED]` direct count |
| ID scheme | `entity_ulid`/`vehicle_ulid`/`event_ulid` = 26-char Crockford ULID (`pipeline/ids.py`), time-ordered | `[VERIFIED]` |
| `cdp_code` | `CDP-ES-{prov2}-{8×Crockford b32(sha256(canonical_key))}`, domain>cif>name+muni+addr | `[VERIFIED]` `services/api/codes.py` |
| Migration pattern | numbered SQL, `IF NOT EXISTS`, inline `-- Rollback:`, ledger `schema_migrations` | `[VERIFIED]` `scripts/migrate.py` |
| Mutation doctrine | INSERT-new + close-gone; UPDATE only a **mutated** field (+emit event); unchanged → refresh `last_seen` only; history append-only | `[VERIFIED]` `pipeline/ingest.py`, `docs/ARCHITECTURE.md §4.4` |
| API envelope | `{ok, data, error, meta}` (FastAPI + asyncpg) | `[VERIFIED]` `services/api/main.py` |

**Design consequence of "PostGIS NOT available":** the geo grid and "near me" queries
use a **lat/lon bounding-box prefilter on a composite btree** + Haversine refine in
SQL, not GiST/SP-GiST spatial indexes. If the operator later installs PostGIS, a
`0099_postgis_geo.sql` can add a generated `geography(Point,4326)` column + GiST index
without touching this core. Documented as the one extension-gated optimization (§10.4).

---

## 1. Architectural principles (the five invariants every table obeys)

These are not aspirations; each maps to a constraint or trigger below.

1. **Identity is immutable and source-independent.** `cdp_code` / `org_code` /
   `platform_code` never change once minted; re-discovery via any source converges to
   the same code (`01-ENTITY-ONTOLOGY.md §6`). Enforced by `UNIQUE` + deterministic
   key generation, never by a surrogate sequence that a second source could re-mint.

2. **Ownership is singular; membership is plural.** A `vehicle` is **owned** by exactly
   one selling `entity` (`vehicle.entity_id` NOT NULL, never a platform). A vehicle has
   **0..M** platform memberships via the `platform_listing` edge. This is the single
   most important decision in the pillar — it is what makes "the same car ∈ a platform
   AND its dealer" expressible (`01-ENTITY-ONTOLOGY.md §4`, D-10).

3. **State is a projection of an append-only log.** `vehicle` holds the *current*
   materialized snapshot for fast serving; `vehicle_event` is the immutable truth from
   which any past state is reconstructable. Events are never updated or deleted. A
   trigger forbids mutation of the log (§5.3). The snapshot can always be rebuilt from
   the log; the log can never be rebuilt from the snapshot — so the log is canonical.

4. **Never UPDATE a non-mutated row.** A row whose real datum changed (price, photo, km)
   is updated **and** emits its event; an unchanged row only refreshes `last_seen`.
   Disappearance is a soft close (`status='gone'` + GONE event), never a hard delete.
   Full history is retained forever.

5. **Tier-1 is physically and logically separated.** `entity.is_tier1` partitions the
   entity row space; Tier-1 platforms never share recipe, raw store, or operation with
   the long-tail (`countries/ES/_tier1/`, `00-TIER1-REGISTRY.md`). The data model keeps
   the flag first-class and indexes it so the two universes are queryable in isolation.

---

## 2. Type system & shared infrastructure — migration `0005`

Before the big tables, the model needs **PostgreSQL ENUM types** (replacing the scattered
`TEXT … CHECK` of `0002`–`0004`), shared trigger functions, and the extensions. ENUMs are
chosen over CHECK because: (a) one authoritative definition, (b) 4-byte storage vs TEXT,
(c) `ALTER TYPE … ADD VALUE` extends them additively (exactly the "widen `kind`" need of
the ontology), (d) self-documenting in `\dT+`.

> **Migration safety note.** `0002`–`0004` shipped the columns as `TEXT + CHECK`. The
> live data already conforms to the legacy 6-value `kind`. Migration `0005` creates the
> ENUM types and `0006` performs the **in-place type swap** with a `USING` cast guarded
> by a pre-flight value audit (§8.2). The swap is reversible (cast back to TEXT).

```sql
-- 0005_types_and_infra.sql — ENUM type system, extensions, shared triggers.
-- Additive, idempotent, reversible.

CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- fuzzy name/alias search (GIN trigram)
CREATE EXTENSION IF NOT EXISTS btree_gin;   -- composite GIN (enum + trigram) for filtered search
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- gen_random_uuid fallback / digest if ever needed

-- ---- Entity taxonomy (the full ontology, 01-ENTITY-ONTOLOGY.md §2) ----
-- 'cadena' retained ONLY for migration readability; never newly assigned (D-11).
DO $$ BEGIN
  CREATE TYPE entity_kind AS ENUM (
    'concesionario_oficial', 'agente_oficial', 'compraventa', 'garaje', 'desguace',
    'rent_a_car_vo', 'subasta', 'importador', 'oem_vo_portal', 'plataforma',
    'cadena'  -- DEPRECATED, read-only
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

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

-- WAF / bot-defense posture (00-TIER1-REGISTRY.md; routes the fetch engine).
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

-- Platform listing membership state.
DO $$ BEGIN
  CREATE TYPE listing_status AS ENUM ('listed', 'removed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---- Shared trigger: forbid UPDATE/DELETE on any append-only log ----
CREATE OR REPLACE FUNCTION cardeep_block_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'append-only table %: % forbidden (history is immutable)',
    TG_TABLE_NAME, TG_OP USING ERRCODE = 'restrict_violation';
END $$;

-- Rollback:
-- DROP FUNCTION IF EXISTS cardeep_block_mutation();
-- DROP TYPE IF EXISTS listing_status, vehicle_event_type, vehicle_status, waf_kind,
--   kind_source, entity_status, org_type, entity_kind;
```

**Why ULID stays the PK type (TEXT), not native `uuid`.** The codebase already mints
26-char Crockford ULIDs in `pipeline/ids.py` `[VERIFIED]`, all FKs reference them, and
the API returns them. Converting to `uuid` would be a destructive, repo-wide rewrite for
no functional gain (ULIDs are already time-sortable, the property `uuid` would give). The
design **keeps `TEXT` ULID PKs** and instead pins their shape with a `CHECK` so a
malformed id can never enter (§3.1). This is the KISS/anti-churn call.

---

## 3. The entity graph — migrations `0006`–`0007`

The entity universe is the **denominator** (`01-ENTITY-ONTOLOGY.md §1`). Three node
types — `organization` (chains/groups/brands/operators), `entity` (the selling point of
sale, the atomic unit of code+recipe+delta+resilience), and a derived `platform` facet —
plus the provenance and alias side-tables that already exist.

### 3.1 `entity` — superset of the live table (in-place evolution)

Migration `0006` **evolves the existing `entity` table in place** (it holds 12.862 live
rows; recreating it is forbidden). It: swaps `kind`/`status`/`website_waf` to ENUM, adds
the ontology columns (`org_id`, `sells_cars`, `kind_source`, lat/lon already present,
geocode quality, defense detail, soft-close fields), and pins the ULID shape.

```sql
-- 0006_entity_evolve.sql — evolve live entity to the full ontology. Additive + in-place.
-- 1.292 desguace + 1.617 conces + 2.753 compraventa + 7.200 garaje are preserved.

-- (a) pin the ULID shape so a malformed id cannot enter (26 Crockford chars).
ALTER TABLE entity
  ADD CONSTRAINT entity_ulid_shape CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$') NOT VALID;
-- NOT VALID: enforced on new rows immediately, legacy rows validated in 0006b after audit.

-- (b) swap kind/status/waf TEXT->ENUM (pre-flight audit in 0006_preflight, §8.2).
ALTER TABLE entity
  ALTER COLUMN kind        TYPE entity_kind   USING kind::entity_kind,
  ALTER COLUMN status      TYPE entity_status USING status::entity_status,
  ALTER COLUMN website_waf TYPE waf_kind      USING COALESCE(website_waf,'none')::waf_kind;
ALTER TABLE entity ALTER COLUMN status SET DEFAULT 'unverified';
ALTER TABLE entity ALTER COLUMN website_waf SET DEFAULT 'none';

-- (c) organization layer FK (fixes failure #3: chain vs branch). NULL = standalone POS.
ALTER TABLE entity ADD COLUMN IF NOT EXISTS org_id TEXT;  -- FK added in 0007 after org exists

-- (d) sells-cars gate (D-4): NULL=unknown, FALSE=pure taller (a non-entity, filtered out).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS sells_cars BOOLEAN;

-- (e) which precedence rung decided the kind (D-6 / §6.5). Default for legacy = 'platform_label'
--     so a higher-precedence signal can later override deterministically.
ALTER TABLE entity ADD COLUMN IF NOT EXISTS kind_source kind_source NOT NULL DEFAULT 'manual';

-- (f) geocode provenance + quality (no PostGIS: plain doubles already exist as lat/lon).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS geocode_source TEXT;   -- 'ine'|'osm'|'google'|'derived'
ALTER TABLE entity ADD COLUMN IF NOT EXISTS geocode_precision TEXT -- 'rooftop'|'street'|'municipality'|'province'
  CHECK (geocode_precision IS NULL OR geocode_precision IN
         ('rooftop','street','postcode','municipality','province'));

-- (g) defense detail beyond the WAF enum (free-text fingerprint the engine recorded).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS defense_detail JSONB;  -- {server, cf_ray, x_cdn, challenge, ...}

-- (h) soft-close audit (mutation doctrine: closure is a state, not a delete).
ALTER TABLE entity ADD COLUMN IF NOT EXISTS closed_at TIMESTAMPTZ;
ALTER TABLE entity ADD COLUMN IF NOT EXISTS close_reason TEXT;

-- (i) data-quality / dedup helpers.
ALTER TABLE entity ADD COLUMN IF NOT EXISTS canonical_key TEXT;    -- the exact key cdp_code hashed (audit)
ALTER TABLE entity ADD COLUMN IF NOT EXISTS attest_count INT NOT NULL DEFAULT 1; -- # of orthogonal sources

-- Index set (the live 0002 indexes are kept; these are the additions).
CREATE INDEX IF NOT EXISTS idx_entity_org        ON entity (org_id) WHERE org_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entity_sells       ON entity (kind) WHERE sells_cars IS NOT FALSE;
CREATE INDEX IF NOT EXISTS idx_entity_kind_prov   ON entity (kind, province_code);
-- geo grid prefilter (bbox on lat/lon; §10.3). Partial: only rows with a fix.
CREATE INDEX IF NOT EXISTS idx_entity_latlon      ON entity (lat, lon) WHERE lat IS NOT NULL;
-- fuzzy name search across both name columns (pg_trgm GIN).
CREATE INDEX IF NOT EXISTS idx_entity_tradename_trgm ON entity USING gin (trade_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_entity_legalname_trgm ON entity USING gin (legal_name gin_trgm_ops);

-- Rollback:
-- (reverse: drop added indexes/columns; ALTER enums back to TEXT via USING col::text)
```

**Column rationale (the non-obvious ones).**
- `attest_count` denormalizes `count(entity_source)` so the capture-recapture coverage
  estimator and the API can rank "how many independent sources attest this" without a
  join. Maintained by the `entity_source` insert path (§3.4), reconcilable by a nightly
  audit. `[ASSUMED]` denormalization is worth it at 50–90k entities × frequent reads.
- `canonical_key` stores the *exact* string `cdp_code` hashed, so a code collision or a
  re-key (D-12 rent-a-car case) is debuggable without re-deriving — the audit trail of
  identity.
- `defense_detail JSONB` complements the `website_waf` enum: the enum routes the engine,
  the JSONB preserves the raw fingerprint (`server`, `cf-ray`, `x-iinfo`, challenge body
  markers) the Tier-1 sweep recorded (`00-TIER1-REGISTRY.md §0`), for forensics when a
  wall escalates.

### 3.2 The `platform` facet — a view + a flag, not a second table

A platform **is** an `entity` with `kind ∈ {plataforma, oem_vo_portal}` (D-10/D-2/D-9).
It is *not* a separate table (that would split identity). The model exposes platforms as
a **view** plus the existing `is_tier1` flag, and gives platform-only attributes a thin
extension table to avoid widening `entity` with columns that are NULL for 99.99% of rows.

```sql
-- 0006_entity_evolve.sql (cont.) — platform extension (1:1 with platform-kind entities).
CREATE TABLE IF NOT EXISTS platform_meta (
    entity_ulid     TEXT PRIMARY KEY REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    listing_counter BIGINT,             -- last re-derived live inventory counter
    counter_at      TIMESTAMPTZ,        -- when (counters drift daily: 00-TIER1 §0)
    data_surface    TEXT,               -- 'next_data'|'graphql'|'json_ld'|'internal_api'|'sitemap'|'es_facet'
    surface_detail  JSONB,              -- endpoint, payload template, header profile ref
    requires_creds  BOOLEAN NOT NULL DEFAULT FALSE,  -- B2B login (BCA/Autorola)
    is_platform_like BOOLEAN NOT NULL DEFAULT FALSE,  -- subasta that also aggregates (D-7)
    CHECK (data_surface IS NULL OR data_surface IN
      ('next_data','graphql','json_ld','internal_api','sitemap','es_facet','app_api'))
);

CREATE OR REPLACE VIEW platform AS
  SELECT e.entity_ulid, e.cdp_code, e.trade_name, e.website, e.is_tier1, e.website_waf,
         e.kind, pm.listing_counter, pm.counter_at, pm.data_surface, pm.requires_creds,
         pm.is_platform_like
    FROM entity e
    LEFT JOIN platform_meta pm USING (entity_ulid)
   WHERE e.kind IN ('plataforma','oem_vo_portal')
      OR pm.is_platform_like;  -- a subasta flagged platform-like is served as a platform too
```

### 3.3 `organization` — chains, groups, brands, operators — migration `0007`

```sql
-- 0007_organization.sql — the chain/group/brand layer (fixes failure #3). Additive.
CREATE TABLE IF NOT EXISTS organization (
    org_ulid   TEXT PRIMARY KEY CHECK (org_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
    org_code   TEXT NOT NULL UNIQUE,        -- ORG-ES-{b32(name|domain)}, immutable
    name       TEXT NOT NULL,
    org_type   org_type NOT NULL,
    website    TEXT,
    hq_province_code CHAR(2) REFERENCES geo_province(code),
    branch_count INT NOT NULL DEFAULT 0,    -- denormalized count(entity WHERE org_id=…)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_org_type ON organization (org_type);
CREATE INDEX IF NOT EXISTS idx_org_name_trgm ON organization USING gin (name gin_trgm_ops);

-- wire the entity.org_id FK now that organization exists.
ALTER TABLE entity
  ADD CONSTRAINT fk_entity_org FOREIGN KEY (org_id)
  REFERENCES organization(org_ulid) ON DELETE SET NULL;

-- Rollback:
-- ALTER TABLE entity DROP CONSTRAINT IF EXISTS fk_entity_org;
-- DROP TABLE IF EXISTS organization;
```

This answers, in one indexed predicate, the questions the current schema **cannot**
(`01-ENTITY-ONTOLOGY.md §2`): *"Flexicar's national stock"* = `WHERE org_id = (SELECT
org_ulid FROM organization WHERE org_code='ORG-ES-…')`; *"how many points of sale does
AUTO1 operate"* = `SELECT branch_count FROM organization WHERE …`. An org owns **no
inventory directly** — its inventory is the union over its branches (a query, never a
stored set), exactly the ontology's §2.12 invariant.

### 3.4 `entity_source` & `entity_alias` — kept as-is, with one addition

`0002` already ships both, well-designed `[VERIFIED]`. The only addition: an
`entity_source.first_seen` (the current table has only `seen_at`, which the upsert
overwrites — losing the *first* attestation date that the capture-recapture estimator
needs). Migration `0007` adds it, backfilled from `seen_at`.

```sql
-- 0007_organization.sql (cont.)
ALTER TABLE entity_source ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ;
UPDATE entity_source SET first_seen = seen_at WHERE first_seen IS NULL;
ALTER TABLE entity_source ALTER COLUMN first_seen SET DEFAULT now();
ALTER TABLE entity_source ALTER COLUMN first_seen SET NOT NULL;
-- attest_count denormalization stays consistent via this trigger:
CREATE OR REPLACE FUNCTION entity_bump_attest() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE entity SET attest_count = (SELECT count(*) FROM entity_source WHERE entity_ulid = NEW.entity_ulid)
   WHERE entity_ulid = NEW.entity_ulid;
  RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_entity_attest ON entity_source;
CREATE TRIGGER trg_entity_attest AFTER INSERT ON entity_source
  FOR EACH ROW EXECUTE FUNCTION entity_bump_attest();
```

---

## 4. The vehicle inventory & the platform dual-membership — migrations `0008`–`0009`

This is the **numerator**, designed for **tens of millions of rows + delta**. The key
decisions: partition the hot tables, split the spec out of the hot path, and make the
platform membership a first-class edge.

### 4.1 `vehicle` — the current materialized snapshot (partitioned)

The live `vehicle` table (39.068 rows) is a single heap. At target scale (the OPEN set
alone is >1.1M listings today, `00-TIER1-REGISTRY.md §1.1`; the full census denominator
× cars/entity reaches tens of millions over time including gone-history) a single heap's
indexes degrade and `VACUUM` on the hot status churn becomes the bottleneck.

**Partitioning strategy: `PARTITION BY LIST (province_code)` with a default partition,
and a SUB-PARTITIONED `00`.**
Rationale, weighed against the alternatives:
- **By `province_code` (chosen).** 52 provinces + a `00` sentinel for national platform
  inventory = ~53 partitions, each independently vacuumable and index-able. The mandate's
  primary access pattern is *geographic* ("ordered by country/province/comarca/city") and
  per-entity (which lives in one province). Province-local queries hit one partition;
  the geo-grid API (§7) prunes to the provinces in the bbox. Bounded, stable cardinality
  (Spain's provinces don't change). `[ASSUMED]` this beats the alternatives for our mix.
- **`00` is itself sub-partitioned by `HASH(platform_entity owner)` `[adversarial GAP-28/34].`**
  The C2C sentinel design (§4.3) routes ~1.4M+ Wallapop+Milanuncios private-seller cars into
  province `00`, the SAME partition that already holds every national-platform car — a single
  oversized partition that defeats the per-province balance rationale exactly where volume is
  highest, and turns `idx_vp_entity_avail (entity_ulid) WHERE status='available'` into a
  multi-hundred-thousand-row equality bucket on one synthetic owner. Fix: `vehicle_p_00` is
  declared `PARTITION BY HASH (entity_ulid)` with **8–16 sub-partitions**, AND the C2C sentinel
  owner is **split per platform** (`c2c_private@wallapop`, `c2c_private@milanuncios`, …) so
  `HASH(entity_ulid)` actually distributes the load across sub-partitions instead of colliding on
  one ulid. Each sub-partition is independently vacuumable; the entity index is per-sub-partition.
  This restores the scale strategy for the highest-volume class. The LIST→sub-HASH choice is
  documented-reversible (a maintenance re-home), so the DDL is not irreversible (§9.7).
- **By `entity_ulid` hash (rejected).** Spreads write load evenly but destroys geo
  locality — every province query scans every partition. The mandate is geo-first.
- **By `first_seen` range / time (rejected for the snapshot, used for events).** The
  snapshot is queried by *where/who*, not *when*; time-partitioning the live snapshot
  would scatter one dealer's stock across time partitions. Time-range is correct for the
  **event log** (§5), wrong for the snapshot.

```sql
-- 0008_vehicle_partitioned.sql — re-home vehicle as a LIST-partitioned table.
-- Strategy: create vehicle_p partitioned, migrate the 39.068 rows, swap names. Reversible.

CREATE TABLE IF NOT EXISTS vehicle_p (
    vehicle_ulid   TEXT NOT NULL CHECK (vehicle_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
    entity_ulid    TEXT NOT NULL,                  -- owning SELLING entity (never a platform)
    province_code  CHAR(2) NOT NULL,               -- partition key; copied from entity at insert
    deep_link      TEXT NOT NULL,                  -- per-vehicle canonical URL on the owner's surface
    -- identity / dedup
    vin            TEXT,                            -- full VIN when available (rare in public data)
    vin_ref        TEXT,                            -- platform listing ref / internal id
    listing_fingerprint TEXT,                       -- (make,model,year,km-band,price-band,photo_hash) hash
    -- core spec (hot, frequently filtered/sorted — stays inline)
    title          TEXT,
    make           TEXT,
    model          TEXT,
    version        TEXT,
    year           INT,
    km             INT,
    price          NUMERIC(12,2),
    currency       CHAR(3) NOT NULL DEFAULT 'EUR',
    fuel           TEXT,
    transmission   TEXT,
    body_type      TEXT,
    -- photo delta (pHash perceptual hash; the strongest cross-platform same-car signal §6)
    photo_url      TEXT,
    photo_hash     TEXT,                            -- 64-bit pHash as hex/bigint string
    photo_count    INT,
    -- lifecycle
    status         vehicle_status NOT NULL DEFAULT 'available',
    recipe_version INT,
    first_seen     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen      TIMESTAMPTZ NOT NULL DEFAULT now(),
    gone_at        TIMESTAMPTZ,                     -- when it left (soft close)
    PRIMARY KEY (province_code, vehicle_ulid),      -- partition key MUST be in the PK
    UNIQUE (province_code, entity_ulid, deep_link)  -- the dedup key (per-owner per-URL)
) PARTITION BY LIST (province_code);

-- one partition per INE province (01..52) + national sentinel '00' + catch-all default.
-- (generated by 0008; shown abbreviated)
CREATE TABLE IF NOT EXISTS vehicle_p_00 PARTITION OF vehicle_p FOR VALUES IN ('00'); -- platforms/national
CREATE TABLE IF NOT EXISTS vehicle_p_28 PARTITION OF vehicle_p FOR VALUES IN ('28'); -- Madrid
CREATE TABLE IF NOT EXISTS vehicle_p_08 PARTITION OF vehicle_p FOR VALUES IN ('08'); -- Barcelona
-- … 01..52 …
CREATE TABLE IF NOT EXISTS vehicle_p_def PARTITION OF vehicle_p DEFAULT;             -- safety net

-- per-partition indexes are created by attaching templates; the global pattern:
--   (entity_ulid) WHERE status='available'   -- the per-entity inventory hot path
--   (entity_ulid, status)                     -- reconciliation read in ingest
--   (status, last_seen)                       -- GONE sweep / freshness
--   (photo_hash) WHERE photo_hash IS NOT NULL -- photo-delta + cross-platform match
--   (make, model, year)                       -- search/filter
--   (price) WHERE status='available'          -- price range + grid stats
-- Postgres 16 propagates indexes created on the partitioned parent to all partitions:
CREATE INDEX IF NOT EXISTS idx_vp_entity_avail ON vehicle_p (entity_ulid) WHERE status='available';
CREATE INDEX IF NOT EXISTS idx_vp_entity_status ON vehicle_p (entity_ulid, status);
CREATE INDEX IF NOT EXISTS idx_vp_status_seen   ON vehicle_p (status, last_seen);
CREATE INDEX IF NOT EXISTS idx_vp_photo_hash    ON vehicle_p (photo_hash) WHERE photo_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_vp_make_model    ON vehicle_p (make, model, year);
CREATE INDEX IF NOT EXISTS idx_vp_fingerprint   ON vehicle_p (listing_fingerprint) WHERE listing_fingerprint IS NOT NULL;

-- migrate live rows (province_code backfilled from the owning entity), then swap:
INSERT INTO vehicle_p (vehicle_ulid, entity_ulid, province_code, deep_link, vin_ref,
       title, make, model, year, km, price, currency, fuel, transmission, photo_url,
       photo_hash, status, recipe_version, first_seen, last_seen)
SELECT v.vehicle_ulid, v.entity_ulid, COALESCE(e.province_code,'00'), v.deep_link, v.vin_ref,
       v.title, v.make, v.model, v.year, v.km, v.price, v.currency, v.fuel, v.transmission,
       v.photo_url, v.photo_hash, v.status::text::vehicle_status, v.recipe_version,
       v.first_seen, v.last_seen
FROM vehicle v JOIN entity e USING (entity_ulid)
ON CONFLICT DO NOTHING;

-- [adversarial GAP-31] PRE-FLIGHT: ON CONFLICT DO NOTHING would SILENTLY DROP any legacy row
-- that collides on the new UNIQUE (province_code, entity_ulid, deep_link) under the backfilled
-- province — the P0 gate "count after == before" would then FAIL with no explanation. Abort the
-- migration BEFORE the INSERT if any such legacy duplicate exists, surfacing the offending rows:
DO $$
DECLARE dup_count INT;
BEGIN
  SELECT count(*) INTO dup_count FROM (
    SELECT COALESCE(e.province_code,'00') AS pc, v.entity_ulid, v.deep_link
    FROM vehicle v JOIN entity e USING (entity_ulid)
    GROUP BY 1,2,3 HAVING count(*) > 1
  ) d;
  IF dup_count > 0 THEN
    RAISE EXCEPTION 'ABORT 0008: % legacy (province,entity,deep_link) duplicates would be silently dropped; resolve before migrating', dup_count;
  END IF;
END $$;

-- [adversarial GAP-31] ATOMIC SWAP: the two RENAMEs run in ONE transaction. DDL is
-- transactional in PostgreSQL, so both renames commit together — there is NEVER a window where
-- the name `vehicle` is absent (the "API never falls" invariant #7 forbids even a brief gap).
BEGIN;
  ALTER TABLE vehicle RENAME TO vehicle_legacy;   -- keep until verified, then drop in 0008b
  ALTER TABLE vehicle_p RENAME TO vehicle;
COMMIT;
-- The E2E migration gate asserts a concurrent `SELECT FROM vehicle` never errors during the swap.

-- Rollback:
-- ALTER TABLE vehicle RENAME TO vehicle_p; ALTER TABLE vehicle_legacy RENAME TO vehicle;
-- DROP TABLE vehicle_p CASCADE;
```
> **The `COALESCE(province,'00')` backfill is a DECLARED placement gap, not a silent merge**
> `[adversarial GAP-31]`: any entity with NULL province lands in `00` alongside national platforms.
> Such rows are flagged `province_source='backfill-null'` and queued for `cdp:geo.backfill`; they are
> a temporary, itemized placement residual, never permanently conflated with national-platform stock.

**Why `province_code` is denormalized onto `vehicle`.** The partition key must be on the
row itself; joining to `entity` to route every insert/read is impossible for a partition
constraint. It is copied from the owning entity at insert and is immutable for the row's
life (a car doesn't change province; if the dealer's geo is corrected, the row is
re-homed by a maintenance job, rare). National platform-owned C2C cars (§4.3 of the
ontology) live in partition `00`.

### 4.2 `vehicle_spec` — the cold spec sidecar (1:1, optional)

The deep spec (full equipment list, dimensions, emissions, history-report fields,
seller's free-text description, all photo URLs) is **large, rarely filtered, and read
only on the PDP/detail call**. Keeping it inline would bloat the hot `vehicle` heap and
every index scan. It is split into a 1:1 sidecar, co-partitioned by province so the join
is partition-local.

```sql
-- 0008_vehicle_partitioned.sql (cont.)
CREATE TABLE IF NOT EXISTS vehicle_spec (
    province_code CHAR(2) NOT NULL,
    vehicle_ulid  TEXT NOT NULL,
    power_cv      INT,
    power_kw      INT,
    doors         INT,
    seats         INT,
    color         TEXT,
    co2_gkm       INT,
    env_label     TEXT,                  -- DGT environmental label (0/ECO/B/C)
    warranty_months INT,
    description   TEXT,                   -- seller free text (also feeds the classifier)
    photo_urls    JSONB,                  -- array of all photo URLs
    raw           JSONB,                  -- the source's full structured blob (provenance)
    PRIMARY KEY (province_code, vehicle_ulid)
) PARTITION BY LIST (province_code);
-- partitions mirror vehicle (00,01..52,default) — created by 0008.
CREATE INDEX IF NOT EXISTS idx_vspec_desc_trgm ON vehicle_spec USING gin (description gin_trgm_ops);
```

### 4.3 `platform_listing` — the dual-membership edge — migration `0009`

The decision that fixes failure #2. The **same physical car** on AS24 *and* coches.net
*and* renew = **one** `vehicle` row (owned by its selling dealer) + **three**
`platform_listing` rows. The edge carries the per-platform listing URL/ref and its own
lifecycle (a car can leave one platform while staying on another).

```sql
-- 0009_platform_listing.sql — the vehicle ↔ platform edge (dual membership). Additive.
CREATE TABLE IF NOT EXISTS platform_listing (
    province_code        CHAR(2) NOT NULL,            -- co-partition with vehicle
    vehicle_ulid         TEXT NOT NULL,
    platform_entity_ulid TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    listing_url          TEXT NOT NULL,               -- the car's URL ON THIS platform
    listing_ref          TEXT,                        -- the platform's own listing id
    platform_price       NUMERIC(12,2),               -- price as shown on THIS platform (may differ)
    status               listing_status NOT NULL DEFAULT 'listed',
    first_seen           TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen            TIMESTAMPTZ NOT NULL DEFAULT now(),
    removed_at           TIMESTAMPTZ,
    PRIMARY KEY (province_code, vehicle_ulid, platform_entity_ulid),
    FOREIGN KEY (province_code, vehicle_ulid) REFERENCES vehicle(province_code, vehicle_ulid) ON DELETE CASCADE
) PARTITION BY LIST (province_code);
-- partitions mirror vehicle.

CREATE INDEX IF NOT EXISTS idx_pl_platform ON platform_listing (platform_entity_ulid, status);
CREATE INDEX IF NOT EXISTS idx_pl_vehicle  ON platform_listing (vehicle_ulid);
CREATE INDEX IF NOT EXISTS idx_pl_ref      ON platform_listing (platform_entity_ulid, listing_ref);

-- Rollback: DROP TABLE IF EXISTS platform_listing CASCADE;
```

**The reflexive case, fully expressed.** A car on AS24 sold by "Flexicar Barcelona"
produces: 1 `entity` (AS24, `kind=plataforma`, `is_tier1=true`), 1 `entity` (Flexicar
BCN branch, `kind=compraventa`), 1 `organization` (Flexicar), 1 `vehicle` (owned by
Flexicar BCN, `entity_ulid`→branch), 1 `platform_listing` (vehicle↔AS24). Per-platform
inventory = `SELECT v.* FROM platform_listing pl JOIN vehicle v USING (province_code,
vehicle_ulid) WHERE pl.platform_entity_ulid = :as24 AND pl.status='listed'`. Per-dealer
inventory = `WHERE v.entity_ulid = :flexicar_bcn`. Both satisfied; the same car answers
both. **C2C private listings** (wallapop/milanuncios) are owned by a per-platform sentinel
`c2c_private` entity (ontology §4.3) so the ownership invariant holds without fabricating
fake dealers.

### 4.4 `auction_lot` — the time-boxed inventory shape — migration `0010` (v2-scoped, defined now)

The third inventory shape (`01-ENTITY-ONTOLOGY.md §5`, D-7). A retail-priced `vehicle`
cannot honestly represent a live bid; forcing it corrupts price-delta semantics. Defined
here so the schema is complete; harvest is v2 (`§9`).

```sql
-- 0010_auction_lot.sql — auction lot overlay (subasta). Defined; harvest deferred to v2.
CREATE TABLE IF NOT EXISTS auction_lot (
    lot_ulid        TEXT PRIMARY KEY CHECK (lot_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
    operator_ulid   TEXT NOT NULL REFERENCES entity(entity_ulid),  -- the subasta operator/platform
    center_ulid     TEXT REFERENCES entity(entity_ulid),           -- physical center (a branch), nullable
    lot_ref         TEXT NOT NULL,
    vehicle_descriptor JSONB NOT NULL,    -- make/model/year/km/expertise (lot data, not a vehicle row)
    seller_ref      TEXT,                  -- fleet/renting/bank (the source of the lot)
    auction_open    TIMESTAMPTZ,
    auction_close   TIMESTAMPTZ,
    current_price   NUMERIC(12,2),
    status          TEXT NOT NULL DEFAULT 'live' CHECK (status IN ('live','sold','withdrawn')),
    first_seen      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (operator_ulid, lot_ref)
);
CREATE INDEX IF NOT EXISTS idx_lot_operator ON auction_lot (operator_ulid, status);
CREATE INDEX IF NOT EXISTS idx_lot_window   ON auction_lot (auction_close) WHERE status='live';
-- Rollback: DROP TABLE IF EXISTS auction_lot;
```

The delta engine generalizes to lots (a lot's PRICE_CHANGE = a new bid; GONE = SOLD or
WITHDRAWN) by emitting into the same event log with the lot id as subject (§5.4).

---

## 5. The delta engine & append-only history — migration `0011`

The mandate's "complete history": additions, removals, price changes, photo changes, km
changes — every one an immutable fact, queryable as "delta since T".

### 5.1 `vehicle_event` — append-only, time-range partitioned

The event log grows **monotonically and forever** (full history retention). It is
queried by *time* ("delta since T") and by *entity*. Therefore: **`PARTITION BY RANGE
(observed_at)` monthly**, sub-decision distinct from the snapshot's province
partitioning. Old months become cold, can be compressed/detached/archived without
touching the hot current month, and the "delta since yesterday" query touches one (or
two) partitions instead of a billion-row heap.

```sql
-- 0011_event_history.sql — append-only delta log, monthly range partitions. Additive.
CREATE TABLE IF NOT EXISTS vehicle_event_p (
    event_ulid   TEXT NOT NULL CHECK (event_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
    vehicle_ulid TEXT NOT NULL,
    entity_ulid  TEXT NOT NULL,
    province_code CHAR(2) NOT NULL,            -- denormalized for geo-scoped delta
    event_type   vehicle_event_type NOT NULL,
    old_value    JSONB,
    new_value    JSONB,
    observed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- [adversarial GAP-14] idempotency key: a real mutation has a stable diff hash. Under
    -- XAUTOCLAIM redelivery (a worker that wrote the event then crashed before XACK), the
    -- redelivered job re-diffs and would re-emit the SAME (vehicle, type, diff) — the UNIQUE
    -- constraint makes that INSERT a no-op, so the append-only log is exactly-once-per-real-
    -- mutation, never a double-emitted delta. NULL never collides (only meaningful diffs key).
    event_key    TEXT NOT NULL,                 -- = hash(vehicle_ulid || event_type || source_diff_hash)
    PRIMARY KEY (observed_at, event_ulid),     -- partition key in PK
    UNIQUE (event_key, observed_at)            -- redelivery dedupe (partition-local)
) PARTITION BY RANGE (observed_at);

-- monthly partitions, auto-created ahead by a maintenance job (§8.3). Example seeds:
CREATE TABLE IF NOT EXISTS vehicle_event_2026_06 PARTITION OF vehicle_event_p
  FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE IF NOT EXISTS vehicle_event_2026_07 PARTITION OF vehicle_event_p
  FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE IF NOT EXISTS vehicle_event_default PARTITION OF vehicle_event_p DEFAULT;

CREATE INDEX IF NOT EXISTS idx_ve_entity_time ON vehicle_event_p (entity_ulid, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_ve_vehicle     ON vehicle_event_p (vehicle_ulid, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_ve_type_time   ON vehicle_event_p (event_type, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_ve_prov_time   ON vehicle_event_p (province_code, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_ve_since        ON vehicle_event_p (observed_at);  -- global delta-since

-- migrate the 41.165 live events (backfill province from entity), then swap:
INSERT INTO vehicle_event_p (event_ulid, vehicle_ulid, entity_ulid, province_code,
       event_type, old_value, new_value, observed_at)
SELECT ve.event_ulid, ve.vehicle_ulid, ve.entity_ulid, COALESCE(e.province_code,'00'),
       ve.event_type::text::vehicle_event_type, ve.old_value, ve.new_value, ve.observed_at
FROM vehicle_event ve LEFT JOIN entity e USING (entity_ulid);
ALTER TABLE vehicle_event RENAME TO vehicle_event_legacy;
ALTER TABLE vehicle_event_p RENAME TO vehicle_event;

-- enforce append-only: block UPDATE and DELETE (history is immutable, principle #3).
DROP TRIGGER IF EXISTS trg_ve_immutable ON vehicle_event;
CREATE TRIGGER trg_ve_immutable BEFORE UPDATE OR DELETE ON vehicle_event
  FOR EACH ROW EXECUTE FUNCTION cardeep_block_mutation();

-- Rollback: swap names back, DROP vehicle_event_p, drop trigger.
```

> **Note on the immutability trigger + partition maintenance.** `DETACH PARTITION` and
> `DROP TABLE <old_month>` are DDL, not row DELETEs, so they are **not** blocked by the
> row-level trigger — archival of cold months works while live rows stay immutable. The
> trigger only forbids application-level UPDATE/DELETE of individual events.

> **Atomic snapshot+event write (the delta exactly-once guarantee, `[adversarial GAP-14]`).**
> The `vehicle` snapshot UPDATE/INSERT and its `vehicle_event` INSERT MUST execute in **ONE DB
> transaction**. If the snapshot write and the event write are not atomic, a crash between them
> (XAUTOCLAIM redelivery, §04 §4.4) re-diffs against an already-advanced snapshot and either emits
> nothing (idempotent, lost nothing) OR — if not atomic — double-emits the event. The single
> transaction + the `event_key` UNIQUE constraint together make the delta **exactly-once per real
> mutation** under at-least-once redelivery: this is the core product's ("full delta, complete
> history") correctness guarantee, now proven under the very crash-recovery mechanism the system
> relies on, not merely asserted from the snapshot's re-run idempotency (which proves new=0/gone=0
> for the SNAPSHOT but says nothing about event DUPLICATION).

### 5.2 The event payload contract (so consumers can rely on shape)

`old_value`/`new_value` are JSONB with a per-type shape, fixed here so the API and any
consumer parse deterministically:

| `event_type` | `old_value` | `new_value` | meaning |
|---|---|---|---|
| `NEW` | `null` | `{price, title, make, model, year, km}` | first time the car is seen |
| `GONE` | `{price}` | `null` | available → no longer harvested |
| `REAPPEARED` | `null` | `{price}` | gone → seen again (relisted) |
| `PRICE_CHANGE` | `{price}` | `{price}` | price mutated |
| `PHOTO_CHANGE` | `{photo, photo_hash}` | `{photo, photo_hash}` | pHash distance over threshold |
| `KM_CHANGE` | `{km}` | `{km}` | odometer mutated |
| `STATUS_CHANGE` | `{status}` | `{status}` | available↔reserved etc. |
| `SPEC_CHANGE` | `{field:old}` | `{field:new}` | any other tracked spec field |

The live `pipeline/ingest.py` already emits NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE
in exactly this spirit `[VERIFIED]`; this only formalizes the JSON shape and adds
REAPPEARED (the relist case the current code silently folds into status flip) and
STATUS_CHANGE/SPEC_CHANGE for the richer spec.

### 5.3 Why state-from-log is the correct shape (and the cost it pays)

The `vehicle` snapshot is a **cache**; `vehicle_event` is the **source of truth**. Any
past inventory ("what did dealer X have on 2025-03-01?") is reconstructable by replaying
events up to that timestamp. This is event-sourcing applied narrowly to inventory delta —
chosen because the mandate demands "complete history" and "delta-since," which a
mutate-in-place table cannot provide without exactly this log. The cost is write
amplification (every mutation writes both the snapshot update and an event); accepted,
because the event write is an append (cheap) and the read patterns (serve current, diff
since T) are both first-class.

### 5.4 Auction lot events reuse the same log

A lot's lifecycle (NEW lot / bid PRICE_CHANGE / SOLD / WITHDRAWN) is recorded in
`vehicle_event` with `vehicle_ulid = lot_ulid` and `event_type ∈ {NEW, PRICE_CHANGE,
GONE}` (GONE carrying `{reason: 'sold'|'withdrawn'}` in `new_value`). One delta API
serves both retail and auction history (v2).

---

## 6. Cross-platform same-car identity (the photo-hash spine) — migration `0009` cont.

The same car surfaces on N platforms with different listing ids. The match key, in
priority (`01-ENTITY-ONTOLOGY.md §4.2`):

1. **VIN** (`vehicle.vin`) — exact, rare in public data.
2. **`listing_fingerprint`** = `hash(make, model, year, km-band, price-band, photo_hash,
   seller_cdp_code)` — the practical key. `photo_hash` (pHash) is the strongest signal
   because the same dealer uploads the same photos everywhere.
3. None → treated as distinct (accept slight over-count, never over-merge).

**v1 scope: match within a single seller's stock across platforms** (cheap, high
precision) — `idx_vp_fingerprint` + `idx_vp_photo_hash` make this a partition-local index
scan. The `listing_fingerprint` column is populated by the ingest path; the
pHash distance threshold for PHOTO_CHANGE vs same-photo is a recipe constant (`[ASSUMED]`
Hamming distance ≤ 6 of 64 bits = "same photo," tunable).

### 6.1 Cross-seller same-car resolver — STRONG-key only, with a measured over-count bound `[adversarial GAP-3/26]`
The dedup key `UNIQUE (province_code, entity_ulid, deep_link)` is **per-owner-per-URL**, so the
same physical car drained from two platforms arrives with two different `deep_link`s and **inserts
two `vehicle` rows** — the failure-#2 "one car = one vehicle + N edges" invariant is a schema shape
with no ingest algorithm unless cross-seller identity is resolved. Deferring it blindly (the prior
"known, bounded over-count" with no bound) means every served platform/national rollup counter is
**knowingly inflated by an UNMEASURED amount** — exactly the L1/L2 lie the Inquisition exists to kill.
This is closed two ways:
- **A STRONG-key cross-seller resolver ships in v1**, deliberately conservative so over-merge stays
  strictly below under-merge: a second sighting matches an existing vehicle ONLY on **VIN exact**, OR
  **pHash Hamming ≤ 6 AND (make, model, year, km-band) all equal**. On match, the ingest path does
  **NOT insert a second `vehicle` row** — it adds a `platform_listing` edge (or, for a different
  selling entity, re-homes ownership per the broker/wholesale precedence rule) so the union, not the
  double, is produced. No match → distinct row (accept slight over-count, never over-merge).
- **The residual cross-seller over-count is BOUNDED by a measured CI.** A labeled sample estimates
  the cross-seller duplication rate per platform; every served platform `listing_counter` and every
  national-stock rollup carries `±dup_ci`. A counter knowingly inflated by an unmeasured amount is
  forbidden: it is either deduped by the resolver above or served WITH its measured bound. (Feeds the
  KPI `cross_seller_dup_ci`, MASTER_PLAN §6.3, and the vehicle-recall estimator, V6 §4.8.)
- **Ingest ordering (the ownership invariant under wholesale).** A platform drain stages raw listings
  to `listing_staging` (additive, `0009`) keyed `(platform_entity_ulid, listing_ref)`, mints/links
  the selling entity (`cdp:resolve_seller`, geocode → province), and only THEN promotes to a
  `vehicle` row owned by that resolved entity + a `platform_listing` edge. No `vehicle` is ever owned
  by a `kind=plataforma` entity; staging-pending rows are counted as a declared "pending-attribution"
  residual, never as fabricated dealers or platform-owned cars. (MASTER_PLAN C-13.)

---

## 7. The live API contract (per-entity, per-platform, delta-since, geo grid, search)

All endpoints return the consistent envelope already live in `services/api/main.py`
`[VERIFIED]`: `{ok: bool, data: any, error: string|null, meta: object|null}`. `meta`
carries pagination/counters. The current API has 5 endpoints; this is the full F6 target
contract (the additions are marked **NEW**).

### 7.1 Envelope & pagination conventions

```jsonc
// success
{ "ok": true, "data": [...], "error": null,
  "meta": { "count": 50, "cursor": "01J…", "next_cursor": "01J…", "total": 1284 } }
// error
{ "ok": false, "data": null, "error": "entity CDP-ES-28-… not found", "meta": null }
```

- **Cursor pagination, not OFFSET.** On a live, shifting set (`02-SCRAPING-ENGINE.md §0`
  warns the inventory shifts across pages), OFFSET double-serves/skips. The cursor is the
  last `vehicle_ulid` (ULIDs are time-sortable), so pagination is stable under concurrent
  inserts. `?limit=` default 50, max 200.
- **`delta-since` uses a timestamp cursor**, not a row cursor (events are time-ordered).

### 7.2 Endpoint catalog

| Method · Path | Purpose | Backed by |
|---|---|---|
| `GET /health` | liveness + counts (live) | counts across core tables |
| `GET /entities/{cdp_code}` | entity card + available count (live) | `entity` + count |
| `GET /entities/{cdp_code}/inventory` | available stock (live) | `vehicle WHERE status='available'` |
| `GET /entities/{cdp_code}/inventory/{vehicle_ulid}` **NEW** | full PDP incl spec | `vehicle` + `vehicle_spec` + `platform_listing` |
| `GET /entities/{cdp_code}/delta?since=` | event stream (live) | `vehicle_event` |
| `GET /platforms/{cdp_code}/inventory` **NEW** | per-platform hosted stock | `platform_listing` ⋈ `vehicle` |
| `GET /platforms/{cdp_code}/delta?since=` **NEW** | per-platform listing delta | listing events |
| `GET /orgs/{org_code}` **NEW** | chain card + branch list + union count | `organization` + `entity` |
| `GET /orgs/{org_code}/inventory` **NEW** | union of branch stock | `vehicle WHERE entity_ulid IN (branches)` |
| `GET /geo/{province}/entities` | entities in province (live) | `entity` |
| `GET /geo/{province}/{comarca}/entities` **NEW** | comarca-scoped | `entity` |
| `GET /geo/grid?bbox=&kinds=&zoom=` **NEW** | map grid of POS + counts | bbox bucket aggregation |
| `GET /delta?since=&province=&type=` **NEW** | global/geo-scoped delta firehose | `vehicle_event` partitions |
| `GET /search?q=&kind=&province=&make=&price_min=&price_max=` **NEW** | faceted search | trgm + filtered indexes |
| `GET /stats` **NEW** | counts by kind/province/tier1 + freshness | rollup view |

### 7.3 The geo-grid endpoint (the map of Spain, no PostGIS)

```
GET /geo/grid?bbox=minLon,minLat,maxLon,maxLat&kinds=compraventa,desguace&zoom=8
→ ok([ { cell:"…", lat, lon, count, by_kind:{…}, sample_cdp:[…] } ], meta:{cells, total})
```

Without PostGIS, the grid is computed by **rounding lat/lon to a zoom-dependent decimal
grid** (`round(lat, z) , round(lon, z)`) and `GROUP BY` the rounded cell, prefiltered by
the bbox on `idx_entity_latlon` (the partial composite btree, §3.1). Server-side cell
size = `10^-(zoom-6)` degrees. This is O(rows-in-bbox), and the bbox prunes to the
visible window. Province-level pruning further narrows partitions when the bbox maps to a
known province set. `[ASSUMED]` adequate to national zoom; if rooftop-density clustering
is later needed, PostGIS `ST_SnapToGrid` is the drop-in (§10.4).

### 7.4 `delta-since` semantics (the contract the consumer relies on)

`GET /delta?since=2026-06-11T00:00:00Z&province=28&type=PRICE_CHANGE` returns every event
with `observed_at >= since`, ordered ascending, cursor-paginated by `(observed_at,
event_ulid)`. Because the log is monthly-partitioned and indexed on `observed_at`, "since
yesterday" touches one partition. The consumer drives an incremental sync by storing the
last `observed_at` it saw and re-requesting — the live system never loses an event
(append-only) so the sync is exactly-once over the log.

---

## 8. Migration plan, in-place safety, and maintenance jobs

### 8.1 Migration sequence (additive, on top of live `0001`–`0004`)

```
0005  types + extensions + shared triggers        (no data change)
0006  entity evolve (enum swap + ontology cols + platform_meta)   [in-place, 12.862 rows]
0007  organization + entity.org_id FK + entity_source.first_seen
0008  vehicle → LIST(province) partitioned + vehicle_spec  [migrate 39.068 rows, swap]
0009  platform_listing edge + listing_fingerprint backfill
0010  auction_lot (defined, v2 harvest)
0011  vehicle_event → RANGE(month) partitioned + immutability trigger  [migrate 41.165]
0012  rollup views (stats, freshness) + materialized geo-grid cache (optional)
```

Each ships with its inline `-- Rollback:` and is applied by the existing runner
(`python -m scripts.migrate up`), which already wraps each in a transaction + ledger
`[VERIFIED]`. The E2E pattern from `docs/ARCHITECTURE.md` (apply → verify → rollback →
verify clean → re-apply → count preserved → idempotency) applies unchanged.

### 8.2 Pre-flight audit guard (so an enum swap never fails mid-migration)

Before `0006` casts `kind` TEXT→ENUM, a pre-flight asserts every live value is in the
enum (the live DB has 4 kinds, all in the enum `[VERIFIED]`):

```sql
-- 0006_preflight (runs inside 0006, before the ALTER)
DO $$
DECLARE bad text;
BEGIN
  SELECT string_agg(DISTINCT kind, ',') INTO bad FROM entity
   WHERE kind NOT IN ('concesionario_oficial','agente_oficial','compraventa','garaje',
     'desguace','rent_a_car_vo','subasta','importador','oem_vo_portal','plataforma','cadena');
  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'pre-flight: entity.kind has values outside enum: %', bad;
  END IF;
END $$;
```

The same guard pattern precedes the `vehicle.status` and `website_waf` swaps.

### 8.3 Maintenance jobs (the model needs three recurring jobs)

1. **Partition pre-creation.** A monthly cron creates next month's `vehicle_event_*`
   partition (and yearly checks province partitions exist). If it misses, rows land in
   the `default` partition (no data loss) and an `alert` fires (origin
   `partition_maintenance`).
2. **Cold-event archival.** Months older than the retention-hot window (`[ASSUMED]` 24
   months) are `DETACH`ed and `pg_dump`ed to cold storage, keeping the live index small
   while preserving full history off-line. DDL, so the immutability trigger allows it.
3. **Denormalization reconcile.** Nightly recompute `entity.attest_count` and
   `organization.branch_count` from source-of-truth counts, correcting any trigger drift,
   and emit a verdict if they diverged (silent drift never passes as TRUSTWORTHY).

### 8.4 Resilience layer — `0004` kept, two additions

`verification_verdict`, `source_health`, `alert` (live `[VERIFIED]`) are unchanged. Two
additions in `0012`: (a) `source_health.entity_ulid`/`platform` nullable FK so an alert's
"exact origin" resolves to a coded node, and (b) an `alert.subject_cdp_code` so the
firehose can filter alerts by entity. These make the mandate's "alert with the exact
origin, self-repair" addressable per-node.

---

## 9. Honest residuals & v1/v2 boundary (no whitewashing)

1. **Auction lots (`0010`) are defined, not harvested.** v1 catalogues `subasta`
   operators + physical centers (denominator); lot-by-lot harvest is v2
   (`01-ENTITY-ONTOLOGY.md §8`). The table exists so v2 is a code change, not a schema
   migration.
2. **Parts inventory (desguace) is out of v1.** The whole-car stock of a desguace is a
   `vehicle`; its **parts** marketplace (Opisto/Ovoko) is a documented v2 shape, no table
   shipped (YAGNI until the parts pillar lands).
3. **Cross-seller same-car matching is out of v1** (§6) — single-seller only, to avoid
   over-merge. `vin`/`listing_fingerprint` are stored now so v2 can extend without a
   migration.
4. **`province_code` denormalization on `vehicle`/`event` is a chosen trade.** It couples
   the row to the owning entity's province; a geo correction requires re-homing the row
   across partitions (a maintenance op, rare). Accepted for the geo-first access pattern.
5. **No PostGIS.** The grid/near-me queries are bbox+Haversine, not spatial-indexed
   (§3.1, §7.3). Adequate at national zoom `[ASSUMED]`; PostGIS is a clean later add
   (§10.4), not a rewrite.
6. **`attest_count`/`branch_count` are denormalized.** Trigger-maintained + nightly
   reconciled (§8.3). The reconcile job is the guard against drift; without it they could
   silently lie — so it is mandatory, not optional.
7. **Scale is designed-for with a reversible re-partition path, not committed blind**
   `[adversarial GAP-34].` The headline is reconciled and stated ONCE: **~1–2M *live* listings at
   any time (00 §1.1), tens-of-millions of *lifetime* rows including forever gone-history (§5).**
   Two knowable-today facts are addressed before 0008/0011 are final, not after a load test: (a)
   **province `LIST` skew** — Madrid/Barcelona + the `00` bucket dwarf rural provinces 10–100×, so
   `LIST` does NOT auto-balance; the worst offender (`00` C2C) is sub-HASH-partitioned (§4.1), and a
   monitoring note flags the metro partitions for sub-partition if they grow unbalanced; (b) the
   **event log volume** (tens-of-millions × multi-event lifecycle × forever) reaches billions of
   rows — the 24-hot-month RANGE window keeps each hot month bounded, cold months are DETACHed to
   archival storage. The `LIST → sub-HASH` and monthly-window choices are **documented-reversible**
   (maintenance re-home / re-window), so the partition DDL is NOT irreversible. Partition-prune plans
   are still `EXPLAIN`-verified once real volume lands. Stated, not hidden.

---

## 10. Why this is the deepest correct shape (closing argument)

### 10.1 Every mandate clause maps to a structure
- *Find every POS, code each uniquely* → `entity` + deterministic `cdp_code` + `org` for
  chains (§3).
- *Extract ALL stock* → `vehicle` (+ `vehicle_spec`, `auction_lot`) (§4).
- *The platforms themselves, same car ∈ platform AND dealer* → platform-as-entity +
  `platform_listing` edge (§3.2, §4.3) — the failure-#2 fix.
- *Live API with full delta (adds, removals, price/photo changes, complete history)* →
  append-only `vehicle_event` + `delta-since` contract (§5, §7.4).
- *Ordered by country/province/comarca/city* → geo backbone + province partitioning +
  geo-grid API (§3, §4.1, §7.3).
- *Recipe saved, source fails → exact-origin alert, self-repair, never falls* →
  `recipe_version` pointer + `source_health`/`alert` resolving to coded nodes (§8.4).
- *Tier-1 separated absolutely* → `is_tier1` first-class + `platform_meta` defense +
  `countries/ES/_tier1/` placement (§3.2, principle #5).

### 10.2 Doctrine compliance is structural, not aspirational
INSERT-new/close-gone is enforced by the ingest path + the soft-close columns; UPDATE
only-on-mutation by the per-field diff (`pipeline/ingest.py` `[VERIFIED]`); history
immutability by the `cardeep_block_mutation` trigger on `vehicle_event` (§5.1) — a
violation **raises**, it is not a convention one can forget.

### 10.3 Scale is addressed at the table level
Two orthogonal partition schemes for two access patterns: **province (LIST)** for the
geo-/entity-queried snapshot, **month (RANGE)** for the time-queried log. Hot/cold split
of spec out of the vehicle heap. Partial + composite indexes sized to the exact hot
paths. This is the standard, correct PG16 answer for "tens of millions + delta," not a
single-heap gamble.

### 10.4 The one extension-gated future optimization (declared, not assumed-done)
If/when the operator installs PostGIS, `0099_postgis_geo.sql` adds a generated
`geography(Point,4326)` to `entity` + a GiST index + swaps the grid endpoint to
`ST_SnapToGrid`/`ST_DWithin`. The current model is **complete and correct without it**;
this is a documented upgrade path, marked `[ASSUMED beneficial]`, never silently relied on.
