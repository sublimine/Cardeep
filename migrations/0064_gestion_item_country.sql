-- 0064_gestion_item_country.sql — country-scope the gestion ledger for aggregated detectors.
-- Red-team final: gestion_item carried no country_code, and its UNIQUE(dedupe_key) collided
-- cross-country for the BY-KIND aggregated detectors — staleness storm (subject "kind:{kind}",
-- detect.py) and coverage_gap (subject "{kind}"). In a 2-country census an ES garaje alert and a
-- DE garaje alert in the same daily bucket minted the SAME dedupe_key and collapsed into one row,
-- erasing per-country granularity for those alerts. (Quarantine / per-subject items key on
-- cdp_code / vehicle_ulid and are already country-safe — unaffected.) The detectors now thread the
-- country into the dedupe_key (e.g. 'staleness|ES|kind:garaje|{bucket}') and write country_code
-- into this column via route.open_or_refresh.
--
-- Additive, idempotent (ADD COLUMN IF NOT EXISTS), reversible. ES is byte-identical: the
-- single-tenant census is entirely 'ES', so every existing row keeps country_code 'ES' via the
-- DEFAULT with no backfill and no churn.

ALTER TABLE gestion_item ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

-- Rollback:
-- ALTER TABLE gestion_item DROP COLUMN IF EXISTS country_code;
