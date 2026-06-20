-- 0050_precision_gate.sql — P09-S4: persist the precision-sampling gate (V6 / sampler.py).
--
-- Extends the Inquisition's authoritative ledger from a COUNT-quorum invariant
-- (0032 trustworthy_needs_independence) to ALSO carry the PRECISION certificate produced by
-- pipeline/inquisition/sampler.py: the blind acceptance-sample size, its RNG seed, the Wilson
-- upper bound on the defect rate, and the contract's p0 threshold. A second DB invariant makes a
-- fabricated precision impossible: a TRUSTWORTHY verdict that declares a precision contract
-- (p0_contract NOT NULL) can only be written when its defect-rate upper bound is at or below the
-- contract (ci_upper <= p0_contract). Backward-compatible: every new column is NULL on historical
-- rows, which satisfy the new CHECK trivially (no validation failure on existing data).

-- 1) Precision columns on the verdict (all nullable -> legacy verdicts unaffected).
ALTER TABLE inquisition_verdict ADD COLUMN IF NOT EXISTS precision_n  INT;
ALTER TABLE inquisition_verdict ADD COLUMN IF NOT EXISTS sample_seed  TEXT;
ALTER TABLE inquisition_verdict ADD COLUMN IF NOT EXISTS ci_upper     DOUBLE PRECISION;
ALTER TABLE inquisition_verdict ADD COLUMN IF NOT EXISTS p0_contract  DOUBLE PRECISION;

-- 2) The precision invariant (idempotent add via guard). A TRUSTWORTHY verdict UNDER a precision
--    contract must carry a defect-rate upper bound at/below the contract threshold.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'trustworthy_needs_precision'
    ) THEN
        ALTER TABLE inquisition_verdict
            ADD CONSTRAINT trustworthy_needs_precision CHECK (
                verdict <> 'TRUSTWORTHY'
                OR p0_contract IS NULL
                OR (ci_upper IS NOT NULL AND ci_upper <= p0_contract)
            );
    END IF;
END $$;

-- 3) sample_event — re-executable provenance of every precision sample (V6 Appendix A):
--    seed + exact sampled keys + plan + per-item defect scores + the CI. Re-run the seed and the
--    verdict reproduces. Append-only audit trail; never updated.
CREATE TABLE IF NOT EXISTS sample_event (
    event_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim_id        TEXT REFERENCES inquisition_claim(claim_id) ON DELETE CASCADE,
    subject_type    TEXT,
    subject_key     TEXT,
    seed            TEXT NOT NULL,
    plan            JSONB NOT NULL,
    sampled_keys    JSONB NOT NULL,
    per_item_scores JSONB,
    ci              JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sample_event_claim   ON sample_event (claim_id);
CREATE INDEX IF NOT EXISTS idx_sample_event_subject ON sample_event (subject_type, subject_key);

-- 4) verification_contract — per-subject quality gates (ODCS-shaped) that drive the sampler:
--    the p0/conf/plan + a freshness TTL. The sampler reads the contract for a subject; at zero
--    sampling budget the precision gate degrades to UNVERIFIED (not REFUTED), per V6 (P09-S5).
CREATE TABLE IF NOT EXISTS verification_contract (
    contract_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_pattern TEXT NOT NULL,
    gates           JSONB NOT NULL,
    ttl_seconds     INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_verification_contract_pattern ON verification_contract (subject_pattern);

-- The read-only inquisitor role reads the new ledgers it judges from (mirrors 0032 grants).
GRANT SELECT ON sample_event          TO cardeep_inquisitor;
GRANT SELECT ON verification_contract TO cardeep_inquisitor;

-- Rollback:
-- DROP TABLE IF EXISTS verification_contract;
-- DROP TABLE IF EXISTS sample_event;
-- ALTER TABLE inquisition_verdict DROP CONSTRAINT IF EXISTS trustworthy_needs_precision;
-- ALTER TABLE inquisition_verdict
--     DROP COLUMN IF EXISTS p0_contract, DROP COLUMN IF EXISTS ci_upper,
--     DROP COLUMN IF EXISTS sample_seed, DROP COLUMN IF EXISTS precision_n;
