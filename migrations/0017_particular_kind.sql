-- 0017_particular_kind.sql — private individual sellers as first-class entities.
--
-- WHY: the mission indexes 100% of cars FOR SALE in Spain. A car sold by a private
-- individual IS inventory a buyer can purchase — denying it would deny real supply —
-- so it must be served exactly like a dealer's car. Until now the platform connectors
-- SKIPPED private sellers (coches.net skipped ~117k, milanuncios ~36k). This adds the
-- 'particular' entity kind so those cars are caged and served.
--
-- MODEL (source-truthful, not inflated):
--   * Where the source exposes a STABLE per-seller id (milanuncios authorId,
--     wallapop user_id) -> ONE entity per real human: a particular with N cars is a
--     single multi-car seller (canonical_key 'particular:{platform}:{sellerId}').
--   * Where the source ANONYMISES privates (coches.net shares contractId='1' across all
--     privates and exposes only a first name) -> ONE per-province bucket entity
--     ('particular:{platform}:{province}'). We do NOT fabricate per-seller identity the
--     source withholds; the car is still served with full car-level delta/historial.
--
-- Particular is a DISTINCT kind so professional inventory stays filterable from C2C.
-- Additive, reversible.

ALTER TYPE entity_kind ADD VALUE IF NOT EXISTS 'particular';

-- Rollback:
-- PostgreSQL cannot DROP an enum value in place. To revert: recreate entity_kind without
-- 'particular', re-cast entity.kind (after deleting/relabelling any kind='particular'
-- rows), then drop the old type. Manual, E2E-verified.
