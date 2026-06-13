# Front: discover_associations — Closing Report

Mined the official Spanish dealer-association + sector directories for car
points-of-sale not yet in cardeep-pg. All counts below are VAM-verified by direct
query against `postgres://cardeep@localhost:5433/cardeep`.

## Sources mined (publicly enumerable member lists)

| Association | Type | URL | Members found | Mechanism |
|---|---|---|---|---|
| **AEDRA** | desguaces / CATs | https://aedra.org/buscador-de-socios/ | 615 | WP Directorist, paginated HTML list + per-member detail page (Google-Maps-embedded address) |
| **ACEVAS** | concesionarios VW/Audi/Skoda | https://www.acevas.com/concesionarios/ | 99 | Super Store Finder WP XML feed (`ssf-wp-xml.php`) |
| **AECS** | concesionarios Stellantis (Opel/Peugeot/Citroën/Fiat/Leapmotor) | https://asociacionstellantis.com/directorio-asociados/ | 74 | static Elementor HTML (name→province→website triples) |

Raw harvests persisted: `aedra_members.json`, `acevas_members.json`,
`aecs_members.json`, `acevas_raw.xml`, `aecs_raw.html`.

## Sources confirmed WALLED / not enumerable (no fabrication)

- **Faconauto** (federation, ~2.018 dealers): no public member list; gateway only.
- **GANVAM** (~7.500 firms): member tools behind login; no public directory.
- **ANCOVE** (compraventa nacional): "contenidos sólo para afiliados" — walled.
- **ANCOPEL** (Opel): `concesionarios-asociados` page returns 404 live; map widget gone.
- **AECS members-zone** (`zona-asociados.*`): auth-walled (the public
  `directorio-asociados` WAS mined — 74 dealers above).

These were probed and honestly excluded rather than guessed.

## Dedup (mandate ladder, against LIVE entity table)

`DedupIndex` built from all 367.8k existing entities. Ladder:
1. bare-host website  2. normalized name + municipality_code  3. name + province.
Dupes get the association attached as a corroborating `entity_source` (provenance),
not a second entity. Reusable helpers in `scripts/associations/dedup_upsert.py`
(also consumed by the paginas_amarillas front — one architecture, no fork).

- records in: 788
- **new: 409** · dup: 353 (host 20, name+muni 201, name+prov 132) · skip_no_province: 26
- 26 skips = AEDRA members whose detail page carried no address at all (unresolvable
  without inventing geo — skipped, not faked).

## Result (VAM-verified in DB)

- **NEW entities: 409**  (desguace 346 [AEDRA], concesionario_oficial 63 [AECS 36 + ACEVAS 27])
- **NEW cars: 327**  harvested from 5 of the new AECS dealer OWN-sites via the
  existing DealerK family connector (VAM verdict TRUSTWORTHY).
- own-site websites attached: 111 (75 AEDRA + 36 AECS)
- association `entity_source` rows: 752 (409 new + 343 corroborating on existing dupes)
- `source_group='association'`, `kind_source='legal_census'`, `status='unverified'`

### Own-site harvest detail (DealerK family, one recipe → N dealers)
gruporojasautomocion.com 57 (re-attributed to AUTOCIBA — autociba.es 301-redirects
there; orphan host-entity merged, gruporojas kept as `domain` alias),
grupodimolk.com 180, hervimotor.com 56, betulacars.es 22, danielrovira.net 12.
AEDRA members are vehicle dismantlers (parts, not VO stock) → no own-site car harvest.

## Scripts (this front)

- `scripts/associations/dedup_upsert.py` — DedupIndex + GeoResolver + upsert helpers
- `scripts/associations/geo_from_address.py` — free-form ES address → INE prov/muni
- `scripts/associations/aedra_scrape.py` — AEDRA list+detail crawler
- `scripts/associations/parse_acevas.py` / `parse_aecs.py` — feed parsers
- `scripts/associations/upsert_associations.py` — dedup + commit (`--commit`)
- report: `scripts/associations/.../upsert_report.json`
