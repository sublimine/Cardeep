# CARDEEP — Censo de fuentes de descubrimiento · ESPAÑA (F1)

> Artefacto-gate de la Fase F1. Producido por el workflow `cardeep-f1-census-es`
> (56 agentes, 926 tool-uses, barrido vivo 2026-06-12) y **re-verificado por mano
> propia del Director** en las cifras que cargan peso (ver §7). Cada fuente está
> marcada [VERIFICADO] (fetcheada en vivo este día) o [ASUMIDO] (inferida, sin abrir).
>
> Regla de lectura: una cifra solo es TRUSTWORTHY con quórum ≥2 vías. Las cifras de
> contador vivo (inventario de plataforma) driftan a diario; se re-derivan al usarlas.

---

## 1. Resumen ejecutivo

El mercado español de puntos de venta de coches se descompone en dos universos que
Cardeep trata por separado:

- **Universo de ENTIDADES** (el denominador a cerrar): los puntos de venta físicos —
  concesionarios oficiales, compraventas, garajes que venden, desguaces/CAT.
- **Universo de INVENTARIO** (el numerador a servir): el stock de coches, accesible
  por dos rutas — las **plataformas agregadoras** (gigantes Tier-1 + abiertas) y la
  **web propia de cada entidad** (long-tail por CMS/DMS).

**Denominador estimado de entidades (triangulación de fuentes ortogonales, §6):**
**~44.000 puntos de venta auto como suelo verificado** (Páginas Amarillas, contadores
en vivo), con techo **~50–90k** si se cuenta el registral CNAE 45 completo y Google
Places. Desglose por segmento con su fuente de verdad en §6.

**Hallazgo estratégico nº1:** AutoScout24.es (**278.329** anuncios, re-derivado por mí)
sirve HTML completo server-side a curl plano, con JSON-LD `AutoDealer` + `PostalAddress`
en cada PDP — **es la mayor fuente de atribución dealer→stock del país y es ABIERTA**.
Mejor ratio valor/esfuerzo de todo el censo. Punto de entrada de F3.

**Hallazgo estratégico nº2:** los OEM exponen sus redes de concesionarios por **APIs
JSON sin autenticar** (Kia 242, MG 212, BYD 106, VW sitemap 166 subsites, Skoda 215,
Toyota 98 grupos…) + portales VO oficiales con stock atribuido por dealer (renew 5.747,
Spoticar 6.334, Das WeltAuto ~10k, MB Certified 4.696…). Censo de red casi gratis.

---

## 2. Universo de INVENTARIO — plataformas (Tier-1 separado del resto)

Política del mandato: **Tier-1 (defensa dura) separado absolutamente** del resto en
datos, código y operación. Clasificación por barrido de cabeceras/desafío en vivo.

### 2.1 ABIERTAS (sin muro real hoy — atacar primero, €0)

| Plataforma | Stock ES (vivo) | Acceso | Atribución dealer | Nota |
|---|---|---|---|---|
| **autoscout24.es** `/lst` | **278.329** ✓mi-curl | HTML SSR + JSON-LD | Fuerte (`AutoDealer`+`PostalAddress`) | bloquea UA Anthropic; OK con UA Chrome. Sin sitemap. **GOLD** |
| **autocasion.com** | 121.985 | HTML + JSON-LD | Fuerte (58 `dealer`) | Cloudflare permisivo; PDP `/{marca}-ocasion/{slug}-ref{ID}`. Grupo Vocento |
| **coches.com** | ~67.259 PDPs | **sitemap** (`vo.xml`→`Todo-VO-{0..3}`) | Sí (`Place`) | Imperva latente pero sirve sitemap+PDP a curl. Cosechar antes de que endurezca |
| **motorflash.com** | aggregator | **sitemap** (`.concesionarios.xml`) | Fuerte (sitemap dealer-keyed) | Motor de los microsites OEM (Motorflash). Buen descubridor de dealers |
| **motor.es** | 50.935 | HTML listado | Sí | PDP `/vercoche/` robots-disallowed; listados crawlables |
| **ocasionplus.com** | 14.049 | sitemap (263 hijos) | Mono-dealer (cadena) | Next.js, sin muro |
| **flexicar.es** | ~23.769 stock real | sitemap (283 sedes) | Mono-cadena | sitemap inflado con landings SEO; PDP `/coches-ocasion/{slug}_{id}/` |
| **clicars.com** | 1.604 | sitemap (Google Storage) | `AutoDealer` JSON-LD | Cloudflare permisivo |
| **autohero.com/es** | ~3.000 | browser/API | Mono-marca (AUTO1) | SPA; sitemap fino |
| **unoauto.com** | ~5.000 | sitemap | Mono-dealer | ⚠ sitemap stale (PDPs 404) — validar frescura |
| **crestanevada.es** | ~1.000 | sitemap | Mono-cadena (32 sedes) | Apache/PHP, sin muro |

### 2.2 TIER-1 (defensa dura — frente separado F5, caza de receta por plataforma)

| Plataforma | Stock ES (vivo) | Defensa | Vía candidata | Estado |
|---|---|---|---|---|
| **wallapop** (motor) | **753.652** | CloudFront/CF | API `api.wallapop.com/api/v3/cars/search` (200 a curl con geo+headers) | API abierta con params correctos; +4.500 dealers PRO |
| **milanuncios** | 666.901 motor-Madrid (parcial) | Adevinta + **GeeTest** | browser + solver / residencial | 405 GeeTest a curl; geo-sensible (fuera de ES dispara muro) |
| **coches.net** | **249.139** ✓mi-curl | Adevinta Lambda@Edge | API `ms-mt--api-web.spain.advgo.net/search` (POST) / browser | SRP 200 a curl; `/concesionario(s)/*` y sitemap 405-walled |
| **spoticar.es** | ~50.000 (claim) | **Akamai** (403 duro) | browser full-fingerprint + sensor Akamai | El muro más duro; 403 hasta en sitemap |
| coches.net/milanuncios comparten infra Adevinta (= fotocasa) | | | | atacar la familia con una sola receta |

> ⚠ **Separación física obligatoria:** el código, las recetas y los datos Tier-1 viven
> en su propio árbol (`countries/ES/_tier1/`), nunca mezclados con el long-tail.

---

## 3. Universo de ENTIDADES — descubrimiento por modalidad

### 3.1 Oficial / registral (verdad jurídica + geo)

| Fuente | Qué da | Acceso | Volumen | Prio |
|---|---|---|---|---|
| **DGT Microdatos Transferencias** | transferencias por entidad → detectar compraventas activas | **dump** ZIP mensual | ~2M transf/año | alta |
| **DGT CAT (desguaces)** | censo oficial de desguaces | API ArcGIS `CATV/FeatureServer/0` | **1.292** ✓mi-curl | alta |
| **BORME** (datos abiertos BOE) | altas/bajas/cambios de empresas (señal de frescura) | API JSON/XML (`Accept: application/json`) | ~100k empresas/año | alta |
| **INE DIRCE / EEE** | conteos por CNAE (denominador, no entidades) | API Tempus3 | counts 451/452/454 | media |
| **datos.gob.es** (CKAN) | hub federado: registros talleres CCAA + censos municipales | API `apidata` (publisher MAYÚSC.) | docenas datasets | alta |
| **Cataluña RASIC** (talleres) | registro oficial talleres Cataluña | Socrata `ebyt-8dme` | **12.155** | alta |
| **Castilla y León** (talleres) | registro talleres CyL + CNAE | dump CSV | ~6.714 | alta |
| **Madrid — Censo de locales** | cada local con actividad + estado, nivel calle | dump CSV/API, **diario** | ~150k+ locales | alta |
| **Barcelona — Cens activitats** | locales planta baja con actividad | dump CSV (~24MB) | decenas de miles | media |
| Iberinform / eInforma / Axesor / Empresite | listas de empresas por CNAE (nombre+provincia+municipio) | HTML paginado | Iberinform **26.205** retail | alta/media |
| Cámaras (Camerdata) | censo empresarial oficial, compra de fichero | API/compra | ~3M total | media |

### 3.2 Asociaciones (multiplicadores de dealer)

| Fuente | Qué da | Volumen | Prio |
|---|---|---|---|
| **AEDRA** buscador socios | desguaces nacionales con tel/web | **615** ✓ | alta |
| **AECA-ITV** | estaciones ITV (geo-ancla) + operadores | ~418 est / 82 op | alta |
| **Gremi del Motor BCN** | dealers+compraventas Barcelona, ficha por socio | **693** | alta |
| **AMDA Madrid** | concesionarios Madrid, ficha rica | **147** | alta |
| **AETRAC** | desguaces Cataluña (AJAX/sitemap 130) | 107–130 | alta |
| **CETRAA** (gateway) | 30 asociaciones provinciales de talleres | ~20.000 talleres | alta |
| **FACONAUTO** (gateway) | 26 asociaciones de marca (sizing universo franquiciado) | 2.018 dealers + 3.642 agentes | media |
| AEAT relación asociaciones | 20 bodies nacionales del sector (cierre de universo) | 20 | media |
| CONEPA / FER / RO-DES (gateways) | federaciones talleres / recicladores | 21 assoc / ~10k empresas | media |

### 3.3 OEM — redes de concesionarios + portales VO (casi gratis)

**APIs JSON sin auth [VERIFICADO]:** Kia **242** ✓ · MG **212** ✓ · BYD **106** · VW OneHub
(⚠ refutada como-citada, ver §8) · Mercedes OneWeb (apikey embebida).
**Sitemaps de red:** SEAT 166 subsites/18.424 URLs · Skoda **215** · Dacia ~150-200 ·
Toyota 98 grupos · Lexus 44 · Peugeot 275 (DOM) · Omoda/Jaecoo ~70.

**Portales VO con stock atribuido por dealer (GOLD):**

| Portal | Stock ES | Marca(s) | Acceso |
|---|---|---|---|
| **renew** (es.renew.auto) | **5.747** ✓agente | Renault/Dacia | HTML SSR, atribución dealer |
| **Spoticar** | 6.334 | 6× Stellantis | browser (Akamai) |
| **Das WeltAuto** | ~10k (SEAT 4.078+VW 3.000+Skoda 1.383+Cupra 1.459) | Grupo VW | HTML (403 a no-browser UA) |
| **MB Certified** | 4.696 | Mercedes | browser |
| **Nissan Ocasión** | 1.546 | Nissan | HTML |
| **Hyundai Promise** | 420 | Hyundai | HTML |
| Audi Selection:plus | dealer subsites (Motorflash) | Audi | browser (Akamai en audi.es) |
| BMW Premium Selection | 56 dealers | BMW/Mini | HTML (dobla como lista dealer) |
| Toyota/Lexus, Honda VO, Volvo Selekt, Mazda Selected, Tesla inventory API | varios | — | mixto |

### 3.4 Directorios genéricos (long-tail + enriquecimiento)

| Fuente | Volumen auto | Acceso | Legal | Prio |
|---|---|---|---|---|
| **Páginas Amarillas** | **~44k** (talleres 29.955+conces 11.202+compra 1.662+desg 1.636) ✓ | HTML `/search/{rubro}/{prov}/.../{pág}` | OK | alta |
| **Google Places** | 50–90k [ASUMIDO] | API ($32/1k) | ⚠ **ToS prohíbe indexar/cachear** → solo enriquecimiento efímero | alta-riesgo |
| **OpenStreetMap** | **12.077** (car 3.516+repair 7.847+parts 714) ✓ | dump Geofabrik + osmium | ODbL (share-alike) | alta |
| **Foursquare OS Places** | decenas de miles | dump parquet (HF) | **Apache 2.0** (comercial OK) | alta |
| **Overture Maps** | decenas de miles (incl. FB places) | dump GeoParquet | **CDLA-Permissive** | alta |
| Empresite/eInforma/Iberinform | registral (CIF/CNAE para dedup) | HTML (rate-limit/reCAPTCHA) | OK | alta/media |
| Infobel / Opendi / Vulka / Infoisinfo | relleno tel/dirección | HTML | OK | media/baja |
| **MUERTOS** (excluir): QDQ (→agencia), Tuugo (spam casino), heycar ES (cerró), desguacesonline.com (en venta), Bing Maps Basic (retirado) | — | — | — | — |

### 3.5 Desguaces (segmento CAT) + cadenas de compraventa

**Desguaces — verdad oficial DGT = 1.292 CATs.** Directorios para enriquecer:
DesguacesDirecto **1.386** (sitemap limpio) · DesguacesOficiales ~2.049 fichas · AEDRA 615 ·
SIGRAUTO 595+25 (PDF/CCAA) · Opisto 449 (IDs `/detalles/<id>`) · Ovoko (403, browser) ·
desguacecoches/desguaces.eu/infodesguaces/tudesguace (cross-check).

**Cadenas de compraventa multi-sucursal (~10-15 marcas):** Flexicar **283** sedes (sitemap) ·
OcasionPlus 120 · compramostucoche/AUTO1 107 · Crestanevada 32 · HR Motor 30+ · Clicars/Autohero ·
Driveris/Compra y Conduce/Autofesa (2ª pasada). ⚠ "Movilcar" y "Grupo García" del brief = sin
cadena nacional identificable → desambiguar.

---

## 4. Arsenal OSS (routing por defensa, estado 2026-06-12 verificado por GitHub API)

| Capa | Herramienta | Estrellas | Estado | Uso en Cardeep |
|---|---|---|---|---|
| **Framework** | **Scrapling** | 63.184 | ✅ v0.4.9 (06-07) | Capa de orquestación estándar (bundlea camoufox+browserforge, selectores auto-reparables) |
| **Browser stealth** | **camoufox** | 9.169 | ✅ v150 beta (05-11) | Motor render fingerprint-level (CF/Turnstile) |
| **Browser stealth** | **patchright** (py) | 1.383 | ✅ v1.60 (06-03) | Parche Playwright undetected (si hay código Playwright) |
| **Browser stealth** | **SeleniumBase** UC/CDP | 12.781 | ✅ (06-12) | Turnstile battle-tested, bajo riesgo prod |
| **Browser CDP** | **nodriver** / **zendriver** | 4.350 / 1.318 | ✅ | Sucesor undetected-chromedriver; zendriver mergea fixes más rápido |
| **No-browser TLS** | **curl_cffi** (lexiforest) | 5.801 | ✅ v0.15.1b2 (06-05) | Workhorse JA3/JA4 para XHR/JSON (APIs OEM, advgo) |
| **No-browser TLS** | **primp** | 538 | ✅ | Cliente TLS secundario (rotación/diversidad) |
| **Headers** | **browserforge** | 1.130 | ✅ | Generación UA/headers consistentes (sustituye fake-useragent) |
| **Unblock service** | **Byparr** / FlareSolverr | 1.601 / 14.270 | ✅ | API de desbloqueo drop-in (Byparr = sucesor moderno) |
| **Heavy (Akamai)** | **BotBrowser** | 2.489 | ✅ (06-10) | Chromium parcheado anti CF/Akamai/Kasada/DataDome/PX/Imperva |
| **Routing** | **is-antibot** + **browsers-benchmark** | 34 / 324 | ✅ | Clasificar defensa por fuente → despachar el motor correcto (data, no reputación) |
| **MUERTOS (no adoptar)** | fake-useragent (archivado 04-01), playwright_stealth original (AtuboDad, 22m stale), hrequests (18m stale), undetected-chromedriver (legacy), lwthiker/curl-impersonate (usar fork lexiforest) | — | ☠ | excluidos |

**Doctrina de routing:** `is-antibot` fingerprintea la defensa de cada fuente →
ABIERTA = curl_cffi (barato) · CF/Turnstile = camoufox/SeleniumBase · Akamai duro =
BotBrowser + sensor de pago (solo con gate de gasto). Decisión grounded en
`browsers-benchmark`, no en fama.

---

## 5. Catálogo completo (181 fuentes)

El censo crudo de las 7 modalidades (181 fuentes con URL, yields, acceso, defensa,
volumen y notas de verificación por fuente) está preservado íntegro en
`docs/research/SOURCES_ES_raw.json`. Esta sección es la destilación; el JSON es la
trazabilidad completa.

Totales por modalidad: oficial 21 · asociaciones 22 · OEM 44 · plataformas 18 ·
directorios 20 · desguaces 34 · arsenal 22 = **181** entradas catalogadas.

---

## 6. Denominador — triangulación (capture-recapture informal)

| Segmento | Fuente A | Fuente B | Verdad / suelo |
|---|---|---|---|
| **Desguaces/CAT** | DGT 1.292 ✓ | DesguacesDirecto 1.386 / AEDRA 615 | **~1.300** (DGT = oficial) |
| **Concesionarios oficiales** | FACONAUTO 2.018 | PA 11.202 (incl. multimarca) / Σ locators OEM | **~2.000 franquiciados**, ~11k con multimarca |
| **Compraventas** | PA 1.662 | cadenas Σ ~800 sedes + independientes | **suelo 1.662**, real mayor (long-tail) |
| **Talleres (garajes)** | PA 29.955 | CETRAA ~20.000 / RASIC+CyL+… registros CCAA | **~30k** (subset que vende coches, a filtrar) |
| **TOTAL auto POS** | PA ~44.000 ✓ | OSM 12.077 (parcial) / Places 50-90k [ASUMIDO] | **suelo 44k, techo 50-90k** |

El denominador se cierra de verdad en F8 con capture-recapture (Chapman) entre PA,
registral CNAE y Places/OSM. Hoy: **~44k verificado, objetivo de cobertura sobre ese
denominador, refinándolo al alza con el registral.**

---

## 7. Verificación por mano propia del Director (quórum, 2026-06-12)

Re-derivadas con curl independiente (vía ortogonal al agente). **5/5 confirmadas:**

| Cifra | Agente | Mi curl | Δ | Veredicto |
|---|---|---|---|---|
| AutoScout24 ES `numberOfResults` | 278.163 | **278.329** | +166 | ✓ (drift contador) |
| coches.net contador | 248.920 | **249.139** | +219 | ✓ (drift contador) |
| DGT CATV `returnCountOnly` | 1.292 | **1.292** | 0 | ✓ exacto |
| Kia `dealerName` count | 242 | **242** | 0 | ✓ exacto |
| MG `Feature` count | 212 | **212** | 0 | ✓ exacto |

---

## 8. Refutaciones y residuos honestos (sin maquillaje)

1. **VW OneHub dealer API REFUTADA como-citada:** el censo afirmó "263 dealers"; la
   verificación viva devolvió **HTTP 500 `No service endpoint provided`** en todas las
   variantes → 0 dealers con la URL dada. Falta el param `serviceConfigEndpoint`
   (capturable del network de la página). La red VW se obtiene igual por sitemap SEAT
   (166 subsites) o concesionarios.seat. **No usar la URL del censo tal cual.**
2. **Das WeltAuto SEO doorways:** las 52 páginas `/provincia/` NO traen listados SSR;
   el stock real está tras BFF `gsl.feature-app.io`. No confundir landing con datos.
3. **Dacia:** la URL `find-a-dealer-listing.html` del censo 404ea; el directorio vivo
   está en raíz `/?page=1..5`.
4. **Google Places — riesgo legal:** ToS prohíbe scraping/caching/crear contenido →
   incompatible con construir un índice permanente. Usar solo enriquecimiento efímero
   o asumir el riesgo explícitamente. FSQ OS Places + Overture (licencias permisivas)
   son el sustituto legal del long-tail geo.
5. **Brief ambiguo:** "Movilcar" (= taller chapa Sevilla, no cadena) y "Grupo García"
   (homónimos independientes, sin red) no corresponden a cadenas nacionales → desambiguar.
6. **Contadores vivos driftan:** todo número de inventario de plataforma se re-deriva
   en el momento de cosechar; los de §2 son foto del 2026-06-12.

---

## 9. Implicaciones → F2 / F3

- **F2 (columna de datos):** el esquema de entidad necesita: identidad jurídica
  (CIF/CNAE del registral) + geo INE (provincia→comarca→municipio) + código único +
  tipo {concesionario_oficial, compraventa, garaje, desguace} + flags de red (VO OEM,
  cadena) + defensa-WAF de su web. El esquema de vehículo: precio, año, km, VIN/ref,
  deep-link, **hash de foto** (para Δfoto), `last_seen`, evento append-only.
- **F3 (primer dealer E2E):** empezar por **AutoScout24.es** (abierto, JSON-LD dealer,
  máxima atribución) como banco de pruebas del pipeline DESCUBRIR→SCRAPEAR→RECETA→API→BORRAR.
- **Orden de ataque de plataformas:** abiertas primero (AS24, autocasion, coches.com
  vía sitemap, motorflash) → APIs OEM (censo de red €0) → Tier-1 al frente F5 separado.
- **Long-tail por familia:** OSM+FSQ+Overture (geo legal gratis) ∪ PA (rúbricas) ∪
  registral (CIF) como semilla; clasificar webs por CMS/DMS → receta por familia.
