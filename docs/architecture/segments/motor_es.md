# motor.es — segment audit (read-only probes verified live, 2026-06-13)

> Probed with the project fetcher (`curl_cffi` `impersonate="chrome131"`, no proxy/browser),
> READ-ONLY (a handful of GETs) while the operator's FULL used-car drain runs on the host.
> Counts are motor.es's OWN on-page counters. VAM per segment = the on-page "N coches" /
> "N modelos" counter cross-checked against `get-data-ajax` `data.total` for the census.

## Segment breakdown (what the platform itself exposes)

| Segment | Surface | motor.es displayed count | Family | Relationship to census | Status |
|---|---|---|---|---|---|
| VO usados | `/segunda-mano/{make}/{model}/` | **50,932** (`get-data-ajax data.total`; landing title "50.769 coches disponibles") | facet (card → `/segunda-mano/anuncio/{id}/` PDP) | the census | ✅ already drained (original connector) |
| km0 / seminuevos | `/coches-km0/` | **5,594** ("Coches de Km 0 / 5.594 coches disponibles") | facet (SAME `anuncio` PDP namespace) | **SUBSET of VO** | ✅ covered by VO; selectable via `--segment km0` |
| VN ofertas | `/coches-nuevos/ofertas/` | **476** ("476 coches encontrados") | offer (`/{make}/{model}/` catalog page) | additive | ✅ NEW — `--segment vn` |
| VN catalog | `/coches-nuevos/` | **450** ("Más de 90 marcas y 450 modelos") | offer (configurator make×model×version) | additive (⊃ vn) | ✅ NEW — `--segment catalog` |
| renting | `/renting/` | **132** ("132 coches encontrados") | offer (catalog-shaped) | additive | ✅ NEW — `--segment renting` |

## Reconciliation to the site-displayed total

motor.es does **NOT** advertise a 230k-style inflated number. Its headline IS the used
census: the `/segunda-mano/` landing title shows **"50.769 coches disponibles"**, the live
gateway counter is `get-data-ajax data.total = 50,932`. **km0 is INSIDE that census, not
additive** — PROVEN live: the km0 car id `23564668` (EBRO S700, dealer `barcelona/m-ocasion`,
km 1749) appears in the VO facet `/segunda-mano/ebro/s700/`, and km0 PDPs are the SAME
`/segunda-mano/anuncio/{id}/` pages. `/segunda-mano/ebro/` total = 139, of which
`/coches-km0/ebro/` = 76 are km0 — a sub-filter, not separate stock.

Reconciled full sellable surface:

```
~50,932  individual used cars (VO — km0's ~5,594 already counted within)
+   476  new-car offers (VN ofertas)
+   132  renting offers
+   450  new-car catalog models (configurator; superset of the 476 offers)
-------
~51,540  additive sellable surface (VO + VN offers + renting)
~51,990  if the full 450-model new catalog is also caged (catalog ⊃ vn → ~26 net new beyond vn)
```

The site's own displayed inventory total is the **~50.9k used census**; the genuinely
uncovered additive inventory beyond it is the **new-car offers (~476)** and **renting (~132)**,
plus the **450-model new catalog** if the configurator is wanted.

## Two surface families, one cage contract

- **facet** (`vo`, `km0`): SSR `<article class="elemento-segunda-mano">` cards → base64
  `data-goto` → `/segunda-mano/anuncio/{id}/` PDP (JSON-LD `@type:Car` with
  `offers.seller.name` = the SELLING DEALER + `/concesionarios/{prov}/{slug}/`). Caged exactly
  as before: vehicle OWNED BY its dealer, `platform_listing` edge, delta, VAM. km0 reuses the
  ENTIRE existing card+PDP path — only the listing root differs (`/coches-km0/{make}/{model}/`).
- **offer** (`vn`, `catalog`, `renting`): `/{make}/{model}/` catalog pages carry `@type:Car` +
  `offers.price` but **NO** individual `data-id`, km, or selling concesionario. They are MODEL
  offers, not stock. Caged as **platform-owned catalog offers** (`vehicle.entity_ulid =
  platform_ulid`, `km = NULL`, `deep_link =` the offer url), so the same edge/delta/VAM/idempotency
  contract holds with zero schema change.

## CLI (the connector extension)

`pipeline/platform/motor_es_wholesale.py` now takes `--segment {all|vo|km0|vn|catalog|renting}`:

```bash
PY=C:/Users/elias/AppData/Local/Programs/Python/Python311/python
# Full additive union (vo used census + vn new offers + renting) — ONE command:
$PY -m pipeline.platform.motor_es_wholesale --segment all --full
# Single segments:
$PY -m pipeline.platform.motor_es_wholesale --segment vo --full        # used census (~50,932)
$PY -m pipeline.platform.motor_es_wholesale --segment km0 --full       # km0 subset (~5,594, ⊂ vo)
$PY -m pipeline.platform.motor_es_wholesale --segment vn --full        # new offers (~476)
$PY -m pipeline.platform.motor_es_wholesale --segment catalog --full   # full new catalog (~450)
$PY -m pipeline.platform.motor_es_wholesale --segment renting --full   # renting (~132)
```

`--segment all` = `vo + vn + renting` (the additive union); it deliberately SKIPS `km0`
(⊂ vo) and `catalog` (⊃ vn) to avoid re-draining the same cars. Request those explicitly.
Proof mode (default, no `--full`) bounds the run by `--max-cells` / `--limit`.

## Smoke proof (this session)

`--segment vn --max-cells 3 --concurrency 3 --rate 2.0`, run TWICE:
- run 1: 3 offer pages fetched, 1 had no Car/offer block (skipped honestly), **2 offers caged**
  (Citroën AMI €7,790, Mobilize Duo €9,798; km=NULL, platform-owned), **2 vehicles, 2
  platform_listing edges, 2 NEW delta events**. VAM **TRUSTWORTHY**, health **healthy**.
  motor.es db edge total 9257 → 9259.
- run 2 (idempotency): same 2 offers re-seen, **0 new cars, 0 new edges, 0 NEW events**, db
  total stays 9259. The cage contract holds exactly.

No full harvest was run (the operator's FULL VO drain is in flight on the host). The full
per-segment drain is the documented `--segment <seg> --full` command above.

## Probe notes / caveats

- `?precio_hasta=` / `?anio_desde=` query filters are ignored on every surface — partition is
  PATH-based only (carried over from the VO recipe).
- The new-car catalog landing only surfaces a featured subset of `/{make}/{model}/` links in
  static HTML; the full 450 lives behind the configurator's filtered views. The `vn` ofertas
  surface (~476, the enumerable individual-offer set) is the practical NEW drain; `catalog`
  enumerates whatever model links the catalog HTML exposes.
- Some offer model pages (e.g. `silence/s04`) lack a parseable `@type:Car` block and are
  skipped honestly (counted under `no_dealer_skipped`).
