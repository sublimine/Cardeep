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

### 2.1 autocasion — el delta grande ⚠
- verdict id 549 avala **15.765**. La DB viva marca **111.827 aristas** (medido esta sesión; el
  archivo de dominio registró 107.612 — la cosecha siguió drenando, deriva +4.215). El salto vino de
  harvests posteriores **sin un nuevo verdict VAM**. El SCOREBOARD reclama 49.391 pero tampoco hay
  `verdict_id` que lo avale.
- **El número del runbook para autocasion es 15.765 (id 549).** Los ~112k = **pendiente de re-VAM**.
- **Acción de cierre:** re-correr `record_count_verdict` sobre la slice viva y persistir un verdict
  nuevo antes de subir el número.

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

> **Cierre.** Todo en este apéndice está FUERA del runbook por una razón declarada y verificable.
> Cuando una de estas unidades cierre end-to-end con un `verification_verdict` TRUSTWORTHY nuevo,
> migra a [VALIDATION-INDEX.md](VALIDATION-INDEX.md) y a su `platforms/<slug>.md` siguiendo el
> protocolo de bitácora viva ([README.md](README.md) §4).
