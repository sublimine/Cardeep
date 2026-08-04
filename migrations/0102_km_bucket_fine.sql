-- 0102_km_bucket_fine.sql — kilometre buckets at 5.000 km, so a typed figure can
-- still be counted exactly.
--
-- Migration 0100 keyed the buckets to the seventeen options the interface offered,
-- which made every reachable filter land on a cube edge and every count exact. Then
-- the field gained a "type the exact kilometres" input, and the guarantee broke: a
-- figure like 87.000 falls INSIDE a bucket, and a bucket cannot be split at read
-- time. The options were to round the user's number in silence, to hand back an
-- approximate count, or to make the grain fine enough that neither is necessary.
--
-- The first two are the same failure this system keeps refusing: a number that
-- looks exact and is not. So the grain moves to a uniform 5.000 km — 0-250.000 in
-- fifty steps, plus an overflow bucket — and the interface snaps typed input to
-- the nearest 5.000. That snap is visible in the field, so the figure shown is
-- always the figure counted.
--
-- The seventeen-option display scale is UNCHANGED and still non-linear; it just no
-- longer defines the storage. Presentation and grain are now independent, which is
-- what let the finer grain happen without touching the control.
--
-- Cost: the cube gains rows wherever a group spans several 5.000 km bands. Measured
-- after the rebuild, not guessed here.
--
-- Replaces the function body only; the cube must be REBUILT after applying this
-- (scripts/build_search_cube.py), because existing rows carry the old indices.

CREATE OR REPLACE FUNCTION km_bucket_of(km integer)
RETURNS smallint LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
$$
  SELECT CASE
    WHEN km IS NULL   THEN -1
    WHEN km < 0       THEN 0
    WHEN km >= 250000 THEN 50
    ELSE (km / 5000)
  END::smallint
$$;

-- Rollback (restores the 0100 definition):
--   CREATE OR REPLACE FUNCTION km_bucket_of(km integer)
--   RETURNS smallint LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
--   $$ SELECT CASE WHEN km IS NULL THEN -1 WHEN km < 5000 THEN 0 ... END::smallint $$;
--   -- then rebuild the cube.
