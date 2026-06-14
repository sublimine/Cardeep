-- 0023_vehicle_cluster.sql — vehicle physical-unit deduplication overlay (CAMPAIGN B7).
--
-- Mirrors 0020_entity_cluster.sql (B1.2) exactly in structure: non-destructive overlay that
-- identifies the "same physical car" across platforms (wallapop, milanuncios, coches.net, etc.)
-- WITHOUT ever mutating a single row in vehicle.  Every vehicle_ulid survives untouched.
--
-- Resolution logic (cluster_vehicles.py):
--   Signal A: identical normalized photo_url (same byte-level photo = same physical car). STRONG.
--   Signal B: firma = exact (make, model, year, km) + price within ±2% + same province_code
--             (via entity.province_code) + same normalized title OR same entity (anti-FP guard).
--   Anti-FP hard guards:
--     - NEVER merge cross-province.
--     - photo_url alone is sufficient.
--     - Firma-only merge requires at least one extra corroborating signal (same title OR same entity).
--
-- vam_verified=FALSE until the Director manually gates it TRUE (same pattern as entity_cluster).

-- ---------------------------------------------------------------------------
-- vehicle_cluster_run: one execution of the physical-unit resolver
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehicle_cluster_run (
    cluster_run_id  TEXT        PRIMARY KEY,                -- caller-supplied id
    run_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolver        TEXT        NOT NULL,                   -- 'union-find-deterministic'
    resolver_version TEXT,
    scope           TEXT        NOT NULL,                   -- SQL condition used to filter vehicles
    blocking_rules  JSONB,                                  -- audit / reproducibility
    n_in            INTEGER,                                -- listings fed to the resolver
    n_clusters      INTEGER,                                -- distinct physical-car groups
    n_merged        INTEGER,                                -- listings collapsed (n_in - n_clusters)
    vam_verified    BOOLEAN     NOT NULL DEFAULT FALSE,     -- TRUE only after Director VAM gate
    vam_verdict_id  BIGINT      REFERENCES verification_verdict(id),
    notes           TEXT
);

-- ---------------------------------------------------------------------------
-- vehicle_cluster: per-listing cluster assignment
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehicle_cluster (
    cluster_run_id      TEXT    NOT NULL
                            REFERENCES vehicle_cluster_run(cluster_run_id) ON DELETE CASCADE,
    vehicle_ulid        TEXT    NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    canonical_vehicle_ulid TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    match_signal        TEXT,           -- 'photo_url' | 'firma' | 'both'
    match_probability   DOUBLE PRECISION,
    cluster_size        INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (cluster_run_id, vehicle_ulid)
);

CREATE INDEX IF NOT EXISTS idx_vc_canonical ON vehicle_cluster (cluster_run_id, canonical_vehicle_ulid);
CREATE INDEX IF NOT EXISTS idx_vc_vehicle   ON vehicle_cluster (vehicle_ulid);
CREATE INDEX IF NOT EXISTS idx_vc_run_sig   ON vehicle_cluster (cluster_run_id, match_signal);

-- ---------------------------------------------------------------------------
-- v_canonical_vehicle: served resolution (most recent vam_verified=TRUE run)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_canonical_vehicle AS
SELECT
    vc.vehicle_ulid,
    vc.canonical_vehicle_ulid,
    v.deep_link              AS vehicle_deep_link,
    cv.deep_link             AS canonical_deep_link,
    vc.match_signal,
    vc.match_probability,
    vc.cluster_size,
    vc.cluster_run_id
FROM vehicle_cluster vc
JOIN vehicle v  ON v.vehicle_ulid  = vc.vehicle_ulid
JOIN vehicle cv ON cv.vehicle_ulid = vc.canonical_vehicle_ulid
WHERE vc.cluster_run_id = (
    SELECT cluster_run_id
    FROM vehicle_cluster_run
    WHERE vam_verified = TRUE
    ORDER BY run_at DESC
    LIMIT 1
);

-- Rollback:
-- DROP VIEW  IF EXISTS v_canonical_vehicle;
-- DROP TABLE IF EXISTS vehicle_cluster CASCADE;
-- DROP TABLE IF EXISTS vehicle_cluster_run CASCADE;
