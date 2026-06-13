-- 0020_entity_cluster.sql — entity-resolution overlay (CAMPAIGN B1.2).
-- Additive + reversible. Delivers "one code per physical dealer" WITHOUT ever rewriting an
-- immutable cdp_code: a NON-DESTRUCTIVE overlay that groups existing entities under a
-- deterministically-chosen canonical entity. Every original cdp_code survives untouched; the
-- API resolves any entity -> its canonical at query time (view v_canonical). This is how B1
-- collapses the ~14k historical duplicates (OEM-VO explosion + cross-source + intra-source)
-- that the forward-fixes (B1.0/B1.1) only stop going forward.
--
-- FK NOTE: entity.cdp_code has only a UNIQUE INDEX (uq_entity_cdp_code), NOT a unique
-- constraint, so PostgreSQL cannot use it as an FK target. We key on entity_ulid (the PK) and
-- expose the human cdp_code through the resolving view.

-- A clustering run: one execution of a resolver over a scope, with its parameters and the VAM
-- verdict that gates whether it becomes the served mapping. Only the latest vam_verified=TRUE
-- run is authoritative (see v_canonical).
CREATE TABLE IF NOT EXISTS entity_cluster_run (
    cluster_run_id   TEXT PRIMARY KEY,                 -- caller-supplied id (ISO ts + scope tag)
    run_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolver         TEXT NOT NULL,                    -- 'splink' | 'deterministic' | 'manual'
    resolver_version TEXT,                             -- e.g. 'splink 4.0.16'
    scope            TEXT NOT NULL,                    -- e.g. "kind <> 'particular'"
    threshold        DOUBLE PRECISION,                 -- match-probability cut used for clustering
    blocking_rules   JSONB,                            -- the rules used (audit + reproducibility)
    n_entities_in    INTEGER,                          -- entities fed to the resolver
    n_clusters_out   INTEGER,                          -- distinct canonical groups produced
    n_merged         INTEGER,                          -- non-canonical members collapsed
    vam_verified     BOOLEAN NOT NULL DEFAULT FALSE,   -- TRUE only after the 3-path VAM passes
    vam_verdict_id   BIGINT REFERENCES verification_verdict(id),
    notes            TEXT
);

-- One row per clustered entity: which canonical it resolves to, in which run. The canonical is
-- itself an entity (the chosen representative of the cluster); a singleton maps to itself.
CREATE TABLE IF NOT EXISTS entity_cluster (
    cluster_run_id    TEXT NOT NULL
                        REFERENCES entity_cluster_run(cluster_run_id) ON DELETE CASCADE,
    entity_ulid       TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    canonical_ulid    TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    match_probability DOUBLE PRECISION,                -- confidence this entity joins the cluster
    cluster_size      INTEGER NOT NULL DEFAULT 1,      -- members in this canonical group
    PRIMARY KEY (cluster_run_id, entity_ulid)
);

CREATE INDEX IF NOT EXISTS idx_ec_canonical ON entity_cluster (cluster_run_id, canonical_ulid);
CREATE INDEX IF NOT EXISTS idx_ec_entity    ON entity_cluster (entity_ulid);

-- The served resolution: every clustered entity -> its canonical cdp_code, from the most recent
-- VAM-verified run ONLY. Entities never seen by a verified run are absent here and resolve to
-- themselves in the API consumer (COALESCE(canonical, self)). Immutable cdp_codes are never
-- touched — this view is the single place identity is resolved.
CREATE OR REPLACE VIEW v_canonical AS
SELECT  e.cdp_code,
        ec.entity_ulid,
        ec.canonical_ulid,
        c.cdp_code         AS canonical_cdp_code,
        ec.match_probability,
        ec.cluster_size,
        ec.cluster_run_id
FROM entity_cluster ec
JOIN entity e ON e.entity_ulid = ec.entity_ulid
JOIN entity c ON c.entity_ulid = ec.canonical_ulid
WHERE ec.cluster_run_id = (
    SELECT cluster_run_id FROM entity_cluster_run
    WHERE vam_verified = TRUE
    ORDER BY run_at DESC
    LIMIT 1
);

-- Rollback:
-- DROP VIEW IF EXISTS v_canonical;
-- DROP TABLE IF EXISTS entity_cluster CASCADE;
-- DROP TABLE IF EXISTS entity_cluster_run CASCADE;
