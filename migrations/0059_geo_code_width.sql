-- 0059_geo_code_width.sql -- widen the geo identity code columns from the ES-sized
-- CHAR(2)/CHAR(5) to VARCHAR(8)/VARCHAR(16) so real non-ES administrative codes fit,
-- closing the two width gaps Project 360-A locked as explicit guards
-- (test_country_isolation_multicountry.py gaps A + B):
--   (A) FR overseas department (DOM) codes are 3 digits ('971' Guadeloupe .. '976'
--       Mayotte) -> would not fit geo_province.code CHAR(2).
--   (B) IT ISTAT comune codes are 6 digits ('058091' Roma, '015146' Milano)
--       -> would not fit geo_municipality.code CHAR(5).
--
-- THE INVARIANT (non-negotiable): every existing ES row stays byte-identical. CHAR(n)
-- blank-pads a stored value to n; VARCHAR does not. Every ES code is EXACTLY full width
-- (province 2-char 01-52, municipality 5-digit INE), so NO ES value carries padding and
-- the CHAR->VARCHAR conversion is a pure 1:1 identity (verified live: '28'::char(2)::
-- varchar(8) = '28' len 2; '28079'::char(5)::varchar(16) = '28079' len 5). The composite
-- PK (country_code, code), all 6 composite FKs, and the two ES-guarded CHECKs are preserved.
-- (The only deliberate semantic change is that bpchar's trailing-space-insensitive equality
-- becomes varchar exact equality -- immaterial because no ES code is sub-width or padded.)
--
-- WIDTH JUSTIFICATION:
--   VARCHAR(8)  province: FR DOM 3-digit, German Kreis AGS 5-digit, NUTS-2/3 up to 5
--               alphanumeric (e.g. 'ITI43') -- 8 is a safe ceiling for any EU sub-national
--               province/department/Kreis identifier with headroom.
--   VARCHAR(16) municipality: IT ISTAT 6-digit, German AGS 8-digit, FR INSEE 5 (2A/2B),
--               Polish TERYT 7-digit, plus composite/alphanumeric LAU schemes -- 16 is
--               generous headroom for any EU municipality/LAU code.
--
-- VERIFIED LIVE against the dry-run cardeep DB (:5434, @0058) before writing:
--   * The 8 code columns are CHAR(2) (province family) / CHAR(5) (municipality family).
--   * geo_province PK = (country_code, code); geo_municipality PK = (country_code, code).
--   * Exactly 6 COMPOSITE FKs target the geo PKs (post-0053):
--       entity_province_code_fkey, entity_municipality_code_fkey, geo_comarca_province_code_fkey,
--       geo_municipality_province_code_fkey, denominator_estimate_province_code_fkey,
--       organization_hq_province_code_fkey -- all FOREIGN KEY (country_code, <col>)
--       REFERENCES geo_*(country_code, code), MATCH SIMPLE.
--   * 6 VIEWS depend (directly or transitively) on the entity / denominator_estimate code
--     columns and therefore BLOCK ALTER COLUMN TYPE ('cannot alter type of a column used by
--     a view'): servable_entity, v_servable_dealer (-> servable_entity), v_province_seal,
--     v_canonical_deduped_draft, v_dealer_recipe, v_resolved_dealer. NO view depends on
--     geo_province.code / geo_municipality.code directly. They are dropped (dependents
--     first) and recreated BYTE-IDENTICAL (bodies are the live pg_get_viewdef) after the swap.
--   * Two ES-shaped CHECKs (country-guarded to ES in 0053) reference the code columns and
--     are PRESERVED unchanged -- they cast to ::text and survive the type change:
--       geo_municipality.municipality_province_prefix, entity.chk_entity_muni_province.
--   * One column-scoped TRIGGER binds entity.municipality_code (so it BLOCKS the type change,
--     'cannot alter type of a column used in a trigger definition'): trg_entity_set_comarca
--     (BEFORE INSERT OR UPDATE OF municipality_code, origin 0018_comarca.sql:38-40). It is
--     dropped before the swap and recreated byte-identical after; its function
--     entity_set_comarca() carries no column-type dependency and is left untouched.
--
-- ORDERING (one txn, the runner wraps the whole migration -- NO BEGIN/COMMIT here, per the
-- scripts/migrate.py convention shared by 0052/0053): (1) drop the 6 dependent views
-- (dependents first); (2) drop the 6 composite FKs + the column-scoped trigger; (3) ALTER
-- the 8 columns to VARCHAR; (4) recreate the 6 composite FKs (guarded) + the trigger;
-- (5) recreate the 6 views (bases first).
-- IDEMPOTENT: DROP ... IF EXISTS, ALTER ... TYPE varchar is a no-op when already varchar,
-- each FK ADD is DO-block guarded, each view is CREATE OR REPLACE. The schema_migrations
-- ledger skips an already-applied 0059 anyway.

-- 1. Drop the 6 views that depend on the columns being widened (dependents BEFORE bases:
--    v_servable_dealer -> servable_entity). v_dealer_resolved is NOT touched (it does not
--    reference any widened column); v_province_seal is recreated still referencing it.
DROP VIEW IF EXISTS v_servable_dealer;
DROP VIEW IF EXISTS servable_entity;
DROP VIEW IF EXISTS v_province_seal;
DROP VIEW IF EXISTS v_canonical_deduped_draft;
DROP VIEW IF EXISTS v_dealer_recipe;
DROP VIEW IF EXISTS v_resolved_dealer;

-- 2. Drop the 6 composite FKs that target the geo PKs (IF EXISTS = idempotent). The PK
--    columns cannot change type while a child FK references them.
ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_province_code_fkey;
ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_municipality_code_fkey;
ALTER TABLE geo_comarca          DROP CONSTRAINT IF EXISTS geo_comarca_province_code_fkey;
ALTER TABLE geo_municipality     DROP CONSTRAINT IF EXISTS geo_municipality_province_code_fkey;
ALTER TABLE denominator_estimate DROP CONSTRAINT IF EXISTS denominator_estimate_province_code_fkey;
ALTER TABLE organization         DROP CONSTRAINT IF EXISTS organization_hq_province_code_fkey;

-- 2b. Drop the column-scoped trigger that binds entity.municipality_code (it BLOCKS the type
--     change). The function entity_set_comarca() is NOT dropped (no column-type dependency);
--     the trigger is recreated byte-identical in section 4b.
DROP TRIGGER IF EXISTS trg_entity_set_comarca ON entity;

-- 3. Widen the PK-source columns AND every FK-referrer to the SAME VARCHAR type. The USING
--    cast is a 1:1 identity for the exact-width ES data (no padding to strip). The composite
--    PK indexes and the secondary indexes on these columns are rebuilt automatically; the two
--    ES-guarded CHECKs are re-validated automatically (every ES row still satisfies them).
--    Province family -> VARCHAR(8):
ALTER TABLE geo_province         ALTER COLUMN code              TYPE varchar(8)  USING code::varchar(8);
ALTER TABLE geo_comarca          ALTER COLUMN province_code     TYPE varchar(8)  USING province_code::varchar(8);
ALTER TABLE geo_municipality     ALTER COLUMN province_code     TYPE varchar(8)  USING province_code::varchar(8);
ALTER TABLE entity               ALTER COLUMN province_code     TYPE varchar(8)  USING province_code::varchar(8);
ALTER TABLE denominator_estimate ALTER COLUMN province_code     TYPE varchar(8)  USING province_code::varchar(8);
ALTER TABLE organization         ALTER COLUMN hq_province_code  TYPE varchar(8)  USING hq_province_code::varchar(8);
--    Municipality family -> VARCHAR(16):
ALTER TABLE geo_municipality     ALTER COLUMN code              TYPE varchar(16) USING code::varchar(16);
ALTER TABLE entity               ALTER COLUMN municipality_code TYPE varchar(16) USING municipality_code::varchar(16);

-- 4. Recreate the 6 composite FKs exactly as 0053 defined them (MATCH SIMPLE; both sides now
--    VARCHAR of matching width). Each ADD is DO-block guarded so a re-run is a no-op.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'geo_comarca_province_code_fkey'
                 AND conrelid = 'geo_comarca'::regclass) THEN
    ALTER TABLE geo_comarca ADD CONSTRAINT geo_comarca_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'geo_municipality_province_code_fkey'
                 AND conrelid = 'geo_municipality'::regclass) THEN
    ALTER TABLE geo_municipality ADD CONSTRAINT geo_municipality_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'entity_province_code_fkey'
                 AND conrelid = 'entity'::regclass) THEN
    ALTER TABLE entity ADD CONSTRAINT entity_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'entity_municipality_code_fkey'
                 AND conrelid = 'entity'::regclass) THEN
    ALTER TABLE entity ADD CONSTRAINT entity_municipality_code_fkey
      FOREIGN KEY (country_code, municipality_code) REFERENCES geo_municipality (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'denominator_estimate_province_code_fkey'
                 AND conrelid = 'denominator_estimate'::regclass) THEN
    ALTER TABLE denominator_estimate ADD CONSTRAINT denominator_estimate_province_code_fkey
      FOREIGN KEY (country_code, province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'organization_hq_province_code_fkey'
                 AND conrelid = 'organization'::regclass) THEN
    ALTER TABLE organization ADD CONSTRAINT organization_hq_province_code_fkey
      FOREIGN KEY (country_code, hq_province_code) REFERENCES geo_province (country_code, code);
  END IF;
END
$$;

-- 4b. Recreate the column-scoped trigger byte-identical (origin 0018_comarca.sql:38-40),
--     now bound to the widened entity.municipality_code.
DROP TRIGGER IF EXISTS trg_entity_set_comarca ON entity;
CREATE TRIGGER trg_entity_set_comarca
    BEFORE INSERT OR UPDATE OF municipality_code ON entity
    FOR EACH ROW EXECUTE FUNCTION entity_set_comarca();

-- 5. Recreate the 6 views BYTE-IDENTICAL (bodies are the live pg_get_viewdef captures),
--    bases before dependents (servable_entity before v_servable_dealer).

CREATE OR REPLACE VIEW servable_entity AS
 SELECT entity_ulid,
    cdp_code,
    kind,
    legal_name,
    trade_name,
    cif,
    cnae,
    province_code,
    municipality_code,
    comarca_id,
    address,
    postcode,
    lat,
    lon,
    phone,
    email,
    website,
    website_waf,
    is_tier1,
    status,
    recipe_version,
    first_discovered_source,
    created_at,
    last_seen,
    org_id,
    sells_cars,
    kind_source,
    geocode_source,
    geocode_precision,
    defense_detail,
    closed_at,
    close_reason,
    canonical_key,
    attest_count,
    defense_tier,
    source_group,
    role,
    country_code
   FROM entity e
  WHERE (status <> ALL (ARRAY['evicted'::entity_status, 'closed'::entity_status])) AND NOT (EXISTS ( SELECT 1
           FROM gestion_item g
          WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type = 'entity'::text AND g.subject_key = e.cdp_code));

CREATE OR REPLACE VIEW v_servable_dealer AS
 SELECT se.entity_ulid,
    se.cdp_code,
    se.kind,
    vdr.resolved_cdp_code,
    (EXISTS ( SELECT 1
           FROM servable_vehicle sv
          WHERE sv.entity_ulid = se.entity_ulid)) AS has_inventory,
    se.country_code
   FROM servable_entity se
     JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
  WHERE se.status = 'active'::entity_status AND (se.kind::text <> ALL (ARRAY['particular'::text, 'desguace'::text])) AND (se.kind::text <> 'garaje'::text OR (EXISTS ( SELECT 1
           FROM servable_vehicle sv
          WHERE sv.entity_ulid = se.entity_ulid)));

CREATE OR REPLACE VIEW v_resolved_dealer AS
 SELECT e.entity_ulid,
    e.cdp_code,
    e.trade_name,
    e.kind,
    e.province_code,
    er.resolved_dealer_ulid,
    rd.cdp_code AS resolved_dealer_cdp_code,
    rd.trade_name AS resolved_dealer_name,
    er.signal,
    er.probability,
    er.run_id
   FROM entity_resolution er
     JOIN entity e ON e.entity_ulid = er.entity_ulid
     JOIN entity rd ON rd.entity_ulid = er.resolved_dealer_ulid
  WHERE er.run_id = (( SELECT entity_resolution_run.run_id
           FROM entity_resolution_run
          WHERE entity_resolution_run.vam_verified = true
          ORDER BY entity_resolution_run.run_at DESC
         LIMIT 1)) AND (e.kind = ANY (ARRAY['compraventa'::entity_kind, 'concesionario_oficial'::entity_kind, 'garaje'::entity_kind]));

CREATE OR REPLACE VIEW v_dealer_recipe AS
 WITH connector_source_keys AS (
         SELECT DISTINCT es.source_key
           FROM entity_source es
             JOIN entity e ON e.entity_ulid = es.entity_ulid
          WHERE e.province_code IS NULL AND ((e.kind = ANY (ARRAY['plataforma'::entity_kind, 'oem_vo_portal'::entity_kind, 'subasta'::entity_kind])) OR (e.kind = ANY (ARRAY['compraventa'::entity_kind, 'importador'::entity_kind])) AND (e.role = ANY (ARRAY['chain'::entity_role, 'standalone_pos'::entity_role])) OR e.role = 'chain'::entity_role)
        ), served_dealers AS (
         SELECT DISTINCT e.entity_ulid,
            e.cdp_code,
            e.recipe_version,
            es.source_key
           FROM entity e
             JOIN vehicle v ON v.entity_ulid = e.entity_ulid AND v.status = 'available'::text
             JOIN entity_source es ON es.entity_ulid = e.entity_ulid
          WHERE e.kind <> 'particular'::entity_kind
        ), classified AS (
         SELECT sd.entity_ulid,
            sd.cdp_code,
            sd.source_key,
                CASE
                    WHEN sd.recipe_version IS NOT NULL THEN 'per_dealer'::text
                    WHEN csk.source_key IS NOT NULL THEN 'connector'::text
                    ELSE 'none'::text
                END AS recipe_kind,
                CASE
                    WHEN sd.recipe_version IS NOT NULL THEN NULL::text
                    WHEN csk.source_key IS NOT NULL THEN sd.source_key
                    ELSE NULL::text
                END AS recipe_ref,
                CASE
                    WHEN sd.recipe_version IS NOT NULL THEN 1
                    WHEN csk.source_key IS NOT NULL THEN 2
                    ELSE 3
                END AS rank
           FROM served_dealers sd
             LEFT JOIN connector_source_keys csk ON csk.source_key = sd.source_key
        ), best_per_dealer AS (
         SELECT DISTINCT ON (classified.entity_ulid) classified.entity_ulid,
            classified.cdp_code,
            classified.source_key,
            classified.recipe_kind,
            classified.recipe_ref
           FROM classified
          ORDER BY classified.entity_ulid, classified.rank, classified.source_key
        )
 SELECT entity_ulid,
    cdp_code,
    source_key,
    recipe_kind,
    recipe_ref
   FROM best_per_dealer;

CREATE OR REPLACE VIEW v_canonical_deduped_draft AS
 SELECT cd.canonical_cdp_code,
    cd.canonical_entity_ulid,
    ce.trade_name AS canonical_trade_name,
    ce.municipality_code AS canonical_municipality,
    ce.province_code AS canonical_province,
    cd.super_canonical_cdp_code,
    cd.super_canonical_ulid,
    se.trade_name AS super_canonical_trade_name,
    se.municipality_code AS super_canonical_municipality,
    cd.component_size,
    cd.is_representative,
    cd.evidence_deep_link,
    cd.run_id
   FROM canonical_dedup cd
     JOIN entity ce ON ce.entity_ulid = cd.canonical_entity_ulid
     JOIN entity se ON se.entity_ulid = cd.super_canonical_ulid
  WHERE cd.run_id = (( SELECT canonical_dedup_run.run_id
           FROM canonical_dedup_run
          ORDER BY canonical_dedup_run.run_at DESC
         LIMIT 1));

CREATE OR REPLACE VIEW v_province_seal AS
 WITH venta_num AS (
         SELECT e.province_code,
            count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
           FROM entity e
             LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
          WHERE (e.kind = ANY (ARRAY['compraventa'::entity_kind, 'concesionario_oficial'::entity_kind])) AND e.province_code IS NOT NULL AND (EXISTS ( SELECT 1
                   FROM vehicle v
                  WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available'::text))
          GROUP BY e.province_code
        ), desg AS (
         SELECT e.province_code,
            count(DISTINCT e.entity_ulid) AS numerator,
            count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key = 'dgt_cat'::text) AS denominator
           FROM entity e
             LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
          WHERE e.kind = 'desguace'::entity_kind AND e.province_code IS NOT NULL
          GROUP BY e.province_code
        )
 SELECT d.province_code,
    'venta'::text AS segment,
    d.point_est AS denominator,
    COALESCE(n.numerator, 0::bigint) AS numerator,
    round(((100.0 * COALESCE(n.numerator, 0::bigint)::numeric)::double precision / NULLIF(d.point_est, 0::double precision))::numeric, 1) AS coverage_pct,
        CASE
            WHEN d.point_est IS NULL OR d.point_est = 0::double precision THEN 'NO_DENOM'::text
            WHEN ((100.0 * COALESCE(n.numerator, 0::bigint)::numeric)::double precision / d.point_est) >= 85::double precision THEN 'SELLADO'::text
            WHEN ((100.0 * COALESCE(n.numerator, 0::bigint)::numeric)::double precision / d.point_est) >= 50::double precision THEN 'PARCIAL'::text
            ELSE 'GAP'::text
        END AS verdict
   FROM denominator_estimate d
     LEFT JOIN venta_num n ON n.province_code = d.province_code
  WHERE d.segment = 'venta'::text
UNION ALL
 SELECT dg.province_code,
    'desguace'::text AS segment,
    dg.denominator,
    dg.numerator,
    round(100.0 * dg.numerator::numeric / NULLIF(dg.denominator, 0)::numeric, 1) AS coverage_pct,
        CASE
            WHEN dg.denominator IS NULL OR dg.denominator = 0 THEN 'NO_DENOM'::text
            WHEN dg.numerator >= dg.denominator THEN 'SELLADO'::text
            ELSE 'GAP'::text
        END AS verdict
   FROM desg dg;


-- Rollback:
-- (Reverse of the forward DDL. CLEAN ONLY while NO geo/entity row holds a code wider than the
--  original CHAR(2)/CHAR(5) -- a varchar->char(2) cast TRUNCATES '971'/'058091'. Any pilot or
--  onboarding that seeded wide non-ES codes MUST delete them BEFORE rolling back. Reverse the
--  ordering: drop the 6 views, drop the 6 FKs, shrink the 8 columns, re-add the 6 FKs, recreate
--  the 6 views.)
--
-- DROP VIEW IF EXISTS v_servable_dealer;
-- DROP VIEW IF EXISTS servable_entity;
-- DROP VIEW IF EXISTS v_province_seal;
-- DROP VIEW IF EXISTS v_canonical_deduped_draft;
-- DROP VIEW IF EXISTS v_dealer_recipe;
-- DROP VIEW IF EXISTS v_resolved_dealer;
-- DROP TRIGGER IF EXISTS trg_entity_set_comarca ON entity;
-- ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_province_code_fkey;
-- ALTER TABLE entity               DROP CONSTRAINT IF EXISTS entity_municipality_code_fkey;
-- ALTER TABLE geo_comarca          DROP CONSTRAINT IF EXISTS geo_comarca_province_code_fkey;
-- ALTER TABLE geo_municipality     DROP CONSTRAINT IF EXISTS geo_municipality_province_code_fkey;
-- ALTER TABLE denominator_estimate DROP CONSTRAINT IF EXISTS denominator_estimate_province_code_fkey;
-- ALTER TABLE organization         DROP CONSTRAINT IF EXISTS organization_hq_province_code_fkey;
-- ALTER TABLE geo_province         ALTER COLUMN code              TYPE char(2)  USING code::char(2);
-- ALTER TABLE geo_comarca          ALTER COLUMN province_code     TYPE char(2)  USING province_code::char(2);
-- ALTER TABLE geo_municipality     ALTER COLUMN province_code     TYPE char(2)  USING province_code::char(2);
-- ALTER TABLE entity               ALTER COLUMN province_code     TYPE char(2)  USING province_code::char(2);
-- ALTER TABLE denominator_estimate ALTER COLUMN province_code     TYPE char(2)  USING province_code::char(2);
-- ALTER TABLE organization         ALTER COLUMN hq_province_code  TYPE char(2)  USING hq_province_code::char(2);
-- ALTER TABLE geo_municipality     ALTER COLUMN code              TYPE char(5)  USING code::char(5);
-- ALTER TABLE entity               ALTER COLUMN municipality_code TYPE char(5)  USING municipality_code::char(5);
-- (re-add the 6 composite FKs as in section 4, recreate trg_entity_set_comarca as in 4b, then
--  recreate the 6 views from section 5.)
