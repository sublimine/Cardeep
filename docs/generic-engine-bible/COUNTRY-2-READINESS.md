# Country-#2 Readiness — el motor listo para "otra ejecución" · rama `feature/country-2-readiness`
> 2026-06-28. El censo servido ya es country-proof + sellado + VIVO en `:5433` (ver `COUNTRY-PROOF-BUILD.md`). Esto es la **fase 2**: enhebrar país por el spine discover→ingest→seal para que un 2º país (DE/FR/…) corra **automáticamente**, no solo no-corrompa. Default `country_code="ES"` en cada firma ⇒ **ES byte-idéntico**.

## INGENIERÍA — 18 ítems CERRADOS (TDD + gateados; verificados por mí)
Recon partió la deuda; el mint (`codes.py`) y la capa servida ya eran country-proof. Lo cerrado:
- **P0 · Spine de escritura** (`08de097`): `DiscoveredEntity.country_code` · `discover.py` (geo/cdp/INSERT por país) · `ingest.py` (gate de provincia country-scoped como `complete.py:171`, mint+INSERT por país) · `harvest_dealer.py --country` · `complete.py` recipe-path `country_of_cdp`. → un dealer DE se descubre/ingiere/mintea **como DE** (`CDP-DE-…`), ya no forzado a ES.
- **P1 · Sello/MSE** (`890df79`, mig `0065`): `discovery_capture.country_code` + `capture.py` filtra por país + `seal.compute` lee por país + carga denominador del país + `cli.py --country`. → estratos MSE y certificado **por país**, sin colapso ES/DE.
- **P2 · Producto/auditoría/identidad** (`d51c50a`, mig `0066`): `product_stats` por país (`/stats?country=`) · `canonical_key_backfill` `country_of_cdp` · `pipeline/identity/phone.py` (dispatch por país; ES→`phone_es` byte-idéntico, no-ES→E.164 anticolisión). → DE rellena su `canonical_key` y el teléfono sigue siendo hard-key de dedup.
- **P3 · Calidad** (`de840bc`): `splink_merge` (sufijos legales por país + filtro) · `detect.py` (baselines/cohortes por país) · `price_sanity` (banda por moneda) · `free_proxies` (egress por país) · `capture` DSN de `CARDEEP_DSN` · `load_geo --country`. (+ arregló un bug pre-existente `price_trap` `bigint>=text`.)

**Gate:** los 4 goldens país-#2 cableados al job `country-proof-invariant` → **29 goldens / `212 passed` / floor 207** (`:5434` dry-run). Migraciones aditivas `0065`-`0066`.

## DESPLIEGUE (cuándo y cómo — NO está en `:5433` aún, a propósito)
La rama está **probada, gateada y lista** pero **no desplegada a producción**: (1) sin valor para el censo ES-only de hoy (es prep para país-#2); (2) `0066` reestructura `product_stats` (single-row→por-país) y **NO es backward-compatible** con el handler `/stats` viejo en vivo → su despliegue exige **coordinación** (aplicar `0065`+`0066` a `:5433` **y** reiniciar la API con el código nuevo, en ventana). Se despliega **al onboardar el país #2**, junto con el pack operacional.

## OPERACIONAL — el pack que aporta el OWNER (NO es código; datos/infra/decisión de negocio)
El motor consume esto; no se puede inventar. Para `cover(DE)`:
- **OPS-A · Backbone geo DE** — `geo_province`/`geo_municipality`/`geo_comarca` para DE (Länder→Kreise→Gemeinden + centroides). Esquema listo (PK `(country_code,code)` 0053, códigos ensanchados 0059). Sin esto `GeoResolver.load('DE')` vuelve vacío y discover/ingest descartan DE.
- **OPS-B · Fuentes de descubrimiento DE + ≥2-3 listas ORTOGONALES** — registro tipo-DGT (KBA/Destatis-equiv), asociaciones DE (ZDK…), marketplaces DE, mapeadas a los buckets MSE (la maquinaria de buckets es country-agnóstica; faltan las fuentes reales).
- **OPS-C · Recetas de scraping DE** — `countries/DE/recipes/` (AS24 es pan-EU y ya sirve; la flota DE necesita recetas reales por plataforma/dealer).
- **OPS-D · Denominador/censo externo DE** — `countries/DE/census/…` (KBA/Destatis) para la triangulación + `COVERAGE_ANCHORS('DE',*)`. Sin esto el sello DE = `no_anchor`.
- **OPS-E · Flota de scheduler DE** — REGISTRY de fuentes DE + cadencias por país (el enhebrado de país en los jobs ya es ingeniería hecha).
- **OPS-F · Plan de numeración telefónica DE** — reglas E.164 nacionales (o cablear `phonenumbers` tras la firma `phone_match_key`, ya country-aware).
- **OPS-G · Gazetteer/aliases de localidades DE** — para resolución de cola larga (degradación, no bloqueante).

## ⇒ Estado
**Código: el motor está listo para correr un 2º país** (toda la country-blindness del spine cerrada, default ES byte-idéntico, gateado 212/212). **Onboardar DE de verdad = aportar el pack operacional (OPS-A…G) + el despliegue coordinado.** Eso es la frontera honesta de lo que el código solo puede terminar.
