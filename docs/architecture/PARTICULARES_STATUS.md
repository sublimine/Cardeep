# PARTICULARES STATUS

> Live status of private-individual (`kind=particular`) caging across platform
> connectors. Privates are first-class inventory: a car a private sells IS supply
> a buyer can purchase, so it is caged and served exactly like a dealer's car, but
> kept on a DISTINCT `entity_kind='particular'` so professional inventory stays
> filterable from C2C. Model defined in `migrations/0017_particular_kind.sql`.

## Live rollup — verified against `cardeep-pg` (2026-06-12)

Verification path: direct `docker exec cardeep-pg psql` against the live DB,
cross-checked by a second query path (per-platform `entity_source` join).

| Platform | Model used | Particular entities | Private cars caged this run | Full-drain CLI |
|---|---|---|---|---|
| coches.net | claude-opus-4-8 | 53 | +10,639 (live owned: 10,643) | `python -m pipeline.platform.coches_net_wholesale --pages <N>` (drain: raise `--pages` well past default 5 until pages run dry; `--start-page` for efficient top-up) |
| milanuncios | claude-opus-4-8 | 331 | +371 | `python -m pipeline.platform.milanuncios_wholesale --provinces all --pages 100` (default `--provinces`=all 52, `--pages 100` per facet cell; each cell ends naturally on a short/empty page) |
| wallapop | claude-opus-4-8 | 1,442 | +1,489 | `python -m pipeline.platform.wallapop_wholesale --target <N>` (drain: raise `--target` past default 8000 — e.g. `--target 80000` — to re-harvest all per-seller privates and let `cleanup_legacy_buckets()` retire emptied legacy garaje buckets) |

`--provinces all` above is shorthand: omitting `--provinces` already defaults to all
52 INE provinces. Raise `--concurrency` only as far as the JSON_API governor's
per-host bucket allows; it is the real limiter, not the flag.

## Grand totals (live)

| Metric | Value |
|---|---|
| `entity` (all kinds) | 28,801 |
| `entity` where `kind='particular'` | 1,826 |
| `vehicle` (grand total) | 363,722 |
| `vehicle` owned by `kind='particular'` entities | 12,503 (all `status='available'`) |
| `platform_listing` (grand total edges) | 324,489 |

Per-platform private-car ownership (reconciles to 12,503 = 10,643 + 371 + 1,489):
coches.net 10,643 · milanuncios 371 · wallapop 1,489.

Particular-entity provenance (via `entity_source`): coches_net_wholesale 53 ·
milanuncios_wholesale 331 · wallapop_wholesale 1,442 (= 1,826).

## Legacy garaje bucket cleanup — NOT yet complete (by design)

The wallapop connector upgraded from per-province garaje buckets
(`trade_name ILIKE 'Particulares wallapop%'`) to per-seller `kind=particular`
entities. `cleanup_legacy_buckets()` (`pipeline/platform/wallapop_wholesale.py:872`)
VAM-verifies a re-point FIRST (a bucket car is deletable only once its `deep_link`
is owned by a `kind=particular` entity), then DELETEs only superseded bucket
vehicles and any fully-emptied bucket entity (PG doctrine DELETE+INSERT, CASCADE).

Last run: 50 → 48 buckets (2 retired), 1,476 superseded bucket cars deleted.

**Live DB still holds 48 `Particulares wallapop%` garaje buckets containing 22,900
cars.** These are NOT orphaned data — they are private cars not yet re-harvested
into per-seller twins. They stay intact on purpose: deleting them before the
re-point would drop real available inventory and trip the VAM no-drop guard.
Completing the migration requires a FULL wallapop re-harvest
(`--target 80000`-class) so every legacy bucket car is re-pointed and its bucket
auto-retired. Until that full drain runs, the criterion "no legacy
`Particulares wallapop%` buckets remain" is NOT met.

No legacy particular/garaje bucket ever existed for coches.net or milanuncios in
this connector path (coches.net never had a particular bucket here; milanuncios is
per-seller from the start). The pre-existing coches.net per-province particular
buckets noted elsewhere come from a separate connector and were not touched here.
