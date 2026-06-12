-- 0003_vehicles_events.sql — Inventory snapshot + append-only delta history
-- Additive, idempotent, reversible. Implements the mandate's live delta.

CREATE TABLE IF NOT EXISTS vehicle (
    vehicle_ulid   TEXT PRIMARY KEY,
    entity_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    deep_link      TEXT NOT NULL,                  -- per-vehicle URL
    title          TEXT,
    make           TEXT,
    model          TEXT,
    year           INT,
    km             INT,
    price          NUMERIC(12,2),
    currency       CHAR(3) NOT NULL DEFAULT 'EUR',
    fuel           TEXT,
    transmission   TEXT,
    photo_url      TEXT,
    photo_hash     TEXT,                           -- perceptual hash for Δphoto detection
    vin_ref        TEXT,
    recipe_version INT,
    status         TEXT NOT NULL DEFAULT 'available'
        CHECK (status IN ('available','gone')),
    first_seen     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (entity_ulid, deep_link)
);

CREATE INDEX IF NOT EXISTS idx_vehicle_entity ON vehicle (entity_ulid);
CREATE INDEX IF NOT EXISTS idx_vehicle_status ON vehicle (entity_ulid, status);
CREATE INDEX IF NOT EXISTS idx_vehicle_available ON vehicle (entity_ulid) WHERE status = 'available';

-- Append-only delta history. NEVER updated or deleted — the full timeline.
CREATE TABLE IF NOT EXISTS vehicle_event (
    event_ulid   TEXT PRIMARY KEY,
    vehicle_ulid TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    entity_ulid  TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    event_type   TEXT NOT NULL
        CHECK (event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE')),
    old_value    JSONB,
    new_value    JSONB,
    observed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_event_vehicle ON vehicle_event (vehicle_ulid);
CREATE INDEX IF NOT EXISTS idx_event_entity_time ON vehicle_event (entity_ulid, observed_at);
CREATE INDEX IF NOT EXISTS idx_event_type ON vehicle_event (event_type);

-- Rollback:
-- DROP TABLE IF EXISTS vehicle_event;
-- DROP TABLE IF EXISTS vehicle;
