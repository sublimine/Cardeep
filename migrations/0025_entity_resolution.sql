-- 0025_entity_resolution.sql — F1 entity-resolution overlay (β).
--
-- Derives "same professional dealer across channels" as a graph node via
-- inventory-fingerprint (Jaccard on canonical_vehicle_ulid from B7) +
-- strong-identifier reinforcement (phone / website domain).
--
-- NON-DESTRUCTIVE overlay: mirrors 0020_entity_cluster.sql pattern exactly.
-- Entity rows are NEVER mutated. Every entity_ulid survives untouched.
-- The resolved dealer is derived from the graph, not stamped onto entity.
--
-- Key design decision (verified §A of ENTITY_RESOLUTION_ARCHITECTURE.md):
--   - Strong identifiers (tel/domain) are ALMOST EMPTY on digital channels
--     (wallapop/coches_net/milanuncios tel=0/web=0).
--   - Inventory fingerprint IS the dominant key: 181k+ used-car canonicals
--     shared cross-entity P (B7 run vehicle-identity-det-v1).
--   - θ=0.30 Jaccard: calibrated to real data (see resolve_entities.py).
--
-- Anti-over-merge guards (§8 of architecture):
--   - catalog/new-stock canonicals excluded (km=0 or >MAX_ENTITY_COLLISION_K)
--   - Phone HIGH-COLLISION: one identifier alone never merges cross-province
--   - Transitive closure only on accepted edges (union-find deterministic)
--
-- vam_verified=FALSE until Director gates TRUE (same pattern as B1.2).

-- ---------------------------------------------------------------------------
-- entity_resolution_run: one execution of the β resolver
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entity_resolution_run (
    run_id              TEXT        PRIMARY KEY,              -- caller-supplied id
    run_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolver            TEXT        NOT NULL,                 -- 'inventory-fingerprint-v1'
    n_in                INTEGER,                              -- P-stratum entities fed
    n_resolved_dealers  INTEGER,                              -- distinct derived dealer nodes
    n_merged            INTEGER,                              -- entities collapsed
    vam_verified        BOOLEAN     NOT NULL DEFAULT FALSE,   -- TRUE only after Director gate
    vam_verdict_id      BIGINT      REFERENCES verification_verdict(id),
    notes               JSONB
);

-- ---------------------------------------------------------------------------
-- entity_resolution: per-entity assignment to a resolved dealer
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entity_resolution (
    run_id              TEXT        NOT NULL
                            REFERENCES entity_resolution_run(run_id) ON DELETE CASCADE,
    entity_ulid         TEXT        NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    resolved_dealer_ulid TEXT       NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    signal              TEXT        NOT NULL,  -- 'fingerprint' | 'phone' | 'website' | 'fingerprint+phone' | 'fingerprint+website' | 'none'
    probability         NUMERIC(6,4),          -- Jaccard score when fingerprint present, else 1.0 for id match
    PRIMARY KEY (run_id, entity_ulid)
);

CREATE INDEX IF NOT EXISTS idx_er_resolved_dealer ON entity_resolution (run_id, resolved_dealer_ulid);
CREATE INDEX IF NOT EXISTS idx_er_entity ON entity_resolution (entity_ulid);
CREATE INDEX IF NOT EXISTS idx_er_signal ON entity_resolution (run_id, signal);

-- ---------------------------------------------------------------------------
-- v_resolved_dealer: served resolution (most recent vam_verified=TRUE run)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_resolved_dealer AS
SELECT
    e.entity_ulid,
    e.cdp_code,
    e.trade_name,
    e.kind,
    e.province_code,
    er.resolved_dealer_ulid,
    rd.cdp_code           AS resolved_dealer_cdp_code,
    rd.trade_name         AS resolved_dealer_name,
    er.signal,
    er.probability,
    er.run_id
FROM entity_resolution er
JOIN entity e  ON e.entity_ulid  = er.entity_ulid
JOIN entity rd ON rd.entity_ulid = er.resolved_dealer_ulid
WHERE er.run_id = (
    SELECT run_id
    FROM entity_resolution_run
    WHERE vam_verified = TRUE
    ORDER BY run_at DESC
    LIMIT 1
)
AND e.kind IN ('compraventa', 'concesionario_oficial', 'garaje');

-- Rollback:
-- DROP VIEW  IF EXISTS v_resolved_dealer;
-- DROP TABLE IF EXISTS entity_resolution CASCADE;
-- DROP TABLE IF EXISTS entity_resolution_run CASCADE;
