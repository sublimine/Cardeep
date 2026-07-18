-- 0083_vin_ref_remediation.sql — 04-arbitrage F6 (identidad-captura): vin_ref contamination fix.
--
-- CRITICAL FINDING (F6 audit, 2026-07-18): 2,520,623 of 2,670,828 vehicles (94.4%) carry a
-- NON-NULL vin_ref, but only 41,510 (1.6%) are well-formed 17-character VINs (standard charset
-- A-H/J-N/P/R-Z/0-9, excluding I/O/Q to avoid 1/0 confusion). The remaining 2,479,113 rows hold
-- source-native LISTING IDS masquerading as VINs — traced to a real code bug: several harvester
-- modules (verified live: pipeline/sources/autoscout24.py:208,
-- `vin_ref=str(raw.get("id") or raw.get("identifier") or "")`, feeding source_keys as24/
-- as24_wholesale/autoscout24_census, ~680k rows) store the source's own listing id into vin_ref
-- instead of leaving it NULL when no real VIN is available on that surface (contrast
-- pipeline/platform/oem_ford_wholesale.py, which correctly does exactly that: "matrícula is not
-- a VIN, so vin_ref stays NULL"). ``platform_listing.listing_ref`` already exists as the CORRECT
-- home for a source-native listing id (migrations/0009:20) — vin_ref was never meant to double
-- as a general dedupe key.
--
-- Impact: any cross-platform VIN-match consumer (02-history-reports' link_lifetimes.py,
-- scripts/cross_platform_dedup_watermark.py's pHash arm) that trusted a non-null vin_ref as "this
-- is a real VIN" was silently poisoned by ~2.48M fake identifiers — worse than the column being
-- honestly empty, because a shared fake ID CAN coincidentally collide across sources and produce
-- a false cross-platform match.
--
-- This migration is the DATA-LEVEL remediation only: it NULLs every vin_ref that does not match
-- the standard 17-character VIN shape, protecting every current and future consumer immediately.
-- It does NOT fix the harvester code that WROTE the contamination (pipeline/sources/
-- autoscout24.py and an audited list of ~15 other connector modules following the same
-- anti-pattern — see plans/cardeep-omni/04-arbitrage.md F6 section for the full source-by-source
-- table) — that is a separate, larger, per-connector code-fix pass (declared scope boundary, not
-- hidden) so the contamination does NOT return on the next harvest for those sources until that
-- follow-up lands.
--
-- Verified before writing this migration (live cardeep-pg, 2026-07-18):
--   total non-null vin_ref:            2,520,623
--   to be NULLed (not valid VIN shape): 2,479,113
--   to be KEPT (valid VIN shape):          41,510
--
-- Idempotent: the WHERE clause only ever matches non-conforming values; re-running after the
-- first application matches 0 rows. Reversible in the sense that no VALID VIN is ever touched —
-- the removed values were never real VINs, so there is nothing correct to roll back to (the
-- "rollback" of a data-quality fix is simply not re-running it).

UPDATE vehicle
   SET vin_ref = NULL
 WHERE vin_ref IS NOT NULL
   AND upper(vin_ref) !~ '^[A-HJ-NPR-Z0-9]{17}$';

-- Rollback: not applicable (see header — nothing valid is removed by this migration).
