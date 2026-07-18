-- 0091_sector_news.sql — 09-trading-terminal Fase 5: real sector news ingestion.
--
-- NUMBERING: `ls migrations/*.sql | sort -V | tail` at creation time showed 0090 (this pilar's
-- own 0090_market_sale_inference.sql, the most recent on disk at the time). This is 0091.
--
-- C10 (carta §4, row C10): "Un titular SOLO se muestra si existe fila... con source_url vivo,
-- title cotejado contra el HTML de origen y published_at real. Cero fabricación, cero atribución
-- no verificada. Hasta que exista esa ingesta (Fase 5), el panel de noticias NO EXISTE en la UI."
--
-- REAL SOURCES VERIFIED LIVE THIS SESSION (curl'd and read in full, not assumed): ANFAC
-- (anfac.com/feed/, real WordPress RSS 2.0, live items dated 2026-07-16), Faconauto
-- (faconauto.com/feed/, valid RSS 2.0 channel, zero items in this session's fetch — a real,
-- honest absence, not a broken feed), GANVAM (ganvam.es/feed/, valid RSS 2.0 channel with a
-- description confirming "Asociación Nacional de Vendedores de Vehículos a Motor..."). These are
-- the Spain-specific analogues of the carta's cited SMMT/KBA/DGT/ACEA pattern (carta §2.4).
--
-- V5 (carta §7, row V5): double verification per item — (a) content_hash of the ORIGINAL fetch
-- (sha256 of title+description, written at ingest time, never mutated after), (b) periodic
-- re-fetch of the item's OWN permalink (source_url) checking the title still appears in the live
-- page (pipeline/terminal/ingest_news.py's verify_item()) — updates verified_at on match. An item
-- whose verified_at has gone stale (see V5_FRESHNESS_DAYS, terminal.py) is NOT served — "si el
-- origen murió o cambió, el ítem se marca y no se muestra."

CREATE TABLE IF NOT EXISTS sector_news (
    news_ulid     TEXT PRIMARY KEY,
    source_name   TEXT NOT NULL,              -- 'ANFAC' | 'Faconauto' | 'GANVAM' | ...
    source_url    TEXT NOT NULL,               -- the article's OWN permalink (re-fetched for V5)
    title         TEXT NOT NULL,
    published_at  TIMESTAMPTZ,                 -- from the feed's <pubDate>, NULL if unparseable
    fetched_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    content_hash  TEXT NOT NULL,               -- sha256(title + description) at first ingest
    verified_at   TIMESTAMPTZ,                 -- last successful V5 re-fetch match; NULL = never verified
    symbol_keys   TEXT[] NOT NULL DEFAULT '{}', -- deterministic keyword match against market_symbol
    UNIQUE (source_url)
);

CREATE INDEX IF NOT EXISTS idx_sector_news_verified ON sector_news (verified_at DESC);
CREATE INDEX IF NOT EXISTS idx_sector_news_symbol_keys ON sector_news USING GIN (symbol_keys);

-- Rollback:
-- DROP TABLE IF EXISTS sector_news;
