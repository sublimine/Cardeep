-- 0104_fuel_norm_fix.sql — three misclassifications in fuel_norm(), each measured.
--
-- 0103 shipped a fuel normaliser that looked complete and got three groups wrong.
-- All three were found by comparing its output against an independent count of the
-- same census, which is the only way this class of bug ever surfaces: every one of
-- them produced a plausible answer.
--
--  1. "Electro/Gasolina" — 50.376 cars — filed as GASOLINA.
--     It is the Spanish notation for a hybrid. The pattern looked for "electric"
--     and this word is "electro", so it fell through to the petrol branch. Checked
--     against the models carrying the label: Toyota C-HR, Corolla and Yaris,
--     Renault Arkana, Kia Sportage, Ford Puma, Fiat 500 — textbook hybrids, all of
--     them. Fifty thousand hybrids were being counted as petrol cars, and a buyer
--     filtering for hybrids never saw them.
--
--  2. "Híbrido no enchufable" — 5.076 cars — filed as PLUG-IN HYBRID.
--     The plug-in test ran first and matched the word "enchufable" inside the
--     phrase that negates it. The label says exactly what it is not, and the
--     classifier read it as what it is not.
--
--  3. "Gas licuado (GPL)" (6.152), "Gas Licuado" (1.405) and "Bifuel" (1.056) —
--     unclassified. GPL is the same fuel as GLP written the Italian/French way,
--     and bi-fuel in this market means petrol/LPG. "DIES" (1.540) is diesel
--     abbreviated by one feed.
--
-- Left deliberately unclassified: "2" (6.537, an opaque numeric code), "ESS"
-- (3.643, ambiguous between essence and a code) and "Gas" (1.664, could be LPG or
-- CNG). Guessing at these would put cars in a fuel they may not have — the whole
-- point of the '' bucket is that "we do not know" is a real answer.
--
-- The cube must be REBUILT after applying this.

CREATE OR REPLACE FUNCTION fuel_norm(txt text)
RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
$$
  SELECT CASE
    WHEN txt IS NULL OR btrim(txt) = '' THEN ''
    -- NEGATION FIRST. "Híbrido no enchufable" has to be caught before the plug-in
    -- test, or the phrase that denies it is what matches.
    WHEN lower(imm_unaccent(txt)) ~ 'no\s+enchufable'                 THEN 'hibrido'
    WHEN lower(imm_unaccent(txt)) ~ '(enchufable|plug.?in|phev)'      THEN 'hibrido_enchufable'
    WHEN lower(imm_unaccent(txt)) ~ '(micro.?hibrid|mild|mhev)'       THEN 'mild_hibrido'
    WHEN lower(imm_unaccent(txt)) ~ '(hibrid|hev)'                    THEN 'hibrido'
    -- "Electro/Gasolina" is a hybrid, not a petrol car. This line must sit ABOVE
    -- both the electric and the petrol branches, because it contains a word that
    -- resembles one and a word that is the other.
    WHEN lower(imm_unaccent(txt)) ~ 'electro.*(gasolina|diesel)'      THEN 'hibrido'
    WHEN lower(imm_unaccent(txt)) ~ '(electric|^electro$|bev|^e$)'    THEN 'electrico'
    WHEN lower(imm_unaccent(txt)) ~ '(glp|gpl|lpg|autogas|gas\s*licuado|bifuel)' THEN 'glp'
    WHEN lower(imm_unaccent(txt)) ~ '(gnc|cng|gas\s*natural)'         THEN 'gnc'
    WHEN lower(imm_unaccent(txt)) ~ '(diesel|^dies|gasoleo|gasoil|^d$|tdi|hdi|dci|cdti)' THEN 'diesel'
    WHEN lower(imm_unaccent(txt)) ~ '(gasolina|petrol|bencina|^b$)'   THEN 'gasolina'
    ELSE ''
  END
$$;

-- Rollback: restore the 0103 body, then rebuild the cube.
