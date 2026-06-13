# CARDEEP — SEGMENT CENSUS · `b2b_extra_auctions` (España)

> **Front:** EVERY B2B wholesale + AUCTION / remarketing platform serving Spain **beyond
> the 3 we already hold** (Autorola, BCA España, Ayvens Carmarket). Keyword-driven,
> exhaustive. **EXCLUDES social media (FB/IG)** by owner mandate.
>
> **Verification:** universe swept live via WebSearch + WebFetch + `curl_cffi` chrome131
> on **2026-06-13**. Every DB count below is from **my own query** that day against
> `postgres://cardeep@localhost:5433/cardeep`. Each external fact is `[V]` (fetched live
> this day) or `[A]` (vendor/secondary, not re-derived on-site).
>
> **Result:** the one extra auction operator in the mandate's list that exposes a full
> **free, public** car-stock surface — **Subastacar** — is **CONNECTED** this run (233
> cars, 100% field completeness). The credentialed B2B operators (AUTO1, OPENLANE/Adesa,
> Manheim ES, Alcopa) are documented **GATED**; the non-resolving / out-of-scope names
> (Aucto, Ucars, Reezocar, EpicAuctions, Carmen) are confessed honestly as holes.

---

## 0. Taxonomy reference (DB, my query 2026-06-13)

The auction group lives under `source_group='official_registry'` (no dedicated `auction`
enum value exists — the same nearest-enum convention every auction member uses), modelled
with the dual-membership ontology: `kind='plataforma'` (the platform) + `kind='subasta'`
(the selling auction-house / sale event) + `vehicle` owned by the seller + `platform_listing`
edge.

`entity.kind='plataforma'` live count: **11** (was 10 before this front; **+1 = Subastacar**).

Auction/B2B platforms already present before this front (the mandate baseline to go BEYOND):

| trade_name | website | source_group | status |
|---|---|---|---|
| Autorola | autorola.es | official_registry | HAVE (auction, stealth-browser slice) |
| BCA Espana | es.bca-europe.com | official_registry | HAVE (auction, stealth-browser slice) |
| Ayvens Carmarket | carmarket.ayvens.com | official_registry | HAVE (auction, public GraphQL) |
| **Subastacar** | **subastacar.com** | **official_registry** | **NEWLY CONNECTED (this run)** |

---

## 1. The universe of "extra" B2B / auction platforms (enumerated ALL)

Every B2B wholesale / remarketing / auction operator serving Spain beyond the 3, found via
the live sweep (WebSearch + AutoAuctionAtlas Spain directory `[V]` + CarsBarter list + the
mandate's named targets). Classified by whether the **car stock is publicly reachable via a
FREE vector** (curl_cffi / data-layer; Playwright if walled) or is **login-gated B2B**.

### 1.1 Mandate-named targets

| Operator | Domain | Live probe 2026-06-13 | Stock surface | Verdict |
|---|---|---|---|---|
| **Subastacar** | subastacar.com | `[V]` 200, 238 resultados / 12 pág SSR | **SSR HTML + schema.org `vehicle` JSON-LD, NO login** (with `offers.price`) | **MISSING → CONNECTED** |
| AUTO1.com | auto1.com | `[V]` 200; `/es/cars` **302→`/es/merchant/signin`** | 30k-car wholesale stock behind a **professional login**; API is credentialed | MISSING — **GATED** (login wall) |
| Adesa = **OPENLANE** | openlane.eu | `[V]` 200; `/es/findcar` = **~6 KB Angular SPA shell**, no public data layer | B2B remarketer, lots behind dealer login | MISSING — **GATED** (JS SPA + dealer login) |
| Manheim España | manheim.es | `[V]` `/vehiculos` **404** on public host | catalog behind buyer login (B2B) | MISSING — **GATED** |
| Aucto | aucto.es | `[V]` **DNS does not resolve** / connection refused | — | MISSING — **UNREACHABLE** (no live host) |
| EpicAuctions | — | `[V]` no identifiable ES car-auction operator resolves | — | **UNREACHABLE** — not a real ES auction surface (confessed) |
| Reezocar | reezocar.com | `[V]` 200 root; `/used-cars` 404 | **French consumer car-import aggregator**, not an ES B2B auction | **OUT OF SCOPE** — not an ES auction platform |
| Carmen | — | `[V]` carmen.io / carmenautomocion unrelated/dead | — | **UNREACHABLE** — no ES car-auction operator under the name (confessed) |
| Ucars | ucars.es | `[V]` **DNS does not resolve** (`ucars.com` is an unrelated generic shell) | — | MISSING — **UNREACHABLE** (no live ES host) |

### 1.2 Other ES-serving B2B / auction operators found in the live sweep (not mandate-named)

Source: **AutoAuctionAtlas** "B2B Vehicle Auctions — Europe / Spain" directory `[V]` +
CarsBarter professionals list. Every operator that the directory flags as **serving Spain**:

| Operator | Domain | Nature | Stock surface | Verdict |
|---|---|---|---|---|
| Alcopa Auction ES | alcopa-auction.es | B2B auction (ES branch of the Alcopa group) | `[V]` listing host **405 / WAF** to a plain fetch; B2B | MISSING — GATED (WAF + B2B) |
| Northgate Trade / VO | vo.northgate.es | fleet/commercial remarketer (ZIGUP) | `[V]` 200 root but listing paths 404; login-shaped | MISSING — GATED (no public catalog path) |
| Veiko | veiko.es | ES used-car / auction site | `[V]` 200 SSR, `coche` markers, login+registr present | MISSING — partial SSR; bidding/portal login-shaped (deferred, not a clean free catalog) |
| LocalizaVO | localizavo.es | Localiza (rent-a-car) VO remarketing | `[V]` 200, login+registr markers | MISSING — VO remarketing; overlaps the rentacar_vo front, login-shaped |
| 2ndMove by Europcar | b2b.2ndmove.eu | Europcar fleet remarketing | `[A]` B2B-only per directory | MISSING — GATED (B2B fleet) |
| Tartiere B2B | tartiereb2b.com | dealer-group B2B remarketing | `[A]` B2B per directory | MISSING — GATED (B2B) |
| Copart Spain | copart.es | salvage/damaged-vehicle auction | `[A]` member/login auction (salvage, not standard VO) | MISSING — GATED + salvage (different vertical) |
| CarOnSale | caronsale.com | pan-EU dealer-to-dealer wholesale | `[V]` 200 but Next.js app, login-gated stock | MISSING — GATED (login wall) |
| AutoProff | autoproff.com | Nordic/EU dealer auction | `[A]` B2B login | MISSING — GATED (B2B, not ES-primary) |
| Autobid.de (Auktion & Markt) | autobid.de | DE-centric B2B auction specialist | `[A]` B2B login; DE-primary | MISSING — GATED (B2B, DE-primary) |

> Note: `subastacar.com` is the **only** operator in this entire universe (mandate-named +
> directory) whose **full car stock is enumerable anonymously via a free vector** — every
> other reachable B2B operator gates the catalog behind a professional/dealer login, and the
> remaining names either do not resolve or are a different vertical (salvage / French import).

---

## 2. What was CONNECTED this run — Subastacar

**Connector:** `pipeline/platform/subastacar_wholesale.py` (mirrors the proven
dual-membership template `group_subastas_wholesale` / `coches_net_wholesale` exactly).

**Surface (verified live 2026-06-13):**
- **Listing:** `GET https://www.subastacar.com/coches-segunda-mano-ocasion/?pagina=N` → 200
  text/html, server-rendered, ~21 vehicle detail anchors/page, paginated `?pagina=N`.
  Site declares **"238 resultados en 12 Páginas"** — the EXACT denominator.
- **Detail:** each detail page embeds a schema.org **`vehicle` JSON-LD** block we parse
  (not brittle DOM): `brand.name`, `model`, `vehicleIdentificationNumber` (VIN),
  `mileageFromOdometer.value`, `dateVehicleFirstRegistered`, `vehicleEngine.fuelType`,
  `vehicleTransmission`, `bodyType`, `color`, `image[].url`, and **`price` (an explicit
  asking price)** — richer than the bid-gated Ayvens lot (whose price is NULL).
- **Access:** fully public to an anonymous `curl_cffi` chrome131 GET. A "solo profesionales"
  login exists for an iframe bidding portal, but the **stock itself is fully public**.
  `defense_tier=t0_open`, `website_waf=none`, `is_tier1=FALSE`, `data_surface=json_ld`.

**Data model:** Subastacar is a single auction marketplace (no calendar of discrete sale
events), so the selling point is the platform-as-auction-house — ONE national entity
`kind='subasta'` (province NULL), every car owned by it; the platform entity carries the
`platform_listing` edge. No per-lot dealer/province exists on this surface; none fabricated.

**Run result (live, 2026-06-13):**

| metric | value |
|---|---|
| site declared total | 238 |
| detail links seen | 233 |
| details fetched | 233 |
| JSON-LD parse failures | 0 |
| cars caged | **233** |
| new cars | 233 |
| platform edges | 233 |
| NEW delta events | 233 |
| count verdict | **TRUSTWORTHY** (233 vs 238, within 10% tolerance) |

**Field completeness (my DB query, 233 cars):** make 233/233 · year 233/233 · km 233/233 ·
**price 233/233** · fuel 233/233 · transmission 233/233 · VIN 233/233 · photo 233/233 —
**100% on every field.**

**Idempotency:** re-run adds 0 new cars / 0 new edges / 0 new events (ON CONFLICT path).

---

## 3. Honest holes (genuinely-unreachable-free)

The mandate's "mejor confesar hueco que vender mentira" — declared straight:

- **AUTO1, OPENLANE/Adesa, Manheim ES, Alcopa, 2ndMove, Tartiere, CarOnSale, AutoProff,
  Autobid, Northgate** — all **GATED**: the car stock requires a verified professional /
  dealer login (these are B2B-only wholesale remarketers by design). No free anonymous
  catalog vector exists; connecting them would require fabricated credentials, which is
  forbidden. Reachable only behind paid/credentialed access.
- **Aucto (aucto.es), Ucars (ucars.es)** — **UNREACHABLE**: DNS does not resolve from here;
  no live host to connect.
- **EpicAuctions, Carmen** — **UNREACHABLE / not real ES auction operators**: no identifiable
  Spanish car-auction platform resolves under either name. Confessed as a hole, not faked.
- **Reezocar** — **OUT OF SCOPE**: a French consumer car-import/sourcing aggregator, not a
  Spanish B2B auction; no public ES auction stock surface.
- **Copart Spain** — GATED + a different vertical (salvage/damaged auctions, member login).
- **Veiko, LocalizaVO** — partial SSR but bidding/portal is login-shaped and LocalizaVO
  overlaps the existing `rentacar_vo` front; deferred, not a clean free standard-VO catalog.

---

## 4. Sources

- AutoAuctionAtlas — B2B Vehicle Auctions Europe / Spain directory `[V]`
  (autoauctionatlas.com/platforms/region/europe/)
- Ganvam — AUTO1 / Adesa professional-auction coverage `[V]`
- OPENLANE / Adesa — openlane.eu, cms.adesa.eu `[V]`
- AUTO1.com `[V]`, Manheim.es `[V]`, Alcopa-auction.es `[V]`, Subastacar.com `[V]`
- Live `curl_cffi` chrome131 probes of every domain above, 2026-06-13.
