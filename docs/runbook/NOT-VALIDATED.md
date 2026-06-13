# NOT-VALIDATED — el apéndice honesto (FUERA del runbook)

> Lo intentado, aspiracional, roto, o pendiente de re-VAM. **No cumple la regla dura** (sin verdict
> TRUSTWORTHY persistido que avale el número, o discrepancia código↔doc, o conocido-roto). Declarado
> sin maquillaje; jamás se presenta como "funciona". Cada ítem lleva su evidencia. Verificado contra
> la DB viva **2026-06-13**.

---

## 1. Los 10 veredictos REFUTED (confesados, NO servidos)

`[VERIFICADO]` en la tabla `verification_verdict` (`verdict='REFUTED'`). Son outcomes de PRIMERA
CLASE (rutan la entidad FUERA del set servido), no fallos del verificador:

| id | subject_type | subject_key | primary_value | divergencia | qué |
|---:|---|---|---:|---:|---|
| 5 | entity_inventory | CDP-ES-46-NM30P5P0 | 77 | 0.0128 | inventario de entidad que no reconcilió |
| 55 | source | `oem_mg` | 70 | 0.6698 | count entidades ≠ declarado |
| 56 | source | `oem_byd` | 90 | 0.1509 | count entidades ≠ declarado |
| 57 | source | `oem_skoda` | 196 | 0.0884 | count entidades ≠ declarado |
| 59 | source | `oem_hyundai` | 174 | 0.0057 | count entidades ≠ declarado |
| 63 | source | `osm` | 9.956 | 0.1756 | count entidades ≠ declarado |
| 399 | platform_slice | CDP-ES-00-VMCZWW5N | 227 | 0.0542 | slice AS24 (no servido) |
| 544 | group_vam | `long_tail_families` | 10.178 | 0.9907 | no aditivo: ya en otros grupos |
| 548 | platform_slice | CDP-ES-00-XM91J1NZ | 111.498 | 0.1833 | coches.com 20.432 fantasmas cross-surface (clave-identidad = URL); fix → id 551 TRUSTWORTHY 91.066 |
| 560 | platform_segment | CDP-ES-00-XM91J1NZ:renting | 1.035 | 0.0010 | coches.com renting; corregido → id 564 TRUSTWORTHY 1.034 |

---

## 2. Deltas vivos sin re-VAM (el número validado va por detrás del vivo)

### 2.1 autocasion — el delta grande ✅ RESUELTO (re-VAM hecho 2026-06-13)
- **Cerrado.** El delta se re-derivó por 3 caminos ortogonales que concuerdan al dígito
  (`db_edges=111.844 == db_join_vehicles=111.844 == db_distinct_refs=111.844`, div 0.0) y se persistió
  **verdict id=638 TRUSTWORTHY (`platform_slice`)** vía `pipeline.verify.record_count_verdict`. El
  número del runbook para autocasion es ahora **111.844 (id 638)**; el viejo id 549 (15.765) queda como
  histórico. Migrado a [VALIDATION-INDEX.md](VALIDATION-INDEX.md) y
  [platforms/autocasion.md](platforms/autocasion.md). Ya NO es un delta pendiente.

### 2.2 wallapop cola profunda → ~651k (G1)
- El oráculo `remaining_documents` da el denominador ≈651.340; el validado es **565.128 (id 592)**.
  El resto exige paginación facet/cursor profunda aún no completada (band-boundary collapse por
  dedup). Pendiente de drenaje, no validado.

### 2.3 coches.net / wallapop / coches.com deltas (+1.235 / +10.225 / +1.022)
- Ingesta viva posterior al verdict. El número validado es el `verdict_N`; el live es la frontera de
  re-VAM pendiente (no contradice el verdict, solo lo supera sin avalar).

### 2.4 Otros grupos — desfase veredicto↔DB
- Los verdicts 541/542/543 sellaron **37.319 / 166 / 27** a 00:37Z. La DB viva creció a **39.201 /
  215 / 6.785** por drenes posteriores commiteados. El delta de cada grupo **no** tiene aún un
  `verification_verdict` re-persistido a su valor vivo. **Acción:** re-emitir el VAM por grupo para
  cerrar el ledger a los valores vivos.

### 2.5 Motorflash — slice en drenaje activo ⚠
- verdict id 619 avala **187** aristas (sellado a 18:46Z). El conector `motorflash_wholesale.py` sigue
  drenando en vivo: la DB viva marca **1.207+ aristas y subiendo** (`[VERIFICADO]` esta sesión,
  creciendo durante el muestreo; techo ~50k = ~1.000 dealers × ~50 coches). El slice NO cumple aún la
  idempotencia "re-run = 0 nuevos".
- **El número del runbook para Motorflash es 187 (id 619)**, registrado con su verdict TRUSTWORTHY
  confirmado; el vivo (1.207+) es cross-check `[VERIFICADO]`. Ver
  [platforms/motorflash.md](platforms/motorflash.md).
- **Acción de cierre:** re-emitir el VAM al valor de meseta cuando el drenaje cierre.

---

## 3. Discrepancia código↔documentación

### 3.1 Governor milanuncios (comentario engañoso)
- El connector `milanuncios_wholesale.py` (L54/L1186/L1200) **afirma** que `searchapi.gw.milanuncios.com`
  está en la "JSON_API class", pero el host **NO está en `_HOST_RATE_CLASSES`** (governor.py L96-141
  solo registra `web.gw.coches.net`, `api.wallapop.com`, `gql.autocasion.com`, `es.renew.auto`,
  `scs.audi.de`, `kiaokasion.net`, `services.flexicar.es`, `api-carmarket.ayvens.com`). En ejecución
  **hereda STEALTH 0,7 req/s**, no JSON_API. No invalida el resultado VAM (id 554 cuadra al coche),
  pero el comentario es engañoso. **Acción:** registrar el host en `_HOST_RATE_CLASSES` (si el
  gateway tolera JSON_API) o corregir el comentario.

---

## 4. Capa de motor no poblada / no construida

### 4.1 `organization` / `group_vam` VAM muerto
- Tabla `organization` **vacía (0 filas vivas)** `[VERIFICADO]`, `entity.org_id` NULL. La capa
  cadena/grupo (`0007`) existe en esquema pero no poblada.

### 4.2 auto_repair efectos caros (P10-scaffold)
- `refingerprint`/`escalate_tier`/`re_receta` con `succeeded=FALSE`, `repair_outcome='pending'`,
  `_SPEND_GATED_ACTIONS`. El LAZO corre real (€0); el EFECTO con gasto espera autorización P10. Es la
  única excepción declarada (marcada en `health.py:325-331`), no un stub oculto.

### 4.3 Escalada Tier-1 en `fetch.py`
- El seam lanza `NotImplementedError` (por diseño — no fallback silencioso). El motor
  camoufox/Playwright vive FUERA de `fetch.py` (se usó vía `coches_net_segments.py` /
  `cage_autorola_bca_subastas.py`, validado), pero `fetch.py` por sí solo NO sirve Tier-1.

### 4.4 Defectos de calidad flagged (sin spend)
- `platform.listing_counter` NULL en las 24 plataformas → usar `count(platform_listing)`, no el
  counter. API sin endpoint propio `oem_vo_portal` (HTTP 400 guard en `/platforms/{cdp_code}`).

### 4.5 Watermark cross-platform ≈134k excedentes — MEASURE-ONLY
- ≈134.027 filas excedentes (14,36 %, cota inferior estricta, verdict id 574). **NO se ha ejecutado
  merge:** es una medición validada, no una capacidad de deduplicación activa. El merge cross-seller
  está fuera de v1 (riesgo de over-merge; `photo_hash` aún sin poblar).

---

## 5. Fuentes reconocidas sin superficie limpia (no conectadas)

### 5.1 OEM-VO amurallados/diferidos
| Marca | Superficie | Estado | Motivo |
|---|---|---|---|
| **Mazda** (`mazdaselected.es`) | Mazda Selected | ⛔ AMURALLADO | TLS connect timeout a `curl_cffi`; sin superficie limpia (necesitaría camoufox/otro ingress). |
| **Honda** (`vehiculosdeocasion.honda.es`) | Honda Approved | ⚪ SIN DATA-LAYER | jQuery SSR; el buscador pagina re-GETeando la MISMA URL HTML (no hay JSON). |
| **Suzuki** (`auto.suzuki.es`) | directorio de ~30 subsitios `redsuzuki.es` | 🟡 DIFERIDO (long-tail) | Cada subsitio renderiza su HTML sin JSON central; scrape per-dealer. |

### 5.2 Cadenas / rent-a-car / subastas sin probe ni aristas
| Grupo | Miembro | Estado |
|---|---|---|
| rentacar_vo | Sixt ES | Sin storefront VO español ("GW" solo en `sixt.de`). Ausente de `entity`. |
| rentacar_vo | Europcar ES ("2nd Move") | Ex-flota solo vía B2B con registro (`b2b.2ndmove.eu`). Cagearla duplicaría. |
| rentacar_vo | Goldcar | Sitemap = solo alquiler/app; ex-flota vía 2ndMove B2B. Sin surface propio. |
| vo_chains | Aurgi, GpsAutos, Crandon | Citados como futuros `chain`; sin probe ni aristas en DB. |
| subastas | Allane (Sixt Leasing) | Remarketer DE-céntrico; sin surface de stock VO ES. Ausente de `entity`. |
| subastas | Aucto (`aucto.es`) | Connection refused / no alcanzable. Ausente de `entity`. |

### 5.3 Ola new-channels — gateado / inalcanzable / retirado (probado esta sesión)

> Probados en la ola new-channels (faciliteacoches+RACC, LocalizaVO, importador). Sin verdict
> TRUSTWORTHY que concuerde con la DB viva → FUERA del runbook. Evidencia `[VERIFICADO]` esta sesión.

| Unidad | Surface | Estado | Evidencia |
|---|---|---|---|
| **MODRIVE** (`modrive.com`) | importador own-site (SSR JSON-LD ItemList) | ⚪ RETIRADO de DB | El verdict id 626 selló 19 aristas; la DB viva tiene **0 listings y 0 platform row** para `CDP-ES-00-MVRE0FYC` (`[VERIFICADO]`: ni `platform_listing` ni fila `platform`). El verdict ya NO concuerda con la DB → no registrable. El catálogo full (2.021 coches) vive en un widget AutoUncle de TERCEROS (host distinto), no es superficie propia. |
| **CarCollect** (`carcollect.com`) | B2B auction | ⛔ GATED | `www.carcollect.com` = sitio marketing HubSpot CMS (sitemap 821 URLs, CERO detalle per-lote; "8.154 en vivo" es contador de marketing). `trade.carcollect.com` (Next.js SPA) 308→`/login` y todo `/api/*` 307→`/login` anónimo. B2B-only (cuenta + verificación + fee 82€/coche). Sin data-layer anónimo. Ausente de `entity`. |
| **Manheim España** (`manheim.es`) | B2B remarketer | ⛔ GATED (sin credenciales) | Catálogo tras login de comprador; sin credenciales = bloqueo real. Ausente de `entity`. |
| **Importador lead-gen (4 sitios)** | WordPress lead-gen / info | ⚪ SIN STOCK MACHINE-READABLE | De los candidatos de la censada `kind='importador'`, solo MODRIVE exponía stock own-site curl_cffi-alcanzable (y se retiró). El resto son sitios WordPress lead-gen / informativos SIN catálogo de stock propio legible por máquina (declarado en el docstring de `group_importador_wholesale.py`). Las entidades `kind='importador'` reclasificadas (Carismatic ×4, Trend Cars ×6) NO tienen aristas propias cosechadas (`[VERIFICADO]`: 0 `platform_listing` propios) → no es slice validable. |
| **Raceocasion / Europa Subastas** | subastas | ⛔ NO ALCANZADO | Ausentes de `entity` (`[VERIFICADO]`: 0 filas por `trade_name`/`website`). No expusieron superficie pública anónima cosechable en esta ola. |

---

## 6. Long-tail no validado

1. **Las 89 unreachable genuinamente muertas/walled** (39 NXDOMAIN + 50 hard wall) — confirmadas
   no-recuperables por camoufox stealth. Negocios muertos / dominios expirados / CF-DataDome-SSL
   roto. **No hay receta porque no hay superficie.**
2. **avolo.net** (HTTP 500, shell de error) y **renaultleioa.es** (renderiza pero 0 precios own-site;
   sus links apuntan off-site a agregadores). Resuelven pero sin stock own-site que cagear.
3. **9.828 cars own-site sin familia asignada** (de los 20.165 globales, 10.178 family-tagged; el
   resto en entities con website sin receta de familia). Long-tail real **pendiente** de asignar a
   una familia — no validado como cosechado. (Nota: el `primary_value=10.178` del verdict REFUTED 544
   es exactamente este conjunto family-tagged, no aditivo a los otros grupos.)
4. **Roster generic excluido honestamente** (en docstring de `family_generic_custom`): homepages OEM
   /global (ford.com, maserati.com, honda.es, polestar.com, lancia.es, mopar.eu, copart.es),
   delegadores cuyo stock vive en otro connector (es.renew.auto, quadis.es, concesionarios.seat,
   lexusauto.es, yomovo.es), shells JS sin cards SSR (automotordursan.com, automovilesroel.es,
   promosale.es, grupoadarsa.com, stylecarcanarias.com), y hosts parked/thin. Construir receta para
   un shell JS o homepage de marca **fabricaría propiedad** → se saltan, no se fingen.
5. **Miembros builder sin superficie machine-readable** (Wix warmupData, Squarespace/BaseKit SSR
   vacío, Google Sites contacto): reachable-pero-sin-inventario-SSR. De 9 members builder, solo 2
   productores.
6. **grupogamboa.com, setienherra.es** (inventario.pro): comparten template pero devolvieron cert
   errors; probable misma familia, **no confirmados** como cosechados.

---

## 7. Descubrimiento intentado SIN cierre (fase DESCUBRIR)

> Lo validado de la ola de descubrimiento está en [03-DISCOVERY.md](03-DISCOVERY.md) y en el ledger
> (association +409, DealerK own-site 327 / id 609, geo-sweep +68). Aquí va lo que se intentó y NO
> cumple la regla dura.

### 7.1 `paginas_amarillas` / discover_directories — DRY-RUN, +0 escrito
- El frente corrió pero el report `docs/research/paginas_amarillas_upsert_report.json` marca
  `"committed": false` (new=62 propuestas: 36 concesionario + 18 compraventa + 6 desguace + 2 garaje).
- `[VERIFICADO]` en la DB viva: `count(entity WHERE first_discovered_source='paginas_amarillas')` =
  **0**; `count(entity_source WHERE source_key='paginas_amarillas')` = **0**. Sin escritura no hay
  unidad de descubrimiento → **NO entra al runbook**.
- **Acción de cierre:** re-correr con `--commit` (tras revisar las 62 propuestas) y re-contar la DB.
  (La `directory` `source_group=9.953` viva es OSM/censo legado, NO este frente.)

### 7.2 Asociaciones AMURALLADAS (sin lista pública enumerable)
| Asociación | Alcance estimado | Estado | Motivo |
|---|---|---|---|
| **Faconauto** | ~2.018 dealers (federación) | ⛔ AMURALLADO | sin lista de socios pública; solo gateway. |
| **GANVAM** | ~7.500 firmas | ⛔ AMURALLADO | herramientas de socio tras login; sin directorio público. |
| **ANCOVE** | compraventa nacional | ⛔ AMURALLADO | "contenidos sólo para afiliados". |
| **ANCOPEL** | concesionarios Opel | ⛔ ROTO | página `concesionarios-asociados` da 404 en vivo; widget de mapa desaparecido. |
| **AECS zona-asociados** | zona privada Stellantis | ⛔ AUTH-WALLED | `zona-asociados.*` tras login (el `directorio-asociados` público SÍ se minó → 74 dealers, validado). |

Probadas y excluidas honestamente, no adivinadas. Sin superficie pública no hay descubrimiento.

### 7.3 Cierre geográfico al 100 % — PENDIENTE
- El barrido geo es por **muestreo** (capital + 2ª/3ª ciudad por provincia), no censo exhaustivo del
  long-tail. WebSearch devuelve la primera página por consulta; quedan pueblos pequeños sin barrer.
- Para cerrar el denominador (~44k suelo Páginas Amarillas) la vía correcta es ingerir los **dumps geo
  legales** (Foursquare OS Places Apache-2.0, Overture CDLA) + Páginas Amarillas por rúbrica — ya
  catalogados en `SOURCES_ES.md`, **fuera del alcance** de esta ola. Google Places API descartado por
  ToS (prohíbe indexar/cachear).
- **Enriquecimiento detectado (no nuevo):** ~20 candidatos deduplicados por `nombre+municipio` eran
  dealers YA en el censo vía marketplaces pero con `website IS NULL`; el sweep halló su web propia →
  oportunidad de back-fill de `website` para habilitar cosecha own-site. **No ejecutado**, registrado.

---

> **Cierre.** Todo en este apéndice está FUERA del runbook por una razón declarada y verificable.
> Cuando una de estas unidades cierre end-to-end con un `verification_verdict` TRUSTWORTHY nuevo,
> migra a [VALIDATION-INDEX.md](VALIDATION-INDEX.md) y a su `platforms/<slug>.md` siguiendo el
> protocolo de bitácora viva ([README.md](README.md) §4).
