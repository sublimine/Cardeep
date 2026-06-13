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

## Member 2 — Centauro (DRAINED 2026-06-13)

| Field | Value |
|---|---|
| Domain / website | `centauro.net` |
| `cdp_code` | `CDP-ES-03-BMPR08V3` |
| HQ province / muni | `03` Alicante / `03014` |
| Surface | `https://ventas.centauro.net/coches-ocasion/?pagina=N` (fully SSR; NOT the React `centauro.net/comprar-coche…/disponibilidad` app, which loads from `content-api.centauro.net` client-side) |
| Card data | per-card `<form>` hidden inputs: `precio`, `precioNuevo` (factory-new → ex-fleet discount delta), `kilometros`, `marcaVehiculo`, `modeloVehiculo`, `mesesAntiguedad` (→ year); version from the ficha URL slug; photo `images.motorflash.com`/`media.staticmf.com` |
| Enumeration | `?pagina=1..N`, 12 cars/page, declares `28 coches`. Pages past the last CLAMP-REPEAT (re-serve the tail), so the drain stops on a window with 0 new distinct cars |
| Caveat | fuel/transmission only on the PDP → left NULL (never faked). Year derived from age-in-months (current_year − round(months/12)); month/day not claimed |
| Harvest | **28 cars caged = 28 edges = 28 join-vehicles = 28 NEW events. VAM TRUSTWORTHY.** Re-run: 0 new |

## Member 3 — Record Go (DRAINED 2026-06-13)

| Field | Value |
|---|---|
| Domain / website | `recordgoocasion.es` |
| `cdp_code` | `CDP-ES-12-H26EC1KD` |
| HQ province / muni | `12` Castellón / `12040` (Castelló de la Plana) |
| Surface | `https://www.recordgoocasion.es/coches/segunda-mano/?page=N` (DealerK/MotorK WordPress, `cdn.dealerk.es`, `vcard-*` classes — the SAME CMS family `family_dealerk_wholesale` harvests; its `parse_cards` reads it byte-for-byte) |
| Enumeration | `?page=1..N` (15/page then 3 on page 2 = 18; page 3 empties → clean boundary). The Yoast `stock_listing_0-sitemap.xml` is EMPTY → harvest the listing page, not the sitemap. `/page/2/` 404s; `?pagina=` is ignored — only `?page=` paginates |
| Per-car URL | `/coches/segunda-mano/{city}/{brand}/{model}/{fuel}/{trim}/{id}/` |
| Harvest | **18 cars caged = 18 edges = 18 join-vehicles = 18 NEW events. VAM TRUSTWORTHY.** Re-run: 0 new |

## Gaps — confessed, NOT fabricated (probed live 2026-06-13)

| Company | Verdict |
|---|---|
| Sixt ES | NO Spanish used-car storefront. `sixt.es` sitemaps = ride/magazine only; `/coches-ocasion`,`/gw` 404. Sixt's used-car ("GW") business is DE-only (`sixt.de`). No ES surface to harvest. |
| Europcar ES | Ex-fleet ("2nd Move") sold ONLY via the registration-gated B2B platform `2ndmove.es → b2b.2ndmove.eu` (`/es/register`, professionals only; `/es/vehicles`,`/es/search` 404). `europcar.es/servicios/coches-segunda-mano` 404s. Its marketplace presence (`motorflash/coches.net europcar-second-hand`) is already covered by the marketplace connectors → caging it from there would double-count. |
| Goldcar | Europcar-group rental brand; sitemap (4,699 URLs) is ALL rental-location/app pages, zero used-car path. Ex-fleet sold via the same B2B 2ndMove platform. No public own-site surface. |

Each harvestable member is one more company entity (`kind=rent_a_car_vo`, `source_group=rentacar_vo`)
flowing through the ONE wholesale architecture — not a fork of it. Connector now multi-member:
`python -m pipeline.platform.group_rentacar_vo_wholesale --member {all|okmobility|centauro|recordgo}`.
