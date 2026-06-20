-- 0049_discovery_splink_cluster.sql
-- Splink probabilistic cross-source merge (§V6) feeding the exhaustiveness MSE.
--
-- Splink (Fellegi-Sunter, DuckDB backend) links dealer entities across sources
-- by name+municipality(+phone+website+geo). Its clusters collapse more
-- cross-source duplicates than the existing deterministic dedup, raising the
-- capture-recapture overlap m per stratum -> tighter denominator CI.
--
-- This is an ADDITIVE overlay table, owned by pipeline/exhaustiveness/. It does
-- not alter entity / entity_cluster / v_dealer_resolved.

BEGIN;

CREATE TABLE IF NOT EXISTS discovery_splink_cluster (
    entity_ulid     text NOT NULL,
    splink_cluster  text NOT NULL,          -- canonical cluster id (lowest entity_ulid)
    match_weight    double precision,        -- representative link strength
    build_run_id    text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (entity_ulid, build_run_id)
);

CREATE INDEX IF NOT EXISTS ix_discovery_splink_cluster
    ON discovery_splink_cluster (build_run_id, splink_cluster);

COMMIT;
