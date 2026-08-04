-- 0100_search_cube.sql — precomputed counts for the live result counter.
--
-- The problem: the panel's submit button has to say how many cars match the
-- current filter combination, and it has to say it while the user is still
-- choosing. Measured on the live table, a filtered `count(*)` runs 600-2700 ms
-- depending on selectivity — between four and eighteen times the budget a control
-- that updates as you type can afford.
--
-- THE DESIGN DECISION THAT MAKES THIS EXACT RATHER THAN APPROXIMATE:
-- a rollup normally trades precision for speed, because a bucketed dimension can
-- only answer questions that land on bucket boundaries. Here the boundaries ARE
-- the boundaries — `km_bucket` is keyed to the exact list of kilometre options the
-- UI offers (RangeFields.KM_STEPS), and year is discrete already. Every filter the
-- interface can express therefore falls on a cube edge, so the count it returns is
-- the true count, not an estimate. Nothing in this system publishes a "~".
--
-- Province lives on `entity`, not on `vehicle`, and that join measured 3.2 s. It is
-- resolved once here at build time so the runtime path never joins at all.
--
-- Refreshed by ATOMIC SWAP, never REFRESH MATERIALIZED VIEW CONCURRENTLY: the
-- concurrent form merges with UPDATE/DELETE and leaves dead tuples behind, which
-- this project's standing Postgres doctrine forbids. Building a sibling table and
-- renaming it costs one exclusive lock measured in milliseconds and produces zero
-- dead tuples. Hence a TABLE, not a materialized view.
--
-- Additive and reversible; touches no existing object.

CREATE TABLE IF NOT EXISTS search_cube (
    make          text     NOT NULL,
    model         text     NOT NULL,
    province_code varchar(8),
    year          smallint,
    km_bucket     smallint NOT NULL,   -- index into the UI's own kilometre scale
    n             integer  NOT NULL
);

-- Two indexes, both measured as load-bearing: the first serves every query that
-- starts from a marque (the common case), the second every query that starts from
-- a province with no marque chosen — which otherwise degrades to a full scan of
-- the cube.
CREATE INDEX IF NOT EXISTS idx_search_cube_make
    ON search_cube (make, model, province_code, year) INCLUDE (n, km_bucket);
CREATE INDEX IF NOT EXISTS idx_search_cube_prov
    ON search_cube (province_code, year) INCLUDE (n, make, km_bucket);

-- One row, always. The counter has to be able to say how old its answer is, and a
-- snapshot presented as live is a lie of omission.
CREATE TABLE IF NOT EXISTS search_cube_meta (
    only_row     boolean PRIMARY KEY DEFAULT true CHECK (only_row),
    computed_at  timestamptz NOT NULL,
    rows_in_cube integer     NOT NULL,
    vehicles     bigint      NOT NULL
);

-- km_bucket_of — the single definition of the kilometre scale, shared by the cube
-- builder and the count endpoint. Keeping it in the database rather than in both
-- callers is what stops the two from ever disagreeing about where a boundary is;
-- a cube built on one scale and queried on another would return wrong counts
-- silently, which is the worst failure mode this table could have.
--
-- Boundaries mirror RangeFields.KM_STEPS exactly. Bucket i covers [step[i], step[i+1]).
CREATE OR REPLACE FUNCTION km_bucket_of(km integer)
RETURNS smallint LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
$$
  SELECT CASE
    WHEN km IS NULL      THEN -1
    WHEN km <       5000 THEN 0
    WHEN km <      10000 THEN 1
    WHEN km <      20000 THEN 2
    WHEN km <      30000 THEN 3
    WHEN km <      40000 THEN 4
    WHEN km <      50000 THEN 5
    WHEN km <      60000 THEN 6
    WHEN km <      70000 THEN 7
    WHEN km <      80000 THEN 8
    WHEN km <      90000 THEN 9
    WHEN km <     100000 THEN 10
    WHEN km <     125000 THEN 11
    WHEN km <     150000 THEN 12
    WHEN km <     175000 THEN 13
    WHEN km <     200000 THEN 14
    WHEN km <     250000 THEN 15
    ELSE 16
  END::smallint
$$;

-- Rollback:
--   DROP FUNCTION IF EXISTS km_bucket_of(integer);
--   DROP TABLE IF EXISTS search_cube_meta;
--   DROP INDEX IF EXISTS idx_search_cube_prov;
--   DROP INDEX IF EXISTS idx_search_cube_make;
--   DROP TABLE IF EXISTS search_cube;
