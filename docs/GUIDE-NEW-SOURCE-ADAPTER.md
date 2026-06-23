# GUIDE — Add a New Source / Connector

> Part of the **Cardeep Replication Bible**. This is the most common replication
> task: wiring one more source into the census. It is **executable** — every
> command, query and gate below is grounded in the real code/DB (file:line and
> live numbers cited inline). Verified against the running DB on **2026-06-23**.
>
> Live DSN used throughout: `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`
> (`psql` is not on PATH on the dev box — use the `python + asyncpg` heredoc shown
> in §9).

---

## 0. What a "source" is, and the two kinds you can add

Cardeep has **two orthogonal source surfaces**, and they live in different
registries. Pick the right one before writing a line of code:

| Surface | Produces | Contract | Registry | CLI |
|---|---|---|---|---|
| **DISCOVER** (a *census* adapter) | dealer **entities** (points of sale) | `SourceAdapter` → `DiscoveredEntity` (`pipeline/sources/base.py:7-40`) | `ADAPTERS` in `pipeline/discover.py:48-74` | `python -m pipeline.discover <key>` |
| **SCRAPE** (a *harvest* connector) | **inventory** (vehicles) for known entities | a platform module under `pipeline/platform/*.py` that writes `record_run` | `REGISTRY` in `pipeline/ops/scheduler.py:131-291` | scheduler launches `python -m <module> [args]` |

The lifecycle the product runs is **DISCOVER → SCRAPE → RECIPE → API → DELTA**.
This guide covers adding a source to **either** surface, plus the **recipe** that
makes a scrape reproducible.

The **recipe** is a third, cross-cutting asset: a per-dealer YAML that lets
Cardeep re-scrape *without keeping the raw crude* (`pipeline/recipe_schema.py:1-21`).
The canonical way to mint+verify one is the **RecipeHarness**
(`pipeline/recipe_harness.py`). See §6 for the honest gap there.

### Country note (FASE 0)

A source is **country-scoped today only at the path/prefix layer**:

- `cdp_code` carries the country in its human prefix: `mint_code()` emits
  `CDP-{country_code}-{province2}-{base32}` with `country_code` defaulting to
  `"ES"` (`services/api/codes.py:44-53`). The **dedup pre-image deliberately does
  NOT include the country** (`services/api/codes.py:56-65`) so threading a country
  never re-keys an existing entity.
- Recipe/raw/census paths default to ES via `pipeline/paths.py`
  (`recipe_root`/`recipes_flat_dir`/`data_root`/`census_dir`, all default
  `DEFAULT_COUNTRY = "ES"`, `pipeline/paths.py:22,33-52`). `write_recipe` derives
  the country from the cdp_code via `country_of_cdp()` and lands the YAML under
  `countries/<CC>/recipes/` (`pipeline/recipe.py:43-94`, `pipeline/paths.py:55-63`).
- The DB has a `country_code CHAR(2) DEFAULT 'ES'` on `geo_province`,
  `geo_comarca`, `geo_municipality`, `entity` plus composite `UNIQUE
  (country_code, code)` (migration `migrations/0052_country.sql:51-77`). Live
  check: **431,212/431,212 entity rows are `country_code='ES'`** (§9).

> The full country switchover (PK swap to `(country_code, code)`, relaxing the
> ES-specific geo CHECKs `municipality_province_prefix` / `chk_entity_muni_province`,
> country-specific sources) is **deferred and documented** in
> `migrations/0052_country.sql:25-41`. Adding a *new source for the same country
> (ES)* — the subject of this guide — needs none of that.

---

## 1. Decision tree

```
Does the new source enumerate DEALERS (points of sale)?
  └─ YES → it's a DISCOVER adapter            → §2  (SourceAdapter)
Does the new source pull INVENTORY for dealers we already know?
  └─ YES → it's a SCRAPE connector            → §4  (platform module + REGISTRY)
Do you want a reproducible per-dealer extraction asset (recipe)?
  └─ YES → write an Extractor for the harness → §5–6 (RecipeHarness, EXTRACTORS)
```

Most replication work starts with a **DISCOVER adapter** (you need entities
before you can scrape them), so that is the worked example in §2–3.

---

## 2. Implement a DISCOVER adapter (`SourceAdapter`)

### 2.1 The contract — read it first

`pipeline/sources/base.py`:

- `DiscoveredEntity` (lines 7-26) is the normalized output. Required by the
  ingest path: `kind`, `source_key`. Everything else is optional but
  province-bearing fields drive geo-resolution. `extra: dict` carries
  source-specific metadata.
- `SourceAdapter` (lines 29-40) has exactly two methods you implement:
  - `declared_count() -> int | None` — **the source's own oracle** (its asserted
    total). This is the `source_declared` leg of the VAM quorum gate (§3.2). If
    the source cannot assert a count, return `None`.
  - `fetch() -> list[DiscoveredEntity]` — yields the entities.

### 2.2 Reference implementation — `KiaOemAdapter`

`pipeline/sources/oem_kia.py` is the cleanest minimal adapter (~106 lines, open
unauthenticated JSON, 242 dealers live as of 2026-06-12). Study it:

- `source_key = "oem_kia"` (line 56) — the stable key written to `entity_source`.
- `declared_count()` returns the **in-scope** count (Spain only), not the raw API
  count (`oem_kia.py:74-76`). The denominator must match what `fetch()` yields, or
  the VAM gate falsely refutes.
- `fetch()` (lines 78-105) maps each raw dealer to a `DiscoveredEntity`, sets
  `kind="concesionario_oficial"`, derives `province_name` from the postcode
  (INE province = first 2 digits, `oem_kia.py:67-72`), and **transparently
  excludes** out-of-scope (non-Spain) rows via `self.excluded_count`
  (`oem_kia.py:84`). `pipeline.discover` reads `excluded_count` for the run log
  (`discover.py:121-123`).

A **census-style** adapter (enumerate sellers from a directory/sitemap, not just
as a by-product of inventory) is shown by `AutocasionCensusAdapter`
(`pipeline/sources/autocasion_census.py`). Note its identity engineering: it mints
the *same* cdp_code inputs as the inventory connector
(`address="profesional:{slug}"`, `website=None`) so an already-known dealer
**collapses on `ON CONFLICT (cdp_code)`** instead of duplicating
(`autocasion_census.py:14-27, 205-212`). This dedup discipline is mandatory for any
new census source: never set `website` to a shared portal URL or every entity
collapses by domain.

### 2.3 Skeleton for a new adapter

Create `pipeline/sources/<your_source>.py`:

```python
"""<Source> dealer adapter — DISCOVER vector.
Open/authed surface, transport notes, verified live <date>: <N> entities.
"""
from __future__ import annotations

from pipeline.sources.base import DiscoveredEntity, SourceAdapter


class YourSourceAdapter(SourceAdapter):
    source_key = "your_source"           # stable; written to entity_source

    def __init__(self) -> None:
        self._rows: list[dict] | None = None
        self.excluded_count = 0           # read by pipeline.discover for the run log

    def _load(self) -> list[dict]:
        if self._rows is None:
            self._rows = ...              # fetch ONCE, cache (declared_count + fetch reuse it)
        return self._rows

    def declared_count(self) -> int | None:
        # the source's own oracle, scoped to the SAME denominator fetch() yields
        return sum(1 for r in self._load() if self._in_scope(r))

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        self.excluded_count = 0
        for r in self._load():
            if not self._in_scope(r):
                self.excluded_count += 1   # exclude transparently, never silently drop
                continue
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",      # or compraventa | garaje | desguace | plataforma | cadena
                source_key=self.source_key,
                source_ref=...,                    # stable id/url within the source
                legal_name=..., trade_name=...,
                province_name=...,                 # INE 2-digit code OR raw name (resolved at ingest)
                municipality_name=...,
                address=..., postcode=...,
                lat=..., lon=..., phone=..., email=..., website=...,
                extra={"brand": "..."},
            ))
        return out
```

**Rules grounded in the codebase:**

1. **Cache the fetch.** `declared_count()` and `fetch()` are both called by
   `pipeline.discover.discover()` (`discover.py:118-122`) — load the source once
   and cache (`oem_kia.py:62-65`, `autocasion_census.py:167-172`).
2. **Keep the denominator honest.** `declared_count()` must count exactly what
   `fetch()` will yield. Out-of-scope rows are excluded from *both* and counted in
   `excluded_count`.
3. **Identity dedup.** If this source can re-see dealers known from another
   source, mint the *same* cdp_code inputs (`name + municipality + address`, or
   `domain`, or `cif`) so it collapses on conflict — see
   `services/api/codes.py:56-97` for the canonical-key priority
   (`particular > domain > cif > name|municipality`).
4. **Never fabricate identity the source withholds**
   (`services/api/codes.py:66-71`).

---

## 3. Register and run the DISCOVER adapter

### 3.1 Register in `ADAPTERS`

Edit `pipeline/discover.py`:

1. Add the import next to the others (`discover.py:19-42`):
   ```python
   from pipeline.sources.your_source import YourSourceAdapter
   ```
2. Add the entry to `ADAPTERS` (`discover.py:48-74`):
   ```python
   ADAPTERS: dict[str, type[SourceAdapter]] = {
       ...
       "your_source": YourSourceAdapter,
   }
   ```

That is the whole registration. `main()` validates the key and runs it
(`discover.py:170-175`).

### 3.2 What `discover()` does for you — and the VAM gate

`pipeline/discover.py:117-167` is the canonical DISCOVER pipeline. It:

1. Calls `adapter.fetch()` + `adapter.declared_count()` and prints
   `declared / fetched / excluded_out_of_scope` (`discover.py:118-123`).
2. Loads the `GeoResolver`, geo-resolves each entity to INE codes, and (for
   lat/lon-only POIs) falls back to a `ProvinceGeocoder` (`discover.py:127-132,
   80-90`).
3. Mints the immutable `cdp_code` and upserts `entity` +
   `entity_source` **idempotently** via `ON CONFLICT (cdp_code) DO UPDATE SET
   last_seen = now()` (`discover.py:91-114`). `last_seen` is the heartbeat the
   delta/lifecycle reads.
4. Counts **per-run** ingestion `seen_at >= run_start` — NOT cumulative — so a
   later run that silently dropped entities cannot emit a false TRUSTWORTHY
   (`discover.py:148-154`).
5. **Closes with the VAM count quorum gate** (`discover.py:159-165`):
   ```python
   verdict = await record_count_verdict(
       conn, subject_type="source", subject_key=source_key,
       claim="entity count == declared count",
       paths={"db_ingested": in_db, "fetched": len(entities),
              "source_declared": declared},
       tolerance=0.0)
   ```

**Understand the gate (`pipeline/verify.py:53-212`)** — it is the acceptance
criterion for your source:

- A count is **TRUSTWORTHY** only when ≥2 **orthogonal** paths agree exactly AND
  span ≥2 collector *families* AND ≥2 *origins* (`verify.py:117-119, 156-159`).
  The three paths above map to families `db` / `http` / `source`
  (`verify.py:31-50`), so a clean run gives a real quorum.
- **UNVERIFIED** means "cannot certify a quorum" (e.g. same-family or
  within-tolerance-but-not-exact) — it is **not** a failure
  (`verify.py:160-164`).
- **REFUTED** means paths disagree — your `declared_count()` and what landed in
  the DB diverge. Fix the adapter, do not relax the gate.
- A modal value of **0** never certifies TRUSTWORTHY unless the caller passes
  `measured_by_observation=True` ("better a hole than a lie",
  `verify.py:150-155`).

### 3.3 Run and verify (TDD order)

```bash
cd /c/Users/elias/projects/cardeep

# 1) Unit test first (RED). Mirror tests/test_autoscout24_census.py shape.
python -m pytest tests/test_your_source.py -q

# 2) Live discover run (writes entity + entity_source + a verification_verdict)
python -m pipeline.discover your_source
```

Expected stdout tail (real shape from `discover.py:122-165`):

```
[your_source] declared=242 fetched=242 excluded_out_of_scope=3
[your_source] new=240 in_db=242 skipped_no_province=0 municipality_resolved=242/242 (100.0%)
[your_source] VAM verdict: TRUSTWORTHY
```

**Acceptance gate:** verdict is `TRUSTWORTHY` (or a documented `UNVERIFIED` when
the source asserts no count). `REFUTED` blocks — debug the denominator.

---

## 4. Implement + register a SCRAPE connector (inventory)

A SCRAPE connector is a `pipeline/platform/<name>_wholesale.py` module. There are
**47 platform modules today** (`ls pipeline/platform/*.py | wc -l` → 47). The
contract is *behavioral*, not a base class:

1. Declare a stable `*_SOURCE_KEY` constant (e.g.
   `KIA_SOURCE_KEY = "oem_kia_wholesale"`, `oem_kia_wholesale.py:121`). This is
   the key written to `source_health` and matched by the scheduler's DUE query.
2. Be runnable as `python -m pipeline.platform.<module> [args]` — an `argparse`
   `main()` + `if __name__ == "__main__"` (`oem_kia_wholesale.py:1247-1276`).
3. **Write its own `record_run`** on every path. The scheduler explicitly does
   NOT write health rows (`scheduler.py:5-9, 375-385`). `record_run` is *the
   single writer* of `source_health` + `source_breaker`
   (`pipeline/ops/health.py:84-128`); it also writes the `harvest_run` audit row,
   manages the circuit breaker, and (when `declared_total` is passed) auto-runs
   the B9 coverage gate. Real call: `oem_kia_wholesale.py:1178-1188`.
4. Respect the breaker: skip if `is_open(conn, SOURCE_KEY)` before draining
   (`oem_kia_wholesale.py:1074-1078`).

> Use `pipeline/platform/oem_kia_wholesale.py` as the template (open OEM-VO
> portal, full breaker + record_run + coverage wiring). Copy its structure; do
> not invent a second architecture.

### 4.1 Register in the scheduler `REGISTRY`

Edit `pipeline/ops/scheduler.py`, inside `_build_registry()`
(`scheduler.py:131-291`). Add one `SourceEntry(source_key, module, extra_args)`:

```python
SourceEntry("your_source_wholesale",
            "pipeline.platform.your_source_wholesale", ["--pages", "1"]),
```

- `source_key` **must equal** the `*_SOURCE_KEY` the connector writes to
  `source_health` — otherwise health/breaker/due-selection continuity breaks
  (this is the documented `F-autocasion-orphaned` regression cause,
  `scheduler.py:139-145`).
- `extra_args` is the exact argv tail passed to the subprocess
  (`scheduler.py:370-372`).
- **Multi-source modules**: one `SourceEntry` per key, disambiguated by
  `--member` / `--members` / `--brand` (`scheduler.py:112-119, 186-238`).

### 4.2 Seed the cadence row in `source_health`

The scheduler only runs sources that **exist in `source_health`** and are DUE
(`scheduler.py:309-349`). A connector that writes `record_run` will create its own
row on first run, but to schedule it from the start, seed a row with the desired
`harvest_interval_hours` (Tier-1 = 24h; OEM/groups = 168h; families = 720h, per
the section banners in `scheduler.py:138-289`). Connectors that need a *ban-safe*
cadence the connector itself doesn't pass rely on the migration seed (e.g. the AS24
168h cadence lives in the `0039` seed row, `scheduler.py:161-166`).

Live `source_health` has **56 rows** today (§9). The `--dry-run` gap report lists
any `source_health` key with **no module** as UNMAPPED and excludes it from
scheduling (`scheduler.py:359-363, 715-753`).

### 4.3 Validate at minimal scope (the pre-VPS rule)

Before scheduling, prove the connector works on this terminal at €0:

```bash
# Smoke ONE connector at minimal scope (no full drain)
python -m pipeline.platform.your_source_wholesale --pages 1

# Or via the matrix harness (serial, single-producer, per-connector timeout)
python scripts/validate_connectors.py your_source
```

`scripts/validate_connectors.py:1-12` is explicit: *prove every connector/recipe
WORKS on this terminal first; only what works here goes to the VPS.* It captures
VAM verdict + cars caged + exit into `state/validation_matrix.json`. Add your
connector to its `CONNECTORS` list (`validate_connectors.py:35+`).

---

## 5. Schedule the connector

### 5.1 Inspect what would run (READ-ONLY, safe anytime)

```bash
python -m pipeline.ops.scheduler --dry-run        # DUE sources + the exact argv + gap report
python -m pipeline.ops.scheduler --check-silence  # sources silent > 2x their interval (no alerts fired)
```

`--dry-run` prints registry coverage (total `source_health` rows, mapped,
UNMAPPED), then every DUE source with `WOULD RUN` / `UNMAPPED`
(`scheduler.py:690-754`). Confirm your key shows `WOULD RUN` with the right cmd.

### 5.2 Start the live scheduler

```bash
python -m pipeline.ops.scheduler                  # blocking; single-producer
```

Architecture you are joining (`scheduler.py:1-25, 815-949`):

- APScheduler 3.x `BlockingScheduler` + `SQLAlchemyJobStore` on cardeep-pg —
  crash-safe (jobs survive process death).
- **Single producer, in series**: one `heartbeat_tick` every
  `TICK_INTERVAL_MINUTES = 15` (`scheduler.py:76`) runs DUE connectors **one at a
  time** (`scheduler.py:484-520`). Never two subprocesses at once (the "AS24
  cicatriz" — two governors on one host lost 138 dealers,
  `scheduler.py:820-826`).
- A **session-level pg advisory lock** (`0x43415244` = 'CARD') refuses a second
  scheduler on the same host (`scheduler.py:826-837`).
- DUE selection:
  `now() - COALESCE(last_ok, last_fail, '1970-01-01') >= harvest_interval_hours *
  interval '1 hour'`, most-overdue first, breaker-open sources
  (`consecutive_fails >= 3`) skipped (`scheduler.py:309-349`).
- Each connector is launched with `PYTHONIOENCODING=utf-8` in the child env
  (Windows cp1252 fix, `scheduler.py:386-397`). 4h subprocess wall by default
  (`scheduler.py:102-104`).
- A crash-before-`record_run` safety net records the failure itself only if no new
  `harvest_run` row appeared this cycle (`scheduler.py:435-477`).

### 5.3 DISCOVER scheduling is a SEPARATE producer

DISCOVER vectors are **not** in the harvest `REGISTRY`. They are scheduled by
`pipeline/discover_schedule.py` (its own advisory lock `0x43415244 + 1`,
`discover_schedule.py:50`), with a `DISCOVERY_REGISTRY` of `DiscoveryJob`s carrying
their own cadence and recipe-first env knobs (`discover_schedule.py:53-84`):

```bash
python -m pipeline.discover_schedule --seed      # register cadence rows in source_health
python -m pipeline.discover_schedule --dry-run   # cadences + which vectors are DUE
python -m pipeline.discover_schedule --once your_source   # run one vector now
python -m pipeline.discover_schedule --tick      # run all DUE vectors once (cron-friendly)
python -m pipeline.discover_schedule --serve     # blocking loop
```

To schedule your new DISCOVER adapter recurrently, add a `DiscoveryJob` to
`DISCOVERY_REGISTRY` (`discover_schedule.py:65-84`):

```python
"your_source": DiscoveryJob(
    "your_source", "your_source", cadence_hours=168, orthogonal=True, env={}),
```

- `vector` is the argument passed to `python -m pipeline.discover <vector>`
  (`discover_schedule.py:163-167`) — it must equal your `ADAPTERS` key from §3.1.
- `orthogonal=True` marks it as an independent census list (vs a
  dependent/resolution vector).
- `requires_env=(...)` **GATES** auto-run when an env var is absent (e.g.
  `dork_municipal` refuses to auto-run without `CARDEEP_SEARXNG_URL` to avoid a
  DDG ban; `--once` overrides as operator intent, `discover_schedule.py:120-130,
  194-198`).

`_record` upserts `source_health` directly (€0, no harvest side-effects) so the
vector still surfaces in `--check-silence` and the gap report
(`discover_schedule.py:18-21, 133-160`).

---

## 6. The recipe — reproducible per-dealer extraction (and the honest gap)

A **recipe** is the durable asset that lets Cardeep re-scrape *without the raw
crude* (`pipeline/recipe_schema.py:1-21`). The schema is a round-trippable
`Recipe` dataclass (`recipe_schema.py:96-167`): `transport` / `fingerprint` /
`pagination` / `parsing` / `evidence`, with a **closed status vocabulary**
`DRAFT | VERIFIED | FAILED` (`recipe_schema.py:29-33`) — a recipe is never in an
unnamed state.

### 6.1 The canonical cycle — `RecipeHarness` (sample-verify-delete + VAM)

`pipeline/recipe_harness.py:135-194` drives one dealer through:

```
EXTRACT SAMPLE (k≈3-5)  ->  VERIFY (VAM)  ->  BUILD recipe  ->  PERSIST YAML  ->  DELETE sample
                                  ^  if VERIFY refutes -> mark FAILED w/ reason  ^
```

Doctrine, all enforced in code (`recipe_harness.py:10-21`):

- **recipe-first** — the YAML config is the durable asset (`write_recipe`,
  step 4, `recipe_harness.py:177-184`).
- **sample-verify-DELETE** — only `k` cars are pulled; the sample lives only in
  memory and the reference is dropped at step 5
  (`recipe_harness.py:186-189`) — the harness never writes raw to disk, so there
  is nothing to leak.
- **VAM** — verification reuses `record_count_verdict` with
  `subject_type="recipe_sample"` (`recipe_harness.py:156-161`), the same gate as
  §3.2.
- **no silent failure** — `decide_status` returns `(VERIFIED|FAILED, reason)`:
  FAILED on empty sample, on **any** parse loss (`fetched != parsed`), on
  under-target, or on VAM REFUTED (`recipe_harness.py:94-117`).

The VAM evidence paths are built by `sample_paths` (`recipe_harness.py:80-91`):
always `fetched` (http family) vs `parsed` (db family); `source_declared` is added
**only** when the sample is the *full dealer* (`declared <= k`) — including it on a
deliberate subset would force a false REFUTED.

Run the harness for one dealer (writes the YAML + seals a verdict if a conn is
given):

```bash
python -m pipeline.recipe_harness <source> <dealer_ref> [k]
# e.g.
python -m pipeline.recipe_harness autoscout24 <dealer-slug> 5
```

Output (`recipe_harness.py:277-281`): `declared / fetched / parsed`, `VAM=<verdict>`,
`status=<VERIFIED|FAILED> reason=...`, and the persisted `recipe=` path under
`countries/ES/recipes/<cdp_code>.yaml`.

### 6.2 Write an `Extractor` (the only thing a new source must implement)

The harness is source-agnostic; a new source implements the tiny `Extractor`
protocol (`recipe_harness.py:65-74`): `source: str`, `recipe_template(dealer_ref)
-> Recipe` (a DRAFT recipe, transport/pagination/parsing pre-filled, evidence
empty), and `sample(dealer_ref, k) -> Sample`.

The reference extractors are in `pipeline/recipe_extractors.py`. Study
`AutoScout24Extractor` (`recipe_extractors.py:37-92`) — it **reuses** the already
verified `pipeline.sources.autoscout24` module (the extractor is *glue, not a
second scraper*, `recipe_extractors.py:1-7`). Its `sample()` pulls a bounded
`k`-slice from page 1, parses with the source module's own `parse_listing_vehicle`,
and sets `full_dealer = declared is not None and declared <= fetched`
(`recipe_extractors.py:76-92`). `CochesComExtractor` / `CochesNetExtractor` /
`AutocasionExtractor` follow the same pattern over open Tier-0 surfaces.

For an *arbitrary dealer website* (no known marketplace), reuse
`GenericWebExtractor` (`pipeline/recipe_extract_web.py:117-165`): it discovers the
stock page and pulls schema.org JSON-LD / microdata vehicles — the §4 cost-0 rung.
Sites with no vehicle JSON-LD yield an empty sample → recipe FAILED with a precise
reason (the honest outcome, never a fake success, `recipe_extract_web.py:1-12`).

Register your extractor in the `EXTRACTORS` map (`recipe_extractors.py:280-286`):

```python
EXTRACTORS = {
    "autoscout24": AutoScout24Extractor,
    "web_generic": GenericWebExtractor,
    "coches_com": CochesComExtractor,
    "coches_net": CochesNetExtractor,
    "autocasion": AutocasionExtractor,
    "your_source": YourSourceExtractor,   # <-- add here
}
```

### 6.3 THE HONEST GAP — only 5 of 47 connectors use the harness

This is real and must be documented to any replication team:

- `EXTRACTORS` has exactly **5 entries** (`recipe_extractors.py:280-286`):
  `autoscout24`, `web_generic`, `coches_com`, `coches_net`, `autocasion`.
- There are **47 platform connectors** (`pipeline/platform/*.py`).

So the recipe-harness cycle is wired for **~5/47** of the harvest surface. The
master plan names the executable recipe harness as the **highest-ROI gap**
(`docs/MASTER_PLAN_CARDEEP_2026-06-20.md:32, 493-531`): historically the real order
was *scrape → ingest → recipe POST-HOC*, and **no loader ever replayed a recipe**
(`recipe_harness.py:5-8`). The harness inverts that into the mandated
recipe-first/sample-verify-delete cycle, but only for the extractors above.

The **honesty clause is in `RecipeRunner`** (`recipe_harness.py:220-256`): it
replays a recipe *solely* from its YAML, but explicitly does **NOT** claim a
fully field-map-driven interpreter — the extractor still owns the parse code
(`recipe_harness.py:228-232`). What is *proven* is that the YAML carries enough to
relocate the source and reproduce the sample with no retained crude.

> **Target pattern for replication:** every new SCRAPE connector should also ship
> an `Extractor` registered in `EXTRACTORS`, so its recipe is harness-verified
> (sample-verify-delete + VAM) and replayable — not left in the post-hoc majority.
> Closing the 5/47 gap is the explicit direction of travel; do not add to the
> 42-connector backlog without a documented reason.

---

## 7. End-to-end checklist (verifiable criteria)

DISCOVER source:

- [ ] `pipeline/sources/<src>.py` implements `SourceAdapter`: `source_key`,
      `declared_count()`, `fetch()` (cached load; honest `excluded_count`).
- [ ] Identity dedup verified — re-seen dealers collapse on `ON CONFLICT
      (cdp_code)` (no `website=<shared portal>`).
- [ ] Imported + added to `ADAPTERS` (`discover.py:48-74`).
- [ ] `python -m pipeline.discover <key>` runs; VAM verdict is **TRUSTWORTHY**
      (or documented UNVERIFIED).
- [ ] (Recurrent) added to `DISCOVERY_REGISTRY` + `--seed` run
      (`discover_schedule.py`).

SCRAPE connector:

- [ ] `pipeline/platform/<name>_wholesale.py` declares `*_SOURCE_KEY`, has an
      `argparse main()`, writes `record_run` on every path, honors the breaker.
- [ ] `SourceEntry` added to `_build_registry()` with `source_key ==
      *_SOURCE_KEY` (`scheduler.py:131-291`).
- [ ] `source_health` cadence row seeded (interval per tier).
- [ ] `python scripts/validate_connectors.py <name>` passes at minimal scope (€0).
- [ ] `python -m pipeline.ops.scheduler --dry-run` shows it `WOULD RUN` with the
      right cmd, **not** UNMAPPED.

RECIPE:

- [ ] (Target) `Extractor` written + registered in `EXTRACTORS`
      (`recipe_extractors.py:280-286`).
- [ ] `python -m pipeline.recipe_harness <source> <dealer_ref>` → `status=VERIFIED`,
      YAML under `countries/ES/recipes/`, zero raw sample on disk.

---

## 8. Rollback / safety

Everything here is **additive and reversible**:

- A new adapter/connector module is an untracked file — delete it to revert.
- Removing the `ADAPTERS` / `REGISTRY` / `EXTRACTORS` entry de-registers it; no
  schema change.
- A seeded `source_health` row is a single row; delete it to unschedule:
  ```sql
  DELETE FROM source_health WHERE source_key = 'your_source_wholesale';
  ```
- The scheduler is **single-producer** behind a host advisory lock
  (`scheduler.py:826-837`) — starting a second instance fails fast, it never
  doubles the request rate.
- `--dry-run` / `--check-silence` (harvest) and `--dry-run` / `--seed` (discovery)
  are **read-only / €0** — use them freely to verify before going live.
- The DISCOVER pipeline is idempotent (`ON CONFLICT (cdp_code) DO UPDATE SET
  last_seen = now()`, `discover.py:99-114`) — re-running a source never
  duplicates entities.

There is **no migration to roll back** for adding a same-country source. (FASE 0's
`migrations/0052_country.sql` is already applied and additive; its own rollback
block is at `0052_country.sql:83-91`, but you do not touch it to add a source.)

---

## 9. Live verification queries (asyncpg heredoc — `psql` not on PATH)

```bash
cd /c/Users/elias/projects/cardeep && python - <<'PY'
import asyncio, asyncpg
DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
async def main():
    c = await asyncpg.connect(DSN)
    print("entity_total        :", await c.fetchval("SELECT count(*) FROM entity"))
    print("entity_active       :", await c.fetchval("SELECT count(*) FROM entity WHERE status='active'"))
    print("entity_country_ES   :", await c.fetchval("SELECT count(*) FROM entity WHERE country_code='ES'"))
    print("source_health_rows  :", await c.fetchval("SELECT count(*) FROM source_health"))
    print("vehicle_total       :", await c.fetchval("SELECT count(*) FROM vehicle"))
    # is my source landing entities?
    print("my_source in_db     :", await c.fetchval(
        "SELECT count(*) FROM entity_source WHERE source_key=$1", "your_source"))
    # latest VAM verdict for my source
    r = await c.fetchrow(
        "SELECT verdict, primary_value, evidence FROM verification_verdict "
        "WHERE subject_type='source' AND subject_key=$1 AND superseded_by IS NULL "
        "ORDER BY id DESC LIMIT 1", "your_source")
    print("my_source verdict   :", dict(r) if r else None)
    await c.close()
asyncio.run(main())
PY
```

**Live baseline verified 2026-06-23 (authoritative — supersedes any drifted doc;
the audit flagged SYSTEM-A-Z claiming 419k):**

| Metric | Live value |
|---|---|
| `entity` total | **431,212** |
| `entity` active (`status='active'`) | **419,890** |
| `entity` non-`particular` kinds | **91,412** |
| `entity` `country_code='ES'` | **431,212** (100%) |
| `source_health` rows | **56** |
| `vehicle` total | **2,312,292** |
| `vehicle_event` total | **2,613,135** |
| `verification_verdict` total | **1,346** |
| distinct `entity_source.source_key` | **88** |
| platform connector modules | **47** (`pipeline/platform/*.py`) |
| recipe-harness `EXTRACTORS` | **5** (`recipe_extractors.py:280-286`) |

> The "active" count (419,890) is the number behind the ~419k figure seen
> elsewhere; the **total** entity count is 431,212. Cite the metric you mean.
