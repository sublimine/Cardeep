"""P05 fase 2 — shared SQL for the platform connectors (strangler core).

Each constant here is ONE bulk statement that many connectors had hand-copied byte-identical. They
are collapsed to a single source of truth and imported (aliased to the connector's local name).
Connectors whose statement genuinely differs keep their own literal on purpose — only the identical
copies collapse here (see tests/test_bulk_insert_vehicles_parity for the anti-drift guard).
"""
from __future__ import annotations

# Bulk vehicle insert (14 cols, unnest of 13 typed arrays). 27 connectors; the 8 with a different
# vehicle row (no transmission, price NULL, scalar entity_ulid, fewer columns) keep their literal.
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

# Generic entity_source link upsert by cdp_code (join each unnested cdp_code to its entity, refresh
# seen_at). The connectors call it _BULK_UPSERT_OWNER_SOURCES or _BULK_UPSERT_DEALER_SOURCES — same
# statement, two local synonyms — both alias this one canonical constant.
BULK_UPSERT_ENTITY_SOURCE = """
INSERT INTO entity_source (entity_ulid, source_key, source_ref)
SELECT e.entity_ulid, $3, u.source_ref
  FROM unnest($1::text[], $2::text[]) AS u(cdp_code, source_ref)
  JOIN entity e ON e.cdp_code = u.cdp_code
ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()
"""

# Touch the vehicles still present this window: refresh last_seen + mark available (the delta loop
# uses this to keep a re-seen listing alive). 35 connectors, one identical statement.
BULK_TOUCH_VEHICLES = """
UPDATE vehicle v SET last_seen = now(), status = 'available'
  FROM unnest($1::text[]) AS u(vehicle_ulid)
 WHERE v.vehicle_ulid = u.vehicle_ulid
"""

# Emit a NEW vehicle_event per freshly-inserted listing (event_type NEW, new_value JSONB). 35
# connectors, one identical statement.
BULK_INSERT_EVENTS = """
INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
        old_value, new_value)
SELECT u.event_ulid, u.vehicle_ulid, u.entity_ulid, 'NEW', NULL, u.new_value::jsonb
  FROM unnest($1::text[], $2::text[], $3::text[], $4::text[])
       AS u(event_ulid, vehicle_ulid, entity_ulid, new_value)
"""
