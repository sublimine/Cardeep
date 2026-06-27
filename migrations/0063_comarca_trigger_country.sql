-- 0063_comarca_trigger_country.sql — country-scope the comarca-resolution trigger.
-- Red-team R2 #7: entity_set_comarca() (migration 0018) resolved comarca_id by
-- municipality_code ALONE, but geo_municipality's PK is (country_code, code) and
-- migration 0053 lets FR INSEE and ES INE codes (both 5-digit) collide. A non-ES
-- entity whose municipality_code matched a Spanish INE code inherited a Spanish
-- comarca_id (or a non-deterministic pick among the colliding rows). Comarca is an
-- ES-specific layer (INE comarca agraria), so for a non-ES tenant the country-scoped
-- lookup correctly finds no row and leaves comarca_id NULL.
-- Additive, idempotent, reversible (CREATE OR REPLACE). ES behaviour is byte-identical:
-- every ES entity already matched its own ES municipality row; adding country_code = 'ES'
-- changes nothing for the single-tenant census (entity.country_code is NOT NULL DEFAULT 'ES').

CREATE OR REPLACE FUNCTION entity_set_comarca() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.municipality_code IS NOT NULL THEN
        SELECT m.comarca_id INTO NEW.comarca_id
          FROM geo_municipality m
         WHERE m.code = NEW.municipality_code
           AND m.country_code = NEW.country_code;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Rollback (restores 0018 verbatim, country-blind):
-- CREATE OR REPLACE FUNCTION entity_set_comarca() RETURNS TRIGGER AS $$
-- BEGIN
--     IF NEW.municipality_code IS NOT NULL THEN
--         SELECT m.comarca_id INTO NEW.comarca_id
--           FROM geo_municipality m WHERE m.code = NEW.municipality_code;
--     END IF;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
