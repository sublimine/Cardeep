# 03 · DESCUBRIMIENTO — los arneses de hallazgo de puntos de venta (validados)

> **DESCUBRIR** es la primera fase del E2E (`DESCUBRIR→SCRAPEAR→RECETA→API→DELTA`). No scrapea
> stock: **encuentra entidades** (puntos de venta) que aún no están en el censo y las da de alta
> idempotentemente (`entity` + `entity_source`). Este capítulo documenta los **métodos de
> descubrimiento validados** — no son conectores de plataforma, son herramientas que pueblan el
> censo. Regla dura del runbook: cada cifra de aquí se re-derivó de la DB viva esta sesión
> (`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`, **2026-06-13**), no del log del
> harness. Lo intentado-sin-commit o amurallado va a [NOT-VALIDATED.md](NOT-VALIDATED.md).

---

## 0 · Invariante común de descubrimiento

Todos los arneses comparten la **misma espina**, no es un fork:

1. **Índice de dedup contra el censo vivo** antes de escribir nada. Se construye desde
   `SELECT trade_name, legal_name, website, municipality_code, province_code FROM entity` (todo el
   censo). Escalera de coincidencia: **(1) host pelado → (2) `nombre-normalizado|municipio` → (3)
   nombre+provincia**. Helpers reutilizables en `scripts/associations/dedup_upsert.py`
   (`DedupIndex`, `GeoResolver`, `bare_host`, `cdp_code`, `ulid`), consumidos también por el frente
   `paginas_amarillas` — una sola arquitectura.
2. **Upsert idempotente**: el `cdp_code` es inmutable y derivado de la identidad canónica
   (host registrable > nombre+municipio+dirección). Un duplicado **no** crea segunda entidad: se le
   adjunta la fuente como `entity_source` corroborante (procedencia), no inventario.
3. **Geo a INE** (provincia/municipio) por dirección libre o pista de provincia; sin geo resoluble y
   sin host → se descarta, no se inventa.
4. **Toda cifra se re-cuenta desde la DB** (VAM): el número del runbook nunca es el del log.

`source_group` etiqueta el origen del hallazgo (`association`, `geo_sweep`); `kind_source`
(`legal_census`) marca la naturaleza de la fuente; `status='unverified'` hasta que una receta de
stock confirme inventario propio.

---

## 1 · Association-mining (`source_group='association'`) — +409 puntos de venta

Minado de los **directorios oficiales de asociaciones** del sector del automóvil en España. Solo se
minan las listas de socios **públicamente enumerables**; las amuralladas se declaran y se excluyen
(sin fabricar).

### 1.1 Asociaciones enumerables (minadas)

| Asociación | Tipo | Listado público | Miembros | Mecanismo de extracción |
|---|---|---|---:|---|
| **AEDRA** | desguaces / CATs | `aedra.org/buscador-de-socios/` | 615 | WP Directorist: lista HTML paginada + página-detalle por socio (dirección embebida en Google Maps) |
| **ACEVAS** | concesionarios VW/Audi/Škoda | `acevas.com/concesionarios/` | 99 | Super Store Finder, feed XML WP (`ssf-wp-xml.php`) |
| **AECS** | concesionarios Stellantis (Opel/Peugeot/Citroën/Fiat/Leapmotor) | `asociacionstellantis.com/directorio-asociados/` | 74 | HTML estático Elementor (triples nombre→provincia→web) |

→ `kind`: AEDRA = `desguace`; ACEVAS/AECS = `concesionario_oficial`.

### 1.2 Asociaciones AMURALLADAS (probadas y excluidas — NO en el censo)

`Faconauto` (~2.018 dealers, solo gateway) · `GANVAM` (~7.500 firmas, herramientas tras login) ·
`ANCOVE` ("contenidos sólo para afiliados") · `ANCOPEL` (página `concesionarios-asociados` da 404 en
vivo) · `AECS zona-asociados` (auth-walled; el `directorio-asociados` público SÍ se minó). Detalle y
evidencia en [NOT-VALIDATED.md](NOT-VALIDATED.md) §7.

### 1.3 Micro-acciones (paso a paso)

1. **AEDRA** `aedra_scrape.py`: crawl de la lista WP Directorist paginada + GET de cada
   página-detalle → nombre, web, teléfono, dirección cruda. Persiste `aedra_members.json`.
2. **ACEVAS** `parse_acevas.py`: GET del feed XML `ssf-wp-xml.php` → nombre, web, email, dirección,
   CP, provincia. Persiste `acevas_members.json`.
3. **AECS** `parse_aecs.py`: parse del HTML Elementor estático → nombre, provincia, web. Persiste
   `aecs_members.json`.
4. `upsert_associations.py` normaliza los tres a un record común y aplica la escalera de dedup contra
   el censo vivo; geo por `geo_from_address.py` (dirección ES libre → INE prov/muni). Inserta solo lo
   nuevo (`--commit`); a los dupes les adjunta la asociación como `entity_source`.
5. Cada número se re-deriva contando la DB.

### 1.4 Resultado VAM (re-contado en la DB viva)

| métrica | valor | reconciliación DB `[VERIFICADO]` |
|---|---:|---|
| records de entrada (aedra+acevas+aecs) | 788 | report `records_in=788` |
| **entidades NUEVAS (commit)** | **409** | `count(entity WHERE source_group='association')` = **409** |
| — desguace (AEDRA) | 346 | `first_discovered_source='aedra'` = 346 |
| — concesionario_oficial (AECS) | 36 | `first_discovered_source='aecs'` = 36 |
| — concesionario_oficial (ACEVAS) | 27 | `first_discovered_source='acevas'` = 27 |
| dupes (host 20 + name+muni 201 + name+prov 132) | 353 | adjuntados como `entity_source` corroborante |
| skip sin provincia (sin dirección resoluble) | 26 | descartados, no inventados |
| `entity_source` corroborantes vivos | aedra 586 · acevas 98 · aecs 68 | dupes + nuevos por fuente |

> 346 + 36 + 27 = **409** ✓ ; dup 353 + new 409 + skip 26 = 788 ✓ (cuadra al dígito).

### 1.5 Cosecha de stock propio derivada (DealerK own-site, +327 coches · VAM TRUSTWORTHY)

5 de los concesionarios AECS nuevos corren su web propia sobre la familia **DealerK/MotorK** (ya
documentada en [family-dealerk-wp](platforms/family-dealerk-wp.md)). El conector de familia existente
los cosechó sin receta nueva — el descubrimiento **multiplicó** directamente a inventario:

| dealer | host | `first_discovered_source` | coches (DB) |
|---|---|---|---:|
| DIMOLK AUTOMOCIÓN | grupodimolk.com | aecs | 180 |
| AUTOCIBA | autociba.es | aecs | 57 |
| ESLAUTO AUTOMOCIÓN | hervimotor.com | aecs | 56 |
| BETULA CARS | betulacars.es | aecs | 22 |
| DANIEL ROVIRA | danielrovira.net | aecs | 12 |
| **TOTAL** | — | — | **327** |

`[VERIFICADO]` Σ coches sobre estos 5 dealers (todos `source_group='association'`) = **327**, firmado
por **verdict id=609 TRUSTWORTHY** (`family_slice family_dealerk_wp`, `db_family_vehicles == harvested_pairs
== cars_ingested_distinct == 327`, `divergence=0.0`). AEDRA (desguaces) no aporta stock VO own-site
(venden piezas, no coches) → cero cosecha, por diseño.

### 1.6 Scripts / CLI (reproducible)

```bash
# Parsers de fuente (escriben los *_members.json):
python scripts/associations/aedra_scrape.py
python scripts/associations/parse_acevas.py
python scripts/associations/parse_aecs.py
# Dedup + alta idempotente (dry-run sin flag; escribe con --commit):
CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep \
  python scripts/associations/upsert_associations.py --commit
# Cosecha del stock propio (familia DealerK ya validada):
python -m pipeline.platform.family_dealerk_wholesale --dealers grupodimolk.com autociba.es \
  hervimotor.com betulacars.es danielrovira.net
```

Report del frente: `docs/research/associations/upsert_report.json` (`committed: true`).

---

## 2 · Barrido geográfico (`source_group='geo_sweep'`) — +68 dealers

Busca el **"garaje perdido"**: pequeños puntos de venta locales (compraventa, concesionario, coches
ocasión, desguace) ausentes de los marketplaces grandes y del censo previo, vía búsqueda web por
provincia a la **web propia** de cada negocio.

### 2.1 Micro-acciones (paso a paso) — `scripts/geo_sweep_collect.py`

1. **Búsqueda geográfica por provincia** (52 provincias + grandes ciudades) con las rúbricas
   concesionario / compraventa / coches ocasión / desguace vía WebSearch (resultados tipo
   Places + web general), capturando nombre + municipio + web propia → `candidates_batch{1..4}.json`.
2. **Dedup duro** de cada candidato contra el censo vivo (`_dedup_index.json`): (a) host pelado ya en
   DB → descartado; (b) `nombre+municipio` normalizado ya en DB → descartado. Solo pasa lo nuevo.
3. **Sonda de web propia** (`curl_cffi` `chrome131`): home + slugs de listado rankeados
   (`/coches`, `/vehiculos-ocasion`, `/stock`, …); **cosechable = ≥3 tokens de precio** en alguna
   superficie de listado (umbral `MIN_PRICE_TOKENS=3`).
4. **Upsert idempotente** entity + entity_source (`source_key='geo_sweep'`,
   `first_discovered_source='geo_sweep'`); geo a INE; `cdp_code` inmutable.
5. Cada cifra se re-cuenta desde la DB.

### 2.2 Resultado VAM (re-contado en la DB viva)

| métrica | valor | reconciliación DB `[VERIFICADO]` |
|---|---:|---|
| **dealers NUEVOS distintos** | **68** | `count(entity WHERE first_discovered_source='geo_sweep')` = **68** |
| — compraventa | 59 | por `kind` |
| — desguace | 7 | por `kind` |
| — concesionario_oficial | 1 | por `kind` |
| — garaje | 1 | por `kind` |
| `entity_source` `geo_sweep` | 68 | == nuevas (el dedup salta los conocidos) |
| colisiones de host con preexistentes | 0 | dedup limpio |
| con web propia accesible | 51 / 68 | sonda `curl_cffi` |
| con web propia **cosechable** (≥3 tokens precio) | 40 / 68 | listas para receta per-dealer |
| cobertura | 36 provincias | con ≥1 dealer nuevo |

> 59 + 7 + 1 + 1 = **68** ✓.

### 2.3 CLI (reproducible)

```bash
CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep \
  python scripts/geo_sweep_collect.py docs/research/geographic/candidates_batch1.json
```

Reports: `docs/research/geographic/FRONT_discover_geographic.md` + `candidates_batch{1..4}_processed.json`.

---

## 3 · Qué NO entra (descubrimiento intentado, fuera del runbook)

- **`paginas_amarillas` / discover_directories** — corrió en **DRY-RUN** (`committed: false`,
  new=62 propuestas) pero **NO se commiteó**: `count(entity WHERE first_discovered_source='paginas_amarillas')`
  = **0** en la DB viva. Sin escritura no hay unidad validada → [NOT-VALIDATED.md](NOT-VALIDATED.md).
- **Asociaciones amuralladas** (Faconauto/GANVAM/ANCOVE/ANCOPEL): sin lista pública enumerable.
- **Cierre geográfico al 100 %** del denominador (~44k suelo Páginas Amarillas): el sweep es por
  muestreo de capital + 2ª/3ª ciudad, no censo exhaustivo. La vía de cierre (dumps geo legales
  Foursquare/Overture + PA por rúbrica) está catalogada pero **pendiente**.

Detalle con evidencia en [NOT-VALIDATED.md](NOT-VALIDATED.md) §7.
