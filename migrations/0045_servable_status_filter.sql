-- 0045_servable_status_filter.sql — make servable_vehicle the TRUE live-served surface: exclude
-- 'gone' vehicles (coherence audit 2026-06-16, Inquisitor invariant pass INV10).
--
-- ROOT DEFECT FOUND: servable_vehicle (the "publish-gate view" — migration 0031 states verbatim
-- "The API reads through these views, never the raw tables ... the instant a quarantining item
-- opens, the subject vanishes from every served surface — mechanically, not by promise") guarded
-- price and quarantine but NOT status. It therefore contained 7,721 status='gone' vehicles
-- (sold/withdrawn). A 'gone' car is a baja in the delta/history, never live inventory — exposing it
-- on the servable surface is a lie at the served surface.
--   (The API routers happened to filter status='available' themselves on the RAW table, so the live
--    API output did not leak gone cars — but that very fact proved the API was BYPASSING this view,
--    breaking the 0031 invariant and leaving the quarantine mechanism inert for served data. The
--    companion router change routes those four live-inventory reads back through this view, so all
--    three guards — status, price, quarantine — apply at one source of truth.)
--
-- Fix: add status='available'. servable_vehicle now == exactly what may be served live:
-- available AND (price>0 OR price IS NULL) AND not-quarantined. Today (verified live): gone=7,721
-- dropped, price<=0=0 globally, open-quarantine=0  ->  1,704,968 -> 1,697,247. Available cars are
-- unchanged, so the routed API endpoints (which already filtered status='available') see identical
-- output today and become correct the moment a quarantine opens.
-- Additive guard, idempotent (CREATE OR REPLACE), reversible (rollback = the 0040 definition).

CREATE OR REPLACE VIEW servable_vehicle AS
  SELECT vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, currency,
         fuel, transmission, photo_url, photo_hash, vin_ref, recipe_version, status,
         first_seen, last_seen
    FROM vehicle v
   WHERE v.status = 'available'                          -- NEW: a 'gone' car is a baja, never live stock
     AND (v.price > 0 OR v.price IS NULL)                -- drop zero/negative junk prices (0040)
     AND NOT (EXISTS ( SELECT 1
            FROM gestion_item g
           WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'vehicle'::text
             AND g.subject_key = v.vehicle_ulid));

-- Rollback (restore the 0040 definition — price + quarantine guards, no status filter):
-- CREATE OR REPLACE VIEW servable_vehicle AS
--   SELECT vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, currency,
--          fuel, transmission, photo_url, photo_hash, vin_ref, recipe_version, status,
--          first_seen, last_seen
--     FROM vehicle v
--    WHERE (v.price > 0 OR v.price IS NULL)
--      AND NOT (EXISTS ( SELECT 1
--             FROM gestion_item g
--            WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'vehicle'::text
--              AND g.subject_key = v.vehicle_ulid));
