-- 0072_vehicle_cluster_country_proof.sql — country-proof for the SECOND served axis (T1.2-ext, road-to-13)
--
-- entity_cluster got the mechanical country-proof belt in 0071, but vehicle_cluster (the other served
-- axis — v_canonical_vehicle reads it) had no equivalent: a direct INSERT could fuse two vehicles whose
-- dealers live in different countries. This closes that asymmetry. A vehicle's country is entity(
-- vehicle.entity_ulid).country_code (vehicle.entity_ulid is NOT NULL, so it is always defined). Same
-- pattern as 0071 with one extra join. Forward-only, additive, idempotent, reversible.

CREATE OR REPLACE FUNCTION cardeep_vehicle_cluster_single_country() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE c_member text; c_canon text;
BEGIN
  SELECT e.country_code INTO c_member
    FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
    WHERE v.vehicle_ulid = NEW.vehicle_ulid;
  SELECT e.country_code INTO c_canon
    FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
    WHERE v.vehicle_ulid = NEW.canonical_vehicle_ulid;
  IF c_member IS DISTINCT FROM c_canon THEN
    RAISE EXCEPTION 'vehicle_cluster row spans countries: vehicle % (%) vs canonical % (%) [run %]',
      NEW.vehicle_ulid, c_member, NEW.canonical_vehicle_ulid, c_canon, NEW.cluster_run_id
      USING ERRCODE = 'restrict_violation';
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_vehicle_cluster_country ON vehicle_cluster;
CREATE TRIGGER trg_vehicle_cluster_country
  BEFORE INSERT OR UPDATE ON vehicle_cluster
  FOR EACH ROW EXECUTE FUNCTION cardeep_vehicle_cluster_single_country();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_vehicle_cluster_country ON vehicle_cluster;
-- DROP FUNCTION IF EXISTS cardeep_vehicle_cluster_single_country();
