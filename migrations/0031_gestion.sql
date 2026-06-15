-- 0031_gestion.sql — V4 Gestionador: managed-item ledger + state-machine audit.
--
-- PROBLEM: CARDEEP has no mechanism to track detected anomalies (lies, gaps,
-- fabrication events) as managed work items, route them to resolution lanes,
-- enforce quarantine of subjects whose integrity is in doubt, or record the
-- audit trail of every state transition. Detectors can fire but their output
-- disappears; a lie can be re-detected 50 times with no closure.
--
-- SOLUTION: Two tables per V4-GESTIONADOR.md §2:
--   gestion_item       — one ticket per (detector, subject, time-bucket).
--                        Carries severity, lane, state, measured evidence,
--                        baseline expectation, quarantine flag, and the
--                        verification_verdict FK that is required for closure.
--   gestion_transition — append-only audit of every state change (who/when/why).
--
-- STATE MACHINE (§4.2):
--   OPEN → ROUTED → IN_PROGRESS → REVERIFYING → RESOLVED
--   Any state → QUARANTINED (if quarantines=TRUE; serving frozen immediately)
--   REVERIFYING → REOPENED (if independent recheck fails)
--   ESCALATE_* items: OPEN → ROUTED → ESCALATED → IN_PROGRESS | WONT_FIX
--   RESOLVED can REOPEN on regression.
--
-- LANES (§4.1): AUTO_FIX | RESEARCH | QUARANTINE | ESCALATE_GASTO | ESCALATE_OWNER
--
-- DETECTORS (§3): count_inflation | silent_cap | field_loss | staleness |
--                 fabrication | coverage_gap | price_trap |
--                 geo_resolution_drift | classifier_drift
--
-- KEY INVARIANTS:
--   1. dedupe_key UNIQUE: one open item per (detector, subject, time-bucket).
--      Re-detection updates measured + appends a transition; never opens a dupe.
--   2. quarantines=TRUE means subject is excluded from every served surface
--      (enforced via servable_entity view, defined in §4.3).
--   3. RESOLVED requires verdict_id FK — no independent recheck = no closure.
--   4. gestion_transition is append-only; no rows are ever updated or deleted
--      (the history IS the proof).
--
-- NON-DESTRUCTIVE: additive, IF NOT EXISTS everywhere.
-- See Rollback block at end of file.

-- ---------------------------------------------------------------------------
-- 1. gestion_item — the managed ticket
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gestion_item (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Detector identity
    detector      TEXT NOT NULL,
    -- Valid values (V4 §3.10):
    --   'count_inflation' | 'silent_cap' | 'field_loss' | 'staleness' |
    --   'fabrication'     | 'coverage_gap' | 'price_trap' |
    --   'geo_resolution_drift' | 'classifier_drift'

    -- Subject coordinates
    subject_type  TEXT NOT NULL,
    -- 'entity' | 'source' | 'segment' | 'field' | 'geo' | 'model' | 'vehicle'
    subject_key   TEXT NOT NULL,
    -- cdp_code | source_key | 'garaje@28' | vehicle_ulid | ...

    -- Severity & anomaly score
    severity      TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    score         DOUBLE PRECISION,   -- detector-normalised 0..1 anomaly score

    -- Evidence
    measured      JSONB NOT NULL,     -- the numbers / stats that fired the detector
    baseline      JSONB,              -- the expectation / threshold it diverged from

    -- Routing
    lane          TEXT NOT NULL CHECK (lane IN (
                    'AUTO_FIX', 'RESEARCH', 'QUARANTINE',
                    'ESCALATE_GASTO', 'ESCALATE_OWNER')),

    -- State machine (V4 §4.2)
    state         TEXT NOT NULL DEFAULT 'OPEN' CHECK (state IN (
                    'OPEN', 'ROUTED', 'IN_PROGRESS', 'REVERIFYING',
                    'RESOLVED', 'QUARANTINED', 'ESCALATED',
                    'WONT_FIX', 'REOPENED')),

    -- Quarantine flag — the teeth (V4 §4.3)
    quarantines   BOOLEAN NOT NULL DEFAULT FALSE,
    -- When TRUE and closed_at IS NULL, the publish gate must exclude subject_key.

    -- Closure proof (V4 §4.2 — "No verdict_id → no RESOLVED")
    verdict_id    BIGINT REFERENCES verification_verdict(id),

    -- Timestamps & SLA
    opened_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    sla_due       TIMESTAMPTZ,        -- opened_at + lane-specific SLA (§4.4)
    closed_at     TIMESTAMPTZ,
    closed_reason TEXT,

    -- Idempotency key (V4 §2): detector|subject_key|time_bucket
    -- One open item per recurring condition; re-fires append transitions only.
    dedupe_key    TEXT NOT NULL,
    UNIQUE (dedupe_key)
);

-- Hot query: open items by state
CREATE INDEX IF NOT EXISTS idx_gestion_open
    ON gestion_item (state)
    WHERE closed_at IS NULL;

-- Quarantine gate lookup: subjects with an open quarantining item
CREATE INDEX IF NOT EXISTS idx_gestion_quar
    ON gestion_item (subject_type, subject_key)
    WHERE quarantines AND closed_at IS NULL;

-- SLA breach sweep
CREATE INDEX IF NOT EXISTS idx_gestion_sladue
    ON gestion_item (sla_due)
    WHERE closed_at IS NULL;

-- Dashboard: open items by detector + severity
CREATE INDEX IF NOT EXISTS idx_gestion_detector
    ON gestion_item (detector, severity)
    WHERE closed_at IS NULL;

-- ---------------------------------------------------------------------------
-- 2. gestion_transition — append-only state-machine audit trail
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gestion_transition (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id     BIGINT NOT NULL REFERENCES gestion_item(id) ON DELETE CASCADE,
    from_state  TEXT,               -- NULL on initial OPEN transition
    to_state    TEXT NOT NULL,
    actor       TEXT NOT NULL,
    -- 'detector' | 'gestionador' | 'auto_fix:<job>' | 'owner' | 'system'
    note        TEXT,
    payload     JSONB,
    at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Efficient lookup of all transitions for a given item
CREATE INDEX IF NOT EXISTS idx_gtrans_item
    ON gestion_transition (item_id, at);

-- ---------------------------------------------------------------------------
-- 3. servable_entity / servable_vehicle — publish-gate views (V4 §4.3)
--
-- The API reads through these views, never the raw tables.
-- A subject is SERVABLE iff it has no open, quarantining gestion_item.
-- This is a database invariant: the instant a quarantining item opens,
-- the subject vanishes from every served surface — mechanically, not
-- by promise.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW servable_entity AS
SELECT e.*
FROM entity e
WHERE NOT EXISTS (
    SELECT 1
    FROM gestion_item g
    WHERE g.quarantines
      AND g.closed_at IS NULL
      AND g.subject_type = 'entity'
      AND g.subject_key  = e.cdp_code
);

CREATE OR REPLACE VIEW servable_vehicle AS
SELECT v.*
FROM vehicle v
WHERE NOT EXISTS (
    SELECT 1
    FROM gestion_item g
    WHERE g.quarantines
      AND g.closed_at IS NULL
      AND g.subject_type = 'vehicle'
      AND g.subject_key  = v.vehicle_ulid::TEXT
);

-- Rollback:
-- DROP VIEW IF EXISTS servable_vehicle;
-- DROP VIEW IF EXISTS servable_entity;
-- DROP TABLE IF EXISTS gestion_transition;
-- DROP TABLE IF EXISTS gestion_item;
