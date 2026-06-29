-- 0066_product_stats_country.sql — /stats per country.
--
-- The single-row product_stats cache (0055, keyed by `id SMALLINT PK CHECK(id=1)`) becomes ONE ROW
-- PER country_code, so GET /stats can serve a SECOND tenant's product figures instead of only ES's.
--
-- ES-PRESERVING: `ADD COLUMN country_code NOT NULL DEFAULT 'ES'` stamps the existing single row as
-- the ES row (its counts unchanged); the new PRIMARY KEY is country_code. The `id` single-row guard
-- (PK + CHECK(id=1)) is removed — product_stats is a PRIVATE precomputed cache with NO foreign key
-- referencing it (0055: "nothing else depends on it"); refresh_product_stats.py + services/api/stats.py
-- + services/api/routers/ops.py are updated in lockstep to key by country_code. The DATA is preserved
-- (the ES row and its counts survive); the only column dropped is the now-meaningless single-row id.
--
-- ZERO-RISK FOR ES: with ES the sole tenant, product_stats holds exactly the same ES counts as before,
-- now addressed by country_code='ES' instead of id=1. /stats?country defaults to 'ES' → byte-identical.

ALTER TABLE product_stats ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE product_stats DROP CONSTRAINT IF EXISTS product_stats_pkey;
ALTER TABLE product_stats DROP CONSTRAINT IF EXISTS product_stats_id_check;
ALTER TABLE product_stats DROP COLUMN IF EXISTS id;
ALTER TABLE product_stats ADD PRIMARY KEY (country_code);

COMMENT ON TABLE product_stats IS
    'Per-country precomputed cache of the GET /stats product counts (exact, not approximate). One row '
    'per country_code (PK), refreshed off-request by the harvest scheduler (refresh_product_stats); '
    'GET /stats?country reads the requested tenant''s row instantly with a live-compute fallback. '
    'See scripts/refresh_product_stats.py + services/api/stats.py + services/api/routers/ops.py.';

-- Rollback:
-- ALTER TABLE product_stats DROP CONSTRAINT product_stats_pkey;
-- DELETE FROM product_stats WHERE country_code <> 'ES';
-- ALTER TABLE product_stats ADD COLUMN id SMALLINT DEFAULT 1 CHECK (id = 1);
-- UPDATE product_stats SET id = 1;
-- ALTER TABLE product_stats DROP COLUMN country_code;
-- ALTER TABLE product_stats ADD PRIMARY KEY (id);
