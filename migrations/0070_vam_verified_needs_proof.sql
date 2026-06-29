-- 0070_vam_verified_needs_proof.sql — vam_verified=TRUE requires a real proof verdict (T1.1, road-to-13)
--
-- canonical_dedup_run.vam_verified is the flag that makes a run SERVED (v_dealer_resolved reads the
-- latest vam_verified=TRUE run, ORDER BY run_id DESC). It was a MANUAL boolean with NO check: a
-- human/script could set it TRUE without the run ever passing quorum (adversarial review #1 — the
-- "invariantes mecánicos VAM" finding). The column vam_verdict_id already exists (no backfill of the
-- column); this makes the real requirement a DB INVARIANT — vam_verified=TRUE only when vam_verdict_id
-- references a TRUSTWORTHY verification_verdict with quorum_n>=2.
--
-- Mirrors EXACTLY pipeline.identity.vam_gate.vam_verified_allowed (the tested pure single-source-of-
-- truth, tests/test_vam_gate.py) and the gestion_item RESOLVED proof (0036). Forward invariant only
-- (no backfill of existing rows — additive, idempotent, reversible). migrate.py applies the forward
-- section; the Rollback block is stripped.

CREATE OR REPLACE FUNCTION cardeep_vam_verified_needs_proof() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_verdict text; v_quorum int;
BEGIN
  IF NEW.vam_verified AND (TG_OP = 'INSERT' OR OLD.vam_verified IS DISTINCT FROM TRUE) THEN
    IF NEW.vam_verdict_id IS NULL THEN
      RAISE EXCEPTION 'canonical_dedup_run % cannot be vam_verified without vam_verdict_id (no proof)',
        NEW.run_id USING ERRCODE = 'restrict_violation';
    END IF;
    SELECT verdict, quorum_n INTO v_verdict, v_quorum
      FROM verification_verdict WHERE id = NEW.vam_verdict_id;
    IF v_verdict IS DISTINCT FROM 'TRUSTWORTHY' OR COALESCE(v_quorum, 0) < 2 THEN
      RAISE EXCEPTION 'canonical_dedup_run % vam_verified needs a TRUSTWORTHY verdict with quorum_n>=2; '
                      'vam_verdict_id % is verdict=% quorum_n=%',
        NEW.run_id, NEW.vam_verdict_id, COALESCE(v_verdict, '<missing>'), COALESCE(v_quorum, 0)
        USING ERRCODE = 'restrict_violation';
    END IF;
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_canonical_dedup_vam_proof ON canonical_dedup_run;
CREATE TRIGGER trg_canonical_dedup_vam_proof
  BEFORE INSERT OR UPDATE ON canonical_dedup_run
  FOR EACH ROW EXECUTE FUNCTION cardeep_vam_verified_needs_proof();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_canonical_dedup_vam_proof ON canonical_dedup_run;
-- DROP FUNCTION IF EXISTS cardeep_vam_verified_needs_proof();
