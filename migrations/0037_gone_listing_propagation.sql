-- 0037_gone_listing_propagation.sql — vehicle 'gone' removes its platform_listing (audit P2 A-gone-listed-desync)
--
-- The soft-GONE sweep (delta._MARK_GONE / ingest / generic_dealer_site) sets vehicle.status='gone' but
-- never propagated to platform_listing, leaving rows (gone, listed, removed_at NULL) — a platform-keyed
-- serving path would still show a gone car as a live listing. A single AFTER UPDATE trigger covers ALL
-- gone-paths (one point of truth) instead of patching three call sites.
--
-- Only 'gone' removes the listing — 'reserved' is still live on the platform. Eviction (0033) hard-DELETEs
-- the vehicle and the FK ON DELETE CASCADE already removes its platform_listing, so that path is unaffected.
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

CREATE OR REPLACE FUNCTION cdp_gone_removes_listing() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE platform_listing
     SET status = 'removed', removed_at = now()
   WHERE vehicle_ulid = NEW.vehicle_ulid AND status = 'listed';
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_vehicle_gone_removes_listing ON vehicle;
CREATE TRIGGER trg_vehicle_gone_removes_listing
  AFTER UPDATE OF status ON vehicle
  FOR EACH ROW WHEN (NEW.status = 'gone' AND OLD.status IS DISTINCT FROM 'gone')
  EXECUTE FUNCTION cdp_gone_removes_listing();

-- Backfill the existing desync (gone vehicles whose listing is still 'listed').
UPDATE platform_listing pl
   SET status = 'removed', removed_at = now()
  FROM vehicle v
 WHERE pl.vehicle_ulid = v.vehicle_ulid AND v.status = 'gone' AND pl.status = 'listed';

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_vehicle_gone_removes_listing ON vehicle;
-- DROP FUNCTION IF EXISTS cdp_gone_removes_listing();
-- (the backfilled removed_at values are not reverted — they are correct.)
