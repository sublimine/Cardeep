-- 0002_entities.sql — Point-of-sale entities + provenance + dedup aliases
-- Additive, idempotent, reversible.

CREATE TABLE IF NOT EXISTS entity (
    entity_ulid    TEXT PRIMARY KEY,
    cdp_code       TEXT NOT NULL,                 -- immutable Cardeep code, CDP-ES-{prov}-{b32}
    kind           TEXT NOT NULL
        CHECK (kind IN ('concesionario_oficial','compraventa','garaje','desguace','plataforma','cadena')),
    legal_name     TEXT,
    trade_name     TEXT,
    cif            TEXT,                           -- registral legal id (nullable)
    cnae           TEXT,                           -- CNAE activity code (nullable)
    province_code  CHAR(2) REFERENCES geo_province(code),
    municipality_code CHAR(5) REFERENCES geo_municipality(code),
    comarca_id     BIGINT REFERENCES geo_comarca(id),
    address        TEXT,
    postcode       TEXT,
    lat            DOUBLE PRECISION,
    lon            DOUBLE PRECISION,
    phone          TEXT,
    email          TEXT,
    website        TEXT,
    website_waf    TEXT                            -- none|cloudflare|akamai|datadome|perimeterx|imperva
        CHECK (website_waf IS NULL OR website_waf IN
               ('none','cloudflare','akamai','datadome','perimeterx','imperva','other')),
    is_tier1       BOOLEAN NOT NULL DEFAULT FALSE, -- hard separation of hard-defense platforms
    status         TEXT NOT NULL DEFAULT 'unverified'
        CHECK (status IN ('active','closed','unverified')),
    recipe_version INT,                            -- pointer to git recipe.yaml version
    first_discovered_source TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_entity_cdp_code ON entity (cdp_code);
CREATE INDEX IF NOT EXISTS idx_entity_province ON entity (province_code);
CREATE INDEX IF NOT EXISTS idx_entity_municipality ON entity (municipality_code);
CREATE INDEX IF NOT EXISTS idx_entity_kind ON entity (kind);
CREATE INDEX IF NOT EXISTS idx_entity_tier1 ON entity (is_tier1) WHERE is_tier1 = TRUE;
CREATE INDEX IF NOT EXISTS idx_entity_website ON entity (website) WHERE website IS NOT NULL;

-- Multi-source provenance: which sources attest this entity (capture-recapture + dedup)
CREATE TABLE IF NOT EXISTS entity_source (
    entity_ulid TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    source_key  TEXT NOT NULL,                     -- e.g. 'paginasamarillas','dgt_cat','as24'
    source_ref  TEXT,                              -- id/url within that source
    seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (entity_ulid, source_key)
);
CREATE INDEX IF NOT EXISTS idx_entity_source_key ON entity_source (source_key);

-- Name/domain variants for dedup
CREATE TABLE IF NOT EXISTS entity_alias (
    entity_ulid TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    alias_kind  TEXT NOT NULL DEFAULT 'name'
        CHECK (alias_kind IN ('name','domain','cif','phone')),
    PRIMARY KEY (entity_ulid, alias)
);
CREATE INDEX IF NOT EXISTS idx_entity_alias_alias ON entity_alias (alias);

-- Rollback:
-- DROP TABLE IF EXISTS entity_alias;
-- DROP TABLE IF EXISTS entity_source;
-- DROP TABLE IF EXISTS entity;
