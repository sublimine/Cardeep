-- 0033_evict.sql — EVICT-DELETE ledger
--
-- Adds the 'evicted' value to entity_status, the evicted_at tombstone column,
-- the capacity_ledger table (disk watermark + per-eviction reclaim tracking),
-- and the audit_eviction table (append-only, immutable via trigger).
--
-- Additive, idempotent, reversible.
-- migrate.py applies only the forward section (before the trailing Rollback block).
--
-- NOTE: ALTER TYPE ADD VALUE IF NOT EXISTS is safe inside a transaction in PG 12+
-- (including PG 16 used here).  migrate.py wraps each statement individually via
-- split_statements() so this statement runs in its own transaction — no issue.

-- ---------------------------------------------------------------------------
-- 1. Extend entity_status enum with 'evicted'
-- ---------------------------------------------------------------------------

ALTER TYPE entity_status ADD VALUE IF NOT EXISTS 'evicted';

-- ---------------------------------------------------------------------------
-- 2. Add evicted_at tombstone column to entity (nullable TIMESTAMPTZ)
-- ---------------------------------------------------------------------------

ALTER TABLE entity
  ADD COLUMN IF NOT EXISTS evicted_at TIMESTAMPTZ;

-- ---------------------------------------------------------------------------
-- 3. capacity_ledger — disk watermark + per-eviction reclaim record
--
--    One row per eviction event. Tracks raw bytes freed and vehicle counts
--    deleted so the Director can monitor disk reclaim over time.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS capacity_ledger (
    id               BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cdp_code         TEXT        NOT NULL,
    vehicles_deleted INTEGER     NOT NULL DEFAULT 0,
    raw_bytes_freed  BIGINT      NOT NULL DEFAULT 0,
    disk_free_before BIGINT,                         -- bytes free before LRU evict
    disk_free_after  BIGINT,                         -- bytes free after LRU evict
    evicted_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT capacity_ledger_cdp_code_check
        CHECK (cdp_code ~ '^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$')
);

CREATE INDEX IF NOT EXISTS idx_capacity_ledger_cdp
    ON capacity_ledger (cdp_code, evicted_at DESC);

-- ---------------------------------------------------------------------------
-- 4. audit_eviction — append-only eviction audit log
--
--    Immutable: BEFORE UPDATE/DELETE trigger raises, mirroring verdict_audit
--    pattern from migration 0026.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_eviction (
    id               BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cdp_code         TEXT        NOT NULL,
    evicted_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason           TEXT        NOT NULL,
    actor            TEXT        NOT NULL DEFAULT 'director',
    vehicles_deleted INTEGER     NOT NULL DEFAULT 0,
    raw_bytes_freed  BIGINT      NOT NULL DEFAULT 0,
    CONSTRAINT audit_eviction_cdp_code_check
        CHECK (cdp_code ~ '^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$')
);

CREATE INDEX IF NOT EXISTS idx_audit_eviction_cdp
    ON audit_eviction (cdp_code, evicted_at DESC);

-- Immutability trigger function (mirrors cdp_audit_immutable from 0026)
CREATE OR REPLACE FUNCTION audit_eviction_immutable() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit_eviction is append-only (attempted % on id %)', TG_OP, OLD.id;
END $$;

-- Guard against UPDATE
DROP TRIGGER IF EXISTS trg_audit_eviction_noupd ON audit_eviction;
CREATE TRIGGER trg_audit_eviction_noupd
    BEFORE UPDATE OR DELETE ON audit_eviction
    FOR EACH ROW EXECUTE FUNCTION audit_eviction_immutable();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_audit_eviction_noupd ON audit_eviction;
-- DROP FUNCTION IF EXISTS audit_eviction_immutable();
-- DROP INDEX IF EXISTS idx_audit_eviction_cdp;
-- DROP TABLE IF EXISTS audit_eviction;
-- DROP INDEX IF EXISTS idx_capacity_ledger_cdp;
-- DROP TABLE IF EXISTS capacity_ledger;
-- ALTER TABLE entity DROP COLUMN IF EXISTS evicted_at;
-- -- Note: removing an enum value requires rebuilding the type; document as manual step.
-- -- ALTER TYPE entity_status ... (no IF NOT EXISTS equivalent for DROP VALUE in PG 16)
