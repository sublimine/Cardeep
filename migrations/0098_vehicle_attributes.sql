-- 0098_vehicle_attributes.sql — colour, body type and trim, each with its provenance.
--
-- Why this exists: the census can answer "Mercedes C 63 AMG" but cannot answer
-- "coche rojo grande de familia", because the three attributes that question is made
-- of do not exist as columns. Measured against the live table (2026-08-03), the
-- signal is not in `title` either: colour words match 889 of 2,434,963 titles
-- (0.04%) and body-type words 48,351 (2.0%). Adding the columns is the precondition
-- for every route that fills them.
--
-- Provenance is NOT optional. A colour read from a structured source field and a
-- colour guessed from a URL slug are different claims, and a number computed over
-- them has to be able to say which it counted. `*_source` records how each value
-- was obtained so any figure built on it stays auditable:
--     source    — the platform published it as a field (highest trust)
--     url_slug  — parsed out of deep_link (e.g. '…-dolcevita-rojo-2/')
--     title     — parsed out of the listing title
--     model_map — inferred from make+model via model_attributes (body_type only:
--                 a Ford Galaxy is a monovolumen by construction, not by listing)
--     photo     — derived from the photograph (reserved; no such pass runs today)
-- NULL source with a NULL value is simply "unknown", which is the honest default
-- for the majority of rows and must never be rendered as an absence of the trait.
--
-- Lock profile: ADD COLUMN without a default is catalogue-only on PostgreSQL 11+,
-- so this does not rewrite the 2 GB heap. The CHECK constraints are added NOT VALID
-- for the same reason — they police every future write immediately while skipping
-- the full-table verification scan. Existing rows are all NULL and trivially
-- conform; VALIDATE can be run later under a weaker lock if ever desired.
--
-- Additive and reversible; touches no existing column.

ALTER TABLE vehicle
    ADD COLUMN IF NOT EXISTS color        text,
    ADD COLUMN IF NOT EXISTS body_type    text,
    ADD COLUMN IF NOT EXISTS trim         text,
    ADD COLUMN IF NOT EXISTS color_source text,
    ADD COLUMN IF NOT EXISTS body_source  text,
    ADD COLUMN IF NOT EXISTS trim_source  text;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vehicle_color_source_check') THEN
        ALTER TABLE vehicle ADD CONSTRAINT vehicle_color_source_check
            CHECK (color_source IS NULL OR color_source = ANY (ARRAY['source','url_slug','title','photo'])) NOT VALID;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vehicle_body_source_check') THEN
        ALTER TABLE vehicle ADD CONSTRAINT vehicle_body_source_check
            CHECK (body_source IS NULL OR body_source = ANY (ARRAY['source','url_slug','title','model_map'])) NOT VALID;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vehicle_trim_source_check') THEN
        ALTER TABLE vehicle ADD CONSTRAINT vehicle_trim_source_check
            CHECK (trim_source IS NULL OR trim_source = ANY (ARRAY['source','url_slug','title'])) NOT VALID;
    END IF;
END $$;

-- Partial indexes: every query that touches these columns is a filter for a KNOWN
-- value, never a scan for the unknown majority. Indexing only the populated rows
-- keeps them small (colour is expected around 10% of the table on day one).
CREATE INDEX IF NOT EXISTS idx_vehicle_color_available
    ON vehicle (color) WHERE status = 'available' AND color IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_vehicle_body_available
    ON vehicle (body_type) WHERE status = 'available' AND body_type IS NOT NULL;

-- model_attributes — body type and segment as a property of the MODEL, not of the
-- listing. This is the table that makes "grande de familia" answerable: labelling
-- the ~943 make+model pairs that carry 77% of the fleet is bounded work, whereas
-- labelling 2.5M listings is not. Keyed to mv_market_make_model's own natural key
-- so the two never drift apart.
--
-- `confidence` and `source` exist so a low-confidence label can be excluded from a
-- hard filter while still contributing to ranking. `seats` is nullable on purpose:
-- for many models it genuinely varies by trim, and inventing one number to make a
-- filter feel complete is the exact failure this schema is built to prevent.
CREATE TABLE IF NOT EXISTS model_attributes (
    make_raw    text        NOT NULL,
    model       text        NOT NULL,
    body_type   text,
    segment     text,
    seats       smallint,
    is_family   boolean,
    source      text        NOT NULL,
    confidence  real        NOT NULL DEFAULT 0.0,
    reviewed_by text,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (make_raw, model),
    CONSTRAINT model_attributes_body_check CHECK (
        body_type IS NULL OR body_type = ANY (ARRAY[
            'utilitario','compacto','berlina','familiar','suv','monovolumen',
            'coupe','cabrio','furgoneta','pickup'])),
    CONSTRAINT model_attributes_source_check CHECK (
        source = ANY (ARRAY['llm','human','dataset'])),
    CONSTRAINT model_attributes_confidence_check CHECK (confidence >= 0.0 AND confidence <= 1.0),
    CONSTRAINT model_attributes_seats_check CHECK (seats IS NULL OR (seats BETWEEN 1 AND 9))
);

CREATE INDEX IF NOT EXISTS idx_model_attributes_body
    ON model_attributes (body_type) WHERE body_type IS NOT NULL;

-- Rollback:
--   DROP INDEX IF EXISTS idx_model_attributes_body;
--   DROP TABLE IF EXISTS model_attributes;
--   DROP INDEX IF EXISTS idx_vehicle_body_available;
--   DROP INDEX IF EXISTS idx_vehicle_color_available;
--   ALTER TABLE vehicle DROP CONSTRAINT IF EXISTS vehicle_trim_source_check;
--   ALTER TABLE vehicle DROP CONSTRAINT IF EXISTS vehicle_body_source_check;
--   ALTER TABLE vehicle DROP CONSTRAINT IF EXISTS vehicle_color_source_check;
--   ALTER TABLE vehicle DROP COLUMN IF EXISTS trim_source, DROP COLUMN IF EXISTS body_source,
--       DROP COLUMN IF EXISTS color_source, DROP COLUMN IF EXISTS trim,
--       DROP COLUMN IF EXISTS body_type, DROP COLUMN IF EXISTS color;
