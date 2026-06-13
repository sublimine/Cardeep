# rentacar_vo — additional members probe (Centauro, Record Go, Sixt, Europcar, Goldcar)

**Front**: `rentacar_more` · **Probed LIVE**: 2026-06-13 · curl_cffi chrome131
**Connector**: `pipeline/platform/group_rentacar_vo_wholesale.py` (extends OK Mobility primary)

Goal: connect the remaining RENT-A-CAR VO fleets (sell ex-fleet used cars) as further
members of the existing `rentacar_vo` source_group, each one company entity
(`kind=rent_a_car_vo`), harvest its public used-stock surface, verify in DB.

Dedup check against `entity` (bare-host website + normalized name+municipality):
none of recordgo/centauro/europcar exist; the "Goldcars"/"Sixteen Negative" rows are
unrelated anonymized particulares/compraventas (no website) — all real companies below
are GENUINELY NEW entities.

---

## HARVESTABLE (own public used-stock surface) — 2 members

### Centauro (centauro.net) — SSR `ventas.centauro.net`
- **Surface**: `https://ventas.centauro.net/coches-ocasion/?pagina=N` (NOT the React
  `centauro.net/comprar-coche-segunda-mano/disponibilidad/` app, which loads cars from
  `content-api.centauro.net` client-side). `ventas.centauro.net` is a **fully server-rendered**
  storefront (1.16 MB HTML) — no browser, no API reverse-engineering needed.
- **Access**: OPEN. Chrome TLS fingerprint GET returns full markup. `defense_tier=t1_soft`.
- **Enumeration**: `?pagina=1..N`, 12 cars/SSR page. Page declares **28 coches** total
  (verified: page1=12, page2=12, page3=4 → 28 distinct; page4 repeats page3 tail = boundary).
- **Per-card data** (hidden `<input>` form fields + URL slug):
  - `deep_link`: `a href=/ficha-vehiculo-ocasion/{make-model-trim-slug}/{numeric-id}`
  - `listing_ref`: trailing numeric id (stable; e.g. `111199069`)
  - `marcaVehiculo` = make · `modeloVehiculo` = model · version from URL slug tail
  - `precio` = current price (int €) · `precioNuevo` = original price → **price-drop delta**
  - `kilometros` = km · `mesesAntiguedad` = age in months → year = current_year - round(months/12)
  - photo: `media.staticmf.com` / `images.motorflash.com` (motorflash own-stock CDN)
  - fuel/transmission NOT on the listing card (only on PDP) → left NULL (never fabricated)
- **HQ province**: Centauro HQ = Alicante (Pol. Industrial, Pais Valencia) → INE **03**.
- **Ownership**: single-operator storefront → company OWNS every car; `platform_listing` edge
  records the listing (same model as OK Mobility).

### Record Go (recordgoocasion.es) — DealerK WordPress (already a known family)
- **Surface**: `https://www.recordgoocasion.es/coches/segunda-mano/` — server-rendered.
- **CMS**: **DealerK / MotorK** (`cdn.dealerk.es/dealer/datafiles/vehicle`, `vcard-*` classes).
  The EXISTING `family_dealerk_wholesale.py` parser (`parse_cards`) reads it byte-for-byte:
  verified 15 cards parsed with make/model/year/km/price/fuel intact.
- **Access**: OPEN. `defense_tier=t1_soft`.
- **Enumeration**: single page; `<meta>` declares **18 coches** "desde 10.200 €".
  `/page/2/` 404s. The Yoast `stock_listing_0-sitemap.xml` is EMPTY (CMS not emitting per-car
  sitemap entries) → harvest the listing page, not the sitemap.
- **Per-car URL**: `/coches/segunda-mano/{city}/{brand}/{model}/{fuel}/{trim}/{id}/` — city, brand,
  model, fuel, trim and a stable numeric id all in the path.
- **HQ province**: Record Go Ocasión = Castellón de la Plana (Avda. Casalduch 61) → INE **12**.
  (Per-car city in URL: valencia/sevilla/malaga — recorded; cars still owned by the company.)
- **Ownership**: single-operator storefront → company OWNS every car; `platform_listing` edge.

---

## GAPS (no public own-site used-stock surface) — confessed, not faked

### Sixt ES — NO Spanish used-car storefront
- `sixt.es/robots.txt` sitemaps = only `ride-sitemap` + `magazine/*`. `sixt.es/sitemap.xml` empty.
- `/coches-ocasion/`, `/gw/` → 404. No `gw.sixt.es`. Sixt's used-car ("GW"/Gebrauchtwagen)
  business is **DE-only** (`sixt.de`); no ES public surface exists. → GAP (no ES VO surface).

### Europcar ES — used cars sold via B2B-gated 2ndMove only
- `europcar.es/servicios/coches-segunda-mano` and `/es-es/coches-ocasion` → **404** (landing gone).
- Europcar's ex-fleet ("2nd Move") sells through **`www.2ndmove.es` → `b2b.2ndmove.eu/es/home`**,
  a **registration-gated B2B** platform (`/es/register`, professionals only). No public browsable
  stock; `/es/vehicles` and `/es/search` → 404. → GAP (surface is login-walled B2B).
- Europcar second-hand cars DO surface on `motorflash.com/concesionario/europcar-second-hand`
  and milanuncios — but those are MARKETPLACE listings already covered by the marketplace
  connectors, not an own-site. Caging Europcar from a marketplace would double-count, so deferred.

### Goldcar — Europcar-group rental brand, NO own used-stock surface
- `goldcar.es/sitemap.xml` = 4,699 URLs, ALL rental-location/app pages; zero used-car sales path.
- Goldcar (Europcar Mobility Group) liquidates ex-fleet via the same B2B 2ndMove platform.
  "Goldcar Sales" appears only as a coches.net/motor.es dealer (marketplace). → GAP (B2B-gated).

---

## Result
2 new company entities added under `rentacar_vo` (Centauro + Record Go), each owning its
ex-fleet used stock. Sixt/Europcar/Goldcar confirmed to have NO public own-site used-stock
surface in ES (Sixt: none; Europcar+Goldcar: B2B-login-walled 2ndMove) — recorded as honest
gaps in the connector recipe, not fabricated.
