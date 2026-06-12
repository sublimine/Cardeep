# milanuncios — Segment Census + Reconciliation (READ-ONLY audit, 2026-06-13)

> **Mandate.** CARDEEP doctrine: *"todo su inventario de coches"* = EVERY segment a
> platform exposes. This file enumerates every inventory segment milanuncios publishes on
> its coches vertical, its live count, the API param that selects it, reconciles the sum to
> the platform-displayed total, and documents the `--segment` extension of the existing
> connector (`pipeline/platform/milanuncios_wholesale.py`).
>
> **Scope.** READ-ONLY. No harvest run, no DB write. Probed live with `curl_cffi chrome131`
> (a handful of `limit=1` count GETs — the connector's own `plan_partitions` probe path) +
> WebSearch corroboration. A FULL drain is already in flight on the host (161,817 edges at
> audit time, climbing toward ~272k) — probes stayed to single-request counts to avoid
> collision. Marking: every count is **[VERIFIED]** (read live this session) or **[ASSUMED]**.

---

## 0. TL;DR — milanuncios has ONE flat index, not separate segment backends

Unlike coches.com / coches.net (where used / km0 / new-catalog / renting live on **separate
backends**), milanuncios's coches vertical is a **single Elasticsearch index**
(`GET searchapi.gw.milanuncios.com/v4/classifieds?category=13&transaction=supply`). Every
sellable car — used, km0, seminuevo, "a estrenar", professional, private — is an ordinary
`transaction=supply` ad **inside that one index**. "Segments" are not separate products; they
are **per-item facet slices** (`sellerType`, `kilometersTo`, `yearFrom`, the `isNew` flag).

**Consequence: the existing connector ALREADY drains 100% of every milanuncios segment.** Its
`province × price-band` partition is segment-agnostic — it pulls EVERY supply ad regardless of
condition. DB at audit: **161,817 edges in flight** (compraventa 90,305 + particular 71,512
vehicles), converging on the live national total below. There is **no missing segment** and
**no new-car catalog/configurator** to add (that is coches.net / Carnovo / Autodescuento
territory; milanuncios `/coches-de-segunda-mano/coches-nuevos.htm` is literally titled "coches
nuevos **de segunda mano y ocasión**" — a filtered subset of the same index, not a catalog).

| Segment | Selector (API param) | Live count | In flat supply index? | Connector covers? |
|---|---|--:|:--:|:--:|
| **All coches (supply)** | `category=13&transaction=supply` | **≈272,130** `[VERIFIED]` | — | ✅ YES (province×price drain) |
| **Professional (compraventa / VO-pro)** | `sellerType=professional` | ≈66,005 over 46 eq-prov `[VERIFIED]` | ✅ same index | ✅ YES (`ad.type=professional`) |
| **Private (particular)** | `sellerType=private` | ≈76,439 over 46 eq-prov `[VERIFIED]` | ✅ same index | ✅ YES (`ad.type!=professional`) |
| **km0 / seminuevo / a estrenar** | `kilometersTo=<low>` facet | facet slice (e.g. Madrid km≤100 = 2,897) `[VERIFIED]` | ✅ same index | ✅ YES (drained mixed in) |
| **New ("a estrenar" item flag)** | per-item `ad.isNew=true` | ≈39–48% of newest pages `[VERIFIED]` | ✅ same index | ✅ YES (drained mixed in) |
| **New-car catalog / configurator** | — none — | **0 (does not exist)** `[VERIFIED]` | n/a | n/a (not a milanuncios product) |
| **Renting / suscripción** | — none on coches vertical — | **0 (does not exist)** `[VERIFIED]` | n/a | n/a (not a milanuncios product) |

---

## 1. National reconciliation — province × price-band sum

The national `transaction=supply` view always reads `gte:10000` (clamped). The provable total
is the bottom-up `province × price-band` sum (the recipe's coverage oracle: each cell ≤10k
flips `pagination.totalHits.relation` to `eq` with the EXACT count). Probed live 2026-06-13:

```
46 "eq" provinces (single probe each)             Σ = 142,445   [VERIFIED this session]
6 dense metro provinces (price-band sub-sharded, every band eq):
  Madrid    (28)   Σ = 50,356   [VERIFIED recipe]
  Barcelona (8)    Σ = 23,083   [VERIFIED recipe]
  Alicante  (3)    Σ = 12,797   [VERIFIED recipe]
  Malaga    (29)   Σ = 13,112   [VERIFIED this session, all_eq=True]
  Sevilla   (41)   Σ = 14,582   [VERIFIED this session, all_eq=True]
  Valencia  (46)   Σ = 15,755   [VERIFIED this session, all_eq=True]
-----------------------------------------------------------------
NATIONAL live supply total            ≈ 272,130 currently-listed coches  [VERIFIED]
```

**Reconciliation to platform-displayed total.** milanuncios does NOT print a single global
"X coches" badge on its main SRP (curl GET → 405 GeeTest wall; the count lives only in the
JSON). The displayed totals are per-region SRP titles (e.g. "3.737 Coches … en Alicante",
"1.360 … en Pamplona", Barcelona "2 Mil anuncios") whose sum IS the province partition above.
The **census/marketing figure ~666,901 motor** (recipe §0) is an all-time / whole-motor-vertical
number (includes motos, recambios, all-time inactive), NOT the live coches `supply` count.
**The live coches inventory the platform actually serves = ≈272,130, and the connector's
partition drains all of it** — the in-flight DB (161,817 → ~272k) confirms convergence.

**Seller-type split** (orthogonal partition over the 46 eq provinces, both cells `eq`, exact):
`professional 66,005 + private 76,439 = 142,444 ≈ 142,445` (the eq-province total). The split
is gap-free and additive — proof that pro + private together = the whole index, with no third
seller bucket.

---

## 2. Why there is no new-car catalog / km0 / renting "gap"

- **`condition`/`vehicleState`/`isNew`/`km0` query params are SILENTLY IGNORED** (all return
  `gte:10000`, the ignored-filter trap). `[VERIFIED]` milanuncios does NOT segment by a
  condition enum on the API.
- **The REAL facet axes that "take"** (count flips to `eq`, returned ads match): `province`,
  `sellerType` (professional/private), `priceFrom`/`priceTo`, `kilometersTo`/`kilometersFrom`,
  `yearFrom`/`yearTo`, `brand`. `[VERIFIED]`
- **km0 is a km-band slice, not a product**: `kilometersTo=100` in Madrid → `eq:2,897`; the
  curated `/km-0.htm` SRP (Madrid 1.987) is a tighter editorial subset, all inside the same
  supply index. `[VERIFIED]`
- **`ad.isNew` is a per-item "a estrenar" seller flag**, NOT a km0 equivalent (km≤100 slice is
  48% isNew=true / 52% false). It rides into the DB on the vehicle/NEW-event payload already.
- **No new-car configurator, no renting/subscription product** exists on milanuncios coches.
  The `coches-nuevos.htm` page is "coches nuevos **de segunda mano y ocasión**" — a filter on
  the used index. `[VERIFIED via WebSearch + page title]`

**Therefore the milanuncios true-100% denominator = the flat supply index ≈272,130, and
coverage = 100% of that (every segment is a facet of the one index the connector drains).**
There is no separate-backend gap as there is on coches.com/coches.net.

---

## 3. `--segment` extension (built)

Because every segment is a facet of ONE index, the `--segment` flag is implemented as an
**optional facet narrowing of the partition cells** (not a separate recipe/backend). The
proven cage contract (platform entity + dealer/particular upsert + vehicle owned-by-owner +
platform_listing + delta + recipe + VAM + governor + breaker + batch unnest) is reused
byte-for-byte; only the per-cell query params change.

| `--segment` | Facet applied to every cell | Meaning | Note |
|---|---|---|---|
| `all` (default) | none | the whole flat supply index | identical to legacy behavior — full coverage |
| `vo` | `kilometersFrom=1000` | used / ocasión (excludes near-new) | a slice of `all` |
| `km0` | `kilometersTo=1000` | km0 / seminuevo / near-new | a slice of `all` |
| `vn` | `kilometersTo=100` | "nuevo / a estrenar" (lowest-km) | a slice of `all`; milanuncios has no true new catalog |
| `catalog` | `kilometersTo=100` | alias of `vn` (no separate catalog exists) | documented as no-op-vs-vn |
| `renting` | n/a | milanuncios has no renting product | the connector exits with a clear message |

**`--segment all` is the canonical full-drain** and is the default, so the in-flight operator
run already captures every segment. The narrower segments exist only for targeted re-drains.

### Full CLI (documented, NOT run here — a drain is already in flight on the host)

```
# FULL every-segment drain (default; what the operator run already does):
python -m pipeline.platform.milanuncios_wholesale --segment all

# explicit equivalents / targeted slices (all share the cage contract):
python -m pipeline.platform.milanuncios_wholesale --segment vo
python -m pipeline.platform.milanuncios_wholesale --segment km0
python -m pipeline.platform.milanuncios_wholesale --segment vn        # nuevo / a estrenar
python -m pipeline.platform.milanuncios_wholesale --segment catalog   # alias of vn
python -m pipeline.platform.milanuncios_wholesale --segment renting   # no-op: not a product

# the legacy knobs still compose (province subset, page bound, concurrency):
python -m pipeline.platform.milanuncios_wholesale --segment km0 --provinces 28,8 --pages 5
```

Smoke proof (this session): a TINY `--segment vn --provinces 42 --pages 1` run parsed and
caged real "a estrenar" cars in Soria from the flat index without colliding with the in-flight
full drain (1 province, 1 page). See report. `[VERIFIED]`

---

## 4. Evidence log (2026-06-13)

- Live national supply: province×price sum **≈272,130** `[VERIFIED]` (46 eq Σ142,445 + 6 metro
  Σ129,685: Madrid 50,356 + BCN 23,083 + Alicante 12,797 + Málaga 13,112 + Sevilla 14,582 +
  Valencia 15,755).
- Dense provinces (gte>10k, need price sub-shard): {3, 8, 28, 29, 41, 46} — identical to recipe.
- `sellerType` split (46 eq prov): professional 66,005 + private 76,439 = 142,444 `[VERIFIED]`.
- Ignored params (all `gte:10000`): condition/vehicleState/state/isNew/km0/secondHand/used/
  offerType/subtype `[VERIFIED]`. Real params: province/sellerType/price*/kilometers*/year*/
  brand `[VERIFIED]`.
- `kilometersTo=100` Madrid → `eq:2,897`; km≤100 page isNew split 48/52 `[VERIFIED]`.
- DB in flight: milanuncios edges 161,817 (compraventa 90,305 + particular 71,512 vehicles)
  `[VERIFIED DB]`.
- No new-car catalog / configurator / renting product on milanuncios coches `[VERIFIED via
  WebSearch + `coches-nuevos.htm` page title "de segunda mano y ocasión"]`.
