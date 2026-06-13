-- 0018_comarca.sql — Populate the comarca layer (INE comarca agraria, MAPA).
-- Additive, idempotent, reversible. Adds an INE comarca code + provenance to
-- geo_comarca so the pais -> PROVINCIA -> COMARCA -> ciudad grid is complete,
-- and an index to traverse entity inventory by comarca.

-- INE comarca-agraria number, 2 digits, unique within its province.
-- Nullable so manually-added (non-agrarian) comarcas remain valid.
ALTER TABLE geo_comarca ADD COLUMN IF NOT EXISTS ine_code CHAR(2);
ALTER TABLE geo_comarca ADD COLUMN IF NOT EXISTS source   TEXT;

-- One INE comarca number per province (when present). Partial unique index so
-- rows with NULL ine_code (future non-agrarian comarcas) do not collide.
CREATE UNIQUE INDEX IF NOT EXISTS uq_comarca_province_inecode
    ON geo_comarca (province_code, ine_code)
    WHERE ine_code IS NOT NULL;

-- Traverse entity inventory by comarca without a province scan.
CREATE INDEX IF NOT EXISTS idx_entity_comarca ON entity (comarca_id)
    WHERE comarca_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_municipality_comarca ON geo_municipality (comarca_id)
    WHERE comarca_id IS NOT NULL;

-- Keep entity.comarca_id consistent with its municipality automatically, so
-- live-inserted/updated entities inherit the comarca without a backfill pass.
-- (Backfill of existing rows + the municipality->comarca map is done by
-- scripts/backfill_comarca.py; this trigger maintains it going forward.)
CREATE OR REPLACE FUNCTION entity_set_comarca() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.municipality_code IS NOT NULL THEN
        SELECT m.comarca_id INTO NEW.comarca_id
          FROM geo_municipality m WHERE m.code = NEW.municipality_code;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_entity_set_comarca ON entity;
CREATE TRIGGER trg_entity_set_comarca
    BEFORE INSERT OR UPDATE OF municipality_code ON entity
    FOR EACH ROW EXECUTE FUNCTION entity_set_comarca();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_entity_set_comarca ON entity;
-- DROP FUNCTION IF EXISTS entity_set_comarca();
-- DROP INDEX IF EXISTS idx_municipality_comarca;
-- DROP INDEX IF EXISTS idx_entity_comarca;
-- DROP INDEX IF EXISTS uq_comarca_province_inecode;
-- ALTER TABLE geo_comarca DROP COLUMN IF EXISTS source;
-- ALTER TABLE geo_comarca DROP COLUMN IF EXISTS ine_code;
