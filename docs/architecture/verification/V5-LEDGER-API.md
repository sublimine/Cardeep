# V5 — VERIFICATION LEDGER, PUBLISH-GATE, AUDIT TRAIL & API/DASHBOARD

> **CARDEEP NEVER SELLS LIES.** A number is not "true" because the path that produced
> it says so. It is true only when **≥2 orthogonal paths** that did **not** share a
> failure mode independently land on it within tolerance, and a tamper-evident ledger
> records that they did. This document is the **authoritative, DB-enforced** validator.
> It **supersedes and subsumes** the light `05-VERIFICATION-VAM` of the master
> architecture: everything VAM did (count-quorum on `verification_verdict`) is a strict
> subset of the schema and rules below.
>
> **Anti-hallucination contract for this doc.** Every structural claim about the live
> system is tagged `[VERIFIED]` (I read the source / ran it against the live DB on
> 2026-06-12) or `[ASSUMED]` (design target, not yet in code). No placeholders, no
> "// resto igual". Concrete DDL, concrete formulas, concrete thresholds, worked numeric
> examples with the project's real numbers.

---

## 0. Ground truth this design is built on (so nothing here is invented)

`[VERIFIED]` by reading the repo + querying the live `cardeep-pg` (PostgreSQL **16.14**)
on 2026-06-12:

- **Existing ledger** `migrations/0004_verification_health.sql`: table
  `verification_verdict(id, subject_type, subject_key, claim, primary_value,
  primary_path, verifier_paths JSONB, independent_values JSONB, divergence,
  verdict CHECK IN ('TRUSTWORTHY','REFUTED','UNVERIFIED'), evidence, created_at)`
  + `source_health` + `alert`. **No quorum is enforced in the DB** — the CHECK only
  constrains the verdict label, not the evidence behind it. `QUARANTINED` does not exist.
- **Existing verifier** `pipeline/verify.py::record_count_verdict(...)` writes one row per
  claim from a `paths: dict[str,int]`. Call sites:
  - `pipeline/discover.py` → `subject_type='source'`, paths
    `{db_ingested, fetched, source_declared}`.
  - `pipeline/ingest.py` → `subject_type='entity_inventory'`, paths
    `{db_available, harvested, source_declared}`.
- **Live data** (read from the running API / DB, the real denominator of every example
  in this doc): **12.814 entities** (garaje 7.200 · compraventa 2.753 ·
  concesionario_oficial 1.569 · desguace 1.292) · **22.300 servable vehicles** ·
  **212 dealers harvested** · 52/52 provinces · 10 sources.
- **Denominator census** `docs/research/SOURCES_ES.md`: floor **~44.000** auto POS
  (Páginas Amarillas), ceiling **50–90k** (CNAE 45 registral / Places); per-segment
  truths — desguaces DGT **1.292** (official), concesionarios franquiciados FACONAUTO
  **2.018**, capture-recapture (Chapman) is the F8 plan. DGT CATV re-derived by hand =
  **1.292** (Δ0); Kia **242**, MG **212** (Δ0); AS24 **278.329**, coches.net **249.139**
  (counter drift only). VW OneHub "263 dealers" was **REFUTED** (HTTP 500).
- `[VERIFIED]` in the live DB: `jsonb_array_length('[1,2,3]')=3`; distinct-value counting
  over `jsonb_each` works. (Subqueries are **not** allowed inside a CHECK, so quorum
  arithmetic that needs them is pushed into `IMMUTABLE` scalar functions, §3.2.)

**Design rule from those facts:** the new ledger is a *superset migration* (`0005`) of
`0004` — same column names kept, new columns added, the CHECK widened to 4 verdicts and
hardened with a quorum predicate. Nothing the current pipeline writes breaks.

---

## 1. The lie taxonomy → what each detection means for the ledger

The validator exists to catch six failure modes. Each maps to a concrete ledger signal,
a verdict, and a routed action (the "Gestionador" of the mandate). This table is the spine
everything else implements.

| # | Failure mode | Concrete symptom in evidence | Verdict it forces | Routed action |
|---|---|---|---|---|
| L1 | **Inflated count** | a source/primary path reports N, but independent paths cluster at M ≪ N | `REFUTED` (if rival quorum at M) or `UNVERIFIED` | `research` (re-derive) |
| L2 | **Silent cap** | `db_ingested == fetched == declared` all equal a round/limit value (1000, page-size·pages) while a denominator path says more | `QUARANTINED` (cap-suspect rule §4.5) | `fix` (raise limit) |
| L3 | **Silently dropped field** | row count agrees but a *field-fill* path (e.g. `price_nonnull`) diverges from `rows` beyond tolerance | `REFUTED` on the field claim | `fix` (recipe) |
| L4 | **Staleness** | latest TRUSTWORTHY verdict for a subject is older than the subject's freshness SLA | verdict **expires** → `UNVERIFIED` (gate closes) | `research` (re-harvest) |
| L5 | **Fabrication** | a path's value has no evidence artifact (`evidence_uri` null) or fails replay | `QUARANTINED` | `escalate` |
| L6 | **Coverage gap** | observed entities in a (segment, province) cell are far below the denominator CI lower bound | segment/cell verdict `UNVERIFIED` | `research` (find sources) |

The ledger must therefore record, per claim: **which paths**, **what each independently
produced**, **whether they were orthogonal**, **the evidence artifact per path**, and a
**verdict with a machine-checkable justification**. That is the schema of §3.

---

## 2. Independence is the whole game — the orthogonality model

A quorum of 2 paths that share a failure mode is **one** path wearing two hats. The ledger
must *prove* independence, not assume it. We model each path with an **independence
signature**: the set of shared-fate dimensions it touches.

```
path = {
  path_name,                       -- e.g. 'db_ingested'
  value,                           -- the number/string it produced
  family,                          -- collector family: 'self' | 'registry' | 'aggregator' |
                                   --   'geo' | 'capture_recapture' | 'oem_api' | 'manual'
  transport,                       -- 'http_html' | 'http_json' | 'sitemap' | 'sql' | 'arcgis' | 'dump'
  origin,                          -- the actual host/source_key/SQL table
  evidence_uri,                    -- artifact: data/probe/... blob hash, URL+timestamp, or SQL hash
  collected_at
}
```

**Two paths are ORTHOGONAL iff they differ in `family` AND in (`transport` OR `origin`).**
Formally, with shared-fate vector `s(p) = (family, origin)`:

```
orthogonal(p_i, p_j)  ⇔  family(p_i) ≠ family(p_j)  ∧  origin(p_i) ≠ origin(p_j)
```

Rationale, worked on the real call sites:

- `discover.py` paths `{db_ingested(sql/self), fetched(http/self), source_declared(http/source)}`.
  `db_ingested` and `fetched` share `family='self'` and the same HTTP fetch lineage → they
  are **NOT** orthogonal. They guard against *ingestion loss* (a real bug class), but two of
  them agreeing is **not a quorum** — it is one harvest confirming it didn't drop rows
  in the last 20 cm of pipe. This is exactly why the current `verify.py` added the
  `primary_agrees` rule. The deep ledger formalizes it: **`db_ingested`/`fetched` form an
  intra-path *integrity* check, not an inter-path *truth* quorum.** A count is only
  `TRUSTWORTHY` when an **external** orthogonal path (DGT registry, OSM, capture-recapture,
  hand-curl) corroborates.
- Real example that *is* orthogonal: desguaces ingested via `db_ingested=1292` (family
  `self`, origin `dgt_cat`) vs the census corroboration **Barcelona 76 = exact** from an
  independent DGT evidence pull (family `registry`, different origin) vs AEDRA 615 /
  DesguacesDirecto 1.386 (family `aggregator`). Different families, different origins →
  a real quorum.

The ledger stores the full path objects in `verifier_paths` (JSONB array) so independence is
**auditable after the fact**, and a generated column `orthogonal_quorum` (§3.2) recomputes it
in the DB so a human can never hand-flip a verdict to TRUSTWORTHY without the evidence.

---

## 3. The ledger schema (DDL) — migration `0005`

`[ASSUMED]` (this is the design; it is a backward-compatible superset of `0004`).
Additive, idempotent, reversible — matching the project's migration doctrine.

### 3.1 Immutable helper functions (so CHECKs can be quorum-aware)

PostgreSQL CHECK constraints cannot run subqueries, but **can** call `IMMUTABLE`
functions over the row's own columns. We make quorum arithmetic a pure function of
`verifier_paths` (a JSONB array of path objects) and `independent_values`.

```sql
-- 0005_verification_deep.sql — DEEP validator: quorum-enforced ledger, publish-gate,
-- immutable audit trail, denominator, gestionador. Additive, idempotent, reversible.

-- ---------------------------------------------------------------------------
-- (A) Pure functions used by CHECK constraints. IMMUTABLE = safe in CHECK.
-- ---------------------------------------------------------------------------

-- Count of DISTINCT collector families among the path objects.
CREATE OR REPLACE FUNCTION cdp_distinct_families(paths JSONB)
RETURNS INT LANGUAGE sql IMMUTABLE AS $$
  SELECT COALESCE(COUNT(DISTINCT p->>'family'), 0)::INT
  FROM jsonb_array_elements(COALESCE(paths, '[]'::jsonb)) AS p
$$;

-- Count of DISTINCT origins (actual host/source_key/SQL table) among the path objects.
-- [adversarial GAP-30] origin-distinctness is now DB-ENFORCED via origin_n + the widened
-- chk_trustworthy_needs_quorum CHECK, NOT "enforced per-family at write time" in app code.
-- The DB no longer takes the (hand-set) family label on faith: two differently-familied
-- paths reading the same host fail the gate because origin_n stays 1.
CREATE OR REPLACE FUNCTION cdp_distinct_origins(paths JSONB)
RETURNS INT LANGUAGE sql IMMUTABLE AS $$
  SELECT COALESCE(COUNT(DISTINCT p->>'origin'), 0)::INT
  FROM jsonb_array_elements(COALESCE(paths, '[]'::jsonb)) AS p
$$;

-- Size of the modal agreement cluster: how many paths share the most common value,
-- within relative tolerance tol. Returns the largest cluster size.
CREATE OR REPLACE FUNCTION cdp_modal_cluster(values_arr JSONB, tol DOUBLE PRECISION)
RETURNS INT LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
  vals DOUBLE PRECISION[];
  best INT := 0; cnt INT; i INT; j INT; vi DOUBLE PRECISION; vj DOUBLE PRECISION;
BEGIN
  SELECT array_agg((e)::text::DOUBLE PRECISION)
    INTO vals
  FROM jsonb_array_elements(COALESCE(values_arr,'[]'::jsonb)) AS e
  WHERE jsonb_typeof(e) = 'number';
  IF vals IS NULL THEN RETURN 0; END IF;
  FOR i IN 1 .. array_length(vals,1) LOOP
    vi := vals[i]; cnt := 0;
    FOR j IN 1 .. array_length(vals,1) LOOP
      vj := vals[j];
      IF GREATEST(ABS(vi),ABS(vj),1) = 1 THEN
        IF vi = vj THEN cnt := cnt + 1; END IF;
      ELSIF ABS(vi - vj) / GREATEST(ABS(vi),ABS(vj)) <= tol THEN
        cnt := cnt + 1;
      END IF;
    END LOOP;
    best := GREATEST(best, cnt);
  END LOOP;
  RETURN best;
END $$;
```

`[VERIFIED]` the primitives these rely on (`jsonb_array_elements`, numeric cast,
`jsonb_typeof`) run on the live PG 16.14.

### 3.2 The ledger table — quorum enforced by the database itself

```sql
-- ---------------------------------------------------------------------------
-- (B) The verdict ledger. Superset of 0004.verification_verdict.
--     Old rows remain valid; new columns are nullable or defaulted.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS verification_verdict (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- WHAT is being judged
    subject_type       TEXT  NOT NULL,        -- 'source'|'entity'|'entity_inventory'|
                                              -- 'platform'|'count'|'segment'|'province_cell'|
                                              -- 'denominator'|'field_fill'
    subject_key        TEXT  NOT NULL,        -- source_key / cdp_code / 'ES:desguace:08' / ...
    claim              TEXT  NOT NULL,        -- human-readable assertion
    claim_kind         TEXT  NOT NULL DEFAULT 'count'
        CHECK (claim_kind IN ('count','field_fill','existence','freshness','coverage','denominator')),

    -- HOW it was produced and corroborated
    primary_path       TEXT,                  -- name of the producing path (e.g. 'db_ingested')
    primary_value      TEXT,
    verifier_paths     JSONB NOT NULL DEFAULT '[]'::jsonb,  -- ARRAY of path objects (§2)
    independent_values JSONB NOT NULL DEFAULT '[]'::jsonb,  -- ARRAY of the numeric values

    -- The MEASUREMENT
    tolerance          DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    divergence         DOUBLE PRECISION,      -- (max-min)/max over numeric paths
    quorum_n           INT GENERATED ALWAYS AS
                         (cdp_modal_cluster(independent_values, tolerance)) STORED,
    family_n           INT GENERATED ALWAYS AS
                         (cdp_distinct_families(verifier_paths)) STORED,
    -- origin-distinctness DB-ENFORCED, not trusted to app code [adversarial GAP-30]
    origin_n           INT GENERATED ALWAYS AS
                         (cdp_distinct_origins(verifier_paths)) STORED,

    -- The JUDGMENT
    verdict            TEXT NOT NULL
        CHECK (verdict IN ('TRUSTWORTHY','REFUTED','UNVERIFIED','QUARANTINED')),

    -- Evidence + lifecycle
    evidence           TEXT,                  -- human note (kept from 0004)
    evidence_uri       TEXT,                  -- artifact pointer: data/probe/<hash> | URL@ts | sql:<hash>
    method_version     TEXT NOT NULL DEFAULT 'vam-1',  -- which verifier rule produced this
    expires_at         TIMESTAMPTZ,           -- freshness SLA (NULL = never; §4.4)
    superseded_by      BIGINT REFERENCES verification_verdict(id),  -- newer verdict for same subject+claim
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- ===== DB-ENFORCED QUORUM (the heart) =====
    -- TRUSTWORTHY is structurally impossible without ≥2 agreeing paths AND ≥2 families
    -- AND ≥2 DISTINCT ORIGINS [adversarial GAP-30]: two paths with different family labels
    -- but the SAME origin host (a plausible mislabel — an 'aggregator' and a 'registry' both
    -- reading the same vendor feed) no longer satisfy the gate. Origin-distinctness is now
    -- enforced BY THE DB, not by the application layer V5 itself says cannot be trusted.
    CONSTRAINT chk_trustworthy_needs_quorum CHECK (
        verdict <> 'TRUSTWORTHY'
        OR (quorum_n >= 2 AND family_n >= 2 AND origin_n >= 2)
    ),
    -- A REFUTED/UNVERIFIED/QUARANTINED verdict needs at least the paths recorded.
    CONSTRAINT chk_paths_present CHECK (
        jsonb_typeof(verifier_paths) = 'array'
        AND jsonb_typeof(independent_values) = 'array'
    ),
    -- divergence is a ratio in [0,1] when present
    CONSTRAINT chk_divergence_range CHECK (
        divergence IS NULL OR (divergence >= 0 AND divergence <= 1)
    )
);

CREATE INDEX IF NOT EXISTS idx_verdict_subject   ON verification_verdict (subject_type, subject_key);
CREATE INDEX IF NOT EXISTS idx_verdict_verdict   ON verification_verdict (verdict);
CREATE INDEX IF NOT EXISTS idx_verdict_expiry    ON verification_verdict (expires_at)
    WHERE expires_at IS NOT NULL;
-- "latest verdict per subject+claim" is the publish-gate's hot path:
CREATE INDEX IF NOT EXISTS idx_verdict_latest
    ON verification_verdict (subject_type, subject_key, claim, created_at DESC);
```

> **Why this is the strongest line in the system.** The
> `chk_trustworthy_needs_quorum` CHECK makes it **physically impossible** to store a
> `TRUSTWORTHY` row whose own JSONB evidence does not contain ≥2 numerically-agreeing
> values spanning ≥2 collector families. `quorum_n` and `family_n` are **generated
> columns** recomputed by the DB from the evidence — an operator (or a buggy agent)
> cannot pass a literal `quorum_n=2`; the database derives it. To fake TRUSTWORTHY you
> would have to fabricate a second, differently-familied evidence artifact and pass its
> replay (§7). The lie surface collapses to "forge two independent artifacts," which the
> audit trail and replay are designed to catch.

### 3.3 The append-only, tamper-evident audit trail

A verdict row is itself mutable in principle (someone with DB rights could `UPDATE` it).
The **audit trail** is the immutable witness: every verdict insert is hash-chained, and a
trigger forbids `UPDATE`/`DELETE`.

```sql
-- ---------------------------------------------------------------------------
-- (C) Immutable, hash-chained audit log. Append-only by trigger.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS verdict_audit (
    seq         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    verdict_id  BIGINT NOT NULL REFERENCES verification_verdict(id),
    subject_type TEXT NOT NULL,
    subject_key  TEXT NOT NULL,
    claim        TEXT NOT NULL,
    verdict      TEXT NOT NULL,
    quorum_n     INT  NOT NULL,
    family_n     INT  NOT NULL,
    payload_hash TEXT NOT NULL,     -- sha256 of the canonicalized verdict row
    prev_hash    TEXT,              -- sha256 of the previous audit row (chain)
    chain_hash   TEXT NOT NULL,     -- sha256(prev_hash || payload_hash)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION cdp_audit_append() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  prev TEXT;
  payload TEXT;
  ph TEXT;
BEGIN
  SELECT chain_hash INTO prev FROM verdict_audit ORDER BY seq DESC LIMIT 1;
  payload := encode(digest(
      coalesce(NEW.subject_type,'')||'|'||coalesce(NEW.subject_key,'')||'|'||
      coalesce(NEW.claim,'')||'|'||coalesce(NEW.verdict,'')||'|'||
      coalesce(NEW.primary_value,'')||'|'||
      coalesce(NEW.verifier_paths::text,'[]')||'|'||
      coalesce(NEW.independent_values::text,'[]')||'|'||
      coalesce(NEW.quorum_n::text,'0')||'|'||coalesce(NEW.family_n::text,'0'),
      'sha256'), 'hex');
  ph := encode(digest(coalesce(prev,'GENESIS')||'|'||payload, 'sha256'),'hex');
  INSERT INTO verdict_audit(verdict_id, subject_type, subject_key, claim, verdict,
                            quorum_n, family_n, payload_hash, prev_hash, chain_hash)
  VALUES (NEW.id, NEW.subject_type, NEW.subject_key, NEW.claim, NEW.verdict,
          NEW.quorum_n, NEW.family_n, payload, prev, ph);
  RETURN NEW;
END $$;

CREATE OR REPLACE FUNCTION cdp_audit_immutable() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'verdict_audit is append-only (attempted % on seq %)', TG_OP, OLD.seq;
END $$;

DROP TRIGGER IF EXISTS trg_verdict_audit_append ON verification_verdict;
CREATE TRIGGER trg_verdict_audit_append
    AFTER INSERT ON verification_verdict
    FOR EACH ROW EXECUTE FUNCTION cdp_audit_append();

DROP TRIGGER IF EXISTS trg_verdict_audit_noupd ON verdict_audit;
CREATE TRIGGER trg_verdict_audit_noupd
    BEFORE UPDATE OR DELETE ON verdict_audit
    FOR EACH ROW EXECUTE FUNCTION cdp_audit_immutable();
```

`digest(...,'sha256')` requires `pgcrypto`. Migration `0005` does
`CREATE EXTENSION IF NOT EXISTS pgcrypto;` at the top. `[ASSUMED]` pgcrypto installable
(it ships with the standard `postgres:16` image used by `cardeep-pg`).

**Chain verification query** (run by the dashboard's integrity tile, §9):

```sql
-- Returns the first broken link, or no rows if the chain is intact.
WITH chained AS (
  SELECT seq, prev_hash, chain_hash, payload_hash,
         lag(chain_hash) OVER (ORDER BY seq) AS expected_prev
  FROM verdict_audit)
SELECT seq FROM chained
WHERE seq > (SELECT min(seq) FROM verdict_audit)
  AND prev_hash IS DISTINCT FROM expected_prev
ORDER BY seq LIMIT 1;
```

### 3.4 The publish-gate view — the only thing the public API may read

A number/entity is **served only if its latest, non-expired verdict is TRUSTWORTHY.** This
is not application logic that can be bypassed; it is a **view** the read API is bound to.

```sql
-- ---------------------------------------------------------------------------
-- (D) Publish-gate. "latest verdict per (subject_type, subject_key, claim)".
-- [adversarial GAP-33] MATERIALIZED, not a plain view: at tens of millions of rows + a
-- ledger that grows with every harvest, a DISTINCT ON … ORDER BY created_at DESC over the
-- WHOLE ledger on the hot read path would make the "never falls" API a heavy analytical
-- scan. The latest-verdict row per subject is kept in a MATERIALIZED VIEW (or an
-- incrementally-maintained entity_latest_verdict table refreshed by the ingest/verify path),
-- so the publish-gate is an index lookup. is_publishable is computed at QUERY time from
-- expires_at so freshness self-closes WITHOUT a write — but the materialized base keeps the
-- per-subject latest small. A continuous re-verification cadence (MASTER_PLAN C-11 TTLs)
-- keeps the served SET fresh, so the gate withholds individual stale rows without the served
-- data collapsing to near-zero between harvest cycles.
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS v_latest_verdict AS
SELECT DISTINCT ON (subject_type, subject_key, claim)
       id, subject_type, subject_key, claim, claim_kind, verdict,
       quorum_n, family_n, origin_n, divergence, expires_at, created_at
FROM verification_verdict
ORDER BY subject_type, subject_key, claim, created_at DESC;
CREATE UNIQUE INDEX IF NOT EXISTS idx_lv_subject
    ON v_latest_verdict (subject_type, subject_key, claim);
-- REFRESH MATERIALIZED VIEW CONCURRENTLY v_latest_verdict; -- by the verify path, incremental
-- is_publishable is evaluated at read time so expiry needs no rewrite of the matview:
--   (verdict='TRUSTWORTHY' AND (expires_at IS NULL OR expires_at > now()))

-- Entities that may be served: their existence claim is currently publishable.
CREATE OR REPLACE VIEW v_publishable_entity AS
SELECT e.*
FROM entity e
JOIN v_latest_verdict lv
  ON lv.subject_type = 'entity'
 AND lv.subject_key  = e.cdp_code
 AND lv.claim_kind   = 'existence'
WHERE lv.verdict = 'TRUSTWORTHY'
  AND (lv.expires_at IS NULL OR lv.expires_at > now());   -- is_publishable, read-time

-- Inventory counts that may be served: per-entity inventory claim publishable.
CREATE OR REPLACE VIEW v_publishable_inventory AS
SELECT v.*
FROM vehicle v
JOIN entity e ON e.entity_ulid = v.entity_ulid
JOIN v_latest_verdict lv
  ON lv.subject_type = 'entity_inventory'
 AND lv.subject_key  = e.cdp_code
WHERE lv.verdict = 'TRUSTWORTHY'
  AND (lv.expires_at IS NULL OR lv.expires_at > now())    -- is_publishable, read-time
  AND v.status = 'available';
```

> **Honesty invariant.** Anything not TRUSTWORTHY is **not** served as fact. It can still
> be exposed via the *verification* API (§8) clearly labelled `UNVERIFIED`/`QUARANTINED`,
> but the data API (`/entities`, `/inventory`) reads **only** `v_publishable_*`. A gap is
> confessed (count shown as "unverified"), never silently filled.

### 3.5 The denominator table — bounding "how many exist"

To detect coverage gaps (L6) the validator needs a *defensible* denominator per
(segment, province) with a **confidence interval**, not a single guessed number. We persist
the capture-recapture inputs and the Chapman estimate.

```sql
-- ---------------------------------------------------------------------------
-- (E) Denominator estimates with CI (Chapman capture-recapture). Per cell.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS denominator_estimate (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    segment       TEXT NOT NULL,        -- 'desguace'|'concesionario_oficial'|'compraventa'|'garaje'|'all'
    province_code CHAR(2) REFERENCES geo_province(code),  -- NULL = national
    method        TEXT NOT NULL DEFAULT 'chapman'
        CHECK (method IN ('chapman','source_floor','registral_ceiling','assumed')),
    n1            INT,                   -- captures by source A
    n2            INT,                   -- captures by source B
    m2            INT,                   -- recaptures (in both A and B)
    point_est     DOUBLE PRECISION NOT NULL,  -- N̂
    ci_low        DOUBLE PRECISION NOT NULL,
    ci_high       DOUBLE PRECISION NOT NULL,
    sources_used  JSONB NOT NULL DEFAULT '[]'::jsonb,  -- which source_keys A,B were
    evidence_uri  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_ci_order CHECK (ci_low <= point_est AND point_est <= ci_high)
);
CREATE INDEX IF NOT EXISTS idx_denom_cell ON denominator_estimate (segment, province_code, created_at DESC);
```

### 3.6 The Gestionador queue — every detection is routed, none is dropped

```sql
-- ---------------------------------------------------------------------------
-- (F) Gestionador: each non-TRUSTWORTHY detection becomes a routed work item.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gestionador_item (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    verdict_id   BIGINT REFERENCES verification_verdict(id),
    subject_type TEXT NOT NULL,
    subject_key  TEXT NOT NULL,
    detection    TEXT NOT NULL          -- maps to L1..L6
        CHECK (detection IN ('inflated','silent_cap','dropped_field','stale','fabrication','coverage_gap')),
    route        TEXT NOT NULL
        CHECK (route IN ('fix','research','quarantine','escalate')),
    severity     TEXT NOT NULL DEFAULT 'warning'
        CHECK (severity IN ('info','warning','critical')),
    state        TEXT NOT NULL DEFAULT 'open'
        CHECK (state IN ('open','in_progress','resolved','wontfix')),
    note         TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_gest_open ON gestionador_item (route, severity)
    WHERE state = 'open';
CREATE INDEX IF NOT EXISTS idx_gest_subject ON gestionador_item (subject_type, subject_key);
```

```sql
-- Rollback (0005):
-- DROP VIEW IF EXISTS v_publishable_inventory, v_publishable_entity;
-- DROP MATERIALIZED VIEW IF EXISTS v_latest_verdict;
-- DROP TABLE IF EXISTS gestionador_item, denominator_estimate;
-- DROP TRIGGER IF EXISTS trg_verdict_audit_noupd ON verdict_audit;
-- DROP TRIGGER IF EXISTS trg_verdict_audit_append ON verification_verdict;
-- DROP TABLE IF EXISTS verdict_audit;
-- ALTER TABLE verification_verdict DROP CONSTRAINT IF EXISTS chk_trustworthy_needs_quorum, ...;
-- (verification_verdict itself is NOT dropped — it predates 0005; only added cols/constraints are.)
-- DROP FUNCTION IF EXISTS cdp_audit_append, cdp_audit_immutable, cdp_modal_cluster, cdp_distinct_families;
```

---

## 4. The verdict decision function — exact rules & thresholds

Given a claim with paths `P = {pᵢ}`, numeric values `V = {vᵢ}`, tolerance `τ`:

Definitions:
- **divergence** `d = (max V − min V) / max V` (0 when all equal; the existing
  `verify.py` formula, kept).
- **modal cluster** `q = cdp_modal_cluster(V, τ)` — largest set of paths agreeing within `τ`.
- **family count** `f = cdp_distinct_families(P)`.
- **rival cluster** `r` = size of the second-largest agreeing cluster at a *different* value.

### 4.1 TRUSTWORTHY
```
q ≥ 2  ∧  f ≥ 2  ∧  r < 2  ∧  primary_value ∈ modal_cluster  ∧  not cap_suspect
```
i.e. at least two paths from at least two **different families** agree, no rival pair
contradicts, the value actually served (primary) is inside the agreeing cluster, and it
doesn't smell like a silent cap (§4.5). **This is exactly the DB CHECK plus the
application-side rival/cap/primary guards.**

### 4.2 REFUTED
```
(r ≥ 2  ∧  rival_value ≠ modal_value)            -- two independent paths insist on a different number
 ∨ (claim_kind='field_fill' ∧ d > τ_field)        -- field-fill diverges beyond field tolerance
 ∨ (primary_value ∉ modal_cluster ∧ q ≥ 2)        -- the served value is the outlier
```

### 4.3 UNVERIFIED
```
q < 2  ∨  f < 2                                    -- not enough orthogonal corroboration yet
```
The honest default. The current `verify.py` returns `UNVERIFIED` when `len(values) < 2`;
the deep rule also returns it when values exist but **families** don't (the
`db_ingested`+`fetched`-only case — integrity ok, truth not yet established).

### 4.4 Staleness → expiry (L4)
Each subject_type has a freshness SLA → sets `expires_at = created_at + sla`:

| subject_type | SLA `Δ` | Why |
|---|---|---|
| `entity_inventory` | **24 h** | inventory/prices drift daily (census §6 note) |
| `platform` (Tier-1 counter) | 24 h | live counters drift daily |
| `source` (discovery count) | 30 d | the dealer/registry universe moves slowly |
| `entity` (existence) | 90 d | a POS rarely vanishes; re-confirm quarterly |
| `denominator` | 180 d | census-grade, refreshed per F8 cycle |

When `now() > expires_at`, the **read-time** `is_publishable` predicate
(`verdict='TRUSTWORTHY' AND (expires_at IS NULL OR expires_at > now())`, evaluated in
`v_publishable_*`) flips to false **without any write** — the gate self-closes and a `stale`
Gestionador item is opened by the sweep job. The `v_latest_verdict` matview holds only the latest
row per subject (small); the continuous re-verification cadence (MASTER_PLAN C-11) keeps the served
SET fresh so the publishable set does not collapse wholesale between harvests (G-A33).

### 4.5 Cap-suspect rule (L2 — silent caps) — the subtle killer
A count is **cap_suspect** when all paths agree on a value that *looks like a limit*:
```
cap_suspect ⇔ value == primary_value
            ∧ ( value mod 1000 == 0                       -- round cap (1000, 5000…)
              ∨ value == page_size · floor(value/page_size)  -- exact pages·page_size
              ∨ value == declared_limit_of(source) )       -- known API hard cap
            ∧ denominator_ci_low(segment,province) > value -- and the floor says there's more
```
When cap_suspect, verdict is forced to **QUARANTINED** even if `q≥2, f≥2`, because
agreement *at the cap* is exactly what a silent truncation produces. Route → `fix`.

### 4.6 Fabrication (L5)
A path with `evidence_uri IS NULL`, or whose artifact fails replay (§7), is dropped from
`P` before the vote and recorded; if dropping it takes `q<2`, verdict becomes
`UNVERIFIED`; if the fabricated path was the **primary**, verdict becomes `QUARANTINED` and
routes `escalate`.

---

## 5. Worked numeric examples — on CARDEEP's real numbers

### 5.1 Desguaces, national — TRUSTWORTHY (real, 1.292)
Paths:
| path | value | family | origin |
|---|---|---|---|
| db_ingested | 1292 | self | dgt_cat (SQL) |
| dgt_returnCountOnly | 1292 | registry | DGT CATV ArcGIS |
| census_BCN_extrapolation* | 1300 | aggregator | SOURCES_ES triangulation |

`V={1292,1292,1300}`, `τ=0.02`. divergence `d=(1300−1292)/1300=0.0062 ≤ τ`.
`q = cdp_modal_cluster = 3` (1300 is within 2% of 1292). `f = 3` distinct families.
`r=0`. primary `1292 ∈` cluster. Not a round cap (1292). →
**TRUSTWORTHY**. The DB CHECK passes (`quorum_n=3≥2, family_n=3≥2`). *(\*the BCN-76-exact
corroboration in PROGRESO is the province-cell instance of this; national uses the
aggregator triangulation.)*

### 5.2 The `discover.py` default paths alone — UNVERIFIED, not TRUSTWORTHY
Paths actually written today for a source: `{db_ingested, fetched, source_declared}`.
Say all three = 241 (Kia). Under the *old* `verify.py` this reads near-TRUSTWORTHY. Under
the **deep** rule: `db_ingested` and `fetched` share `family='self'`; `source_declared`
shares the same HTTP origin → effectively `f` (distinct external families) `= 1`. So
**`family_n=1 < 2` → UNVERIFIED.** The gate stays closed until an orthogonal path (FACONAUTO
roster, OEM locator cross-count, hand-curl) is added. **This is the single biggest honesty
upgrade over the current VAM** — it stops a self-confirming harvest from reading as truth.
Kia becomes TRUSTWORTHY only after, e.g., the FACONAUTO/AMDA roster (family `aggregator`)
corroborates 241.

### 5.3 Silent cap — QUARANTINED (synthetic but realistic for AS24 per-dealer)
A dealer harvest returns `db_available=1000, harvested=1000, source_declared=1000`. `q=3,
f` (self+self+source) `→` even if external, all land on **1000**. `denominator` not
applicable per-dealer, but the **page-cap rule** fires: AS24 paginates 20/page; 1000 =
50·20 exactly and the profile counter said "1.2k vehículos". cap_suspect → **QUARANTINED**,
Gestionador `fix` (raise page depth). Without this rule we would have published a truncated
inventory as TRUSTWORTHY — a lie.

### 5.4 Inflated count — REFUTED (VW OneHub, real refutation)
Census claimed `source_declared=263` VW dealers. Live verification path
`http_probe=0` (HTTP 500). SEAT-sitemap path `=166`. `V={263,0,166}`. No cluster of ≥2
(all differ beyond τ); the **primary path that produced 263 returns 0 on replay** →
`primary_value ∉ modal_cluster`. → **REFUTED**, Gestionador `research` ("fix the URL /
serviceConfigEndpoint param"). Matches the real SOURCES_ES §8 finding exactly.

### 5.5 Coverage gap — UNVERIFIED segment (real, garaje vs denominator)
Live garaje observed `= 7.200`. Denominator estimate for `segment='garaje'` (PA 29.955
floor; CETRAA ~20.000): Chapman with `n1=29955 (PA), n2≈20000 (CETRAA), m2≈9000` →
`N̂ = (n1+1)(n2+1)/(m2+1) − 1 = 29956·20001/9001 − 1 ≈ 66.554 − 1 ≈ 66.553`. (This counts
*all* garages; the sellable subset is smaller, hence the `to filter` note — a second claim.)
Coverage `7200 / ci_low`. Even against the conservative floor 29.955, `7200 ≪ 29.955` →
**coverage_gap**, segment verdict **UNVERIFIED**, Gestionador `research` (add sources:
RASIC 12.155, CyL 6.714, Madrid censo). The dashboard shows garaje coverage honestly as
**~24% of floor**, not "done."

### 5.6 Denominator CI itself — Chapman + variance (the number behind the gauges)
Chapman estimator and its variance (Seber):
```
N̂  = (n1+1)(n2+1)/(m2+1) − 1
Var = (n1+1)(n2+1)(n1−m2)(n2−m2) / ((m2+1)²(m2+2))
CI  = N̂ ± 1.96·√Var
```
Worked for **desguaces** with `n1=1292 (DGT)`, `n2=1386 (DesguacesDirecto)`, overlap
`m2≈1180` (DGT mostly ⊂ aggregator):
`N̂ = 1293·1387/1181 − 1 ≈ 1518 − 1 ≈ 1517`.
`Var = 1293·1387·(1292−1180)(1386−1180)/(1181²·1182) ≈ 1293·1387·112·206 / (1.394e6·1182)`
`≈ 4.14e10 / 1.648e9 ≈ 25.1`, `√Var ≈ 5.0`, CI `≈ 1517 ± 9.8 = [1507, 1527]`.
So the **honest** desguace denominator is ~1.5k once long-tail unofficial scrappers are
counted, while the **official servable** floor is DGT's 1.292. The dashboard publishes
coverage as **1.292 / [1507,1527] ≈ 85% (CI 84.6–85.7%)** of the *real* population — and
**100% of the official DGT register**, stated as two distinct, non-misleading KPIs.

---

## 6. Mapping the existing verifier onto the deep ledger (no rewrite, an upgrade)

`record_count_verdict(conn, subject_type, subject_key, claim, paths, tolerance)` is extended
(signature-compatible) to:
1. Build **path objects** (attach `family/transport/origin/evidence_uri`) from a small
   registry keyed by path-name (`db_ingested→self/sql`, `fetched→self/http`,
   `source_declared→source/http`, `dgt_returnCountOnly→registry/arcgis`, …).
2. Compute `independent_values` = the numeric list; write it so the **generated columns**
   `quorum_n`,`family_n` derive in-DB.
3. Apply §4 decision (including the new family/cap/expiry guards) to choose the verdict.
4. On any non-TRUSTWORTHY, `INSERT … gestionador_item` with the routed action.
5. Set `expires_at` from the §4.4 SLA table.

Backward compat: old call sites keep working; they simply start producing **UNVERIFIED**
(honest) instead of false-TRUSTWORTHY when only self-family paths exist — which is the point.

---

## 7. Replay — turning "trust" into "reproduce"
`evidence_uri` is not decoration. Each value must be **re-derivable**:
- `sql:<sha256(query)>` → re-run the stored query, compare.
- `http:<url>@<iso8601>` + `data/probe/<blobhash>` → the raw artifact is on disk
  (the harvester already dumps raw to `data/` per PROGRESO); re-extract with the recipe.
- `arcgis:<layer>?returnCountOnly` → re-hit the count endpoint.
A nightly **replay job** samples k% of TRUSTWORTHY verdicts, reproduces each path, and if a
value no longer reproduces within τ, inserts a fresh **REFUTED**/**QUARANTINED** verdict
(the gate self-corrects) + a `fabrication`/`stale` Gestionador item. Replay is what makes
fabrication (L5) and staleness (L4) *detectable*, not just *declarable*.

### 7.1 Eviction vs replay — the artifact must outlive nothing but its verdict `[adversarial GAP-35]`
`08-REPO-ORGANIZATION` makes `data/**` GITIGNORED and EVICTED by capacity (`evict.py`), keeping
only a KB-sized `tombstone.json`. But the `data/probe/<blobhash>` artifact a verdict's
`evidence_uri` points at is **exactly what eviction deletes** — after eviction, the
`http:<url>@<ts> + data/probe/<blobhash>` replay above cannot reproduce, so replay-based
fabrication/staleness detection (the §10 guarantee) is silently unavailable for €0 on any subject
whose crude was evicted (most of them over time). Reproducibility-from-recipe (08 law #5) and
reproducibility-from-artifact (here) are DISTINCT: the recipe re-runs the SAME path that produced
the count and cannot detect a fabricated COUNT; only the pinned artifact can.
- **RULE (binding): TRUSTWORTHY verdicts pin their crude.** `evict.py` **MUST skip any blob
  referenced by `evidence_uri` of a non-expired TRUSTWORTHY verdict.** The pinned set is small and
  bounded (only the latest, live verdict per subject pins; superseded/expired verdicts release their
  pin), so capacity pressure is bounded, not unbounded.
- **Once a verdict EXPIRES** (C-11 TTL), its crude becomes evict-eligible and replay for that subject
  correctly requires a live re-fetch (the spend already acknowledged for Tier-1, MASTER_PLAN P11).
  The artifact thus survives **exactly as long as the verdict it proves** — no longer, no shorter.
- A `fabricated-COUNT` is therefore detectable for €0 on every *live* TRUSTWORTHY subject (its pinned
  artifact replays); after expiry, detection is by live re-fetch, declared, never assumed-available.

---

## 8. The verification API (read surface) — honest KPIs only

Mounted alongside the existing FastAPI (`services/api/main.py`, same `{ok,data,error,meta}`
envelope). All counts come from `v_latest_verdict` / the views — never raw tables.

| Endpoint | Returns |
|---|---|
| `GET /verify/health` | chain integrity (§3.3 query → `intact: true/false`, broken_seq), counts of verdicts by label, open Gestionador by route |
| `GET /verify/coverage?segment=&province=` | per-cell: `observed`, `denominator{point,ci_low,ci_high,method}`, `coverage_pct`, `coverage_ci`, `verdict` |
| `GET /verify/segments` | matrix segment × {observed, trustworthy, unverified, quarantined, coverage_pct} |
| `GET /verify/provinces` | 52 rows: per-province observed vs CI, coverage %, # publishable entities |
| `GET /verify/subject/{type}/{key}` | full verdict history for one subject (audit-backed timeline) |
| `GET /verify/gestionador?route=&state=` | open work items (the honest backlog) |
| `GET /verify/denominator` | national + per-segment CI table with sources_used |

**Response contract (worked, desguace national):**
```json
{ "ok": true,
  "data": { "segment": "desguace", "province": null,
            "observed": 1292,
            "denominator": { "point": 1517, "ci_low": 1507, "ci_high": 1527, "method": "chapman" },
            "coverage_pct": 85.2, "coverage_ci": [84.6, 85.7],
            "official_register_pct": 100.0,
            "verdict": "TRUSTWORTHY" },
  "error": null, "meta": { "as_of": "2026-06-12T00:00:00Z" } }
```
Two KPIs, never conflated: **coverage of the estimated real population (with CI)** and
**coverage of the official register**. No single rosy number.

---

## 9. The dashboard — what an operator sees (and can't be lied to by)

A read-only board over the §8 endpoints. Tiles:

1. **Integrity** — green only if the audit hash-chain verifies (§3.3) AND no verdict row
   lacks a `verdict_audit` witness. Red ⇒ tampering/data-loss; everything else is suspect.
2. **Coverage matrix** — segment × province heatmap of `coverage_pct`, each cell colored by
   its `verdict` (TRUSTWORTHY green / UNVERIFIED amber / QUARANTINED red), the CI band shown
   on hover. Empty (denominator-less) cells are grey, **not** green.
3. **Trust ledger** — counts: TRUSTWORTHY vs UNVERIFIED vs REFUTED vs QUARANTINED, and the
   **publishable %** = served / observed. (Today, e.g., desguace TRUSTWORTHY; garaje
   UNVERIFIED at ~24% of floor — shown as such.)
4. **Gestionador backlog** — open items by route (fix/research/quarantine/escalate) and
   severity; critical-route items are the operator's queue.
5. **Denominator panel** — per-segment CI, the capture-recapture inputs (n1,n2,m2) and which
   sources produced them; staleness countdown to next F8 refresh.
6. **Drift / freshness** — # of subjects whose verdict expires in <24h (the re-harvest queue).

**KPI honesty rules baked into the board:**
- Coverage is always shown **against a CI**, never a point number alone.
- A segment with no denominator estimate shows "coverage: unknown," not 100%.
- "Entities: 12.814" is labelled **observed**; "served" is the (smaller) publishable count;
  the two are never merged into one triumphant figure.
- Every TRUSTWORTHY tile is click-through to its audit row + replayable evidence.

---

## 10. Why this is the deepest validator (summary of the guarantees)

1. **Quorum is in the database, not the code** — `chk_trustworthy_needs_quorum` over
   *generated* `quorum_n`/`family_n`; you cannot store a TRUSTWORTHY lie.
2. **Independence is modeled and enforced** — ≥2 *families*, not just ≥2 *paths*; the
   self-confirming-harvest loophole of the current VAM is closed (§5.2).
3. **The audit trail is immutable and hash-chained** — append-only triggers + chain
   verification; tampering is detectable.
4. **The publish-gate is a bound view** — the data API physically cannot serve a
   non-TRUSTWORTHY/expired number; gaps are confessed.
5. **Six lie modes each have a detection, a verdict, and a route** — nothing is dropped;
   the Gestionador is the honest backlog.
6. **Staleness self-expires the gate**; **replay turns trust into reproduction**;
   **silent caps are quarantined** even when paths "agree."
7. **Denominator is a CI, not a guess** — coverage is reported as an interval and split
   from official-register coverage, so no rosy single number is ever sold.

> Better to confess a gap than sell a lie — and here the database itself refuses to let the
> lie be stored.
