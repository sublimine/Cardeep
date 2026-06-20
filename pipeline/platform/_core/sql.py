"""P05 fase 2 — shared SQL for the platform connectors (strangler core).

BULK_INSERT_VEHICLES is the ONE bulk vehicle upsert that 27 connectors had hand-copied byte-for-
byte (14 columns, unnest of 13 typed arrays, ON CONFLICT (entity_ulid, deep_link) DO NOTHING).
Connectors whose vehicle row genuinely differs (no transmission, price NULL, scalar entity_ulid,
fewer columns) keep their own literal on purpose — only the identical copies collapse here.
"""
from __future__ import annotations

BULK_INSERT_VEHICLES = """
INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
        year, km, price, fuel, transmission, photo_url, vin_ref, status)
SELECT u.vehicle_ulid, u.entity_ulid, u.deep_link, u.title, u.make, u.model,
       u.year, u.km, u.price, u.fuel, u.transmission, u.photo_url, u.vin_ref, 'available'
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[],
              $7::int[], $8::int[], $9::numeric[], $10::text[], $11::text[], $12::text[],
              $13::text[])
       AS u(vehicle_ulid, entity_ulid, deep_link, title, make, model,
            year, km, price, fuel, transmission, photo_url, vin_ref)
ON CONFLICT (entity_ulid, deep_link) DO NOTHING
"""
