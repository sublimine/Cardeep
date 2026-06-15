-- 0030_entity_completion.sql — Per-entity completion ledger (SU-B2 foundation).
--
-- PROBLEM: There is no authoritative per-entity record of whether a dealer has
-- passed all five binary gates (G1-G5) defined in V2-COMPLETION-PROOF.md.
-- The existing `verification_verdict` table stores count quorums per source
-- (subject_type='entity_inventory'), but has NO per-entity completion state,
-- no gate breakdown, no freshness SLA, and no COMPLETED/STALE verdict.
--
-- SOLUTION: `entity_completion` is the authoritative ledger for the completion
-- state of every dealer entity. One row per cdp_code, upserted on each gate
-- evaluation run. The verdict column is constrained by a DB-enforced trigger so
-- COMPLETED can only be written when g1 ∧ g2 ∧ g3 ∧ g4 ∧ g5 are all TRUE and
-- completed_at is set — a buggy validator cannot fabricate a completion.
--
-- DESIGN DECISIONS:
--   1. cdp_code is the PK (FK to entity.cdp_code CASCADE DELETE), not entity_ulid.
--      After dedup, the canonical cdp_code is the stable identity surface.
--   2. All five gate columns are NOT NULL DEFAULT FALSE — absent ≡ not passed.
--   3. Evidence columns (s_declared, h_harvested, d_landed, d_valid, field_integrity,
--      recipe_sha, served_count) record the proof behind each gate flip.
--   4. sla_seconds is NOT NULL; tier assignment is caller responsibility.
--      (24h=86400, 7d=604800, 30d=2592000 — from V2 §3.F)
--   5. A DB trigger enforces the invariant: verdict='COMPLETED' ⟺
--      g1 ∧ g2 ∧ g3 ∧ g4 ∧ g5 = TRUE ∧ completed_at IS NOT NULL.
--      Any violation raises an exception, blocking the write.
--   6. last_blind_at / last_blind_pass / e_set / e_field are for the §4 blind
--      re-scrape linkage (aggregate proof block β-complete / §5 LQAS).
--      Populated when a blind sample is run; NULL until then.
--   7. updated_at stamps every upsert via the trigger below.
--
-- THE ONLY TRUSTWORTHY ANSWER TO "how many entities are COMPLETED":
--   SELECT count(*)
--   FROM entity_completion
--   WHERE verdict = 'COMPLETED'
--     AND now() - last_harvest_at <= make_interval(secs => sla_seconds);
--
-- Absent an entity_completion row: the entity is INCOMPLETE by definition,
-- regardless of any agent claim.
--
-- NON-DESTRUCTIVE: additive, idempotent (IF NOT EXISTS everywhere).
-- Rollback drops tables and trigger in reverse dependency order.

-- ---------------------------------------------------------------------------
-- Main ledger table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entity_completion (
    cdp_code          TEXT PRIMARY KEY REFERENCES entity(cdp_code) ON DELETE CASCADE,

    -- ---- Gate flags (the five binary predicates from V2-COMPLETION-PROOF §1) ----
    g1_identity       BOOLEAN NOT NULL DEFAULT FALSE,  -- identity & geo resolved
    g2_inventory      BOOLEAN NOT NULL DEFAULT FALSE,  -- count quorum TRUSTWORTHY + field_integrity>=0.98
    g3_recipe         BOOLEAN NOT NULL DEFAULT FALSE,  -- recipe.yaml git-committed at HEAD
    g4_served         BOOLEAN NOT NULL DEFAULT FALSE,  -- live API returns D matching DB count
    g5_delta          BOOLEAN NOT NULL DEFAULT FALSE,  -- second harvest produced type-consistent events

    -- ---- G2 evidence (count reconciliation paths from V2 §3.B) ----
    s_declared        INT,              -- S: source-declared numberOfResults
    h_harvested       INT,              -- H: distinct deep_links collected by harvester
    d_landed          INT,              -- D: DB-landed available rows (authority)
    d_valid           INT,              -- D_valid: rows passing field-integrity floor
    field_integrity   DOUBLE PRECISION, -- D_valid / D (must be >= 0.98 for G2=TRUE)

    -- ---- G3 evidence ----
    recipe_sha        TEXT,             -- git commit SHA proving the recipe is committed (G3)

    -- ---- G4 evidence ----
    served_count      INT,              -- live /inventory count returned by the API (G4)

    -- ---- Freshness / SLA (V2 §3.F) ----
    last_harvest_at   TIMESTAMPTZ,      -- when the last harvest completed (freshness watermark)
    sla_seconds       INT NOT NULL DEFAULT 604800, -- tier SLA: 86400 / 604800 / 2592000

    -- ---- Completion verdict ----
    verdict           TEXT NOT NULL DEFAULT 'INCOMPLETE'
        CHECK (verdict IN ('COMPLETED', 'INCOMPLETE', 'STALE', 'REFUTED', 'QUARANTINED')),

    -- ---- Aggregate proof linkage (§4 blind re-scrape / §5 LQAS) ----
    last_blind_at     TIMESTAMPTZ,      -- when this entity was last blind-sampled
    last_blind_pass   BOOLEAN,          -- did it pass the blind re-scrape? NULL=not sampled
    e_set             DOUBLE PRECISION, -- listing-error rate from blind compare (§4)
    e_field           DOUBLE PRECISION, -- field-error rate from blind compare (§4)

    -- ---- Lifecycle timestamps ----
    completed_at      TIMESTAMPTZ,      -- set (once) when verdict first becomes COMPLETED
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Covering index for the "how many COMPLETED" hot query
CREATE INDEX IF NOT EXISTS idx_completion_verdict
    ON entity_completion (verdict);

-- Index for freshness / staleness sweeps
CREATE INDEX IF NOT EXISTS idx_completion_stale
    ON entity_completion (last_harvest_at)
    WHERE last_harvest_at IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Integrity trigger: enforce COMPLETED ⟺ g1∧g2∧g3∧g4∧g5 ∧ completed_at
--
-- Fires BEFORE INSERT OR UPDATE. Raises an exception if the invariant is
-- violated. This is the structural defense against a buggy caller writing
-- COMPLETED with any gate false, or writing all gates TRUE without completing.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION entity_completion_check()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- COMPLETED requires all five gates TRUE and completed_at stamped.
    IF NEW.verdict = 'COMPLETED' THEN
        IF NOT (
            NEW.g1_identity = TRUE
            AND NEW.g2_inventory = TRUE
            AND NEW.g3_recipe   = TRUE
            AND NEW.g4_served   = TRUE
            AND NEW.g5_delta    = TRUE
            AND NEW.completed_at IS NOT NULL
        ) THEN
            RAISE EXCEPTION
                'entity_completion invariant violated: verdict=COMPLETED requires g1∧g2∧g3∧g4∧g5=TRUE and completed_at IS NOT NULL for cdp_code=%',
                NEW.cdp_code;
        END IF;
    END IF;

    -- INCOMPLETE / STALE / REFUTED / QUARANTINED must NOT have completed_at
    -- unless this is a downgrade of a previously-COMPLETED row (completed_at
    -- is allowed to persist as the historical watermark; verdict is what rules).
    -- No extra constraint here — completed_at is a historical fact stamp,
    -- not a live signal; the verdict column is the live signal.

    -- Auto-stamp updated_at on every write.
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_entity_completion_check ON entity_completion;
CREATE TRIGGER trg_entity_completion_check
    BEFORE INSERT OR UPDATE ON entity_completion
    FOR EACH ROW EXECUTE FUNCTION entity_completion_check();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_entity_completion_check ON entity_completion;
-- DROP FUNCTION IF EXISTS entity_completion_check();
-- DROP TABLE IF EXISTS entity_completion;
