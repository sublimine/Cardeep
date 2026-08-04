-- 0103_fuel_price_dims.sql — fuel and price as countable dimensions.
--
-- WHY THIS EXISTS, stated plainly: the panel was lying.
--
-- The free-text parser resolves "SUV híbrido por menos de 20.000 €" into body,
-- fuel and price, and the interface renders all three as chips. The counter behind
-- them knew nothing about fuel or price, so it answered the question that was left
-- — and the gap was not a rounding error. Measured on the live index: that query
-- displayed 428.322 against 23.775 real (18x); "Coche eléctrico por menos de
-- 20.000 € en Madrid" displayed 256.825 against 2.226 (115x). A number that large,
-- printed under the conditions it ignores, is the exact failure the cube was built
-- to prevent, and adding parsed chips without adding the dimensions re-introduced
-- it one layer up.
--
-- COST, measured rather than feared: a rollup can never hold more rows than the
-- facts it summarises. The cube stands at 1.070.235 rows over 1.483.606 cars, so
-- every remaining dimension in existence can add at most 38% before it degenerates
-- into one row per car. That ceiling is what made this affordable.
--
-- FUEL. The census holds 110 raw spellings across accents, abbreviations and
-- one-letter codes. Folding them is not tidying: `fuel ILIKE '%electr%'` matches
-- 52.330 rows and `unaccent(fuel) ILIKE '%electr%'` matches 107.429, so half of
-- every electric car in Spain was invisible to an accent.
--
-- PRICE. A uniform 1.000 € grain, which is finer than any bound a person states
-- (nobody filters at 17.350 €) and coarse enough to keep the cube's row count
-- inside the ceiling above. Same contract as kilometres: the interface snaps to the
-- grain and shows the snapped figure, so the number displayed is always the number
-- counted. Cars with no published price sit in -1 and are excluded the moment a
-- price bound is set — never silently, always with the excluded count returned.
--
-- Additive and reversible. The cube must be REBUILT after applying this.

CREATE OR REPLACE FUNCTION fuel_norm(txt text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
$$
  SELECT CASE
    WHEN txt IS NULL OR btrim(txt) = '' THEN ''
    -- Order matters: "híbrido enchufable" must be tested before "híbrido", and
    -- "mild hybrid" before both, or a plug-in is filed as a plain hybrid.
    WHEN lower(imm_unaccent(txt)) ~ '(enchufable|plug.?in|phev)'      THEN 'hibrido_enchufable'
    WHEN lower(imm_unaccent(txt)) ~ '(mild|mhev|micro.?hibrid)'       THEN 'mild_hibrido'
    WHEN lower(imm_unaccent(txt)) ~ '(hibrid|hev)'                    THEN 'hibrido'
    WHEN lower(imm_unaccent(txt)) ~ '(electric|bev|^e$)'              THEN 'electrico'
    WHEN lower(imm_unaccent(txt)) ~ '(diesel|gasoleo|gasoil|^d$|tdi|hdi|dci|cdti)' THEN 'diesel'
    WHEN lower(imm_unaccent(txt)) ~ '(gasolina|petrol|bencina|^b$|^g$)' THEN 'gasolina'
    WHEN lower(imm_unaccent(txt)) ~ '(glp|lpg|autogas)'               THEN 'glp'
    WHEN lower(imm_unaccent(txt)) ~ '(gnc|cng|gas natural)'           THEN 'gnc'
    ELSE ''
  END
$$;

-- Bucket i covers [i×1.000, (i+1)×1.000). 100 is the overflow bucket (>=100.000 €),
-- -1 means no usable price was ever published.
CREATE OR REPLACE FUNCTION price_bucket_of(price numeric)
RETURNS smallint LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
$$
  SELECT CASE
    WHEN price IS NULL OR price <= 0 THEN -1
    WHEN price >= 100000             THEN 100
    ELSE (price / 1000)::int
  END::smallint
$$;

-- Rollback:
--   DROP FUNCTION IF EXISTS price_bucket_of(numeric);
--   DROP FUNCTION IF EXISTS fuel_norm(text);
--   -- then rebuild the cube.
