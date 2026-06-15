-- 0036_gestion_resolved_proof.sql — RESOLVED requires a REAL proof verdict (audit F7)
--
-- 0031 gates "RESOLVED requires verdict_id" (route.py:226), but verdict_id only needs to be
-- NON-NULL — it could point to a REFUTED/UNVERIFIED verdict, or a grandfathered TRUSTWORTHY with
-- quorum_n=0. That is a closure "proof" that is not a proof. This makes the real requirement a DB
-- invariant: a gestion_item may enter RESOLVED only if verdict_id references a TRUSTWORTHY verdict
-- with quorum_n>=2 (the same quorum the Inquisition/VAM require to certify a claim).
--
-- (verification_verdict already CHECK-enforces TRUSTWORTHY => quorum>=2 for NEW rows via 0026
-- chk_trustworthy_needs_quorum, but 989 grandfathered NOT VALID rows predate it with quorum_n=0;
-- requiring quorum_n>=2 here rejects those as closure proof too.)
--
-- gestion_item is currently empty (L3 not yet exercised) -> no backfill. Forward invariant only.
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

CREATE OR REPLACE FUNCTION cardeep_gestion_resolved_needs_proof() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_verdict text; v_quorum int;
BEGIN
  IF NEW.state = 'RESOLVED'
     AND (TG_OP = 'INSERT' OR OLD.state IS DISTINCT FROM 'RESOLVED') THEN
    IF NEW.verdict_id IS NULL THEN
      RAISE EXCEPTION 'gestion_item % cannot be RESOLVED without verdict_id (no independent recheck)',
        NEW.id USING ERRCODE = 'restrict_violation';
    END IF;
    SELECT verdict, quorum_n INTO v_verdict, v_quorum
      FROM verification_verdict WHERE id = NEW.verdict_id;
    IF v_verdict IS DISTINCT FROM 'TRUSTWORTHY' OR COALESCE(v_quorum, 0) < 2 THEN
      RAISE EXCEPTION 'gestion_item % RESOLVED needs a TRUSTWORTHY verdict with quorum_n>=2; '
                      'verdict_id % is verdict=% quorum_n=%',
        NEW.id, NEW.verdict_id, COALESCE(v_verdict, '<missing>'), COALESCE(v_quorum, 0)
        USING ERRCODE = 'restrict_violation';
    END IF;
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_gestion_resolved_proof ON gestion_item;
CREATE TRIGGER trg_gestion_resolved_proof
  BEFORE INSERT OR UPDATE ON gestion_item
  FOR EACH ROW EXECUTE FUNCTION cardeep_gestion_resolved_needs_proof();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_gestion_resolved_proof ON gestion_item;
-- DROP FUNCTION IF EXISTS cardeep_gestion_resolved_needs_proof();
