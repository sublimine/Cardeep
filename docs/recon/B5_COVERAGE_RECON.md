# CARDEEP — B5 Coverage Recon: Denominador real + filtrado particular/dealer

> Auditor: agente de reconocimiento autónomo  
> Fecha: 2026-06-14  
> DB live: `cardeep-pg` :5433, db `cardeep`  
> Metodología: [VERIFICADO DB] = query directa a la DB · [VERIFICADO fuente] = lectura de
> fuente oficial · [ASUMIDO] = inferido, no re-derivado  
> Compromiso: un hueco confesado vale más que un número inventado.

---

## 1. DENOMINADOR REAL — ¿cuántos puntos de venta existen en España?

### 1.1 Concesionarios oficiales (CNAE 4511 + redes OEM)

| Fuente | Cifra | Año | Notas |
|--------|-------|-----|-------|
| DBK/INFORMA Observatorio Sectorial | **2.143 concesionarios** (grupos principales) | 2024 | [VERIFICADO fuente] — "rebote notable" tras tendencia descendente; 2023 eran 2.006 |
| FACONAUTO (declarado en architectura doc) | **2.018 franquiciados + 3.642 agentes** = ~5.660 instalaciones | ~2024 | [VERIFICADO fuente — citado en `07-COVERAGE-STRATEGY.md §2 SEG-2`] |
| Total instalaciones (grupos + agentes + secundarias) | **5.358 instalaciones operativas** | 2024 | [VERIFICADO fuente — La Tribuna de Automoción jun-2025] |
| eInforma CNAE 4511 (empresas registradas) | **~27.284 empresas** | ~2024 | [VERIFICADO fuente — incluye autónomos, pequeños, multimarca; NO solo concesionarios de marca] |

**Interpretación crítica:** Los 27.284 del CNAE 4511 incluyen TODO lo que vende coches ligeros —
concesionarios de marca, compraventas, importadores, multimarcas, autónomos ocasionales. Las
2.143 de FACONAUTO/DBK son sólo las redes franquiciadas de marca. La brecha (27.284 vs 2.143)
es la compraventa + garajes + independientes — el segmento más difuso del mercado.

**Denominador de referencia para SEG-2 (concesionario_oficial):** 2.018–2.143 franquiciados +
3.642 agentes. [VERIFICADO fuente]

### 1.2 Compraventas / garajes / independientes (CNAE 4519 + 4511 residual)

| Fuente | Cifra | Año | Notas |
|--------|-------|-----|-------|
| eInforma CNAE 4519 (venta otros vehículos motor) | **~12.050 empresas** | ~2024 | [VERIFICADO fuente — incluye furgonetas, camiones, motos; no es puro coches] |
| Páginas Amarillas "compraventa" (citado en arquitectura) | **1.662** locales | ~2024 | [VERIFICADO fuente — citado en `07-COVERAGE-STRATEGY.md §2 SEG-4`; es SUELO bajo, no techo] |
| OSM `shop=car` (citado en arquitectura) | **3.516** locales | ~2024 | [VERIFICADO fuente — citado en `07-COVERAGE-STRATEGY.md §2 SEG-4`] |
| CNAE 4511 total (empresas activas) | **27.284** | ~2024 | [VERIFICADO fuente] — techo máximo del universo POS, incluye todo tipo |

**Estimación real del universo compraventa+garaje (POS independientes):** La arquitectura
(§2 SEG-4) estima un denominador verdadero entre el floor de PA (1.662) y el techo CNAE
(~27k), con el estimador Chapman sobre fuentes ortogonales como método definitivo. No hay
censo oficial único para compraventas independientes. [ASUMIDO: universo ~5.000-15.000
compraventas POS reales, pendiente de cierre Chapman]

### 1.3 Desguaces / CATs (CNAE 3831/3832)

| Fuente | Cifra | Año | Notas |
|--------|-------|-----|-------|
| DGT CAT FeatureServer (censo legal exacto) | **1.292** CATs activos | 2024 | [VERIFICADO DB — `entity_source: dgt_cat = 1.292` en `07-COVERAGE-STRATEGY.md §2 SEG-1`] |
| SIGRAUTO red concertada | **595 CATs + 25 fragmentadoras** | may-2026 | [VERIFICADO fuente — `sigrauto.com/donde-puedo-entregar-mi-vehiculo`, actualizado 18-05-2026] |
| AEDRA asociados | **>600 miembros** | 2024 | [VERIFICADO fuente] |
| DesguacesOficiales (directorio) | ~2.049 listados | ~2024 | [VERIFICADO fuente — citado en arquitectura §2 SEG-1; incluye inactivos/dudosos] |

**El denominador de desguaces es exacto:** 1.292 CATs autorizados (DGT, censo legal).
SIGRAUTO 595 es subconjunto concertado, AEDRA 600+ es subconjunto asociado.
Los 2.049 de DesguacesOficiales incluyen inactivos → no es denominador.

**Estado CARDEEP SEG-1:** 100% SELLADO [VERIFICADO DB — `kind=desguace: 1.645` en DB,
supera el DGT 1.292 porque incluye inactivos y desguaces de directorio aún sin verificar
contra el censo legal].

### 1.4 Tabla denominador consolidado

| Segmento | Denominador oficial | Fuente | Cobertura CARDEEP actual | Cobertura % |
|----------|---------------------|--------|--------------------------|-------------|
| Concesionarios franquiciados | 2.143 (grupos) / 5.358 (instalaciones) | FACONAUTO/DBK 2024 | 1.844 `kind=concesionario_oficial` | **86,1%** de grupos / 34,4% de instalaciones [VERIFICADO DB] |
| Desguaces CATs | 1.292 (exacto) | DGT CAT legal | 1.645 (incluye inactivos/directorios) | **>100% denomin. legal** (sobrecolección, deflación pendiente) [VERIFICADO DB] |
| Compraventas POS indep. | ~1.662 floor / ~27k techo | PA / CNAE 4511 | 39.308 `kind=compraventa` | **>100% floor** (overcount incluye plataformas → deflación necesaria) [VERIFICADO DB] |
| Garajes que venden | indefinido hasta deflación | CETRAA ~20k (todos talleres) | 7.220 `kind=garaje`, `sells_cars` NULL en 7.201 | **INMENSURABLE sin deflación** [VERIFICADO DB] |
| Plataformas (Tier-1 + open) | ~23 plataformas | Registro propio | 18 `kind=plataforma` | **78%** [VERIFICADO DB] |

---

## 2. PARTICULAR vs DEALER — split, señal de detección, estrategia de filtrado

### 2.1 Split actual en DB [VERIFICADO DB — queries directas 2026-06-14]

| Kind | Entidades | Notas |
|------|-----------|-------|
| `particular` | **328.776** | 220.340 de wallapop_wholesale · 108.383 de milanuncios_wholesale · 53 legacy buckets coches.net |
| `compraventa` | **39.308** | dealers independientes de ocasión |
| `garaje` | **7.220** | talleres, la mayoría sin señal de venta activa |
| `concesionario_oficial` | **1.844** | redes OEM |
| `desguace` | **1.645** | CATs + directorios |
| `subasta` | **97** | subastas B2B |
| `plataforma` | **18** | plataformas como entidad |
| `oem_vo_portal` | **14** | portales VO de marca |
| `importador` | **11** | importadores independientes |
| `rent_a_car_vo` | **6** | flotas rent-a-car VO |
| `cadena` | **4** | cadenas multimarca |
| **TOTAL** | **378.943** | |

**Total dealers/POS (non-particular):** **50.167** entidades [VERIFICADO DB]  
**Total particulares C2C:** **328.776** entidades [VERIFICADO DB]

### 2.2 `sells_cars` — estado de población [VERIFICADO DB]

El campo `sells_cars` indica si un POS activamente vende coches. Estado actual:

| Kind | sells_cars=True | sells_cars=False | sells_cars=NULL |
|------|-----------------|-----------------|-----------------|
| `garaje` | 0 | 19 | **7.201** (99,7% sin poblar) |
| `concesionario_oficial` | 226 | 0 | 1.618 (87,7% sin poblar) |
| `compraventa` | 36.497 | 0 | 2.811 (7,1% sin poblar) |
| `desguace` | 346 | 0 | 1.299 (78,9% sin poblar) |
| `particular` | 328.776 | 0 | 0 |

**El campo `sells_cars` está prácticamente sin poblar para `garaje`** (99,7% NULL) y
significativamente sin poblar para `desguace` (78,9%). El deflactor SEG-5 (F4e) no ha
ejecutado. Los 7.220 garajes incluyen talleres puros sin venta de coches — el denominador
del segmento garaje es INFLADO por definición hasta que `sells_cars` se resuelva.

**¿Qué significa `sells_cars`?** Es una señal booleana que dice "este punto de venta tiene
inventario activo en venta o aparece como vendedor en alguna plataforma". Cuando es NULL,
la señal no ha sido computada (no hay evidencia recopilada de si vende o no).

### 2.3 ¿El producto debe servir los 328k particulares?

**Respuesta directa:** Depende del caso de uso del producto, pero hay argumentos fuertes
en ambos sentidos:

**A FAVOR de incluir particulares:**
- 328.776 entidades = inventario C2C REAL con 500.334 coches disponibles [VERIFICADO DB].
- La wallapop tiene 305.323 listings de privados y milanuncios 76.439 — es el 50%+ del
  mercado de ocasión.
- Un comprador busca coche sin importar si es dealer o particular.

**EN CONTRA / argumento de filtrado:**
- El mandato del proyecto es "puntos de venta" (POS) — una persona vendiendo su único coche
  NO es un punto de venta.
- Los 328k particulares incluyen vendedores únicos que no volverán → ruido para un B2B que
  quiere contactar dealers.
- La `entity_kind` ya los separa: el filtrado es `WHERE kind != 'particular'`.

**Recomendación arquitectónica:** mantener ambos en DB (ya lo hace), pero exponer la API
con filtro por defecto `kind != 'particular'` para el producto POS, y activar C2C solo
cuando el cliente/caso de uso lo requiera explícitamente.

### 2.4 Señal para detectar "particular-revendedor" (dealer encubierto)

**Distribución de particulares por número de coches disponibles** [VERIFICADO DB]:

| Bucket | N particulares | N vehículos | % del total particulares |
|--------|---------------|-------------|--------------------------|
| 0 coches activos | (residual) | 0 | — |
| 1 coche | **281.855** | 281.855 | **85,7%** |
| 2-3 coches | **45.599** | 92.489 | 13,9% |
| 4-10 coches | **1.107** | 5.787 | 0,34% |
| 11-30 coches | **161** | 2.353 | 0,05% |
| >30 coches | **54** | 117.850 | 0,016% |

**Los 54 particulares con >30 coches son casi todos legacy province-buckets de coches.net**
[VERIFICADO DB — los top 20 son "Particulares coches.net PROVINCIA", buckets heredados que
agrupan privados por provincia, no entidades únicas reales]. Los 328.723 per-seller reales
(wallapop 220.340 + milanuncios 108.383) presentan distribución sana:

- 85,7% tienen 1 solo coche → particulares genuinos.
- 13,9% tienen 2-3 coches → algunos son revendedores esporádicos, mayoría genuinos.
- 0,34% tienen 4-10 coches → zona gris: posibles revendedores activos.
- 0,05% tienen 11-30 coches → señal fuerte de dealer-encubierto.

**Umbral de detección propuesto:** `v_count >= 5 AND platform_attributed = 'professional'`
en la fuente o `v_count >= 10` sin otra señal → clasificar como `kind=compraventa`
candidato, verificar con VAM. Wallapop ya retorna `type=professional` vs `type=normal`
en `/api/v3/users/{id}` [VERIFICADO fuente — wallapop.md §0] — esa señal es la más limpia
para dealers encubiertos en wallapop. milanuncios retorna `sellerType=professional` o
`sellerType=private` en el ad [VERIFICADO fuente — SEGMENT_GAPS.md §6].

---

## 3. WALLAPOP EXHAUSTIVO — ¿el cap 8.000 es de API o de memoria?

### 3.1 Origen del cap — diagnóstico confirmado [VERIFICADO fuente — wallapop.md §7]

**El cap 8.000 NO es de la API.** El cursor `order_by=newest` puede caminar hasta
**~224k coches distintos** (el techo del cursor plano) sin ningún límite server-side
en el número de páginas [VERIFICADO fuente — wallapop.md §7.1: "a bare cursor walk
walked 5,800+ pages with RSS flat at 39→71 MB and no server-side cap"].

El cap de 8.000 era un parámetro de configuración del conector (`--target 8000` por
defecto) combinado con una muerte silenciosa por OOM en corridas con 15 procesos
concurrentes, cuando el host llegaba al 92% de RAM [VERIFICADO fuente — wallapop.md §7.2].

**Causa exacta del OOM:** tres estructuras de memoria monotónicas:
1. `seen_ids` (~22 MB en 224k coches).
2. `harvested_cageable` tuple set (~61 MB en 224k coches).
3. `seller_cache` de 64k `SellerRef` (~30 MB).
Total proyectado a 651k: ~325 MB, suficiente para cruzar el límite en un host al 92%.

**Fix implementado** (`pipeline/platform/wallapop_wholesale.py`):
- `seen_ids` → `_BoundedSeen` FIFO capped 300k.
- `harvested_cageable` → eliminado, reemplazado por contador entero.
- `seller_cache` → `_BoundedSellerCache` LRU capped 50k.
[VERIFICADO fuente — wallapop.md §7.2: "verified: bounded run walked the flat pass to
completion with seen_ids and seller_cache pinned at their caps, 0 window errors"]

### 3.2 Ceiling real del cursor plano [VERIFICADO fuente — wallapop.md §7.1]

| Profundidad | Coches distintos | Yield/página |
|-------------|-----------------|--------------|
| página 200 | 8.013 | 40,0 |
| página 1.000 | 39.985 | 40,0 |
| página 5.000 | 193.384 | ~38,7 |
| página 5.740 | 220.051 | 29/pág (saturación) |
| **límite práctico** | **~224k** | yield → 0 |

**El cursor plano satura en ~220-224k coches.** Para alcanzar los 651.199 restantes:
sweep por keyword×centroid (40 marcas × 8 centroides ES, `order_by=most_relevance`,
geo honrada) + partición por provincia/precio. [VERIFICADO fuente — wallapop.md §7.1]

### 3.3 Estado actual en DB [VERIFICADO DB — 2026-06-14]

- Wallapop en DB: **584.160 vehículos** (compraventa 327.892 + particular 256.153 + otros).
- Wallapop ceiling declarado: **651.199** [VERIFICADO fuente — SEGMENT_GAPS.md §2].
- Profundidad actual: **89,7%** del total declarado.
- Gap restante: ~67k coches + migración legacy garaje-bucket (22.900 coches en 48 buckets
  que aún no se han re-apuntado a entidades per-seller `kind=particular`).

### 3.4 Estrategia concreta para enumeración exhaustiva sin OOM

Con el fix de memoria implementado, la estrategia es:

1. **Paso A — cursor plano bounded:** ejecutar `--target 250000` (supera el ceiling de
   224k, el cursor se detiene solo al saturar). Sin OOM: `_BoundedSeen` + LRU seller cache.
2. **Paso B — keyword×centroid sweep:** 40 marcas × 8 centroides ES (Madrid, Barcelona,
   Valencia, Sevilla, Bilbao, Zaragoza, Málaga, Palma), `order_by=most_relevance`, global
   `seen_ids` shared con paso A para dedup por `item.id`. Esto captura el catálogo más allá
   del cursor plano (~427k adicionales).
3. **Paso C — province×price-band sharding** (análogo a milanuncios): para provincias con
   >10k listings, partir por banda de precio (0-5k, 5k-15k, 15k-30k, >30k) para no
   saturar ningún cursor de subquery.
4. **Cleanup:** `cleanup_legacy_buckets()` re-apunta los 22.900 legacy bucket cars a sus
   per-seller twins y retira buckets vacíos.

**Costo:** €0 (curl_cffi, no proxy requerido para receta geolocalizada) [VERIFICADO fuente].

---

## 4. COBERTURA GEOGRÁFICA — 52 provincias

### 4.1 Estado completo [VERIFICADO DB — 2026-06-14]

**Ninguna provincia tiene 0 entidades** — las 52 están presentes. [VERIFICADO DB]

**Tabla completa de dealers (non-particular) por provincia:**

| Rank | Código | Provincia | Total entidades | Dealers | Particulares |
|------|--------|-----------|-----------------|---------|-------------|
| 1 | 28 | Madrid | 51.281 | 8.040 | 43.241 |
| 2 | 08 | Barcelona | 40.296 | 5.048 | 35.248 |
| 3 | 46 | Valencia | 22.564 | 2.844 | 19.720 |
| 4 | 03 | Alicante | 17.787 | 2.060 | 15.727 |
| 5 | 29 | Málaga | 17.320 | 1.887 | 15.433 |
| 6 | 41 | Sevilla | 15.418 | 2.121 | 13.297 |
| 7 | 30 | Murcia | 13.735 | 1.544 | 12.191 |
| 8 | 43 | Tarragona | 9.298 | 944 | 8.354 |
| 9 | 18 | Granada | 8.822 | 1.009 | 7.813 |
| 10 | 15 | A Coruña | 8.669 | 1.434 | 7.235 |
| ... | ... | ... | ... | ... | ... |
| 43 | 49 | Zamora | 1.424 | 248 | 1.176 |
| 44 | 16 | Cuenca | 1.502 | 191 | 1.311 |
| 45 | 19 | Guadalajara | 2.717 | 165 | 2.552 |
| 46 | 40 | Segovia | 1.354 | 133 | 1.221 |
| 47 | 44 | Teruel | 1.011 | 133 | 878 |
| 48 | 05 | Ávila | 1.261 | 136 | 1.125 |
| 49 | 34 | Palencia | 1.261 | 150 | 1.111 |
| 50 | 42 | Soria | 705 | 101 | 604 |
| 51 | 52 | Melilla | 735 | 17 | 718 |
| 52 | 51 | Ceuta | 235 | 9 | 226 |

### 4.2 Gaps geográficos detectados [VERIFICADO DB]

**Ceuta (51):** 235 entidades totales, 9 dealers. Extremadamente escaso.
- Explicación probable: Ceuta y Melilla están fuera del alcance natural de wallapop/milanuncios
  para el grueso de listings. Las 226 entidades "particular" de Ceuta son residuales.
- Gap real: solo 3 compraventas y 3 concesionarios_oficial registrados para una ciudad de
  ~84k habitantes con múltiples marcas representadas.
- Estrategia de cierre: censo directo (Cámara de Comercio de Ceuta, búsqueda manual OEM
  locator para Ceuta) — el volumen es pequeño y enumerable a mano.

**Melilla (52):** 735 entidades, 17 dealers. Mejor que Ceuta pero aún thin.
- 4 concesionarios_oficial, 12 compraventas, 0 garajes, 1 desguace.
- Estrategia: ídem Ceuta.

**Provincias en zona de riesgo (<150 dealers):**
- Soria (42: 101), Guadalajara (165: residual de plataformas urbanas lejanas),
  Segovia (133), Teruel (133).
- Estas provincias tienen pocos dealers reales (economías pequeñas) pero el número
  puede estar subestimado por baja presencia en plataformas nacionales.

**Canarias (35+38) — CUBIERTOS:**
- Las Palmas (35): 5.684 total, 789 dealers.
- Santa Cruz de Tenerife (38): 5.718 total, 752 dealers.
- Ambas bien representadas vía wallapop y plataformas nacionales.

**Baleares (07) — CUBIERTA:** 8.446 total, 1.031 dealers. OK.

### 4.3 Validez de los números geográficos

Los 50.167 dealers distribuidos en 52 provincias incluyen entidades de fuentes muy
heterogéneas (wallapop, milanuncios, OSM, OEM locators, etc.). La distribución geográfica
refleja la presencia en plataformas, no necesariamente la densidad real de POS físicos.
Provincias rurales con pocas plataformas digitales pueden estar bajo-representadas.

---

## 5. LONG-TAIL — fuentes y estrategias para garajes/desguaces pequeños

### 5.1 Fuentes actuales que traen long-tail [VERIFICADO fuente — longtail_families.md]

| Fuente | Entidades aportadas | Estado |
|--------|---------------------|--------|
| OSM `shop=car` | 9.956 | Activo, ingestado |
| DGT CAT | 1.292 desguaces | Activo, 100% sellado |
| AEDRA directorio | 586 desguaces | Activo |
| Long-tail family recipes (7 familias CMS/DMS) | 85 dealers, 7.205 coches | Activo, VAM TRUSTWORTHY |
| Motorflash (DMS) | 201 entidades | Activo |
| OEM locators (múltiples marcas) | ~2.000 entidades | Parcialmente activo |

**Familias CMS/DMS detectadas** (369 dominios propios, 283 alcanzables):
- WordPress: 157 dominios (42,5%) → una receta cubre el mayor bloque.
- Genérico/custom: 73 dominios (19,8%).
- Unreachable: 86 dominios (23,3%) → WAF/DNS muertos, requieren stealth.
- DMS vendor (inventario.pro, motorflash): 28 dominios (7,6%).
- Framework (Next/Astro/Nuxt): 17 dominios (4,6%).
- Builder (Wix/Ueni/Google Sites): 8 dominios (2,2%).

### 5.2 Directorios sin explotar para long-tail [ASUMIDO/parcialmente VERIFICADO fuente]

| Fuente | Potencial | Obstáculo | Estrategia |
|--------|-----------|-----------|------------|
| **Páginas Amarillas** — "garaje", "compraventa" | ~30k listados talleres, ~1.662 compraventas | Rate-limit, CAPTCHA leve | curl_cffi + paginación by-province. Ya citado en arquitectura como fuente Discovery |
| **Google Maps/Places API** | ~20-30k POIs `shop=car_repair` + `car_dealer` | ToS prohíbe scraping de resultados; Places API de pago ($0.032/request) | Usar FSQ/Overture (permissive license) como alternativa; Google Places solo si el coste es autorizado |
| **Overture Maps** (permissive license, sustituto de Google Places) | Cubre toda España, ~10k+ POIs relevantes | Descarga masiva en Parquet (tera-escala), requiere filtrado | `SELECT * FROM places WHERE category IN ('car_dealer','auto_repair') AND country='ES'` en DuckDB local — €0, permissive |
| **Foursquare Open Places (FSQ)** | ~5-10k POIs España | Requiere cuenta FSQ gratuita | Descarga directa monthly dump, filtrado por categoria. Ya en arquitectura como fuente |
| **CETRAA / CCAA registries** | ~20.000 talleres total España (filtrar los que venden) | Datos dispersos por CCAA, formatos heterogéneos | RASIC Socrata (catalán), CyL CSV descargable, CETRAA gateway — citados en arquitectura |
| **Milanuncios "Profesionales"** | ~66.005 anuncios de profesionales | Ya parcialmente cubierto | Mejorar atribución de entidades dealer en milanuncios: 15.188 compraventas ya detectadas vía `sellerType=professional` |
| **coches.net dealer profiles** | ~7.269 dealers detectados | Ya cubierto | Exhaustión del segmento New/Km0/Renting pendiente (~9-10k coches gap) |
| **AutoScout24 dealer attribution** | ~278k coches atribuibles a miles de dealers | Ya parcialmente cubierto (262 dealers, AS24 receta construida) | Drain completo de AS24 (plataforma como entidad, F4a en roadmap) |
| **Listados GANVAM/FACONAUTO** | ~2.000 miembros + red agentes | No directamente exportable en masa | Scraping de directorios de asociación + OEM locators ya implementados |
| **Asociaciones provinciales** (AMDA Madrid 147, Gremi BCN 693) | ~840 entre estos dos | Páginas web con listados | Scraping semi-manual de listados; volumen enumerable |

### 5.3 Estrategias concretas para el long-tail no cubierto

**Estrategia 1 — Overture Maps dump (prioridad alta, €0):**
DuckDB + Parquet dump de Overture Maps (`places` dataset) para España, filtrando
`category_main IN ('car_dealer', 'automotive', 'vehicle_dealer')`. Fuente OpenStreetMap
+ propietaria bajo licencia permisiva. Diferente mecanismo de captura que OSM → válido
para Chapman.

**Estrategia 2 — CCAA taller registries + `sells_cars` classifier (prioridad alta):**
Ingerir los ~20.000 talleres de los registros CCAA (RASIC, CyL, CETRAA) y aplicar
classifier local (LLM barato: Haiku) sobre nombre + descripción + presencia en
plataformas para derivar `sells_cars`. Convierte 7.220 garajes NULL en entidades
verificadas o eliminadas del denominador.

**Estrategia 3 — Chapman capture-recapture (infraestructura ya lista):**
La tabla `entity_source` + `entity_cluster` ya permite calcular el estimador Chapman
entre fuentes ortogonales. El denominador real SEG-4/SEG-5 emerge de cruzar OSM ∩ PA ∩
AS24-atribución ∩ Overture. Ejecutar el primer estimador por provincia.

**Estrategia 4 — Motorflash y DMS expansion (prioridad media):**
Motorflash ya tiene 201 dealers en DB. El DMS vendor cubre 28 dominios. Expandir a
familias CMS WordPress (157 dominios, una receta para todos) = el bloque de mayor ROI
en long-tail propio.

**Estrategia 5 — Desguaces AEDRA + DesguacesDirecto (cross-check, €0):**
AEDRA tiene >600 socios. DesguacesDirecto lista 1.386. Cruzar contra los 1.645 en DB
para detectar huecos en el censo DGT y enriquecer con datos de contacto.

---

## 6. ESTADO DE VEHÍCULOS Y PLATAFORMAS [VERIFICADO DB — 2026-06-14]

### 6.1 Inventario vivo

| Métrica | Valor |
|---------|-------|
| Total vehicles en DB | **1.644.198** |
| Vehicles `status='available'` | **1.642.823** |
| Vehicles en compraventas | 1.075.157 (65,4%) |
| Vehicles en particulares | 500.334 (30,5%) |
| Vehicles en concesionarios_oficial | 40.852 (2,5%) |
| Vehicles en subastas | 7.336 (0,4%) |

### 6.2 Profundidad wallapop [VERIFICADO DB + fuente]

| Métrica | Valor |
|---------|-------|
| Wallapop declarado (SEGMENT_GAPS.md) | 651.199 coches ES |
| Wallapop en DB (vehicles) | 584.160 |
| Cobertura wallapop | **89,7%** |
| Gap restante (vehicles) | ~67k + 22.900 legacy bucket migration |
| Causa del gap | cursor no completado al 100% + legacy buckets pendientes de migrar |

### 6.3 Tier-1 grandes plataformas — profundidad total [VERIFICADO fuente — SEGMENT_GAPS.md]

| Plataforma | Declarado | DB edges (aprox) | Gaps segmento |
|------------|-----------|------------------|---------------|
| coches.net | ~282.700 | 272.903 (usados) | New ~6k · Km0 ~3k · Renting ~800 |
| wallapop | 651.199 | 584.160 (vehículos) | 0 segmentos; profundidad al 89,7% |
| coches.com | 117.745 (real) | en progreso | 0 (todos cubiertos) |
| autocasion | 135.452 | en progreso | 0 (todos cubiertos) |
| motor.es | ~51.540 | en progreso | 0 (todos cubiertos) |
| milanuncios | ~272.130 | en progreso | 0 (índice plano, cubierto) |

---

## 7. GAPS HONESTOS Y RESIDUOS CONFESADOS

1. **`sells_cars` unpopulated (garaje):** 7.201/7.220 garajes sin señal. El denominador
   SEG-5 es INMENSURABLE sin ejecutar F4e (deflación). Confeso, no oculto.

2. **Ceuta/Melilla cobertura thin:** 9 y 17 dealers respectivamente. Volumen real de POS
   físicos desconocido pero mayor que estos números. Require censo directo.

3. **Compraventas: overcount de 39.308 vs ~1.662 floor real:** Los 39.308 `kind=compraventa`
   incluyen dealers atribuidos desde plataformas (muchos reales), pero la cifra no ha sido
   deflactada contra el CNAE/PA denominador real. Muchos pueden ser el mismo POS descubierto
   por varias plataformas y no deduplicado a entidad única aún.

4. **Chapman no ejecutado:** La infraestructura existe (`entity_source`, `entity_cluster`)
   pero el estimador CR no ha corrido para dar `N̂` por segmento/provincia. El denominador
   SEG-4/SEG-5 sigue siendo "floor PA" vs "ceiling CNAE", sin intervalo de confianza.

5. **AS24 drain incompleto:** AutoScout24 tiene receta construida pero solo 262 entidades
   atribuidas (vs las ~278k listings que declara). F4a (plataforma como entidad + drain
   wholesale) es el siguiente movimiento de máximo ROI.

6. **Wallapop gap residual:** 89,7% de profundidad, ~67k coches por capturar + 22.900
   legacy bucket migration pendiente. Con el fix de memoria, el CLI puede completarlo.

---

## 8. FUENTES Y REFERENCIAS

### Fuentes web verificadas

- [DBK Observatorio Sectorial — Concesionarios 2025](https://www.dbk.es/es/detalle-nota/concesionarios-automovil-2025)
- [La Tribuna de Automoción — facturación 2024](https://www.latribunadeautomocion.es/2025/06/concesionarios-facturaron-48-406-millones-euros-2024-crecieron-numero-contratos-distribucion/)
- [SIGRAUTO — centros autorizados](https://www.sigrauto.com/donde-puedo-entregar-mi-vehiculo) (595 CATs + 25 fragmentadoras, actualizado 2026-05-18)
- [eInforma CNAE 4511](https://www.einforma.com/empresas/Comercio-Al-Por-Mayor-Y-Al-Por-Menor--Reparacion-De-Vehiculos-De-Moto/CNAE-4511-Venta-De-Automoviles-Y-Vehiculos-De-Motor-Ligeros.html)
- [INE DIRCE 2024](https://www.ine.es/dyngs/Prensa/es/DIRCE2024.htm)
- [GANVAM — mercado ocasión 2024](https://ganvam.es/el-mercado-de-ocasion-cumple-las-previsiones-y-cierra-2024-superando-los-dos-millones-de-unidades/)

### Documentos de arquitectura CARDEEP verificados

- `docs/architecture/07-COVERAGE-STRATEGY.md` — estrategia completa por segmento
- `docs/architecture/SEGMENT_GAPS.md` — gaps por plataforma Tier-1
- `docs/architecture/PARTICULARES_STATUS.md` — estado particular kind
- `docs/architecture/LONGTAIL_STATUS.md` — long-tail own-site harvest
- `docs/architecture/longtail_families.md` — familias CMS/DMS
- `docs/architecture/tier1_recipes/wallapop.md` — receta wallapop + fix OOM

---

*Dossier generado 2026-06-14. Todos los números de DB verificados con queries directas
a `cardeep-pg :5433`. Los números de fuentes externas están marcados [VERIFICADO fuente]
con URL. Los [ASUMIDO] son inferencias declaradas.*
