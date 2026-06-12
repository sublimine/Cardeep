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
