-- 0097_market_make_model_mv.sql — precomputed make/model counts for the public
-- brand selector.
--
-- Why a materialized view and not a query: the landing's brand picker needs the
-- real universe of marques and, once one is chosen, its real models. Measured
-- against the live table, `GROUP BY make` takes 5.0s and `GROUP BY model` for a
-- single make takes 8.9s — usable for a report, unusable for a dropdown that
-- opens on click. The shared response cache does not rescue it either: its TTL
-- is 60s (services/api/cache.py), so one visitor a minute would pay the full
-- aggregation.
--
-- Rolled up here instead: ~156 makes and their models, a few thousand rows, read
-- by index in milliseconds. `make_raw` keeps the source spelling exactly as the
-- census recorded it — canonicalisation of the dirty values ("WOLKSWAGEN",
-- "MERCEDES BENZ", "GOLF" as a make) belongs in the API, where it can be read
-- and corrected, not baked irreversibly into stored data.
--
-- Additive and reversible; touches no existing object.

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_market_make_model AS
SELECT upper(trim(make))              AS make_raw,
       trim(model)                    AS model,
       count(*)::bigint               AS n,
       min(price) FILTER (WHERE price > 0)::int AS price_min,
       now()                          AS computed_at
  FROM vehicle
 WHERE status = 'available'
   AND make <> ''
   AND model <> ''
 GROUP BY 1, 2;

-- REFRESH ... CONCURRENTLY requires a unique index, and refreshing without it
-- would lock the view against readers for the length of the rebuild.
CREATE UNIQUE INDEX IF NOT EXISTS mv_market_make_model_key
    ON mv_market_make_model (make_raw, model);

CREATE INDEX IF NOT EXISTS mv_market_make_model_make
    ON mv_market_make_model (make_raw);

-- Refresh (schedule alongside the other periodic jobs; the API serves
-- `computed_at` so staleness is visible rather than assumed):
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_market_make_model;
--
-- Rollback:
--   DROP MATERIALIZED VIEW IF EXISTS mv_market_make_model;
