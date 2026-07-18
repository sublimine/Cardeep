-- 0090_market_sale_inference.sql — 09-trading-terminal Fase 4: "venta probable" inference.
--
-- NUMBERING: `ls migrations/*.sql | sort -V | tail` at creation time showed 0089 as the highest
-- file on disk (0089_feed_export.sql, a parallel frontier of this same block). This is 0090.
--
-- C5 (carta §4, corrected per 00-MASTER.md C-9): "Venta probable (inferida)" = GONE + sin
-- reaparición detectada por el motor lifetime_link de 02-history-reports (v_vehicle_lifetime,
-- migrations/0075) EN VEZ de la heurística original de la carta sobre vehicle_cluster —
-- resolución explícita del MASTER: "09-Fase-4 (inferencia de venta 'sin reaparición en 14 días')
-- debe CONSUMIR el motor lifetime_link de 02-F1 en cuanto exista — su heurística propia sobre
-- vehicle_cluster no detecta reapariciones semanas después en otro dealer, exactamente lo que 02
-- construye." + último precio dentro de +/-25% de la mediana del símbolo (market_bucket_daily).
--
-- DECLARED GAP, VERIFIED LIVE THIS SESSION (not assumed — the task explicitly required
-- verifying, not assuming, that lifetime_link now has real signal after 04-arbitrage-F6's
-- vin_ref remediation, migration 0083): re-ran pipeline/identity/link_lifetimes.py fresh
-- against the remediated data (41,575 candidate vehicles, up from the pre-remediation
-- 2,520,623-row contaminated set) — result: 12,526 VIN candidate pairs, ZERO edges survive
-- the resolver's anti-FP guards (breakdown: 6,970 predecessor-not-gone, 4,196 out-of-window,
-- 1,133 active-sibling, 227 same-domain-churn, 0 pass all guards). v_vehicle_lifetime is
-- CURRENTLY EMPTY at the serving level (zero rows AND the one existing run has
-- vam_verified=FALSE). The remediation did NOT produce real cross-dealer signal today — the
-- task's own optimistic premise ("debería empezar a tener señal real ahora") is verified FALSE
-- for this specific corpus snapshot, reported here rather than assumed.
--
-- CONSEQUENCE for this table's confidence formula: "sin reaparición en v_vehicle_lifetime" is
-- currently a near-VACUOUS condition (true for ~100% of GONE vehicles, since the view has
-- nothing to contradict it) — absence of evidence in an empty engine is NOT evidence of
-- absence. `evidence.lifetime_link_coverage` is written as an explicit field precisely so this
-- is never silently laundered into false confidence; `confidence` is capped LOW
-- (CONFIDENCE_CAP_WHEN_LIFETIME_EMPTY in pipeline/terminal/infer_sales.py) whenever the
-- lifetime_link engine's edge count is zero, and rises automatically (zero code change here)
-- once 02-F1's engine or 04-F6's photo_hash backfill starts producing real edges.
--
-- V4 (carta §7, row V4): audited/audit_result columns exist from day 1 (this migration) so the
-- N>=50 manual re-visit sample (Obscura/Playwright against the original platform) has somewhere
-- to write its verdict — but NO audit has been run yet in this execution (declared, not hidden):
-- `audited=FALSE` on every row until a real audit pass lands. The API/UI badge degrades to "sin
-- verificar" whenever no audit is <=30d fresh (enforced at read time, not by a stored flag that
-- could go stale silently).

CREATE TABLE IF NOT EXISTS market_sale_inference (
    vehicle_ulid   TEXT PRIMARY KEY REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    symbol_key     TEXT NOT NULL REFERENCES market_symbol(symbol_key) ON DELETE CASCADE,
    gone_at        TIMESTAMPTZ NOT NULL,
    inference      TEXT NOT NULL CHECK (inference IN ('probable_sale', 'delisted', 'relisted')),
    confidence     NUMERIC NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    evidence       JSONB NOT NULL,       -- {last_price, symbol_median, price_ratio, lifetime_link_checked,
                                          --  lifetime_link_coverage, lifetime_link_edge_found, ...}
    computed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    audited        BOOLEAN NOT NULL DEFAULT FALSE,
    audited_at     TIMESTAMPTZ,
    audit_result   TEXT CHECK (audit_result IN ('confirmed_sold', 'still_listed_elsewhere', 'inconclusive') OR audit_result IS NULL)
);

CREATE INDEX IF NOT EXISTS idx_sale_inference_symbol ON market_sale_inference (symbol_key, inference);
CREATE INDEX IF NOT EXISTS idx_sale_inference_audit_freshness ON market_sale_inference (audited, audited_at DESC);

-- Rollback:
-- DROP TABLE IF EXISTS market_sale_inference;
