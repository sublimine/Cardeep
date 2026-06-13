# FRONT discover_geographic — parte de entrega

> Barrido geográfico del "garaje perdido": pequeños puntos de venta locales
> ausentes de los marketplaces y del censo previo. Verificado por consulta
> propia a la base de datos (VAM). Fecha: 2026-06-13.

## Método

1. **Dedup duro contra el censo vivo** antes de añadir nada. Índice construido
   desde `SELECT trade_name, legal_name, website, municipality_code, province_code
   FROM entity` (367.686 entidades de partida): 1.133 hosts pelados + 231.080
   claves `nombre-normalizado|municipio`. Persistido en `_dedup_index.json`.
2. **Búsqueda geográfica por provincia** (52 provincias + grandes ciudades) con
   las rúbricas concesionario / compraventa / coches ocasión / desguace vía
   WebSearch (resultados tipo Google/Bing Places + web general), capturando
   nombre + municipio + web propia.
3. **Dedup de cada candidato**: (a) host pelado ya en DB → descartado;
   (b) `nombre+municipio` normalizado ya en DB → descartado. Solo pasa lo
   genuinamente nuevo.
4. **Sonda de web propia** (`curl_cffi` chrome131): home + slugs de listado
   rankeados; cosechable = ≥3 tokens de precio en alguna superficie de listado.
5. **Upsert idempotente** entity + entity_source (`source_key=geo_sweep`,
   `first_discovered_source=geo_sweep`), geo a INE provincia/municipio, cdp_code
   inmutable derivado de la identidad canónica (host > nombre+municipio).

Harness: `scripts/geo_sweep_collect.py`. Candidatos crudos en
`candidates_batch{1..4}.json`; resultados procesados en
`candidates_batch{1..4}_processed.json`; entidades nuevas verificadas en
`_new_entities_verified.json`.

## Resultado (VAM — contado desde la propia DB)

- **68 dealers nuevos distintos** añadidos (`first_discovered_source=geo_sweep`),
  todos con web propia. Cero colisiones de host con entidades preexistentes.
- **51 de 68** con web propia accesible; **40 de 68** con web propia
  COSECHABLE (≥3 tokens de precio + slug de listado identificado), listas para
  receta de stock per-dealer.
- Cobertura: **36 provincias** con al menos un dealer nuevo.
- Por tipo: compraventa 59 · desguace 7 · concesionario_oficial 1 · garaje 1.

### Verificación de no-duplicación
- `entity` total: 367.686 → 367.798 (delta incluye otros frentes en paralelo).
- `entity_source` para `geo_sweep`: 68 (== nuevas; el dedup salta los conocidos).
- Colisiones de host geo_sweep ↔ preexistentes: **0**.

## Confesión honesta de huecos (sin maquillaje)

- El barrido es por **muestreo de capital + 2ª/3ª ciudad por provincia**, no un
  censo exhaustivo del long-tail. WebSearch devuelve la primera página por
  consulta; quedan pueblos pequeños sin barrer. Para cierre al 100% del
  denominador (~44k suelo PA) la vía correcta es ingerir los dumps geo legales
  (Foursquare OS Places Apache-2.0, Overture CDLA) + Páginas Amarillas por
  rúbrica — fuera del alcance de este frente, ya catalogados en `SOURCES_ES.md`.
- **Google Places API NO usado**: su ToS prohíbe indexar/cachear (riesgo legal
  declarado en el censo). El sustituto legal son FSQ/Overture + búsqueda web a
  web propia, que es lo aplicado aquí.
- **Enriquecimiento detectado (no es nuevo, pero es oro):** ~20 candidatos
  deduplicados por `nombre+municipio` resultaron ser dealers YA en el censo vía
  marketplaces pero con `website IS NULL`. El sweep encontró su web propia →
  oportunidad de back-fill de `website` para habilitarles cosecha de stock
  propio. No ejecutado (mi KPI es dealers nuevos), pero registrado.
