-- 0016_tiering_groups.sql — multi-axis classification (defense tier × group/family × role).
-- Replaces the flat is_tier1 boolean with a real organizational structure. Additive, reversible.

-- Defense tier: granular, NOT binary (is_tier1 stays as a derived convenience flag).
DO $$ BEGIN
  CREATE TYPE defense_tier AS ENUM (
    't0_open',          -- no real wall: open JSON API, sitemap, registry, OEM API
    't1_soft',          -- WAF present but serving to curl_cffi (Cloudflare-permissive, Imperva-serving)
    't2_js_challenge',  -- needs a stealth browser to mint a cookie / pass JS (DataDome, Imperva reese84)
    't3_hard_sensor',   -- active sensor (Akamai/Kasada/PerimeterX) — free stealth-Chromium still cracks it
    't4_spend_gated'    -- only paid residential/sensor works AFTER all free vectors are proven dead
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Group / family: the "grupos" axis — what KIND of source/operator this is, above the entity kind.
DO $$ BEGIN
  CREATE TYPE source_group AS ENUM (
    'marketplace_generalist',  -- C2C+pro classifieds (wallapop, milanuncios)
    'marketplace_motor',       -- car-specialist marketplaces (coches.net, autoscout24, autocasion, coches.com, motor.es)
    'oem_vo_portal',           -- manufacturer certified-used portals (renew, DasWeltAuto, Spoticar, MB Certified)
    'oem_dealer_network',      -- OEM dealer locators (Kia/MG/BYD/Skoda/Dacia/Hyundai/Mercedes/SEAT APIs)
    'chain',                   -- multi-branch retailers (Flexicar, OcasionPlus, Clicars, Autohero)
    'rentacar_vo',             -- rent-a-car selling ex-fleet (OK Mobility, Centauro, Record)
    'official_registry',       -- DGT, BORME, INE, datos.gob, CCAA registries
    'association',             -- FACONAUTO, GANVAM, AEDRA, AMDA, Gremi...
    'directory',               -- Paginas Amarillas, OSM, FSQ, Overture, generic directories
    'desguace_network',        -- AEDRA / DesguacesDirecto / scrapyard networks
    'long_tail_web'            -- the entity's own website (the mountain garage)
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Operational role of the entity within the market graph.
DO $$ BEGIN
  CREATE TYPE entity_role AS ENUM ('platform', 'dealer_network', 'chain', 'standalone_pos', 'registry', 'directory');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

ALTER TABLE entity ADD COLUMN IF NOT EXISTS defense_tier defense_tier;
ALTER TABLE entity ADD COLUMN IF NOT EXISTS source_group source_group;
ALTER TABLE entity ADD COLUMN IF NOT EXISTS role entity_role;

-- platform family ties co-defended siblings to ONE recipe (e.g. Adevinta/Schibsted: coches.net+milanuncios+fotocasa).
ALTER TABLE platform_meta ADD COLUMN IF NOT EXISTS family TEXT;

CREATE INDEX IF NOT EXISTS idx_entity_defense_tier ON entity (defense_tier) WHERE defense_tier IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entity_source_group ON entity (source_group) WHERE source_group IS NOT NULL;

-- Rollback:
-- ALTER TABLE platform_meta DROP COLUMN IF EXISTS family;
-- ALTER TABLE entity DROP COLUMN IF EXISTS role;
-- ALTER TABLE entity DROP COLUMN IF EXISTS source_group;
-- ALTER TABLE entity DROP COLUMN IF EXISTS defense_tier;
-- DROP TYPE IF EXISTS entity_role, source_group, defense_tier;
