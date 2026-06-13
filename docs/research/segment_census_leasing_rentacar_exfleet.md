# Segment census — `leasing_rentacar_exfleet`

Family: **leasing / renting / rent-a-car operators that SELL their ex-fleet used cars in Spain.**
Scope: every operator that liquidates its own ex-fleet stock to the public through a
browsable used-stock surface, beyond Ayvens/OK Mobility. EXCLUDES social media (out of scope
by owner mandate). Verified LIVE 2026-06-13.

DB family today (`source_group='rentacar_vo'`, `kind='rent_a_car_vo'`): **OK Mobility, Centauro,
Record Go** — already caged by `pipeline.platform.group_rentacar_vo_wholesale`. Ayvens Carmarket
(B2B auctions) + BCA España are already in DB as `plataforma` (subastas, `official_registry`).

This census extends the SAME module with new members and confesses the genuinely-unreachable.

---

## Universe (every operator named, with disposition)

| Operator | Public ex-fleet used-stock surface | Vector | Disposition | Live count |
|---|---|---|---|---|
| **OK Mobility** | okmobility.com/en/buy-car/used | curl_cffi SSR | HAVE (in DB) | 172 |
| **Centauro** | ventas.centauro.net/coches-ocasion | curl_cffi SSR | HAVE (in DB) | 28 |
| **Record Go** | recordgoocasion.es/coches/segunda-mano | curl_cffi DealerK | HAVE (in DB) | 18 |
| **Arval (AutoSelect)** | autoselect.arval.es | curl_cffi JSON API | **NEW — CONNECTED** | **1172** |
| **Northgate Ocasión** | northgate.es/vehiculos-ocasion | curl_cffi JSON POST | **NEW — CONNECTED** | **108** |
| **Athlon Car Outlet** | athloncaroutlet.es/buscar-coches | Angular-hydrated (browser) | NEW — entity caged, drain deferred (browser-required) | 114 |
| **Ayvens used-cars B2C** | used-cars.ayvens.com/es-es/catalog | JSON API reachable | Reachable but **inventory empty (count:0)** — live channel is the B2B auction already in DB | 0 |
| **ALD Automotive** | = Ayvens (rebrand) | — | Same as Ayvens (ALD→Ayvens). Carmarket auctions already in DB | — |
| **Alphabet (BMW) Used Cars** | alphabet.com/.../alphabet-used-cars | online **auction**, pro-gated | Unreachable-free (auction, registration-gated). Appears in DB only as BCA subasta lots | n/a |
| **LeasePlan / CarNext** | (wound down) | — | Unreachable-free. CarNext shut B2C retail in ES/EU (2021→BCA); now pro auctions only | n/a |
| **Hertz Ocasión** | hertzocasion.es | landing page only | Unreachable-free. NO online stock; sale by phone/email (carsalesspain2@hertz.com) | n/a |
| **Sixt ES** | — | — | Unreachable-free. No ES used-car storefront (GW business is DE-only) | n/a |
| **Europcar ES** | — | — | Unreachable-free. Ex-fleet only via pro-gated 2ndmove.es / b2b.2ndmove.eu | n/a |
| **Goldcar** (Europcar grp) | — | — | Unreachable-free. Same disposal route as Europcar (pro auctions) | n/a |
| **Enterprise / Alamo / Avis** | — | — | Unreachable-free in ES. US-style "car sales" division has no public ES browsable stock | n/a |

---

## CONNECTED — recipe detail

### Arval AutoSelect — `autoselect.arval.es`  (NEW, curl_cffi JSON API)
- B2C used-stock storefront of Arval (BNP Paribas), Spain's largest ex-fleet seller
  (~2,500 cars/month; 150,000-car fleet). HQ Madrid.
- **API**: `GET https://arval-prod-euw-appservice-portalapi.azurewebsites.net/api/Announcements/4?pageNumber=N&pageSize=24`
  - returns `{announcements:{currentPageNumber, allAnnouncementsCount, allPageQuantity, announcements:[…]}, pageContent}`
  - `allAnnouncementsCount` declares full stock (**1172** live). 24 cars/page → 49 pages.
- **Per-car JSON**: `id`, `make`, `model`, `trim`, `salePriceGross`, `previousSalePriceGross`
  (price-drop delta), `details.mileage`, `details.registrationYear`, `details.fuelTypeLabel`,
  `details.gearbox`, `mainImage`, `offerUrl` (deep-link), `location`, `firstRegistrationDate`.
- Access: OPEN JSON (Chrome TLS fingerprint; no key/cookie). t1_soft.

### Northgate Ocasión — `northgate.es/vehiculos-ocasion`  (NEW, curl_cffi JSON POST)
- B2C used-stock of Northgate Renting (vans + cars), 40 own workshops nationwide. HQ Madrid.
- AEM site. The vehicle list is one POST returning the FULL array:
  - `POST https://www.northgate.es/content/northgate/es/vehiculos-ocasion/jcr:content.catalogsearch.html`
  - body `type[]=` (urlencoded) → JSON **array of 108** vehicles. Client paginates over the array.
- **Per-car JSON**: `id`, `brand`, `model`, `version`, `year`, `km`, `fuel`, `price`, `province`,
  `location`, `color`, `power`, `url` (deep-link `/vehiculos-ocasion/catalogo/…-{id}`), `imagePaths`.
- `{filter:""}` returns only price/km/type facet metadata; `type[]=` is the array trigger.
- Access: OPEN JSON POST (X-Requested-With). t1_soft. Per-car `province` gives true location.

---

## DEFERRED — reachable but browser-required

### Athlon Car Outlet — `athloncaroutlet.es/buscar-coches`  (Angular hydrate)
- Sales channel for Athlon (Daimler/Mercedes-Benz Mobility) ex-renting fleet. HQ store
  Santa Perpètua de Mogoda (Barcelona, 08) + Madrid. **114** cars (facets: 56 diesel + 27
  hybrid + 29 petrol + 2 EV). Already in DB as plain `compraventa` branches (no stock edge).
- Stack: Angular SPA at `occasions.services.athlon.com/es`; data via Athlon **IRT** API
  `services.athlon.com/api/irt/secured/employee/athloncaroutletes/{facets,search,info}`.
  `facets` GET works unauth (declares 114); the `search` POST uses an undocumented query DSL
  (all guessed bodies → 500) and the listing HTML is NOT in the raw curl response (client-rendered).
- **Deep-link pattern** (recovered from hydrated DOM): `https://www.athloncaroutlet.es/buscar-coches/{make}/{model}/{licensePlate}` — license plate is the stable per-car ref.
- DOM card (`.cardetail`): make+model, version, `MM-YYYY` reg, km, energy label, fuel,
  transmission, location, price, image AssetId.
- Disposition: entity caged in `rentacar_vo` with this recipe; the ex-fleet stock drain is
  deferred to a camoufox/Playwright hydrate pass (same browser-required tier the repo already
  reserves for hydrated SPAs), NOT faked from the empty static HTML.

---

## CONFESSED unreachable-free (honest gaps)
- **Ayvens/ALD B2C retail** (`used-cars.ayvens.com`): API authenticates fine
  (`x-ald-subscription-key=6b2007dc3a864fcea99040d8c3e72a69`, `x-country=es`, `x-tenant=ald-es`)
  but `vehicleads` returns `count:0` for ES (and FR/IT) — the B2C retail catalogue is dormant.
  Ayvens' live disposal is the **professional auction** at carmarket.ayvens.com, already in DB.
- **Alphabet Used Cars**: online auction, professional-registration-gated. No public browsable stock.
- **LeasePlan / CarNext**: B2C retail wound down (2021, folded into BCA); pro auctions only now.
- **Hertz Ocasión**: hertzocasion.es is a landing page; sale by phone/email, no online catalog.
- **Sixt ES**: no Spanish used-car storefront (used business is DE-only).
- **Europcar / Goldcar**: ex-fleet only through pro-gated 2ndmove.es / b2b.2ndmove.eu.
- **Enterprise / Alamo / Avis**: no public ES browsable ex-fleet stock surface.

Mejor confesar el hueco que vender una mentira: these are professional-auction or
phone/email channels with no free public stock vector — not a tooling failure.
