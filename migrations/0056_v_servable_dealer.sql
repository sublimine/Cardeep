-- 0056_v_servable_dealer.sql — ONE canonical "car sales point" definition for the served census.
--
-- WHY. The owner caught the public "Puntos de venta" being inflated ~2.9x, and the data-quality audit
-- (workflow wqvzjds77) found THREE surfaces using THREE different scopes (stats.py kind<>'particular' =
-- 54.587; geo excludes unverified; the seal numerator ~18.298) so the headline count never matched what
-- the explorer paginated. This view is the single source of truth: a "car sales point" is a publish-gated
-- (servable_entity), ACTIVE entity that actually sells CARS — i.e. NOT a private platform listing
-- (kind='particular'), NOT a parts-only scrapyard (kind='desguace'), and (for garaje/talleres) only when
-- it actually has servable inventory. stats.py, geo.py and the seal will all read from here so the public
-- count == the paginated set == the certified scope.
--
-- COLUMNS:
--   entity_ulid / cdp_code / kind  the servable sales-point entity.
--   resolved_cdp_code              its deduped identity (count DISTINCT this for the sales-point count).
--   has_inventory                  TRUE iff it has >=1 servable vehicle (active sales point with stock).
--
-- HONEST COUNTS (verified live 2026-06-23): directory = count(DISTINCT resolved_cdp_code) ~= 36.3k;
-- with live inventory = count(DISTINCT resolved_cdp_code) WHERE has_inventory ~= 18.3k. (The old 54.587
-- lumped in ~35k empty shells + 2.3k desguaces; particulares — 352k platform listings — were never
-- sales points.)
--
-- WHY ZERO-RISK: a VIEW is a saved query — it touches no row, no FK, no served cdp_code. CREATE OR
-- REPLACE is idempotent. Reversible: DROP VIEW (see Rollback). It reads servable_entity / v_dealer_resolved
-- / servable_vehicle, all pre-existing.

CREATE OR REPLACE VIEW v_servable_dealer AS
SELECT se.entity_ulid,
       se.cdp_code,
       se.kind,
       vdr.resolved_cdp_code,
       EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid) AS has_inventory
  FROM servable_entity se
  JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
 WHERE se.status = 'active'
   AND se.kind::text NOT IN ('particular', 'desguace')
   AND (se.kind::text <> 'garaje'
        OR EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid));

COMMENT ON VIEW v_servable_dealer IS
    'Single source of truth for the car-sales-point census: publish-gated (servable_entity) active '
    'entities that sell cars (NOT particular/desguace; garaje only with inventory). has_inventory marks '
    'active sales points with live stock. Consumed by /stats, /geo and the seal. See '
    'plans/P-census-data-quality.md.';

-- Rollback:
-- DROP VIEW IF EXISTS v_servable_dealer;
