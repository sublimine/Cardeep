-- 0035_append_only_row_guards.sql — complete append-only enforcement (audit follow-up to F2/0034)
--
-- 0034 sealed TRUNCATE on the four append-only ledgers. The live-schema audit then found two of
-- them lacked any ROW-level UPDATE/DELETE guard despite being documented append-only:
--   * gestion_transition — INSERT-only by design (0031 invariant #4); no code path mutates it.
--   * vehicle_event       — content-immutable, BUT vehicle_ulid is legitimately re-pointed during
--                           cross-platform dedup canonicalization (scripts/cross_platform_dedup_
--                           watermark.py, scripts/fix_coches_com_deeplink.py both UPDATE only
--                           vehicle_ulid). A blanket guard would break dedup.
--
-- Decisions:
--   * gestion_transition: reuse the shared cardeep_block_mutation() (blocks ALL UPDATE/DELETE).
--   * vehicle_event: a SURGICAL guard — block DELETE, and block UPDATE of every column EXCEPT
--     vehicle_ulid (the sole column dedup re-points). This seals the delta-history content
--     (price/type/timestamps — the basis of the product's delta feature) while preserving
--     canonicalization.
--
-- Verified (live, 2026-06-15): only the two dedup scripts UPDATE vehicle_event, and only its
-- vehicle_ulid column; nothing UPDATE/DELETEs gestion_transition.
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

-- gestion_transition: genuinely INSERT-only -> total row guard.
DROP TRIGGER IF EXISTS trg_gestion_transition_noupd ON gestion_transition;
CREATE TRIGGER trg_gestion_transition_noupd
  BEFORE UPDATE OR DELETE ON gestion_transition
  FOR EACH ROW EXECUTE FUNCTION cardeep_block_mutation();

-- vehicle_event: surgical content-immutability guard (allow vehicle_ulid re-pointing only).
CREATE OR REPLACE FUNCTION cardeep_vehicle_event_guard() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'vehicle_event is append-only: DELETE forbidden (event_ulid %)', OLD.event_ulid
      USING ERRCODE = 'restrict_violation';
  END IF;
  -- UPDATE: only vehicle_ulid may change (cross-platform canonicalization re-pointing).
  IF NEW.event_ulid  IS DISTINCT FROM OLD.event_ulid
  OR NEW.entity_ulid IS DISTINCT FROM OLD.entity_ulid
  OR NEW.event_type  IS DISTINCT FROM OLD.event_type
  OR NEW.old_value   IS DISTINCT FROM OLD.old_value
  OR NEW.new_value   IS DISTINCT FROM OLD.new_value
  OR NEW.observed_at IS DISTINCT FROM OLD.observed_at THEN
    RAISE EXCEPTION 'vehicle_event content is immutable; only vehicle_ulid may be re-pointed '
                    '(canonicalization). Attempted content change on event_ulid %', OLD.event_ulid
      USING ERRCODE = 'restrict_violation';
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_vehicle_event_immutable ON vehicle_event;
CREATE TRIGGER trg_vehicle_event_immutable
  BEFORE UPDATE OR DELETE ON vehicle_event
  FOR EACH ROW EXECUTE FUNCTION cardeep_vehicle_event_guard();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_vehicle_event_immutable ON vehicle_event;
-- DROP FUNCTION IF EXISTS cardeep_vehicle_event_guard();
-- DROP TRIGGER IF EXISTS trg_gestion_transition_noupd ON gestion_transition;
