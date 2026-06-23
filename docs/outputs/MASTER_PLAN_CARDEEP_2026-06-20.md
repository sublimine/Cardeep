# PLANO MAESTRO CARDEEP — Arquitectura de élite del sistema de cobertura y scraping
**Fecha:** 2026-06-20 · **Autor:** Jefe Arquitecto (Director soberano de la misión) · **Estado:** documento de arquitectura, NO ejecución.

> **Naturaleza de este documento.** Es el plano de ingeniería para llevar cardeep —y en especial su sistema de scraping/cobertura— a estándar "1000/10". No introduce cambios en el código. Cada subsistema se audita con evidencia `archivo:línea` real (lectura directa por agentes de auditoría), se contrasta con el estado del arte 2025-2026 (investigación web con fuentes citadas), y se decide **mejorar / mantener / reemplazar** con justificación. Cambios quirúrgicos de alto impacto; no rediseño por rediseño.
>
> **Marco estratégico (mandato del Director, vinculante):**
> 1. El objetivo inmediato **NO es el volcado masivo de vehículos**. Es, por cada ENTIDAD: scrapear → extraer UNOS POCOS vehículos → **guardar la receta/config que funcionó** → **verificar (doctrina VAM)** → **borrar la muestra** (almacenamiento del PC). Ciclo canónico: **recipe-first / sample-verify-delete**.
> 2. El volcado total irá a una **VPS**, que **no se toca** hasta que TODO esté verificado a la perfección en local.
> 3. **Coste no es criterio** (vendrá mucho más adelante). Arsenal disponible: Camoufox, nodriver, curl_cffi/curl-impersonate, etc.
> 4. Postura: **la antidetección más agresiva del mercado**, presente y de los próximos años.
> 5. **Corregir lo roto y subir de nivel lo mejorable**, reutilizando lo bueno (orquestación, doctrina VAM, invariantes).
>
> **Honestidad metodológica.** Se separa `[VERIFICADO]` (leído en fuente: código o documentación citada) de `[ASUMIDO]` (inferencia razonada no probada en vivo). Donde no se pudo cerrar una verificación, se declara el hueco.

---

## 0. Tabla de notas as-is → to-be (resumen ejecutivo cuantificado)

| # | Área | Nota AS-IS | Nota objetivo | Decisión | Hueco crítico (1 línea) |
|---|------|:---:|:---:|---|---|
| 1 | Motor antidetección + transporte | **4.5/10** | 10/10 | **Mejorar + añadir Tier-1** | Sin proxies en código; fingerprint estático único; Tier-1 es un `raise`. |
| 2 | Harness de RECETA por entidad | **3/10** | 10/10 | **Reemplazar (construir)** | La receta documenta pero **no se ejecuta**; no hay ciclo recipe-first/sample-verify-delete. |
| 3 | Governor / rate-limit distribuible | **7/10** | 10/10 | **Mejorar (distribuir)** | In-memory, no persistente, no distribuible; sin AIMD. |
| 4 | Conectores / Adapters | **6/10** | 10/10 | **Mejorar (unificar)** | 29× persistencia copy-paste; sin clase base de cosecha; extractor genérico sin LLM. |
| 5 | Verificación VAM | **5.5/10** | 10/10 | **Mejorar (despertar lentes)** | 2 de 5 lentes muertas; independencia de lente-A nominal; denominador estadístico ausente. |
| 6 | Identidad / record-linkage | **8/10** | 10/10 | **Mantener + elevar** | Cross-source no servido; delta vivo infra-cableado (1.7M NEW vs <15k cambios). |
| 7 | Orquestación / scheduler / observabilidad | **8/10** | 10/10 | **Mantener + elevar** | 6 de 9 detectores sin caller en prod; sin métricas en el tiempo; serie pura. |
| 8 | Arquitectura de datos / almacenamiento | **8.5/10** | 10/10 | **Mantener** | sample-and-delete sólido; eviction automática no corre. |
| 9 | Producción VPS | **N/A** | 10/10 | **Diseñar (no tocar)** | No existe; diseño listo, despliegue diferido hasta verificación local total. |
| 10 | Modelo de datos / API | **8/10** | 10/10 | **Mantener + elevar** | cdp_code sin UNIQUE constraint (no FK-able); 3 sistemas de identidad solapados. |

**Nota global del sistema as-is: ~6.4/10.** Núcleo de datos y orquestación maduros y honestos; los dos huecos que más comprometen el mandato son (a) **el harness de receta ejecutable no existe** y (b) **el motor Tier-1 / antidetección agresiva no está construido** (solo declarado). El plan los trata como los dos proyectos de cabecera.

---

## 1. Motor de antidetección y transporte

### 1.1 AS-IS (evidencia archivo:línea) — Nota **4.5/10**

**Transporte HTTP [VERIFICADO]:** cliente único `curl_cffi.requests` (`pipeline/engine/fetch.py:27`). Impersonation **hardcoded** a `chrome131` (`fetch.py:31` `_IMPERSONATE = "chrome131"`, aplicada en sesión `fetch.py:70`). UA fija Chrome131/Win10 (`fetch.py:33-36`), headers Sec-Fetch + `es-ES` (`fetch.py:37-47`). Sesión = 1 fingerprint = 1 cookie jar (`fetch.py:61-76`) — coherencia intra-sesión correcta.

**Tier-1 [VERIFICADO]:** **ausente**. Camoufox/nodriver/BotBrowser existen solo como texto en docstring (`fetch.py:14-20`) y en el mensaje del `NotImplementedError`; cualquier `tier != 0` **lanza excepción** (`fetch.py:94-98`). Decisión correcta (fail-loud, no fallback silencioso) pero significa cero capacidad contra challenge activo.

**Rotación de fingerprints [VERIFICADO]:** **no existe**. Valor único de proceso; el constructor admite otro `impersonate` (`fetch.py:68`) pero ningún llamador lo varía. Sin pool ni floor de fingerprints.

**Anti-CF/DataDome/Akamai [VERIFICADO]:** lo único real es el TLS/JA3+HTTP2 de Chrome que aporta `impersonate=chrome131`. Ausente: resolución de JS challenge, `cf_clearance`/`__cf_bm`, `_abck` Akamai, cookie DataDome, captcha, detección semántica de bloqueo (un 403-challenge se trata como error no-retryable, `fetch.py:118-119`, sin inspeccionar body).

**Errores/retry [VERIFICADO]:** retryables `{429,500,502,503,504}` (`fetch.py:49`), 4 reintentos (`fetch.py:51`), backoff exponencial con full-jitter cap 30s (`fetch.py:133-134`), honra `Retry-After` (`fetch.py:130-132`). Timeout único 40s (`fetch.py:50`). **Sin detección de ban ni circuit breaker en el motor** (el "breaker" que el governor invoca vive fuera, en `ops/health.py`).

**Proxies [VERIFICADO]:** **NO soportados en código**. Ningún parámetro `proxies` en `Session(...)` (`fetch.py:70`) ni en `get(...)` (`fetch.py:108`). Las peticiones salen por la IP del host. Crítico para el caso de uso (cosechar tras WAFs geo/IP-filtrados).

### 1.2 TO-BE "1000/10"

Modelo de **tres carriles** con rotación de identidad sobre un floor compartido:

- **Tier-0 (volumen):** `curl_cffi` rotando entre perfiles **reales** de la allowlist (`chrome146`, `chrome142`, `safari260`, `firefox147`) — nunca JA3 random (cae fuera de allowlist → ban). Base barata para los ~30k dealers sin JS-challenge.
- **Tier-1 (challenge):** `nodriver` como motor primario (único con **0 bloqueos** en el benchmark independiente de 651 verdictos: [ianlpaterson.com](https://ianlpaterson.com/blog/anti-detect-browser-benchmark-patchright-nodriver-curl-cffi/)) porque elimina Playwright del plano de control (vector `Runtime.enable`). `Camoufox` como segundo motor (diversidad Firefox + rotación BrowserForge con distribución estadística real).
- **Tier-1 duro (DataDome/Akamai/Kasada):** patrón **"navegador genera cookie → curl_cffi sirve"**: el browser resuelve el challenge una vez, extrae `cf_clearance`/`datadome`/`_abck`, y curl_cffi drena el inventario reusando **cookie + fingerprint + IP idénticos** (invariante obligatorio). Evaluar `Hyper Solutions SDK` (genera sensor sin navegador, Python nativo) y `BotBrowser` como PoC a medir contra targets reales.

**Capa transversal obligatoria:** pool de **proxies residenciales ES** sticky 30-60min por dealer + headful bajo Xvfb + humanización de pacing. Sin esto ninguna herramienta aguanta DataDome 2026 (marca por intención, no solo fingerprint).

### 1.3 Gap, decisión y por qué

**Decisión: MEJORAR el transporte (rotación + proxies) y AÑADIR el subsistema Tier-1 que hoy es un `raise`.** Reutilizar `fetch.py` como núcleo Tier-0 (es correcto y honesto); el fail-loud en Tier-1 es la base perfecta para colgar el engine real. No se reemplaza curl_cffi: es la elección correcta y empíricamente competitiva (26/31 OK con 21 líneas).

### 1.4 Diseño técnico concreto

```
pipeline/engine/
  fetch.py            # Tier-0 — añadir: param proxy, selección de perfil desde fingerprint pool
  transport.py  (NEW) # router de tier: elige carril por receta/clasificación del host
  fingerprints.py(NEW)# pool de perfiles reales (allowlist) + política de rotación (por sesión/ban)
  identity_pool.py(NEW)# lease/checkout de identidad = (proxy + fingerprint + cookies); cooldown per-domain
  tier1/
    browser_nodriver.py (NEW)  # motor primario challenge
    browser_camoufox.py (NEW)  # motor secundario (diversidad)
    cookie_harvester.py (NEW)  # genera cf_clearance/_abck/datadome → entrega a fetch.py
    ban_detector.py     (NEW)  # clasificación semántica: 403-challenge vs 403-real vs 200-interstitial
```

**Interfaz `Transport`:**
```python
class Transport(Protocol):
    async def fetch(self, url: str, *, recipe: Recipe, identity: Identity) -> Response: ...
    # tier resuelto por recipe.engine + clasificación del host
```

**Invariante de identidad (regla dura):** durante la vida de un `cf_clearance`/sensor, `IP + UA + JA4 + headers` no cambian. La identidad sticky-por-dealer y el governor per-host son **la misma decisión** desde dos ángulos (permiso de pegar al host).

### 1.5 Herramientas/repos recomendados

- [nodriver](https://github.com/ultrafunkamsterdam/nodriver) (Tier-1 primario; **verificar implicación licencia AGPL-3.0** sobre el modelo API público de cardeep antes de comprometer).
- [Camoufox](https://github.com/daijro/camoufox) + BrowserForge (diversidad de motor).
- [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) / [rebrowser-patches](https://github.com/rebrowser/rebrowser-patches) (drop-in defensivo si hay Playwright legacy).
- [lexiforest/curl-impersonate](https://github.com/lexiforest/curl-impersonate) (fork activo; targets chrome146/safari260).
- [Byparr](https://github.com/DamienDessagne/FlareSolverr-Lite) (cookie-generator microservicio).
- [Hyper Solutions SDK](https://github.com/Hyper-Solutions/hyper-sdk-py) (sensor Akamai/DataDome sin navegador — PoC).
- [BotBrowser](https://github.com/botswin/BotBrowser) (referencia DataDome/Akamai/Kasada — PoC a medir).

### 1.6 Riesgos
- **Licencia AGPL-3.0 de nodriver** sobre distribución API pública `[ASUMIDO, requiere criterio legal]`.
- DataDome marca por **intención**: el fingerprint perfecto no basta sin humanización → riesgo de falso sentido de seguridad.
- Mantenimiento de Camoufox tuvo un parón de ~1 año (riesgo de proyecto).
- Sin benchmark independiente DataDome/Akamai con números duros → **montar prueba propia** sobre targets reales antes de comprometer motor.

### 1.7 Criterios de "hecho/verificado"
- [ ] curl_cffi rota ≥4 perfiles reales; cero JA3 random (test que verifica el ClientHello).
- [ ] `identity_pool` entrega identidad sticky-por-dealer con cooldown per-domain medible.
- [ ] `tier1` resuelve ≥1 portal Cloudflare-managed real y curl_cffi sirve el inventario reusando la cookie (E2E sobre un dealer `family_unreachable`).
- [ ] `ban_detector` distingue 403-challenge de 403-real en un set etiquetado.
- [ ] Proxies ES enrutados desde código y verificables (IP de salida == IP del pool).

---

## 2. Harness de RECETA por entidad (recipe-first / sample-verify-delete)

### 2.1 AS-IS — Nota **3/10**

**[VERIFICADO]** El ciclo actual NO es recipe-first. En `pipeline/harvest_dealer.py:28-86` el orden real es **scrape completo → ingest+delta+VAM → receta(post-hoc) → verify**: `write_recipe(cdp_code)` se escribe DESPUÉS del ingest (`harvest_dealer.py:71-73`), no antes, y no se valida una muestra contra la receta antes de drenar.

**Esquema de receta [VERIFICADO]:** `pipeline/recipe.py` serializa YAML a `countries/ES/recipes/<cdp_code>.yaml` (`recipe.py:58-60`) con integridad round-trip (`recipe.py:64-68`). Campos: `version, source, scope, engine` (p.ej. `"curl_cffi+chrome131_impersonate+json_api(POST)"`), `endpoint, request, enumeration` (paginación), `field_map` (selectores por campo). **Pero ningún loader ejecuta la receta para re-scrapear** — la receta es documental/auditoría, no un motor parametrizado; la cosecha está hardcodeada por módulo. Solo **7 recetas en disco**, todas de familia; **0 recetas per-dealer pobladas**.

**"Borrar" muestra [VERIFICADO]:** existe `pipeline/evict.py` con sample-and-delete sólido (ver §8), pero opera sobre inventario ya volcado, no como cierre de un ciclo de muestra-verificada.

**Driver hardcoded [VERIFICADO]:** `harvest_dealer.py` está atado a AS24 (`source_key="as24"`, `scrape_dealer` de `autoscout24`, `:22,:65`). No es orquestador genérico per-dealer multi-plataforma.

### 2.2 TO-BE "1000/10"

El **harness canónico del mandato**, como pieza de primera clase:

```
DESCUBRIR → SCRAPEAR MUESTRA (k vehículos, k≈3-10) → PERSISTIR RECETA → VERIFICAR (VAM sobre la muestra) → BORRAR MUESTRA
                                                          ↑ si VERIFY falla → re-caza de receta (loop) ↑
```

La receta es **ejecutable y reproducible**: un `RecipeRunner` lee el YAML (`engine` + `field_map` + `enumeration`) y produce vehículos sin código por-dealer. "Que una receta funciona" = el RecipeRunner, partiendo solo del YAML, reproduce la muestra y pasa el quórum VAM por un camino independiente del que la generó.

### 2.3 Gap, decisión y por qué

**Decisión: REEMPLAZAR el flujo actual por un harness recipe-first explícito, reutilizando los componentes buenos** (esquema YAML con round-trip, evict, VAM). El esquema de receta es bueno pero **muerto como motor**: hay que hacerlo ejecutable. Es el proyecto de mayor ROI del plan porque materializa el mandato literal.

### 2.4 Diseño técnico concreto

**Esquema de receta v2 (declarativo, 3 niveles de fallback por coste creciente — patrón [web2api](https://github.com/Endogen/web2api)):**
```yaml
cdp_code: CDP-ES-MA-XXXXXXXX
version: 2
engine:
  tier: 0|1
  transport: curl_cffi:chrome146 | nodriver | camoufox
  proxy_class: residential_es_sticky
extraction:
  level_1_structured: { type: json-ld|microdata, schema: Vehicle }   # extruct, coste 0
  level_2_selectors:  { listing_path: ..., card: ..., fields: {...} } # CSS declarativo
  level_3_llm:        { model: qwen3.6-local, schema: Vehicle, temp: 0 } # solo si 1 y 2 fallan
enumeration: { pagination: {param: page, from: 1, size: 100} }
verify:       { lenses: [A_requery, B_raw_recount], min_quorum: 2 }
provenance:   { worked_level: 2, sampled_at: ..., sample_n: 5 }
```

**Componentes:**
```
pipeline/recipe/
  schema.py    (NEW) # Pydantic Recipe v2, validación estricta
  runner.py    (NEW) # RecipeRunner: YAML → vehículos (sin código por-dealer)
  harness.py   (NEW) # ciclo recipe-first/sample-verify-delete orquestado
  cazador.py   (NEW) # re-caza de receta: prueba combinaciones engine/selectors hasta pasar VAM
  extract/
    structured.py (NEW) # extruct: JSON-LD/Microdata/RDFa/OpenGraph (coste 0, SIEMPRE primero)
    selectors.py  (NEW) # CSS/XPath declarativo
    llm_local.py  (NEW) # Crawl4AI + Qwen3.6 + Instructor/Outlines (JSON Schema forzado)
```

**Reproducibilidad:** la receta se versiona en git (`countries/ES/<prov>/<cdp>/recipe.yaml`); `evict.py` ya la protege (`evict.py:139-171`). Prueba de "funciona" = `cazador` la marca VERIFIED solo si `RecipeRunner` reproduce muestra + VAM quórum≥2.

### 2.5 Herramientas/repos
- [extruct](https://github.com/scrapinghub/extruct) (estructurados, coste 0 — probar siempre primero).
- [Crawl4AI](https://github.com/unclecode/crawl4ai) + [Instructor](https://python.useinstructor.com/) / [Outlines](https://github.com/dottxt-ai/outlines) (LLM local con schema forzado).
- Qwen 3.6 local vía Ollama (JSON Schema nativo, temp 0).
- [web2api](https://github.com/Endogen/web2api) (patrón de receta declarativa de referencia).

### 2.6 Riesgos
- LLM local puede alucinar campos: mitigar con Outlines (constrained decoding a nivel de token) + verificación VAM obligatoria sobre la muestra.
- `[ASUMIDO]` no verificado en vivo que los marketplaces concretos emitan schema.org Vehicle — comprobar con extruct sobre muestra real antes de dimensionar capa LLM.

### 2.7 Criterios de "hecho/verificado"
- [ ] `RecipeRunner` reproduce una muestra de ≥3 dealers de familias distintas **solo desde el YAML**.
- [ ] Ciclo completo recipe-first ejecuta DESCUBRIR→MUESTRA→RECETA→VERIFY→BORRAR sobre 1 dealer y deja la receta en git + 0 vehículos de muestra en disco.
- [ ] `cazador` re-caza una receta que falla y converge a VERIFIED en ≤N intentos.
- [ ] Cobertura del long-tail: un dealer bespoke sin selector cae a LLM-local y pasa VAM.

---

## 3. Governor / rate-limit distribuible y gestión de identidades

### 3.1 AS-IS — Nota **7/10**

**[VERIFICADO]** Token bucket continuo + floor de min-spacing con jitter (`pipeline/engine/governor.py:184-215`), **per-host** (`governor.py:151-165`), clases STEALTH 0.7req/s y JSON_API 12req/s (`governor.py:51-54,88-91`) + overrides por host (`governor.py:323-396`). Doble constraint (token + spacing) bien implementado (`governor.py:208-215`). **In-memory, mono-proceso asyncio** (`governor.py:234`), **sin persistencia** (reinicio reabre bucket lleno, `governor.py:179`), **no distribuible**. AIMD anunciado pero ausente (`governor.py:193-195`). Crash-safe solo dentro de un proceso vivo.

### 3.2 TO-BE "1000/10"
Governor **per-host distribuible y persistente** que permita N workers en paralelo sin romper el agregado contra un dominio, con AIMD adaptativo.

### 3.3 Gap, decisión y por qué
**Decisión: MEJORAR — distribuir y persistir el algoritmo correcto, sin reescribir su lógica.** El núcleo (token bucket per-host con spacing+jitter) es correcto; el déficit es solo el backend de estado.

**Insight clave (de la investigación):** **no introducir Redis todavía.** `pyrate-limiter` soporta `PostgresBucket` + `PostgresClock` → rate-limit distribuido reusando el Postgres existente, persistente entre reinicios, con `try_acquire_async()` (encaja con asyncio). Redis-GCRA entra solo cuando Postgres sature.

### 3.4 Diseño técnico
```
Fase A (local, sin Redis):
  governor.py → backend pluggable; PostgresBucket per-host (pyrate-limiter), PostgresClock como "now" compartido
  AIMD: acquire() ya devuelve `waited`; cerrar el lazo (baja rate ante 429/ban, sube lento ante éxito)
Fase B (escala VPS):
  redis-gcra (Lua, portable) o redis-cell (módulo) — una clave por dominio `ratelimit:<host>`
Identidades:
  tabla Postgres identity_lease(domain, identity_id, leased_until, cooldown_until, burned) — checkout sticky-por-dealer
```
**Identidad + rate-limit = misma decisión**: ambos gobiernan el "permiso de pegar al host"; modelarlos juntos.

### 3.5 Herramientas/repos
- [pyrate-limiter](https://pypi.org/project/pyrate-limiter/) (PostgresBucket/PostgresClock — Fase A).
- [redis-gcra (Losant)](https://github.com/Losant/redis-gcra) / [redis-cell](https://github.com/brandur/redis-cell) (Fase B).

### 3.6 Riesgos
- Verificar que la unidad de trabajo es "1 dealer = 1 host coherente"; si un dealer reparte inventario entre hosts, clavar el governor al **host real**, no al dealer.

### 3.7 Criterios "hecho"
- [ ] 2 procesos concurrentes contra el mismo host no superan el ceiling agregado (test multi-proceso).
- [ ] Reinicio del proceso no reabre el bucket lleno (estado persiste).
- [ ] AIMD baja el rate ante una racha de 429 y se recupera.

---

## 4. Conectores / Adapters

### 4.1 AS-IS — Nota **6/10**

**[VERIFICADO]** `pipeline/sources/base.py` define el contrato de **censo** (`SourceAdapter`, `base.py:29-40`: `declared_count()`, `fetch()`), implementado por los 14 `sources/*.py`. **Pero los 30 conectores de `platform/*.py` (los que sacan inventario) NO heredan de ninguna clase base** — son módulos de funciones sueltas con `async def harvest(...)`.

**Duplicación de persistencia [VERIFICADO]:** `_persist` literal no existe; la persistencia está **copiada verbatim**: `ensure_platform_entity` redefinida en **29 archivos** (md5 del cuerpo idéntico byte-a-byte en ≥3 verificados: `07d808e26217b31712a3b4a105ab3240`), `cdp_code_dealer` ×21, `_ingest_window` ×18 (**ya con firmas divergentes** → bomba de drift), `upsert_dealer` ×11. Mayor pasivo de mantenimiento del repo.

**Extractor genérico [VERIFICADO]:** `generic_dealer_site.py` (sitemap→JSON-LD→microdata→OG, 100% heurístico, **sin LLM**); `family_generic_custom_wholesale.py` con `DealerRecipe` registry per-dealer (parsers bespoke manuales). Caps duros `_MAX_VEHICLE_PAGES=500` (truncado silencioso). Familias del long-tail bien razonadas (dealerk, wordpress, wix/ueni, dms, framework, unreachable→Tier-1).

### 4.2 TO-BE "1000/10"
Un **framework de adapter de cosecha** con persistencia centralizada y la receta como motor (no copia), + extractor genérico con fallback LLM-local para el long-tail bespoke.

### 4.3 Gap, decisión y por qué
**Decisión: MEJORAR (unificar), sin cambiar comportamiento observable.** La arquitectura de familias es buena; el déficit es estructural (duplicación, sin contrato, receta no ejecutable). Refactor reversible de alto impacto.

### 4.4 Diseño técnico (plan de unificación, reversible)
1. **Extraer `pipeline/platform/_persistence.py`** con las funciones idénticas; empezar por las 29 copias byte-idénticas de `ensure_platform_entity` (reemplazo mecánico seguro, hash único confirmado).
2. **Definir `WholesaleConnector` Protocol/ABC** (`harvest()`, `declared_count()`, `recipe`) que formalice el contrato implícito, alineado con `SourceAdapter`.
3. **Unificar `_ingest_window`** en una función parametrizada por `field_map` (absorbe las 18 variantes; resuelve divergencia geo/geocoder vía parámetro opcional).
4. **Receta ejecutable** (converge con §2): el `_ingest_window` unificado se alimenta del `field_map` del YAML → "la receta la mantiene, el motor la late".
5. **Cobertura del tail:** fallback LLM-local para `SITEMAP_SOLO`/bespoke sin parser; parametrizar los caps.

### 4.5 Herramientas/repos
- [extruct](https://github.com/scrapinghub/extruct), [Crawl4AI](https://github.com/unclecode/crawl4ai) (ver §2).

### 4.6 Riesgos
- El refactor de persistencia toca 29 archivos: hacerlo con tests de regresión de paridad (mismo SQL emitido antes/después).

### 4.7 Criterios "hecho"
- [ ] 0 copias de `ensure_platform_entity`/`cdp_code_dealer`/`_ingest_window` fuera de `_persistence.py` (grep == 1 definición).
- [ ] Todos los conectores cumplen el Protocol `WholesaleConnector`.
- [ ] Paridad de comportamiento verificada (snapshot de inserts pre/post refactor idéntico).

---

## 5. Verificación VAM

### 5.1 AS-IS — Nota **5.5/10**

**[VERIFICADO]** 5 lentes (`pipeline/inquisition/models.py:21-27`). Estado: **A_requery ACTIVA** (`_lens_a.py:42-51`, SQL real), **B_raw_recount DORMIDA** (abstención incondicional `lenses.py:135` `_RAW_STORE_AVAILABLE=False`, `:156-164`), **C_live_refetch DORMIDA** (siempre ABSTAIN, cero red, `lenses.py:210-217`), **D_cross_source ACTIVA** (`_lens_d.py:54-99`), **E_batch_hash ACTIVA** (SHA-256, cazador de empty-delta `lenses.py:377-386`).

**Quórum [VERIFICADO]:** real, no placeholder — 6 reglas §5.4 en `quorum.py:136-297`, umbrales `TAU_REL=0.005, TAU_ABS=50.0` (`quorum.py:34-35`). **Pero** TRUSTWORTHY exige ≥2 ASSERTs independientes con D≥2 (`quorum.py:257`); con B y C dormidas, muchos subjects solo tienen A (que lee la misma DB) → **estructuralmente imposible certificar**, sesgado a default-REFUTED (`prosecutor.py:512-513`).

**Independencia [VERIFICADO]:** lente A conserva `source`+`cache` del productor (`_lens_a.py:23-24`) → D=2 nominal, **lee la misma tabla que escribió el ingest** (no es camino de datos independiente). Lente D sí cambia source a witnesses reales (única independencia genuina) pero los witnesses están dentro de la misma DB.

**Denominador / captura-recaptura [VERIFICADO]:** infraestructura presente (`denominator_estimate`, migración 0026:250-266) pero **Chapman declarado incalculable hoy** (`scripts/recon/b6_chapman_final.py:13-18`: m=10 global → IC inservible, causa = `entity_cluster` casi sin mergear). El denominador vivo es `registral_ceiling` (techo DIRCE) + `source_floor`, **no captura-recaptura estadística**.

### 5.2 TO-BE "1000/10"
Las 5 lentes vivas con **independencia real** (al menos una toca el portal vivo), quórum alcanzable, y denominador estadístico con IC defendible (captura-recaptura multi-lista).

### 5.3 Gap, decisión y por qué
**Decisión: MEJORAR — despertar las lentes dormidas y construir el denominador estadístico.** La arquitectura es honesta y sólida (declara sus huecos); lo que falta es exactamente lo que da valor de verificación *independiente y externa*. Es prerequisito del mandato "verificar TODO".

### 5.4 Diseño técnico
1. **Despertar Lente C (refetch vivo)** — mayor ROI. Requiere fase harvest con identidad de egress separada (JA3/IP distinto del que produjo el dato). Es la única con D=4 y verificación contra el portal real. Se apoya en el motor §1.
2. **Despertar Lente B (raw recount)** — implementar evidence-store (`evidence_uri`): el harvest persiste bytes (JSON-LD/`__NEXT_DATA__`/sitemap) y B recuenta sobre ellos, camino independiente del SQL de ingest.
3. **Quórum para subjects mono-lente:** añadir 2ª lente o declararlos explícitamente no-certificables.
4. **Denominador estadístico:** prerequisito = **mergear `entity_cluster`** (subir m por celda) → desbloquea Chapman/MSE. Usar **Rcapture** (log-lineal/AIC) + **LCMCR** (clase latente, heterogeneidad), reportar ambos y su divergencia. Triangular contra censo CNAE-451/DGT. Declarar siempre el supuesto (independencia/homogeneidad).
5. **Endurecer A:** dejar de contar A como independencia para TRUSTWORTHY salvo combinada con B/C/D.

### 5.5 Herramientas/repos
- [Splink v4](https://github.com/moj-analytical-services/splink) (prerequisito: merge de entidades para el denominador — ver §6).
- [Rcapture](https://www.researchgate.net/publication/26469564) / [LCMCR](https://rdrr.io/cran/LCMCR/man/LCMCR-package.html) (vía rpy2; no hay equivalente Python maduro `[VERIFICADO]`) o GLM Poisson con statsmodels para el log-lineal base.

### 5.6 Riesgos
- Captura-recaptura depende de supuestos frágiles (independencia de listas, captura homogénea — falsa en cardeep por heterogeneidad de digitalización). Todo "% cobertura" va con supuesto declarado y triangulado.
- MSE vive en R: puente rpy2 añade dependencia.

### 5.7 Criterios "hecho"
- [ ] Lente C refetch un portal vivo y discrepa/confirma contra DB por egress independiente.
- [ ] Lente B recuenta sobre bytes crudos persistidos.
- [ ] ≥1 subject mono-lente pasa a ≥2 lentes o se marca no-certificable explícitamente.
- [ ] Denominador nacional con IC reportado bajo ≥2 modelos (log-lineal + clase latente) + triangulación externa.

---

## 6. Identidad / record-linkage de entidades a escala

### 6.1 AS-IS — Nota **8/10**

**[VERIFICADO contra código + DB viva]** Clustering dealers `dealer-identity-det-v1` **vam_verified=TRUE**: union-find determinista (`cluster_dealers.py:194-228`), 4 aristas todas con guard de `municipality_code` (nombre+muni, phone+muni, web+muni, levenshtein≤2). 61.551→42.259 canónicos (19.292 merged, 31%) — **no es mar de singletons**. Particulares fuera de scope (`cluster_dealers.py:59`). Cadenas vs sucursales: **propiedad emergente** del guard de muni (Flexicar Madrid ≠ Flexicar Sevilla nunca comparten muni), verificada a posteriori (CHECK `cluster_dealers.py:746-777`), no impuesta por regla de cadena — el guard anti-cadena explícito vive en `cross_source_dedup.py:164-177` y `resolve_entities.py:681-684`.

**cdp_code [VERIFICADO]:** minteo determinista por identidad canónica (`services/api/codes.py:34-89`), inmutable (overlay no-destructivo). **Debilidad:** `uq_entity_cdp_code` es UNIQUE INDEX, no CONSTRAINT (migración 0002:35) → no FK-able; relaciones por `entity_ulid`.

**Cross-source [VERIFICADO — hallazgo clave]:** `cross-source-dedup-v1` está **vam_verified=FALSE** (50.497 in, solo 688 merged) → la vista servida `v_canonical` (0020:51-67) **no lo sirve**. El dedup servido real que reduce el conteo es la capa deeplink/residual (`residual-namemuni-v1` vam_verified=TRUE → 29.827 dealers servidos).

**Deltas [VERIFICADO]:** `vehicle_event` enum `NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE` (0003), historial append-only sellado por trigger (0035), guards anti-falso-retiro fuertes (`delta.py:145-282` coverage-gate + cap 50%; `delta_guard.py:66-141`). **Debilidad mayor:** el motor de delta es correcto pero **apenas se ejerce** — DB viva: 1.705.965 NEW vs 1.125 PRICE / 339 KM / 3.568 PHOTO / 9.791 GONE. Los 43 connectors emiten **solo NEW** (delta vivo diferido A4-phase-2).

### 6.2 TO-BE "1000/10"
Record-linkage probabilístico y auditable (cadenas/sucursales/particulares como clustering de features), cross-source servido, y **delta vivo cableado en toda la flota**.

### 6.3 Gap, decisión y por qué
**Decisión: MANTENER el núcleo (es fuerte y verificado contra DB) y ELEVAR con Splink + cablear el delta.** El union-find determinista funciona; **Splink** lo formaliza como Fellegi-Sunter probabilístico, da match-weights auditables (satisface "verificar cada número"), y su clustering desbloquea el denominador de §5. El delta infra-cableado es el agujero entre "el motor late" y "el delta vive".

### 6.4 Diseño técnico
- **Splink v4 (DuckDB, `dedupe_only` + clustering)** sobre las ~43k entidades: blocking rules laxas encadenadas, EM no supervisado, comparadores geográficos para cadena-vs-sucursal. Salida = IDs de entidad estables + match-weight desglosado. Reemplaza/complementa el union-find artesanal manteniendo la reversibilidad de overlay.
- **Cablear delta:** importar `diff_vehicle` (`delta.py:289-345`, ya correcto) en los 29 conectores vía el `_persistence.py` unificado de §4 → un solo punto emite PRICE/PHOTO/KM/GONE.
- **Servir cross-source:** gatear el run cross-source por VAM y exponerlo en `v_dealer_resolved`.

### 6.5 Herramientas/repos
- [Splink v4](https://github.com/moj-analytical-services/splink) · [dedupe](https://docs.dedupe.io/) (afinado de casos frontera con active learning).

### 6.6 Riesgos
- Splink puede fusionar sucursales de cadena con nombre idéntico: combinar blocking laxo con comparadores geográficos finos; mantener el guard de muni.
- Cablear delta en 29 sitios: hacerlo tras la unificación de §4 (un punto, no 29).

### 6.7 Criterios "hecho"
- [ ] Splink reproduce/mejora el merge actual (≥31% colapso) con match-weights auditables.
- [ ] Cross-source servido en `v_dealer_resolved` (vam_verified).
- [ ] Delta vivo: tras 2ª cosecha, PRICE/PHOTO/KM/GONE > 0 en flota (no solo AS24).

---

## 7. Orquestación / scheduler y observabilidad

### 7.1 AS-IS — Nota **8/10**

**[VERIFICADO]** Scheduler APScheduler `BlockingScheduler` + `SQLAlchemyJobStore` sobre Postgres (`scheduler.py:804-829`) → **crash-safe**. Doble single-producer: `max_instances=1` + **pg advisory lock** (`scheduler.py:813-823`). `coalesce`+`misfire_grace_time` (reanudación). **Red de seguridad crash-before-record** que cierra el fallo silencioso de los "138 dealers" (`scheduler.py:400-464`). Selección de overdue con breaker excluido (`scheduler.py:296-336`).

**Observabilidad [VERIFICADO] — el subsistema más maduro (9/10):** `record_run` único escritor de health (`health.py:84-286`), **alerta con origen exacto** machine-readable `<source>:<phase>[:<code>]` + dedup (`health.py:289-324`), watchdog de silencio cubre el punto ciego pasivo (`silence_watchdog.py:57-167`), gate de cobertura B9 con verdicto VAM ortogonal (`coverage_verify.py`). Auto-reparación con loop+clasificación+alerta+breaker (`health.py:381-440`).

**Debilidades [VERIFICADO]:**
- **6 de 9 detectores del gestionador sin caller en producción**: el scheduler solo cablea `run_price_trap` (`scheduler.py:622`); `count_inflation, silent_cap, field_loss, staleness, fabrication, coverage_gap` solo se invocan desde tests (`dry_run_all`). **LIVE como código, muertos en operación.**
- **Sin métricas en el tiempo** (todo es estado-actual en tablas; sin Prometheus/Grafana/histogramas).
- **Reparaciones caras son scaffold** (`health.py:378,419-424`): refingerprint/escalate_tier/re_receta se clasifican y alertan pero no ejecutan (gated tras "P10 spend gate").
- Serie pura (un connector lento bloquea el tick); sin paralelo per-host.
- G5 (delta proven) es stub, `g5_check.py` no existe (`complete.py:455-465`) → COMPLETED inalcanzable.

### 7.2 TO-BE "1000/10"
Mantener el núcleo crash-safe (es de referencia), **cablear los 6 detectores**, añadir **métricas en el tiempo** con `domain` como origen exacto, ejecutar las reparaciones caras (conectadas al motor §1), y permitir **paralelo per-host** sin romper el agregado (gobernado por §3).

### 7.3 Gap, decisión y por qué
**Decisión: MANTENER y ELEVAR.** No migrar a Celery/Temporal — APScheduler+Postgres+advisory-locks es el patrón crash-safe correcto para la escala actual, validado por la tendencia 2025 "Postgres-as-queue". Lo que falta es activación (detectores), observabilidad temporal y ejecución de remedios.

### 7.4 Diseño técnico
- **Cablear detectores:** un job 6h que corra `dry_run_all` (los 6 €0) y enrute por el gestionador (state machine ya correcta, `route.py:229-248`).
- **Métricas:** cliente Prometheus por worker → `scraper_requests_total{domain,status}`, `scraper_blocks_total{domain,reason}`; Grafana success/ban-rate por dominio; Alertmanager → ban-rate per-domain dispara auto-reparación. El label `domain` **es** el origen exacto.
- **Paralelo per-host:** N workers asyncio tomando dealers con advisory-lock per-dealer + governor per-host compartido (§3) como embudo agregado.
- **Reparaciones caras:** conectar refingerprint→§1.fingerprints, escalate_tier→§1.tier1, re_receta→§2.cazador.
- **Cerrar G5:** implementar `g5_check.py` (2ª cosecha prueba delta) o redefinir el verdicto.

### 7.5 Herramientas/repos
- Prometheus + Grafana + Alertmanager ([Apify: Monitoring Scrapers with Grafana](https://use-apify.com/blog/monitoring-scrapers-grafana-dashboard)).
- Mantener APScheduler (no Temporal salvo workflows largos que justifiquen el peso).

### 7.6 Riesgos
- Paralelo per-host: verificar que el governor se clava al host real (no al dealer) — ver §3.6.

### 7.7 Criterios "hecho"
- [ ] Los 6 detectores corren en prod y abren gestion_items reales.
- [ ] Dashboard Grafana con success/ban-rate por dominio + alerta operativa.
- [ ] Una reparación cara (re_receta) se ejecuta de extremo a extremo.
- [ ] N workers cosechan en paralelo sin superar el ceiling agregado por host.

---

## 8. Arquitectura de datos y almacenamiento (local sample-and-delete vs VPS volcado total)

### 8.1 AS-IS — Nota **8.5/10**

**[VERIFICADO]** `evict.py` sample-and-delete con **3 gates duros re-leídos dentro de la transacción** (`evict.py:246-270`): (1) sin TRUSTWORTHY activo + evidencia REFUTED/UNVERIFIED; (2) **receta preservada** (recipe.yaml en git HEAD o cobertura por connector ~98%, `evict.py:139-171`); (3) `available=0` + sin gestion OPEN. **Protección de recetas:** `_measure_raw_files` solo escanea `data/`, **nunca toca `countries/ES/`** (`evict.py:60-61,281-286`). Borrado = tombstone (entity→`evicted`, vehicle→`gone`, NO DELETE — el trigger append-only abortaría); files físicos borrados **solo tras commit** (`evict.py:520-523`). LRU por mtime, watermark `DISK_EVICT_THRESHOLD_PCT=80`, ledger inmutable. Default `--dry-run`.

**Debilidad:** la eviction automática por capacidad **no corre** (manual Director-only, `capacity_ledger`/`audit_eviction` vacíos).

### 8.2 TO-BE "1000/10"
Local = **sample-and-delete automático** gobernado por el harness §2 (la muestra verificada se borra al cerrar el ciclo). VPS = volcado total (diferido). Frontera limpia entre ambos.

### 8.3 Gap, decisión y por qué
**Decisión: MANTENER (es sólido y seguro) y conectar el borrado al harness §2.** El diseño anti-pérdida (tombstone, recipe-protect, commit-then-delete) es de élite. Solo falta que el ciclo recipe-first dispare el borrado de la muestra automáticamente.

### 8.4 Diseño técnico
- El `harness.py` (§2), tras VERIFY OK, invoca `evict` sobre la muestra de ese cdp (gates ya garantizan que la receta está a salvo).
- Mantener la doctrina "better a hole than a lie": ningún borrado sin receta preservada + verdicto no-REFUTED.
- **Frontera local/VPS:** local nunca acumula inventario masivo (solo muestras efímeras + recetas); VPS recibe el volcado total cuando todo esté verificado.

### 8.5 Riesgos
- Borrado automático mal gateado destruiría muestras antes de verificar: los 3 gates re-leídos en transacción ya lo previenen; no debilitarlos.

### 8.6 Criterios "hecho"
- [ ] Ciclo §2 borra la muestra automáticamente tras VERIFY, con receta intacta en git.
- [ ] Eviction por watermark (80%) corre sin intervención manual y deja ledger.

---

## 9. Arquitectura de producción VPS (cuando toque — NO antes de verificación local total)

### 9.1 Estado: **no existe; diseño listo, despliegue diferido (mandato).**

### 9.2 TO-BE — topología canónica
```
VPS único (Docker Compose) — primera fase de producción:
  [APScheduler]  orquestador crash-safe (Postgres jobstore + advisory locks) — NO migrar a Celery
       ▼ cola de dealers (Postgres-as-queue ahora; Redis solo al saturar)
  [N workers asyncio disposables] cada uno:
     1. advisory-lock per-dealer
     2. checkout identidad sticky (lease en Postgres) — §3
     3. GOVERNOR PER-HOST compartido (embudo agregado) — §3
     4. cosecha (RecipeRunner §2) → delta → API
     5. métricas Prometheus {domain,status,reason} — §7
     6. ban → cooldown per-domain + alerta (origen = label domain)
  [Postgres] estado durable   [Prometheus+Grafana] observabilidad
  [Redis] OPCIONAL — solo al activar GCRA atómico a escala
Evolución solo si la escala lo exige: redis-GCRA → scrapy-redis → Temporal (workflows largos) → k8s (multi-VPS)
```

### 9.3 Decisiones y por qué
- **No introducir Redis aún:** Postgres ya soporta cola + jobstore + clock + buckets (pyrate-limiter). Menos piezas móviles.
- **Workers stateless disposables** en Docker (paridad dev/prod, escalado horizontal).
- **Seguridad:** secrets fuera de código (.env / secret manager), proxies y credenciales rotables, CSP/headers si hay superficie web pública.

### 9.4 Herramientas/repos
- Docker Compose; [scrapy-redis](https://github.com/rmax/scrapy-redis) (si migra a crawl masivo); [Temporal](https://temporal.io/) (si workflows per-dealer largos lo justifican).

### 9.5 Criterios "hecho"
- [ ] Compose levanta orquestador + workers + Postgres + Prometheus/Grafana en VPS limpia.
- [ ] Despliegue reproducible (imagen versionada) y rollback probado.
- [ ] **Precondición de gate:** 100% verificado en local antes de tocar la VPS (mandato).

---

## 10. Modelo de datos (entidad/particular) y API

### 10.1 AS-IS — Nota **8/10**

**[VERIFICADO]** Tablas núcleo: `entity` (PK `entity_ulid`, cdp_code inmutable), `entity_source`, `entity_alias`, `vehicle` (UNIQUE entity+deep_link), `vehicle_event` (append-only, trigger 0035), overlays no-destructivos `entity_cluster`/`vehicle_cluster`/`canonical_dedup` con vistas VAM-gated, `source_coverage` (gate GONE), ledgers inmutables. Invariantes DB reales (0041 muni[:2]=province; CHECK regex cdp_code). Cadena de resolución servida `v_dealer_resolved` (0028:35-76).

**Debilidades [VERIFICADO]:** (1) cdp_code sin UNIQUE CONSTRAINT → no FK-able; (2) proliferación de runs no servidos (`cross-source-dedup-v1` FALSE); (3) **3 sistemas de identidad solapados** (`entity_cluster` B1, `entity_resolution` β-fingerprint, `canonical_dedup` deeplink) sin un registro autoritativo único por endpoint → riesgo de deriva de conteos; (4) `entity_resolution-fingerprint-v1` vam_verified=TRUE pero no aparece en `v_dealer_resolved` (vive en paralelo).

### 10.2 TO-BE "1000/10"
Modelo entidad/particular con **una autoridad de identidad clara por endpoint**, cdp_code FK-able, y API con envelope consistente y delta servido.

### 10.3 Gap, decisión y por qué
**Decisión: MANTENER (el modelo es fuerte) y ELEVAR con consolidación de identidad.** Splink (§6) reduce los 3 sistemas a una autoridad probabilística. Documentar/forzar qué vista es autoritativa por endpoint.

### 10.4 Diseño técnico
- Promover `uq_entity_cdp_code` a CONSTRAINT (permite FK por cdp_code donde convenga) — migración reversible.
- Registro único `identity_authority(endpoint → run_id)` que declare qué overlay sirve cada endpoint (elimina la ambigüedad lexicográfica de `ORDER BY run_id DESC`).
- API: envelope `{success, data, error, meta}` consistente; exponer delta (price/photo/km history) por dealer/vehículo.

### 10.5 Riesgos
- Promover a CONSTRAINT requiere que el dedup haya colapsado duplicados lógicos primero (orden: Splink → constraint).

### 10.6 Criterios "hecho"
- [ ] Una sola autoridad de identidad declarada por endpoint (sin deriva de conteos).
- [ ] cdp_code FK-able tras dedup.
- [ ] API sirve delta history verificable por dealer.

---

## 11. ROADMAP por fases (cada punto como un PROYECTO)

> Orden gobernado por dependencias y por el mandato "verificar todo en local antes de VPS". Coste no es criterio; la secuencia lo es.

### FASE 0 — Fundaciones reutilizables (desbloquean el resto)
**P0.1 Unificar persistencia y contrato de adapter (§4).** Entregables: `_persistence.py`, Protocol `WholesaleConnector`, `_ingest_window` unificado. Verificación: grep==1 definición, paridad de inserts pre/post. Dependencias: ninguna. **Es prerequisito de P3 (delta) y P1 (receta ejecutable).**

**P0.2 Governor distribuible+persistente (§3, Fase A).** Entregables: backend PostgresBucket + AIMD. Verificación: test multi-proceso no supera ceiling; reinicio no reabre bucket. Dependencias: ninguna.

### FASE 1 — El harness de receta (corazón del mandato)
**P1 Harness recipe-first / sample-verify-delete (§2).** Entregables: `RecipeRunner`, `harness.py`, `cazador.py`, extractores 3-niveles (extruct→selectors→LLM-local). Verificación: ciclo E2E sobre ≥3 dealers de familias distintas, receta en git + 0 muestra en disco, reproducción solo-desde-YAML. Dependencias: P0.1 (receta ejecutable), §8 (borrado). **Proyecto de mayor ROI.**

### FASE 2 — Motor de antidetección agresiva
**P2.1 Transporte Tier-0 con rotación + proxies (§1).** Entregables: fingerprint pool, identity_pool, proxies ES en código. Verificación: rota ≥4 perfiles reales, IP de salida == pool. Dependencias: P0.2 (identidad+governor juntos).

**P2.2 Tier-1 (nodriver/Camoufox + cookie-harvester + ban_detector) (§1).** Entregables: motores challenge, patrón "browser genera cookie → curl_cffi sirve". Verificación: resuelve ≥1 portal CF-managed real (un dealer `family_unreachable`). Dependencias: P2.1. **Decisión legal AGPL nodriver antes de comprometer.**

### FASE 3 — Verificación y cobertura al 100%
**P3.1 Cablear delta vivo en la flota (§6).** Entregables: `diff_vehicle` en los 29 conectores vía `_persistence.py`. Verificación: PRICE/PHOTO/KM/GONE>0 tras 2ª cosecha. Dependencias: P0.1.

**P3.2 Despertar lentes VAM B y C + endurecer A (§5).** Entregables: evidence-store (B), refetch vivo (C), quórum para mono-lente. Verificación: C discrepa/confirma por egress independiente. Dependencias: P2.2 (C necesita egress separado).

**P3.3 Record-linkage Splink + denominador estadístico (§5,§6,§10).** Entregables: Splink dedupe+clustering, cross-source servido, denominador con IC (Rcapture+LCMCR) triangulado. Verificación: merge auditable, denominador nacional con IC bajo ≥2 modelos. Dependencias: P3.1.

### FASE 4 — Activación de orquestación y observabilidad
**P4.1 Cablear los 6 detectores + métricas en el tiempo (§7).** Entregables: job `dry_run_all` en prod, Prometheus+Grafana, ban-rate por dominio. Verificación: detectores abren gestion_items, dashboard operativo. Dependencias: ninguna fuerte.

**P4.2 Reparaciones caras ejecutables + G5 (§7).** Entregables: refingerprint/tier/re_receta conectados a §1/§2; `g5_check.py`. Verificación: una reparación cara E2E; COMPLETED alcanzable. Dependencias: P2.2, P1.

### FASE 5 — Producción VPS (solo tras verificación local total)
**P5 Topología VPS (§9).** Entregables: Docker Compose (orquestador+workers+Postgres+observabilidad), despliegue reproducible. Verificación: levanta en VPS limpia, rollback probado. **Precondición de gate: Fases 0-4 verificadas al 100% en local.**

### Diagrama de dependencias
```
P0.1 ─┬─> P1 ──────────────┐
      ├─> P3.1 ─> P3.3 ─┐  │
P0.2 ─┴─> P2.1 ─> P2.2 ─┼─>P3.2  └─> P4.2 ─┐
                        └─> P4.1 ──────────┴─> P5 (gate: todo local verificado)
```

---

## 12. Resumen ejecutivo

cardeep tiene un **núcleo de datos y orquestación de grado institucional y honesto**: clustering determinista verificado contra DB viva (31% de colapso real, no singletons), scheduler crash-safe con red de seguridad que cierra el fallo silencioso de los "138 dealers", observabilidad con alerta de origen exacto + dedup + watchdog (el subsistema más maduro, 9/10), sample-and-delete con protección de recetas a prueba de pérdida, y una doctrina VAM con quórum real. Nada de esto debe reescribirse: **se mantiene y se eleva.**

Los **dos huecos que más comprometen el mandato** son estructurales y están claramente localizados:
1. **El harness de receta ejecutable no existe** (la receta documenta pero no se ejecuta; el ciclo es scrape→ingest→receta post-hoc, no recipe-first/sample-verify-delete). → **Proyecto P1, el de mayor ROI.**
2. **El motor de antidetección agresiva / Tier-1 no está construido** (es un `raise`; sin proxies en código; fingerprint estático único). → **Proyectos P2.1/P2.2.**

Tres huecos de segundo orden los acompañan: **delta vivo infra-cableado** (1.7M altas vs <15k cambios — el motor late pero el delta no vive), **2 de 5 lentes VAM muertas** (verificación 100% endógena a la propia DB, sin camino externo al portal vivo) y **6 de 9 detectores sin caller en producción** (LIVE como código, muertos en operación). Todos son **activación/cableado de piezas correctas ya escritas**, no rediseños.

La estrategia es quirúrgica y respeta el marco: **corregir lo roto, elevar lo mejorable, reutilizar lo bueno.** El state-of-the-art confirma las elecciones base (curl_cffi competitivo, APScheduler+Postgres validado por la tendencia "Postgres-as-queue", Splink como estándar de record-linkage, captura-recaptura multi-lista para el denominador) y aporta lo que falta (nodriver/Camoufox para Tier-1, pyrate-limiter para distribuir el governor sin Redis aún, extruct+LLM-local para el long-tail, Prometheus para observabilidad temporal). La VPS no se toca hasta que las Fases 0-4 estén verificadas al 100% en local — el gate es el mandato.

### Matriz de notas as-is → to-be
| Área | as-is | to-be | Decisión |
|---|:---:|:---:|---|
| 1. Antidetección + transporte | 4.5 | 10 | Mejorar + construir Tier-1 |
| 2. Harness de receta | 3 | 10 | Reemplazar (construir) |
| 3. Governor distribuible | 7 | 10 | Mejorar (distribuir) |
| 4. Conectores/Adapters | 6 | 10 | Mejorar (unificar) |
| 5. Verificación VAM | 5.5 | 10 | Mejorar (despertar lentes) |
| 6. Identidad/record-linkage | 8 | 10 | Mantener + elevar (Splink) |
| 7. Orquestación/observabilidad | 8 | 10 | Mantener + elevar |
| 8. Datos/almacenamiento | 8.5 | 10 | Mantener |
| 9. Producción VPS | N/A | 10 | Diseñar (diferido) |
| 10. Modelo de datos/API | 8 | 10 | Mantener + elevar |
| **Global** | **~6.4** | **10** | **Quirúrgico** |

---

### Apéndice — Procedencia y honestidad
- **Auditoría (archivo:línea):** lectura directa por 5 agentes de auditoría sobre `pipeline/engine/`, `ops/`, `platform/`, `sources/`, `inquisition/`, `identity/`, `migrations/` + verificación cruzada contra DB viva (`cardeep-pg`, asyncpg :5433) en el caso de identidad/esquema.
- **State-of-the-art:** 4 agentes de investigación web con fuentes citadas (benchmarks independientes, repos GitHub, docs oficiales, papers).
- **`[ASUMIDO]` no cerrados:** (a) implicación AGPL de nodriver sobre el modelo API público; (b) precios/scoring interno de WAFs y SDKs comerciales (no públicos — requieren PoC propia); (c) inexistencia de paquete Python maduro de MSE (verificado entre fuentes consultadas, no exhaustivo); (d) que `v_dealer_resolved` es la vista que consume la API de producción (la migración lo afirma; no se leyó el endpoint). Cada uno se prueba en su fase correspondiente antes de comprometer decisión irreversible.
