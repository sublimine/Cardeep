-- 0040_servable_price_floor.sql — hide zero/negative-priced junk at the served surface
-- (audit P2 A-zero-and-tiny-prices; complements the price_trap detector, which by design cannot
-- see price<=0 — its base CTE filters price>0 and ln(0) is undefined).
--
-- The served `servable_vehicle` view excluded only quarantined rows; it did NOT guard the price.
-- A vehicle priced 0 or negative is junk data, never a real listing. This adds a surgical guard
-- that removes EXACTLY price<=0 and nothing else: positive AND NULL prices are preserved (NULL =
-- "price on request", a legitimate listing the audit did not flag). Today price<=0 & available = 0
-- rows (already sanitized at ingest by pipeline/price_sanity.py), so this is a forward/defence-in-
-- depth guard: even if a future ingest path bypasses sanitation, the served surface stays clean.
-- Additive, idempotent (CREATE OR REPLACE), fully reversible.

CREATE OR REPLACE VIEW servable_vehicle AS
  SELECT vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, currency,
         fuel, transmission, photo_url, photo_hash, vin_ref, recipe_version, status,
         first_seen, last_seen
    FROM vehicle v
   WHERE (v.price > 0 OR v.price IS NULL)                 -- NEW: drop zero/negative junk prices
     AND NOT (EXISTS ( SELECT 1
            FROM gestion_item g
           WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'vehicle'::text
             AND g.subject_key = v.vehicle_ulid));

-- Rollback:
-- CREATE OR REPLACE VIEW servable_vehicle AS
--   SELECT vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, currency,
--          fuel, transmission, photo_url, photo_hash, vin_ref, recipe_version, status,
--          first_seen, last_seen
--     FROM vehicle v
--    WHERE NOT (EXISTS ( SELECT 1
--             FROM gestion_item g
--            WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'vehicle'::text
--              AND g.subject_key = v.vehicle_ulid));
