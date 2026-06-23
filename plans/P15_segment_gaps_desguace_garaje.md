# P15 — Segment coverage gaps: DESGUACE inventory + garaje `sells_cars`

> **Scope.** Two concrete segment-coverage gaps, scoped codegen/plan-only (no heavy runs).
> All counts below are **[VERIFIED]** against live DB `cardeep-pg` (`:5433`, db `cardeep`)
> on 2026-06-22 via small aggregated queries, or read from repo source this session.
> Env: `CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep` ·
> `python = C:/Users/elias/AppData/Local/Programs/Python/Python311/python`.
>
> Ground truth read this session:
> - `docs/architecture/01-ENTITY-ONTOLOGY.md` §2.4 (garaje + `sells_cars` gate D-4),
>   §2.5 (desguace), §5 (inventory shapes), §6.5 (type-resolution precedence), §8 (residuals).
> - `pipeline/sources/dgt_cat.py` (DGT CAT discovery adapter — entities only, no inventory).
> - `pipeline/sources/borme_cnae.py` (the only desguace **classifier** keywords today).
> - `pipeline/platform/generic_dealer_site.py` (own-site harvester — **already** matches
>   `desguace|pieza|recambio` paths; kind-agnostic `(entity_ulid, website)` API).
> - `scripts/probe_dealer_sites.py`, `scripts/run_generic_dealer_e2e.py` (probe + e2e runner).
> - `migrations/0005_types_and_guards.sql` (`kind_source` enum), `0006_entity_evolve.sql`
>   (`sells_cars BOOLEAN`), `0043_province_seal_desguace.sql` (desguace seal = DISCOVERY only).

---

## 0. Live numbers (the two gaps, measured)

```
entity by kind (2026-06-22):
  particular              339,800
  compraventa              66,536
  garaje                    7,899   <-- gap B
  desguace                  2,700   <-- gap A
  concesionario_oficial     2,177
  subasta                     177
  plataforma                   18
  oem_vo_portal                14
  importador                   11
  rent_a_car_vo                 6
  cadena                        4

desguace vehicles owned (JOIN vehicle ON entity kind='desguace') = 0     [VERIFIED]
desguace with own website (non-null)                            = 542   [VERIFIED]
desguace by discovery source_key: dgt_cat 1292 · paginas_amarillas 729
  · aedra 581 · overture 250 · dork_municipal 112 · geo_sweep 7 · borme_cnae 5

garaje sells_cars:  NULL 7,874 · FALSE 19 · TRUE 6                       [VERIFIED]
garaje signal availability: website 1,031 · owns >=1 available vehicle 55
  · sale-keyword in name 20 · as platform 0                             [VERIFIED]
garaje sells_cars set rows: FALSE×19 (kind_source=platform_label) ·
  TRUE×6 (kind_source=manual)                                           [VERIFIED]
```

---

# GAP A — DESGUACE inventory = 0 vehicles (despite 2,700 entities)

## A.1 Root cause (verified, three layers)

1. **By-design v1 boundary, partially.** `01-ENTITY-ONTOLOGY.md` §2.5 / §5 / §8.2:
   a desguace has **two** stocks — *parts* (primary, high-volume) and *whole salvage/used
   vehicles* (secondary). The doc states: **"the car inventory (whole vehicles) is the v1
   target; parts inventory is a documented v2 extension, not v1 scope."** So **parts = v2
   (correctly deferred); whole-car salvage = v1 target that was never wired.**

2. **The seal masks it.** `migrations/0043_province_seal_desguace.sql` defines the desguace
   segment seal as **DISCOVERY coverage only** ("scrapyards (CATs) have no schema.org
   inventory, so the seal is *did we find at least the official DGT census?*"). numerator =
   desguaces found, denominator = `dgt_cat` subset. With that definition the segment reads
   `SELLADO` at 0 vehicles — inventory is **structurally invisible to the seal**, so nothing
   ever flagged the 0.

3. **No harvester is pointed at desguaces.** `dgt_cat.py` emits `DiscoveredEntity` only
   (no vehicles). The generic own-site harvester `generic_dealer_site.py` **already supports
   the desguace path patterns** (`_VEHICLE_PATH_RE` line 49-57 includes
   `desguace|pieza|recambio|ocasion`) and its `(entity_ulid, website)` API is kind-agnostic —
   but the only lead selector that feeds it, `scripts/probe_dealer_sites.py`, filters
   `WHERE first_discovered_source LIKE '%overture%' AND kind IN (...,'desguace',...)`
   (line 71-74). Only **250** desguaces came from overture; the other ~292 desguaces-with-
   websites (dgt_cat / paginas_amarillas / aedra) were **never probed for inventory**.

**Verdict:** the engine exists; the wiring + a desguace-shaped lead selector + an honest
seal extension do not. This is a **wiring/plan gap, not a missing-engine gap.**

## A.2 Does a desguace inventory harvester exist? — Inventory of connectors/sources

| Component | desguace handling today | Reusable for whole-car inventory? |
|---|---|---|
| `pipeline/sources/dgt_cat.py` | DGT CAT discovery (1,292 entities) — **entities only** | No (discovery, not inventory) |
| `pipeline/sources/borme_cnae.py` | `_classify()` maps `desguace`/`descontaminaci` → kind | No (registral discovery/typing) |
| `pipeline/sources/dork_municipal.py`, `associations.py` | desguace discovery (aedra etc.) | No (discovery) |
| `pipeline/platform/generic_dealer_site.py` | `_VEHICLE_PATH_RE` already includes `desguace\|pieza\|recambio\|ocasion`; `probe_single()` + `harvest_dealer_site(entity_ulid, website)` are **kind-agnostic** | **YES — this is the harvest engine to reuse** |
| `scripts/probe_dealer_sites.py` | filters `overture`-only leads; includes `desguace` in kind set | Partially — needs a desguace lead selector |
| `scripts/run_generic_dealer_e2e.py` | harvests `SCHEMA_ORG` probes, ingests, VAM | **YES — reuse as the ingest/VAM driver** |
| `migrations/0043_province_seal_desguace.sql` | desguace seal = discovery-only | Needs an inventory-shape extension (A.5) |

**Conclusion: no desguace *inventory* harvester exists, but it must NOT be built from scratch.**
The own-site harvester + e2e runner already do the work; the missing piece is a **desguace
lead selector** + an honest **two-shape seal** so the 0-inventory province does not read
SELLADO on inventory it never had.

## A.3 Two real desguace sites with scrapeable stock (live curl evidence, 2026-06-22)

Live small curls (1 page each, redirect-followed):
- `https://makrodesguaces.es` → 301→`https://www.makrodesguaces.es/` HTTP 200, 255 KB, Joomla
  CMS; robots.txt present (Joomla disallows). Parts-dominant.
- `https://tudesguace.com` → 301→`https://www.tudesguace.com/` HTTP 200, 60 KB.
- `https://desguaceselrubio.com` → HTTP 202 (bot-challenge shape, 1.5 KB).

**[VERIFIED] finding from the live probes:** the *individual* desguace long-tail is
**parts-dominant** — whole-car ("vehículo para circular / siniestrado completo") listings are
sparse on these sites, exactly as the ontology predicts ("whole-car: low"). The scrapeable
**whole-car salvage** supply concentrates on a few **specialist surfaces** (the ontology names
the parts ecosystem Opisto/Ovoko/RecOpart as parts=v2; the whole-car analogues are the salvage/
auction operators already modeled as `subasta`, e.g. Autorola salvage lots — `subasta` overlay,
not desguace). So the **realistic v1 desguace inventory** = the *minority* of CAT desguaces that
publish whole-car stock on their **own site** in schema.org form.

> **No-maquillaje note:** I did NOT find a dense, free, schema.org whole-car feed across the
> desguace long-tail in these probes. The honest v1 expectation is **low** whole-car yield
> (tens–low-hundreds of cars across the 542 sited desguaces), not a coches.net-scale segment.
> The correct deliverable is therefore (a) a cheap probe to *measure* the real yield and
> (b) a seal that stays honest at low/zero yield — both below. Parts inventory stays v2.

## A.4 Plan A — reuse, don't rebuild (€0, light)

**Phase A1 — desguace lead selector (new tiny script, reuses existing engine).**
Mirror `probe_dealer_sites.py` but select **all** desguaces with own websites, regardless of
discovery source. Skeleton in §A.6 (`scripts/probe_desguace_sites.py`). Output:
`docs/recon/desguace_probe.json` (JSON-lines, same shape `run_generic_dealer_e2e.py` already
consumes). Bounded: `--sample N` (default 60), `--workers 6`.

**Phase A2 — measure yield (proof run, bounded).**
`python scripts/run_generic_dealer_e2e.py --probe docs/recon/desguace_probe.json --limit 30`.
This already harvests `SCHEMA_ORG` leads, ingests via `ingest_generic_dealer_vehicles`, and
prints a VAM verdict per entity. No new ingest code. Records the true whole-car yield.

**Phase A3 — honest seal extension (migration).** Extend `v_province_seal` desguace branch so
it reports **two numerators**: discovery (unchanged) AND an itemized **inventory** sub-row that
is `caused-zero` / `NUMERATOR-SEALED` per the ontology §2.5 inventory model, never silently
SELLADO. Skeleton in §A.7. This makes the 0→N transition observable.

**Phase A4 — parts = v2, declared.** Keep parts out of v1 (ontology §8.2). The seal carries a
`declared_gap{shape:'parts', cause:'v2-deferred'}` so the gap is itemized, never hidden.

**Acceptance criteria (A):**
- [ ] `scripts/probe_desguace_sites.py` selects **all** sited desguaces (not overture-only),
      writes `docs/recon/desguace_probe.json`.
- [ ] A bounded e2e run ingests ≥1 desguace's whole-car stock OR the probe report proves
      `SCHEMA_ORG=0` across the sample (honest "no free whole-car feed" verdict, recorded).
- [ ] `v_province_seal` desguace rows expose discovery vs inventory separately; 0 inventory
      reads as an **itemized declared state**, not SELLADO.
- [ ] Parts inventory remains a declared v2 gap (no fabrication).

## A.5 Why this is the right shape (not a coches.net-style segment recipe)

coches.net/coches.com gaps are *segment recipes on one platform*. The desguace gap is the
opposite: **one shape (own-site schema.org) across thousands of tiny entities**, already solved
by the generic harvester. Building a bespoke desguace connector would duplicate
`generic_dealer_site.py` and violate DRY. The only desguace-specific code is the **lead query**
and the **seal semantics** — everything else reuses the proven path.

## A.6 Skeleton — `scripts/probe_desguace_sites.py` (new file)

```python
"""P15-A — Probe desguace own-sites for whole-car (schema.org) inventory.

Mirrors scripts/probe_dealer_sites.py but selects EVERY desguace with an own-site
website (not just overture-discovered leads — the original probe's
`first_discovered_source LIKE '%overture%'` filter left ~292 sited desguaces
unprobed). Reuses pipeline.platform.generic_dealer_site.probe_single unchanged.

Whole-car ONLY (v1 scope per 01-ENTITY-ONTOLOGY §2.5/§8.2); parts inventory is v2.

Usage:
    python scripts/probe_desguace_sites.py [--sample 60] [--workers 6] \\
        [--out docs/recon/desguace_probe.json] \\
        [--dsn postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.platform.generic_dealer_site import probe_single  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Reuse the platform/OEM exclusion list from probe_dealer_sites by importing it,
# so a desguace whose only "website" is a directory/social page is skipped.
from scripts.probe_dealer_sites import _is_own_site  # noqa: E402

DEFAULT_DSN = os.environ.get(
    "CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
)


async def _fetch_desguace_leads(dsn: str, limit: int) -> list[dict]:
    conn = await asyncpg.connect(dsn=dsn)
    try:
        rows = await conn.fetch(
            """
            SELECT entity_ulid, legal_name, trade_name, website, kind, province_code
              FROM entity
             WHERE kind = 'desguace'
               AND website IS NOT NULL
               AND website <> ''
             ORDER BY province_code, entity_ulid
             LIMIT $1
            """,
            limit,
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


def _probe_one(lead: dict) -> dict:
    t0 = time.monotonic()
    probe = probe_single(lead["entity_ulid"], lead["website"])
    out = asdict(probe)
    out.update(
        legal_name=lead.get("legal_name"),
        trade_name=lead.get("trade_name"),
        kind=lead["kind"],
        province_code=lead.get("province_code"),
        wall_s=round(time.monotonic() - t0, 2),
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=60)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default="docs/recon/desguace_probe.json")
    ap.add_argument("--dsn", default=DEFAULT_DSN)
    args = ap.parse_args()

    leads = asyncio.run(_fetch_desguace_leads(args.dsn, args.sample))
    leads = [ld for ld in leads if _is_own_site(ld["website"])]
    logger.info("desguace own-site leads to probe: %d", len(leads))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    labels: dict[str, int] = {}
    with out_path.open("w", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(_probe_one, ld) for ld in leads]
            for fut in as_completed(futs):
                rec = fut.result()
                labels[rec["label"]] = labels.get(rec["label"], 0) + 1
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    logger.info("labels: %s", labels)
    logger.info("wrote %s", out_path)
    schema_org = labels.get("SCHEMA_ORG", 0)
    print(
        f"SCHEMA_ORG={schema_org} of {len(leads)} probed. "
        f"{'>=1 harvestable whole-car feed found.' if schema_org else 'No free whole-car feed in sample (honest zero).'}"
    )


if __name__ == "__main__":
    main()
```

## A.7 Skeleton — `migrations/00XX_province_seal_desguace_inventory.sql` (new migration)

```sql
-- 00XX_province_seal_desguace_inventory.sql — split the DESGUACE seal into DISCOVERY +
-- INVENTORY sub-rows so 0 whole-car inventory reads as an itemized declared state, NOT
-- silently SELLADO. Read-only view change; fully reversible (rollback restores 0043).
--
-- 0043 sealed desguace on DISCOVERY only (found >= DGT census). That branch is preserved
-- verbatim under segment='desguace'. This adds segment='desguace_inventory':
--   numerator   = desguaces with >=1 whole-car vehicle (status='available')
--   denominator = desguaces found (discovery numerator)
--   verdict     = NO_INVENTORY when numerator=0 (the honest v1 state, NOT 'SELLADO'),
--                 PARCIAL 1-84%, SELLADO >=85% — never reports covered inventory that
--                 does not exist. Parts inventory stays a declared v2 gap (not modeled here).

CREATE OR REPLACE VIEW v_province_seal AS
WITH venta_num AS (
    SELECT e.province_code,
           count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
      FROM entity e
      LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
     WHERE e.kind IN ('compraventa', 'concesionario_oficial')
       AND e.province_code IS NOT NULL
       AND EXISTS (SELECT 1 FROM vehicle v
                    WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
     GROUP BY e.province_code
),
desg AS (
    SELECT e.province_code,
           count(DISTINCT e.entity_ulid)                                          AS numerator,
           count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key = 'dgt_cat')  AS denominator,
           count(DISTINCT e.entity_ulid) FILTER (
               WHERE EXISTS (SELECT 1 FROM vehicle v
                              WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
           )                                                                       AS inv_numerator
      FROM entity e
      LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
     WHERE e.kind = 'desguace' AND e.province_code IS NOT NULL
     GROUP BY e.province_code
)
-- VENTA — byte-identical to 0042/0043
SELECT d.province_code,
       'venta'::text                                   AS segment,
       d.point_est                                     AS denominator,
       COALESCE(n.numerator, 0)                        AS numerator,
       round((100.0 * COALESCE(n.numerator, 0) / NULLIF(d.point_est, 0))::numeric, 1)
                                                       AS coverage_pct,
       CASE
         WHEN d.point_est IS NULL OR d.point_est = 0 THEN 'NO_DENOM'
         WHEN 100.0 * COALESCE(n.numerator, 0) / d.point_est >= 85 THEN 'SELLADO'
         WHEN 100.0 * COALESCE(n.numerator, 0) / d.point_est >= 50 THEN 'PARCIAL'
         ELSE 'GAP'
       END                                             AS verdict
  FROM denominator_estimate d
  LEFT JOIN venta_num n ON n.province_code = d.province_code
 WHERE d.segment = 'venta'
UNION ALL
-- DESGUACE (discovery) — byte-identical to 0043
SELECT dg.province_code,
       'desguace'::text                                AS segment,
       dg.denominator,
       dg.numerator,
       round((100.0 * dg.numerator / NULLIF(dg.denominator, 0))::numeric, 1)
                                                       AS coverage_pct,
       CASE
         WHEN dg.denominator IS NULL OR dg.denominator = 0 THEN 'NO_DENOM'
         WHEN dg.numerator >= dg.denominator THEN 'SELLADO'
         ELSE 'GAP'
       END                                             AS verdict
  FROM desg dg
UNION ALL
-- DESGUACE (whole-car inventory) — NEW honest sub-seal; 0 reads as NO_INVENTORY
SELECT dg.province_code,
       'desguace_inventory'::text                      AS segment,
       dg.numerator                                    AS denominator,  -- desguaces found
       dg.inv_numerator                                AS numerator,    -- desguaces with stock
       round((100.0 * dg.inv_numerator / NULLIF(dg.numerator, 0))::numeric, 1)
                                                       AS coverage_pct,
       CASE
         WHEN dg.numerator IS NULL OR dg.numerator = 0 THEN 'NO_DENOM'
         WHEN dg.inv_numerator = 0 THEN 'NO_INVENTORY'   -- honest v1 zero, never SELLADO
         WHEN 100.0 * dg.inv_numerator / dg.numerator >= 85 THEN 'SELLADO'
         WHEN 100.0 * dg.inv_numerator / dg.numerator >= 50 THEN 'PARCIAL'
         ELSE 'GAP'
       END                                             AS verdict
  FROM desg dg;

-- Rollback: restore the 0043 two-segment view (venta + desguace discovery), drop the
-- desguace_inventory branch. (Copy the CREATE OR REPLACE VIEW body from 0043.)
```

> **Verify-before-merge:** confirm `denominator_estimate`, `v_dealer_resolved`, and
> `vehicle.status='available'` semantics are unchanged vs 0043 (this skeleton assumes the
> 0042/0043 venta branch verbatim — diff it against the live 0043 before applying).

---

# GAP B — garaje `sells_cars` unresolved (7,874 of 7,899 NULL)

## B.1 Root cause (verified)

`01-ENTITY-ONTOLOGY.md` §2.4 / D-4: `garaje` = workshop that **also sells** cars. The
denominator must be gated by `entity.sells_cars` so ~30k pure talleres (OSM/PA/CCAA
over-collection) don't inflate it. The column exists (`migrations/0006`,
`sells_cars BOOLEAN DEFAULT NULL`) **but no code path writes it** — confirmed: grep
`sells_cars` across `pipeline/` finds it only as a passthrough in
`platform/_core/{contract,persistence,sql}.py` (set by platform connectors that already
*know* the seller is a dealer) and in `migrations`. **There is no classifier/heuristic job
that resolves the garaje NULLs.** Result: 7,874 NULL — neither counted in nor excluded from
the served denominator deterministically.

The ontology §6.5 prescribes the resolution rung: **"5. local-LLM classifier over listing
text → importador / garaje-sells / compraventa"**, with `kind_source='classifier'`. The
`kind_source` enum (`migrations/0005`) already includes `classifier` and `legal_census`.

## B.2 Signal availability (measured — what a €0 heuristic can use)

```
garaje total 7,899 · website 1,031 · owns >=1 available vehicle 55
  · sale-keyword in name 20 · as platform 0
Already-set: FALSE×19 (kind_source=platform_label) · TRUE×6 (kind_source=manual)
```

Three **free, deterministic** signals are available without any LLM call or paid service:

| Tier | Signal | Verdict | `kind_source` | Confidence |
|---|---|---|---|---|
| **H1 hard-positive** | entity owns ≥1 `vehicle` with `status='available'` | `sells_cars=TRUE` | `classifier` | highest — it is *literally* selling a car we ingested |
| **H2 hard-positive** | has ≥1 `platform_listing` edge as a seller | `sells_cars=TRUE` | `classifier` | high |
| **H3 name-keyword** | `trade_name`/`legal_name` matches `compraventa\|compra-venta\|venta de\|ocasi[oó]n\|seminuevo\|vehiculos\|autom[oó]viles` | `sells_cars=TRUE` (weak) | `classifier` | medium |
| **H4 site sale-signal** | own-site homepage/sitemap contains a vehicle PDP (reuse `generic_dealer_site.probe_single` → label ∈ {SCHEMA_ORG, SITEMAP_SOLO}) | `sells_cars=TRUE` | `classifier` | medium-high |
| **H5 negative** | website is dead/pure-taller AND no vehicle AND no listing AND no keyword AND probe label ∈ {SIN_SITEMAP, MUERTO} | leave **NULL** (unknown), do **not** force FALSE | — | — |

> **Discipline (no maquillaje):** H5 deliberately leaves NULL, not FALSE. Forcing FALSE on
> "no signal found" would fabricate a negative; the ontology §2.4 wants the gate *populated
> where determinable*, and `sells_cars IS NOT FALSE` (the `idx_entity_sells` partial index,
> `migrations/0006` line 59) already treats NULL conservatively as "maybe-sells". Only a
> *positive* signal flips to TRUE; a *verified* pure-taller (future registral CNAE-4520-only
> match) flips to FALSE — that is rung-1 registral, out of this €0 heuristic's reach.

## B.3 Plan B — €0 deterministic resolver (no LLM needed for the bulk)

The owner mandate is **€0**. The ontology's "local-LLM classifier" (rung 5) is the *ceiling*;
the **floor** that resolves the bulk for free is H1+H2 (DB-only, zero fetch):
the 55 garajes that already own available vehicles are **immediately** `sells_cars=TRUE`
with `kind_source='classifier'` — pure SQL, no network. H3 (name keyword) adds ~20 more.
H4 (site probe) is an optional bounded pass over the 1,031 sited garajes reusing the existing
probe engine. Local-LLM (rung 5, T08-local-llm) is the **last** resort for the ambiguous
residual, only if a local model is available at €0 — never a paid API.

**Phase B1 — DB-only resolver (instant, no fetch).** New module
`pipeline/identity/resolve_sells_cars.py` (skeleton §B.5): one UPDATE for H1/H2 (owns
vehicle / has listing → TRUE), one UPDATE for H3 (name keyword → TRUE). Idempotent: only
touches `sells_cars IS NULL` rows, stamps `kind_source='classifier'`. **This alone resolves
the 55 hard-positives + ~20 keyword rows deterministically, today, free.**

**Phase B2 — bounded site-probe pass (optional, reuses engine).** For sited garajes still
NULL, run `generic_dealer_site.probe_single` (already thread-pooled in
`probe_dealer_sites.py`); a non-MUERTO label with a vehicle PDP → TRUE. Bounded `--sample`.

**Phase B3 — local-LLM residual (only if a free local model exists).** Per
`docs/architecture/tooling/T08-local-llm.md`; classify ambiguous own-site text. Skipped if
no €0 local model — never falls back to a paid API. Honest: residual stays NULL.

**Acceptance criteria (B):**
- [ ] `pipeline/identity/resolve_sells_cars.py` exists, idempotent, touches only NULL rows,
      stamps `kind_source='classifier'`.
- [ ] After B1, the 55 vehicle-owning garajes + name-keyword garajes read `sells_cars=TRUE`
      (verifiable: `SELECT count(*) FROM entity WHERE kind='garaje' AND sells_cars=TRUE`).
- [ ] No NULL is forced to FALSE without a verified negative signal (no fabrication).
- [ ] Local-LLM path is gated on a €0 local model; absence → residual NULL, declared.

## B.4 Why heuristic-first, not LLM-first

The ontology names an LLM classifier, but **the strongest signal is already in our own DB**:
if we ingested an available `vehicle` for an entity, that entity *demonstrably sells cars* —
no text classification can beat that. Spending LLM tokens (even local) on the 55 obvious
cases would be waste. Heuristic-first (H1→H4) resolves every *determinable* row for €0;
the LLM is reserved for the genuinely ambiguous own-site-text residual, consistent with the
cost doctrine.

## B.5 Skeleton — `pipeline/identity/resolve_sells_cars.py` (new file)

```python
"""P15-B — Resolve entity.sells_cars for garaje entities, €0 deterministic-first.

Per 01-ENTITY-ONTOLOGY §2.4 (D-4) and §6.5 (rung 5 = classifier). The column exists
(migrations/0006) but no code populates the 7,874 NULL garaje rows. This resolver
fills only what is DETERMINABLE for free, in precedence order, and NEVER fabricates a
negative: NULL stays NULL unless a positive signal flips it TRUE (a verified pure-taller
FALSE is a rung-1 registral job, out of scope here).

Signals (cheapest first, all €0):
  H1  owns >=1 vehicle status='available'  -> TRUE  (DB-only, no fetch)
  H2  has >=1 platform_listing as seller   -> TRUE  (DB-only, no fetch)
  H3  sale keyword in trade/legal name     -> TRUE  (DB-only, weak but free)
  H4  own-site probe finds a vehicle PDP   -> TRUE  (bounded fetch, reuses probe_single)

All writes stamp kind_source='classifier' and touch ONLY sells_cars IS NULL rows
(idempotent, re-runnable). Run order: resolve_db_signals() first (free), then optionally
resolve_site_signals() (bounded fetch).

Usage:
    python -m pipeline.identity.resolve_sells_cars            # H1+H2+H3 (DB-only)
    python -m pipeline.identity.resolve_sells_cars --probe --sample 100   # + H4
"""
from __future__ import annotations

import argparse
import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# H3 — sale-intent keywords in the trading/legal name (Spanish). Conservative: each implies
# a car *sale* activity, not mere repair.
_NAME_SALE_RE = (
    r"compraventa|compra-venta|venta de veh|venta de coch|venta de autom"
    r"|ocasi[oó]n|seminuev|veh[ií]culos de|autom[oó]viles"
)


async def resolve_db_signals(conn: asyncpg.Connection) -> dict[str, int]:
    """H1+H2+H3 — pure SQL, zero network. Returns rows updated per signal."""
    out: dict[str, int] = {}

    # H1 — owns an available vehicle (the strongest possible signal).
    h1 = await conn.execute(
        """
        UPDATE entity e
           SET sells_cars = TRUE, kind_source = 'classifier'
         WHERE e.kind = 'garaje' AND e.sells_cars IS NULL
           AND EXISTS (SELECT 1 FROM vehicle v
                        WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
        """
    )
    out["H1_owns_vehicle"] = int(h1.split()[-1])

    # H2 — appears as a seller via a platform_listing edge.
    h2 = await conn.execute(
        """
        UPDATE entity e
           SET sells_cars = TRUE, kind_source = 'classifier'
         WHERE e.kind = 'garaje' AND e.sells_cars IS NULL
           AND EXISTS (SELECT 1 FROM platform_listing pl
                        WHERE pl.platform_entity_ulid = e.entity_ulid)
        """
    )
    out["H2_has_listing"] = int(h2.split()[-1])

    # H3 — sale keyword in the name (weakest free signal; still a positive intent marker).
    h3 = await conn.execute(
        """
        UPDATE entity e
           SET sells_cars = TRUE, kind_source = 'classifier'
         WHERE e.kind = 'garaje' AND e.sells_cars IS NULL
           AND lower(coalesce(e.trade_name,'') || ' ' || coalesce(e.legal_name,'')) ~ $1
        """,
        _NAME_SALE_RE,
    )
    out["H3_name_keyword"] = int(h3.split()[-1])
    return out


async def resolve_site_signals(conn: asyncpg.Connection, sample: int) -> dict[str, int]:
    """H4 — bounded own-site probe over still-NULL sited garajes. Reuses the proven
    generic_dealer_site.probe_single (thread-pooled by the caller in production)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from pipeline.platform.generic_dealer_site import probe_single

    rows = await conn.fetch(
        """
        SELECT entity_ulid, website FROM entity
         WHERE kind = 'garaje' AND sells_cars IS NULL
           AND website IS NOT NULL AND website <> ''
         ORDER BY province_code, entity_ulid
         LIMIT $1
        """,
        sample,
    )
    hits = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(probe_single, r["entity_ulid"], r["website"]): r for r in rows}
        for fut in as_completed(futs):
            probe = fut.result()
            if probe.label in ("SCHEMA_ORG", "SITEMAP_SOLO") and probe.vehicle_urls_found > 0:
                await conn.execute(
                    """
                    UPDATE entity SET sells_cars = TRUE, kind_source = 'classifier'
                     WHERE entity_ulid = $1 AND sells_cars IS NULL AND kind = 'garaje'
                    """,
                    futs[fut]["entity_ulid"],
                )
                hits += 1
    return {"H4_site_probe": hits, "H4_probed": len(rows)}


async def _main(probe: bool, sample: int) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        db = await resolve_db_signals(conn)
        print("DB-only (H1/H2/H3):", db)
        if probe:
            site = await resolve_site_signals(conn, sample)
            print("Site probe (H4):", site)
        remaining = await conn.fetchval(
            "SELECT count(*) FROM entity WHERE kind='garaje' AND sells_cars IS NULL"
        )
        print(f"garaje sells_cars still NULL (declared unknown): {remaining}")
    finally:
        await conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="also run H4 bounded site probe")
    ap.add_argument("--sample", type=int, default=100)
    args = ap.parse_args()
    asyncio.run(_main(args.probe, args.sample))


if __name__ == "__main__":
    main()
```

> **Verify-before-merge:** confirm `platform_listing.platform_entity_ulid` is the column a
> *seller* garaje would populate (per ontology §4 a garaje is a *selling entity*, its cars
> link to a platform via `platform_listing` whose `platform_entity_ulid` is the **platform**,
> not the seller). If garaje-as-seller is keyed elsewhere (e.g. `vehicle.entity_ulid` only),
> **H2 is redundant with H1 and should be dropped** — H1 already covers "we ingested its
> cars". Diff against `migrations/0009_platform_listing.sql` before applying. H1 + H3 are
> unconditionally correct; H2 is the one to validate.

---

## Summary — what to build (both gaps), all €0 and reuse-first

| Gap | New file (skeleton above) | Reuses | Heavy run? |
|---|---|---|---|
| A: desguace inventory | `scripts/probe_desguace_sites.py` + `migrations/00XX_province_seal_desguace_inventory.sql` | `generic_dealer_site.probe_single` / `harvest_dealer_site`, `run_generic_dealer_e2e.py` | No — bounded `--sample`/`--limit` proof runs only |
| B: garaje sells_cars | `pipeline/identity/resolve_sells_cars.py` | DB-only SQL + `generic_dealer_site.probe_single` (H4) | No — H1/H2/H3 are pure SQL; H4 bounded |

**Net new engine code = 0.** Both gaps are wiring + lead-selection + honest seal/flag
population over the existing harvest engine. Parts inventory (desguace) and registral
pure-taller FALSE (garaje) are **declared** v2/rung-1 gaps, not fabricated.
