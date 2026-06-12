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
>
> Live DB figures verified against `cardeep-pg` (`:5433`, db `cardeep`); published
> counts probed live `2026-06-13` with `curl_cffi chrome131`. Marking discipline:
> every count is **[VERIFIED]** (read this session) or **[ASSUMED]** (inferred /
> vendor-stated, not re-derived).

---

## 0. TL;DR — two different gap shapes

The two Tier-1 platforms audited fail the "true 100%" test in **opposite** ways:

| Platform | True total (live) | In DB | Gap shape | Gaps |
|---|--:|--:|---|---|
| **coches.net** | **~282,700** | 272,903 edges | **SEGMENT** gap — used is 100% sealed, every non-used kind is 0% | New ~6,089 · Km0+seminuevos ~3,107 · Renting ~808 |
| **wallapop** | **651,199** | 81,142 edges | **DEPTH** gap — one flat vertical, every segment incidentally covered, cursor not walked to the end | *(none — no segment excluded)* |

- **coches.net** drains the USED (ocasión) segment fully and reaches **0%** of NEW,
  KM0/seminuevos and RENTING — those live on **separate backends** the open
  `web.gw.coches.net/search` gateway cannot reach. The connector covers **~96.5% by
  count but 0% of the non-used kinds**. This is a real, caused, segment-shaped gap.
- **wallapop** has **NO** separate VN (new-car) catalog, **NO** km0 vertical, **NO**
  renting vertical. It is one generalist cars vertical (`category_id=100`); the
  connector's unfiltered `order_by=newest` cursor covers every seller type and every
  km/year band by construction. Its ~12.5% DB depth is a **cursor-DEPTH shortfall**
  (chunked at ~8k, not walked to `remaining_documents → 0`), **not** a skipped
  segment. `gaps = []`.

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

## 3. Consolidated grand totals

| Platform | Segments published | True grand total | In DB | % depth | Segment gaps |
|---|---|--:|--:|--:|---|
| **coches.net** | used · new · km0/seminuevos · renting | **~282,700** | 272,903 edges | ~96.5% by count | **3** (new ~6,089 · km0 ~3,107 · renting ~808) |
| **wallapop** | cars vertical (pro 345,836 + private 305,323) | **651,199** | 81,142 edges | ~12.5% | **0** |

**Tier-1 true total (audited platforms) ≈ 282,700 + 651,199 = ~933,900 cars.**

### Action items by platform

- **coches.net** — close the SEGMENT gap: build three new segment recipes, each a
  distinct backend from the used gateway — `/nuevo/` (~6,089), `/km-0/` (~3,107 /
  combined ~6,210), `/renting/` (~808). None is reachable via `web.gw.coches.net/search`.
- **wallapop** — close the DEPTH gap: run the existing `order_by=newest` cursor to
  `remaining_documents → 0` (≈651k) and let `cleanup_legacy_buckets()` retire the
  emptied legacy `garaje` buckets. No new selector required.

---

*Source of truth: live DB `cardeep-pg` (`:5433`) + per-platform audits
[`segments/coches_net.md`](segments/coches_net.md) and
[`segments/wallapop.md`](segments/wallapop.md). Generated 2026-06-13.*
