-- 0019_listing_segment.sql — segment flag on the platform <-> vehicle edge.
-- Additive + reversible. A marketplace lists the SAME catalog under several offer
-- segments (used / new / km0 / renting); the segment is a property of THIS listing on
-- THIS platform, not of the car's owner — so it lives on platform_listing, the edge.
--
-- coches.net exposes the segments via the search gateway's filters.offerTypeIds:
--   used     = the default segunda-mano drain (offerTypeIds unset / [0])
--   new      = offerTypeIds [1]            (offerType.literal 'Nuevo')
--   km0      = offerTypeIds [2,3,4,5]      (offerType.literal 'Km0')
--   renting  = offerTypeIds [10]           (offerType.literal 'Subscription')
--
-- Existing rows predate the flag and were all drained from the used surface, so the
-- column DEFAULTs to 'used' and backfills every current edge to 'used' (one statement,
-- no row rewrite beyond the default fill). New segment harvests stamp their own value.

ALTER TABLE platform_listing
  ADD COLUMN IF NOT EXISTS segment TEXT NOT NULL DEFAULT 'used';

-- Constrain to the known offer segments so a typo can never enter the edge.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'platform_listing_segment_chk'
  ) THEN
    ALTER TABLE platform_listing
      ADD CONSTRAINT platform_listing_segment_chk
      CHECK (segment IN ('used', 'new', 'km0', 'renting'));
  END IF;
END $$;

-- Slice queries ("all NEW cars on coches.net") hit (platform, segment).
CREATE INDEX IF NOT EXISTS idx_pl_segment
  ON platform_listing (platform_entity_ulid, segment);

-- Rollback:
-- DROP INDEX IF EXISTS idx_pl_segment;
-- ALTER TABLE platform_listing DROP CONSTRAINT IF EXISTS platform_listing_segment_chk;
-- ALTER TABLE platform_listing DROP COLUMN IF EXISTS segment;
