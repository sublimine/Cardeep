-- 0080_fleet_ops.sql — 03-garage-fleet F3: the dealer's OWN write layer.
--
-- FIRST real write surface of the whole product (00-MASTER.md recon: "Cero
-- endpoints de escritura" — grep of @router.(post|put|patch|delete) over
-- services/api/ returned 0 results before this block). Architecture decision
-- (carta §5, "censo (capa scraper) y workspace (capa dealer) no comparten
-- tablas de escritura"): fleet_ops/fleet_ops_event are ADDITIVE annotations by
-- vehicle_ulid REFERENCE — they never UPDATE `vehicle`/`vehicle_event` (the
-- append-only census scraper output, migrations/0003 + its guards in 0034/0035).
--
-- Two tables, mirroring the vehicle/vehicle_event pattern already proven in 0003:
--   fleet_ops        — current state per vehicle (status K13, purchase_cost,
--                       target_price, notes). One row per vehicle that has EVER
--                       been touched by the dealer; a vehicle with no row is
--                       implicitly status='entrada' (no pre-seeding of 468 rows
--                       for a dealer who has touched none of them).
--   fleet_ops_event   — append-only audit trail of every write (K15 override
--                       capture included): actor_user_ulid + observed_at +
--                       from_value/to_value JSONB, so "quien cambió qué y
--                       cuándo" is always reconstructable by replay (carta §7,
--                       K13 row: "replay de fleet_ops_event reconstruye el
--                       estado; el replay manda").
--
-- Authorization for every write lives in the router (services/api/routers/
-- dealer_ops.py), not here — but the FK to `vehicle` and `app_user` still
-- enforces referential integrity at the DB layer regardless of the app code.
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

CREATE TABLE IF NOT EXISTS fleet_ops (
    vehicle_ulid          TEXT PRIMARY KEY REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    status                TEXT NOT NULL DEFAULT 'entrada'
        CHECK (status IN ('entrada', 'preparacion', 'publicado', 'reservado', 'vendido', 'entregado')),
    purchase_cost         NUMERIC(12,2),
    target_price          NUMERIC(12,2),
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by_user_ulid  TEXT NOT NULL REFERENCES app_user(user_ulid)
);

CREATE INDEX IF NOT EXISTS idx_fleet_ops_status ON fleet_ops (status);

-- fleet_ops_event: append-only audit trail. event_type covers every write kind
-- the router exposes; PRICE_OVERRIDE additionally carries reason_category +
-- delta_vs_median (K15 — closes the Tekion "override gap" cited in carta §2.1:
-- reason + actor + delta vs the market suggestion, never just the new number).
CREATE TABLE IF NOT EXISTS fleet_ops_event (
    event_ulid        TEXT PRIMARY KEY,
    vehicle_ulid      TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    actor_user_ulid   TEXT NOT NULL REFERENCES app_user(user_ulid),
    event_type        TEXT NOT NULL
        CHECK (event_type IN ('STATUS_CHANGE', 'COST_SET', 'PRICE_OVERRIDE', 'NOTE_SET')),
    from_value        JSONB,
    to_value          JSONB,
    reason_category   TEXT,   -- required by the router for PRICE_OVERRIDE only
    delta_vs_median    NUMERIC,  -- K15: (target_price / segment_p50) - 1 at event time, from 01's M2
    observed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fleet_ops_event_vehicle ON fleet_ops_event (vehicle_ulid, observed_at);
CREATE INDEX IF NOT EXISTS idx_fleet_ops_event_actor ON fleet_ops_event (actor_user_ulid, observed_at);

-- Append-only enforcement (same primitive as 0005/0034/0035 — cardeep_block_mutation()
-- references only TG_TABLE_NAME/TG_OP, reused verbatim). Unlike vehicle_event,
-- fleet_ops_event has NO legitimate re-pointing use case, so the guard is total:
-- no UPDATE, no DELETE, no TRUNCATE, ever.
DROP TRIGGER IF EXISTS trg_fleet_ops_event_noupd ON fleet_ops_event;
CREATE TRIGGER trg_fleet_ops_event_noupd
  BEFORE UPDATE OR DELETE ON fleet_ops_event
  FOR EACH ROW EXECUTE FUNCTION cardeep_block_mutation();

DROP TRIGGER IF EXISTS trg_fleet_ops_event_notrunc ON fleet_ops_event;
CREATE TRIGGER trg_fleet_ops_event_notrunc
  BEFORE TRUNCATE ON fleet_ops_event
  FOR EACH STATEMENT EXECUTE FUNCTION cardeep_block_mutation();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_fleet_ops_event_notrunc ON fleet_ops_event;
-- DROP TRIGGER IF EXISTS trg_fleet_ops_event_noupd ON fleet_ops_event;
-- DROP TABLE IF EXISTS fleet_ops_event;
-- DROP TABLE IF EXISTS fleet_ops;
