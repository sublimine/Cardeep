# COUNTRY SWITCHOVER — onboarding country #2 (the Fase-0 follow-on checklist)

> Scope: the EXACT code + schema deltas to flip when you add a second tenant
> (e.g. `DE`, `FR`) on top of what Fase-0 already landed. Fase-0 made the census
> *country-parametrizable* WITHOUT touching any ES byte; this doc is the deferred
> work Fase-0 explicitly left undone, enumerated as an executable checklist.
>
> Every claim below was read from the real code and verified against the live PG
> (`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`) on 2026-06-23.
> Where a number is cited it is `[VERIFIED]` from a live query, not from prose.

---

## 0. Live ground truth (verified 2026-06-23)

Run this first; the rest of the doc assumes these baselines and the
verification steps re-query them.

```bash
cd /path/to/cardeep
python - <<'PY'
import asyncio, asyncpg
DSN='postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep'
async def m():
    c=await asyncpg.connect(DSN)
    for n,s in [
      ('entity_total','SELECT count(*) FROM entity'),
      ('entity_nonES',"SELECT count(*) FROM entity WHERE country_code<>'ES'"),
      ('geo_province','SELECT count(*) FROM geo_province'),
      ('geo_comarca','SELECT count(*) FROM geo_comarca'),
      ('geo_municipality','SELECT count(*) FROM geo_municipality'),
      ('vehicle','SELECT count(*) FROM vehicle'),
    ]:
        print(n,'=',await c.fetchval(s))
    await c.close()
asyncio.run(m())
PY
```

Live values today (the switchover MUST NOT change any of them for ES):

| Object | Live count | Source |
|---|---|---|
| `entity` (all `country_code='ES'`) | **431,212** | live query 2026-06-23 |
| `entity` where `country_code<>'ES'` | **0** | live query 2026-06-23 |
| `geo_province` | **52** | live query |
| `geo_comarca` | **323** | live query |
| `geo_municipality` | **8,132** | live query |
| `vehicle` | **2,312,297** | live query |
| `vehicle_event` | **2,613,139** | live query |
| `entity_completion` | **37,657** | live query |
| `entity` non-`particular` | **91,412** | live query |

> DRIFT NOTE: `migrations/0052_country.sql:20-22` documents the at-migration-time
> counts as **431,211** entity / 52 province / 8,132 municipality / 323 comarca.
> Live entity is now **431,212** (one row higher) because harvest/cosecha keeps
> running. `docs/architecture/SYSTEM-A-Z.md` historically said ~419k served — that
> is the *served/dedup* subset, NOT the raw `entity` rowcount (431,212). When you
> quote a number in the switchover, quote the live query, not a doc literal.

Entity kind distribution (drives `_NATIONAL_KINDS` and the geo adapter, §4):
`particular` 339,800 · `compraventa` 76,076 · `garaje` 10,021 · `desguace` 2,785 ·
`concesionario_oficial` 2,300 · `subasta` 177 · `plataforma` 18 · `oem_vo_portal` 14 ·
`importador` 11 · `rent_a_car_vo` 6 · `cadena` 4 `[VERIFIED live]`.

---

## What Fase-0 ALREADY did (do NOT redo)

These are live and verified — they are the platform the switchover builds on:

1. **`country_code CHAR(2) NOT NULL DEFAULT 'ES'`** added to `geo_province`,
   `geo_comarca`, `geo_municipality`, `entity`
   (`migrations/0052_country.sql:51-54`). Live: all four columns exist, default
   `'ES'::bpchar` `[VERIFIED]`.
2. **Composite UNIQUE** `(country_code, code)` on `geo_province`
   (`uq_geo_province_country_code`, `0052:63-65`) and `geo_municipality`
   (`uq_geo_municipality_country_code`, `0052:72-74`). Live: both present `[VERIFIED]`.
3. **Country-scoped indexes** `idx_entity_country`, `idx_geo_municipality_country`
   (`0052:80-81`).
4. **`mint_code(*, province_code, digest, country_code='ES')`** — the ONE home of
   the `CDP-{country}-` prefix literal (`services/api/codes.py:44-53`).
5. **`canonical_key(... country_code='ES')`** that DELIBERATELY ignores the country
   in the returned dedup pre-image (`codes.py:61-65`) — so threading a country can
   never re-key an entity.
6. **`pipeline/paths.py`** — `recipe_root` / `recipes_flat_dir` / `data_root` /
   `census_dir` / `country_of_cdp`, all defaulting to `ES`
   (`paths.py:33-63`). `country_of_cdp` already parses `^CDP-([A-Z]{2})-`
   (`paths.py:30`).

Fase-0's regression guard is `tests/test_country_golden.py` — it pins ES
byte-identity and contains the **strict-xfail** that flips when the switchover
lands (see §2).

---

## DEFERRED items (the switchover) — verbatim from `0052_country.sql:25-41`

The migration's own "DELIBERATELY NOT DONE in FASE-0" block enumerates the
deferred work. Each lettered item below maps to a checklist section:

- **(a)** swap `geo_province` / `geo_municipality` PK to `(country_code, code)` →
  forces composite rewrite of all 7 FKs → **§1**.
- **(b)** add `country_code` to `denominator_estimate` / `organization` and rewrite
  their FKs → **§1**.
- **(c)** relax the ES-specific CHECKs `municipality_province_prefix`
  (`geo_municipality`) and `chk_entity_muni_province` (`entity`) to per-country →
  **§3**.
- **(d)** `country_code` on `vehicle` (2,312,297 rows) — derivable via
  `vehicle.entity_ulid → entity.country_code`; YAGNI, stays deferred unless a
  query proves it needed → **§3 note**.
- **(e)** `geo_comarca` composite UNIQUE — `geo_comarca` has no `code` column
  (PK `id`, UNIQUE `(province_code, name)`), so no `(country, code)` surface; the
  2-vs-3-level adapter handles it → **§4**.

---

## 1. The onboarding migration: PK swap + FK rewrites

**File to create:** `migrations/0053_country_onboarding.sql` (next free number;
last applied is `0052_country.sql` `[VERIFIED: ls migrations/]`).

### 1.1 Why this is one atomic migration

The FK fan-out is exact and verified live. `geo_province.code` (PK
`geo_province_pkey`, `0001_geo.sql:5`) is referenced by **5 FKs**, all confirmed
live via `pg_constraint`:

| Child FK | Definition |
|---|---|
| `denominator_estimate_province_code_fkey` | `FK (province_code) REFERENCES geo_province(code)` |
| `entity_province_code_fkey` | `FK (province_code) REFERENCES geo_province(code)` |
| `geo_comarca_province_code_fkey` | `FK (province_code) REFERENCES geo_province(code)` |
| `geo_municipality_province_code_fkey` | `FK (province_code) REFERENCES geo_province(code)` |
| `organization_hq_province_code_fkey` | `FK (hq_province_code) REFERENCES geo_province(code)` |

`geo_municipality.code` (PK `geo_municipality_pkey`, `0001_geo.sql:19`) is
referenced by **1 FK**: `entity.entity_municipality_code_fkey`.
`entity.cdp_code` (UNIQUE INDEX `uq_entity_cdp_code`, NOT a named constraint —
`CREATE UNIQUE INDEX uq_entity_cdp_code ON public.entity USING btree (cdp_code)`
`[VERIFIED live]`) is referenced by **1 FK**: `entity_completion_cdp_code_fkey`.
Total = **5 + 1 + 1 = 7 FKs**, exactly as `0052_country.sql:9-18` states.

A composite PK swap on `geo_province`/`geo_municipality` invalidates every
single-column FK targeting the old PK, so the PK swap and ALL its FK rewrites
must be in **one transaction** (the runner wraps each migration in
`async with conn.transaction():` — `scripts/migrate.py:118`).

> `entity.cdp_code` and its FK are **NOT** touched here. `cdp_code` is already
> globally unique across countries (the `CDP-{cc}-` prefix differs per country —
> `mint_code`, `codes.py:53`), so `uq_entity_cdp_code` and
> `entity_completion_cdp_code_fkey` stay single-column. Leave them alone.

### 1.2 Exact DDL to write

Follow the house conventions verified in existing migrations: additive/guarded,
idempotent, single trailing `-- Rollback:` marker (the runner strips from the
LAST `-- Rollback:` via `rfind` — `scripts/migrate.py:47-65`; a header mention is
safe because the strip falls back to full SQL if no forward DDL remains).

```sql
-- 0053_country_onboarding.sql — flip geo PK to (country_code, code) and rewrite
-- the 5+1 referencing FKs to composite. Pre-req: 0052 applied (composite UNIQUEs
-- already exist). This migration is the FK-breaking half deferred by 0052:25-31.
-- ALL ES rows are country_code='ES' so the composite keys are 1:1 with the old
-- single-column keys; no row is renumbered, no FK target changes for ES.

BEGIN;  -- (the runner already opens a txn; BEGIN is illustrative for manual psql)

-- (b) add country_code to the two tables 0052 skipped, default 'ES' backfills.
ALTER TABLE denominator_estimate ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE organization         ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

-- 1. Drop the 6 child FKs that target the single-column geo PKs.
ALTER TABLE entity               DROP CONSTRAINT entity_province_code_fkey;
ALTER TABLE entity               DROP CONSTRAINT entity_municipality_code_fkey;
ALTER TABLE geo_comarca          DROP CONSTRAINT geo_comarca_province_code_fkey;
ALTER TABLE geo_municipality     DROP CONSTRAINT geo_municipality_province_code_fkey;
ALTER TABLE denominator_estimate DROP CONSTRAINT denominator_estimate_province_code_fkey;
ALTER TABLE organization         DROP CONSTRAINT organization_hq_province_code_fkey;

-- 2. Swap the PKs to composite. The composite UNIQUEs from 0052 already enforce
--    uniqueness; promote them to PK after dropping the old single-column PK.
ALTER TABLE geo_municipality DROP CONSTRAINT geo_municipality_pkey;
ALTER TABLE geo_province     DROP CONSTRAINT geo_province_pkey;
ALTER TABLE geo_province     ADD CONSTRAINT geo_province_pkey     PRIMARY KEY (country_code, code);
ALTER TABLE geo_municipality ADD CONSTRAINT geo_municipality_pkey PRIMARY KEY (country_code, code);
-- (the now-redundant uq_geo_*_country_code UNIQUEs may be dropped, or kept as
--  documentation; dropping them is cleaner since the PK now covers them.)

-- 3. Re-add the 6 FKs as COMPOSITE (country_code, code).
ALTER TABLE geo_comarca
  ADD CONSTRAINT geo_comarca_province_code_fkey
  FOREIGN KEY (country_code, province_code) REFERENCES geo_province(country_code, code);
ALTER TABLE geo_municipality
  ADD CONSTRAINT geo_municipality_province_code_fkey
  FOREIGN KEY (country_code, province_code) REFERENCES geo_province(country_code, code);
ALTER TABLE entity
  ADD CONSTRAINT entity_province_code_fkey
  FOREIGN KEY (country_code, province_code) REFERENCES geo_province(country_code, code);
ALTER TABLE entity
  ADD CONSTRAINT entity_municipality_code_fkey
  FOREIGN KEY (country_code, municipality_code) REFERENCES geo_municipality(country_code, code);
ALTER TABLE denominator_estimate
  ADD CONSTRAINT denominator_estimate_province_code_fkey
  FOREIGN KEY (country_code, province_code) REFERENCES geo_province(country_code, code);
ALTER TABLE organization
  ADD CONSTRAINT organization_hq_province_code_fkey
  FOREIGN KEY (country_code, hq_province_code) REFERENCES geo_province(country_code, code);

COMMIT;

-- Rollback:
-- (reverse: drop composite FKs, restore single-column PKs from the composite
--  UNIQUEs, re-add single-column FKs, drop the two added country_code columns)
```

> CAVEAT — NULLable FK columns: `entity.province_code` and
> `entity.municipality_code` are nullable (gap dealers carry NULL — see
> `chk_entity_muni_province`, §3). A composite FK with one NULL component is NOT
> enforced by PG (MATCH SIMPLE, the default), which preserves today's behavior:
> NULL geo rows stay valid. Do NOT use `MATCH FULL`.

### 1.3 Verification

```bash
python -m scripts.migrate up        # applies 0053; prints "applied 0053 ..."
python -m scripts.migrate verify    # 0 drift required (CI gate; exit 0)
```

Then assert the FK shape flipped and ES rowcount is unchanged:

```sql
-- expect 6 composite FKs now reference (country_code, code)
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname IN ('entity_province_code_fkey','entity_municipality_code_fkey',
  'geo_comarca_province_code_fkey','geo_municipality_province_code_fkey',
  'denominator_estimate_province_code_fkey','organization_hq_province_code_fkey');
-- expect geo PKs are composite
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
WHERE conname IN ('geo_province_pkey','geo_municipality_pkey');
-- ES invariant: rowcount byte-identical to §0 baseline
SELECT count(*) FROM entity WHERE country_code='ES';   -- expect 431,212 (or live §0)
```

**GATE:** if any ES rowcount changes or `verify` shows drift → ROLLBACK (the
migration is a single txn; an exception inside `conn.transaction()` auto-aborts —
`scripts/migrate.py:118-124`). Re-running `up` is safe (ledger skips applied).

---

## 2. The regex widening — the HIDDEN 6th blocker

**File:** `pipeline/complete.py:89`. This is the ONLY entity-gating regex still
hard-coding `^CDP-ES-`. Confirmed exhaustively:
`services/api/codes.py:51` is a docstring only, and `pipeline/paths.py:30`
already uses the widened form `^CDP-([A-Z]{2})-` `[VERIFIED via grep across
services/ and pipeline/]`.

### 2.1 Exact change

Current (`pipeline/complete.py:87-89`):

```python
# cdp_code format: CDP-ES-{NN}-{8×Crockford-base32}
# Crockford alphabet: digits + uppercase excluding I, L, O, U
_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")
```

Change the literal `ES` to a 2-letter class — strict superset, accepts every live
ES code unchanged AND any `CDP-XX-`:

```python
# cdp_code format: CDP-{CC}-{NN}-{8×Crockford-base32}
# Crockford alphabet: digits + uppercase excluding I, L, O, U
_CDP_CODE_RE = re.compile(r"^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")
```

> The `[0-9]{2}` province segment is NOT a country concern (it is the geo zone /
> '00' national sentinel — see `_PROVINCE_RE`, `complete.py:73`, and the
> `_NATIONAL_KINDS` block `complete.py:75-85`). Province-range validity per
> country is handled in §4, not in this regex. Keep `[0-9]{2}` as-is.

### 2.2 Flip the xfail in the golden test

`tests/test_country_golden.py:278-291` `TestG1RegexCountryWidening::test_accepts_foreign_country_segment`
currently self-`pytest.xfail()`s while the regex is narrow. The test's own
docstring (`:283-284`) says it "AUTO-FLIPS to XPASS ... then the marker must be
removed." After widening:

- Remove the `if not rx.match("CDP-DE-28-FPB3W1R6"): pytest.xfail(...)` guard
  (`test_country_golden.py:286-290`) so the two `assert rx.match(...)` lines
  (`:291-292`) run unconditionally.

### 2.3 Verification

```bash
python -m pytest tests/test_country_golden.py::TestG1RegexCountryWidening -v
# all 3 tests PASS (no xfail/xpass). Specifically:
#   test_accepts_all_live_es_codes   PASS  (every CDP-ES- code still matches)
#   test_accepts_foreign_country_segment PASS (CDP-DE-/CDP-FR- now match)
#   test_rejects_malformed           PASS  (3-letter country, 1-digit prov, etc rejected)
python -m pytest tests/test_country_golden.py -q   # full Fase-0 guard still green
```

**GATE:** `test_rejects_malformed` (`:294-305`) must still reject `CDP-ESP-...`
(3-letter), `cdp-es-...` (lowercase), 7/9-char tails, and `I`/`L` tails. If it
doesn't, the class is too loose — revert.

---

## 3. Geo CHECK relaxation (deferred item (c))

Two ES-shaped CHECKs assume INE's `<prov2><muni3>` municipality coding. They are
satisfied by every current row (all ES), so Fase-0 left them; a country whose
municipality codes are NOT `<province2><local3>` must relax them at onboarding.

### 3.1 The two CHECKs (verified live)

| Constraint | Table | Definition (live) | Origin |
|---|---|---|---|
| `municipality_province_prefix` | `geo_municipality` | `CHECK (left(code,2) = province_code)` | `0001_geo.sql:26` |
| `chk_entity_muni_province` | `entity` | `CHECK (municipality_code IS NULL OR province_code IS NULL OR left(municipality_code,2) = province_code)` | `0041_entity_muni_province_invariant.sql:14-17` |

### 3.2 Decision per country (do NOT relax blindly)

- If country #2's municipality codes ALSO prefix the province (many EU NUTS-like
  schemes do), KEEP both CHECKs as-is — they remain correct and free. Skip §3.3.
- If they do NOT (the new country uses non-prefixed muni codes), relax to
  per-country. Write the relaxation in `0053_country_onboarding.sql` (same
  migration as §1) so geo integrity is never momentarily unguarded.

### 3.3 Relaxation DDL (only if the new country needs it)

```sql
-- geo_municipality: gate the prefix invariant on ES only.
ALTER TABLE geo_municipality DROP CONSTRAINT municipality_province_prefix;
ALTER TABLE geo_municipality ADD CONSTRAINT municipality_province_prefix
  CHECK (country_code <> 'ES' OR left(code, 2) = province_code);

-- entity: gate the muni/province prefix invariant on ES only (preserve the
-- NULL-tolerant shape from 0041 exactly).
ALTER TABLE entity DROP CONSTRAINT chk_entity_muni_province;
ALTER TABLE entity ADD CONSTRAINT chk_entity_muni_province
  CHECK (country_code <> 'ES'
         OR municipality_code IS NULL OR province_code IS NULL
         OR left(municipality_code, 2) = province_code);
```

> The ES branch (`country_code <> 'ES' OR ...`) keeps the ORIGINAL invariant
> binding on every ES row — so ES integrity is byte-identical, and the new
> country gets its own (country-specific) geo loader to enforce its own shape.

### 3.4 Deferred item (d): `vehicle.country_code`

Do NOT add it reflexively. `0052_country.sql:36-38` proves it is derivable via
`vehicle.entity_ulid → entity.country_code`; live `vehicle` = **2,312,297** rows
`[VERIFIED]`, so a column add is a 2.3M-row rewrite. Add it ONLY if a real query
plan proves the join is the bottleneck (YAGNI per the migration's own rationale).

### 3.5 Verification

```sql
-- ES rows still satisfy BOTH CHECKs (count unchanged vs §0)
SELECT count(*) FROM geo_municipality WHERE country_code='ES';  -- expect 8,132
SELECT count(*) FROM entity WHERE country_code='ES';            -- expect 431,212
-- the relaxed CHECK lets a non-prefixed new-country muni in (insert a probe row,
-- assert it commits, then ROLLBACK the probe).
```

---

## 4. The geo-hierarchy adapter (2 vs 3 levels) — deferred item (e)

ES uses a **3-level** backbone: `geo_province (52) → geo_comarca (323) →
geo_municipality (8,132)` `[VERIFIED live]`. `geo_comarca` is the OPTIONAL middle
level: it has **no `code` column** (PK is `id`
`GENERATED ALWAYS AS IDENTITY`, UNIQUE is `(province_code, name)` —
`0001_geo.sql:11-16`), and `geo_municipality.comarca_id` is **nullable**
(`0001_geo.sql:22`). So a 2-level country (province → municipality, no comarca)
already fits the schema with zero DDL: just never populate `geo_comarca` and leave
`comarca_id` NULL.

### 4.1 What to build: a per-country geo loader

There is no generic geo-loader module today; ES geo is resolved by
`pipeline/geo.py`, an INE-specific resolver (`geo.py:1-19`) with hard-coded ES
artifacts:

- `_PROVINCE_ALIASES` — island/bilingual ES province name → INE code map
  (`geo.py:61-71`), e.g. `"menorca":"07"`, `"gipuzkoa":"20"`.
- `_GAZETTEER_PATH = data/geo/nomenclator_entidades_ine.csv` — the ES INE
  Nomenclátor locality gazetteer (`geo.py:45-48`).
- It loads provinces/municipalities straight from the DB
  (`SELECT code, name FROM geo_province` / `... FROM geo_municipality` —
  `geo.py:153,157`), so once country #2's geo rows are seeded with their
  `country_code`, the resolver indexes them — BUT the index is currently NOT
  country-scoped.

**Onboarding actions:**

1. **Seed country #2's geo rows** into `geo_province` / (`geo_comarca` if 3-level)
   / `geo_municipality` with `country_code='<CC>'`. Use the official source for
   that country (the ES analog is INE). The composite PK from §1 lets a foreign
   `01` province coexist with ES `01`.
2. **Country-scope `pipeline/geo.py`’s queries** (`geo.py:153,157`): add
   `WHERE country_code = $1` and thread a `country_code` arg through the resolver,
   defaulting to `'ES'` (mirror the Fase-0 default-arg pattern in `codes.py` /
   `paths.py`). Provide the new country's own alias map + gazetteer (do NOT reuse
   the ES `_PROVINCE_ALIASES` / INE CSV).
3. **Widen the province-range validators per country.** `complete.py:73`
   `_PROVINCE_RE = ^(0[1-9]|[1-4][0-9]|5[0-2])$` hard-codes ES's 01-52 range and
   is referenced at `complete.py:142`; `_NATIONAL_KINDS` (`complete.py:83-85`,
   feeding the '00' national sentinel at `:141`) is also ES-tuned. For country #2,
   make the valid-province set country-aware (table-driven from `geo_province`
   filtered by `country_code`, or a per-country range), so a foreign province code
   is not rejected as `invalid_province_code`.

> `geo_comarca` composite UNIQUE (deferred item (e)): extend to
> `(country_code, province_code, name)` ONLY if country #2 is 3-level AND two
> countries could share a comarca name within the same province code. For a
> 2-level country this is moot (no comarca rows). `0052:39-41` documents this.

### 4.2 Verification

```sql
-- foreign geo seeded and country-scoped
SELECT country_code, count(*) FROM geo_province     GROUP BY 1;  -- ES=52, <CC>=N
SELECT country_code, count(*) FROM geo_municipality GROUP BY 1;
```

```python
# resolver returns a foreign muni code WITHOUT cross-country bleed
from pipeline.geo import GeoIndex   # (or the resolver entry point)
# assert resolve(country='<CC>', province='<foreign>', muni='<foreign>') is foreign
# assert resolve(country='ES', ...) is byte-identical to pre-switchover ES output
```

**GATE:** an ES resolution MUST return the same code it returned before
country-scoping (re-run a sample of `tests/test_geo*` or the resolver's own
fixtures); if any ES code changes, the `WHERE country_code` scoping leaked.

---

## 5. The per-country source roster

ES sources are **module-per-source**, not a registry file (there is no
`sources.yaml` / `registry.py` — `[VERIFIED: glob found none]`). Two families:

- `pipeline/sources/` — **26 modules** `[VERIFIED: ls | wc]` — discovery /
  triangulation feeds (e.g. `borme_cnae.py`, `axesor_cnae.py`,
  `paginas_amarillas.py`, `overture.py`, `dgt_cat.py`, OEM dealer-locators
  `oem_*.py`, census feeds `*_census.py`).
- `pipeline/platform/` — **47 modules** `[VERIFIED: ls | wc]` — marketplace /
  OEM-VO / CMS-family inventory connectors (e.g. `coches_net_facet.py`,
  `milanuncios_wholesale.py`, `wallapop_facet.py`, `as24_facet.py`, the
  `family_*` CMS connectors, the `oem_*_wholesale.py` portals).

These are **country-specific by construction**: `coches.net`, `milanuncios`,
`wallapop`, `paginas_amarillas`, BORME/DIRCE, INE are Spain-only. They are NOT
reusable for country #2 except as structural templates.

### 5.1 Onboarding actions

1. **Build a new source roster for country #2** under the same two folders, one
   module per real source (the new country's dominant marketplaces, its company
   register analog to BORME/DIRCE, its OEM dealer locators, its national
   statistics geo analog to INE). Keep the existing per-module shape so the
   harvest/ingest engine treats them identically.
2. **Route paths via `pipeline/paths.py` (already country-aware).** Every
   source/connector must call `recipe_root('<CC>')` / `data_root('<CC>')` /
   `census_dir('<CC>')` (`paths.py:33-52`) instead of hard-coding
   `countries/ES` / `data/ES`. The new tree is `countries/<CC>/recipes`,
   `countries/<CC>/census`, `data/<CC>`. Today the ES recipe tree has **60**
   per-dealer YAMLs in `countries/ES/recipes/` and one census CSV
   (`countries/ES/census/dirce_cnae451.csv`) `[VERIFIED: ls]`.
3. **Mint codes with the country arg.** Every connector that mints an entity must
   pass `country_code='<CC>'` to `cdp_code` / `cdp_pair` / `mint_code`
   (`codes.py:44,100,121`). The default is `'ES'` so an un-updated connector would
   silently mint `CDP-ES-` for a foreign entity — audit every mint call-site of
   the new roster. (`DEFAULT_COUNTRY` / `paths`/`codes` imports appear across
   **47 files** in `pipeline/` `[VERIFIED grep]`; the new roster's mints are the
   ones to thread.)
4. **Persist `entity.country_code='<CC>'`** on insert in the new country's ingest
   path. The column exists and defaults `'ES'` — so, as with minting, a missing
   explicit value silently stamps a foreign dealer as ES. Make it explicit in the
   new ingest writes.

### 5.2 Verification

```sql
-- no foreign entity accidentally minted as ES
SELECT count(*) FROM entity
WHERE country_code='<CC>' AND cdp_code NOT LIKE 'CDP-<CC>-%';   -- expect 0
-- no ES entity got a foreign prefix
SELECT count(*) FROM entity
WHERE country_code='ES' AND cdp_code NOT LIKE 'CDP-ES-%';       -- expect 0
```

```bash
# the new roster writes under countries/<CC>/, never countries/ES/
git status --porcelain countries/ES/   # expect EMPTY (ES tree untouched)
ls countries/<CC>/recipes countries/<CC>/census data/<CC>   # populated
```

---

## 6. Golden re-verification (the closing gate)

The whole switchover is "done" only when the ES byte-identity guard is still
green AND the new country surfaces correctly. `tests/test_country_golden.py` is
the contract.

### 6.1 ES must remain byte-identical

```bash
python -m pytest tests/test_country_golden.py -v
```

These classes pin the ES invariant and MUST all PASS (the literals at
`test_country_golden.py:54-69` are the live ES golden codes, e.g.
`domain:ford.es → CDP-ES-28-ZB6C77HC`):

- `TestCdpByteIdentityES` (`:72-96`) — ES `cdp_code`/`cdp_pair` unchanged.
- `TestDefaultCountryUnchanged` (`:99-130`) — `canonical_key` country-blind
  (`canonical_key(...,country_code='DE')` == `canonical_key(...,country_code='ES')`,
  `:115-119`), default == explicit ES.
- `TestMintCodeHelper` (`:133-180`) — `mint_code` ES default == legacy, only the
  country segment swaps (`:163-171`).
- `TestPathHelpersES` (`:183-227`) — ES paths == `countries/ES`, `data/ES`, etc.
- `TestCountryOfCdp` (`:230-257`) — `CDP-DE-...→DE`, garbage → ES.
- `TestG1RegexCountryWidening` (`:260-305`) — after §2 the xfail is removed and
  all 3 PASS.

### 6.2 New-country smoke

After §1-§5 land and a first harvest of country #2 runs:

```sql
-- the new country has entities, all correctly prefixed and stamped
SELECT count(*) FROM entity WHERE country_code='<CC>';          -- > 0
SELECT count(*) FROM entity
  WHERE country_code='<CC>' AND cdp_code LIKE 'CDP-<CC>-%';     -- == above
-- G1 (complete.py) accepts a sample of the new entities
```

```bash
python -m scripts.migrate verify    # exit 0 (no drift)
python -m pytest -q                  # full suite green (ES regression + new)
```

### 6.3 Final ES regression gate (non-negotiable)

```sql
-- the ONE number that proves we changed nothing for ES
SELECT count(*) FROM entity WHERE country_code='ES';   -- == §0 live baseline
```

If this differs from the §0 baseline (modulo legitimate ongoing cosecha for ES),
a switchover step leaked into ES — STOP and bisect by migration/commit.
`cdp_code` is the immutable dedup key over 431,212 ES entities
(`test_country_golden.py:4-6`); a single changed ES code re-keys the census.

---

## Switchover checklist (one line each)

- [ ] §1 `migrations/0053_country_onboarding.sql`: composite PK swap on
      `geo_province`/`geo_municipality` + rewrite the 6 geo FKs to composite +
      add `country_code` to `denominator_estimate`/`organization`
      (`0052:25-31`; FKs verified live). `migrate up` + `migrate verify` clean.
- [ ] §2 `pipeline/complete.py:89` widen `^CDP-ES-` → `^CDP-([A-Z]{2})-`;
      remove the xfail in `test_country_golden.py:286-290`.
- [ ] §3 relax `municipality_province_prefix` (`0001_geo.sql:26`) and
      `chk_entity_muni_province` (`0041:14-17`) to `country_code<>'ES' OR ...`
      ONLY if the new country's muni codes are not province-prefixed; do NOT add
      `vehicle.country_code` (2.3M rows, derivable).
- [ ] §4 seed country #2 geo (`country_code='<CC>'`), country-scope
      `pipeline/geo.py:153,157`, make `_PROVINCE_RE`/`_NATIONAL_KINDS`
      (`complete.py:73,83-85`) country-aware; comarca is optional (2 vs 3 level,
      `comarca_id` nullable per `0001_geo.sql:22`).
- [ ] §5 new source roster under `pipeline/sources/` + `pipeline/platform/`
      routing through `pipeline/paths.py` with `country_code='<CC>'`; thread
      `country_code` into every mint (`codes.py`) and ingest write.
- [ ] §6 `pytest tests/test_country_golden.py` green (ES byte-identity intact);
      `SELECT count(*) FROM entity WHERE country_code='ES'` == §0 baseline.
