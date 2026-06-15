-- 0026_verification_deep.sql — V5 DEEP VERIFICATION LEDGER
--
-- Superset de 0004_verification_health.sql: quorum DB-enforced, audit hash-chain,
-- denominator Chapman, rol read-only, gestionador queue.
--
-- GRANDFATHERING: las ~1039 filas existentes (incluyendo sellos vivos B1=640,
-- β=1093, B7=1102) fueron escritas con independent_values como objeto JSON y
-- verifier_paths como array de strings o NULL — ninguno tiene campos family/origin.
-- El CHECK chk_trustworthy_needs_quorum se añade NOT VALID para no romperlos.
-- Los verdicts futuros con TRUSTWORTHY exigen quorum_n≥2, family_n≥2, origin_n≥2.
--
-- DEFENSIVE: las funciones IMMUTABLE retornan 0 cuando el JSONB no es array,
-- evitando errores en GENERATED ALWAYS AS STORED sobre datos legacy.
--
-- Additive, idempotent, reversible. migrate.py aplica sólo la sección forward
-- (antes del bloque de rollback comentado al final del archivo).

-- ---------------------------------------------------------------------------
-- 0. Extensión pgcrypto (para digest sha256 del audit trail)
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- 1. Funciones IMMUTABLE (pre-requisito de las GENERATED ALWAYS AS STORED)
--
--    DEFENSIVE: retornan 0 si paths/values_arr es NULL o no es array JSONB.
--    Esto permite que las columnas generadas sean correctas en filas legacy donde
--    independent_values es un objeto ({...}) o NULL.
-- ---------------------------------------------------------------------------

-- Count of DISTINCT collector families among path objects in a JSONB array.
-- Returns 0 if input is NULL or not a JSONB array.
CREATE OR REPLACE FUNCTION cdp_distinct_families(paths JSONB)
RETURNS INT LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE
    WHEN paths IS NULL OR jsonb_typeof(paths) <> 'array' THEN 0
    ELSE COALESCE(
      (SELECT COUNT(DISTINCT p->>'family')::INT
       FROM jsonb_array_elements(paths) AS p),
      0
    )
  END
$$;

-- Count of DISTINCT origins (host/source_key/SQL table) among path objects.
-- Returns 0 if input is NULL or not a JSONB array.
CREATE OR REPLACE FUNCTION cdp_distinct_origins(paths JSONB)
RETURNS INT LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE
    WHEN paths IS NULL OR jsonb_typeof(paths) <> 'array' THEN 0
    ELSE COALESCE(
      (SELECT COUNT(DISTINCT p->>'origin')::INT
       FROM jsonb_array_elements(paths) AS p),
      0
    )
  END
$$;

-- Size of the largest cluster of numeric values agreeing within relative tolerance tol.
-- Returns 0 if input is NULL or not a JSONB array, or contains no numbers.
CREATE OR REPLACE FUNCTION cdp_modal_cluster(values_arr JSONB, tol DOUBLE PRECISION)
RETURNS INT LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
  vals      DOUBLE PRECISION[];
  best      INT := 0;
  cnt       INT;
  i         INT;
  j         INT;
  vi        DOUBLE PRECISION;
  vj        DOUBLE PRECISION;
BEGIN
  IF values_arr IS NULL OR jsonb_typeof(values_arr) <> 'array' THEN
    RETURN 0;
  END IF;
  SELECT array_agg((e)::text::DOUBLE PRECISION)
    INTO vals
  FROM jsonb_array_elements(values_arr) AS e
  WHERE jsonb_typeof(e) = 'number';
  IF vals IS NULL OR array_length(vals, 1) = 0 THEN
    RETURN 0;
  END IF;
  FOR i IN 1 .. array_length(vals, 1) LOOP
    vi  := vals[i];
    cnt := 0;
    FOR j IN 1 .. array_length(vals, 1) LOOP
      vj := vals[j];
      IF GREATEST(ABS(vi), ABS(vj), 1) = 1 THEN
        IF vi = vj THEN cnt := cnt + 1; END IF;
      ELSIF ABS(vi - vj) / GREATEST(ABS(vi), ABS(vj)) <= tol THEN
        cnt := cnt + 1;
      END IF;
    END LOOP;
    best := GREATEST(best, cnt);
  END LOOP;
  RETURN best;
END $$;

-- ---------------------------------------------------------------------------
-- 2. ALTER verification_verdict — columnas nuevas (ADD COLUMN IF NOT EXISTS)
--    Todas nullable o con DEFAULT; las filas existentes las heredan sin error.
-- ---------------------------------------------------------------------------

-- Tipo/kind del claim
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS claim_kind TEXT NOT NULL DEFAULT 'count'
    CHECK (claim_kind IN ('count','field_fill','existence','freshness','coverage','denominator'));

-- Tolerancia relativa para cdp_modal_cluster
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS tolerance DOUBLE PRECISION NOT NULL DEFAULT 0.0;

-- Columnas generadas (STORED): derivadas de independent_values / verifier_paths.
-- Seguras sobre datos legacy: las funciones retornan 0 para non-array / NULL.
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS quorum_n INT
    GENERATED ALWAYS AS (cdp_modal_cluster(independent_values, tolerance)) STORED;

ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS family_n INT
    GENERATED ALWAYS AS (cdp_distinct_families(verifier_paths)) STORED;

ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS origin_n INT
    GENERATED ALWAYS AS (cdp_distinct_origins(verifier_paths)) STORED;

-- Artefacto de evidencia replayable
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS evidence_uri TEXT;

-- Versión del método verificador
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS method_version TEXT NOT NULL DEFAULT 'vam-1';

-- TTL de frescura (NULL = nunca expira)
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;

-- Supersesión: apunta al verdict más reciente para el mismo subject+claim
ALTER TABLE verification_verdict
  ADD COLUMN IF NOT EXISTS superseded_by BIGINT
    REFERENCES verification_verdict(id);

-- ---------------------------------------------------------------------------
-- 3. Widening del CHECK de verdict: 3 → 4 valores (añade QUARANTINED)
--    DROP del viejo constraint + ADD del nuevo.
-- ---------------------------------------------------------------------------

-- El constraint existente se llama 'verification_verdict_verdict_check' (verificado vía \d)
ALTER TABLE verification_verdict
  DROP CONSTRAINT IF EXISTS verification_verdict_verdict_check;

ALTER TABLE verification_verdict
  ADD CONSTRAINT verification_verdict_verdict_check
    CHECK (verdict IN ('TRUSTWORTHY','REFUTED','UNVERIFIED','QUARANTINED'));

-- ---------------------------------------------------------------------------
-- 4. Quorum CHECK — NOT VALID (grandfathering)
--    Las filas existentes NO se revalidan. Los nuevos INSERTs deben cumplirlo.
--    Esto protege los sellos B1=640 (vp=strings, iv=objeto), β=1093, B7=1102 (NULL).
-- ---------------------------------------------------------------------------

-- Eliminar versión previa si existe (idempotencia)
ALTER TABLE verification_verdict
  DROP CONSTRAINT IF EXISTS chk_trustworthy_needs_quorum;

ALTER TABLE verification_verdict
  ADD CONSTRAINT chk_trustworthy_needs_quorum CHECK (
      verdict <> 'TRUSTWORTHY'
      OR (quorum_n >= 2 AND family_n >= 2 AND origin_n >= 2)
  ) NOT VALID;

-- Índices adicionales de V5 (IF NOT EXISTS → idempotentes)
CREATE INDEX IF NOT EXISTS idx_verdict_expiry
  ON verification_verdict (expires_at)
  WHERE expires_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_verdict_latest
  ON verification_verdict (subject_type, subject_key, claim, created_at DESC);

-- ---------------------------------------------------------------------------
-- 5. Audit trail hash-chain (append-only, tamper-evident)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS verdict_audit (
    seq          BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    verdict_id   BIGINT      NOT NULL REFERENCES verification_verdict(id),
    subject_type TEXT        NOT NULL,
    subject_key  TEXT        NOT NULL,
    claim        TEXT        NOT NULL,
    verdict      TEXT        NOT NULL,
    quorum_n     INT         NOT NULL,
    family_n     INT         NOT NULL,
    payload_hash TEXT        NOT NULL,   -- sha256 del payload canonicalizado
    prev_hash    TEXT,                   -- sha256 del chain_hash previo (NULL = GENESIS)
    chain_hash   TEXT        NOT NULL,   -- sha256(prev_hash || payload_hash)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger: AFTER INSERT en verification_verdict → append fila hash-encadenada
CREATE OR REPLACE FUNCTION cdp_audit_append() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  prev    TEXT;
  payload TEXT;
  ph      TEXT;
BEGIN
  SELECT chain_hash INTO prev FROM verdict_audit ORDER BY seq DESC LIMIT 1;
  payload := encode(digest(
      COALESCE(NEW.subject_type,  '') || '|' ||
      COALESCE(NEW.subject_key,   '') || '|' ||
      COALESCE(NEW.claim,         '') || '|' ||
      COALESCE(NEW.verdict,       '') || '|' ||
      COALESCE(NEW.primary_value, '') || '|' ||
      COALESCE(NEW.verifier_paths::text,    '[]') || '|' ||
      COALESCE(NEW.independent_values::text,'[]') || '|' ||
      COALESCE(NEW.quorum_n::text, '0') || '|' ||
      COALESCE(NEW.family_n::text, '0'),
      'sha256'), 'hex');
  ph := encode(digest(COALESCE(prev, 'GENESIS') || '|' || payload, 'sha256'), 'hex');
  INSERT INTO verdict_audit
    (verdict_id, subject_type, subject_key, claim, verdict,
     quorum_n,   family_n,    payload_hash, prev_hash, chain_hash)
  VALUES
    (NEW.id, NEW.subject_type, NEW.subject_key, NEW.claim, NEW.verdict,
     NEW.quorum_n, NEW.family_n, payload, prev, ph);
  RETURN NEW;
END $$;

-- Trigger: BEFORE UPDATE OR DELETE en verdict_audit → prohibición total
CREATE OR REPLACE FUNCTION cdp_audit_immutable() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'verdict_audit is append-only (attempted % on seq %)', TG_OP, OLD.seq;
END $$;

DROP TRIGGER IF EXISTS trg_verdict_audit_append  ON verification_verdict;
CREATE TRIGGER trg_verdict_audit_append
  AFTER INSERT ON verification_verdict
  FOR EACH ROW EXECUTE FUNCTION cdp_audit_append();

DROP TRIGGER IF EXISTS trg_verdict_audit_noupd ON verdict_audit;
CREATE TRIGGER trg_verdict_audit_noupd
  BEFORE UPDATE OR DELETE ON verdict_audit
  FOR EACH ROW EXECUTE FUNCTION cdp_audit_immutable();

-- ---------------------------------------------------------------------------
-- 6. denominator_estimate — estimaciones Chapman/Chao2 por (segment, province)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS denominator_estimate (
    id            BIGINT           GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    segment       TEXT             NOT NULL,
    province_code CHAR(2)          REFERENCES geo_province(code),  -- NULL = nacional
    method        TEXT             NOT NULL DEFAULT 'chapman'
        CHECK (method IN ('chapman','source_floor','registral_ceiling','assumed')),
    n1            INT,                     -- capturas fuente A
    n2            INT,                     -- capturas fuente B
    m2            INT,                     -- recapturas (A ∩ B)
    point_est     DOUBLE PRECISION NOT NULL,
    ci_low        DOUBLE PRECISION NOT NULL,
    ci_high       DOUBLE PRECISION NOT NULL,
    sources_used  JSONB            NOT NULL DEFAULT '[]'::jsonb,
    evidence_uri  TEXT,
    created_at    TIMESTAMPTZ      NOT NULL DEFAULT now(),
    CONSTRAINT chk_ci_order CHECK (ci_low <= point_est AND point_est <= ci_high)
);

CREATE INDEX IF NOT EXISTS idx_denom_cell
  ON denominator_estimate (segment, province_code, created_at DESC);

-- ---------------------------------------------------------------------------
-- 7. Rol read-only cardeep_inquisitor
--    SELECT en tablas de ledger/audit/denominator. Cero writes.
-- ---------------------------------------------------------------------------

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cardeep_inquisitor') THEN
    CREATE ROLE cardeep_inquisitor NOLOGIN NOINHERIT;
  END IF;
END $$;

GRANT SELECT ON verification_verdict  TO cardeep_inquisitor;
GRANT SELECT ON verdict_audit         TO cardeep_inquisitor;
GRANT SELECT ON denominator_estimate  TO cardeep_inquisitor;
GRANT SELECT ON source_health         TO cardeep_inquisitor;

-- ---------------------------------------------------------------------------
-- Rollback:
-- REVOKE SELECT ON verification_verdict, verdict_audit, denominator_estimate,
--        source_health FROM cardeep_inquisitor;
-- DROP ROLE IF EXISTS cardeep_inquisitor;
-- DROP INDEX IF EXISTS idx_denom_cell;
-- DROP TABLE IF EXISTS denominator_estimate;
-- DROP TRIGGER IF EXISTS trg_verdict_audit_noupd ON verdict_audit;
-- DROP TRIGGER IF EXISTS trg_verdict_audit_append ON verification_verdict;
-- DROP FUNCTION IF EXISTS cdp_audit_immutable();
-- DROP FUNCTION IF EXISTS cdp_audit_append();
-- DROP TABLE IF EXISTS verdict_audit;
-- ALTER TABLE verification_verdict DROP CONSTRAINT IF EXISTS chk_trustworthy_needs_quorum;
-- ALTER TABLE verification_verdict DROP CONSTRAINT IF EXISTS verification_verdict_verdict_check;
-- ALTER TABLE verification_verdict
--   ADD CONSTRAINT verification_verdict_verdict_check
--     CHECK (verdict = ANY (ARRAY['TRUSTWORTHY','REFUTED','UNVERIFIED']));
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS superseded_by;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS expires_at;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS method_version;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS evidence_uri;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS origin_n;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS family_n;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS quorum_n;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS tolerance;
-- ALTER TABLE verification_verdict DROP COLUMN IF EXISTS claim_kind;
-- DROP FUNCTION IF EXISTS cdp_modal_cluster(jsonb, double precision);
-- DROP FUNCTION IF EXISTS cdp_distinct_origins(jsonb);
-- DROP FUNCTION IF EXISTS cdp_distinct_families(jsonb);
-- (pgcrypto se mantiene — puede ser necesaria para otras partes del sistema)
