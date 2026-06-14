-- 0022_geo_centroides.sql — Seed centroid lat/lon into geo_municipality (B4.3).
-- Source: PopulateTools/ine-places (MIT-compatible, derived from official INE data).
--         8,119 of 8,132 municipalities covered (99.8%). The 13 remaining are
--         recently created/split municipalities not yet in the upstream dataset;
--         their lat/lon stays NULL and the KNN geocoder skips them.
-- Additive, idempotent (UPDATE ... WHERE lat IS DISTINCT FROM), reversible.
-- No new columns needed: lat + lon already exist in geo_municipality (0001_geo.sql).

-- Spatial index: speeds up the in-province KNN lookup in MunicipalityGeocoder.
CREATE INDEX IF NOT EXISTS idx_municipality_centroid
    ON geo_municipality (province_code, lat, lon)
    WHERE lat IS NOT NULL AND lon IS NOT NULL;

-- Seed is applied by scripts/seed_geo_centroides.py (called from migrate up hook
-- or run standalone). SQL migrations carry only DDL; bulk CSV data goes through
-- the Python seeder to keep migration files small and avoid embedding 8k rows of
-- escaped string literals in SQL.

-- Rollback:
-- DROP INDEX IF EXISTS idx_municipality_centroid;
-- UPDATE geo_municipality SET lat = NULL, lon = NULL;
