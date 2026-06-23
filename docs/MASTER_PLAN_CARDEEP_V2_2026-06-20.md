# PLANO MAESTRO CARDEEP · V2 — El Sistema de Descubrimiento como columna vertebral
**Fecha:** 2026-06-20 · **Autor:** Jefe Arquitecto + equipo de I+D (Director soberano de la misión) · **Estado:** deliverable documental de arquitectura. NO toca código.

> **Por qué existe esta V2.** La V1 (`docs/MASTER_PLAN_CARDEEP_2026-06-20.md`) auditó bien los subsistemas maduros (orquestación, VAM, identidad) pero cometió un error de encuadre fatal: **enterró el descubrimiento en un §4 de "Conectores/Adapters"** y nunca lo trató como lo que es — **el corazón del mandato**: "sellar el 100% de los puntos de venta de coches de España y DEMOSTRARLO con intervalo de confianza". Esta V2 reescribe el documento con el **SISTEMA DE DESCUBRIMIENTO** como §1, la sección más extensa y detallada, y degrada todo lo demás a su servicio. Lo que en V1 estaba bien auditado se conserva y se eleva; lo que estaba ausente —el sistema de descubrimiento multivector y el framework de exhaustividad demostrable— se diseña aquí desde cero a nivel átomo.

> **Marco estratégico (mandato del Director, vinculante e inalterado):**
> 1. Objetivo: por cada ENTIDAD → descubrir → scrapear muestra (k≈3-10 coches) → guardar receta/config → verificar (VAM) → borrar muestra. Ciclo **recipe-first / sample-verify-delete**.
> 2. Volcado masivo → VPS, **diferido** hasta verificación local total.
> 3. **Coste no es criterio** (todavía). Arsenal: Camoufox, nodriver, curl_cffi, proxies residenciales ES.
> 4. Antidetección **la más agresiva** del mercado, presente y de los próximos años.
> 5. **Corregir lo roto, elevar lo mejorable, reutilizar lo bueno.** No rediseño por rediseño.
> 6. **NUEVO eje rector de esta V2:** el descubrimiento no es "una fuente más"; es un **sistema de censo nacional** con denominador estadístico y certificado de cobertura por estrato. "Cubrir el 100%" sin medir el denominador es fe, no ingeniería.

> **Honestidad metodológica.** `[VERIFICADO]` = leído en fuente (código `archivo:línea` o documentación/URL citada). `[ASUMIDO]` = inferencia razonada no probada en vivo. Donde no se cerró una verificación, se declara el hueco. Procedencia: §0.4 Auditoría por agentes (lectura directa del repo) + investigación web SOTA con fuentes citadas (apéndice).

---

## §0 — RESUMEN EJECUTIVO

### 0.1 El diagnóstico en una frase

cardeep tiene un **back-end de datos y verificación de grado institucional** (clustering determinista verificado contra DB viva, scheduler crash-safe, doctrina VAM con quórum real, sample-and-delete a prueba de pérdida) **montado sobre un sistema de descubrimiento incompleto y, sobre todo, no demostrable**. Sabe procesar con honestidad lo que descubre; **no sabe aún cuántos dealers existen que no ha descubierto nadie**, y por tanto no puede certificar el 100%. Esta V2 ataca exactamente ese hueco: convierte el descubrimiento de una colección de 13 adaptadores sueltos en un **sistema de censo multivector con framework de exhaustividad (captura-recaptura multi-lista) que emite un % de cobertura con IC por provincia × tipo**.

### 0.2 El hallazgo que reordena todo el plan

**[VERIFICADO]** El "denominador verdadero" hoy es **incalculable con precisión**: `scripts/recon/b6_chapman_final.py:5-17` confiesa que el solapamiento entre las dos listas más ortogonales (OSM físico × Wallapop anuncios) es **m=10 canónicos globales** → IC de Chapman `[0, 303.679]`, inservible. Causa raíz triple: (a) **falta una tercera/cuarta lista verdaderamente ortogonal** (Overture, registro administrativo CNAE) que el sistema no ingiere; (b) el **cross-source dedup no está servido** (`cross-source-dedup-v1` vam_verified=FALSE, 50.497 in → 688 merged), así que las listas no se cruzan bien y el solapamiento real queda artificialmente bajo; (c) **el vector marketplace-as-census no existe** — Wallapop/Milanuncios solo cosechan inventario de dealers ya conocidos, no enumeran vendedores como entidades. Estos tres son los proyectos de cabecera de esta V2, y los tres viven en el **sistema de descubrimiento**, no en el back-end.

### 0.3 Matriz as-is → to-be (reordenada: descubrimiento primero)

| # | Subsistema | Nota AS-IS | Nota objetivo | Decisión | Hueco crítico (1 línea, con evidencia) |
|---|------------|:---:|:---:|---|---|
| **1** | **SISTEMA DE DESCUBRIMIENTO (censo multivector)** | **4/10** | **10/10** | **CONSTRUIR el sistema** | 13 adapters sueltos; **0 de los 6 vectores estratégicos completos**; sin marketplace-census; sin geo-grid; sin BORME/CNAE; sin grafo recursivo; PA fuera del pipeline (`scripts/discover_paginas_amarillas.py`). |
| **2** | **FRAMEWORK DE EXHAUSTIVIDAD (denominador + IC)** | **2/10** | **10/10** | **CONSTRUIR (lo que demuestra el 100%)** | Chapman m=10 → IC `[0, 303k]` inservible (`b6_chapman_final.py:5-17`); sin MSE multi-lista; denominador = techo registral, no estadístico. |
| 3 | Motor antidetección + transporte (Tier-1) | 4.5/10 | 10/10 | Mejorar + construir Tier-1 | Tier-1 es un `raise` (`fetch.py:94-98`); sin proxies en código; fingerprint estático único. |
| 4 | Harness de RECETA ejecutable | 3/10 | 10/10 | Reemplazar (construir) | La receta documenta pero **no se ejecuta** (`harvest_dealer.py:71-73` receta post-hoc); sin RecipeRunner. |
| 5 | Identidad / record-linkage (Splink) | 8/10 | 10/10 | Mantener + elevar | Núcleo determinista fuerte (31% colapso); cross-source no servido; delta vivo infra-cableado (1.7M NEW vs <15k cambios). |
| 6 | Conectores / persistencia | 6/10 | 10/10 | Mejorar (unificar) | `ensure_platform_entity` copiado byte-idéntico ×29; sin clase base de cosecha. |
| 7 | Verificación VAM | 5.5/10 | 10/10 | Mejorar (despertar lentes) | 2 de 5 lentes muertas (B/C dormidas); independencia de A nominal; denominador estadístico ausente. |
| 8 | Governor / rate-limit distribuible | 7/10 | 10/10 | Mejorar (distribuir) | In-memory mono-proceso (`governor.py:234`); sin AIMD; no distribuible. |
| 9 | Orquestación / scheduler / observabilidad | 8/10 | 10/10 | Mantener + elevar | 6 de 9 detectores sin caller en prod; sin métricas en el tiempo. |
| 10 | Datos / almacenamiento (sample-and-delete) | 8.5/10 | 10/10 | Mantener | eviction automática no corre. |
| 11 | Producción VPS | N/A | 10/10 | Diseñar (diferido) | No existe; gate = verificación local total. |
| 12 | Modelo de datos / API | 8/10 | 10/10 | Mantener + elevar | cdp_code sin UNIQUE CONSTRAINT (no FK-able); 3 sistemas de identidad solapados. |

**Nota global del sistema as-is: ~5.9/10** (baja respecto al 6.4 nominal de la V1 porque la V1 no puntuó honestamente el descubrimiento como sistema). **El delta de valor está concentrado en §1 y §2:** sin un sistema de descubrimiento demostrable, todo lo demás procesa con excelencia un universo que no sabe si está completo.

### 0.4 Procedencia y honestidad de esta V2

- **Auditoría as-is:** lectura directa del repo por agente (todos los `pipeline/sources/*.py`, `pipeline/platform/*facet|wholesale.py`, `identity/`, `geo.py`, `geocode.py`, `scripts/recon/b6_chapman_*.py`). Evidencia `archivo:línea` en cada sección.
- **SOTA:** 3 frentes de investigación web con fuentes citadas (apéndice §A): (1) MSE/captura-recaptura, (2) los 6 vectores de descubrimiento, (3) antidetección Tier-1 + record-linkage.
- **`[ASUMIDO]` no cerrados** se listan en el apéndice §B.

---

# §1 — EL SISTEMA DE DESCUBRIMIENTO (sección estrella)

> Esta es la pieza que la V1 no tenía. Aquí se diseña, a nivel átomo, **cómo cardeep encuentra el 100% de los puntos de venta de coches de España** —del grupo Quadis con 100 sedes al garaje de montaña con web de 3 coches o sin web— y cómo lo **orquesta, almacena y mide**. El framework de exhaustividad que lo certifica es §2.

## 1.0 Principio rector: descubrimiento ≠ cosecha

**[VERIFICADO]** La auditoría reveló una distinción que el código implementa pero **no documenta**, y que la V1 ignoró: existen dos clases de adaptador radicalmente distintas.

- **DESCUBRIMIENTO (F1 census):** crea **entidades-dealer** nuevas. Hoy: 13 adaptadores en `pipeline/discover.py:36-50` (DGT-CAT, OSM, 8 OEM, 3 asociaciones), cada uno implementando el contrato `SourceAdapter` (`sources/base.py`) → `DiscoveredEntity` → geo-resolución INE → minteo `cdp_code` → VAM count gate (`discover.py:135-141`).
- **COSECHA (wholesale/facet):** extrae **inventario** de dealers **ya conocidos**. Hoy: 37 módulos `platform/*_wholesale.py` + 2 `*_facet.py`. **[VERIFICADO — hallazgo clave]** *Ningún* módulo wholesale descubre dealers nuevos: todos atribuyen anuncios a un `seller_id` que se busca contra `entity.website` preexistente. Wallapop wholesale enumera **~224.822 dealers** y Milanuncios **~123.600** (`b6_chapman_final.py:61-92`), **pero como subproducto de cosechar inventario, no como censo deliberado de vendedores**.

**La consecuencia estratégica:** las dos mayores poblaciones de vendedores de España (Wallapop, Milanuncios) **están físicamente presentes en el sistema como atribución de anuncios, pero NO como entidades censadas y verificadas**. Convertirlas en censo es el Vector 1, y es la palanca que captura a los dealers sin web propia.

## 1.1 AS-IS — auditoría del descubrimiento actual (evidencia archivo:línea) · Nota **4/10**

### 1.1.1 Vectores que SÍ existen hoy

| Vector existente | Adaptador (`archivo:línea`) | Mecanismo | Entidades aprox. | Naturaleza |
|---|---|---|---|---|
| Censo legal desguaces | `sources/dgt_cat.py:38-42` | ArcGIS FeatureServer REST (`returnCountOnly=true`) | **1.292** (exacto, sellado) | Administrativo |
| Directorio geo voluntario | `sources/osm.py:63-64` | Overpass `shop=car/car_repair/car_parts` | **~9.956** declared (~12.077 fetched) | Geográfico, **sesgo urbano** |
| OEM oficiales (8 marcas) | `sources/oem_{kia,mg,byd,skoda,dacia,hyundai,mercedes,seat}.py` | JSON API / GeoJSON / HTML paginado por marca | **242+212+106+215+482+175+242+98 ≈ 1.772** | Oficial de marca |
| Asociaciones sector (3) | `sources/associations.py:48,80,117` | JSON local (dump web) AEDRA/ACEVAS/AECS | variable (en fichero) | Censo asociativo |
| Long-tail directorio | `scripts/discover_paginas_amarillas.py:1-222` | Páginas Amarillas live crawl (5 rubros) schema.org | ~1.662 compraventas | **FUERA del pipeline** (script suelto, sin VAM) |

**Cobertura geo `[VERIFICADO]`:** 52/52 provincias + 8.131 municipios INE exactos + ~63k gazetteer de localidades (`geo.py:200-234`), con cascada exact→fuzzy WRatio≥88→Nomenclátor, fallback lat/lon→provincia por nearest-neighbor (`geocode.py:78-103`) y CP→municipio (`geocode.py:225-260`). La geo-resolución **no es el cuello de botella**; las fuentes lo son.

### 1.1.2 Vectores que FALTAN (los 6 estratégicos del mandato)

| Vector estratégico | Estado as-is | Evidencia |
|---|---|---|
| **V1 Marketplace-as-census** | ❌ **NO existe** | Wallapop/Milanuncios solo cosechan inventario; no enumeran sellers como entidades (`wallapop_wholesale.py`, atribución por seller_id). |
| **V2 Geo-grid Maps/Places + Overture** | ❌ NO (solo OSM parcial) | Sin Google Places, sin Overture Maps (señalado como gap clave en `b6_chapman_analysis.py:369-379`). |
| **V3 Dorking por 8.131 municipios** | ❌ NO | Sin motor de búsqueda programable por municipio. |
| **V4 Registros oficiales (BORME/CNAE/OEM ampliado)** | ⚠️ Parcial | Solo 8 de ~35-40 OEM; sin BORME, sin INE DIRCE/CNAE 451, sin Registro Mercantil. |
| **V5 Descubrimiento recursivo en grafo** | ❌ NO | Sin crawl de sucursales/grupos desde webs conocidas. |
| **V6 Long-tail invisible (colapso por teléfono/CIF)** | ⚠️ Parcial | `cluster_dealers.py:170-186` colapsa por phone+muni / web+muni, pero **solo entre entidades ya descubiertas**, no infiere vendedor desde anuncios sueltos sin web. |

**Veredicto de cobertura:** la arquitectura F1 (contrato + VAM + minteo inmutable) es **sólida y reutilizable** (8/10 como *arquitectura*). La **cobertura de vectores es 4/10**: dominan las fuentes "fáciles" (OEM oficiales, censos administrativos), justo las que ya están en cualquier directorio; el long-tail invisible —el verdadero reto del mandato— apenas está tocado, y las dos mayores poblaciones de vendedores no están censadas.

## 1.2 TO-BE — arquitectura del Sistema de Descubrimiento

### 1.2.1 Visión: un censo nacional de 6 vectores ortogonales + colapsador

El principio metodológico (tomado de HRDAG, ver §2) es que **ninguna fuente única cubre el 100%; la cobertura es la unión de listas deliberadamente ortogonales**, y la ortogonalidad es lo que además habilita el denominador estadístico. Por eso el sistema se diseña como **6 vectores que capturan por mecanismos independientes** (administrativo, geográfico, comercial-digital, búsqueda, grafo, inferencia) + un **Vector 6 que colapsa al vendedor real** y alimenta el dedup.

```
                          ┌─────────────────────────────────────────────┐
                          │   DISCOVERY ORCHESTRATOR (pipeline/discover) │
                          │   contrato SourceAdapter + VAM count gate    │
                          └───────────────────┬─────────────────────────┘
   V1 marketplace-census ──┐                  │                  ┌── V4 registros oficiales
   V2 geo-grid + Overture ─┤   DiscoveredEntity stream           ├── V5 grafo recursivo
   V3 dorking municipal  ──┘   (kind, cif, cnae, geo, contacto)  └── (OEM ampliado, BORME, CNAE)
                              │                                   │
                              ▼                                   ▼
                    ┌──────────────────────────────────────────────────┐
                    │  V6 COLAPSADOR  (teléfono E.164 / CIF / email /    │
                    │  geo) → Splink → entidad canónica (vendedor real)  │
                    └───────────────────────┬──────────────────────────┘
                                            ▼
                    ┌──────────────────────────────────────────────────┐
                    │  §2 FRAMEWORK DE EXHAUSTIVIDAD                    │
                    │  captura-recaptura multi-lista (dga/LCMCR)        │
                    │  → N̂ por provincia×tipo + IC + % cobertura sellada│
                    └──────────────────────────────────────────────────┘
```

### 1.2.2 Esquema de datos del descubrimiento (extensión, no reemplazo)

Se extiende `DiscoveredEntity` (`sources/base.py`) y se añade una tabla de **observaciones de captura** que es el input directo del framework §2. Clave: **cada fuente que "ve" un vendedor deja una fila de captura**, aunque el vendedor ya exista — eso es lo que permite contar el solapamiento `m`.

```sql
-- NUEVO: registro de captura por (lista, entidad canónica). Es el átomo del MSE.
CREATE TABLE discovery_capture (
    capture_id      bigserial PRIMARY KEY,
    source_key      text NOT NULL,          -- 'osm','overture','wallapop_census','borme_cnae4511',...
    vector          smallint NOT NULL,      -- 1..6 (qué vector estratégico)
    entity_ulid     uuid NOT NULL,          -- entidad cruda descubierta
    canonical_ulid  uuid,                   -- rellenado por V6/Splink (NULL hasta colapsar)
    province_code   char(2),                -- estrato geográfico
    dealer_type     text,                   -- estrato tipo: oficial|compraventa|desguace|garaje
    captured_at     timestamptz NOT NULL DEFAULT now(),
    confidence      real,                   -- calidad del match de colapso (de Splink)
    UNIQUE (source_key, entity_ulid)
);
-- El denominador §2 se calcula sobre la matriz (canonical_ulid × source_key) agregada por estrato.
```

`DiscoveredEntity` gana campos para alimentar el colapso V6 y la triangulación CNAE:
```python
@dataclass
class DiscoveredEntity:
    # ... campos actuales ...
    phone_e164: str | None = None       # normalizado E.164 (phonenumbers) — clave fuerte V6
    cif_validated: bool = False         # checksum NIF/CIF verificado (python-stdnum) — clave fuerte V6
    email_canonical: str | None = None  # lower + canonicalización — clave V6
    cnae_code: str | None = None        # 4511/4519/4520/4531/4532 — triangulación censo §2
    vector: int = 0                     # qué vector lo descubrió
```

## 1.3 LOS 6 VECTORES — diseño técnico concreto

> Para cada vector: **diana abierta concreta** (no genérico), algoritmo, herramienta/repo con enlace, criterio de verificación, y por qué supera lo convencional. Las dianas marcadas `[VERIFICADO]` fueron confirmadas por investigación web en esta sesión (ver apéndice §A.2).

### VECTOR 1 — Marketplace-as-census (la palanca del long-tail con presencia digital)

**Qué es:** enumerar **todos los vendedores profesionales** de cada plataforma como entidades-dealer (no como anuncios). Captura al dealer que no tiene web propia pero sí ficha de tienda en un marketplace — una fracción enorme del long-tail.

**Dianas abiertas concretas `[VERIFICADO]`:**
- **autocasion.com** → `sitemap stock.xml` enumera **2.981 dealers** con `lastmod` diario. Diana inmediata, coste ~0, sin WAF.
- **ocasionplus** → sitemap de **138 sedes**; **flexicar.es** → **+200 delegaciones** con VIN; **coches.com** → IDs secuenciales de tienda `D{N}` (enumeración directa).
- **motor.es** → directorio de concesionarios paginado.
- **wallapop** → `api/v3/general/search` con partición geográfica (ya se drena para inventario en `wallapop_facet.py`; **reusar la misma paginación para enumerar `seller_id` únicos** y emitir un `DiscoveredEntity` por seller, no por coche).
- **Tier-1 (DataDome/Akamai)**: coches.net, autoscout24.es, milanuncios → requieren el motor §3 (Camoufox + IP ES sticky). Diferidos a fase con Tier-1 listo.

**Algoritmo (seller-census, no inventory):**
```
para cada plataforma P con directorio/sitemap de tiendas:
    sellers = enumerar_perfiles_profesionales(P)         # sitemap | API sellers | IDs secuenciales
    para cada seller s:
        emit DiscoveredEntity(kind='compraventa'|'oficial', source_key=f'{P}_census',
                              trade_name=s.name, website=s.shop_url, phone_e164=norm(s.phone),
                              province_name=s.province, vector=1, source_ref=s.seller_id)
    declared_count = len(sellers)   # del oracle del sitemap/API → VAM gate honesto
```

**Repos/técnicas:** sitemaps XML estándar; `wallapop` API pública `api/v3/general/search`. **Por qué supera lo convencional:** la práctica habitual scrapea inventario y deduce dealers como subproducto sucio; aquí el **seller es el objeto de primera clase**, con su propio VAM count gate (declared sellers == fetched == ingested), lo que da un censo verificable por plataforma y una **lista ortogonal limpia** para el MSE.

**Verificación:** `autocasion_census` ingiere 2.981 ± tolerancia 0, VAM TRUSTWORTHY; cada seller produce ≥1 fila `discovery_capture`.

---

### VECTOR 2 — Geo-grid Maps/Places + Overture + OSM (cobertura física exhaustiva)

**Qué es:** teselar **toda España** en celdas y consultar, por celda y categoría, todas las bases de POIs geográficas. Captura el local físico que no aparece en marketplaces ni tiene web.

**Capa base GRATIS y ortogonal `[VERIFICADO]`:**
- **Overture Maps** (places theme, Parquet/DuckDB por bounding-box, **CC BY 4.0**): ~10k+ POIs automotive ES, **origen Google/Meta/Apple/TomTom** → **ortogonal a OSM** (clave para el MSE; señalado como gap en `b6_chapman_analysis.py:369-379`). Consulta vía DuckDB `read_parquet(s3 overture)` filtrando bbox España + categorías automotive.
- **OSM Overpass** (ya parcialmente usado): `shop=car`, `shop=car_repair`, `shop=car_parts`. Añadir `out count` para `declared_count` honesto.

**Capa premium (cap duro a vencer) `[VERIFICADO]`:**
- **Google Places** (Nearby/Text Search, `type=car_dealer`/`car_repair`): **cap de 60 resultados/consulta**. Se vence con **grid adaptativo quadtree**: empezar en celdas grandes; **subdividir solo las celdas que devuelven 60** (saturadas, típicamente urbanas). ~15.000 celdas reales para cobertura nacional, ~$1.000 una corrida (coste no es criterio en esta fase).

**Algoritmo (quadtree adaptativo):**
```
cola = [bbox(España)]
mientras cola no vacía:
    celda = cola.pop()
    res = places_nearby(celda, type='car_dealer')
    emitir cada POI como DiscoveredEntity(vector=2, source_key='google_places')
    si len(res) >= 60 y celda.lado > MIN_LADO:   # saturada → puede ocultar POIs
        cola += celda.subdividir_en_4()
```

**Repos/técnicas:** Overture `places` (`overturemaps.org`), DuckDB spatial; Overpass API; patrón quadtree de geo-grid Places scraping. **Por qué supera lo convencional:** una sola pasada Overpass deja huecos (mapeadores urbanos); **tres capas de POIs de orígenes distintos** + grid adaptativo que **no asume densidad uniforme** capturan el local rural que el barrido ingenuo pierde, y aportan **dos listas ortogonales nuevas** (Overture, Places) al denominador.

**Verificación:** Overture y OSM producen listas con solapamiento medible; celdas saturadas detectadas y subdivididas (log del quadtree); ningún POI automotive ES en Overture queda sin fila de captura.

---

### VECTOR 3 — Dorking sistemático por los 8.131 municipios (descubre dominios propios)

**Qué es:** para cada uno de los **8.132 municipios INE** (tabla maestra abierta en GitHub `codeforspain` `[VERIFICADO]`), lanzar plantillas de búsqueda y cosechar dominios de dealers con web propia que ningún directorio indexa.

**Motor `[VERIFICADO]`:** **SearXNG self-hosted** (meta-buscador, coste-cero, sin cuota) como motor principal + **Serper.dev** como respaldo de calidad. Nota dura: **Google CSE cerrado a nuevos clientes y Bing Web Search API retirada** → SearXNG es la vía sostenible. Descubrimiento complementario de dominios `.es`: **Certificate Transparency** (crt.sh, base PostgreSQL pública) — no existe zone file `.es` abierto, pero los certados sí.

**Algoritmo:**
```
para cada municipio m en INE(8132):
    para cada plantilla t in ["concesionario {m}", "compraventa coches {m}",
                              "venta coches ocasion {m}", "desguace {m}"]:
        hits = searxng(t)
        para cada hit con dominio propio (no marketplace conocido):
            emit DiscoveredEntity(vector=3, source_key='dork_municipal',
                                  website=hit.domain, municipality_name=m, source_ref=t)
    # crt.sh: dominios .es nuevos con CN que matchee patrón automoción
```

**Por qué supera lo convencional:** los directorios solo contienen a quien se dio de alta; el dorking municipal **encuentra la web propia del garaje que nunca se listó**, barriendo el territorio entero (no una muestra) — exactamente el "garaje de montaña" del mandato. Estratificado por municipio, además, mide cobertura geográfica fina.

**Verificación:** cobertura de los 8.132 municipios (0 saltados); dominios nuevos no presentes en otras listas → señal de long-tail genuino; tasa de dominios automoción confirmados por extruct (JSON-LD `AutoDealer`).

---

### VECTOR 4 — Registros oficiales (administrativo, máxima ortogonalidad)

**Qué es:** la lista **más ortogonal a todo lo digital**, porque su mecanismo de captura es fiscal/legal, no comercial. Es la que ancla el denominador §2 contra un censo externo.

**Dianas `[VERIFICADO]`:**
- **Localizadores OEM ampliados:** hoy 8 marcas; faltan ~27-32 (Audi, BMW, Ford, Nissan, Toyota, Volvo, Renault, Peugeot, Citroën, Opel, VW, Fiat, Jeep, Cupra, Tesla, Volvo, JLR, Suzuki, Mazda, Honda, Mitsubishi, Lexus, Mini, DS, Alfa, Porsche, Audi…). Cada uno = XHR/JSON propio (mismo patrón que `oem_kia.py:74-76`). **Nota:** varios ya existen como `oem_*_wholesale.py` pero **NO en `discover.py` ADAPTERS** → promoverlos a F1 census es trabajo de cableado, no de investigación.
- **BORME** (Boletín Oficial del Registro Mercantil) vía **API BOE + librería `bormeparser`**, filtrando **CNAE 4511/4519** → long-tail de altas/bajas de empresas de automoción + **delta registral** (constituciones/disoluciones).
- **INE DIRCE** (Directorio Central de Empresas): **dimensiona el meta** (cuántas empresas CNAE 451 hay por provincia) → input directo del techo del denominador y de la triangulación §2.
- Asociaciones: FACONAUTO/GANVAM **sin directorio abierto** `[VERIFICADO]` → vía indirecta (sus listados públicos parciales) o se omiten como lista.

**Por qué supera lo convencional:** un censo de dealers basado solo en fuentes digitales está **estructuralmente sesgado** hacia quien tiene presencia online. El registro administrativo es la **única lista cuya probabilidad de captura no correlaciona con la digitalización del dealer** → es la que rompe la heterogeneidad y hace creíble el `N̂` (ver §2.5). BORME además da el **delta de altas/bajas** que el motor de delta (`delta.py`) hoy apenas ejerce.

**Verificación:** OEM ampliado a ≥30 marcas en `discover.py`; BORME-CNAE produce entidades con CIF validado por checksum; INE DIRCE da el conteo CNAE-451 por provincia usado en la triangulación §2.7.

---

### VECTOR 5 — Descubrimiento recursivo en grafo (grupos y franquicias)

**Qué es:** desde cada web de dealer conocido, **crawl en grafo** que salta a sucursales, grupo matriz y dealers hermanos. Captura la sede que no se lista sola pero cuelga de un grupo.

**Dianas `[VERIFICADO]`:** grupos verificados con muchas sedes — **Quadis (+100)**, **Huertas (+50, URLs semánticas auto-clasificables)**, **Caetano**. Patrón: `robots.txt`/`sitemap` → JSON-LD `AutoDealer`/`AutoDealer` schema.org → `Scrapy CrawlSpider` con `restrict_css` a "nuestras instalaciones/concesionarios" → **Common Crawl CDX + Web Graph** para saltar de un dealer a su grupo matriz y de ahí a los hermanos sin recrawl.

**Algoritmo:**
```
frontera = webs_conocidas(entity.website where vector in (1..4))
visto = set()
mientras frontera:
    url = frontera.pop()
    dom = registrable_domain(url)
    si dom in visto: continue
    visto.add(dom)
    html = fetch(url)               # Tier-0 normalmente; Tier-1 si WAF
    para link in extraer_sucursales(html):   # JSON-LD branch[], "instalaciones", footer
        emit DiscoveredEntity(vector=5, source_key='graph_recursive', website=link, ...)
        si registrable_domain(link) not in visto: frontera.add(link)
    # Common Crawl: hermanos del mismo grupo via web-graph backlinks
```

**Por qué supera lo convencional:** el descubrimiento plano trata cada web como aislada; el **grafo explota la estructura corporativa real** (un grupo enlaza a todas sus sedes), capturando sucursales que ninguna otra lista ve por separado, y respetando el guard anti-cadena de identidad (`cross_source_dedup.py:164-177`) para no colapsar Flexicar Madrid con Flexicar Sevilla.

**Verificación:** desde Quadis se descubren ≥N sucursales no presentes en otras listas; el guard de municipio mantiene las sedes como entidades distintas (cadena), no como duplicado.

---

### VECTOR 6 — Long-tail invisible: colapso al vendedor real (sin web ni ficha)

**Qué es:** el caso más duro del mandato — el vendedor **profesional disfrazado de particular** o sin presencia propia, que solo existe como **anuncios sueltos**. Se reconstruye colapsando anuncios por señales de contacto compartidas, y se distingue del particular genuino por **volumen y recurrencia**.

**Técnicas y repos `[VERIFICADO]`:** **entity resolution con Splink** (Fellegi-Sunter probabilístico, auditable) colapsando por:
- **Teléfono → E.164** (`phonenumbers`, port de libphonenumber; ES `+34`). Señal fuerte si el número aparece en N≥umbral anuncios.
- **CIF/NIF** (`python-stdnum`): la letra es **checksum** → validar antes de usar como clave fuerte. **La señal más fuerte** cuando está presente.
- **Email canónico** (lower + normalización).
- **Geo** (Nominatim self-hosted + **DBSCAN haversine** sobre coordenadas de anuncios → un punto de venta recurrente).
- **OCR/matrícula** (`PaddleOCR` + `fast-alpr`) sobre fotos: misma matrícula re-anunciada / mismo fondo de nave = mismo vendedor.

**Crítico — term-frequency adjustment `[VERIFICADO]`:** Splink pondera un **valor raro compartido** (móvil presente en solo 2 fichas → casi seguro mismo dueño) mucho más que uno común (centralita de marketplace → ruido). Esto es exactamente lo que evita sobre-fusionar por un teléfono genérico, y es nativo en el modelo Fellegi-Sunter.

**Por qué supera lo convencional:** la heurística ingenua (mismo teléfono → mismo dealer) sobre-fusiona por centralitas compartidas y sub-fusiona por números rotados; el modelo probabilístico con TF-adjustment y el guard geográfico dan un colapso **auditable con match-weight** (satisface "verificar cada número") y reversible (extiende el overlay `residual-namemuni-v1` ya en repo, commit `a73f9d6`). Es además el paso 1 obligatorio de HRDAG: **sin colapso correcto, el MSE de §2 miente** (un dealer partido en 3 listas infla `m` o lo desinfla según el caso).

**Verificación:** colapso reproduce/mejora el dedup actual con match-weights; un vendedor con N anuncios y 1 teléfono raro → 1 entidad; precisión auditada por bridges de Splink.

## 1.4 Orquestación del sistema de descubrimiento

- **Contrato:** todos los vectores implementan el `SourceAdapter` existente (`sources/base.py`) → reutiliza el VAM count gate de `discover.py:135-141` sin tocar el orquestador. Cada vector es un `source_key` con su `declared_count()` honesto.
- **Integrar Páginas Amarillas:** promover `scripts/discover_paginas_amarillas.py` a `sources/paginas_amarillas.py` con VAM gate (hoy es script suelto sin verdad única).
- **Continuo/incremental, no one-shot:** un job programado (APScheduler, §9) por vector con cadencia propia (BORME diario por el delta de altas/bajas; Overture mensual por su release; geo-grid trimestral). Cada corrida añade filas `discovery_capture` con `captured_at` → habilita la **curva de acumulación** que mide la parada del descubrimiento (§2.7).
- **Colapso V6 tras cada ola:** Splink corre sobre las nuevas entidades crudas y rellena `canonical_ulid` en `discovery_capture` → la matriz de captura queda lista para el MSE.

## 1.5 Por qué este sistema supera lo convencional

1. **Ortogonalidad deliberada:** los 6 vectores se eligen por **mecanismo de captura independiente** (fiscal, geográfico, comercial, búsqueda, grafo, inferencia), no por conveniencia. Esa ortogonalidad es lo que el MSE necesita y lo que un scraper convencional nunca diseña.
2. **El seller como objeto de primera clase** (V1) en vez de subproducto del inventario → censo verificable, no estimación sucia.
3. **Demostrabilidad incorporada:** cada captura deja una fila para el denominador. El sistema **no solo descubre; mide cuánto le falta por descubrir** (§2).
4. **Long-tail explícitamente atacado** por tres vías complementarias (V3 dorking, V5 grafo, V6 inferencia), donde la práctica habitual se rinde.

---

# §2 — FRAMEWORK DE EXHAUSTIVIDAD (lo que demuestra el 100% con IC)

> Esta sección responde a la frase exacta del mandato: "DEMOSTRARLO con intervalo de confianza". Es la pareja inseparable de §1: el descubrimiento produce las listas; este framework certifica qué fracción del universo verdadero representan.

## 2.1 AS-IS · Nota **2/10**

**[VERIFICADO]** Existe infraestructura (`denominator_estimate`, migración 0026:250-266) pero el cálculo es **inservible**: `b6_chapman_final.py:5-17` documenta que con `entity_cluster` casi sin mergear cross-source, el solapamiento OSM×Wallapop es **m=10 globales** → `N̂≈151.840`, **IC `[0, 303.679]`**. El denominador "vivo" es un **techo registral** (DIRCE) + **floor de fuentes**, no una estimación estadística con IC. **Causa raíz:** (a) faltan listas ortogonales (Overture, CNAE) que §1 V2/V4 aportan; (b) cross-source dedup no servido (`cross-source-dedup-v1` FALSE) → solapamiento real subcontado; (c) solo 2 listas, ambas con heterogeneidad de captura severa.

## 2.2 TO-BE — captura-recaptura multi-lista estratificada

Estimar `N̂` (población verdadera de dealers) **por estrato provincia × tipo** (~52 × 4 ≈ 200 estratos) a partir de la matriz de captura de las 6 listas, con IC, y certificar `% cobertura = n_observado / N̂` usando la **cota inferior** del IC (disciplina anti-maquillaje).

## 2.3 Algoritmos y stack (decisión por densidad de datos)

**[VERIFICADO]** No hay equivalente Python maduro a los paquetes de referencia → **puentear a R vía `rpy2`** (reimplementar en PyMC reintroduce riesgo en lo único que no podemos equivocar: los números).

| Situación del estrato | Modelo | Paquete (R, vía rpy2) | Razón |
|---|---|---|---|
| ≥3 listas, tabla con datos | **Bayesian model averaging sobre grafos descomponibles** | **`dga`** (Johndrow/Lum/Ball, HRDAG) | Pondera todas las estructuras de dependencia → incorpora incertidumbre de dependencia en el IC. Caballo de batalla forense. |
| Heterogeneidad fuerte / tabla dispersa (rural) | **Latent-class (Dirichlet process)** | **`LCMCR`** (Manrique-Vallier 2016, Biometrics) | Captura heterogeneidad sin asumir su forma; tolera dispersión. |
| Validación cruzada | **Log-lineal + model selection (BIC)** | **`Rcapture::closedpMS.t`** | Segundo camino independiente; si discrepa mucho de `dga`, desconfiar (regla de doble verificación). |
| Solo 2 listas | **Chapman + IC bootstrap** | `recapr` | Piso, no certificación; marcar estrato "baja confianza". |
| Sin garantía de independencia (siempre, en realidad) | **IC dependence-robust (identificación parcial)** | Sun et al. 2020 (test-inversion bootstrap) | Banda conservadora honesta cuando no se puede jurar independencia. |

**Fórmulas base (referencia, `recapr`/Seber):**
- Chapman: `N̂ = (n₁+1)(n₂+1)/(m₂+1) − 1`
- Var (Seber): `Var = (n₁+1)(n₂+1)(n₁−m₂)(n₂−m₂) / [(m₂+1)²(m₂+2)]`
- IC: bootstrap (el Wald normal es pobre con `m₂` pequeño).

## 2.4 Esquema de cálculo

```
para cada estrato (provincia, tipo):
    M = matriz_captura(canonical_ulid × source_key)   # de discovery_capture
    K = nº listas con datos en el estrato
    si K >= 3:        N̂, IC = dga(M)  ;  validar con Rcapture::closedpMS.t
    elif heterogéneo: N̂, IC = LCMCR(M)
    elif K == 2:      N̂, IC = chapman_bootstrap(M)   # baja confianza
    cobertura = n_obs / N̂ ;  cobertura_inf = n_obs / N̂_sup
    sellado = (cobertura_inf >= UMBRAL)               # p.ej. 0.95
    triangular(N̂, censo_CNAE_451[provincia])          # §2.7
```

## 2.5 Supuestos críticos (lo que muerde) y mitigación

| Supuesto | Violación en dealers | Efecto | Mitigación (de §1) |
|---|---|---|---|
| Independencia de listas | Marketplaces comparten feeds | Correlación positiva → **subestima `N̂`** | Interacciones (Rcapture) / model-averaging (dga); **V4 registro ortogonal** |
| Homogeneidad de captura | Garaje rural casi invisible | Subestima la cola | **LCMCR** (clases latentes); **V3 dorking + V6 inferencia** capturan la cola |
| Población cerrada | Altas/bajas durante cosecha | Sesga `N̂` | Estratificar por ventana temporal (snapshot); **BORME da el delta** |
| Emparejamiento perfecto | Dealer partido entre listas | Falsos no-solapamientos → **sobreestima `N̂`** | **V6 colapso Splink es prerequisito** del MSE |

## 2.6 Criterio formal de "sellado al 100%"

Por estrato: **sellado al X% ⇔ cota inferior del IC de cobertura ≥ X**. Se usa la cota inferior, nunca el puntual. **Criterio de parada del descubrimiento** `[ASUMIDO sobre teoría VERIFICADA]`: parar cuando `N̂` se estabiliza al añadir listas (la curva de acumulación asíntota; el "no-observado" `N̂ − n_obs` deja de caer). Las filas `discovery_capture.captured_at` de §1 dan esa curva directamente.

## 2.7 Triangulación externa obligatoria

Contrastar `N̂` contra censo independiente: **INE DIRCE / CNAE 4511-4532** (de V4), **DGT** (puntos de venta/talleres). Si `N̂ ≫ censo` → listas correlacionadas no modeladas o dedup imperfecto; si `N̂ ≈ censo` → sello creíble. **El censo externo es la prueba por camino distinto** que exige la doctrina del Director. Patrón metodológico tomado de **HRDAG** (Kosovo/Siria/Guatemala): linkage primero → estratificar → no elegir un modelo → reportar `N̂` con IC → triangular.

## 2.8 Por qué supera lo convencional

Un scraper convencional declara "cobertura" como `dealers_encontrados / estimación_a_ojo`. Esto entrega un **`N̂` con IC por estrato, bajo ≥2 modelos independientes, triangulado contra un censo fiscal**, con un criterio de sellado basado en la cota inferior. Es la diferencia entre "creemos que tenemos casi todos" y "certificamos, con 95% de confianza, ≥X% de cobertura en la provincia P para el tipo T".

## 2.9 Criterios de "hecho/verificado"

- [ ] Matriz `discovery_capture` poblada por ≥4 listas ortogonales (incl. Overture y CNAE).
- [ ] `dga`/`LCMCR` corren vía rpy2 y emiten `N̂`+IC por estrato.
- [ ] Cross-source dedup (V6/Splink) servido → `m` por estrato sube de 10 a un valor que estrecha el IC.
- [ ] Denominador nacional con IC bajo ≥2 modelos + triangulación CNAE/DGT.
- [ ] Tablero de cobertura por provincia×tipo con cota inferior y estado de sellado.

---

# §3 — Motor de antidetección y transporte (Tier-1)

**AS-IS · 4.5/10 [VERIFICADO]:** transporte único `curl_cffi` impersonate hardcoded `chrome131` (`fetch.py:31`), Tier-1 = `raise NotImplementedError` (`fetch.py:94-98`), **sin proxies en código** (`fetch.py:70,108`), fingerprint estático único, sin rotación, sin detección semántica de ban.

**TO-BE — stack de 3 capas (decidido por DÓNDE gatea cada plataforma: TLS / protocolo-automatización / JS / comportamiento) `[VERIFICADO por benchmark Paterson, 651 verdictos, 2026-05-13]`:**
1. **Capa barata (servir inventario):** `curl_cffi impersonate=chrome146` (o `rnet`) reutilizando cookie de clearance con **mismo JA3+UA+IP sticky**. Para targets sin JS, basta (curl_cffi 26 OK, empata a CloakBrowser).
2. **Capa navegador (generar clearance):** **nodriver** (único con **0 bloqueos** en el benchmark; CDP directo evita el leak `Runtime.enable` de Playwright) para CF Turnstile/DataDome; **patchright `channel=chrome`** drop-in; **Camoufox** (Firefox parcheado) para diversidad. Headful bajo **Xvfb**; **headful real** para DataDome (Xvfb no basta `[VERIFICADO SeleniumBase #4216]`).
3. **Capa sensor/comercial:** **Hyper Solutions SDK** (sensor Akamai/Kasada/DataDome sin navegador); **Byparr** self-hosted.

**Patrón clave `[VERIFICADO para CF/Akamai]`:** navegador genera cookie (`cf_clearance`/`_abck`/`datadome`) → curl_cffi la drena con TLS+UA+IP **idénticos** (si difieren, la cookie muere en la 1ª reutilización). **Matiz honesto:** contra **DataDome** (marca por intención/comportamiento, >85k modelos ML) el fingerprint perfecto no basta sin humanización de pacing.

**Regla dura:** **jamás randomizar JA3 a mano** — los WAFs usan allowlist de fingerprints known-good; un JA3 random cae fuera. Target estable `chrome146`.

**ALERTA `[VERIFICADO]`:** **nodriver es AGPL-3.0** (copyleft de red) → decisión legal antes de meterlo en la API viva de cardeep.

**Diseño (igual que V1, válido):** `engine/transport.py` (router de tier), `fingerprints.py` (pool allowlist), `identity_pool.py` (lease proxy+fingerprint+cookies sticky-por-dealer), `tier1/{browser_nodriver,browser_camoufox,cookie_harvester,ban_detector}.py`. Reutiliza `fetch.py` como Tier-0 (correcto y empíricamente competitivo).

**Conexión con §1:** el Tier-1 es **prerequisito de V1 sobre coches.net/autoscout24/milanuncios** (DataDome/Akamai) y de la **lente C de VAM** (refetch vivo por egress independiente).

**Criterios:** rota ≥4 perfiles reales (test del ClientHello); resuelve ≥1 portal CF-managed real y curl_cffi sirve reusando cookie; `ban_detector` distingue 403-challenge de 403-real; IP de salida == pool ES.

---

# §4 — Harness de RECETA ejecutable (recipe-first / sample-verify-delete)

**AS-IS · 3/10 [VERIFICADO]:** orden real `harvest_dealer.py:28-86` = scrape→ingest→receta **post-hoc** (`:71-73`)→verify; la receta `recipe.py` se **serializa pero ningún loader la ejecuta**; solo 7 recetas de familia, 0 per-dealer; driver hardcoded a AS24.

**TO-BE — receta ejecutable como motor (igual diseño que V1, sigue siendo el de mayor ROI):**
```
DESCUBRIR(§1) → SCRAPEAR MUESTRA (k≈3-10) → PERSISTIR RECETA → VERIFICAR (VAM) → BORRAR MUESTRA
                                     ↑ si VERIFY falla → cazador re-caza receta (loop) ↑
```
Esquema v2 con **3 niveles de extracción por coste creciente** `[VERIFICADO repos]`: `extruct` (JSON-LD/microdata, coste 0, SIEMPRE primero) → selectores CSS declarativos → **LLM local** (`Crawl4AI` + `Outlines`/`Instructor`, constrained decoding, Qwen local temp 0) solo si 1 y 2 fallan. Componentes `pipeline/recipe/{schema,runner,harness,cazador}.py` + `extract/{structured,selectors,llm_local}.py`. "La receta funciona" = `RecipeRunner` reproduce la muestra **solo desde el YAML** y pasa quórum VAM por camino independiente.

**Criterios:** RecipeRunner reproduce ≥3 dealers de familias distintas solo-desde-YAML; ciclo E2E deja receta en git + 0 muestra en disco; cazador converge a VERIFIED; un bespoke sin selector cae a LLM-local y pasa VAM.

---

# §5 — Identidad / record-linkage (Splink) — eje compartido con §1.V6

**AS-IS · 8/10 [VERIFICADO contra DB viva]:** clustering `dealer-identity-det-v1` **vam_verified=TRUE**, union-find determinista 4 aristas con guard de municipio (`cluster_dealers.py:194-228`), 61.551→42.259 canónicos (**31% colapso real**, no singletons). **Debilidades:** cross-source `cross-source-dedup-v1` **vam_verified=FALSE** (50.497→688) → no servido en `v_canonical`; **delta vivo infra-cableado** (1.7M NEW vs <15k cambios; los 43 connectors emiten solo NEW).

**TO-BE — elevar con Splink v4 (MIT, v4.0.16 mar-2026) `[VERIFICADO]`:** Fellegi-Sunter probabilístico, EM no supervisado, DuckDB (~1M registros/min en laptop), **match-weights auditables** (satisface "verificar cada número"), comparador geográfico `DistanceInKMLevel` (Haversine) + `JaroWinklerLevel` para **cadena-vs-sucursal** (mismo nombre + <~0.5km = sucursal/colapsar; mismo nombre + lejos = cadena/no colapsar), **term-frequency adjustment** para no sobre-fusionar por teléfono genérico, **cluster bridges** para cazar over-merging. **Es el mismo motor que V6 (§1)** — una sola inversión sirve al descubrimiento y a la identidad. Cablear `diff_vehicle` (`delta.py:289-345`, ya correcto) en los 29 conectores vía el `_persistence.py` unificado de §6.

**Por qué supera el union-find artesanal:** formaliza el merge como probabilístico con pesos auditables y reversibles (extiende overlay), y su clustering **desbloquea el denominador de §2** (sube `m` por estrato).

**Criterios:** Splink reproduce/mejora el 31% con match-weights; cross-source servido en `v_dealer_resolved`; delta vivo (PRICE/PHOTO/KM/GONE>0 tras 2ª cosecha en flota, no solo AS24).

---

# §6 — Conectores / persistencia unificada

**AS-IS · 6/10 [VERIFICADO]:** `ensure_platform_entity` copiado **byte-idéntico ×29** (md5 `07d808e26217b31712a3b4a105ab3240`), `cdp_code_dealer` ×21, `_ingest_window` ×18 (**firmas ya divergentes → bomba de drift**). Los 30 `platform/*.py` no heredan de clase base.

**TO-BE:** extraer `pipeline/platform/_persistence.py` (empezar por las 29 copias byte-idénticas, reemplazo mecánico seguro); `WholesaleConnector` Protocol; `_ingest_window` único parametrizado por `field_map` (absorbe las 18 variantes y converge con la receta ejecutable de §4); fallback LLM-local para el tail bespoke. **Es prerequisito de cablear el delta (§5) en un punto, no en 29.**

**Criterios:** grep==1 definición de cada función; todos los conectores cumplen el Protocol; paridad de inserts pre/post refactor.

---

# §7 — Verificación VAM (despertar lentes + denominador)

**AS-IS · 5.5/10 [VERIFICADO]:** 5 lentes, **A activa** (pero lee la misma DB que escribió el ingest → independencia nominal), **B/C dormidas** (`lenses.py:135,210-217`), D/E activas. Quórum real (`quorum.py:136-297`) pero TRUSTWORTHY exige ≥2 ASSERTs independientes → con B/C muertas, muchos subjects solo tienen A → **imposible certificar**, sesgo default-REFUTED.

**TO-BE:** despertar **Lente C (refetch vivo)** — la única con D=4 y verificación contra el portal real, se apoya en el motor §3 (egress independiente); despertar **Lente B (raw recount)** sobre evidence-store de bytes; endurecer A (dejar de contarla como independencia salvo combinada). El **denominador estadístico es §2** (esta lente y el framework de exhaustividad son la misma doctrina "verificar todo" en dos planos).

**Criterios:** C discrepa/confirma por egress independiente; B recuenta sobre bytes crudos; ≥1 subject mono-lente pasa a ≥2 o se marca no-certificable.

---

# §8 — Governor / rate-limit distribuible

**AS-IS · 7/10 [VERIFICADO]:** token bucket per-host + spacing+jitter correcto (`governor.py:184-215`), pero **in-memory mono-proceso** (`:234`), sin persistencia, sin AIMD, no distribuible.

**TO-BE:** backend pluggable → **`pyrate-limiter` PostgresBucket+PostgresClock** (rate-limit distribuido **reusando el Postgres existente, sin Redis aún**); cerrar el lazo AIMD (`acquire()` ya devuelve `waited`); tabla `identity_lease` para checkout sticky-por-dealer. **Identidad + rate-limit = misma decisión** (permiso de pegar al host) → modelar juntos con §3. Redis-GCRA solo al saturar Postgres (Fase B/VPS).

**Criterios:** 2 procesos concurrentes no superan el ceiling agregado por host; reinicio no reabre bucket lleno; AIMD baja ante racha de 429.

---

# §9 — Orquestación / scheduler / observabilidad

**AS-IS · 8/10 [VERIFICADO]:** APScheduler `BlockingScheduler`+`SQLAlchemyJobStore` sobre Postgres → crash-safe; doble single-producer (`max_instances=1` + advisory lock); red de seguridad crash-before-record. Observabilidad madura (9/10): `record_run` único escritor, alerta con origen exacto `<source>:<phase>[:<code>]`, watchdog de silencio. **Debilidades:** **6 de 9 detectores sin caller en prod** (solo `run_price_trap` cableado), sin métricas en el tiempo, reparaciones caras son scaffold, serie pura.

**TO-BE — mantener núcleo (no migrar a Celery/Temporal), elevar:** cablear los 6 detectores (job 6h `dry_run_all`); Prometheus+Grafana con label `domain` como origen exacto; paralelo per-host (N workers asyncio + advisory-lock per-dealer + governor §8 como embudo); reparaciones caras conectadas a §3/§4. **Añadido V2:** el scheduler también orquesta los **6 vectores de descubrimiento** (§1.4) con cadencias propias (BORME diario, Overture mensual, geo-grid trimestral) → el descubrimiento continuo vive aquí.

**Criterios:** 6 detectores abren gestion_items reales; dashboard con ban-rate por dominio; una reparación cara E2E; N workers sin superar el ceiling.

---

# §10 — Datos / almacenamiento (sample-and-delete) · §11 — VPS · §12 — Modelo/API

**§10 AS-IS · 8.5/10 [VERIFICADO]:** `evict.py` sample-and-delete con 3 gates re-leídos en transacción, receta protegida (`evict.py:139-171` nunca toca `countries/ES/`), tombstone (no DELETE), commit-then-delete. Debilidad: eviction automática no corre. **TO-BE:** conectar el borrado al harness §4 (la muestra verificada se borra al cerrar el ciclo); mantener "better a hole than a lie".

**§11 VPS — diseño diferido (gate = verificación local total):** Docker Compose [APScheduler + N workers asyncio disposables + Postgres + Prometheus/Grafana], Postgres-as-queue (Redis solo al saturar), workers stateless. **No tocar hasta Fases 0-4 verificadas al 100% en local** (mandato).

**§12 Modelo/API AS-IS · 8/10 [VERIFICADO]:** tablas núcleo sólidas, invariantes DB reales. Debilidades: cdp_code sin UNIQUE CONSTRAINT (no FK-able), 3 sistemas de identidad solapados. **TO-BE:** Splink (§5) consolida a una autoridad probabilística; promover `uq_entity_cdp_code` a CONSTRAINT tras dedup; registro `identity_authority(endpoint→run_id)`; envelope API `{success,data,error,meta}` + delta servido. **Añadido V2:** exponer el **certificado de cobertura §2** (N̂, IC, % por provincia×tipo) como endpoint — el producto final no es solo el inventario, es el **mapa con su prueba de completitud**.

---

# §13 — ROADMAP por fases (el descubrimiento como columna vertebral)

> Orden gobernado por dependencias y por el mandato "verificar todo en local antes de VPS". El cambio de encuadre frente a la V1: **las Fases 1 y 2 son ahora descubrimiento + exhaustividad**, no antidetección.

### FASE 0 — Fundaciones reutilizables
- **P0.1 Unificar persistencia + contrato adapter (§6).** Prerequisito de delta (§5) y receta ejecutable (§4).
- **P0.2 Governor distribuible+persistente (§8, Fase A).**
- **P0.3 Splink v4 sobre las ~43k entidades (§5/§1.V6).** Desbloquea simultáneamente identidad, cross-source servido y el `m` del denominador (§2). **Pieza de doble uso — máxima prioridad.**

### FASE 1 — EL SISTEMA DE DESCUBRIMIENTO (corazón del mandato)
- **P1.1 Vectores de coste-0 e inmediatos (§1):** V1 dianas abiertas (autocasion stock.xml 2.981, ocasionplus, flexicar, coches.com), V2 capa gratis (Overture + Overpass `out count`), integrar Páginas Amarillas al pipeline con VAM.
- **P1.2 Vectores administrativos (§1.V4):** OEM ampliado a ≥30 marcas (cableado), BORME-CNAE 4511/4519 (`bormeparser`), INE DIRCE para el meta.
- **P1.3 Vectores de búsqueda y grafo (§1.V3, V5):** SearXNG self-hosted por 8.132 municipios; crawl recursivo desde grupos (Quadis, Huertas) con Common Crawl.
- **P1.4 Long-tail invisible (§1.V6):** colapso Splink por teléfono E.164/CIF/email/geo/OCR.

### FASE 2 — FRAMEWORK DE EXHAUSTIVIDAD (la prueba del 100%)
- **P2.1 Matriz `discovery_capture` + rpy2 bridge (§2).**
- **P2.2 MSE por estrato (`dga`/`LCMCR`/`Rcapture`) + IC + criterio de sellado por cota inferior.**
- **P2.3 Triangulación contra CNAE-451/DGT + tablero de cobertura provincia×tipo.**

### FASE 3 — Motor de antidetección agresiva (habilita V1-Tier1 y Lente C)
- **P3.1 Transporte Tier-0 con rotación + proxies ES (§3).**
- **P3.2 Tier-1 (nodriver/Camoufox + cookie-harvester + ban_detector) (§3).** *Decisión legal AGPL nodriver antes de comprometer.* Desbloquea V1 sobre coches.net/autoscout24/milanuncios.

### FASE 4 — Harness de receta + verificación viva
- **P4.1 Harness recipe-first/sample-verify-delete + RecipeRunner + cazador (§4).**
- **P4.2 Despertar lentes VAM B y C + endurecer A (§7).** C necesita egress de §3.2.
- **P4.3 Cablear delta vivo en la flota (§5).**

### FASE 5 — Activación de orquestación y observabilidad
- **P5.1 Cablear los 6 detectores + métricas Prometheus/Grafana (§9).**
- **P5.2 Descubrimiento continuo programado (§1.4) + reparaciones caras ejecutables (§9).**

### FASE 6 — Producción VPS (solo tras verificación local total)
- **P6 Topología VPS (§11).** **Precondición de gate:** Fases 0-5 verificadas al 100% en local + certificado de cobertura §2 emitido.

### Diagrama de dependencias
```
P0.1 ─┬─> P4.1 ───────────────┐
      ├─> P4.3 ──┐            │
P0.2 ─┤          │            │
P0.3 ─┴─> P1.4 ─┬┴─> P2.1 ─> P2.2 ─> P2.3 (certificado de cobertura)
   P1.1 P1.2 P1.3┘                              │
P3.1 ─> P3.2 ─┬─> P1(Tier1 targets) ─> P4.2 ───┤
              └─> P5.* ──────────────────────────┴─> P6 (gate: todo local verificado + cobertura certificada)
```

---

# §14 — Resumen ejecutivo final

La V1 era correcta en lo que auditó pero **miraba al sitio equivocado**: trataba cardeep como un problema de scraping con un back-end excelente. El problema real, el del mandato, es **un problema de censo nacional demostrable**: encontrar el 100% de los puntos de venta de España y **probar con IC** que se ha encontrado. Esta V2 reordena el plano alrededor de esa verdad.

Los **dos proyectos de cabecera** de la V2 son, ahora explícitamente, los que la V1 enterró:
1. **El SISTEMA DE DESCUBRIMIENTO multivector (§1):** 6 vectores deliberadamente ortogonales (marketplace-census, geo-grid+Overture, dorking municipal, registros oficiales, grafo recursivo, colapso del invisible), con el seller como objeto de primera clase y el long-tail atacado por tres vías. Hoy: 4/10 de cobertura sobre una arquitectura F1 8/10.
2. **El FRAMEWORK DE EXHAUSTIVIDAD (§2):** captura-recaptura multi-lista (`dga`/`LCMCR`/`Rcapture` vía rpy2, patrón HRDAG) que emite `N̂`+IC por provincia×tipo y certifica el sellado por la **cota inferior** del IC, triangulado contra el censo fiscal CNAE/DGT. Hoy: 2/10, bloqueado por m=10 — y desbloqueado en cuanto §1 aporta listas ortogonales y §5/Splink sirve el cross-source.

Todo lo demás —antidetección Tier-1, harness de receta, governor, VAM, identidad, orquestación, datos, API— se mantiene como en la V1 (auditado, sólido) pero **subordinado a su papel en el descubrimiento**: el Tier-1 existe para alcanzar los marketplaces Tier-1 del Vector 1 y la lente C; Splink sirve a la vez a la identidad y al colapso del Vector 6 y al `m` del denominador; el scheduler orquesta los 6 vectores en continuo. La estrategia sigue siendo quirúrgica —corregir lo roto, elevar lo mejorable, reutilizar lo bueno— pero con el eje correcto: **cardeep no estará terminado cuando scrapee bien; estará terminado cuando pueda enseñar un mapa de España con un número de cobertura y su intervalo de confianza al lado.**

---

## APÉNDICE §A — Fuentes y repos citados

### A.1 Captura-recaptura / MSE (§2)
- recapr vignette (Chapman/varianza Seber): https://cran.r-project.org/web/packages/recapr/vignettes/recapr_vignette1.html
- vChapman (varianza): https://rdrr.io/github/mbtyers/recapr/man/vChapman.html
- Brittain & Böhning 2009 (sesgo/precisión): http://www.personal.soton.ac.uk/dab1f10/Brittain_Boehning.pdf
- Rcapture (CRAN): https://cran.r-project.org/package=Rcapture · `closedpMS`: https://www.rdocumentation.org/packages/Rcapture/versions/1.4-2/topics/closedpMS
- HRDAG — Computing MSE in R: https://hrdag.org/tech-notes/basic-mse.html
- LCMCR (CRAN): https://cran.r-project.org/package=LCMCR · doc: https://rdrr.io/cran/LCMCR/man/lcmCR.html
- Manrique-Vallier 2016 (Biometrics, Dirichlet process MSE): https://www.researchgate.net/publication/297678257_Bayesian_population_size_estimation_using_Dirichlet_process_mixtures
- dga (CRAN): https://cran.r-project.org/package=dga · anuncio HRDAG: https://hrdag.org/2015/04/24/hrdag-offers-new-r-package-dga/ · dgaFast: https://github.com/OlivierBinette/dgaFast
- Sun et al. 2020 (dependence-robust CI, identificación parcial): https://arxiv.org/abs/2008.00127
- Binette & Steorts 2021 (fiabilidad MSE): https://arxiv.org/pdf/1902.06078 · MSETools: https://github.com/OlivierBinette/MSETools
- HRDAG tag MSE: https://hrdag.org/tag/multiple-systems-estimation/ · Austin Rochford PyMC capture-recapture: https://austinrochford.com/posts/2018-01-31-capture-recapture.html

### A.2 Vectores de descubrimiento (§1)
- Overture Maps (places, CC BY 4.0): https://overturemaps.org · OSM Overpass: https://overpass-api.de
- INE municipios (codeforspain): https://github.com/codeforspain (tabla maestra 8.132 municipios)
- SearXNG (meta-buscador self-hosted): https://github.com/searxng/searxng · Serper.dev: https://serper.dev
- Certificate Transparency crt.sh: https://crt.sh
- BORME parser: `bormeparser` (PyPI/GitHub) · API BOE: https://www.boe.es/datosabiertos · INE DIRCE: https://www.ine.es (Directorio Central de Empresas)
- Splink v4 (record-linkage, MIT): https://github.com/moj-analytical-services/splink · docs: https://moj-analytical-services.github.io/splink
- phonenumbers (E.164): https://github.com/daviddrysdale/python-phonenumbers · python-stdnum (CIF/NIF checksum): https://arthurdejong.org/python-stdnum/
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR · fast-alpr: https://github.com/ankandrew/fast-alpr · DBSCAN (scikit-learn haversine)
- extruct (JSON-LD/microdata): https://github.com/scrapinghub/extruct · Scrapy CrawlSpider · Common Crawl CDX: https://commoncrawl.org

### A.3 Antidetección + record-linkage (§3, §5)
- Benchmark Paterson (651 verdictos, 2026-05-13): https://ianlpaterson.com/blog/anti-detect-browser-benchmark-patchright-nodriver-curl-cffi/ · benchmark techinz: https://github.com/techinz/browsers-benchmark
- nodriver (AGPL-3.0): https://github.com/ultrafunkamsterdam/nodriver · Camoufox (fork coryking): https://github.com/daijro/camoufox
- patchright: https://github.com/Kaliiiiiiiiii-Vinyzu/patchright · BotBrowser: https://github.com/botswin/BotBrowser
- curl_cffi (lexiforest): https://github.com/lexiforest/curl_cffi · curl-impersonate: https://github.com/lexiforest/curl-impersonate · rnet: https://github.com/0x676e67/rnet
- Hyper Solutions SDK: https://github.com/Hyper-Solutions/hyper-sdk-py · Byparr: https://github.com/ThePhaseless/Byparr
- SeleniumBase #4216 (DataDome/Xvfb): https://github.com/seleniumbase/SeleniumBase/issues/4216
- dedupe: https://github.com/dedupeio/dedupe · Zingg (AGPL): https://github.com/zinggAI/zingg · recordlinkage: https://github.com/J535D165/recordlinkage
- pyrate-limiter (PostgresBucket, §8): https://pypi.org/project/pyrate-limiter/

## APÉNDICE §B — `[ASUMIDO]` no cerrados (honestidad)
1. Conteo real de POIs automotive de Overture/OSM para España (requiere `out count` Overpass + query Overture en vivo).
2. JSON exacto de los localizadores OEM de las ~27 marcas no implementadas (patrón conocido, endpoint por capturar marca a marca).
3. Slug/dataset exacto de BORME-CNAE en datos.gob.es (reconfirmar antes de cablear el adapter).
4. URLs de grupos secundarios para V5 más allá de Quadis/Huertas/Caetano.
5. Licencias de Camoufox/patchright/BotBrowser (marcadas, LICENSE no leído directo); implicación AGPL de nodriver sobre la API pública (requiere criterio legal).
6. Erosión del patrón cookie-reuse específicamente bajo DataDome (inferencia, no prueba directa).
7. Criterio numérico de "sellado al 100%" (umbral 0.95 propuesto): construcción sobre teoría verificada, a validar empíricamente contra el censo externo antes de declararse sellado.
8. Inexistencia de paquete Python maduro de MSE (verificado entre fuentes consultadas, no exhaustivo) → decisión rpy2.

---
*Fin del PLANO MAESTRO CARDEEP V2. Documento de arquitectura; no introduce cambios en el código. El descubrimiento es la columna vertebral; todo lo demás lo sirve.*
