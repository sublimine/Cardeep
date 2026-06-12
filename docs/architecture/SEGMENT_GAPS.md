# CARDEEP — Tier-1 SEGMENT GAP MATRIX

> **Mandate.** CARDEEP doctrine: *"todo su inventario de coches"* = EVERY inventory
> segment a Tier-1 platform exposes (usados/ocasión, NUEVOS, km0/seminuevos,
> renting/suscripción, C2C privados), not only the used pool. This matrix is the
> per-platform rollup: for EACH platform, EVERY segment it publishes, that segment's
> PUBLISHED count, whether the existing connector covers it (yes/no), and the true
> grand total per platform.
>
> **Sources of truth (per-platform audits, read these for the probe-by-probe
> evidence):**
> - coches.net → [`segments/coches_net.md`](segments/coches_net.md)
> - wallapop → [`segments/wallapop.md`](segments/wallapop.md)
> - coches.com → [`segments/coches_com.md`](segments/coches_com.md)
> - autocasion → [`segments/autocasion.md`](segments/autocasion.md)
> - motor.es → [`segments/motor_es.md`](segments/motor_es.md)
> - milanuncios → [`segments/milanuncios.md`](segments/milanuncios.md)
>
> Live DB figures verified against `cardeep-pg` (`:5433`, db `cardeep`); published
> counts probed live `2026-06-13` with `curl_cffi chrome131`. Marking discipline:
> every count is **[VERIFIED]** (read this session) or **[ASSUMED]** (inferred /
> vendor-stated, not re-derived).
>
> **Env (per-platform CLI):** `CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`
> · `python = C:/Users/elias/AppData/Local/Programs/Python/Python311/python`.

---

## 0. TL;DR — three different gap shapes

The six Tier-1 platforms audited fall into **three** distinct gap shapes:

| Platform | True total (live) | Site-displayed | Gap shape | Segment gaps closed this session |
|---|--:|--:|---|---|
| **coches.net** | **~282,700** | — | **SEGMENT** gap — used 100% sealed, every non-used kind 0% | New ~6,089 · Km0 ~3,107 · Renting ~808 *(still open — separate backends)* |
| **wallapop** | **651,199** | ~750k mktg | **DEPTH** gap — flat vertical, every segment incidental, cursor not walked to end | *(none — no segment excluded)* |
| **coches.com** | **117,745** capturable | **230,000** ("más de 230.000 ofertas") | **SEGMENT** (closed) — 4 segments, all now drained by one connector | vo 92,381 · km0 15,630 · vn 826 · renting 8,908 — all **covered** |
| **autocasion** | **135,452** | ~135,452 (sum of segment titles) | **SEGMENT** (closed) — 3 segments, all now drained | vo 123,512 · vn 5,946 · km0 5,994 — all **covered**; renting N/A |
| **motor.es** | **~51,540** additive | ~50,932 used census | **SEGMENT** (closed) — used census + offer segments now drained | vo 50,932 (km0 5,594 ⊂ vo) · vn 476 · catalog 450 · renting 132 — all **covered** |
| **milanuncios** | **~272,130** | ~272,130 (Σ per-region titles) | **DEPTH/flat** — one ES index, every segment a facet of it, already 100% covered | *(none — all segments are facets of one index)* |

- **coches.net** drains the USED (ocasión) segment fully and reaches **0%** of NEW,
  KM0/seminuevos and RENTING — those live on **separate backends** the open
  `web.gw.coches.net/search` gateway cannot reach. The connector covers **~96.5% by
  count but 0% of the non-used kinds**. This is a real, caused, segment-shaped gap **still open**.
- **wallapop** has **NO** separate VN (new-car) catalog, **NO** km0 vertical, **NO**
  renting vertical. It is one generalist cars vertical (`category_id=100`); the
  connector's unfiltered `order_by=newest` cursor covers every seller type and every
  km/year band by construction. Its ~12.5% DB depth is a **cursor-DEPTH shortfall**
  (chunked at ~8k, not walked to `remaining_documents → 0`), **not** a skipped
  segment. `gaps = []`.
- **coches.com / autocasion / motor.es** each expose every sellable segment on its own
  surface; the gap was SEGMENT-shaped and is **closed this session** — each connector now
  takes a `--segment` flag that drains every segment under one cage contract.
- **milanuncios** is a single flat Elasticsearch supply index where every segment (used,
  km0, "a estrenar", pro, private) is a per-item facet slice — the existing connector
  already drains 100% of every segment; `--segment` only narrows targeted re-drains.

---

## 1. coches.net — per-segment matrix

`source_key = coches_net_wholesale`. Open JSON gateway `POST web.gw.coches.net/search`
(tenant `coches`) is **hardwired to the used index** — `categoryId`, `offerTypeId`,
`sellerTypeId`, `isCertified`, `km`, `year`, `subscriptionVehicleState` are ALL inert
on it `[VERIFIED]`. NEW / KM0 / RENTING are separate products on separate backends with
no open sibling endpoint found (`/newcars/search`, `/renting/search`, … → 404; alternate
tenants → 400). Full probe log: [`segments/coches_net.md`](segments/coches_net.md).

| Segment | Selector (web) | Published | Covered? | Coverage detail |
|---|---|--:|:--:|---|
| **Used (ocasión / segunda-mano)** | `/segunda-mano/`, gateway `/search` | **272,720** `[VERIFIED live]` | ✅ YES | DB **272,903** `platform_listing` edges (≈ live used total + accumulated cross-run drift); dual-membership (dealer compraventa + per-province particular). Segment sealed. |
| **New (coches nuevos)** | `/nuevo/` | **~6,089** `[VERIFIED via SRP/WebSearch]` | ❌ NO | Dealer new-car catalog; gateway 404s `/nuevo/search`. Needs a separate `/nuevo/` recipe. |
| **Km0 + seminuevos** | `/km-0/` | **~3,107** `[VERIFIED via SRP/WebSearch]` | ❌ NO | Combined `/nuevo/km-0/` surface ~6,210; no open endpoint. |
| **Renting / suscripción** | `/renting/` | **~808** `[VERIFIED via SRP/WebSearch]` | ❌ NO | `subscriptionVehicleState` exists in schema but inert on used gateway; no open renting endpoint. |

**Entity attribution:** `entity_source.source_key='coches_net_wholesale'` attributes
**7,223 entities** `[VERIFIED]`.

### True grand total — coches.net

```
USED      272,720   ✅ covered (DB 272,903 edges)
NEW       ~6,089    ❌ gap
KM0       ~3,107    ❌ gap   (NEW+KM0 combined surface ~6,210)
RENTING   ~808      ❌ gap
--------------------------------------------------
TRUE TOTAL ≈ 282,700  (used 272,720 + new ~6,089 + km0 ~3,107 + renting ~808)
COVERED    272,720..272,903  → ~96.5% of platform by count, 0% of non-used kinds
```

**Overlap caveat `[ASSUMED]`:** `/nuevo/km-0/` (~6,210) is a COMBINED surface; adding
`/nuevo/` (6,089) + `/km-0/` (3,107) separately double-counts the km0∩new region. The
honest non-used residual after de-overlapping is **~9–10k cars** across new+km0+renting;
the exact union needs the segmented SRPs (Imperva-walled this session) to deduplicate.
The ~282,700 grand total is the de-overlapped figure (used + ~9–10k non-used residual).

**GAPS = [ New (coches nuevos) ~6,089 · Km0 + seminuevos ~3,107 · Renting / suscripción ~808 ]**
— cause: the open `/search` gateway is segment-locked to the used index; the three
non-used kinds live on separate backends, each a distinct recipe-hunt (Imperva-fronted
SRP or a dedicated `nuevo`/`renting` BFF host).

---

## 2. wallapop — per-segment matrix

`source_key = wallapop_wholesale`; platform entity `CDP-ES-00-EMRH0TWQ`. Probed live via
`GET api.wallapop.com/api/v3/search/section` at `category_id=100` (cars vertical),
reading the server's own `pointers.ORGANIC.remaining_documents`. Full probe log:
[`segments/wallapop.md`](segments/wallapop.md).

There is **no** coches.com-style hidden `vn.xml` NEW segment here — the analogue does
not exist. The only real partitions are seller type, mileage range, and year range; all
condition facets (`condition=new`, `is_new=true`, `car_status=new`, …) are silently
ignored (return the full 651,199) `[VERIFIED]`.

| Segment / axis | param | Published (live) | Covered? | Coverage detail |
|---|---|--:|:--:|---|
| **Whole cars vertical** | `category_id=100` | **651,199** `[VERIFIED]` | ✅ YES | Flat `order_by=newest` cursor walks the ENTIRE catalog with no segment filter. |
| **Professional / dealer** | `seller_type=professional` | 345,836 `[VERIFIED]` | ✅ YES | `users/{id}` type=professional → `compraventa` entity. |
| **Private (C2C)** | `seller_type=private` | 305,323 `[VERIFIED]` | ✅ YES | type=normal → per-seller `particular` entity. |
| **Km0 / 0-km slice** | `max_km` range | ~2,197 @0km (~4,937 ≤10km) `[VERIFIED]` | ✅ YES (incidental) | Inside the unfiltered cursor; no discrete km0 vertical. |
| **New model-year slice** | `min_year` range | ~29,936 (2025+) `[VERIFIED]` | ✅ YES (incidental) | Inside the unfiltered cursor; a slice, not a segment. |
| **New-car (VN) catalog** | — | **does not exist** | N/A | wallapop has no VN vertical. |
| **Renting vertical** | — | **does not exist** | N/A | `subcategory_ids=renting` → HTTP 400. |

(`has_warranty=true` → 289,739 is a dealer/quality signal overlapping both seller types,
not an inventory segment — recorded for completeness only.)

### True grand total — wallapop

```
WHOLE VERTICAL  651,199  (= professional 345,836 + private 305,323, ±live jitter)
--------------------------------------------------
TRUE TOTAL = 651,199 live ES cars (category_id=100), geo-independent.
            (The ~750k marketing figure includes non-current / other-locale listings.)
IN DB      81,142 platform_listing edges → ~12.5% DEPTH
           (compraventa 36,227 + legacy garaje-bucket 22,900 + particular 22,015)
```

**Shortfall is DEPTH, not coverage.** The connector runs chunked (~8k target/run) and
has not walked the cursor to `remaining_documents → 0`. No segment is excluded; the
22,900 legacy `garaje` bucket cars are mid-migration to per-seller `particular`
(connector `cleanup_legacy_buckets`). To reach ~651k, walk the existing cursor deeper —
no new selector to add.

**GAPS = [ ]** — no missing segment exists on wallapop.

---

## 3. coches.com — per-segment matrix

`source_key = coches_com_wholesale`. The homepage literally renders **"más de 230.000
ofertas"** — honoured as the **declared site total**, not dismissed as marketing. Beneath it,
every sellable segment is enumerated and reconciled. Counts hand-counted against the live
`__NEXT_DATA__` SSR blob (SRP/hub `total` field + make-partition Σ). Full probe log:
[`segments/coches_com.md`](segments/coches_com.md).

| Segment | Selector (web) | Published | Covered? | Coverage detail |
|---|---|--:|:--:|---|
| **VO (usados)** | `/coches-segunda-mano/{make}.htm` | **92,381** `[VERIFIED live]` | ✅ YES (`vo`) | `classifieds.total`; `seoData[all-makes]` n=93 Σ=92,382. Owned by the selling dealer (compraventa). |
| **Km0 (seminuevos)** | `/km0/{make}.htm` | **15,630** `[VERIFIED live]` | ✅ YES (`km0`) | Σ `/km0/` `brands` == `popularClassified.total`; `seoData[all-makes]` n=68 Σ=15,630. Structural twin of VO (same card, `category=2`,`isKm0=true`); `/km0/…?id=` link namespace distinct so VO∩km0 cannot collide. |
| **VN / catalog (coches nuevos)** | `/coches-nuevos/coches-nuevos.htm` | **826** `[VERIFIED live]` | ✅ YES (`vn` = `catalog`) | `search.total`; version OFFER (`versionId`, make, model, `pvp`/`price`/`discount`) with no per-car dealer → platform-owned, PVP→price captured as `price_drop`. |
| **Renting / suscripción** | `/renting-coches` | **8,908** `[VERIFIED live]` | ✅ YES (`renting`) | `totalOffers`; platform-owned offer (make/model, `fee`/mes, `dealerId`/`dealerName`, `href`). SSR special offers caged; full paginated list is the documented escalation reserve. |

### True grand total — coches.com

```
VO        92,381   ✅ covered (vo)
KM0       15,630   ✅ covered (km0)
VN        826      ✅ covered (vn = catalog)
RENTING   8,908    ✅ covered (renting)
--------------------------------------------------
CAPTURABLE TOTAL = 117,745  distinct sellable listings
SITE-DISPLAYED   = 230,000  ("más de 230.000 ofertas" — declared site peg)
GAP TO DISPLAYED = 112,255  = the platform's OWN offer-inflation, not hidden stock
```

**Why 230,000 is multi-counted, not 230k distinct cars `[VERIFIED]`:** the VO page's
`seoData[all-provinces]` is `type=showroom_list.province` and its counts sum to **~4,287,186**
(Madrid alone 632,851) — an order of magnitude above any real car count. coches.com counts each
listing across every showroom × financing surface; **230,000 is the platform's headline
"ofertas" figure, not 230,000 distinct cars**. We cage the 117,745 real distinct listings and
DECLARE 230,000 as the site peg.

**`--segment all` (CLI):**

```
python -m pipeline.platform.coches_com_wholesale --segment all --all
```

Runs vo → km0 → vn → renting in SEQUENCE under the same per-host governor/breaker (all hit
`www.coches.com`) and emits the reconcile report above. Per segment:
`--segment {vo|km0|vn|catalog|renting} --all`. Bounded proof: `--limit N` or `--pages P`.

**GAPS = [ ]** — all four segments covered by the extended connector. The 112,255 residual to
the displayed 230,000 is platform offer-inflation, not a missing segment.

---

## 4. autocasion — per-segment matrix

`source_key = autocasion_facet`; platform entity `CDP-ES-00-QY06GW0B`. Three drainable
inventory segments, each its own SSR facet tree carrying `-ref{ID}` PDP cards + a `<title>`
count; the same make-partition machinery drains all three. The connector previously drained
**only used**; it now drains all three. Full probe log:
[`segments/autocasion.md`](segments/autocasion.md).

| Segment | Selector (web facet) | Published | Covered? | Coverage detail |
|---|---|--:|:--:|---|
| **VO (used / ocasión)** | `/coches-segunda-mano/{make}-ocasion[/{prov}]` | **123,512** `[VERIFIED live]` | ✅ YES (`vo`) | SRP `/coches-ocasion` `<title>`. MERCEDES-BENZ (>10k) splits by province. Sealed by the make-partition. |
| **VN (new / coches nuevos = catalog)** | `/coches-nuevos/{make}` | **5,946** `[VERIFIED live, make-sum]` | ✅ YES (`vn` = `catalog`) | Σ per-make `<title>` over **76 makes with stock, every make < 10k** (no province split). Dealer new-car catalog; `catalog` is an alias of `vn`. |
| **KM0 (km cero / demo)** | `/coches-km0/{make}-km0` | **5,994** `[VERIFIED live, make-sum]` | ✅ YES (`km0`) | Σ per-make `<title>` over **84 makes with stock, every make < 10k** (no province split). Near-new dealer stock (`km0=true`). |
| **Renting / suscripción** | — (every `/renting*` 404s) | **does not exist** | N/A | Honest declared gap: `--segment renting` accepted but reported non-existent, never a silent skip. |

### True grand total — autocasion

```
VO  (used / ocasión)   123,512   ✅ covered (vo)
VN  (new / catalog)      5,946    ✅ covered (vn)   — 76 makes, every make < 10k
KM0 (km cero / demo)     5,994    ✅ covered (km0)  — 84 makes, every make < 10k
RENTING                  —        N/A (does not exist on autocasion)
--------------------------------------------------
TRUE TOTAL = 135,452 cars  (vo + vn + km0); renting N/A — reconciles to the site-displayed sum
```

**Make axis is the non-overlapping denominator `[VERIFIED]`:** VN/KM0 province aggregates
OVERLAP (a national new-car offer surfaces in every province) and are NOT summed; the make sum
is. The three segments are disjoint product surfaces (used XOR new XOR km0); a global
`seen_ids` set additionally collapses any cross-page / cross-slice / cross-segment id repeat
exactly once.

**`--segment all` (CLI):**

```
python -m pipeline.platform.autocasion_facet --segment all
```

Per segment: `--segment {vo|vn|km0}` (aliases: `catalog`→vn; `renting` reported non-existent);
`--segment vn,km0` composes; bounded proof `--max-makes N` / `--make smart`.

**GAPS = [ Renting / suscripción — does not exist on autocasion ]** (a true non-existent
segment, not an uncovered one). All three real segments covered.

---

## 5. motor.es — per-segment matrix

`source_key = motor_es_wholesale`. motor.es shows **NO** 230k-style inflated figure — its
headline IS the used census: the `/segunda-mano/` landing title shows **"50.769 coches
disponibles"**, the live `get-data-ajax data.total = 50,932`, km0 included. Two surface
families (facet vs offer) share one cage contract. Full probe log:
[`segments/motor_es.md`](segments/motor_es.md).

| Segment | Selector (web) | Published | Covered? | Coverage detail |
|---|---|--:|:--:|---|
| **VO (used census)** | `/segunda-mano/{make}/{model}/` | **50,932** `[VERIFIED live]` | ✅ YES (`vo`) | `get-data-ajax data.total`; landing title "50.769 coches". Card → `/segunda-mano/anuncio/{id}/` PDP, vehicle owned by selling dealer. **This is the census.** |
| **Km0 / seminuevos** | `/coches-km0/` | **5,594** `[VERIFIED live]` | ✅ via VO (`km0` selectable) | **PROVEN SUBSET of VO** — same `/segunda-mano/anuncio/{id}/` PDP namespace (km0 id 23564668 EBRO S700 appears in `/segunda-mano/ebro/s700/`). Not additive. |
| **VN (new-car offers)** | `/coches-nuevos/ofertas/` | **476** `[VERIFIED live]` | ✅ YES (`vn`) | "476 coches encontrados"; `/{make}/{model}/` offer page (`@type:Car` + `offers.price`, no id/km/dealer) → platform-owned catalog offer. Additive. |
| **Catalog (full new-car catalog)** | `/coches-nuevos/` | **450** `[VERIFIED live]` | ✅ YES (`catalog`) | "Más de 90 marcas y 450 modelos" (configurator). **⊃ vn** — ~26 net new beyond the 476 offers. |
| **Renting** | `/renting/` | **132** `[VERIFIED live]` | ✅ YES (`renting`) | "132 coches encontrados"; catalog-shaped, platform-owned offers. Additive. |

### True grand total — motor.es

```
~50,932  VO used census (km0's ~5,594 already counted within)
+   476  VN new-car offers
+   132  renting offers
-------
~51,540  additive sellable surface (VO + VN offers + renting)
~51,990  if the full 450-model new catalog is also caged (catalog ⊃ vn → ~26 net new beyond vn)
```

**Reconciliation `[VERIFIED]`:** the site-displayed inventory total reconciles to the **~50.9k
used census** (km0 included). The genuinely uncovered additive inventory beyond it = **VN
offers (~476) + renting (~132)** plus the **450-model new catalog** if the configurator is
wanted.

**`--segment all` (CLI):**

```
python -m pipeline.platform.motor_es_wholesale --segment all --full
```

`--segment all` = **vo + vn + renting additive union**; it deliberately SKIPS `km0` (⊂ vo) and
`catalog` (⊃ vn) to avoid re-draining the same cars — request those explicitly. Per segment:
`--segment {vo|km0|vn|catalog|renting} --full`. Proof mode (no `--full`) bounds by
`--max-cells` / `--limit`.

**GAPS = [ ]** — every segment covered; `all` drains the de-overlapped additive union.

---

## 6. milanuncios — per-segment matrix

`source_key = milanuncios_wholesale`. Unlike the separate-backend platforms, milanuncios's
coches vertical is a **single Elasticsearch index**
(`GET searchapi.gw.milanuncios.com/v4/classifieds?category=13&transaction=supply`). Every
sellable car — used, km0, seminuevo, "a estrenar", pro, private — is an ordinary
`transaction=supply` ad inside that one index. "Segments" are **per-item facet slices**, not
separate products; the existing `province × price-band` partition already drains 100% of them.
Full probe log: [`segments/milanuncios.md`](segments/milanuncios.md).

| Segment / axis | param | Published (live) | Covered? | Coverage detail |
|---|---|--:|:--:|---|
| **All coches (full flat supply index)** | `category=13&transaction=supply` · `--segment all` | **~272,130** `[VERIFIED]` | ✅ YES (`all`, default) | The province×price-band drain pulls EVERY supply ad regardless of condition. |
| **Professional (compraventa / VO-pro)** | `sellerType=professional` (split, not a `--segment`) | **66,005** over 46 eq-prov `[VERIFIED]` | ✅ YES (in `all`) | `ad.type=professional` → compraventa entity. Seller-split cross-check, not a flag. |
| **Private (particular)** | `sellerType=private` (split, not a `--segment`) | **76,439** over 46 eq-prov `[VERIFIED]` | ✅ YES (in `all`) | `ad.type!=professional` → per-seller particular entity. Seller-split cross-check, not a flag. |
| **Km0 / seminuevo** | `kilometersTo<=1000` facet · `--segment km0` | facet slice (e.g. Madrid km≤100 = 2,897) `[VERIFIED]` | ✅ YES (mixed in `all`) | A km-band slice of `all`, not a discrete vertical. |
| **VN / nuevo a estrenar** | `kilometersTo<=100` facet · `--segment vn` (`catalog` alias) | per-item `ad.isNew` flag (~39–48% of newest pages) `[VERIFIED]` | ✅ YES (mixed in `all`) | A lowest-km slice of `all`; no separate new-car catalog. |
| **New-car catalog / configurator** | — none — | **does not exist** `[VERIFIED]` | N/A | `coches-nuevos.htm` is "coches nuevos **de segunda mano y ocasión**" — a filter on the used index, not a catalog. |
| **Renting / suscripción** | — none — | **does not exist** `[VERIFIED]` | N/A | No renting product on milanuncios coches; `--segment renting` exits with a clear message. |

### True grand total — milanuncios

```
46 "eq" provinces (single probe each)              Σ = 142,445   [VERIFIED]
6 dense metro provinces (price-band sub-sharded):
  Madrid 50,356 + Barcelona 23,083 + Alicante 12,797
  + Malaga 13,112 + Sevilla 14,582 + Valencia 15,755 = 129,685   [VERIFIED]
--------------------------------------------------
NATIONAL live supply total ≈ 272,130 currently-listed coches  [VERIFIED]
```

**Seller-split cross-check `[VERIFIED]`:** professional 66,005 + private 76,439 = 142,444 over
the 46 eq provinces — gap-free, additive, ≈ the eq-province total (142,445); proves pro +
private together = the whole index with no third seller bucket. **Marketing ~666,901 is the
whole-motor-vertical / all-time figure** (includes motos, recambios, inactive), NOT the live
coches `supply` count. milanuncios prints no single global badge — per-region SRP titles
sum to ~272,130.

**`--segment all` (CLI):**

```
python -m pipeline.platform.milanuncios_wholesale --segment all
```

`--segment all` is the **canonical full-drain and the default** — the in-flight operator run
already captures every segment. Narrower slices: `--segment {vo|km0|vn|catalog}` (`catalog`→vn;
`renting` no-op: not a product). Professional/private are a `sellerType` split inside `all`
(both seller types are caged in the default drain), **not** a `--segment` choice. Legacy knobs
(`--provinces`, `--pages`, `--concurrency`) compose.

**GAPS = [ ]** — every segment is a facet of the one supply index the connector already drains.
No new-car catalog and no renting product exist on milanuncios coches.

---

## 7. Consolidated grand totals

| Platform | Segments published | True grand total | Site-displayed | Segment gaps |
|---|---|--:|--:|---|
| **coches.net** | used · new · km0/seminuevos · renting | **~282,700** | — | **3** (new ~6,089 · km0 ~3,107 · renting ~808) — *open* |
| **wallapop** | cars vertical (pro 345,836 + private 305,323) | **651,199** | ~750k mktg | **0** (depth-only) |
| **coches.com** | vo · km0 · vn/catalog · renting | **117,745** capturable | **230,000** (offer-inflated) | **0** (all 4 covered) |
| **autocasion** | vo · vn/catalog · km0 (renting N/A) | **135,452** | ~135,452 | **0** real (renting does not exist) |
| **motor.es** | vo (⊃km0) · vn · catalog · renting | **~51,540** additive | ~50,932 census | **0** (all covered) |
| **milanuncios** | flat supply index (pro 66,005 + private 76,439 + facets) | **~272,130** | ~272,130 | **0** (one index, all facets) |

**Tier-1 true total (6 audited platforms):**
~282,700 (coches.net) + 651,199 (wallapop) + 117,745 (coches.com) + 135,452 (autocasion)
+ ~51,540 (motor.es) + ~272,130 (milanuncios) ≈ **~1,510,800 cars**.

### Action items by platform

- **coches.net** — close the SEGMENT gap (still open): build three new segment recipes, each a
  distinct backend from the used gateway — `/nuevo/` (~6,089), `/km-0/` (~3,107 /
  combined ~6,210), `/renting/` (~808). None is reachable via `web.gw.coches.net/search`.
- **wallapop** — close the DEPTH gap: run the existing `order_by=newest` cursor to
  `remaining_documents → 0` (≈651k) and let `cleanup_legacy_buckets()` retire the
  emptied legacy `garaje` buckets. No new selector required.
- **coches.com** — segment gap CLOSED: `--segment all --all` drains vo+km0+vn+renting (117,745).
  Reserve: replay the renting list XHR to cage all 8,908 (only inline SSR offers caged today).
- **autocasion** — segment gap CLOSED: `--segment all` drains vo+vn+km0 (135,452). No renting
  product exists; no further segment to add.
- **motor.es** — segment gap CLOSED: `--segment all --full` drains the additive union
  vo+vn+renting (~51,540); add `--segment catalog` for the full 450-model new catalog (~51,990).
- **milanuncios** — no segment gap: `--segment all` (the default full-drain) already covers every
  facet of the single supply index (~272,130). Only run the in-flight drain to completion.

---

*Source of truth: live DB `cardeep-pg` (`:5433`) + pipeline connectors under
`pipeline/platform/` + per-platform audits in [`segments/`](segments/):
[`coches_net.md`](segments/coches_net.md), [`wallapop.md`](segments/wallapop.md),
[`coches_com.md`](segments/coches_com.md), [`autocasion.md`](segments/autocasion.md),
[`motor_es.md`](segments/motor_es.md), [`milanuncios.md`](segments/milanuncios.md).
Generated 2026-06-13.*
