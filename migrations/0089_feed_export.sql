-- 0089_feed_export.sql — 07-marketing F3: traceability ledger for C6 feed exports
-- (plans/cardeep-omni/07-marketing.md S5.2).
--
-- The FILE itself is never stored (doctrine of capacity, cf. capacity_ledger in
-- 0033_evict.sql) — GET /entities/{cdp}/feed/{target} generates the feed content LIVE
-- from `vehicle`/`entity` on every request (pipeline/marketing/feeds.py's deterministic
-- templates) and this table only records the metadata + a content_hash for integrity
-- verification, so a dealer or an auditor can confirm "the file I downloaded is the one
-- Cardeep actually generated" without Cardeep hoarding a copy of every export forever.
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

CREATE TABLE IF NOT EXISTS feed_export (
    export_ulid     TEXT PRIMARY KEY,
    entity_ulid     TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE,
    target          TEXT NOT NULL
        CHECK (target IN ('google_vehicle_ads', 'meta_aia', 'schema_org_jsonld')),
    item_count      INTEGER NOT NULL,
    valid_count     INTEGER NOT NULL,
    invalid_report  JSONB NOT NULL DEFAULT '[]'::jsonb,
    content_hash    TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_feed_export_entity ON feed_export (entity_ulid, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feed_export_target ON feed_export (target, created_at DESC);

-- Rollback:
-- DROP TABLE IF EXISTS feed_export;
