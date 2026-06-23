-- 0055_product_stats.sql — fast /stats: a precomputed single-row product-counts cache.
--
-- PROBLEM. GET /stats ran 5 aggregates live, two of them COUNT(DISTINCT)/JOIN over 2.3M+ rows
-- (v_dealer_resolved, v_canonical_vehicle JOIN servable_vehicle) — ~83s cold. The web portal therefore
-- almost always rendered its (now removed) fallback while waiting. This table holds the EXACT counts
-- (not an approximation), refreshed off the request path by a scheduler cadence job; /stats reads one
-- row instantly and reports computed_at so the age is explicit. Honest: real numbers, disclosed freshness.
--
-- WHY ADDITIVE / ZERO-RISK: CREATE TABLE IF NOT EXISTS only; touches no existing table/column/FK/row.
-- The /stats handler falls back to the live computation when the row is absent (pre-refresh / pre-migration),
-- so behaviour is preserved until the refresh job populates it. Single row enforced by PK + CHECK(id=1).
-- Reversible: DROP the table (see Rollback) — nothing else depends on it.

CREATE TABLE IF NOT EXISTS product_stats (
    id                         SMALLINT     PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    dealers                    BIGINT,
    vehicles_unique_available  BIGINT,
    events                     BIGINT,
    provinces                  INTEGER,
    municipalities             INTEGER,
    computed_at                TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE product_stats IS
    'Single-row precomputed cache of the GET /stats product counts (exact, not approximate). Refreshed '
    'off-request by the harvest scheduler (refresh_product_stats); /stats reads it instantly with a '
    'live-compute fallback. See scripts/refresh_product_stats.py + services/api/routers/ops.py.';

-- Rollback:
-- DROP TABLE IF EXISTS product_stats;
