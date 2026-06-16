-- 0041_entity_muni_province_invariant.sql — make "muni belongs to province" a DB invariant
-- (audit SU-A6 coherence). Spanish INE municipality codes are 5 digits whose first 2 ARE the
-- province code, so municipality_code[:2] MUST equal province_code whenever both are set. Until
-- now this held by CONVENTION only — the backfill/ingest self-verify gate enforces it in Python,
-- but there was NO DB CHECK, so a future bad write could land a muni-province mismatch in the
-- SERVED surface (geo endpoints filter on municipality_code). The SU-A6 dig found province_code
-- errors among the un-served gap dealers (NULL muni, coords 600-700km off); this guard makes the
-- served invariant DB-enforced so such an error can never reach served data via a code regression.
--
-- Verified live before adding: served muni-province mismatch = 0, so the constraint VALIDATES
-- cleanly over all existing rows (not NOT-VALID — it certifies the whole table). NULL muni OR NULL
-- province are allowed (the gap dealers are not served). Idempotent (DROP IF EXISTS + ADD), reversible.

ALTER TABLE entity DROP CONSTRAINT IF EXISTS chk_entity_muni_province;
ALTER TABLE entity ADD CONSTRAINT chk_entity_muni_province
  CHECK (municipality_code IS NULL OR province_code IS NULL
         OR left(municipality_code, 2) = province_code);

-- Rollback:
-- ALTER TABLE entity DROP CONSTRAINT IF EXISTS chk_entity_muni_province;
