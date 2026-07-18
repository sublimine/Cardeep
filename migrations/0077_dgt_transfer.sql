-- 0077_dgt_transfer.sql — DGT vehicle-transfer microdata ingestion (CAMPAIGN
-- 01-market-intelligence, F4). Additive, idempotent, reversible.
--
-- Schema CONFIRMED against the REAL official DGT "Documento de interfaz de Envío de
-- Datos (Transferencias)" (fetched 2026-07-18 from
-- https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/matraba/TRANSFERENCIAS_MATRABA.pdf)
-- AND cross-verified against a real downloaded file
-- (https://www.dgt.es/microdatos/salida/2026/6/vehiculos/transferencias/export_mensual_trf_202606.zip,
-- 40,396,793 bytes, valid PK zip, HTTP 200/application-zip — verified live, not assumed):
-- the file is fixed-width text, 69 declared fields summing to EXACTLY 714 bytes per
-- record (+1 newline = the 715-byte lines read from the real file). No discrepancy
-- between the documented interface and the live file. This closes the [ASUMIDO] that
-- 01-market-intelligence.md §5 flagged for this migration.
--
-- Confirmed from the primary source (not carried over from the carta's own research):
--   - NO price field anywhere in the 69 columns (carta's "no incluye precio" claim
--     independently re-verified against the real interface doc).
--   - BASTIDOR_ITV (VIN) is CHAR(21) but the real file truncates to 8 real chars +
--     '*' padding (verified in the sample rows) — matches the carta's "restringido
--     desde 2025-02-01" claim.
--   - COD_PROVINCIA_VEH is an ALPHA code (historic vehicle-plate province letter,
--     e.g. 'M'=Madrid, 'B'=Barcelona, 'GC'=Las Palmas) — NOT the same as Cardeep's
--     numeric INE geo_province.code. A mapping table is REQUIRED (built in
--     pipeline/market/ingest_dgt.py::DGT_PROVINCE_TO_INE, cross-referenced against
--     both the DGT PDF's Anexo I and a live SELECT code,name FROM geo_province —
--     this was NOT anticipated in the carta and is a genuine new finding of F4).

-- ---------------------------------------------------------------------------
-- dgt_transfer_batch: one ingested month, with its verification evidence
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dgt_transfer_batch (
    batch_id                    TEXT        PRIMARY KEY,       -- caller-supplied (ULID-shaped)
    month                       CHAR(6)     NOT NULL,          -- YYYYMM
    source_url                  TEXT        NOT NULL,
    zip_sha256                  TEXT        NOT NULL,
    zip_size_bytes              BIGINT,
    n_rows_parsed               INTEGER,
    n_rows_transferencia        INTEGER,                        -- rows where clave_tramite='2' (sanity subset)
    downloaded_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    double_download_verified    BOOLEAN     NOT NULL DEFAULT FALSE,  -- protocol §7: re-download + hash match
    double_download_sha256      TEXT,                            -- hash of the independent re-download
    notes                       TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_dgt_batch_month ON dgt_transfer_batch (month);

-- ---------------------------------------------------------------------------
-- dgt_transfer: normalized per-row transfer records (only the columns this
-- pilar needs today — make/model/province/date; the raw file carries 69 columns
-- but a wide 1:1 mirror is YAGNI until a consumer needs the rest).
-- ---------------------------------------------------------------------------
-- NOTE: geo_province's real PK is COMPOSITE (country_code, code) — verified live
-- (2026-07-18) after a first migration attempt failed with InvalidForeignKeyError on
-- a single-column REFERENCES geo_province(code). A country-isolation migration
-- (0069-0072 series) changed the PK from the single-column shape 0002_entities.sql
-- originally documented; entity.province_code's REAL FK today is
-- FOREIGN KEY (country_code, province_code) REFERENCES geo_province(country_code, code)
-- (confirmed via pg_constraint, not assumed from the old migration text). Mirrored
-- here with the project's single-tenant-today default ('ES', per
-- services/api/stats.py DEFAULT_COUNTRY).
CREATE TABLE IF NOT EXISTS dgt_transfer (
    id                  BIGSERIAL   PRIMARY KEY,
    batch_id            TEXT        NOT NULL REFERENCES dgt_transfer_batch(batch_id) ON DELETE CASCADE,
    fec_tramitacion     DATE        NOT NULL,   -- FEC_TRAMITACION: the transfer date itself
    marca               TEXT,                    -- MARCA_ITV, trimmed (raw DGT casing/spelling, NOT
                                                   -- yet normalized against Cardeep's make dictionary
                                                   -- -- that normalization is corroborate.py's job, §8 of
                                                   -- the carta: "diccionario determinista primero")
    modelo              TEXT,                    -- MODELO_ITV, trimmed (free-text, no normalization)
    cod_tipo            TEXT,                    -- COD_TIPO raw code (carta scope check: Cardeep's
                                                  -- census is CARS; DGT's transferencias file covers
                                                  -- every vehicle type -- trucks, motorcycles, trailers,
                                                  -- tractors, per Anexo I COD_TIPO. '40'=TURISMO is the
                                                  -- passenger-car code; corroborate.py filters to it so
                                                  -- M8 never compares Cardeep's car GONE count against a
                                                  -- DGT denominator inflated by non-car vehicle types)
    cod_provincia_dgt   TEXT,                    -- raw DGT alpha province code (COD_PROVINCIA_VEH)
    country_code        CHAR(2)     NOT NULL DEFAULT 'ES',
    province_code       VARCHAR(2),              -- mapped INE code; NULL for DS (desconocido) /
                                                  -- EX (extranjero) / any unmapped code, never guessed
    clave_tramite       TEXT,                    -- CLAVE_TRAMITE raw code (expect '2' = Transferencia
                                                  -- kept for QC, not assumed)
    CONSTRAINT dgt_transfer_province_fkey
        FOREIGN KEY (country_code, province_code) REFERENCES geo_province(country_code, code)
);

CREATE INDEX IF NOT EXISTS idx_dgt_transfer_batch ON dgt_transfer (batch_id);
CREATE INDEX IF NOT EXISTS idx_dgt_transfer_cohort
    ON dgt_transfer (province_code, marca, modelo, fec_tramitacion);

-- Rollback:
-- DROP TABLE IF EXISTS dgt_transfer;
-- DROP TABLE IF EXISTS dgt_transfer_batch;
