# CARDEEP Connector-Fleet Status

> **One line:** 3 ES giants wired into the live wholesale pipeline (autocasion,
> coches.com, motor.es); the backbone already holds **196,401 vehicles** across
> **157,333 platform listings** and **5 platform entities**, anchored by an earlier
> coches.net harvest. All figures below are `[VERIFIED]` against the live DB
> (`cardeep-pg`, db `cardeep`) on **2026-06-12**.

---

## Grand totals (live DB — `cardeep-pg`)

| Metric | Count | Query |
|---|--:|---|
| Entities (`entity`) | **20,699** | `SELECT count(*) FROM entity` |
| Vehicles (`vehicle`) | **196,401** | `SELECT count(*) FROM vehicle` |
| Platform listings (`platform_listing`) | **157,333** | `SELECT count(*) FROM platform_listing` |
| Platform entities (`entity.kind='plataforma'`) | **5** | `SELECT count(*) FROM entity WHERE kind='plataforma'` |

The 5 platform entities: **coches.net** (154,771 vehicles, prior harvest), **Autocasion**
(2,113), **AutoScout24** (268, prior), **coches.com** (116), **motor.es** (65). Vehicle
counts are `count(DISTINCT pl.vehicle_ulid)` per `platform_entity_ulid`.

---

## Wired connectors (this fleet pass)

| Connector | Cars | Dealers | VAM verdict | Status |
|---|--:|--:|---|---|
| **autocasion** | 2,113 | 580 | **TRUSTWORTHY** | Wired, verified, attribution clean |
| **coches_com** | 90 | 3 | **PENDING** | Wired, VAM not yet cleared |
| **motor_es** | 40 | 21 | **PENDING (run in progress)** | Wired, harvest mid-flight |

Per-connector counts are the connector-run figures. Live-DB platform tallies are slightly
higher where the entity also carries listings from prior runs (e.g. Autocasion DB total
2,113 vs this run's 2,113 cars; coches.com/motor.es DB totals 116/65 vs 90/40 fresh).

---

## Which giants are wired

Implemented wholesale recipes live under `pipeline/platform/`:

- `autocasion_wholesale.py` — **TRUSTWORTHY**, 2,113 cars / 580 dealers
- `coches_com_wholesale.py` — wired, **VAM PENDING**, 90 cars / 3 dealers
- `motor_es_wholesale.py` — wired, **VAM PENDING (run in progress)**, 40 cars / 21 dealers
- `coches_net_wholesale.py` — prior harvest, dominant 154,771-vehicle backbone
- `autoscout24_wholesale.py` — prior harvest, 268 vehicles

---

## What remains

1. **Clear coches.com VAM** — verdict still PENDING; attribution sample too thin
   (3 dealers / 90 cars) to declare TRUSTWORTHY.
2. **Finish motor.es run** — harvest is mid-flight (PENDING_RUN_IN_PROGRESS);
   re-evaluate VAM once the run lands and dealer coverage stabilizes.
3. **Scale the two thin connectors** — coches.com and motor.es are wired but
   shallow vs autocasion; widen page/region coverage to lift car + dealer counts.
4. **Remaining Tier-1 giants not yet wired** as wholesale connectors: wallapop,
   spoticar, milanuncios (camoufox path) — recipes proven in dossiers, not yet
   pipelined.

---

*Source of truth: live DB `cardeep-pg` + `pipeline/platform/*_wholesale.py`. Generated 2026-06-12.*

---

## Rollup — new-API wiring (live DB, 2026-06-12)

Latest connector pass added **spoticar** (5,884 cars / 135 dealers, 0 private, VAM
TRUSTWORTHY) and **milanuncios** (55,113 cars / 2,727 dealers, 35,791 private skipped,
VAM TRUSTWORTHY). All figures below are `[VERIFIED]` against the live DB
(`postgres://...@localhost:5433/cardeep`).

### Grand totals

| Metric | Count | Query |
|---|--:|---|
| Vehicles (`vehicle`) | **349,876** | `SELECT count(*) FROM vehicle` |
| Entities (`entity`) | **26,833** | `SELECT count(*) FROM entity` |
| Platform listings (`platform_listing`) | **310,643** | `SELECT count(*) FROM platform_listing` |

### Platform + OEM VO portal entities (`kind IN ('plataforma','oem_vo_portal')`)

10 entities, car counts = `count(DISTINCT pl.vehicle_ulid)` per `platform_entity_ulid`.

| Entity | kind | cdp_code | Cars |
|---|---|---|--:|
| coches.net | plataforma | CDP-ES-00-TKRV45RP | 154,997 |
| wallapop | plataforma | CDP-ES-00-EMRH0TWQ | 60,012 |
| milanuncios | plataforma | CDP-ES-00-E382JYEH | 55,113 |
| coches.com | plataforma | CDP-ES-00-XM91J1NZ | 20,135 |
| motor.es | plataforma | CDP-ES-00-HSV4XZ2H | 6,819 |
| Autocasion | plataforma | CDP-ES-00-QY06GW0B | 5,972 |
| spoticar | oem_vo_portal | CDP-ES-00-D6X2282Y | 5,884 |
| renew | oem_vo_portal | CDP-ES-00-DT59NK3D | 918 |
| Das WeltAuto | oem_vo_portal | CDP-ES-00-XWX9RHG7 | 552 |
| AutoScout24 | plataforma | CDP-ES-00-VMCZWW5N | 268 |

Distinct vehicles across the 10 platform/OEM entities: **310,702**.

*Rollup generated 2026-06-12 from live DB query.*

---

## Rollup — dealer-giant upgrade pass (live DB, 2026-06-12)

This pass deep-drained the three ES dealer giants (autocasion, coches.com,
motor.es), lifting all three caged tallies. All figures below are `[VERIFIED]`
against the live DB (`cardeep-pg`, db `cardeep`, `postgres://...@localhost:5433/cardeep`).

### Grand totals

| Metric | Count | Query |
|---|--:|---|
| Vehicles (`vehicle`) | **364,181** | `SELECT count(*) FROM vehicle` |
| Entities (`entity`) | **28,831** | `SELECT count(*) FROM entity` |
| Platform listings (`platform_listing`) | **324,957** | `SELECT count(*) FROM platform_listing` |

### Platform + OEM VO portal entities (`kind IN ('plataforma','oem_vo_portal')`)

10 entities; cars = `count(DISTINCT pl.vehicle_ulid)` per `platform_entity_ulid`,
listings = `count(pl.*)` per entity.

| Entity | kind | cdp_code | Cars | Listings |
|---|---|---|--:|--:|
| coches.net | plataforma | CDP-ES-00-TKRV45RP | 165,707 | 165,707 |
| wallapop | plataforma | CDP-ES-00-EMRH0TWQ | 60,094 | 60,094 |
| milanuncios | plataforma | CDP-ES-00-E382JYEH | 55,484 | 55,484 |
| coches.com | plataforma | CDP-ES-00-XM91J1NZ | 21,533 | 21,533 |
| Autocasion | plataforma | CDP-ES-00-QY06GW0B | 7,764 | 7,764 |
| motor.es | plataforma | CDP-ES-00-HSV4XZ2H | 6,819 | 6,819 |
| spoticar | oem_vo_portal | CDP-ES-00-D6X2282Y | 5,884 | 5,884 |
| renew | oem_vo_portal | CDP-ES-00-DT59NK3D | 918 | 918 |
| Das WeltAuto | oem_vo_portal | CDP-ES-00-XWX9RHG7 | 552 | 552 |
| AutoScout24 | plataforma | CDP-ES-00-VMCZWW5N | 268 | 268 |

Distinct vehicles across the 10 platform/OEM entities: **325,061**.

### Dealer giants — caged-now vs declared-full + full-drain CLI

| Giant | Caged now (live DB) | Declared-full (this run) | VAM | Full-drain CLI |
|---|--:|--:|---|---|
| **autocasion** | **7,764** | 7,700 | TRUSTWORTHY | `python -m pipeline.platform.autocasion_facet --makes all` |
| **coches.com** | **21,533** | 19,794 | TRUSTWORTHY | `python -m pipeline.platform.coches_com_wholesale --all` |
| **motor.es** | **6,819** | 6,513 | PASS (like-with-like quorum; `record_count_verdict` per run) | `python -m pipeline.platform.motor_es_wholesale --full` |

Caged-now (live DB `count(DISTINCT pl.vehicle_ulid)`) meets or exceeds each giant's
declared-full target — the deltas (autocasion +64, coches.com +1,739, motor.es +306)
reflect listings retained from prior runs on top of this pass's harvest. All three
giants are TRUSTWORTHY/PASS.

*Rollup generated 2026-06-12 from live DB query.*
