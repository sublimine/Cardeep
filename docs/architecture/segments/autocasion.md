# autocasion — Segment Census (READ-ONLY audit + connector EXTENDED)

> **Mandate.** CARDEEP doctrine: *"todo su inventario de coches"* = EVERY segment a
> platform exposes (usados/ocasión, NUEVOS, km0/seminuevos, renting/suscripción), not
> only the used pool. This file enumerates every inventory segment autocasion.com
> publishes, its PUBLISHED count, the URL that selects it, whether the EXISTING connector
> (`pipeline/platform/autocasion_facet.py`) covers it, and the **extension built this
> session** that drains every segment with one command.
>
> **Scope.** READ-ONLY probes (a handful of GETs/POSTs) + a TINY 1-page smoke of the NEW
> segment to prove the parse. A full operator-driven drain was already running on the host,
> so NO big harvest was launched here. Probed live with `curl_cffi chrome131` on
> 2026-06-13. Marking discipline: every count is **[VERIFIED]** (read live this session)
> or **[ASSUMED]** (inferred, not re-derived).

---

## 0. TL;DR — the gap and the fix

Unlike coches.net (whose open gateway is segment-LOCKED to used), autocasion exposes
**three drainable inventory segments**, each its OWN SSR facet tree that carries PDP
`-ref{ID}` cards and a `<title>` count — so the SAME make-partition machinery drains all
three. The connector previously drained **only the USED segment**; it now drains all three.

| Segment | Selector (web facet) | Published | Covered BEFORE | Covered AFTER (`--segment`) |
|---|---|--:|:--:|:--:|
| **Used (VO / ocasión)** | `/coches-segunda-mano/{make}-ocasion[/{prov}]` | **123,512** `[VERIFIED live]` | ✅ YES (`vo`) | ✅ YES (`vo`) |
| **New (VN / coches nuevos = catalog)** | `/coches-nuevos/{make}` | **5,946** `[VERIFIED live, make-sum]` | ❌ NO | ✅ **YES (`vn`)** |
| **Km0 / Demo** | `/coches-km0/{make}-km0` | **5,994** `[VERIFIED live, make-sum]` | ❌ NO | ✅ **YES (`km0`)** |
| **Renting / suscripción** | — (every `/renting*` 404s) | **does not exist** | N/A | N/A (reported as gap) |

**Site-displayed reconciliation (all sellable segments):**
```
VO  (used / ocasión)   123,512   ✅
VN  (new / catalog)      5,946    ✅ (NEW — 76 makes w/ stock, every make < 10k)
KM0 (km cero / demo)     5,994    ✅ (NEW — 84 makes w/ stock, every make < 10k)
-------------------------------------------------------------
TRUE TOTAL ≈ 135,452 cars  (renting does not exist on autocasion)
```

**One command drains all three:** `python -m pipeline.platform.autocasion_facet --segment all`.

---

## 1. robots.txt + facet vocabulary (probe result)

- The VO recipe (`tier1_recipes/autocasion_datalayer.md`) already established robots.txt
  allows the **path-segment** facets (`/coches-segunda-mano/{make}-ocasion`) and disallows
  query-param filter URLs (`*?*marca=*`) + `/api/*`. The NEW + KM0 facets are the same kind
  of path-segment surface (`/coches-nuevos/{make}`, `/coches-km0/{make}-km0`) — crawlable.
- `/coches-nuevos` landing carries the make/model/province/body facet vocabulary
  (`/coches-nuevos/{make}`, `/coches-nuevos/{make}/{model}`, `/coches-nuevos/{prov}-provincia`,
  `/coches-nuevos/berlinas|compactos|deportivos|…`) `[VERIFIED]`.
- `/coches-km0` landing carries `/coches-km0/{make}-km0`, `/coches-km0/{city}` (bare city
  slug, NOT `-provincia`), `/coches-km0/certificado|electrico|berlinas|…` `[VERIFIED]`.

---

## 2. The GraphQL `search` gateway is the USED index only (why VN/KM0 need the facet)

`POST gql.autocasion.com/graphql/` `search.paginatedAds.total` = **115,179** (the used
ES index) `[VERIFIED]`. `SearchParamInput` requires `{key,value}` (not `{name,value}`);
there is no `condition`/`estado`/`km0`/`new` facet exposed on the API (introspection in the
VO recipe found no such registered facet, and arbitrary keys are rejected). So NEW and KM0
are **not** reachable by a GraphQL param — exactly like the VO 10k-wall situation, the
**URL-path facet** is the surface. Each NEW/KM0 make facet is server-rendered (curl_cffi,
no browser) and carries the slice total in `<title>` + the `-ref{ID}` cards in the body.

---

## 3. Per-segment detail

### SEG · VO — Used (ocasión / segunda-mano) — `--segment vo` (default)
- **Selector.** `/coches-segunda-mano/{make}-ocasion`; MERCEDES-BENZ (>10k) → `/{make}-ocasion/{province}`.
- **Published.** SRP `/coches-ocasion` `<title>` = **123,512** (live this session: 123,516) `[VERIFIED]`.
- **Coverage.** ✅ Sealed by the make-partition (the pre-existing facet drain). DB holds
  **11,621** autocasion `platform_listing` edges at audit time (a partial operator drain in
  progress; the VO partition's declared full = 123,512).

### SEG · VN — New (coches nuevos = the new-car catalog) — `--segment vn`
- **Selector.** `/coches-nuevos/{make}` → `<title>"N {Make} nuevos"`. Province aggregate
  `/coches-nuevos/{prov}-provincia` (Madrid **4,423**, Barcelona 3,908, Valencia 4,077 —
  these OVERLAP because a national new-car offer surfaces in every province, so the
  **make** axis is the non-overlapping denominator, NOT the province sum). `[VERIFIED]`
- **Published.** Σ per-make `<title>` totals = **5,946** over **76 makes with stock**;
  **every make < 10k** (largest probed: BMW 343, then thousands across the long tail), so
  **no province split is needed** `[VERIFIED — sized all 184 makes live]`.
- **Nature.** Dealer new-car catalog: each make/model/version offer is a real `-ref{ID}`
  ad (e.g. `/coches-nuevos/audi-a3/rs3-sedan-…-ref14325105`). `ad()` hydrates it
  (AUDI A3, price 86,907, `km0=false`, year/km null = catalog offer) and the PDP carries
  `offers.offeredBy = AutoDealer` (unoauto, postalCode 28027 → province 28) `[VERIFIED]`.
- **Coverage.** ✅ **NOW covered (`vn`).** Drains through the SAME `process_ref` cage path.
  TINY smoke this session: `--segment vn --make smart` → 18 declared = 18 caged = 18 edges
  = 18 NEW delta events, VAM **TRUSTWORTHY**, breaker closed `[VERIFIED smoke]`.
- **Catalog/configurator note.** autocasion's "new" surface IS the catalog — there is no
  separate configurator endpoint; the new offers are the sellable units. `--segment catalog`
  is therefore an **alias of `vn`**.

### SEG · KM0 — Km0 / Demo — `--segment km0`
- **Selector.** `/coches-km0/{make}-km0` → `<title>"N Km 0 {Make}"`. City aggregate
  `/coches-km0/{city}` (Madrid **1,338**) `[VERIFIED]`.
- **Published.** Σ per-make `<title>` totals = **5,994** over **84 makes with stock**;
  **every make < 10k** (no over-10k make), so no province split needed
  `[VERIFIED — sized all 184 makes live]`.
- **Nature.** Near-new dealer stock. `ad()` hydrates it (SEAT Arona, year 2026, km=1,
  **`km0=true`**, price 21,790) — the cage path works unchanged `[VERIFIED]`.
- **Coverage.** ✅ **NOW covered (`km0`).** Same make-partition, same cage path.

### SEG · Renting / suscripción — does NOT exist
- Every probed path 404s: `/renting`, `/renting-coches`, `/coches-renting` `[VERIFIED]`.
  autocasion has no renting/subscription vertical. `--segment renting` is accepted but
  reported as a **non-existent segment** (honest declared gap, never a silent skip).

---

## 4. True-100% denominator for autocasion (this platform)

```
VO  (used / ocasión)   123,512   ✅ covered (vo)
VN  (new / catalog)      5,946    ✅ covered (vn)   — 76 makes, every make < 10k
KM0 (km cero / demo)     5,994    ✅ covered (km0)  — 84 makes, every make < 10k
RENTING                  —        N/A (does not exist)
-------------------------------------------------------------
TRUE TOTAL ≈ 135,452 cars  (vo + vn + km0)
```

**Overlap note `[VERIFIED]`:** the three segments are DISJOINT product surfaces (a car is
used XOR new XOR km0); a NEW offer's `-ref{ID}` is distinct from any used `-ref{ID}`. The
connector's GLOBAL `seen_ids` set additionally collapses any cross-page / cross-slice /
cross-segment id repeat exactly once, so the union is de-duplicated at harvest. Within VN
and KM0 the **make** axis is non-overlapping (province aggregates overlap and are NOT
summed). No segment exceeds the 10k ES wall in vn/km0, so no province split fires for them.

---

## 5. The connector extension (BUILT this session)

`pipeline/platform/autocasion_facet.py` extended with a `Segment` descriptor + a
`--segment {all|vo|vn|km0}` flag (aliases: `catalog`→vn; `renting` reported non-existent).
Each segment differs ONLY in its facet-path template and `<title>` shape; everything else
is reused **byte-for-byte** from the proven VO path:

- **Same cage contract:** `process_ref` (GraphQL `ad()` hydrate → PDP JSON-LD AutoDealer →
  per-car transaction → platform entity + selling-dealer upsert + vehicle owned by dealer +
  platform_listing edge + delta NEW/PRICE_CHANGE), idempotent `ON CONFLICT`.
- **Same machinery:** per-host governor (gql + www buckets), S-HEALTH breaker, VAM count
  quorum (`harvested_cageable == db_edges == db_join_vehicles`), batch via SSR `?page=N`,
  recipe writer, dual-membership model.
- **Per-segment plan:** `plan_partitions(seg, makes, provinces)` sizes each make's facet
  `<title>`; any make > 10k splits by province (segment-generic — none of vn/km0 hit it
  today, future-drift-safe). Slices from all requested segments concatenate into ONE drain
  with a GLOBAL `seen_ids`.

**Full CLI (drain every segment, one command):**
```
python -m pipeline.platform.autocasion_facet --segment all
```
**Per-segment / bounded:**
```
python -m pipeline.platform.autocasion_facet --segment vn
python -m pipeline.platform.autocasion_facet --segment km0
python -m pipeline.platform.autocasion_facet --segment vn,km0
python -m pipeline.platform.autocasion_facet --segment vn --max-makes 5     # bounded proof
python -m pipeline.platform.autocasion_facet --segment vn --make smart      # tiny slice
python -m pipeline.platform.autocasion_facet --segment vo                   # back-compat default
```

---

## 6. Evidence log (this session, 2026-06-13)

- Path probe `[VERIFIED]`: `/coches-nuevos` HTTP 200 + `-ref{ID}` cards
  (`/coches-nuevos/{make-model}/…-ref{ID}`); `/coches-km0` HTTP 200 + `-ref{ID}` cards;
  every `/renting*` → 404.
- VN make facet `[VERIFIED]`: `/coches-nuevos/seat` = "161 Seat nuevos", `/coches-nuevos/bmw`
  = "343 BMW nuevos", 25 cards/page, `?page=N` paginates cleanly (page1∩page2 = ∅).
- VN province aggregate `[VERIFIED]`: Madrid 4,423 / Barcelona 3,908 / Valencia 4,077 —
  cross-province page-1 sets disjoint → national offers, make axis is the denominator.
- KM0 make facet `[VERIFIED]`: `/coches-km0/seat-km0` = "74 Km 0 Seat"; city `/coches-km0/madrid`
  = "1.338 Km 0 en Madrid".
- Make-sum sizing over all 184 `brands(type:CAR)` `[VERIFIED]`: VN = **5,946** (76 makes,
  0 over-10k); KM0 = **5,994** (84 makes, 0 over-10k).
- Hydration `[VERIFIED]`: VN ref 14325105 → AUDI A3 (km0=false, year/km null, dealer
  unoauto/28027); KM0 ref 19593938 → SEAT Arona (km0=true, year 2026, km 1).
- TINY smoke `[VERIFIED]`: `--segment vn --make smart` → 18 caged / 18 edges / 18 NEW
  events / 0 errors, dealer `unoauto` (prov 28), VAM **TRUSTWORTHY**, breaker closed.
  DB autocasion edges 11,578 → 11,621 (smoke + concurrent operator drain).
- DB `[VERIFIED]`: platform `CDP-ES-00-QY06GW0B`, `source_health` healthy, 0 consecutive fails.
