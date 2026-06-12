-- 0001_geo.sql — Geo backbone (INE): province -> comarca -> municipality
-- Additive, idempotent, reversible. Spain administrative grid for the mandate.

CREATE TABLE IF NOT EXISTS geo_province (
    code        CHAR(2) PRIMARY KEY,          -- INE province code, 2 digits
    name        TEXT NOT NULL,
    ccaa_code   CHAR(2) NOT NULL,             -- autonomous community code
    ccaa_name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS geo_comarca (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    province_code CHAR(2) NOT NULL REFERENCES geo_province(code),
    name          TEXT NOT NULL,
    UNIQUE (province_code, name)
);

CREATE TABLE IF NOT EXISTS geo_municipality (
    code          CHAR(5) PRIMARY KEY,        -- INE municipality code, 5 digits (province = left 2)
    name          TEXT NOT NULL,
    province_code CHAR(2) NOT NULL REFERENCES geo_province(code),
    comarca_id    BIGINT REFERENCES geo_comarca(id),
    lat           DOUBLE PRECISION,
    lon           DOUBLE PRECISION,
    -- invariant: the municipality code must start with its province code
    CONSTRAINT municipality_province_prefix CHECK (left(code, 2) = province_code)
);

CREATE INDEX IF NOT EXISTS idx_municipality_province ON geo_municipality (province_code);
CREATE INDEX IF NOT EXISTS idx_comarca_province ON geo_comarca (province_code);

-- Rollback:
-- DROP TABLE IF EXISTS geo_municipality;
-- DROP TABLE IF EXISTS geo_comarca;
-- DROP TABLE IF EXISTS geo_province;
