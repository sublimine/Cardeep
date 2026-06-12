-- 0009_platform_listing.sql — the vehicle <-> platform edge (dual membership).
-- Additive + reversible. 03-DATA-MODEL §4.3, §6. This is what makes "the same car on a
-- platform AND its selling dealer" expressible: vehicle.entity_ulid stays the SELLING dealer
-- (ownership is singular); platform membership is THIS edge (membership is plural, 0..M).
--
-- ADAPTATION TO THE CURRENT (UN-PARTITIONED) vehicle TABLE:
--   03 §4.3 designs platform_listing co-partitioned with vehicle, keyed/FK'd on
--   (province_code, vehicle_ulid) -- but that composite PK exists only AFTER 0008 partitions
--   vehicle by province. 0008 is DEFERRED (it recreates the live 39,068-row heap and must be
--   its own careful block). The live vehicle PK today is (vehicle_ulid) with no province_code
--   column. So this edge is created NON-partitioned, FK'd on the live vehicle(vehicle_ulid) PK.
--   When 0008 lands, it re-homes this edge to the co-partitioned (province_code, vehicle_ulid)
--   FK as part of its own data-migrate block. The edge's STRUCTURE and SEMANTICS are identical;
--   only the partition/FK shape is adapted to the table that exists now.

CREATE TABLE IF NOT EXISTS platform_listing (
    vehicle_ulid         TEXT NOT NULL
                           REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    platform_entity_ulid TEXT NOT NULL
                           REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    listing_url          TEXT NOT NULL,               -- the car's URL ON THIS platform
    listing_ref          TEXT,                        -- the platform's own listing id (native)
    platform_price       NUMERIC(12,2),               -- price as shown on THIS platform (may differ)
    listing_fingerprint  TEXT,                        -- hash(make,model,year,km-band,price-band,photo_hash,seller) §6
    status               listing_status NOT NULL DEFAULT 'listed',
    first_seen           TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen            TIMESTAMPTZ NOT NULL DEFAULT now(),
    removed_at           TIMESTAMPTZ,
    PRIMARY KEY (vehicle_ulid, platform_entity_ulid)  -- one edge per (car, platform)
);

CREATE INDEX IF NOT EXISTS idx_pl_platform    ON platform_listing (platform_entity_ulid, status);
CREATE INDEX IF NOT EXISTS idx_pl_vehicle     ON platform_listing (vehicle_ulid);
CREATE INDEX IF NOT EXISTS idx_pl_ref         ON platform_listing (platform_entity_ulid, listing_ref);
-- cross-platform same-car match (the pHash/fingerprint spine, §6).
CREATE INDEX IF NOT EXISTS idx_pl_fingerprint ON platform_listing (listing_fingerprint)
  WHERE listing_fingerprint IS NOT NULL;

-- Rollback:
-- DROP TABLE IF EXISTS platform_listing CASCADE;
