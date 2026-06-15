-- 0027_canonical_dedup.sql — Canonical dedup overlay (deep_link graph).
--
-- PROBLEM: B1 seal (dealer-identity-det-v1, 42,259 canonicals) has an over-count
-- caused by inconsistent geocoding upstream: the same physical dealer was ingested
-- with different municipality_code values -> defeats B1's name+municipality key ->
-- produces duplicate canonicals for the same dealer.
--
-- EVIDENCE: 34,904 deep_link values (unique listing URLs) attributed to >1 canonical;
-- 4,621 canonicals involved. One deep_link = one listing = one real dealer
-- => canonicals sharing a deep_link are the same physical dealer.
--
-- SOLUTION: non-destructive overlay that fuses canonicals connected by shared
-- deep_link into super-canonical groups (union-find over pair graph).
--
-- ANTI-HUB GUARD (K=3): deep_links shared by >=3 canonicals are excluded from
-- graph edges. Distribution analysis showed max collision = 3 (only 3 such links,
-- all confirmed legitimate same-dealer merges by trade_name inspection). K=3 is
-- the safe choice; K=5 would exclude 0 links anyway.
--
-- RESULT (measured 2026-06-15, reproduced by scripts/build_canonical_dedup.py):
--   - deep_links in pair graph (n_canon=2): 34,901
--   - deep_links excluded by anti-hub (n_canon>=3): 3
--   - graph edges (canonical pairs): 2,385
--   - components with >= 2 members (super-canonicals): 2,236
--   - component sizes: 5(x1), 4(x6), 3(x134), 2(x2,095)
--   - canonicals in merge graph: 4,621
--   - redundant canonicals collapsed (n_merged): 2,385
--   - DEDUPED DEALER COUNT: 42,259 - 2,385 = 39,874
--
-- NON-DESTRUCTIVE: entity rows are NEVER mutated. No cdp_code is changed.
-- The overlay is a separate table + view for inspection. vam_verified=FALSE
-- until Director gates TRUE.
--
-- Pattern mirrors entity_cluster_run / entity_cluster (0020_entity_cluster.sql).

-- ---------------------------------------------------------------------------
-- canonical_dedup_run: one execution of the deep_link dedup resolver
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS canonical_dedup_run (
    run_id              TEXT        PRIMARY KEY,              -- caller-supplied id
    run_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolver            TEXT        NOT NULL,                 -- 'deep-link-union-find-v1'
    resolver_version    TEXT,                                 -- e.g. '1.0.0'
    source_cluster_run  TEXT        NOT NULL                  -- B1 run_id this was built against
                            REFERENCES entity_cluster_run(cluster_run_id),
    anti_hub_k          INTEGER     NOT NULL DEFAULT 3,       -- exclude deep_links shared by >= K canonicals
    n_canonicals_in     INTEGER,                              -- B1 canonical count fed to resolver
    n_deep_links_used   INTEGER,                              -- deep_links forming merge edges
    n_deep_links_excl   INTEGER,                              -- deep_links excluded by anti-hub
    n_edges             INTEGER,                              -- canonical pair edges in graph
    n_super_canonicals  INTEGER,                              -- distinct super-canonical groups (components)
    n_merged            INTEGER,                              -- canonicals absorbed (not chosen as super-canonical)
    deduped_count       INTEGER,                              -- n_canonicals_in - n_merged
    vam_verified        BOOLEAN     NOT NULL DEFAULT FALSE,   -- TRUE only after Director gate
    vam_verdict_id      BIGINT      REFERENCES verification_verdict(id),
    notes               JSONB
);

-- ---------------------------------------------------------------------------
-- canonical_dedup: per-canonical mapping to its super-canonical
-- ---------------------------------------------------------------------------
-- One row per canonical cdp_code involved in a merge (both representative and
-- absorbed). Canonicals NOT in any merge group are absent (they are their own
-- super-canonical implicitly, i.e. COALESCE(lookup, self)).
CREATE TABLE IF NOT EXISTS canonical_dedup (
    run_id                  TEXT    NOT NULL
                                REFERENCES canonical_dedup_run(run_id) ON DELETE CASCADE,
    canonical_cdp_code      TEXT    NOT NULL,    -- the B1 canonical cdp_code
    canonical_entity_ulid   TEXT    NOT NULL
                                REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    super_canonical_cdp_code TEXT   NOT NULL,    -- component representative cdp_code
    super_canonical_ulid    TEXT    NOT NULL
                                REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    component_size          INTEGER NOT NULL DEFAULT 1,   -- members in this super-canonical group
    is_representative       BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE = this row IS the super-canonical
    evidence_deep_link      TEXT,                -- one deep_link that links this canonical to the component
    PRIMARY KEY (run_id, canonical_cdp_code)
);

CREATE INDEX IF NOT EXISTS idx_cdd_super
    ON canonical_dedup (run_id, super_canonical_cdp_code);
CREATE INDEX IF NOT EXISTS idx_cdd_canonical
    ON canonical_dedup (canonical_cdp_code);
CREATE INDEX IF NOT EXISTS idx_cdd_super_ulid
    ON canonical_dedup (run_id, super_canonical_ulid);

-- ---------------------------------------------------------------------------
-- v_canonical_deduped_draft — inspection view (NOT the served mapping)
-- Shows resolved canonical -> super-canonical from the most recent
-- canonical_dedup_run (regardless of vam_verified, since this is draft-only).
-- The served mapping (v_canonical) is NOT modified by this migration.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_canonical_deduped_draft AS
SELECT
    cd.canonical_cdp_code,
    cd.canonical_entity_ulid,
    ce.trade_name           AS canonical_trade_name,
    ce.municipality_code    AS canonical_municipality,
    ce.province_code        AS canonical_province,
    cd.super_canonical_cdp_code,
    cd.super_canonical_ulid,
    se.trade_name           AS super_canonical_trade_name,
    se.municipality_code    AS super_canonical_municipality,
    cd.component_size,
    cd.is_representative,
    cd.evidence_deep_link,
    cd.run_id
FROM canonical_dedup cd
JOIN entity ce ON ce.entity_ulid = cd.canonical_entity_ulid
JOIN entity se ON se.entity_ulid = cd.super_canonical_ulid
WHERE cd.run_id = (
    SELECT run_id
    FROM canonical_dedup_run
    ORDER BY run_at DESC
    LIMIT 1
);

-- Rollback:
-- DROP VIEW  IF EXISTS v_canonical_deduped_draft;
-- DROP TABLE IF EXISTS canonical_dedup CASCADE;
-- DROP TABLE IF EXISTS canonical_dedup_run CASCADE;
