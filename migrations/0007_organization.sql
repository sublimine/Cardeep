-- 0007_organization.sql — the chain/group/brand/operator layer (fixes failure #3).
-- Additive + reversible. 03-DATA-MODEL §3.3-3.4.

-- The organization node: chains, dealer groups, rent-a-car brands, OEMs, operators.
-- An org owns NO inventory directly; its inventory is the union over its branches (a query).
CREATE TABLE IF NOT EXISTS organization (
    org_ulid   TEXT PRIMARY KEY CHECK (org_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
    org_code   TEXT NOT NULL UNIQUE,        -- ORG-ES-{b32(name|domain)}, immutable
    name       TEXT NOT NULL,
    org_type   org_type NOT NULL,
    website    TEXT,
    hq_province_code CHAR(2) REFERENCES geo_province(code),
    branch_count INT NOT NULL DEFAULT 0,    -- denormalized count(entity WHERE org_id=...)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_org_type ON organization (org_type);
CREATE INDEX IF NOT EXISTS idx_org_name_trgm ON organization USING gin (name gin_trgm_ops);

-- Wire the entity.org_id FK now that organization exists (column added in 0006).
ALTER TABLE entity DROP CONSTRAINT IF EXISTS fk_entity_org;
ALTER TABLE entity
  ADD CONSTRAINT fk_entity_org FOREIGN KEY (org_id)
  REFERENCES organization(org_ulid) ON DELETE SET NULL;

-- entity_source gains first_seen: the current table has only seen_at (overwritten on upsert),
-- losing the FIRST attestation date the capture-recapture estimator needs. Backfill from seen_at.
ALTER TABLE entity_source ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ;
UPDATE entity_source SET first_seen = seen_at WHERE first_seen IS NULL;
ALTER TABLE entity_source ALTER COLUMN first_seen SET DEFAULT now();
ALTER TABLE entity_source ALTER COLUMN first_seen SET NOT NULL;

-- Keep entity.attest_count consistent: recount orthogonal sources on every new attestation.
CREATE OR REPLACE FUNCTION entity_bump_attest() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE entity
     SET attest_count = (SELECT count(*) FROM entity_source WHERE entity_ulid = NEW.entity_ulid)
   WHERE entity_ulid = NEW.entity_ulid;
  RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_entity_attest ON entity_source;
CREATE TRIGGER trg_entity_attest AFTER INSERT ON entity_source
  FOR EACH ROW EXECUTE FUNCTION entity_bump_attest();

-- Rollback:
-- DROP TRIGGER IF EXISTS trg_entity_attest ON entity_source;
-- DROP FUNCTION IF EXISTS entity_bump_attest();
-- ALTER TABLE entity_source ALTER COLUMN first_seen DROP NOT NULL;
-- ALTER TABLE entity_source ALTER COLUMN first_seen DROP DEFAULT;
-- ALTER TABLE entity_source DROP COLUMN IF EXISTS first_seen;
-- ALTER TABLE entity DROP CONSTRAINT IF EXISTS fk_entity_org;
-- DROP INDEX IF EXISTS idx_org_name_trgm;
-- DROP INDEX IF EXISTS idx_org_type;
-- DROP TABLE IF EXISTS organization;
