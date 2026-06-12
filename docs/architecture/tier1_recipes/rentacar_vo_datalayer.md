# rentacar_vo — data-layer recipe

**source_group**: `rentacar_vo`
**Connector**: `pipeline/platform/group_rentacar_vo_wholesale.py`
**Verified LIVE**: 2026-06-13
**Status**: PRIMARY MEMBER (OK Mobility) drained end-to-end, VAM TRUSTWORTHY.

The group is rent-a-car operators that liquidate their **own ex-fleet** used cars through a
dedicated used-stock storefront. The car a buyer purchases is sold by the rent-a-car **company**
itself, so the company is the selling point: it is caged as the entity and OWNS every ex-fleet car,
exactly as a marketplace's dealer owns its cars.

---

## Member 1 — OK Mobility (PRIMARY, drained)

| Field | Value |
|---|---|
| Domain | `okmobility.com` |
| Legal / trade name | OK Mobility Group / OK Mobility |
| `entity_ulid` | `01KTZ236CWY3DYGVQ5KRHN3F3T` |
| `cdp_code` | `CDP-ES-07-KWGRMQ7B` |
| `kind` | `rent_a_car_vo` |
| `source_group` | `rentacar_vo` |
| `role` | `chain` |
| `defense_tier` | `t1_soft` (public site carries an Opticks bot beacon; the listing HTML is unwalled) |
| `is_tier1` | `FALSE` |
| HQ province | `07` (Palma de Mallorca, Illes Balears) |
| `data_surface` | `sitemap` (schema literal) / intent `ssr_html_embedded_card_markup` |
| `source_key` | `group_rentacar_vo_okmobility` |

### Access

OPEN server-rendered HTML. A Chrome TLS fingerprint (`curl_cffi impersonate=chrome131`) over
`GET https://okmobility.com/en/buy-car/used?page=N` returns the same markup the browser renders.
No browser, no proxy, no cookie warm-up.

- The **`/en/`** locale serves HTTP 200; **`/es/`** 404s on this surface.
- The public site fires an `opticksprotection.com` bot beacon (XHR), but the listing HTML itself is
  not gated — a plain governed GET succeeds. Hence `defense_tier=t1_soft`, not `t0_open`.

### Enumeration

`?page=1..N`, ~35 cars per SSR page. `<span id="total-cars">172</span>` declares the full stock.
6 pages cover the whole storefront; the data boundary is a page with zero cards.

### Data surface — per-card SSR markup

Each car is an `<a class="own-car-card" data-carid="N" data-carProgicielId="M" href="…">` block:

| Target field | Source |
|---|---|
| `deep_link` | `a.own-car-card` href → `/en/buy-car/used/{brand}/{model}/{trim}/{sku}/{id}` (absolute) |
| `listing_ref` | `data-carid` (internal OK Mobility car id; stable cross-run dedup key) |
| `progiciel_id` | URL tail id / `data-carProgicielId` (stock id) |
| make / model | `div.car-name` (make = first token; model = remainder; two-token makes handled) |
| `version` | `div.car-motorization` (e.g. `1.0 TSI 95`) |
| year / km / fuel / transmission | `div.car-summary` spans `[year | km | fuel | transmission]` |
| `price` | `div.paying-prices div.big-cipher-text` (ES thousands → integer euros) |
| `prev_price` | `div.deleted-small-cipher-text` (previous price → **price-drop delta**, gold for delta) |
| `photo_url` | `div.car-image[data-srcbg]` (`cdn.okrentacar.es` — the ex-rental fleet CDN, proof of origin) |

Encoding: decode the response as UTF-8 (the `€` glyph is UTF-8 over the wire; price digits are clean).

### Ownership model

OK Mobility is a single-operator storefront, so it has exactly ONE selling entity (the company).
The owning entity and the platform entity are the **same row**: `vehicle.entity_ulid = company`,
and the `platform_listing` edge (`company ↔ vehicle`) records the listing url/ref/price. The same
physical car could also carry a coches.net/AS24 edge (OK Mobility also lists on coches.net) without
changing its owner here.

**Per-branch attribution is deferred, not fabricated.** The listing surface does NOT attribute a car
to a showroom branch, so the company anchors to its HQ province (07) and owns the car. The detail
page (PDP) carries `<input name="store" value="…"/>` and OK Mobility's branch network is finite:

- Palma / Mallorca: Gran Vía Asima (07009), Levante (07007), Manacor (07500)
- Barcelona: El Prat, Calonge (08)
- Bilbao: Sestao (48910)
- Cuenca (16004)
- Jaén (23009)

A future per-branch pass can split ownership by draining the PDP `store` id; the network is recorded
in the recipe so no branch identity is invented now.

### Harvest proof (2026-06-13, `--pages 6`)

| Metric | Value |
|---|---|
| declared full (source) | 172 |
| items seen | 172 |
| dup ids collapsed (cross-page) | 6 |
| cars caged | **166** (166 new on first run) |
| platform_listing edges | **166** |
| NEW delta events | **166** |
| price drops captured | **163** |
| VAM verdict | **TRUSTWORTHY** (db_edges = db_join_vehicles = harvested_cageable = 166) |
| health / breaker | healthy / closed |
| idempotency re-run | 0 new vehicles, 0 new edges, 0 new events |

---

## Further members (same architecture, to be added)

| Company | Surface | Notes |
|---|---|---|
| Centauro | `centauro.net/comprar-coche-segunda-mano/disponibilidad/` | Next.js app; needs an XHR probe to find the JSON endpoint |
| Record Go | `recordgoocasion.es/coches/segunda-mano/` | WordPress dealer-CMS; sitemap (`stock_listing_0-sitemap.xml`) + SSR PDP; ~18 live cars, per-car city in the URL (`/{city}/{brand}/{model}/…`) |
| Sixt / Europcar / Goldcar | TBD | Probe each used-stock surface; cage under the same `rentacar_vo` group, one company entity each |

Each member is one more company entity (`kind=rent_a_car_vo`, `source_group=rentacar_vo`) flowing
through the ONE wholesale architecture — not a fork of it.
