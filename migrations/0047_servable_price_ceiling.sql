-- 0047_servable_price_ceiling.sql — cap the served price at €5M (audit pass-4 D9, served-surface defense).
--
-- 0040 added the price>0 floor to servable_vehicle; 0045 added the status filter. But the view still
-- had NO upper bound, while sanitize_price (pipeline/price_sanity.py) caps the REAL used-market max at
-- €5M (Bugatti Chiron ~€3.6M + margin; >€5M is a sentinel/parse artifact). The bulk connectors
-- (coches_net/milanuncios/wallapop) bypass ingest's sanitize_price, so a future harvest could insert a
-- >€5M sentinel into vehicle.price — and servable_vehicle (price>0) WOULD serve it. This adds the
-- ceiling to the served surface so a sentinel can never reach a consumer, mirroring sanitize_price.
--
-- Today (verified): 0 available vehicles with price>5M -> servable_vehicle unchanged (1,697,247), zero
-- regression. Forward/defence-in-depth. NULL price (price-on-request) is still served. Additive,
-- idempotent (CREATE OR REPLACE), reversible (restore the 0045 definition).
--
-- NOTE (deeper root, documented not fixed here — harvest-phase): the bulk connectors should apply
-- sanitize_price at ingest so vehicle.price AND platform_price never carry junk in the table at all
-- (this view only protects the served vehicle surface; platform_price has its own served path). That
-- connector-sanitize wiring is tracked as D9-root (GitHub #35).

CREATE OR REPLACE VIEW servable_vehicle AS
  SELECT vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, currency,
         fuel, transmission, photo_url, photo_hash, vin_ref, recipe_version, status,
         first_seen, last_seen
    FROM vehicle v
   WHERE v.status = 'available'
     AND ((v.price > 0 AND v.price <= 5000000) OR v.price IS NULL)   -- NEW: <=€5M ceiling (mirror sanitize_price)
     AND NOT (EXISTS ( SELECT 1
            FROM gestion_item g
           WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'vehicle'::text
             AND g.subject_key = v.vehicle_ulid));

-- Rollback (restore the 0045 definition — price>0 floor only, no ceiling):
-- CREATE OR REPLACE VIEW servable_vehicle AS
--   SELECT vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, currency,
--          fuel, transmission, photo_url, photo_hash, vin_ref, recipe_version, status,
--          first_seen, last_seen
--     FROM vehicle v
--    WHERE v.status = 'available' AND (v.price > 0 OR v.price IS NULL)
--      AND NOT (EXISTS ( SELECT 1 FROM gestion_item g WHERE g.quarantines AND g.closed_at IS NULL
--              AND g.subject_type = 'vehicle'::text AND g.subject_key = v.vehicle_ulid));
