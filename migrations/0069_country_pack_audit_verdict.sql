-- 0069_country_pack_audit_verdict.sql — Fase D persistence: the AUTO-AUDITOR's append-only ledger.
--
-- PROBLEM: pipeline/autopilot/auditor.py (Fase D, plans/country-autopilot/01-ARCHITECTURE.md — the
-- N0..N4 table + the HONEST FRONTIER) computes a pure PackAuditVerdict over a PROPOSED
-- countries/<CC>/ pack: five sub-verdicts (N0 Estructura, N1 Ortogonalidad, N2 Credibilidad,
-- N3 VAM-quorum, N4 Cobertura) + an overall BUILD decision and a weakest-link confidence. Until now
-- the verdict evaporated after the call — NOTHING persisted WHAT the auditor ruled, so the
-- orchestrator could not resume, supervise, prove progress, or show the owner WHY a pack was
-- approved / rejected / escalated. The auditor's own docstring named this table as the LATER
-- increment ("Persistence (country_pack_audit_verdict) is a LATER increment").
--
-- SOLUTION: one append-only ledger, country_pack_audit_verdict, mirroring inquisition_verdict (0032)
-- and country_campaign_transition (0067) — the history IS the proof. persist_verdict() (auditor.py)
-- writes one row PER LEVEL (N0..N4) plus one OVERALL summary row per audit run; rows are never
-- UPDATEd or DELETEd, so re-auditing a country APPENDS a fresh batch and the full audit history is
-- reconstructable in order via the (country_code, created_at) index.
--
-- COLUMN SEMANTICS (one row = one level's sub-verdict OR the overall summary):
--   level        — 'N0'..'N4' for a level's sub-verdict; 'OVERALL' for the pack summary row.
--   sub_verdict  — THIS row's own ruling (LevelVerdict.decision; on OVERALL == the pack decision).
--   score        — THIS row's own confidence in [0,1] (LevelVerdict.score; on OVERALL == confidence).
--   reason_code  — THIS row's reason (NULL on a clean APRUEBA level).
--   decision     — the PACK's overall BUILD decision, DENORMALISED onto EVERY row of the run, so a
--                  single row tells the headline outcome and `WHERE decision='RECHAZA'` finds every
--                  fail-closed run without a self-join. (The N2 live-gate is N2's own sub_verdict.)
-- The three verdict values are the auditor's Decision enum: APRUEBA / RECHAZA / ESCALA. The CHECKs
-- pin the level vocabulary and the verdict vocabulary and bound score to [0,1], so a malformed
-- verdict is physically unpersistable — the Inquisition's DB-invariant doctrine (0032).
--
-- NO FK (decoupled by design): a pack is audited from a STAGED / temp tree (auditor.audit_pack
-- accepts any pack_dir) potentially BEFORE its country_campaign row exists, so this ledger does NOT
-- REFERENCE country_campaign — the audit trail must be writable for a country not yet registered.
--
-- ES BYTE-IDENTICAL: the table is NEW and EMPTY. No existing census / entity / orchestration row is
-- read or written and no FK touches any ES backbone, so single-tenant ES behaviour is 100%
-- preserved. ES (the hand-built incumbent) is never auto-audited here.
--
-- NON-DESTRUCTIVE: additive, idempotent (CREATE TABLE / INDEX IF NOT EXISTS), reversible. The runner
-- (scripts/migrate.py) strips everything from the LAST rollback marker onward; that marker appears
-- exactly ONCE, at the foot of this file (this header only DESCRIBES reversibility, it carries no
-- marker, so the forward DDL is never truncated).

-- ---------------------------------------------------------------------------
-- 1. country_pack_audit_verdict — append-only auto-auditor ledger (Fase D).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS country_pack_audit_verdict (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_code  CHAR(2) NOT NULL,

    -- Which level this row records: the five audit levels, or the pack-level summary.
    level         TEXT NOT NULL CHECK (level IN ('N0', 'N1', 'N2', 'N3', 'N4', 'OVERALL')),

    -- This row's own ruling (the auditor's Decision enum).
    sub_verdict   TEXT NOT NULL CHECK (sub_verdict IN ('APRUEBA', 'RECHAZA', 'ESCALA')),

    -- This row's own confidence in [0,1] (a level's score; the pack confidence on the OVERALL row).
    score         NUMERIC NOT NULL CHECK (score >= 0 AND score <= 1),

    -- This row's reason code (NULL on a clean APRUEBA level).
    reason_code   TEXT,

    -- The PACK's overall BUILD decision, denormalised onto every row of the audit run.
    decision      TEXT NOT NULL CHECK (decision IN ('APRUEBA', 'RECHAZA', 'ESCALA')),

    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Efficient lookup of a country's full audit history in chronological order.
CREATE INDEX IF NOT EXISTS idx_country_pack_audit_verdict_cc
    ON country_pack_audit_verdict (country_code, created_at);

-- Rollback:
-- DROP INDEX IF EXISTS idx_country_pack_audit_verdict_cc;
-- DROP TABLE IF EXISTS country_pack_audit_verdict;
