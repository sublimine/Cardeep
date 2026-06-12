-- 0004_verification_health.sql — VAM verdicts + source health + alerts (resilience)
-- Additive, idempotent, reversible.

-- The judge of "done": every trustworthy claim needs quorum >=2 orthogonal paths.
CREATE TABLE IF NOT EXISTS verification_verdict (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_type      TEXT NOT NULL,               -- 'entity' | 'platform' | 'count' | ...
    subject_key       TEXT NOT NULL,               -- cdp_code / domain / source_key
    claim             TEXT NOT NULL,               -- what is being asserted
    primary_value     TEXT,
    primary_path      TEXT,                        -- how the primary value was produced
    verifier_paths    JSONB,                       -- orthogonal verification methods
    independent_values JSONB,                      -- values each path produced
    divergence        DOUBLE PRECISION,            -- spread between paths
    verdict           TEXT NOT NULL
        CHECK (verdict IN ('TRUSTWORTHY','REFUTED','UNVERIFIED')),
    evidence          TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_verdict_subject ON verification_verdict (subject_type, subject_key);
CREATE INDEX IF NOT EXISTS idx_verdict_verdict ON verification_verdict (verdict);

-- Watchdog per source: feeds exact-origin alerts + auto-repair (F7).
CREATE TABLE IF NOT EXISTS source_health (
    source_key        TEXT PRIMARY KEY,
    last_ok           TIMESTAMPTZ,
    last_fail         TIMESTAMPTZ,
    consecutive_fails INT NOT NULL DEFAULT 0,
    status            TEXT NOT NULL DEFAULT 'unknown'
        CHECK (status IN ('healthy','degraded','down','unknown'))
);

-- Alerts with exact origin (mandate: "salta una alerta con el origen exacto").
CREATE TABLE IF NOT EXISTS alert (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    origin      TEXT NOT NULL,                     -- exact source_key / entity cdp_code / phase
    severity    TEXT NOT NULL DEFAULT 'info'
        CHECK (severity IN ('info','warning','critical')),
    message     TEXT NOT NULL,
    payload     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_alert_origin ON alert (origin);
CREATE INDEX IF NOT EXISTS idx_alert_unresolved ON alert (created_at) WHERE resolved_at IS NULL;

-- Rollback:
-- DROP TABLE IF EXISTS alert;
-- DROP TABLE IF EXISTS source_health;
-- DROP TABLE IF EXISTS verification_verdict;
