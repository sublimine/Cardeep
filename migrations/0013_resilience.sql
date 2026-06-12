-- 0013_resilience.sql — S-HEALTH circuit breaker + harvest audit + auto-repair ledger.
-- Additive, idempotent, reversible. (06-RESILIENCE-OPS §5/§6/§10; MASTER_PLAN C-1 row 0013.)
--
-- This is the durable substrate that makes the mandate true: "if a source fails, an
-- alert fires with the EXACT origin, it self-repairs, and Cardeep never falls." It
-- EXTENDS the live 0004 tables (source_health, alert) — it never recreates them. The
-- breaker state must survive a restart (06 §9.4 self-recovery), the harvest_run audit
-- is the throughput/error golden signal the §0 incident lacked, and repair_attempt is
-- the auto-repair evidence trail (law #6: every repair is persisted evidence).
--
-- Column shapes follow MASTER_PLAN §C-1 (binding decision; where pillar 06 §10's draft
-- 0005 disagrees on naming, the plan wins): cooldown_until (not cool_until),
-- consecutive_fails on the breaker, harvest_run{ok bool, rows, error, http_status},
-- repair_attempt{detected_reason, action, succeeded bool, created_at}.

-- Per-source circuit breaker state (must survive restart; 06 §5/§9.4).
-- One breaker per source_key: a tripped breaker for one source never touches another
-- (bulkhead, law #5). 'open' = quarantined, scheduler skips until cooldown_until.
CREATE TABLE IF NOT EXISTS source_breaker (
    source_key        TEXT PRIMARY KEY,
    state             TEXT NOT NULL DEFAULT 'closed'
        CHECK (state IN ('closed', 'open', 'half_open')),
    consecutive_fails INT NOT NULL DEFAULT 0,    -- trips the breaker at the threshold (§5.2)
    opened_at         TIMESTAMPTZ,               -- when it last tripped (cool-down ETA after restart)
    cooldown_until    TIMESTAMPTZ                -- scheduler skips this source until now() >= this
);

-- Per-harvest audit + the throughput/error golden signal (06 §8.1). One row per run:
-- the audit trail the 138-dealer incident lacked (it only printed to stdout, §0.3).
CREATE TABLE IF NOT EXISTS harvest_run (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key   TEXT NOT NULL,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ,
    ok           BOOLEAN NOT NULL,              -- the classified run outcome (true=OK, false=fail)
    rows         INT,                           -- records produced by the run (NULL when unknown)
    error        TEXT,                          -- failure detail when ok=false (NULL on success)
    http_status  INT                            -- last HTTP status when applicable (NULL otherwise)
);
CREATE INDEX IF NOT EXISTS idx_harvest_run_source ON harvest_run (source_key, started_at DESC);

-- Auto-repair audit: every classification + the action taken + whether it worked (06 §6).
-- 'action' is the closed vocabulary of the repair ladder; 'detected_reason' is the typed
-- failure signal the loop classified (403/blocked, fields-null/drift, ban, unknown...).
CREATE TABLE IF NOT EXISTS repair_attempt (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key      TEXT NOT NULL,
    detected_reason TEXT NOT NULL,              -- the classified failure cause (the "why")
    action          TEXT NOT NULL               -- the repair the loop chose (the "what")
        CHECK (action IN ('refingerprint', 'escalate_tier', 're_receta',
                          'quarantine', 'escalate_owner')),
    succeeded       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_repair_attempt_source ON repair_attempt (source_key, created_at DESC);

-- Per-source tuning lives WITH the source, not hardcoded (06 §2.2/§7.1). is_tier1 carries
-- the stricter Tier-1 health/alert track; tuning is a free JSONB knob bag (down_at,
-- host_rps_cap, max_concurrency, cooldown_sec, fail_threshold...). Additive to the live
-- 0004 source_health — the resilience layer CONSUMES that table and only ADDS columns.
ALTER TABLE source_health ADD COLUMN IF NOT EXISTS is_tier1 BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE source_health ADD COLUMN IF NOT EXISTS tuning JSONB;

-- Rollback:
-- ALTER TABLE source_health DROP COLUMN IF EXISTS tuning;
-- ALTER TABLE source_health DROP COLUMN IF EXISTS is_tier1;
-- DROP TABLE IF EXISTS repair_attempt;
-- DROP TABLE IF EXISTS harvest_run;
-- DROP TABLE IF EXISTS source_breaker;
