-- 0032_inquisition.sql — V3 THE INQUISITION (adversarial verifier chain)
--
-- The layer ABOVE the VAM (verify.py count-quorum). Where the VAM asks "do >=2
-- paths agree on a number?", the Inquisition defaults every load-bearing claim to
-- REFUTED and forces it to survive N orthogonal skeptics that share neither source,
-- tool, cache, nor code-path with the producer (Law II — Producer Exclusion).
-- Spec: docs/architecture/verification/V3-INQUISITION.md (3 laws, 5 lenses §3,
-- independence gate §4, quorum math §5, manager router §7, denominator §6).
--
-- This migration is the TABULAR FOUNDATION (block epsilon-1): the three ledger
-- tables + the DB-enforced TRUSTWORTHY invariant. The engines (independence gate,
-- quorum), the lenses (A/B/D/E are zero-cost; C live-refetch is harvest-gated), the
-- prosecutor and the manager router land in pipeline/inquisition/ in later blocks.
--
-- PRECEDENTS (already in the schema, do not recreate):
--   * cardeep_inquisitor read-only ROLE      — 0026_verification_deep.sql
--   * denominator_estimate (Chapman/Chao2)   — 0026_verification_deep.sql
-- The coverage verdict cites the exact denominator_estimate row it relied on via the
-- denom_estimate_id FK (Director refinement: a coverage verdict with no cited
-- estimator is unauditable).
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section
-- (the trailing rollback block below is commented and stripped).

-- ---------------------------------------------------------------------------
-- 1. inquisition_claim — claims entering the Inquisition (producer-emitted)
--    The claim envelope (V3 §2.1). producer_state carries Law II's 4 dimensions.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inquisition_claim (
    claim_id        TEXT PRIMARY KEY,                 -- ULID (producer-generated)
    subject_type    TEXT NOT NULL
        CHECK (subject_type IN (
            'count','entity_field','inventory','coverage','kind','delta','denominator'
        )),
    subject_key     TEXT NOT NULL,
    claim           TEXT NOT NULL,                    -- human + machine assertion
    asserted_value  TEXT,                             -- typed value under test
    producer_state  JSONB NOT NULL,                   -- <source,tool,snapshot,code_path> (Law II)
    load_bearing    BOOLEAN NOT NULL DEFAULT TRUE,    -- only load-bearing claims get full N skeptics
    tolerance       DOUBLE PRECISION NOT NULL DEFAULT 0.005,
    evidence_uri    TEXT,                             -- defendant's exhibit (never trusted as proof)
    status          TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING','PROSECUTING','DECIDED')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The prosecutor's work queue: pending claims, oldest first.
CREATE INDEX IF NOT EXISTS idx_claim_pending
    ON inquisition_claim (created_at)
    WHERE status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_claim_subject
    ON inquisition_claim (subject_type, subject_key);

-- ---------------------------------------------------------------------------
-- 2. inquisition_skeptic — one row per skeptic (audit trail of who tested what,
--    independently). indep_distance = D(s,P) in {0..4} (V3 §4).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inquisition_skeptic (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim_id        TEXT NOT NULL
        REFERENCES inquisition_claim(claim_id) ON DELETE CASCADE,
    lens            TEXT NOT NULL
        CHECK (lens IN (
            'A_requery','B_raw_recount','C_live_refetch','D_cross_source','E_batch_hash'
        )),
    skeptic_state   JSONB NOT NULL,                   -- its <source,tool,cache,path> (+ egress for Lens C)
    indep_distance  INT NOT NULL
        CHECK (indep_distance BETWEEN 0 AND 4),
    measured_value  TEXT,
    verdict         TEXT NOT NULL
        CHECK (verdict IN ('ASSERT','REFUTE_SOFT','REFUTE_HARD','ABSTAIN')),
    confidence      DOUBLE PRECISION
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    reason          TEXT,
    evidence        JSONB,                            -- bytes/headers justifying the verdict
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_skeptic_claim ON inquisition_skeptic (claim_id);

-- ---------------------------------------------------------------------------
-- 3. inquisition_verdict — the authoritative ruling (supersedes the VAM's
--    verification_verdict for load-bearing claims, V3 §9).
--
--    The trustworthy_needs_independence CHECK makes Laws II + III a DB INVARIANT:
--    it is physically impossible to persist TRUSTWORTHY without >=2 asserting
--    skeptics, independence score >=2, and zero un-vetoed hard refutations.
--    The lie cannot be written even by a buggy prosecutor.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inquisition_verdict (
    claim_id        TEXT PRIMARY KEY
        REFERENCES inquisition_claim(claim_id) ON DELETE CASCADE,
    verdict         TEXT NOT NULL
        CHECK (verdict IN ('TRUSTWORTHY','REFUTED','INCONCLUSIVE','QUARANTINED')),
    decided_value   TEXT,
    indep_score     INT NOT NULL,                     -- INDEP (§4); must be >=2 for TRUSTWORTHY
    assert_n        INT NOT NULL DEFAULT 0,
    refute_soft_n   INT NOT NULL DEFAULT 0,
    refute_hard_n   INT NOT NULL DEFAULT 0,
    abstain_n       INT NOT NULL DEFAULT 0,
    reason_code     TEXT,                             -- routes the Manager (§7)
    denom_estimate  DOUBLE PRECISION,                 -- N_hat snapshot for coverage claims (§6)
    denom_ci_low    DOUBLE PRECISION,
    denom_estimate_id BIGINT REFERENCES denominator_estimate(id),  -- the cited estimator (auditable)
    routed_action   TEXT
        CHECK (routed_action IN ('fix','research','quarantine','escalate','none')),
    decided_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Law II + Law III as a database invariant:
    CONSTRAINT trustworthy_needs_independence
        CHECK (
            verdict <> 'TRUSTWORTHY'
            OR (indep_score >= 2 AND assert_n >= 2 AND refute_hard_n = 0)
        )
);
CREATE INDEX IF NOT EXISTS idx_inq_verdict ON inquisition_verdict (verdict);
CREATE INDEX IF NOT EXISTS idx_inq_routed
    ON inquisition_verdict (routed_action)
    WHERE routed_action <> 'none';

-- ---------------------------------------------------------------------------
-- 4. Grants — the read-only inquisitor role reads the ledger it judges from.
--    Writes are performed by the prosecutor under a writer role; the producer
--    roles have no grant here (independence by construction, V3 §2).
--    NOTE (deferred, harvest phase): Lens C live re-fetch must additionally
--    enforce egress_id(skeptic) <> egress_id(producer) — a hard CHECK to be
--    added when the live-refetch lens lands. skeptic_state already carries the
--    egress identity; the CHECK is intentionally not yet present (nothing live
--    to enforce at zero cost).
-- ---------------------------------------------------------------------------
GRANT SELECT ON inquisition_claim   TO cardeep_inquisitor;
GRANT SELECT ON inquisition_skeptic TO cardeep_inquisitor;
GRANT SELECT ON inquisition_verdict TO cardeep_inquisitor;

-- ---------------------------------------------------------------------------
-- Rollback:
-- DROP INDEX IF EXISTS idx_inq_routed;
-- DROP INDEX IF EXISTS idx_inq_verdict;
-- DROP TABLE IF EXISTS inquisition_verdict;
-- DROP INDEX IF EXISTS idx_skeptic_claim;
-- DROP TABLE IF EXISTS inquisition_skeptic;
-- DROP INDEX IF EXISTS idx_claim_subject;
-- DROP INDEX IF EXISTS idx_claim_pending;
-- DROP TABLE IF EXISTS inquisition_claim;
