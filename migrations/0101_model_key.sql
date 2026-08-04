-- 0101_model_key.sql — the model-name equivalent of make_norm().
--
-- Migration 0099 gave marques a canonical layer and the picker immediately stopped
-- showing three "Mercedes-Benz" rows. Models had no such layer, and the same defect
-- was sitting one level down: the census carries "Leon" and "León", "Qashqai" and
-- "QASHQAI", "Tucson" and "TUCSON", "Juke" and "JUKE" as different models, each
-- holding a fraction of the real count, each offered as a separate option.
--
-- Two normalisations, and the second is not cosmetic:
--   * accents, case and punctuation are discarded, exactly as make_norm does;
--   * a leading "Clase " is stripped, because Spanish sources write Mercedes models
--     both ways ("Clase GLA" and "GLA", "Clase CLA" and "CLA") and those are the
--     same car. Measured on the live cube before this existed: Clase GLA 2.951 vs
--     GLA 2.503, Clase CLA 4.252 vs CLA 2.089, Clase GLC 3.563 vs GLC 2.053 — over
--     six thousand cars filed under a duplicate of their own model.
--
-- What this deliberately does NOT do is merge body variants: "Clase C" and
-- "Clase C Estate" stay apart, because an Estate is a different car to buy even
-- though it shares a name. Collapsing those would be tidying the data into a lie.
--
-- The DISPLAY name is chosen by the cube builder, never here: whichever real
-- spelling the census uses most for a key wins, so no label is ever invented.
--
-- Additive and reversible; touches no existing object.

CREATE OR REPLACE FUNCTION model_key(text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
$$
  SELECT upper(regexp_replace(
           imm_unaccent(regexp_replace(lower(btrim(coalesce($1, ''))), '^clase\s+', '')),
           '[^a-zA-Z0-9]', '', 'g'))
$$;

-- Rollback:
--   DROP FUNCTION IF EXISTS model_key(text);
