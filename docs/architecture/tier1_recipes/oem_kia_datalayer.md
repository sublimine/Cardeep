# Kia Seminuevos Certificados ("Kia Okasión") — ES certified-used data-layer recipe

> OEM-VO portal. `source_group=oem_vo_portal`, `kind=oem_vo_portal`, `family=kia_vo`,
> `role=platform`, `defense_tier=t1_soft`, `is_tier1=FALSE`.
> Connector: `pipeline/platform/oem_kia_wholesale.py`. Verified live **2026-06-13**.

## TL;DR

- **Portal**: `www.kia.com/es` — *Kia Seminuevos Certificados* (the Kia Iberia certified-used
  programme, the "buscador" used-car finder). The manufacturer-owned certified-used portal for
  Kia in Spain — the OEM-VO sibling of toyota_lexus / spoticar / renew.
- **Real backend**: a third-party vendor app, **`kiaokasion.net`** ("Kia Okasión"), an
  ASP.NET / `Microsoft-IIS/10.0` application. The kia.com SPA buscador embeds it; the per-dealer
  page injects an inline `__kiaClienteId` (the cluster id) and calls the vendor servlet.
- **Stock API**: a single multiplexed async servlet, keyed by an `accion` form field:

  ```
  POST https://kiaokasion.net/kia/async/metodos.aspx
  Content-Type: application/x-www-form-urlencoded; charset=UTF-8
  X-Requested-With: XMLHttpRequest
  Origin: https://www.kia.com    Referer: https://www.kia.com/
  ```

  - `accion=actualizarCoches` → the car page (the harvest call).
  - `accion=actualizarTodoBuscador` → the facet aggregations (models/bodies/fuels/colours/...).
- **Access**: the bare IIS root (`/kia/`, `/`) **403s plain curl** (IIS request filtering), but the
  `metodos.aspx` POST serves **HTTP 200 `application/json`** to `curl_cffi impersonate=chrome131`
  with a kia.com `Referer`. No proxy, no browser, no cookie warm-up, no auth, €0. No tier-1 CDN WAF
  (no Cloudflare/Akamai) → `is_tier1=FALSE`; soft WAF present, no JS challenge → `defense_tier=t1_soft`.

## Request body (`actualizarCoches`)

```
accion=actualizarCoches
idconcesionario=<cluster>     # the catalog partition key (see below)
pagina=<N>                    # 1-based page; PAGE_SIZE = 10 (fixed)
km=nacional                   # national radius WITHIN a cluster (does NOT aggregate clusters)
orden=1
modelos=  carrocerias=  motores=  cambios=  combustibles=  colores=
kilometros=-  preciominimo=-  preciomaximo=-  anyminimo=-  anymaximo=-
longitud=  latitud=  kmsdistancia=
```

Response envelope:

```json
{ "vehiculos": [ {…car…} ], "num_pagina": 1, "top_paginacion": 4,
  "total_vehiculos": "31", "listado_actualizado": null }
```

## CATALOG PARTITION — the load-bearing structural fact

The vendor catalog is **partitioned by `idconcesionario`** — the kia.com inline `__kiaClienteId`,
which is a **dealer-GROUP CLUSTER id, NOT a single dealer**.

- `idconcesionario=0` → 0 cars. Only a **sparse set** of valid cluster ids carries stock.
- `km=nacional` only relaxes the geo radius **within** a cluster's own stock; it does **NOT**
  aggregate across clusters.
- **Full ES national stock = the UNION over every live cluster id.**
- Live clusters (swept exhaustively over `idconcesionario` 1..2000, **2026-06-13**):
  **55 live clusters, ids 331..1810, Σ total_vehiculos ≈ 1,525 cars.** 0 clusters above 2000,
  0 below 331. (Largest: cluster `926` = QUADIS ARmotors group ≈ 256 cars.)
- A cluster can span several physical sites/cities (e.g. `926` → Tarragona **and** Sant Boi,
  provinces 43 **and** 08). So the **selling dealer is taken PER CAR** from `concesionario` (name) +
  `poblacion` (city), **not** per cluster. The cluster id is the catalog partition + a dealer-identity
  disambiguator.

The connector **discovers the live clusters at runtime** (a one-shot `actualizarCoches?pagina=1`
probe per id over the sweep range; live ⇔ `total_vehiculos>0`), so a newly-onboarded dealer is
caught without a code change. The denominator is `Σ cluster total_vehiculos`.

## Enumeration

1. **Discover clusters**: sweep `idconcesionario` over [1..2000], keep ids with `total_vehiculos>0`.
2. **Drain each cluster**: walk `pagina=1..top_paginacion` (10 cars/page). Stop on the first empty
   `vehiculos[]` or `pagina>top_paginacion`.
3. **Dedup** globally on car `id` (the stable per-car key).

## Per-car field map (`vehiculos[]`)

| Field | Source | Notes |
|---|---|---|
| `listing_ref` / dedup key | `id` | vendor stable car id (clean) |
| `make` | `marca` | `KIA` |
| `model` | `modelo` | |
| `version` | `version` | |
| `year` | `any` (fallback `matriculacion[-4:]`) | |
| `km` | `kilometros` | Spanish-formatted: `13.373` = 13373 |
| `price` | `precio` (€); `precio_alcontado` = cash price | Spanish-formatted |
| `fuel` | `combustible` | |
| `transmission` | `transmision` | Manual / Automático |
| `photo` | `imagen` | absolute https, embeds `idcli_<cluster>` |
| `dealer name` | `concesionario` | latin-1 mojibake |
| `dealer city` | `poblacion` | → province via `GeoResolver.resolve_city_global` |
| `vin` | **none in list** | `matricula` (plate) only in the `actualizarFicha` detail → stored `null` |

**Geo**: the LIST carries **no postal code or lat/lng** — only `poblacion` (city). The province +
municipality are resolved from the city (`GeoResolver.resolve_city_global`; Kia's `poblacion`
values are unambiguous INE municipality names — **100% resolved** in the live probe, so **no ficha
fetch is needed**). The per-car `actualizarFicha?idcoche=<id>` detail does carry `cp`, `direccion`,
`telefono`, `emailconcesionario`, full equipment — available if ever needed, not used by the harvest.

**deep_link**: the vendor ficha is **SPA-only** (`iralaficha(id)` → `loadPageSPA('vdp')`, no
routable per-car URL). The connector mints a stable, traceable kia.com buscador URL keyed by the
globally-unique car id: `…/kia-seminuevos-certificados/buscador/?idcli=<cluster>&idcoche=<id>#<slug>`.

## Caveats

- **page_size**: fixed **10** cars/page; `top_paginacion` governs the page count per cluster.
- **encoding**: dealer/city/version text is **latin-1 mojibake** over the wire
  (`Automoci�n`→Automoción, `M�laga`→Málaga). Repair: `s.encode("latin-1").decode("utf-8")`.
  `id` and numeric fields are clean.
- **es_numbers**: km/price/dimensions are Spanish-formatted (`.` thousands separator) — strip dots.
- **no national aggregate**: `idconcesionario=0` → 0; `km=nacional` is radius-only within a cluster.
- **no private sellers**: OEM certified-used portal — every car belongs to an official Kia dealer.

## Dual membership (ONE architecture)

```
kia (the OEM-VO portal) -> entity kind='oem_vo_portal' (+ platform_meta)   [THE PLATFORM]
each SELLING DEALER      -> entity kind='compraventa' (city-geo-resolved, per car not per cluster)
each CAR                 -> vehicle OWNED BY its dealer (entity_ulid=dealer)
the car ON the portal    -> platform_listing edge (platform_entity <-> vehicle)
```

VAM count quorum (per slice, like-with-like): `db_edges == db_join_vehicles == harvested_cageable`.

## Run

```
python -m pipeline.platform.oem_kia_wholesale            # discover + drain all live clusters (full ES stock)
python -m pipeline.platform.oem_kia_wholesale --clusters 15      # bounded proof slice
python -m pipeline.platform.oem_kia_wholesale --limit 500        # ~target car count
```
