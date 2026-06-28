-- 0067_country_campaign.sql — country-autopilot campaign ledger + append-only state-machine audit.
--
-- PROBLEM: the country-autopilot orchestrator (Phase E, plans/country-autopilot/01-ARCHITECTURE.md)
-- drives each country through the onboarding lifecycle of
-- docs/generic-engine-bible/COVER-NEW-COUNTRY.md:
--     REGISTERED -> KNOW_COUNTRY -> BOOTSTRAPPED -> IN_COVERAGE -> SEALED   (SEALED terminal)
-- ...but nothing persists WHERE each country is in that lifecycle, nor an audit trail of how it
-- got there. Without it the loop cannot resume, supervise, or prove progress.
--
-- SOLUTION: two tables, mirroring the gestion_item / gestion_transition pair (0031):
--   country_campaign            — one row per country (PK country_code); the current lifecycle
--                                 state + a free-form detail jsonb (dossier pointers, gate notes).
--                                 state defaults to REGISTERED.
--   country_campaign_transition — append-only audit of every state change (from/to/actor/note),
--                                 the history that IS the proof (never UPDATEd or DELETEd).
--
-- STATE MACHINE (pipeline/autopilot/state.py is the code mirror that enforces the EDGES):
--   REGISTERED -> KNOW_COUNTRY -> BOOTSTRAPPED -> IN_COVERAGE -> SEALED  (SEALED terminal).
--   The state CHECK below pins the 5 legal STATES; the code state machine rejects illegal EDGES
--   (skips, regressions, leaving SEALED) by raising CampaignTransitionError.
--
-- KEY INVARIANTS:
--   1. country_code PK — one campaign per country; idempotent register via ON CONFLICT DO NOTHING.
--   2. state CHECK constrains the column to the 5 lifecycle states.
--   3. country_campaign_transition is append-only — no row is ever updated or deleted.
--
-- ES BYTE-IDENTICAL: both tables are NEW and EMPTY. No existing census row is read or written and
-- no foreign key touches the ES backbone, so single-tenant ES behaviour is 100% preserved. ES is
-- the hand-built incumbent and is NOT auto-registered here; a future increment MAY backfill an ES
-- campaign row (in SEALED) if the orchestrator needs one — additive and out of scope for this spine.
--
-- NON-DESTRUCTIVE: additive, idempotent (CREATE TABLE / INDEX IF NOT EXISTS), reversible. The
-- runner (scripts/migrate.py) strips everything from the LAST rollback marker onward, so that
-- marker appears exactly once in this file — at the bottom.

-- ---------------------------------------------------------------------------
-- 1. country_campaign — one campaign per country, current lifecycle state.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS country_campaign (
    country_code  CHAR(2) PRIMARY KEY,

    -- Lifecycle state (COVER-NEW-COUNTRY.md). DEFAULT REGISTERED == a freshly-born campaign.
    state         TEXT NOT NULL DEFAULT 'REGISTERED' CHECK (state IN (
                    'REGISTERED', 'KNOW_COUNTRY', 'BOOTSTRAPPED',
                    'IN_COVERAGE', 'SEALED')),

    -- Free-form campaign detail: dossier pointers, gate (PENDIENTE-OWNER) notes, audit context.
    detail        JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 2. country_campaign_transition — append-only state-machine audit trail.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS country_campaign_transition (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_code  CHAR(2) NOT NULL REFERENCES country_campaign(country_code) ON DELETE CASCADE,
    from_state    TEXT,               -- NULL on the initial REGISTERED (birth) transition
    to_state      TEXT NOT NULL,
    actor         TEXT NOT NULL,      -- 'autopilot' | 'owner' | 'system' | ...
    note          TEXT,
    detail        JSONB,
    at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Efficient lookup of a campaign's full transition history in order.
CREATE INDEX IF NOT EXISTS idx_country_campaign_transition_cc
    ON country_campaign_transition (country_code, at);

-- Rollback:
-- DROP TABLE IF EXISTS country_campaign_transition;
-- DROP TABLE IF EXISTS country_campaign;
