-- 0071_entity_cluster_country_proof.sql — country-proof as a MECHANICAL DB constraint (T1.2, road-to-13)
--
-- v_country_proof_violations (0057) is a VIEW: it DETECTS a cross-country cluster but cannot PREVENT
-- one, and no scheduler consults it against :5433 (adversarial review: "country-proof = vista
-- detectora pasiva"). The Python belts (block-keys carry country = 1st belt; _country_guard assertion
-- = 2nd belt) protect the code paths, but a direct INSERT bypasses them. This trigger is the 3rd,
-- MECHANICAL belt: a row whose member and canonical entities live in different countries is rejected
-- by the DB itself, so v_country_proof_violations stays empty BY CONSTRUCTION, not by discipline.
--
-- Per-row (O(1)): compares entity(member).country_code vs entity(canonical).country_code. Forward
-- invariant only (additive, idempotent, reversible). Same pattern for vehicle_cluster when needed.

CREATE OR REPLACE FUNCTION cardeep_entity_cluster_single_country() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE c_member text; c_canon text;
BEGIN
  SELECT country_code INTO c_member FROM entity WHERE entity_ulid = NEW.entity_ulid;
  SELECT country_code INTO c_canon  FROM entity WHERE entity_ulid = NEW.canonical_ulid;
  IF c_member IS DISTINCT FROM c_canon THEN
    RAISE EXCEPTION 'entity_cluster row spans countries: member % (%) vs canonical % (%) [run %]',
      NEW.entity_ulid, c_member, NEW.canonical_ulid, c_canon, NEW.cluster_run_id
      USING ERRCODE = 'restrict_violation';
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_entity_cluster_country ON entity_cluster;
CREATE TRIGGER trg_entity_cluster_country
  BEFORE INSERT OR UPDATE ON entity_cluster
  FOR EACH ROW EXECUTE FUNCTION cardeep_entity_cluster_single_country();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_entity_cluster_country ON entity_cluster;
-- DROP FUNCTION IF EXISTS cardeep_entity_cluster_single_country();
