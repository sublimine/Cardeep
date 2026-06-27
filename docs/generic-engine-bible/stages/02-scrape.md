# Etapa 2 · Scrapear — Biblia
> Estado adversarial: **NEEDS_REWORK** (`holds=false`) — **v2 PROFUNDO**. Fuente: Wave 1 + **30 deep-dives por faceta** (`relleno/02-scrape/g*.json`, lotes `g0..g6`). [VERIFIED path:línea] conservado; líneas load-bearing re-leídas en código. Stack vivo CAÍDO: cifras DB = punto-en-el-tiempo.
>
> **Funnel.** Lectura estrategica: Misión → Lo que existe → Motor/Pack → Costuras → Diseño genérico → Onboarding → Sellado → Veredicto adversarial. Capa PROFUNDA (átomo a átomo): **[Sub-proyectos institucionales — 30 facetas](#sub-proyectos-institucionales-360-por-faceta)** ([índice navegable](#indice-facetas)). Cierre: Mejoras → Riesgos.

---

## Misión
Convertir una **URL de fuente** en **listings genuinos** (vehículos + dealer), pasando los WAF sin quemar la IP ni servir basura, y **cristalizar el cómo en una receta reproducible** (`Recipe v2`) que es el activo — el crudo se evicta. Esta etapa es el **músculo determinista de capa-1** (24/7, autónomo): la escalera de tiers, el pacing, la anti-detección y el harness `sample-verify-delete`.

El **norte genérico** (00-MASTER §Norte): el motor de scrape no scrapea "España"; opera sobre **bytes, hosts y veredictos**. España es la primera ejecución que lo endureció, no el producto. País nuevo = **inyectar un pack**, no reescribir el motor.

> **La espina dorsal — confirmada por el inquisidor.** `country_code` se enhebró en el **esquema** (`0052/0053`) y en el **prefijo** `cdp_code`, pero **NO** en la **lógica** del scrape. Por debajo del esquema el motor sigue **country-BLIND**: el locale del fingerprint, el filtro de egress, el descubrimiento de stock, las firmas de bloqueo, la tabla de rate, el normalizador de identidad y el validador G1 están **soldados a ES**. Onboardar otro país hoy **exige editar el motor**, no un dato de pack. Eso es lo que esta etapa cierra.

---

## Lo que existe HOY (verificado)
El motor de scrape es maquinaria madura y, en su mayoría, country-agnóstica por diseño. Cada capacidad con su evidencia leída:

- **Escalera de fetch por tiers** — Tier-0 `curl_cffi` (impersonación coherente) → rotación de fingerprint en ban → Tier-1 navegador → route-around. Reintentos, backoff con full-jitter, escalado opt-in. `[VERIFIED pipeline/engine/fetch.py:64 (FetchEngine)]`, `[VERIFIED :207 (_fetch_tier0)]`, `[VERIFIED :283 (_fetch_tier1)]`.
- **Superficie pública estable del motor** — `open_session/fetch/fetch_dealer` con `ENGINE_API_VERSION`; los censos importan de aquí, no de internals. `[VERIFIED pipeline/engine/api.py:37 (ENGINE_API_VERSION='1.0.0')]`.
- **Pool de fingerprints REALES y coherentes** — TLS/JA3 + UA + client-hints de un mismo build, rotación sin-repetición, escalado a familias cross (Firefox/Safari) tras agotar Chrome. JA3 **nunca** aleatorio. `[VERIFIED pipeline/engine/fingerprints.py:149 (FingerprintPool)]`, `[VERIFIED :167 (rotate)]`.
- **Detección semántica de bloqueo** — un 200 puede ser interstitial, un 403 puede ser challenge resoluble; firmas de CF/DataDome/Akamai/PerimeterX/Imperva → veredicto `OK/CHALLENGE/BANNED/NOT_FOUND`. `[VERIFIED pipeline/engine/ban_detector.py:26 (Verdict)]`, `[VERIFIED :80 (classify)]`.
- **Governor de rate por host** — token-bucket asyncio-safe, min-spacing + jitter, clases `STEALTH (0.7 r/s)` vs `JSON_API (12 r/s)`, scar de ban en memoria. Único punto de estrangulamiento ante el fetch. `[VERIFIED pipeline/engine/governor.py:88 (JSON_API_*)]`, `[VERIFIED :102 (_HOST_RATE_CLASSES)]`.
- **Tier-1 cookie-reuse** — resuelve el challenge **una** vez en navegador real y mina cookie de clearance reutilizable; `camoufox (MPL-2.0)` por defecto, `nodriver (AGPL-3.0)` solo opt-in; humanización scroll/dwell. `[VERIFIED pipeline/engine/tier1/browser.py:67 (solve_challenge)]`.
- **Cache de clearance por host** — TTL 25 min in-memory; el 2.º drain reusa vía `curl_cffi` sin lanzar navegador. `[VERIFIED pipeline/engine/clearance_cache.py:26 (_DEFAULT_TTL=25*60)]`.
- **Cosecha de proxies libres** — proxyscrape/geonode/github raw + health-check paralelo + score (latencia + bonus Tier-1). Capa de resiliencia coste-cero. `[VERIFIED pipeline/engine/free_proxies.py:72 (fetch_candidates)]`, `[VERIFIED :160 (harvest_alive)]`.
- **Route-around por entidad** — lista ordenada de fuentes (own_site primero, marketplace duro último con `tier=1`); devuelve la primera con contenido genuino. `[VERIFIED pipeline/engine/source_fallback.py:50 (fetch_first_available)]`.
- **Esquema de receta ejecutable v2** — `Transport/Fingerprint/Pagination/Parsing/Evidence`, vocabulario cerrado `DRAFT/VERIFIED/FAILED`, (de)serialización round-trip. `[VERIFIED pipeline/recipe_schema.py:27 (SCHEMA_VERSION=2)]`.
- **Harness recipe-first `sample-verify-delete`** — extrae *k* listings, verifica con VAM (quórum declared/fetched/parsed), persiste receta y **BORRA** la muestra. `decide_status` exige `parse_loss==0` + VAM no-REFUTED. `[VERIFIED pipeline/recipe_harness.py:94 (decide_status)]`, `[VERIFIED :189 (sample.parsed.clear)]`.
- **RecipeRunner.replay** — reproduce una receta SOLO desde su YAML (prueba que la receta es asset auto-suficiente); `reproduced iff parse_loss==0`. `[VERIFIED pipeline/recipe_harness.py:237 (replay)]`.
- **42 conectores de plataforma** (38 `*_wholesale` + 4 `*_facet`) sobre un **único** `ensure_platform_entity` parametrizado por `PlatformSpec` (mata el drift de 29 copias hand-rolled); taxonomía multi-eje `defense_tier/source_group/role`. `[VERIFIED pipeline/platform/_core/contract.py:15 (PlatformSpec)]`, `[VERIFIED :40 (defense_tier opcional)]`, `[VERIFIED migrations/0016_tiering_groups.sql:6 (defense_tier ENUM)]`.
- **`mint_code()` ya country-paramétrico** — `CDP-{country}-{prov}-{base32}`, default ES byte-idéntico; `canonical_key` deliberadamente country-blind. `[VERIFIED services/api/codes.py:44 (mint_code)]`, `[VERIFIED :53 (f"CDP-{country_code}-...")]`, `[VERIFIED :62-65 (country NO entra al pre-image)]`.
- **Artefactos commiteados** — 61 recetas flat por-dealer + 14 Tier-1 (`countries/ES/_tier1/`) + recetas por `source_group` (`countries/ES/_platforms/`). `[VERIFIED countries/ES/recipes/ (61 yaml)]`.

**Veredicto del átomo:** el motor es ~90 % genérico **en mecanismo**; lo que falla es que **8 costuras de dato** y **3 puntos de identidad/sello** llevan ES soldado al engine.

---

## Motor (invariante, reusado byte-idéntico por país)
Lo que **NO** cambia entre países — el mecanismo puro, idéntico para ES/DE/FR/IT/PT/JP/MX:

| Invariante | Anclaje verificado | Por qué es país-blind |
|---|---|---|
| Escalera de tiers (retry, full-jitter, escalado) | `fetch.py:64,207,283` | Opera sobre URLs y bytes; ningún literal de país |
| Coherencia de fingerprint (perfil REAL, JA3 no-aleatorio, client-hints solo Chrome) y rotación sin-repetición | `fingerprints.py:149,167` | El **mecanismo** de coherencia es universal — *el locale dentro de él es pack* (ver costuras) |
| `ban_detector.classify()` — **firmas de vendor** (`cf-chl`, `geo.captcha-delivery.com`, `_incapsula_resource`, `_abck`) | `ban_detector.py:80` | Los tokens de WAF son globales del vendor — *las frases localizadas son pack* (ver costuras) |
| Matemática del token-bucket + clases `STEALTH/JSON_API` + scar de ban | `governor.py:88,168` | El **mecanismo** de pacing — *la tabla host→clase es pack* (ver costuras) |
| Patrón Tier-1 cookie-reuse (resolver una vez, fijar UA+JA3+IP, reusar `curl_cffi`) + cache TTL | `tier1/browser.py:67`, `clearance_cache.py:26` | Mina y reusa cookies sobre cualquier host |
| Esquema `Recipe v2` + round-trip | `recipe_schema.py:27` | `Transport.base_url`/`Pagination.url_template`/`Parsing.field_map` son URLs y selectores, no país |
| Ciclo `sample-verify-delete` + `decide_status` (parse_loss==0, VAM no-REFUTED) + `replay` | `recipe_harness.py:94,237` | El **método** de verificar y reproducir es universal |
| Protocolo `Extractor` (recipe_template + sample) como contrato de adaptador | `recipe_extractors.py:280` | Interfaz mínima; cualquier fuente nueva la implementa |
| `ensure_platform_entity` parametrizado por `PlatformSpec` | `_core/persistence.py:57` | SQL de una sola forma; columnas opcionales `bind NULL` |
| `mint_code()` como ÚNICO hogar del prefijo `CDP-{cc}-` | `codes.py:53` | Ya paramétrico (falta cablearlo en los 31 mints de plataforma — costura) |
| `country_of_cdp()` + helpers de `pipeline/paths.py` (derivan el árbol de país del `cdp_code`) | (Wave 1) | Genéricos por diseño (con un default ES peligroso — sealing-hole SH5) |
| Motor de proxies libres (health-check paralelo + score Tier-1) y route-around por prioridad | `free_proxies.py:72`, `source_fallback.py:50` | El **mecanismo**; *los filtros/prioridades son pack* |

---

## Pack por país (lo que cada país aporta para esta etapa)
El país **NO toca el motor**: aporta un `CountryScrapePack` (dato declarativo, commiteado bajo `countries/<CC>/_pack.py`) + conectores que reusan `_core` + recetas verificadas. El contrato del pack para esta etapa — **enriquecido con las costuras que el inquisidor destapó** (marcadas ⚠):

| Slot del pack | Contenido | Hoy soldado en |
|---|---|---|
| `country_code` | `"DE"`, `"FR"`… (segmento `{cc}` del `cdp_code`) | — (ya paramétrico en `mint_code`) |
| `accept_language` ⚠ | `"de-DE,de;q=0.9,…"` para los 3 perfiles de header | `fingerprints.py:46,65,80` |
| `proxy_country` ⚠ | Filtro de país del harvester de proxies libres | `free_proxies.py:27` |
| `host_rate_classes` ⚠ | `list[(host, RateProfile)]` — hosts del país clasificados `STEALTH`/`JSON_API` | `governor.py:102-148, 367-449` |
| `platform_roster` ⚠ | Plataformas que operan en el país (formas conocidas + **nativas**), cada una con su `base_url`/dealer-path y `defense_tier` | `autoscout24.py:21,67`, conectores |
| `fallback_priorities` ⚠ | Dureza local de cada marketplace (`own_site=10` invariante) | `source_fallback.py:75-86` |
| `web_lang_keywords` ⚠ | `{stock, count, marketplaces}` en la lengua del país (descubrimiento de stock + conteo declarado) | `recipe_extract_web.py:28-34` |
| `block_markers` ⚠ | Frases de bloqueo WAF **localizadas** (de/fr/it/pt/ja) | `ban_detector.py:64-73` |
| `normalize_policy` ⚠ | Política de transliteración por sistema de escritura (`ß→ss`, romaji/pinyin) — country-scoped, ES byte-idéntico | `codes.py:29-32` |
| `money_locale` ⚠ | Moneda + símbolo + separador decimal/millar (`€`/`MXN`/`¥`; `1.234,56` vs `1 234,56`) | `milanuncios_camoufox.py:28`, `recipe_extract_web.py:32` |
| `region_resolver` ⚠ | Resolutor `zip→province/region` del país (cross-ref Etapa 6 Geo) para el slot `{prov}` de 2 chars | `recipe.py:38`, `codes.py:44` |
| `recipe_set` | Las recetas YAML `VERIFIED` bajo `countries/<CC>/` tras pasar el harness | `countries/ES/` |
| `registral_sources` ⚠ | Oráculo registral del país para la familia VAM `registral` (KBA/SIV/Motorizzazione/IMT) — cross-ref Etapa 7 | `verify.py:48` (DGT/CNAE/BORME ES-only) |

> El pack original del átomo listaba 8 slots; la pasada adversarial **forzó 5 más** (`block_markers`, `normalize_policy`, `money_locale`, `region_resolver`, `registral_sources`). Sin ellos el "filtro es pack" que vendía el diseño es **falso en código**.

---

## Costuras ES-hardcoded → fix
Las 9 costuras donde el país está **soldado al motor**. Cada una con su `location | issue | fix` verificado:

| location | issue | fix |
|---|---|---|
| `pipeline/platform/*_wholesale.py` (31 mints) | `[VERIFIED]` 31 líneas `return f"CDP-ES-{PROVINCE_SENTINEL}-{_base32(digest)}"`; **0** conectores usan `mint_code` (importan `_base32`+`cdp_code` pero no el helper). País #2 mintaría `CDP-ES-` para SUS plataformas → **corrupción silenciosa de identidad**. | Importar `mint_code` y reemplazar el f-string por `mint_code(province_code=…, digest=digest, country_code=CC)`. `digest` y `_base32` idénticos → ES byte-idéntico (lo prueba `test_country_golden.py:173`). `CC` viaja en el `CountryScrapePack`/`PlatformSpec`. |
| `pipeline/complete.py:89` | `[VERIFIED]` `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — el validador **G1 hardcodea ES**; toda entidad extranjera falla identidad en silencio. Es el "6.º blocker oculto" vigilado por `xfail(strict)`. | Widenear a `r"^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$"` (superset estricto: acepta ES byte-for-byte + `CDP-DE-`/`CDP-FR-`). Quitar el `pytest.xfail` (`test_country_golden.py:287` auto-flip a XPASS). |
| `pipeline/engine/fingerprints.py:46,65,80` | `[VERIFIED]` `Accept-Language: es-ES,…` soldado en `_chrome/_firefox/_safari_headers`. Un drain de país #2 anuncia navegador **español** sobre host `.de` → tell de geo/locale, content servido en `es`, soft-block. | Parametrizar `accept_language` en las factory de headers (default `es-ES,…` = ES byte-idéntico). El `FingerprintPool` se construye con el locale del pack activo. |
| `pipeline/engine/free_proxies.py:26-27` | `[VERIFIED]` `_COUNTRY = "ES"` constante de módulo; `fetch_candidates()`/`harvest_alive()` **no aceptan arg de país** (proxyscrape/geonode reciben `&country=ES`). El comentario `:26` admite el acople. | Parametrizar `country` en `fetch_candidates`/`harvest_alive` (default `"ES"`); inyectar desde `pack.proxy_country`. Las plantillas `_PROXYSCRAPE`/`_GEONODE` pasan a funciones que formatean el país. |
| `pipeline/engine/governor.py:102-148, 367-449` | `[VERIFIED]` `_HOST_RATE_CLASSES` y todos los `configure_host()` son hosts ES (`www.autoscout24.es`, `web.gw.coches.net`, `searchapi.gw.milanuncios.com`…) cableados **dentro** del motor. Añadir país obliga a **editar el engine**. | Extraer la tabla `host→rate-class` a `pack.host_rate_classes`. El factory `governor()` carga las entradas del pack vía `configure_host` en bucle (ya existe en `:448`). El bucket no se toca. |
| `pipeline/platform/_recipes_runtime/milanuncios_camoufox.py:5` | `[VERIFIED]` `locale='es-ES'`, `os='windows'`, dominio `www.milanuncios.com` y selectores ES soldados en la receta runtime Tier-1. | milanuncios es marca ES → su equivalente Tier-1 de país #2 vive como **otra receta runtime** en su propio `_recipes_runtime` con su locale/dominio. Parametrizar `locale` si la misma marca opera multi-país. |
| `pipeline/recipe_extract_web.py:28-34` | `[VERIFIED]` `_STOCK_HINT` casa solo slugs **españoles** (`coches\|vehiculos\|ocasion\|segunda-mano\|km0…`); `_COUNT_HINT` solo `veh[ií]culos\|coches`; `_MARKETPLACES` ES. El `GenericWebExtractor` — el rung coste-0 universal, el **más reusado** para la cola larga — no descubre stock fuera de ES. | Mover los keywords a `pack.web_lang_keywords` (regex de stock-hint + count-hint + marketplaces). El extractor recibe el language pack; ES default = los actuales. |
| `pipeline/engine/source_fallback.py:75-86` | `[VERIFIED]` `DEFAULT_PRIORITIES` mapea claves de marketplaces ES (`coches_net`, `autocasion`, `wallapop`, `milanuncios`) con su dureza. Otro país → otras claves y dureza. | Parametrizar `pack.fallback_priorities` (dict por país); `own_site=10` invariante, el resto del roster del país. |
| `pipeline/recipe.py:20-40 (AS24_RECIPE default)` | `[VERIFIED]` el default de `write_recipe()` es una receta ES-shaped (`/profesionales/{slug}`, dominio AS24 ES). Solo fallback, pero **acopla** el módulo de persistencia a una plataforma ES. | **Bajo (cosmético):** el path ya es genérico vía `country_of_cdp`. Mover `AS24_RECIPE` al pack de ES; `write_recipe()` exige receta explícita (ya lo hace el harness). No bloquea replicación. |

---

## Diseño genérico A→Z — la abstracción country-proof
**SEPARAR MOTOR (mecanismo, country-blind) de PACK (dato, por-país)**, sin reescribir una línea de ES. Tres piezas:

### 1) Un dataclass `CountryScrapePack` (inyección de dato)
Agrupa las 13 costuras como **dato declarativo**, commiteado bajo `countries/<CC>/_pack.py`:

```python
@dataclass(frozen=True)
class CountryScrapePack:
    country_code: str                                  # 'DE'
    accept_language: str                               # 'de-DE,de;q=0.9,en;q=0.8'
    proxy_country: str                                 # 'DE'
    host_rate_classes: list[tuple[str, RateProfile]]   # [( 'www.autoscout24.de', STEALTH_AS24 ), ...]
    platform_roster: list[PlatformConnectorRef]        # formas conocidas + nativas
    fallback_priorities: dict[str, int]
    web_lang_keywords: WebLangKeywords                 # {stock, count, marketplaces}
    block_markers: tuple[str, ...]                     # frases WAF localizadas de/fr/it…
    normalize_policy: NormalizePolicy                  # transliteración por script (default ES)
    money_locale: MoneyLocale                          # símbolo + separadores
    region_resolver: RegionResolverRef                 # zip->region (Etapa 6)
    registral_sources: tuple[RegistralSource, ...]     # KBA/SIV… (Etapa 7)
```

El motor lo lee **en construcción**: `open_session(pack=...)` propaga `accept_language` al `FingerprintPool`, `proxy_country` a `free_proxies`, y `governor()` carga `host_rate_classes` en su bucle ya-existente (`governor.py:448`). **Default ES** en cada campo → ES byte-idéntico, **cero regresión**.

### 2) Abstracción de conector = `(parser_invariante, country_anchor)`
Un conector de plataforma es un par. El **parser** (extraer `__NEXT_DATA__`/GraphQL/JSON-LD → `Vehicle`) es **idéntico cross-país** — el piloto DE probó que AS24 `.de` coexiste byte-idéntico con `.es` (`test_country_coexistence.py`). Lo único que cambia es el **`country_anchor`**: dominio base (`autoscout24.es → .de`), dealer-path (`/profesionales → /haendler`), entrada en `host_rate_classes`, y el segmento `{cc}` del `cdp_code`. El `PlatformSpec` (`contract.py:15`) absorbe la identidad; se le añade `country_code` para que su mint enrute por `mint_code(country_code=CC)` en vez del f-string `CDP-ES-`.

### 3) Portabilidad de receta = re-anclar + RE-VERIFICAR
La receta YAML ya es country-agnóstica en **esquema**. Portar = re-anclar `Transport.base_url` al dominio del país y **re-verificar vía harness** (`sample-verify-delete`) sobre un dealer muestra del país. Si parsea con `parse_loss==0` y VAM no REFUTA, se sella como `countries/<CC>/…yaml`. **El parser no se duplica**: el mismo `Extractor` sirve, solo cambia el `base_url` que ya viaja en el `Transport`.

### Modelo 3-capas aplicado (00-MASTER §Modelo de ejecución)
- **Capa-1 músculo determinista (24/7):** el motor de tiers — ya existe.
- **Capa-2 IA-local obrera:** SOLO el rung irreducible — síntesis de `field_map` para webs JS-rendered que el `GenericWebExtractor` deja en `FAILED` (hoy **0 en código**, declarado en `recipe_extract_web.py:9`). Salida forzada por gramática (ANTI-DRIFT §1).
- **Capa-3 Claude:** decide el `platform_roster` del país y aprueba recetas en ráfagas; nunca dentro del bucle caliente.

### Estructura de datos
`countries/<CC>/{_pack.py, recipes/, _tier1/, _platforms/<source_group>/, census/}` (espejo de `countries/ES/`). El `cdp_code` `CDP-<CC>-<prov>-<base32>` es la clave que enruta todo; `country_of_cdp` deriva el árbol sin DB.

**La genericidad se logra por inyección de pack y enrutado por `mint_code`, no por reescritura.**

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)
Precondición: `cover(CC)` en estado `KNOW_COUNTRY` (la inteligencia de mercado ya derivó el roster — 00-MASTER §Doctrina de onboarding).

1. **Crear el árbol** `countries/<CC>/` con subdirs `recipes/`, `_tier1/`, `_platforms/<source_group>/`, `census/`.
2. **Autorizar `countries/<CC>/_pack.py`:** `country_code`, `accept_language` (ej. `'de-DE,de;q=0.9'`), `proxy_country`, `web_lang_keywords` (stock/count/marketplaces en la lengua), `fallback_priorities`, `block_markers` localizados, `normalize_policy`, `money_locale`, `region_resolver`.
3. **Enumerar el roster** (capa-3 Claude): qué formas conocidas operan ahí (AS24 `.de`, marketplaces motor nativos, OEM-VO, cadenas, subastas) + las plataformas **NATIVAS** sin equivalente ES.
4. **Para cada plataforma de forma compartida:** re-anclar `base_url` + dealer-path al dominio del país en su `recipe_template`, añadir el host a `host_rate_classes` con su clase, clasificar `defense_tier`.
5. **Para plataformas nativas:** construir el conector reusando `_core/contract.py` (`PlatformSpec` con `country_code`) + `_core/persistence.py`, escribiendo SOLO un parser; o `GenericWebExtractor` para sitios de dealer con JSON-LD.
6. **Cablear los mints:** todos vía `mint_code(province_code=…, digest=…, country_code=CC)`; verificar `grep` **0** ocurrencias de `CDP-ES-` en los conectores del país nuevo.
7. **Correr `RecipeHarness.run`** (`sample-verify-delete`) contra *k* dealers por plataforma; commitear SOLO las recetas `status=VERIFIED` bajo `countries/<CC>/recipes|_tier1`.
8. **Probar reproducibilidad:** `RecipeRunner.replay` sobre cada YAML del país (`reproduced iff parse_loss==0`).
9. **Verificar no-regresión ES:** `tests/test_country_golden.py` + `test_country_coexistence.py` (ES byte-idéntico, CC coexiste). Widenear `complete.py:89` y quitar el `xfail`.
10. **Registrar hosts** del país en el governor vía el bucle de pack (`configure_host`) y validar que **ningún `JSON_API` quede en `STEALTH`** por omisión (el bug milanuncios, `governor.py:144-147`).

---

## Sellado + verificación multi-vía + rollback
**SELLADO de esta etapa** = cada plataforma del roster del país tiene una receta `status=VERIFIED` bajo `countries/<CC>/` con `parse_loss==0` y VAM no-REFUTED (`recipe_harness.py:94`), **Y** `RecipeRunner.replay` la reproduce SOLO desde su YAML (`recipe_harness.py:237`), **Y** cero fuga: `grep` 0 `CDP-ES-` en los conectores del país + 0 `CDP-<CC>-` contaminando ES.

**Verificación por 2.ª vía ortogonal — tres ejes independientes (nunca el mismo parser que escribió el dato):**
- **(a) VAM (cuenta) ⊥ parser** — compara `declared` (oráculo de la fuente, familia *source*) vs `fetched` (lo que el transporte consumió, *http*) vs `parsed` (lo que el parser produjo, *db*). Una receta que parsea pero **mis-cuenta** REFUTA aunque el parser "funcione" (`recipe_harness.py:88-90`).
- **(b) byte-identidad (hash)** — `test_country_golden.py` prueba `mint_code` default == ES literal y que `canonical_key` es country-blind (no re-keya los `cdp_code` existentes — punto-en-el-tiempo).
- **(c) coexistencia (reproducibilidad)** — `test_country_coexistence.py` probó que el piloto DE convivió byte-idéntico con ES **y se revirtió**.

**ROLLBACK:** las recetas son YAML commiteado → `git revert` del árbol `countries/<CC>/`. El motor es **100 % aditivo** (`open_session(pack=)` con default ES; `mint_code()` defaultea a ES). Un país a medio-onboardear **nunca** corrompe ES (su `canonical_key` no incorpora país por diseño, `codes.py:62-65`). Borrar `countries/<CC>/` + la entrada de pack revierte el país sin tocar motor ni ES.

**El "100 %" del país es un INTERVALO certificado:** cota inferior = `#recetas VERIFIED / #plataformas del roster`, que crece al sellar más plataformas; **nunca un entero**.

> ⚠ **El sello actual tiene 6 agujeros** (abajo, SH1–SH6): prueba consistencia interna pero **no coherencia de país/locale/geo**. La biblia del sellado de esta etapa **no está cerrada** hasta resolverlos.

---

## Veredicto adversarial: roturas → resolución
`holds=false → NEEDS_REWORK`. **Ninguna rotura se oculta.** Por cada break, pack ausente y agujero de sellado: su resolución de diseño (cómo se cierra para DE/FR/IT/PT/no-UE) o, si no se puede cerrar, **OPEN ITEM con causa + gating**.

### A · Roturas (breaks)

| # | Sev | Rotura `[VERIFIED]` | Resolución |
|---|---|---|---|
| **B1** | CRITICAL | `fingerprints.py:46,65,80` clavan `es-ES` en los 3 perfiles. El "modelo de coherencia" que el diseño vende invariante lleva el locale soldado: navegador es-ES sobre host `.de` = **incoherencia**. | **CERRABLE.** El **mecanismo** de coherencia es invariante; **el locale es pack** (`accept_language`). Costura fingerprints → fix de la tabla. ES default byte-idéntico. Re-clasificado: locale = pack, no motor. |
| **B2** | CRITICAL | `free_proxies.py:27` `_COUNTRY="ES"` constante; sin arg de país. La capa de resiliencia solo cosecha proxies **españoles**; el comentario `:26` admite el acople. | **PARCIAL.** El harvester libre se parametriza (`pack.proxy_country`) → **€0, cerrable**. Pero el **egress residencial sticky** por país (que la cookie Tier-1 exige, `browser.py:33-36,61`) es **OPEN ITEM** — causa: free proxies son efímeros/flaky sobre IP datacenter; gating: **GASTO** (proxy residencial €>0 + firma owner). |
| **B3** | CRITICAL | `autoscout24.py:21` `_BASE='https://www.autoscout24.es'`, `:67` path `/profesionales/` (ES; DE `/haendler/`, FR `/marchands/`, IT `/concessionari/`), y usa **`urllib` crudo** (`:72-73`), NO el `FetchEngine`. La plataforma exemplar del diseño exige **reescribir la fuente por país** → rompe "holds sin tocar código". | **REWORK REQUERIDO (diseñado).** Refactor de `autoscout24.py`: (1) `base_url` + `dealer_path` inyectados desde `PlatformSpec`/pack; (2) `fetch_page` enruta por `FetchEngine` (gana governor + fingerprint + ban-detect). Tras el refactor, DE/FR/IT son **puro pack**. El parser `__NEXT_DATA__` ya es invariante (piloto DE lo probó). **No es un break de diseño; es deuda de cableado del exemplar.** |
| **B4** | CRITICAL | `recipe_extract_web.py:28-30` `_STOCK_HINT` solo slugs ES; `:32` `_COUNT_HINT` solo `veh[ií]culos\|coches`. El rung coste-0 universal **no descubre stock** en DE `/fahrzeuge`, FR `/vehicules`, IT `/usato`, PT `/viaturas`, JP `在庫/中古車` → `find_stock_url=None` → muestra vacía → receta `FAILED`. | **CERRABLE.** `pack.web_lang_keywords` (stock + count + marketplaces por idioma). ES default = los actuales. Restaura además `declared` para el VAM (ver SH2). |
| **B5** | HIGH | `codes.py:29-32` `_normalize` hace `NFKD + encode('ascii','ignore')` que **DESCARTA** no-ASCII (no translitera): `'トヨタ' → ''`. Dealer JP sin domain/CIF cae a `name:|{muni}` **idéntico** para todos los name-only de un municipio → **MASS FALSE DEDUP**. En DE `'ß'` se descarta → `Strasse`≠`Straße` **no** deduplican. | **OPEN ITEM (cross-ref Etapa 4 Identidad).** Causa: `canonical_key` es el **pre-image inmutable**; cambiar `_normalize` re-keya las entidades ES existentes (rompe golden). Resolución de diseño: `pack.normalize_policy` **country-scoped** (default = `_normalize` actual, ES byte-idéntico; no-ES aplica transliteración `ß→ss`, romaji/pinyin) aplicada **antes** del hash, sin tocar la rama ES. Gating: el golden `test_country_golden.py` debe seguir verde (ES intacto). **La política country-blind no es feature: asume escritura latina.** |
| **B6** | HIGH | `ban_detector.py:64-73` `_STRONG_BLOCK_MARKERS` (los únicos size-independent) **mezclan** tokens de vendor con **texto ES**: `'algo se detuvo'`, `'para continuar, completa el captcha'`. Una página PerimeterX/DataDome en de-DE/ja-JP >30 KB sin el EN `'pardon our interruption'` puede clasificar `Verdict.OK` → interstitial servido como inventario. | **CERRABLE.** Partir los markers: los **tokens de vendor** (`geo.captcha-delivery.com`, `_incapsula_resource`, `attention required! \| cloudflare`) quedan **invariantes** en el motor; las **frases localizadas** pasan a `pack.block_markers` (de/fr/it/pt/ja). El guard de sample-vacío salva el caso 0; el sello gana un assert de locale (SH4). |
| **B7** | HIGH | `governor.py:376-377` el scar AS24 `0.5 r/s` está clavado a `www.autoscout24.es`/`autoscout24.es`. `www.autoscout24.de` **NO** está en `_HOST_RATE_CLASSES` → hereda el `STEALTH` default `0.7 r/s` (`:94-95`), **MÁS ALTO** que el `0.5` con el que la **misma** plataforma se ganó un ban. No hay puente `PlatformSpec.defense_tier` → rate-class. | **CERRABLE (missing_pack MP5).** Bindear la rate-class a `PlatformSpec.defense_tier` (`contract.py:40`, ya existe el campo) en vez del host-TLD. Una plataforma frágil conocida conserva su pace `0.5` en **todos** sus TLDs. El bucket no se toca. |
| **B8** | MEDIUM | `codes.py:53` `mint_code` con `canonical_key` country-blind (`:62-65`): una entidad pan-EU con `domain:europcar.com` descubierta bajo dos países produce el **mismo `base32`** pero prefijos `{cc,prov}` divergentes → **dos `cdp_codes`** para una entidad canónica. El roster ya tiene backends multi-market (`toyota-europe`, `nissanpace`, `api-carmarket.ayvens.com`, `codeweavers`) con el market clavado a ES. | **OPEN ITEM (cross-ref Etapa 4 + transversal).** Causa: la espina dorsal — `canonical_key` country-blind es feature ES que **rompe cross-border**. Resolución de diseño: el **market/tenant** entra en la clave para multi-market (`domain:europcar.de` ≠ `.es`) **o** se decide por scope (huella DIGITAL por país → el storefront `.de` ES un POS distinto del `.es`). Gating: toca el invariante de código inmutable; requiere decisión de identidad antes de cablear. **No se cierra en scrape solo.** |
| **B9** | MEDIUM | `codes.py` `mint_code` exige `province_code` de 2 chars y `recipe.py:38` mapea `zip→province`. El primer-2 del CP español **ES** el código INE de provincia (coincidencia ES). DE PLZ no → Bundesland; JP usa `〒NNN-NNNN`→prefectura; IT CAP no → sigla; FR ~departement (salvo Córcega 2A/2B). | **CERRABLE vía pack + cross-ref Etapa 6 Geo.** `pack.region_resolver` (`zip→region` por país) alimenta el slot `{prov}`. **Flag de esquema:** el slot de 2-char asume INE; revisar ancho para prefecturas/estados (cross-ref el `CHAR(2)` transversal). El scrape difiere la resolución al geo-pack. |
| **B10** | MEDIUM | `milanuncios_camoufox.py:28` clava `€` + campo `price_eur`, `:31` regex de combustible ES (`diesel\|gasolina\|hibrido`). MX=MXN, JP=¥. Además `recipe_extract_web.py:32` `_COUNT_HINT \d{1,5}` no maneja separador de millar: `'1.234 Fahrzeuge'` no casa, y aun en ES `'1.234'` se mal-parsea a `234`. | **CERRABLE.** `pack.money_locale` (símbolo + separadores decimal/millar + mapa de combustible). Bug de millar = fix universal del `_COUNT_HINT` (afecta también a ES). La receta runtime milanuncios es per-plataforma ES → su equivalente vive en el `_recipes_runtime` del país. |
| **B11** | LOW | Recetas/runtime ES viven en el **namespace del ENGINE**, no bajo `countries/ES/`: `_recipes_runtime/milanuncios_camoufox.py`, `sources/autoscout24.py`, `recipe.py:20 AS24_RECIPE`, `recipe_extract_web.py:133`. Viola la propia costura del diseño. | **CERRABLE (higiene).** Reubicar los artefactos ES bajo `countries/ES/` para partición limpia. No bloquea replicación; lo hace el paso 1 del onboarding al espejar el árbol. |

### B · Pack ausente (missing_pack)
Cada uno mapeado a su slot del pack + estado:

| # | Pack ausente | Slot que lo absorbe | Estado |
|---|---|---|---|
| MP1 | Locale/Accept-Language por país | `accept_language` | CERRABLE (B1) |
| MP2 | País/geo del egress | `proxy_country` (libre) + residencial | PARCIAL — residencial **OPEN/GASTO** (B2) |
| MP3 | Strings de bloqueo WAF localizados | `block_markers` | CERRABLE (B6) |
| MP4 | Vocabulario stock + conteo por idioma | `web_lang_keywords` | CERRABLE (B4) |
| MP5 | Rate-class por `defense_tier` (no por host) | bridge `PlatformSpec.defense_tier→RateProfile` | CERRABLE (B7) |
| MP6 | Normalización/transliteración por script | `normalize_policy` | OPEN — cross-ref Identidad (B5) |
| MP7 | Taxonomía provincia/región + `zip→region` | `region_resolver` | CERRABLE — cross-ref Geo (B9) |
| MP8 | Market/tenant/locale de gateways pan-EU | param de market en `PlatformSpec` | OPEN — cross-ref Identidad (B8) |
| MP9 | Host + dealer-path por país (AS24 `/profesionales`→`/haendler`) | `platform_roster` anchors | CERRABLE (B3) |
| MP10 | Moneda + símbolo + formato numérico | `money_locale` | CERRABLE (B10) |
| MP11 | Fuentes registrales/oráculo por país (familia VAM `registral`) | `registral_sources` | **OPEN ITEM** — causa: `verify.py:48` DGT/CNAE/BORME/FacoNauto son **ES-only**; sin KBA/SIV/Motorizzazione/IMT el sello no alcanza quórum registral fuera de ES. Gating: disponibilidad de fuente + **LEGAL** (ToS/RGPD-equiv). Cross-ref Etapa 7. |

### C · Agujeros de sellado (sealing_holes)

| # | Agujero `[VERIFIED]` | Resolución |
|---|---|---|
| **SH1** | El sello prueba `fetched==parsed` + VAM-no-REFUTED + replay, pero **NO** coherencia de país/locale/geo. Un sitio DE servido en español (por `Accept-Language: es-ES`) o geo-redirigido a una página ES **parsea limpio → VERIFIED** sobre la vista locale/geo equivocada. | **Nuevo gate de sello:** assert de coherencia. El pack carga `accept_language`/`money_locale` esperados; el harness verifica que el `lang`/`currency` de la página servida **coincide** con el pack, si no → REFUTE. Cierra junto a B1/B6. |
| **SH2** | El VAM se degrada en silencio fuera de ES: `declared` (familia *source*) es `None` cuando las palabras de conteo no casan (`recipe_harness.py:89` solo añade el path si `s.declared is not None`) → cae de quórum 3-familias a 2-paths → a lo sumo `UNVERIFIED`. La familia `registral` no existe fuera de ES. | **PARCIAL.** (a) Fix de `_COUNT_HINT` vía `web_lang_keywords` restaura `declared` (B4). (b) **Declarar política de quórum no-ES explícita** en el criterio (qué familias se exigen sin `registral`). Mientras MP11 siga OPEN, el intervalo 100 % **no puede estrechar** fuera de ES — el sello sub-certifica (fail-safe), honesto. |
| **SH3** | `parsed` cae a la familia catch-all `other` en `_path_family` (`verify.py:42-50`): `http`-vs-`other` se cuentan como 2 familias "ortogonales" aunque `parsed` es **subconjunto de los mismos bytes** `fetched`. Fuera de ES (sin path `source`/`registral`) pasa a ser la **única** base de un TRUSTWORTHY → ortogonalidad débil. | **REWORK en la definición de sello (pre-existente).** Endurecer `_path_family` para que `parsed` **no** cuente como familia independiente vs los bytes de los que salió; exigir una familia genuinamente independiente (`source`-count o `registral`) para TRUSTWORTHY. Afecta a ES y no-ES por igual. |
| **SH4** | Una página de bloqueo localizada >30 KB con schema.org rancio puede pasar el sello (`fetched==parsed`, VAM no REFUTED) → **FALSE VERIFIED**, porque `ban_detector` no reconoce el mobiliario de bloqueo no-ES. | **Combina B6 + SH1** (block_markers de pack + assert de locale) **más** una heurística "¿inventario real vs error estilizado?" (mín. vehículos distintos, presencia de precio). Nuevo gate del sello. |
| **SH5** | `country_of_cdp` (`paths.py:62-63`) **DEFAULTea a `'ES'`** ante código malformado → un bug de mint en país nuevo vuelca sus recetas en `countries/ES/` **sin error**; ni sello ni rollback verifican que el país persistido coincide con el país objetivo del drain. | **Hardening CERRABLE.** `country_of_cdp` **fail-loud** ante código malformado (sin default ES) **o** assert en el sello: `recipe.country == drain.target_country`. Evita contaminación cross-country silenciosa. Prioridad alta del rework. |
| **SH6** | Granularidad de rollback: el sello es **por-receta YAML**; no hay unidad country-scoped para revertir atómicamente "todas las recetas DE", y el guard de clobber (`recipe.py:88-91 R3`) solo **LOGea**, no bloquea, una sobrescritura cross-country. | **CERRABLE.** Unidad de sello/rollback **country-scoped**: manifiesto por país + `git revert` del árbol `countries/<CC>/` (ya atómico-ish). El guard de clobber pasa de log a **BLOCK** ante sobrescritura cross-country. |

---

## Sub-proyectos institucionales (360 por faceta)
> **Que es esto.** El motor de scrape se descompone en **30 facetas atomicas**; cada una se trata como un **proyecto institucional 360** — su deep-spec verificada (a-f) + una ficha de combate (costura / fix / adversarial / sellado / herramienta NEXT-LEVEL). "360" = el grado de cobertura por faceta, no el numero de facetas. Es la capa PROFUNDA que expande, atomo a atomo, las roturas del Veredicto adversarial.
>
> **Numeracion canonica.** Las referencias cruzadas *"faceta NN"* dentro de las deep-specs resuelven contra esta lista 1-30 (orden column-major de los lotes `g0..g6`). Cada faceta declara su **estado crudo**: `CERRABLE` (cierra por inyeccion de pack), `PARCIAL`/`OPEN` (residual con causa + gate), `REWORK-SELLO` (exige rework de la definicion de sello), `MECANISMO-PURO` (country-blind, sin costura de dato).
>
> **Procedencia.** 29/30 facetas tienen deep-dive dedicado en `relleno/02-scrape/g*.json`; la **faceta 23** (`mint_code`) se reconstruye desde la costura #1 [VERIFIED] del cuerpo v1 — el lote `g*` duplico `canonical_key` en ese slot. Declarado en su subseccion, sin placeholder.

<a id="indice-facetas"></a>
### Indice navegable (1-30)

| # | Faceta | Grupo | Resuelve | Estado | Costura en una linea |
|---|---|---|---|---|---|
| [1](#f1) | Escalera de fetch Tier-0 (retry / backoff / escalado / fail-loud) | Transporte por tiers & pacing | enabler (consume 4/2/3) | MECANISMO-PURO | arbol verdict/backoff country-blind; costura indirecta via lo que consume |
| [2](#f2) | Pool de fingerprints coherentes & rotacion sin-repeticion | Identidad de navegador & anti-deteccion | B1 / MP1 | CERRABLE | Accept-Language es-ES soldado en los 3 factories de header |
| [3](#f3) | Pack de locale & coherencia con geo de egress | Identidad de navegador & anti-deteccion | B1 / MP1 / MP2 / SH1 | CERRABLE (egress PARCIAL) | locale/geoip del navegador sin conciliar con la IP de egress |
| [4](#f4) | Clasificador semantico de bloqueo & gobierno de firmas WAF | Identidad de navegador & anti-deteccion | B6 / MP3 / SH4 | CERRABLE | prosa de interstitial ES en _STRONG_BLOCK_MARKERS + size-gate magico 30000 |
| [5](#f5) | Solve Tier-1 en navegador real (challenge + mint de cookie) | Identidad de navegador & anti-deteccion | B2 / licencia(6) | PARCIAL (proxy OPEN/GASTO) | solve country-blind salvo proxy 'ES sticky' + locale/geoip sin cablear |
| [6](#f6) | Gobierno de licencia de engines Tier-1 (AGPL / MPL / Apache) | Identidad de navegador & anti-deteccion | RIESGO AGPL nodriver | CERRABLE (mejora #3) | garantia de licencia auditada solo sobre el arbol ES |
| [7](#f7) | Reuso & cache de cookie de clearance (multiplicar un solve) | Identidad de navegador & anti-deteccion | mecanismo (consume 11/3) | MECANISMO-PURO | cookie atada a IP exige egress geo-coherente (contrato, no codigo ES) |
| [8](#f8) | Governor token-bucket por host (el unico cuello) | Transporte por tiers & pacing | mecanismo (-> 10) | MECANISMO-PURO | math del bucket country-blind; unico dato ES = la tabla de hosts (9) |
| [9](#f9) | Tabla de rate-class por host & binding por defense_tier | Transporte por tiers & pacing | B7 / MP5 | CERRABLE | _HOST_RATE_CLASSES hosts ES + puente defense_tier->rate-class inexistente |
| [10](#f10) | Estado de rate distribuido multi-proceso (PG / Redis) | Transporte por tiers & pacing | mecanismo / infra | MECANISMO/INFRA | backend distribuido cableado pero default in-memory single-proceso |
| [11](#f11) | Capa de IP de egress: pool sticky por-drain & residencial | Egress & resiliencia de IP | B2 / MP2 | PARCIAL (residencial OPEN/GASTO) | harvester por defecto y PENDING-CREDENTIAL asumen geo ES |
| [12](#f12) | Cosecha & health-scoring de proxies libres (coste-cero) | Egress & resiliencia de IP | B2 / MP2 | CERRABLE (+residencial OPEN) | _COUNTRY='ES' soldado en 3 URLs de fuente de proxies |
| [13](#f13) | Route-around por entidad (fallback own-site-first) | Egress & resiliencia de IP | MP9 (fallback) | CERRABLE | DEFAULT_PRIORITIES = roster ES; .get(key,60) hunde el WAF nacional ajeno |
| [14](#f14) | Contrato CountryScrapePack & inyeccion en el motor (keystone) | Pack keystone (inyeccion) | KEYSTONE (B1/B4/B6/B7/B9/B10 + MP1-MP10) | KEYSTONE-CERRABLE | cada costura soldada en su modulo; el pack las levanta a dato declarativo |
| [15](#f15) | Esquema de receta v2 & persistencia round-trip | Receta como activo & cobertura | SH5 | CERRABLE (+hardening) | AS24_RECIPE default ES + country_of_cdp defaultea ES ante codigo malformado |
| [16](#f16) | Harness sample-verify-delete & decide_status | Verificacion cero-confianza & sello | SH1 / SH3 | REWORK-SELLO | decide_status solo asevera cuenta, no coherencia locale/geo/moneda |
| [17](#f17) | RecipeRunner replay (prueba de auto-suficiencia) | Receta como activo & cobertura | DEUDA replay (5/42) | DEUDA -> CERRABLE | replay re-ejecuta Python por fuente en vez de interpretar el YAML |
| [18](#f18) | VAM count-quorum & oraculo registral por pais | Verificacion cero-confianza & sello | MP11 / SH2 / SH3 | OPEN (registral/LEGAL) | familia 'registral' de _path_family keyed a tokens ES (dgt/cnae/borme) |
| [19](#f19) | Protocolo Extractor & cobertura del registro (5/38 -> roster) | Receta como activo & cobertura | DEUDA cobertura (5/42) | DEUDA -> CERRABLE | solo 5/38 wholesale implementan el protocolo Extractor |
| [20](#f20) | Exemplar cross-pais AutoScout24 (parser-invariante / country-anchor) | Receta como activo & cobertura | B3 / MP9 | REWORK (cableado exemplar) | ancla ES soldada en 3 sitios + urllib crudo sin anti-deteccion |
| [21](#f21) | Extractor web generico de cola-larga & pack de keywords de idioma | Receta como activo & cobertura | B4 / MP4 / SH2 | CERRABLE | _STOCK_HINT/_COUNT_HINT/_MARKETPLACES con slugs y palabras ES |
| [22](#f22) | Contrato strangler de connector & roster de plataformas (_core) | Identidad de entidad, geo & cross-border | MP-plataforma (-> 23) | CERRABLE | PlatformSpec sin country_code; no puede enrutar su mint por pais |
| [23](#f23) | mint_code routing & los 31 hardcodes CDP-ES- | Identidad de entidad, geo & cross-border | costura #1 / RIESGO 31 CDP-ES- | CERRABLE | 31 conectores hornean el literal CDP-ES- en vez de delegar en mint_code |
| [24](#f24) | Identidad canonical_key: transliteracion & estabilidad cross-border | Identidad de entidad, geo & cross-border | B5 / B8 / MP6 / MP8 | OPEN (identidad/transliteracion) | _normalize hace ascii-ignore -> descarta no-ASCII (CJK/sz) |
| [25](#f25) | Resolutor de provincia/region para el segmento {prov} del cdp_code | Identidad de entidad, geo & cross-border | B9 / MP7 | CERRABLE (cross-ref Geo) | no hay resolutor zip->region; una coincidencia INE hace de resolutor |
| [26](#f26) | Parametrizacion de market/tenant de gateways pan-EU (OEM) | Identidad de entidad, geo & cross-border | B8 / MP8 | OPEN (cross-border identidad) | market/tenant clavado a ES en gateways pan-EU por 3 mecanismos |
| [27](#f27) | Normalizacion de recetas runtime Tier-1 (milanuncios -> harness) | Receta como activo & cobertura | B10 / B11 / RIESGO runtime | CERRABLE (higiene) | milanuncios es script suelto fuera del esquema/harness, json.dump a disco |
| [28](#f28) | Pack de moneda & formato numerico de parsing | Moneda & formato numerico | B10 / MP10 | CERRABLE | EUR/price_eur + separadores + PRICE_MAX EUR soldados en 4+ sitios |
| [29](#f29) | Orquestacion del drain, governed-fetch & observabilidad | Transporte por tiers & pacing | observabilidad de drain | CERRABLE | scrape clavado a AS24 + data_root('ES') + bypassa governed_fetch |
| [30](#f30) | Criterio de sellado country-aware & rollback atomico por pais | Verificacion cero-confianza & sello | SH1 / SH5 / SH6 + G1 (complete.py:89) | REWORK-SELLO | el sello no asevera coherencia de pais; country_of_cdp/_CDP_CODE_RE/clobber ES |

> Leyenda de grupos: **Transporte por tiers & pacing** (1,8,9,10,29) · **Identidad de navegador & anti-deteccion** (2,3,4,5,6,7) · **Egress & resiliencia de IP** (11,12,13) · **Pack keystone** (14) · **Receta como activo & cobertura** (15,17,19,20,21,27) · **Verificacion cero-confianza & sello** (16,18,30) · **Identidad de entidad, geo & cross-border** (22,23,24,25,26) · **Moneda & formato numerico** (28).

---

<a id="f1"></a>
### Faceta 01 · Escalera de fetch Tier-0 (retry / backoff / escalado / fail-loud)

> **Grupo:** Transporte por tiers & pacing  ·  **Resuelve:** enabler (consume 4/2/3)  ·  **Estado:** MECANISMO-PURO
>
> **Costura —** Mecanismo-puro country-blind: el arbol verdict/backoff/retry no porta literal ES. La costura es indirecta via lo que consume — classify(block_strings) faceta 4, perfil/locale facetas 2/3. open_session(pack=) [api.py:51] inyecta y el codigo de la escalera no cambia un byte.
>
> **Fix —** Hilar pack por open_session(pack=)->FetchEngine.__init__ para que classify(:215) use pack.block_strings y pick(:93) el locale del pack; assert ENGINE_API_VERSION para que un pack viejo falle ruidoso. La escalera permanece intacta.
>
> **Adversarial —** Soft-block localizado DE/FR/IT/PT >30KB sin marker EN/ES -> Verdict.OK (:219) -> schema.org rancio servido como inventario (FALSE-VERIFIED). Y _MAX_RETRIES per-engine in-memory (:209): sin presupuesto global cross-host, N drains re-ganan el ban agregado en aislamiento.
>
> **Sellado —** Test de exhaustividad (status x Verdict, una rama, CHALLENGE/BANNED nunca devuelve body) + adversarial (bloqueo localizado por locale -> FetchError) + via independiente (soft-block corpus -> fail-loud con la huella quemada). Sello: no body salvo 200^OK^forma-ok.
>
> **Herramienta NEXT-LEVEL —** primp (MIT, EUR0) https://github.com/deedy5/primp [VERIFIED NEXT-LEVEL.md:35,296] — amplia el Tier-0 a formas TLS no-Chrome (JA3/JA4) para route-around antes de Tier-1; se enchufa en _rotate_and_retry(:254).

#### (a) code_hints verificados
- [VERIFIED pipeline/engine/fetch.py:64] `class FetchEngine` — sesion fingerprint-coherente (1 engine = 1 huella = 1 jar, docstring :66-68).
- [VERIFIED fetch.py:46] `_RETRYABLE = {429,500,502,503,504}`; [VERIFIED :48] `_MAX_RETRIES = 4`; [VERIFIED :49] `_BACKOFF_BASE = 2.0` (crece 2,4,8,16 con full-jitter).
- [VERIFIED fetch.py:207] `_fetch_tier0(url,*,headers,allow_escalation)`; [VERIFIED :209] `for attempt in range(_MAX_RETRIES)`.
- [VERIFIED fetch.py:219-245] arbol verdict->accion EXHAUSTIVO: :219 `status==200 and Verdict.OK`->return; :224 NOT_FOUND->raise; :227 CHALLENGE/BANNED->rotacion->escalado opt-in->fail-loud; :240 RETRYABLE->backoff+continue; :244-245 non-retryable non-WAF->raise.
- [VERIFIED fetch.py:254] `_rotate_and_retry` — swap a huella coherente fresca, reintenta UNA vez (None si no hay suerte).
- [VERIFIED fetch.py:375-381] `_backoff` staticmethod; :378 honra Retry-After; :381 `time.sleep(min(delay,30.0)*random.uniform(0.5,1.0))  # full jitter`.
- [VERIFIED pipeline/engine/api.py:37] `ENGINE_API_VERSION = "1.0.0"`; [VERIFIED api.py:51] `open_session(...)` punto de inyeccion.

#### (b) Mecanismo al atomo
La maquina pura URL->bytes-o-fallo. Cada intento: `_polite_wait` (:210) -> `session.get` (:212) -> `ban_detector.classify` (:215) -> rama. La rama OK exige status==200 **Y** `Verdict.OK` (:219): por construccion un 200-interstitial NUNCA se devuelve como contenido. CHALLENGE/BANNED -> `_rotate_and_retry` (1 huella coherente, barato); si la rotacion falla y `allow_tier1_escalation` esta activo (default **False**, :82), handoff a Tier-1; si no, fail-loud nombrando la huella quemada (:236-238). RETRYABLE -> backoff exponencial full-jitter capado a 30s. El escalado es OPT-IN por engine y reversible: los 37 connectors que no lo piden mantienen la semantica Tier-0 fail-loud exacta (docstring :20-26). Coherencia sesion=1-huella=1-jar: `_swap_profile` (:160) re-aplica las cookies Tier-1 minteadas a la sesion fresca (:167).

#### (c) Costura ES->generico + fix exacto
Faceta **MECANISMO-PURO**: el presupuesto de reintentos, la curva de backoff, el arbol verdict y el contrato fail-loud son country-blind y NO portan literal ES. La costura es INDIRECTA: el `verdict` sobre el que ramifica viene de `ban_detector.classify` (faceta 4, firmas ES/EN), la huella que rota (faceta 2) y el locale que presenta (faceta 3) estan soldados a ES. **Fix:** hilar `pack` por `open_session(pack=)` [api.py:51] -> `FetchEngine.__init__`, de modo que el `classify` (:215) use `pack.block_strings` y el `pick` de perfil (:93) use el locale del pack; el codigo de la escalera no cambia un byte. Anadir un assert de `ENGINE_API_VERSION` para que un pack viejo falle ruidoso.

#### (d) Riesgo adversarial concreto
El guard de scope "NUNCA interstitial servido como contenido" depende por entero de que `classify` sea exhaustivo cross-locale: una pagina de bloqueo DE/FR/IT/PT >30KB sin marker EN/ES clasifica `Verdict.OK` en :219 y la escalera devuelve schema.org rancio como inventario (FALSE-VERIFIED silencioso). Segundo hueco real [VERIFIED]: `_MAX_RETRIES` es PER-ENGINE in-memory (:209 loop instance-local); NO hay presupuesto global de reintentos cross-host -> N drains reintentan un host sobrecargado en aislamiento y re-ganan el ban agregado que el governor (faceta 8) existe para evitar. Ruido/no-UE: un host que 200ea una pagina de parking/redirect en el locale objetivo pasa el size-gate; la escalera no tiene check de forma-de-contenido, solo el verdict.

#### (e) Sellado + verificacion multi-via
1. **Exhaustividad**: test table-driven sobre cada par (status x Verdict) asevera que dispara exactamente UNA rama y que CHALLENGE/BANNED jamas retorna body.
2. **Adversarial**: inyectar una pagina de bloqueo localizada >30KB por locale (de/fr/it/pt) y afirmar `FetchError`, no return.
3. **Via independiente**: corpus de soft-block replayado por `_fetch_tier0` con escalado off -> fail-loud con la `key` de la huella quemada en el mensaje. Sello = "no body salvo status==200 ^ Verdict.OK ^ forma-de-contenido OK", probado por fixture, no por confianza.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**primp** (MIT, EUR0) — https://github.com/deedy5/primp [VERIFIED NEXT-LEVEL.md:35,296 lic MIT]. *tls-impersonation-breadth*: la matriz no-Chrome de curl_cffi (Safari/Firefox/Edge/Opera) es estrecha; un WAF que espera forma Safari/Firefox y recibe siempre Chrome tiene via de deteccion. primp (Rust, JA3/JA4+HTTP2, Chrome144-148/Safari/Firefox/Edge/Opera) ensancha la familia TLS coherente con la que la escalera hace route-around ANTES de escalar a Tier-1 (que liga la cookie a la IP y la quema). Se enchufa como impersonate-family alternativa en el paso de rotacion (:254); el pack/host-class decide cuando probar forma no-Chrome. Reduce escaladas Tier-1 (coste + IP-burn). Alternativas: rnet, hrequests.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f2"></a>
### Faceta 02 · Pool de fingerprints coherentes & rotacion sin-repeticion

> **Grupo:** Identidad de navegador & anti-deteccion  ·  **Resuelve:** B1 / MP1  ·  **Estado:** CERRABLE
>
> **Costura —** Accept-Language es-ES soldado como constante de modulo en los 3 factories de header [VERIFIED fingerprints.py:46,65,80]; el pool TLS en si ya es country-blind. open_session(pack=) debe inyectar pack.accept_language; el resto del pool no requiere parametrizacion de pais.
>
> **Fix —** Parametrizar _chrome/_firefox/_safari_headers para tomar accept_language del CountryScrapePack via open_session(pack=) (default 'es-ES,es;q=0.9,en;q=0.8' byte-identico). Nivel superior: sustituir el pool estatico por browserforge keyed por (country,browser,os) generando el perfil coherente entero, y anadir primp como familia de impersonacion no-Chrome en la escalera para no agotar las 4 Chrome.
>
> **Adversarial —** WAF que allow-lista solo Chrome reciente agota las 4 Chrome (146/142/136/131) -> fuerza Tier-1 (IP-bound cookie quemada); homogeneidad chrome_only=True -> correlacion cross-drain; sobre host .de el Accept-Language es-ES anuncia navegador espanol (tell geo/locale); WAF Safari/Firefox-shaped detecta el Chrome-siempre; upgrade de curl_cffi que retire un target rompe el pool (mitigado por test).
>
> **Sellado —** test_fingerprints.py:13-17 cada impersonate in _KNOWN_TARGETS de curl_cffi (fail-loud en upgrade); :20-27 UA-version==impersonate + Sec-Ch-Ua version; :35-36 sin Sec-Ch-Ua en no-Chrome; :48-49 rotate!=burned; :66 agotamiento->None. Multi-via: golden de coexistencia DE/ES + adversarial CreepJS/BrowserScan locale!=pais + echo-server diff Accept-Language emitido vs pack.
>
> **Herramienta NEXT-LEVEL —** browserforge (Apache-2.0, EUR0) https://github.com/daijro/browserforge [VERIFIED NEXT-LEVEL.md:208]; soporte: primp (MIT, EUR0) https://github.com/deedy5/primp [VERIFIED :296]; certificacion CreepJS (MIT) https://github.com/abrahamjuliot/creepjs [VERIFIED :248].

#### (a) Verificacion de code_hints [VERIFIED]
- `FingerprintProfile` frozen dataclass `{key, impersonate, family, user_agent, headers}` [VERIFIED pipeline/engine/fingerprints.py:27-38].
- Tres factories de header con el **invariante de coherencia de familia**: `_chrome_headers` emite `Sec-Ch-Ua`/`Sec-Ch-Ua-Mobile`/`Sec-Ch-Ua-Platform="Windows"` [VERIFIED :41-55]; `_firefox_headers` **NO** emite `Sec-Ch-Ua` (comentario explicito ":59 Firefox does NOT send Sec-Ch-Ua") [VERIFIED :58-71]; `_safari_headers` minimal WebKit [VERIFIED :74-81].
- Plantillas UA `_CHROME`/`_FIREFOX`/`_SAFARI` (Safari pineado `Version/18.0`) [VERIFIED :84-86]; builders `_chrome/_firefox/_safari_profile` [VERIFIED :89-107].
- `_CHROME_POOL` = `(chrome146, chrome142, chrome136, chrome131)` — **exactamente 4 Chrome** ordenados newest-first [VERIFIED :114-119]. `_DIVERSITY_POOL` = `(firefox147, safari260)` reservado para escalacion-on-ban [VERIFIED :120-126].
- `DEFAULT_PROFILE_KEY = "chrome131"` (el legacy single-fingerprint AS24-verificado) [VERIFIED :133]. `get_profile` lanza `KeyError` ante key desconocida (fail-loud) [VERIFIED :136-142].
- `FingerprintPool`: `__init__(chrome_only=True)` -> `_base=_CHROME_POOL`, `_escalation=_DIVERSITY_POOL` [VERIFIED :158-162]; `pick()` = `rng.choice(_base)` [VERIFIED :164-165]; `rotate(burned, already_tried)` anade `burned.key` a `tried`, recorre `_base + _escalation`, devuelve el primero no-probado, **`None` cuando todo esta agotado** (el caller escala a Tier-1) [VERIFIED :167-180].

#### (b) El mecanismo al atomo
Un WAF **allow-LISTA** huellas conocidas-buenas; no las block-lista (docstring :3-8). De ahi la regla dura: **JA3 jamas se randomiza** — un ClientHello TLS que ningun navegador real emite cae fuera de la allow-list y es el camino mas rapido al ban. La coherencia es el producto: `impersonate` (curl_cffi) fija TLS/JA3 + HTTP2 settings; el UA y los client-hints deben venir del **MISMO build**. El guard de mismatch es mecanico: client-hints Chrome solo en familia Chrome (un `Sec-Ch-Ua` sobre un UA Firefox es por si mismo senal de deteccion). `rotate()` materializa el invariante *no-repeat-burned*: tras quemar `chrome146` devuelve `chrome142`, luego `chrome136`, `chrome131`, despues escala a `firefox147`/`safari260`, nunca la huella ya baneada dos veces seguidas; agotado todo -> `None` -> el caller sube a navegador real (Tier-1).

#### (c) Costura ES->generico + fix exacto
La forma TLS es **country-blind por naturaleza** (un JA3 Chrome es identico en ES o DE). La UNICA costura ES dentro de esta faceta es el `Accept-Language` **soldado como constante de modulo** en los 3 factories: `"es-ES,es;q=0.9,en;q=0.8"` [VERIFIED :46], `"es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"` [VERIFIED :65], `"es-ES,es;q=0.9"` [VERIFIED :80]. **Fix exacto:** parametrizar los 3 factories para tomar `accept_language` del `CountryScrapePack` via `open_session(pack=)` (default `"es-ES,es;q=0.9,en;q=0.8"` byte-identico); el pool en si (impersonate targets, familias, rotacion) NO necesita parametrizacion de pais. El salto a nivel-inalcanzable: sustituir el pool mantenido a mano por un **generador** que produzca el perfil entero coherente (headers+navigator+screen+TLS/UA-CH) keyed por `(country, browser, os)`.

#### (d) Riesgo adversarial concreto
- **Upgrade de curl_cffi** retira un target -> pool roto (mitigado por test, ver (e)).
- **WAF allow-lista solo Chrome muy reciente** -> agota las 4 Chrome (146/142/136/131) y fuerza Tier-1 (caro, liga la cookie a la IP y la quema).
- **Homogeneidad Chrome** (`chrome_only=True` por defecto) -> todos los drains presentan Chrome -> correlacion cross-drain trivial.
- **DE/FR/IT/PT:** la forma TLS es correcta, pero el `Accept-Language` es-ES soldado anuncia un **navegador espanol sobre host .de** (tell de geo/locale) — esta es la juntura con la faceta 3 (locale).
- **no-UE/JP:** ademas, un WAF que perfila forma Safari/Firefox y recibe siempre Chrome-shaped tiene una via de deteccion; el `_DIVERSITY_POOL` (2 perfiles) es estrecho.
- **Ruido:** un perfil incoherente (client-hints Chrome sobre UA no-Chrome) seria auto-delator; el invariante de familia lo previene por construccion.

#### (e) Criterio de sellado + verificacion multi-via
Sello = **toda forma presentada es un build real y coherente** y la rotacion jamas devuelve la huella quemada. [VERIFIED tests/test_fingerprints.py]: `:13-17` cada `profile.impersonate in _KNOWN_TARGETS` (de `curl_cffi.requests.impersonate.BrowserTypeLiteral`) -> un upgrade que retire un target **falla ruidoso** en CI; `:20-27` la version del UA == target `impersonate` y `Sec-Ch-Ua` lleva la misma version; `:35-36` **no** hay `Sec-Ch-Ua` en Firefox/Safari; `:48-49` `rotate` devuelve `!= burned`; `:66` agotado todo `rotate` -> `None`. Multi-via: (a) test golden de coexistencia (pack=DE coherente, ES byte-identico); (b) adversarial drive del Tier-1 contra CreepJS/BrowserScan con locale forzado != pais -> el detector marca la incoherencia ANTES del fix y NO despues; (c) via independiente: echo-server local que diffea el `Accept-Language` emitido contra `pack.accept_language` declarado.

#### (f) Herramienta que la eleva a nivel inalcanzable
**browserforge** (Apache-2.0, EUR0) — https://github.com/daijro/browserforge [VERIFIED NEXT-LEVEL.md:208 "fingerprint-coherence-engine"]. Reemplaza `_CHROME_POOL`/`_DIVERSITY_POOL` + el `Accept-Language` soldado por un **generador con red bayesiana** entrenada sobre la distribucion real de trafico, keyed por `(country, browser, os)`: produce un perfil de-DE/fr-FR/ja-JP entero y coherente, no solo el header. Corre 100% CPU (~0.1-0.2 ms/huella), pip-install, Apache-2.0 comercial-limpia. **Soporte directo al riesgo (d) "agota las 4 Chrome":** **primp** (MIT, EUR0) — https://github.com/deedy5/primp [VERIFIED NEXT-LEVEL.md:296 "tls-impersonation-breadth"] amplia el Tier-0 mas alla del pool Chrome de curl_cffi (Safari 18.5/26, Edge/Firefox/Opera recientes con JA3/JA4 + HTTP2 coherentes, nucleo Rust), reduciendo escaladas a Tier-1. **Certificacion:** CreepJS (MIT) — https://github.com/abrahamjuliot/creepjs [VERIFIED NEXT-LEVEL.md:248 "antidetect-validation-harness"] como gate de CI que ata el sello a detectores reales.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f3"></a>
### Faceta 03 · Pack de locale & coherencia con geo de egress

> **Grupo:** Identidad de navegador & anti-deteccion  ·  **Resuelve:** B1 / MP1 / MP2 / SH1  ·  **Estado:** CERRABLE (egress PARCIAL)
>
> **Costura —** Accept-Language 'es-ES' soldado como constante de modulo en los 3 factories de header [VERIFIED fingerprints.py:46/65/80]; Tier-1 camoufox SIN locale ni geoip [VERIFIED browser.py:189, AsyncCamoufox(headless,proxy,humanize) sin locale/geoip]; milanuncios locale='es-ES' geoip=False soldado [VERIFIED milanuncios_camoufox.py:5]; NO existe assert locale<->egress.
>
> **Fix —** Inyectar pack.accept_language en los 3 factories (default literal ES por familia -> golden byte-identico) y pack.locale + geoip=True en _solve_camoufox (browser.py:189); anadir assert de sello locale_lang(presented)==pack.country_lang AND egress_country(ip)==pack.proxy_country antes de VERIFIED.
>
> **Adversarial —** Navegador es-ES sobre host .de/.fr/.it/.pt -> geo-redirect a vista ES que parsea limpio y se sella FALSO (vista equivocada como inventario DE), o soft-block; geoip=False impide alinear timezone/WebRTC aun con proxy correcto; cada fetch no-ES delata un navegador espanol correlacionable; territorios multi-idioma (BE/CH) exigen multi-locale por host.
>
> **Sellado —** VERIFIED requiere coherencia locale<->IP: (a) golden pack=DE con los 4 headers de-DE coherentes + ES byte-identico; (b) adversarial Tier-1 vs CreepJS/BrowserScan con locale!=pais marca incoherencia antes y no despues; (c) echo-server httpbin local diffea Accept-Language emitido vs pack.accept_language declarado.
>
> **Herramienta NEXT-LEVEL —** browserforge (Apache-2.0, EUR0) https://github.com/daijro/browserforge [VERIFIED NEXT-LEVEL.md:208] — generador bayesiano de huellas country-coherentes keyed (country,browser,os), perfil entero coherente, ~0.1-0.2ms CPU; + camoufox geoip-coherence (locale/timezone/geo desde region del proxy) [VERIFIED NEXT-LEVEL.md:209] para el eje locale<->IP del Tier-1.

#### (a) code_hints [VERIFIED]
- [VERIFIED fingerprints.py:46] `_chrome_headers` cablea `Accept-Language: 'es-ES,es;q=0.9,en;q=0.8'` como literal de funcion.
- [VERIFIED fingerprints.py:65] `_firefox_headers` cablea `Accept-Language: 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'`.
- [VERIFIED fingerprints.py:80] `_safari_headers` cablea `Accept-Language: 'es-ES,es;q=0.9'`.
- [VERIFIED browser.py:179] firma `async def _solve_camoufox(...)`; PERO el call real [VERIFIED browser.py:189] es `AsyncCamoufox(headless=headless, proxy=proxy_cfg, humanize=True)` — NO pasa `locale=` NI `geoip=`. El code_hint '(locale/geoip)' es OPTIMISTA: el Tier-1 generico no fija locale alguno -> hereda el del sistema/Camoufox default. Estado real PEOR que es-ES soldado: locale INDEFINIDO, no-determinista por host.
- [VERIFIED milanuncios_camoufox.py:5] `AsyncCamoufox(headless=True, os='windows', locale='es-ES', geoip=False, humanize=True)`: locale ES soldado Y geoip=False (la coherencia geo por IP esta DESACTIVADA).
- [VERIFIED por lectura del fetch/browser path] NO existe en ninguna parte un assert `locale_presentado == pais_egress`. La fuga CRITICAL #1 de ambos verdicts no tiene guard.

#### (b) Mecanismo al atomo
Tres factories de header (Chrome/FF/Safari) son la fuente de verdad del Accept-Language de Tier-0 (curl_cffi): cada `FingerprintProfile.headers` se mergea en CADA request. El valor es una constante de modulo, no un parametro de sesion. En Tier-1, camoufox es el navegador REAL que mina la cookie de clearance; con `geoip=True` Camoufox deriva timezone/locale/WebRTC/geo desde la IP del proxy (coherencia automatica de extremo a extremo). El path generico (browser.py:189) ni siquiera setea locale, y el de milanuncios fuerza es-ES con geoip=False. Resultado atomico: el locale anunciado (HTTP Accept-Language + navigator.language) y el pais de la IP de egress son DOS ejes que ningun codigo concilia; la coherencia que protege ES es accidente del monocultivo, no invariante.

#### (c) Costura ES->generico + fix exacto
El valor debe nacer de `CountryScrapePack.accept_language` (default 'es-ES,es;q=0.9,en;q=0.8' byte-identico). Fix en tres puntos:
1. fingerprints.py:46/65/80 — los 3 factories reciben `accept_language: str` inyectado por `open_session(pack=)` via el FingerprintPool; el default conserva el literal ES EXACTO de cada familia -> golden byte-identico ES.
2. browser.py:189 — `_solve_camoufox` acepta `locale` y `geoip=True` desde el pack y los pasa a AsyncCamoufox: el Tier-1 anuncia el locale del pais Y deriva geo coherente del proxy.
3. Nuevo ASSERT de sello (cierra el sealing-hole): `assert locale_lang(presented) == pack.country_lang AND egress_country(ip) == pack.proxy_country` ANTES de marcar VERIFIED.

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/JP/ruido)
Un navegador es-ES golpeando host .de/.fr/.it/.pt es un tell de geo/locale. El sitio puede: (1) servir contenido en español, (2) soft-block, o (3) geo-redirect a una vista ES que parsea LIMPIO y se sella FALSO — la vista equivocada certificada como inventario DE. Cada fetch no-ES anuncia un navegador español = firma correlacionable entre drains. `geoip=False` de milanuncios significa que aun con proxy residencial correcto el browser no alinea timezone/WebRTC -> incoherencia detectable por DataDome/PerimeterX. Ruido: un pais cuyo idioma comparte territorio (BE fr/nl, CH de/fr/it) exige multi-locale por host, no un escalar por pais.

#### (e) Sellado + verificacion multi-via
Criterio: VERIFIED EXIGE coherencia locale<->IP, no solo fetched==parsed.
- (a) test golden: pack=DE -> los 4 headers (Accept-Language, Sec-CH-UA, UA, platform) son de-DE coherentes y ES sigue byte-identico (patron test_country_coexistence).
- (b) adversarial: dirigir el Tier-1 contra CreepJS/BrowserScan con locale FORZADO != pais y comprobar que el detector marca la incoherencia ANTES del fix y NO la marca despues.
- (c) via independiente: echo-server (httpbin local) que captura el Accept-Language EMITIDO y se diffea contra `pack.accept_language` declarado — la huella emitida debe coincidir con el dato del pack, no con un literal del engine.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
[VERIFIED NEXT-LEVEL.md:208] `browserforge` (Apache-2.0, EUR0) — https://github.com/daijro/browserforge. Reemplaza `_CHROME_POOL`/`_DIVERSITY_POOL` mantenidos a mano y el Accept-Language soldado por un GENERADOR bayesiano de huellas country-coherentes keyed por (country, browser, os): produce header set + navigator + screen + TLS/UA-CH mutuamente consistentes de-DE/fr-FR/ja-JP ENTEROS, no solo el header. ~0.1-0.2 ms/huella, 100% CPU, sin red, sin modelo pesado; el FingerprintPool pasa de lista estatica a wrapper sobre browserforge.HeaderGenerator/FingerprintGenerator parametrizado por pack. Complemento [VERIFIED NEXT-LEVEL.md:209]: camoufox geoip-coherence (calcula locale/timezone/geo desde la region del proxy) sella el eje locale<->IP del Tier-1. Es la mejora 'fingerprint-coherence-engine' que mata el es-ES soldado.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f4"></a>
### Faceta 04 · Clasificador semantico de bloqueo & gobierno de firmas WAF

> **Grupo:** Identidad de navegador & anti-deteccion  ·  **Resuelve:** B6 / MP3 / SH4  ·  **Estado:** CERRABLE
>
> **Costura —** Prosa de interstitial ES hardcoded en `_STRONG_BLOCK_MARKERS` (ban_detector.py:64-73) + size-gate magico 30000 (:111); cero dimension de locale. El mobiliario WAF estructural (cf-chl-/_abck/datadome/_px) ya es country-blind.
>
> **Fix —** Subir los marcadores a `CountryScrapePack.block_strings{challenge,ban,strong}` keyed por locale; mergear pack sobre la base country-blind (la fontaneria WAF queda universal) en `open_session(pack=)`; pack ES por defecto == tuplas de hoy byte-identico; hacer el size-gate 30000 tunable por pack.
>
> **Adversarial —** Muro localizado >30KB DataDome/PerimeterX (FR/DE/IT/PT/JP) sin el EN 'pardon our interruption' -> classify()->OK (ban_detector.py:118) -> schema.org rancio sellado como inventario; lista estatica => rotacion de interstitial del vendor re-clasifica CHALLENGE->OK en silencio; paginas terse <30KB con marcador incidental -> falso BANNED.
>
> **Sellado —** Corpus golden por locale (cada pagina->Verdict exacto, ES byte-identico) + adversarial bloque-localizado->!=OK (cruzado con fill-rate Pandera) + eje independiente MinHash que flaggea rotacion de interstitial; clasificador ⊥ VAM.
>
> **Herramienta NEXT-LEVEL —** datasketch MinHash/LSH (MIT, https://github.com/ekzhu/datasketch) [VERIFIED NEXT-LEVEL.md:232] — disparador de drift para interstitials rotados/localizados; companero contrato Pandera fill-rate (NEXT-LEVEL.md:233); CreepJS (MIT, https://github.com/abrahamjuliot/creepjs, NEXT-LEVEL.md:248) para certificar la huella outbound.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/engine/ban_detector.py:26` `class Verdict(enum.Enum)` -> OK/CHALLENGE/BANNED/NOT_FOUND [VERIFIED].
- `:34` `_CHALLENGE_MARKERS` tupla (CF `just a moment`/`cf-chl-`/`__cf_chl`/`turnstile`, DataDome `datadome`/`geo.captcha-delivery.com`/`dd_cookie`, Akamai `_abck`/`ak_bmsc`/`bm-verify`, PerimeterX `px-captcha`/`_px`/`perimeterx`, generic `unusual traffic`) [VERIFIED].
- `:51` `_CHALLENGE_HEADERS` (`cf-mitigated`,`cf-chl-bypass`,`x-datadome`,`server-timing`) [VERIFIED].
- `:56` `_BAN_MARKERS` (`access denied`,`you have been blocked`,`rate limited`,`too many requests`,...) [VERIFIED].
- `:64` `_STRONG_BLOCK_MARKERS` size-independent; ES soldado `:66 'algo se detuvo'`, `:67 'para continuar, completa el captcha'`; CJK `:71 '请开启javascript'`; `attention required! | cloudflare` [VERIFIED].
- `:80` `classify(status, body, headers)`; `:85` 404/410->NOT_FOUND; `:90` strong-markers->CHALLENGE (precede a todo); `:94` header `cf-mitigated==challenge`; `:98` ramas 401/403/429/503; `:106` rama status==200; `:111` `small = len(body_l) < 30000` size-gate [VERIFIED]; `:127` `is_blocked` helper [VERIFIED].

#### (b) El mecanismo al atomo
`classify` es un arbol de 4 brazos con sesgo conservador (ante duda -> CHALLENGE, jamas OK):
1. **NOT_FOUND duro** primero (404/410): un recurso ido no se escala.
2. **STRONG markers size-independent** ANTES que nada (`:90`): un PerimeterX `Pardon Our Interruption` a 100KB sigue siendo muro; no hay size-gate para esta clase.
3. **Header `cf-mitigated:challenge`** (`:94`): Cloudflare se autodelata por header sin importar el codigo.
4. **Por status**: codigos WAF 401/403/429/503 desambiguados por body (BAN_MARKERS ∧ ¬CHALLENGE_MARKERS -> BANNED; CHALLENGE_MARKERS ∨ body<1500 -> CHALLENGE; resto BANNED). status==200 solo marca cuando `small(<30KB)` ∧ markers (evita falso-positivo en un listing real que solo menciona `ray id`). Fallback 2xx/3xx -> OK; desconocido -> BANNED.

Es EL guardian entre `Verdict.OK` y el harness sellando una pagina como inventario: la unica compuerta que decide "esto es coche real vs pagina de bloqueo estilizada".

#### (c) Costura ES->generico
Las tablas de marcadores son **tuplas globales estaticas** compiladas en el modulo; las cadenas ES (`algo se detuvo`, `para continuar, completa el captcha`) viven HARDCODED dentro de `_STRONG_BLOCK_MARKERS` a nivel de modulo, sin dimension de locale. El `30000` es un numero magico. La fontaneria estructural (`cf-chl-`, `_abck`, `datadome`, `_px`) es **country-blind** (mobiliario WAF neutro al idioma); solo la prosa visible del interstitial varia por locale.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT**: pagina de bloqueo localizada >30KB sin marcador EN -> `classify`==OK (`:118`) -> schema.org rancio sellado como inventario. Ej: DataDome `Bitte warten`/`Veuillez patienter` a 200 >30KB; PerimeterX `Zugriff verweigert` sin `pardon our interruption`.
- **Drift**: lista estatica; un vendor rota el HTML del interstitial y un CHALLENGE conocido pasa a OK en silencio (cero telemetria).
- **no-UE/ruido**: muro Incapsula en japones (中古車 dealer) sin el byte CJK exacto -> OK. Umbral 1500/30000 dimensionado a listings EN: un mercado de paginas terse <30KB con marcador incidental -> falso BANNED (sobre-bloqueo que mata cosecha).

#### (e) Sellado + verificacion multi-via
**Criterio**: `classify` NUNCA devuelve OK para un interstitial conocido en CUALQUIER locale del pack, y no sobre-bloquea inventario real. **Multi-via**: (1) **golden por locale** — fixtures de paginas reales CHALLENGE/BANNED/NOT_FOUND/OK (de/fr/it/pt/es/ja) cada una asertando el Verdict exacto, corpus ES byte-identico; (2) **adversarial** — inyectar bloqueo localizado >30KB con schema.org rancio y asertar `classify != OK` Y que el contrato de fill-rate del harness lo marque; (3) **eje independiente** — telemetria de drift por MinHash: firma de la pagina servida vs firmas selladas de los clusters de bloqueo; una rotacion de interstitial aflora como colapso de Jaccard aunque ningun string estatico case. Clasificador ⊥ VAM(cuenta): pagina sana pasa ambos, bloqueo localizado dispara al menos uno.

#### (f) Herramienta NEXT-LEVEL (eleva a inalcanzable)
**datasketch (MinHash/MinHashLSH)** — MIT — https://github.com/ekzhu/datasketch [VERIFIED NEXT-LEVEL.md:232]. La mejora `self-healing recipe-rot · DRIFT DETECTION` (NEXT-LEVEL.md:229-235): MinHash/LSH de la firma estructural de cada pagina vs la firma sellada; caida de Jaccard > umbral = la fuente/interstitial muto, disparando la senal que la tupla estatica no tiene. Convierte el `adversarial_risk` exacto de la faceta ("firmas WAF estaticas + cero telemetria de drift") en un disparador continuo, CPU puro, €0. Companero: contrato Pandera de fill-rate sobre el sample (NEXT-LEVEL.md:233) para el caso "parsea pero es bloque rancio". Complemento OUTBOUND (certificar que NUESTRA huella Tier-1 no es lo bloqueado): CreepJS (MIT, NEXT-LEVEL.md:248).

[↑ Indice de facetas](#indice-facetas)

---

<a id="f5"></a>
### Faceta 05 · Solve Tier-1 en navegador real (challenge + mint de cookie)

> **Grupo:** Identidad de navegador & anti-deteccion  ·  **Resuelve:** B2 / licencia(6)  ·  **Estado:** PARCIAL (proxy OPEN/GASTO)
>
> **Costura —** El solve es country-blind salvo el proxy residencial etiquetado 'ES' en PENDING_CREDENTIAL_PROXY [VERIFIED tier1/browser.py:62-63] y el locale/geoip del navegador que hoy fija el caller (faceta 3). El mecanismo recibe url+proxy por parametro [VERIFIED :67]; falta cablear locale/geoip desde CountryScrapePack.
>
> **Fix —** Anadir parametros locale/geoip a solve_challenge() y _solve_camoufox() inyectados por el pack (camoufox geoip-coherence deriva timezone/locale de la region del proxy); sustituir el proxy 'ES sticky' [VERIFIED :62-63] por pack.proxy_country; elegir engine por pack.defense_tier (patchright Chrome-shape / camoufox Firefox-shape). Default ES byte-identico cuando pack.country=='ES'.
>
> **Adversarial —** WAF Chrome-shaped (Kasada/Shape-F5) rechaza la forma Firefox de camoufox al instante; DataDome/HUMAN delatan headless [VERIFIED :151-152]; cookie ligada a la IP host efimera [VERIFIED :7-8] se quema en reuso; pais sin proxy de su geo solvea sobre IP-host ES -> cookie incoherente con el egress DE/FR/JP del pais objetivo -> invalidacion al primer reuso.
>
> **Sellado —** VERIFIED sii classify(html)==Verdict.OK (no interstitial) AND cookies+UA no vacios AND reuso curl_cffi (UA+cookie+misma IP) da OK en >=1 fetch. Multi-via: (1) gate antidetect exige trust>=piso; (2) mismo challenge SIN parches debe bloquearse y CON parches minar cookie; (3) echo-server externo confirma JA3/UA/Accept-Language emitidos == pack declarado.
>
> **Herramienta NEXT-LEVEL —** patchright-python (Apache-2.0, EUR0) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python [VERIFIED NEXT-LEVEL.md:256] -- Tier-1 Chromium stealth por defecto para WAFs Chrome-shaped, retira el riesgo AGPL de nodriver; eleccion patchright/camoufox por pack.defense_tier. Co-palanca de sellado: CreepJS (MIT, EUR0) https://github.com/abrahamjuliot/creepjs [VERIFIED NEXT-LEVEL.md:248] -- gate de CI que certifica la huella contra detectores reales.

#### (a)+(b) Mecanismo VERIFICADO al átomo
- Entry síncrono `solve_challenge(url, *, engine="camoufox", proxy=None, timeout=60, wait_after_load=7, headless=False)` [VERIFIED pipeline/engine/tier1/browser.py:67]. Default `engine="camoufox"` (MPL-2.0, file-level copyleft, seguro dentro de un servicio de red) [VERIFIED :12,:27-31].
- Guard de engine fail-loud: `if engine not in ("nodriver","camoufox"): raise Tier1Error` [VERIFIED :79-80].
- Display virtual: `with virtual_display(headful=not headless):` envuelve el solve [VERIFIED :86]. `should_use_virtual_display` es puro y devuelve True SOLO en Linux + headful + sin DISPLAY exportado + Xvfb/pyvirtualdisplay disponible [VERIFIED tier1/display.py:41-60]; no-op en Windows/macOS [VERIFIED display.py:54-55,:71-73]. Fallback: pyvirtualdisplay si está, si no subprocess `Xvfb :N -screen 0 1920x1080x24 -nolisten tcp` [VERIFIED display.py:90-93], restaura el DISPLAY previo al salir [VERIFIED display.py:101-104].
- Loop asyncio gestionado a mano (`_run_coro`) con grace-tick 0.25s y silencio de ResourceWarning [VERIFIED :96-119] — workaround del ProactorEventLoop de Windows que cierra el loop con pipes de subprocess vivas.
- Routing `_solve_async` → camoufox (default) | nodriver [VERIFIED :122-129].
- camoufox: `AsyncCamoufox(headless=headless, proxy=proxy_cfg, humanize=True)` [VERIFIED :189] (humanize=True = cursor/scroll humanization, postura más agresiva contra DataDome/PerimeterX [VERIFIED :187-188]); `goto(url, wait_until="domcontentloaded")` + `sleep(wait_after_load)` [VERIFIED :191-192]; captura `navigator.userAgent` [VERIFIED :194] y `page.context.cookies()` → dict name→value [VERIFIED :195-196]; devuelve `BrowserResult(html, cookies, user_agent, final_url, engine, raw_cookies)` [VERIFIED :48-56,:197-199].
- nodriver (OPT-IN, AGPL-3.0): import lazy `import nodriver as uc` para que importar el engine NUNCA traiga AGPL salvo solve explícito [VERIFIED :134-137]; humanización scroll/dwell `scrollTo(0, scrollHeight/3)`→0.6s→`scrollTo(0,0)`→0.4s [VERIFIED :153-159]; normaliza cookies a (dict, raw) [VERIFIED :202-218].
- INVARIANTE DE REUSO codificado en el contrato del dataclass: "Pin `cookies` + `user_agent` together on reuse" [VERIFIED :50]; devuelve el UA EXACTO que el browser presentó para pinearlo con la cookie (mismo UA+JA3+IP, o el WAF la invalida al primer reuso) [VERIFIED :6-10].
- Fail-loud total: cualquier excepción se normaliza a `Tier1Error` [VERIFIED :44-45,:90-93]; NUNCA devuelve una página-challenge enmascarada como contenido [VERIFIED :73-75].
- proxy PENDING-CREDENTIAL: residential ES sticky no provisionado; corre sobre IP del host por ahora, coste cero [VERIFIED :33-36,:61-64].

#### (b) Costura ES→genérico (fix exacto)
La única atadura ES de este módulo es el proxy residencial sticky etiquetado "ES" en PENDING_CREDENTIAL_PROXY [VERIFIED :62-63 "residential ES sticky proxy"]. El mecanismo de solve es country-blind (recibe `url`+`proxy` por parámetro). La costura real es el LOCALE/GEOIP del navegador (hoy lo fija el caller/receta, faceta 3) y el proxy de SU geo (faceta 11/12). Fix: añadir `locale`/`geoip` como parámetros que el CountryScrapePack inyecta — camoufox soporta geoip-coherence (deriva timezone/locale de la región del proxy) — y sustituir el "ES sticky" por `pack.proxy_country`. Default ES byte-idéntico cuando `pack.country=="ES"`. El engine por defecto pasa a elegirse por `pack.defense_tier` (Chrome-shape vs Firefox-shape).

#### (c) Riesgo adversarial concreto
- **Forma de navegador**: camoufox es Firefox-shaped; un WAF que allow-liste SOLO forma Chrome reciente (Kasada/Shape-F5/parte de DataDome) rechaza la forma Firefox al instante — y hoy NO hay Chromium-stealth Apache por defecto [VERIFIED adversarial_risk facet].
- **Headless flag**: DataDome/HUMAN delatan headless al instante [VERIFIED :151-152 doc nodriver]; sin Xvfb en un VPS sin monitor, un headful falla — de ahí display.py.
- **Cookie IP-bound**: la clearance se liga a la IP que la minó [VERIFIED :7-8]; sobre IP-host efímera o datacenter se quema masivamente en el reuso (faceta 7).
- **No-UE / DE/FR/JP**: un país sin proxy residencial de SU geo solvea sobre IP-host española → la cookie es coherente con ES, no con el egress del país objetivo → el reuso desde la geo correcta la invalida.

#### (d) Sellado + verificación multi-vía
- **Sello**: un solve es VERIFIED sii (1) `ban_detector.classify(html)` == Verdict.OK (no interstitial), (2) cookies no vacías + UA no vacío, (3) el reuso vía curl_cffi con (UA+cookie+misma IP) produce Verdict.OK en ≥1 fetch posterior (faceta 7).
- **Vía 1 (test)**: gate antidetect que dirige el browser contra un detector real y exige trust-score ≥ piso.
- **Vía 2 (adversarial)**: resolver el MISMO challenge con el browser SIN parches (playwright vanilla / nodriver crudo) debe ser BLOQUEADO y CON parches debe minar la cookie — prueba que el detector funciona y que el parche aporta.
- **Vía 3 (independiente)**: capturar el request real en un echo-server externo (tls.peet.ws / httpbin local) y diffear JA3/UA/Accept-Language emitidos vs los declarados por el pack — la huella emitida == dato del pack, no un literal del engine.

#### (e) Herramienta NEXT-LEVEL (eleva a nivel inalcanzable)
- **patchright-python (Apache-2.0, €0)** — https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python [VERIFIED NEXT-LEVEL.md:256]. Drop-in de Playwright que cierra leaks Runtime.enable/Console.enable, `--disable-blink-features=AutomationControlled` y closed shadow roots; stealth Chrome-shaped que pasa Cloudflare/Kasada/Akamai/Shape-F5/DataDome. Lo inalcanzable: promueve un Tier-1 Chromium Apache-2.0 por DEFECTO para WAFs Chrome-shaped (cierra el gap de la forma Firefox de camoufox) Y retira el riesgo AGPL de nodriver; la elección patchright(Chrome)/camoufox(Firefox) se decide por `defense_tier/source_group` del pack. El propio diseño lo nombra como upgrade staged [VERIFIED tier1/browser.py:28-31].
- **CreepJS (MIT, €0)** — https://github.com/abrahamjuliot/creepjs [VERIFIED NEXT-LEVEL.md:248]. El ORÁCULO de validación: gate de CI que dirige el Tier-1 contra 21 tests de fingerprint + lie-detector + trust-score y FALLA el sello de receta Tier-1 si el trust cae bajo umbral. Convierte la anti-detección de [ASSUMED] a [VERIFIED multi-vía]; auto-hosteable desde su fuente.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f6"></a>
### Faceta 06 · Gobierno de licencia de engines Tier-1 (AGPL / MPL / Apache)

> **Grupo:** Identidad de navegador & anti-deteccion  ·  **Resuelve:** RIESGO AGPL nodriver  ·  **Estado:** CERRABLE (mejora #3)
>
> **Costura —** Garantia de licencia hoy auditada solo sobre el arbol ES (countries/ES/_tier1/, 14 dirs [VERIFIED]) y los connectors actuales; la ley de licencias es country-blind pero el ALCANCE del sello no lo es. El default permisivo vive en dos puntos ES-agnosticos ya correctos (fetch.py:57 _TIER1_ENGINE='camoufox', browser.py:67 solve_challenge engine='camoufox'); la costura es que el invariante 'cero AGPL en ruta servida' debe extenderse a countries/*/_tier1/ y a todo connector de cualquier pais, no solo ES.
>
> **Fix —** 1) Mantener default camoufox en ambos puntos (ya VERIFIED). 2) Anadir guard de CI que matchee CABLEADO (import nodriver / engine="nodriver" / tier1_engine="nodriver") sobre countries/*/_tier1/*/recipe.yaml + todos los connectors, con allowlist explicita para los 2 comentarios-prosa (motorflash_wholesale.py:430, coches_com_wholesale.py:891 [VERIFIED]) y fallo del build ante cableado AGPL fuera de la caja opt-in. 3) Parametrizar test_engine_license_default.py por pais (glob countries/*/_tier1/). 4) Stagear patchright (Apache-2.0) como default Chrome-shaped para retirar nodriver del default por completo.
>
> **Adversarial —** Una receta countries/DE/_tier1/ que declare engine: nodriver (WAF DE Chrome-shaped tumba camoufox-Firefox) cablea AGPL en la ruta servida sin que el test ES lo detecte. Ruido VERIFIED: grep nodriver da 44 ficheros pero 2 son comentarios (no imports) — un guard que matchee el token desnudo falla el build por prosa. En P14 (API publica) AGPL-3.0 puede forzar divulgacion de fuente del derivado servido: riesgo existencial si cualquier countries/<CC>/ cablea nodriver para entonces.
>
> **Sellado —** Multi-via: (1) los 4 unit tests de test_engine_license_default.py verdes + extension parametrica por countries/*/_tier1/ exigiendo engine ∈ {camoufox,patchright}; (2) auditoria de grafo pip-licenses/scancode = 0 paquetes AGPL en la ruta del API publico (mecanismo ortogonal al unit test); (3) grep-guard de cableado con allowlist para los 2 comentarios-prosa. Sellado = 3 vias verdes + patchright staged como default Chrome-shaped.
>
> **Herramienta NEXT-LEVEL —** patchright-python (Apache-2.0) — https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python — [VERIFIED en NEXT-LEVEL.md:253-259, lic Apache-2.0 :256]. Stealth Chrome-shaped que retira nodriver(AGPL) del default y cuya verificacion (scancode/pip-licenses, 0 AGPL en grafo del API publico) ES el sello de esta faceta. Complemento: CreepJS/antidetect-validation-harness (MIT, NEXT-LEVEL.md:245-251) certifica el swap antes de sellar.

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/engine/tier1/browser.py:12-31`** [VERIFIED]: el docstring de modulo declara el orden legal: `ENGINES (default is camoufox; nodriver is opt-in only — see the license box)`. La **caja de licencia** vive en `:19-26` (un recuadro ASCII) con el texto literal `LICENSE WARNING — nodriver is AGPL-3.0 (network copyleft)` y `set engine="camoufox" to avoid AGPL`. Camoufox se describe en `:27-31` como `DEFAULT / primary ... (MPL-2.0, file-level copyleft — safe inside a network service)` y nombra **Patchright — Apache-2.0** como el `staged upgrade`.
- **`browser.py:67-69`** [VERIFIED]: `def solve_challenge(url, *, engine: str = "camoufox", ...)` — el **default a nivel de funcion** es camoufox. El guard `:79-80` `if engine not in ("nodriver","camoufox"): raise Tier1Error` cierra el set de engines permitidos.
- **`browser.py:122-129`** [VERIFIED]: `_solve_async` enruta `if engine == "nodriver": _solve_nodriver` else camoufox. El **import AGPL es perezoso**: `:134-137` dentro de `_solve_nodriver`, comentado `AGPL-3.0 dependency — imported lazily so importing pipeline.engine never pulls AGPL code unless a Tier-1 solve is actually requested`, `import nodriver as uc`. **Atomo clave:** importar `pipeline.engine` NUNCA arrastra AGPL; solo un solve nodriver explicito lo carga.
- **`fetch.py:53-57`** [VERIFIED]: constante de modulo `_TIER1_ENGINE = "camoufox"` precedida del comentario `Default Tier-1 engine = camoufox (MPL-2.0...). nodriver/zendriver are AGPL-3.0 (network copyleft): defaulting to them would risk forcing source disclosure once CARDEEP exposes its public API (P03-S3 / P14)`.
- **`countries/ES/_tier1/`** [VERIFIED por `ls`]: contiene **exactamente 14 directorios** de receta (`CDP-ES-00-3N995HG6` ... `CDP-ES-00-ZXZD056M`), cada uno con `recipe.yaml`. Son las 14 recetas Tier-1 a auditar antes de exponer el API.
- **SELLO YA EXISTENTE `tests/test_engine_license_default.py`** [VERIFIED]: 4 tests unitarios puros (sin red): `:21` `test_default_tier1_engine_constant_is_permissive` (asserta `_TIER1_ENGINE not in {"nodriver","zendriver"}`), `:28` `test_default_tier1_chain_runs_no_agpl_engine` (construye `FetchEngine(...)` y asserta `not (_AGPL_ENGINES & set(eng._tier1_engines))`), `:35` `test_nodriver_still_available_as_explicit_optin` (con `tier1_engine="nodriver"` SI aparece), `:42` `test_solve_challenge_default_engine_is_permissive` (inspecciona la firma y exige `default == "camoufox"`).

#### (b) El mecanismo al atomo
La faceta no produce bytes: produce una **garantia legal demostrable** sobre la superficie de red. El mecanismo tiene tres capas:
1. **Default permisivo en DOS puntos** (defensa en profundidad): la constante de motor `fetch.py:57` y el default de parametro `browser.py:67`. Un caller que omite `engine=` cae en camoufox por AMBAS vias. El footgun clasico (un default de funcion distinto de la constante de config) esta cerrado por el test `:42`.
2. **Aislamiento de la dependencia AGPL por import perezoso** (`browser.py:136-137`): el grafo de import de `pipeline.engine` es AGPL-free; nodriver solo entra en memoria si el owner pide `engine="nodriver"` explicito. Esto convierte "no usamos AGPL por defecto" en una propiedad del **grafo de dependencias**, no de la documentacion.
3. **La caja de licencia como decision elevada** (`browser.py:19-26`): el copyleft de red de AGPL-3.0 se modela como una decision LEGAL DEL OWNER, surfaced on purpose and not hidden. nodriver no se borra (es el unico tool con cero-bloqueos en el benchmark de 651 verdicts citado `:16-18`) — se pone tras una puerta consciente.

#### (c) La costura ES->generico
Esta faceta es **casi country-blind**: la ley de licencias no cambia entre ES/DE/FR. Pero la costura existe y es real: **el sello hoy audita un solo arbol** (`countries/ES/_tier1/`, 14 dirs) y un solo grafo de connectors. Cuando entra el pais #2, sus recetas `_tier1` (igual que las 14 de ES) y sus connectors nativos pueden cablear nodriver y reintroducir el riesgo AGPL en una ruta servida. La garantia debe viajar como INVARIANTE country-proof: el guard debe glob `countries/*/_tier1/` y TODOS los connectors de cualquier pais, no solo ES.

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **Fuga por receta de pais nuevo:** una receta `countries/DE/_tier1/CDP-DE-.../recipe.yaml` que declare `engine: nodriver` (porque un WAF DE Chrome-shaped tumba camoufox-Firefox) cablea AGPL en la ruta servida sin que el test ES lo vea.
- **Falso-positivo de grep (ruido VERIFIED):** `grep nodriver` sobre el repo arroja **44 ficheros**, pero dos de ellos son **comentarios en prosa, NO imports**: `pipeline/platform/motorflash_wholesale.py:430` (`Local headful browser (camoufox/nodriver) — €0`) y `pipeline/platform/coches_com_wholesale.py:891` (`camoufox/nodriver homepage warm-up`) [VERIFIED por grep -C2]. Un guard ingenuo que matchee el token desnudo `nodriver` FALLARIA el build por estos comentarios; el guard correcto debe matchear el **cableado** (`import nodriver`, `engine="nodriver"`, `tier1_engine="nodriver"`) y excluir prosa/docstrings.
- **No-UE / exposicion de API publica:** P14 (API publica) es el momento en que AGPL-3.0 muerde — un derivado servido por red puede forzar divulgacion de fuente. Si para entonces cualquier `countries/<CC>/` cablea nodriver en la ruta servida, el riesgo es existencial (lo marca el propio test docstring `:3-7`).

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (test unitario, ya verde):** los 4 tests de `test_engine_license_default.py` pasan. **Extension generica:** parametrizar un test que, para CADA `countries/*/_tier1/*/recipe.yaml`, asserte `engine ∈ {camoufox, patchright}` salvo opt-in marcado.
- **Via 2 (auditoria mecanica de grafo, mecanismo distinto):** `pip-licenses`/`scancode` sobre el grafo de dependencias de la **ruta del API publico** asserta **0 paquetes AGPL/network-copyleft**. Esta via no mira el codigo Python sino el arbol de paquetes instalados — ortogonal al unit test.
- **Via 3 (grep-guard de cableado):** CI falla si `import nodriver`/`engine="nodriver"` aparece FUERA de la caja opt-in, con allowlist explicita para los 2 comentarios prosa de wholesale. Sellado = las 3 vias verdes Y patchright staged como default Chrome-shaped (retira la tentacion de nodriver de raiz).

#### (f) Herramienta NEXT-LEVEL que lo eleva a nivel inalcanzable
**patchright-python** (Apache-2.0) — el match perfecto: cierra el riesgo legal Y mejora la cobertura. NEXT-LEVEL.md:253-259 [VERIFIED] lo define como `stealth Chrome-shaped Apache-2.0 por defecto, retira el riesgo legal AGPL`: promueve Patchright (drop-in de Playwright que cierra los leaks `Runtime.enable`/`Console.enable`, `--disable-blink-features=AutomationControlled`, closed shadow roots) a Tier-1 por defecto para WAFs Chrome-shaped, deja camoufox (Firefox-shaped, MPL-2.0) para WAFs Firefox-shaped y **RETIRA nodriver (AGPL-3.0) del default**. Su verificacion (c) es exactamente el sello de esta faceta: `auditoria de licencias (scancode/pip-licenses) que afirma 0 dependencias AGPL en el grafo del servicio API publico tras retirar nodriver del default`. Complemento: **antidetect-validation-harness / CreepJS** (MIT, NEXT-LEVEL.md:245-251) certifica que el swap a patchright/camoufox sigue pasando los detectores reales antes de sellar. URL: https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python — Apache-2.0 [VERIFIED en NEXT-LEVEL.md:256 y tabla :30].

[↑ Indice de facetas](#indice-facetas)

---

<a id="f7"></a>
### Faceta 07 · Reuso & cache de cookie de clearance (multiplicar un solve)

> **Grupo:** Identidad de navegador & anti-deteccion  ·  **Resuelve:** mecanismo (consume 11/3)  ·  **Estado:** MECANISMO-PURO
>
> **Costura —** MECANISMO PURO country-blind: clearance_cache.py no porta supuesto ES (keying por host, TTL, UA-pin, invalidate-on-reject). El unico acoplamiento de pais es INDIRECTO: la cookie esta atada a la IP de egress, que para coherencia cross-border debe casar el locale (faceta 3) via proxy_country del pack (faceta 14). La costura es el CONTRATO de IP sticky geo-coherente, no codigo en este modulo.
>
> **Fix —** (1) Ningun fix ES dentro de clearance_cache.py: ya es generico. (2) Cerrar el gap real (single-proceso): introducir seam `_ClearanceBackend` (espejo de governor._backend) con default in-memory + backend compartido opcional (Redis TTL nativo o tabla PG con expires_at) para que un solve de worker A sea reusable por worker B; firmas get/put/invalidate identicas, callers fetch.py:305/311/326 intactos. (3) TTL refrescable desde el Max-Age observado del Set-Cookie en vez de 25min plano. (4) Clave = (host, egress_country) y no solo host -> una clearance geo-DE jamas se replaya sobre IP ES.
>
> **Adversarial —** Cookie IP-bound: sobre datacenter o IP de pais equivocado el rechazo es masivo (clearance minada sobre fallback-ES rechazada por WAF DE geofenceado). TTL 25min fijo no sigue la rotacion real del vendor (DataDome rota mas rapido bajo carga) -> replay intra-TTL pero post-expiry sirve soft-block, solo salvado por invalidate-on-reject si classify() lo caza (acopla faceta 4). Sin backend compartido: 4 maquinas = 4 solves del mismo host = 4x ban surface. Peor en JP (geofencing estricto).
>
> **Sellado —** Sellado cuando: (a) 2o FetchEngine del proceso reusa via curl_cffi con 0 lanzamientos de navegador (assert solve_challenge count==1 en dos fetches) -VERIFIED hoy fetch.py:304-308-; (b) cookie cacheada rechazada -> served None -> invalidate + re-solve (fetch.py:311); (c) restart sin cookie rancia (sin persistencia, estructural). Upgrade distribuido multi-via: unit (expiry pop on read), integracion (worker B reusa store de worker A, 0 solves extra), adversarial (clave (host,ES) no devuelta para (host,DE)).
>
> **Herramienta NEXT-LEVEL —** Sin tool cache-especifica en NEXT-LEVEL.md. Directa: PyrateLimiter PostgresBucket/RedisBucket [VERIFIED NEXT-LEVEL.md:301-307, MIT, https://github.com/vutran1710/PyrateLimiter] reusa el PG existente (EUR0) como backend del seam _ClearanceBackend (TTL nativo), espejo del seam _backend del governor. Complementaria: patchright-chromium-tier1 [VERIFIED NEXT-LEVEL.md:253-256, Apache-2.0, https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python] mina clearance Chrome-shaped mas duradera -> menos re-solves.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/engine/clearance_cache.py:26` `_DEFAULT_TTL = 25 * 60.0` (segundos) [VERIFIED]; docstring 1-17 declara **in-memory, process-local, TTL-bounded, NO persistido** (un restart re-resuelve, nunca sirve cookie rancia) y thread-safe via `_lock` (`:28`).
- `@dataclass(frozen=True) Clearance{cookies, user_agent, expires_at}` (`:31-35`); `_store: dict[str, Clearance]` (`:38`).
- `get(host, *, now)` (`:41-51`): lazy-expiring — si `c.expires_at <= t` hace `pop` y devuelve None [VERIFIED :48-50].
- `put(host, cookies, user_agent, *, ttl=_DEFAULT_TTL, now)` (`:54-62`): **ignora cookies vacias** (`if not cookies: return`, `:57-58`) — un solve vacio NO es solve.
- `invalidate(host)` (`:65-68`), `clear()` para tests (`:71-74`).
- Integracion en `pipeline/engine/fetch.py`: `host = self._host_of(url)` (`:301`); **paso 1 cache** (`:303-311`): `cached = clearance_cache.get(host)`; si hit -> `_apply_cookies` + `_serve_with_cookies(url, headers, cached.user_agent)`; si `served is not None: return served`; **si None -> `clearance_cache.invalidate(host)`** (`:311`, invalidate-on-reject). **Paso 2 solve** (`:313-326`): tras solve OK `clearance_cache.put(host, result.cookies, result.user_agent)` (`:326`). `_serve_with_cookies` (`:356-373`) **pinea el UA exacto** `served_headers["User-Agent"] = ua` (`:359-360`) y solo devuelve texto si `status==200 and verdict==Verdict.OK` (`:368-370`), si no None.

#### (b) Mecanismo al atomo
Convierte UN solve caro en navegador (Tier-1) en **miles de fetches baratos** via curl_cffi. Clave = host registrable; valor = (cookies, UA EXACTO, expiry monotonic). TTL 25 min conservador para **nunca** replayar una cookie ya rotada por el WAF. El **invariante de reuso** es lo load-bearing: el request servido se ata al UA EXACTO que mino la cookie (`:359-360`) y la IP de egress queda en el proxy sticky del engine — la tupla (UA + forma-TLS + IP + cookie) que el WAF valido se mantiene coherente en el replay. `invalidate`-on-reject (`fetch.py:311`): un hit que vuelve no-OK (`served is None`) se borra y cae a un solve fresco — jamas sirve la cookie rechazada como contenido. Sin persistencia: una cookie rancia es **estructuralmente imposible** cruzar un restart.

#### (c) Costura ES->generico
Faceta de **MECANISMO PURO, country-blind**: keying por host-string, matematica de TTL, UA-pin e invalidate-on-reject no portan ningun supuesto ES. **No hay es-ES soldado aqui.** El unico acoplamiento de pais es INDIRECTO y vive una capa afuera: la IP a la que la cookie esta atada viene del pool de proxies (faceta 11) y, para coherencia cross-border, el geo del egress debe casar el locale (faceta 3) — un solve DE debe minarse y replayarse sobre IP sticky geo-DE o la cookie se rechaza en masa. La costura no esta en `clearance_cache.py`; es el CONTRATO de que el caller entrega una IP sticky geo-coherente, que el `proxy_country` del pack (faceta 14) garantiza.

#### (d) Riesgo adversarial (DE/FR/IT/PT/no-UE/ruido)
- **Cookie IP-bound**: sobre IP datacenter o IP de pais equivocado el rechazo es masivo; para pais #2 una clearance minada sobre IP fallback-ES (gap faceta 11) es rechazada por un WAF DE que geofencea.
- **TTL fijo 25 min no sigue la rotacion real** del vendor (DataDome rota mas rapido bajo carga) -> un replay dentro del TTL pero pasado el expiry real sirve soft-block; solo invalidate-on-reject salva, y solo si `classify()` lo caza (acopla faceta 4).
- **Sin backend compartido**: N maquinas = N solves del mismo host = N x la superficie de ban que el cache existe para evitar.
- Ruido CJK/no-UE: el keying por host es script-agnostico (sin problema propio), pero la coherencia IP-bound es peor donde el geofencing es estricto (JP).

#### (e) Sellado + verificacion multi-via
- **Hoy [VERIFIED por diseno]**: un 2o `FetchEngine` en el mismo proceso reusa via curl_cffi SIN lanzar navegador (`fetch.py:304-308`); cookie rechazada -> detect+invalidate+re-solve (`:311`); restart -> cero cookie rancia (sin persistencia).
- **Multi-via para el upgrade distribuido**: (1) unit — expiry hace pop en read; (2) integracion — worker B reusa la clearance que worker A guardo en backend compartido, 0 solves extra; (3) adversarial — una clearance keyed `(host, ES)` NO se devuelve para lookup `(host, DE)` (cero replay cross-geo).

#### (f) Herramienta NEXT-LEVEL
No existe herramienta especifica de clearance-cache en NEXT-LEVEL.md. La elevacion **directamente aplicable** es reusar la MISMA infra de backend compartido minada para distributed-pacing: **PyrateLimiter (PostgresBucket/RedisBucket)** [VERIFIED NEXT-LEVEL.md:301-307, MIT, https://github.com/vutran1710/PyrateLimiter] reutiliza el Postgres que el proyecto YA corre (EUR0, cero infra nueva); el store de clearance cabalga el mismo Redis/PG (TTL nativo) tras un seam `_ClearanceBackend` espejo del seam `_backend` del governor (`governor.py:24-28,241`). **Complementaria**: **patchright-chromium-tier1** [VERIFIED NEXT-LEVEL.md:253-256, patchright-python Apache-2.0, https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python] mina una clearance Chrome-shaped mas duradera -> menos re-solves -> menos churn de cache. Honesto: ninguna es cache-especifica; son las palancas de backend y de calidad-aguas-arriba que hacen el cache distribuible y mas longevo.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f8"></a>
### Faceta 08 · Governor token-bucket por host (el unico cuello)

> **Grupo:** Transporte por tiers & pacing  ·  **Resuelve:** mecanismo (-> 10)  ·  **Estado:** MECANISMO-PURO
>
> **Costura —** Mecanismo-puro: la math del bucket es identica cross-pais. Unico contenido ES = la tabla _HOST_RATE_CLASSES (faceta 9) inyectada via configure_host(:248) en el bootstrap del factory (:376-449,:448). El pack aporta host_rate_classes y el bucle existente los consume; el governor no cambia.
>
> **Fix —** No hardcodear hosts en el factory governor(): mover el bloque configure_host ES (:376-449) a countries/ES/_pack.py y que el factory itere pack.host_rate_classes. configure_host ya es data-driven (:248), la costura existe.
>
> **Adversarial —** In-memory single-proceso: _buckets(:235)/_ban_until(:245) en RAM -> N maquinas arrancan con bucket lleno (:179) y re-ganan el ban; restart borra la cicatriz (los 138 dealers a 4x). El seam _backend(:241,290) declarado pero default in-memory: multi-maquina inseguro sin GCRA compartido.
>
> **Sellado —** Test agregado (K corrutinas: spacing>=min_spacing, rate<=bucket) + adversarial (4 procesos con backend distribuido respetan el techo donde in-memory dejaria el burst) + via independiente (host-echo log: pacing observado==configurado). Sello: agregado<=bucket por todo worker + ban observado por todos.
>
> **Herramienta NEXT-LEVEL —** PyrateLimiter (MIT, EUR0) https://github.com/vutran1710/PyrateLimiter [VERIFIED NEXT-LEVEL.md:36,304] — PostgresBucket/RedisBucket respalda el bucket sin tocar la API (seam :26,220); atar rate-class a PlatformSpec.defense_tier (0016) no al TLD.

#### (a) code_hints verificados
- [VERIFIED pipeline/engine/governor.py:168] `class _Bucket` — bucket continuo + min-spacing por host; :179 `_tokens = burst` (arranca lleno); :182 `asyncio.Lock`.
- [VERIFIED governor.py:190] `async def acquire` — :197 `async with self._lock` (math atomica), :200 `_refill`, :203 spacing-floor, :204-207 draw token, :209-215 calcula el sleep minimo que satisface token+spacing + jitter.
- [VERIFIED governor.py:218] `class RateGovernor`; [VERIFIED :284] `async def acquire(host)` — :290-293 ruta a `_backend` si esta seteado, si no bucket in-memory; :295-305 honra la cicatriz de ban `_ban_until`.
- [VERIFIED governor.py:307] `async def record_ban(host,cooldown_s)` — :315 `_ban_until[host]=now+cooldown`, :316-317 persiste al backend si existe.
- [VERIFIED governor.py:332] `wrap_fetch_text` — el UNICO choke-point: :347 host_of, :348 acquire, :349 `asyncio.to_thread(fetch_callable)` (event-loop nunca bloqueado), :354-356 feed de `engine.last_verdict==BANNED`->record_ban.
- [VERIFIED governor.py:4-9 docstring] la cicatriz: "138 dealers cayeron por throttling de AS24 bajo carga 4x".

#### (b) Mecanismo al atomo
Un token-bucket continuo por host registrable (`host_of`, :151), refill `rate`/s hasta `burst`, guardado por un `asyncio.Lock` por host (:197) para que corrutinas concurrentes dibujen tokens atomicamente. `acquire` bloquea hasta que HAYA token **Y** haya pasado min-spacing(+jitter) desde el ultimo grant (:203-204): un bucket vacio pacea human-shaped, no un loop a fondo. Buckets independientes (AS24 nunca frena a Kia, ley #5 aislamiento). El choke-point `wrap_fetch_text` es el unico camino al fetch para codigo gobernado; el fetch sincrono curl_cffi corre en thread (`to_thread`, :349) para no bloquear el loop. El lazo de feedback semantico: `last_verdict==BANNED` -> `record_ban` -> deadline `_ban_until` que `acquire()` honra (:296-305) pausando el host `_ban_cooldown_s=900s` (:246).

#### (c) Costura ES->generico + fix exacto
**MECANISMO-PURO**: la matematica del bucket es identica cross-pais. El UNICO contenido ES es la TABLA de rate-class (faceta 9, `_HOST_RATE_CLASSES`, hosts tipo `www.autoscout24.es`) inyectada via `configure_host` en el bootstrap del factory `governor()` (:376-449) y el bucle `for host,profile in _HOST_RATE_CLASSES.items()` (:448). **Fix:** el governor no cambia; el pack (faceta 14) aporta `host_rate_classes:[(host,profile)]` y el bucle existente (:448) los consume — la costura YA existe (`configure_host` es data-driven, :248). La genericidad se logra NO hardcodeando hosts en el factory: mover el bloque ES `configure_host` (:376-449) a `countries/ES/_pack.py` y que el factory itere `pack.host_rate_classes`.

#### (d) Riesgo adversarial concreto
DOS huecos reales [VERIFIED]. (1) **In-memory single-proceso**: `_buckets` (:235) y `_ban_until` (:245) viven en RAM — al escalar a N maquinas cada proceso ARRANCA con bucket lleno (:179 `_tokens=burst`) y re-gana el ban agregado; un restart BORRA la cicatriz de ban (la cicatriz exacta de los 138 dealers a 4x). (2) El seam `_backend` (:241,290) esta declarado pero el path in-memory es el default; sin un backend GCRA compartido, la cosecha multi-maquina es insegura. No-ES: un host JSON_API de un pais nuevo ausente de la tabla hereda STEALTH 0.7 r/s (1/17 de los 12 r/s que tolera) — estrangulando la cosecha (territorio faceta 9, pero muerde aqui).

#### (e) Sellado + verificacion multi-via
1. **Agregado**: lanzar K corrutinas concurrentes contra un host, afirmar spacing observado >= min_spacing y rate agregado <= rate del bucket (la cicatriz 138-dealer hecha imposible).
2. **Adversarial**: 4 procesos contra un host con backend distribuido -> el agregado respeta el techo (el bucket in-memory dejaria pasar el burst de cada uno).
3. **Via independiente**: medir timestamps reales de un host-echo log y comparar con la clase configurada — pacing observado == pacing configurado. Sello = "el agregado a un host nunca supera su bucket por mas workers que corran" + "un ban grabado lo observa TODO worker".

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**PyrateLimiter** (MIT, EUR0) — https://github.com/vutran1710/PyrateLimiter [VERIFIED NEXT-LEVEL.md:36,304 lic MIT]. *defense-tier-preselect + distributed-pacing*: respaldar el bucket in-memory con `PostgresBucket` (reusa el PG que el proyecto YA corre — cero infra nueva, EUR0) o `RedisBucket`, para cosechar desde N procesos/maquinas sin re-ganar el ban; la API publica (acquire/slot/wrap_fetch_text) es el seam estable (:26,220) y no cambia. Mejora acoplada: atar la rate-class a `PlatformSpec.defense_tier` (migration 0016) y no al host-TLD, para que AS24 .de herede el 0.5 r/s que la PLATAFORMA gano, no el 0.7 default. Alternativas: redis-cell (GCRA CL.THROTTLE exacto), limits.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f9"></a>
### Faceta 09 · Tabla de rate-class por host & binding por defense_tier

> **Grupo:** Transporte por tiers & pacing  ·  **Resuelve:** B7 / MP5  ·  **Estado:** CERRABLE
>
> **Costura —** _HOST_RATE_CLASSES (10 hosts ES) y los 9 configure_host STEALTH estan soldados como hosts/TLD ES en governor() [VERIFIED governor.py:102-148,376-441]; y el PUENTE PlatformSpec.defense_tier->rate-class NO existe en codigo (defense_tier solo aparece en comentarios). La fragilidad viaja por TLD, no por plataforma.
>
> **Fix —** (1) Declarar host_rate_classes:[(host,profile)] como dato del CountryScrapePack que el bucle governor.py:448 ya-existente consume; (2) construir el bridge defense_tier->rate-class (t0_open/t1_soft->JSON_API; HTML/stealth/t2+->STEALTH) para que la fragilidad viaje por plataforma en todos sus TLD; (3) consumir entity.defense_tier (ya en DB) al construir el governor para que AS24 .de herede 0.5.
>
> **Adversarial —** autoscout24.de ausente hereda STEALTH 0.7 > el 0.5 ganado-con-ban -> re-gana el ban; un JSON_API de pais nuevo ausente corre a 0.7 vs 12 (1/17); cicatriz arquetipica: searchapi.gw.milanuncios.com faltaba en la tabla y heredo STEALTH 17x lento (BUGFIX governor.py:142-147); DE/FR/IT/PT roster ausente -> todo STEALTH; mis-clasificacion manual sin bridge.
>
> **Sellado —** Todo host del roster clasificado; AS24 .de hereda 0.5 via defense_tier (no 0.7). Multi-via: (a) test host t3 arranca en Tier-1 con 0 probes Tier-0 y .de hereda 0.5; (b) adversarial 4 procesos concurrentes -> rate agregado respeta el techo; (c) via independiente spacing observado en host-echo log == clase configurada.
>
> **Herramienta NEXT-LEVEL —** PyrateLimiter (MIT, EUR0) https://github.com/vutran1710/PyrateLimiter [VERIFIED NEXT-LEVEL.md:304]: ata rate-class a PlatformSpec.defense_tier + PostgresBucket/RedisBucket multi-proceso reusando el PG existente (EUR0). Alt redis-cell (GCRA CL.THROTTLE, el algoritmo exacto del seam governor.py:26,220).

#### (a) Verificacion de code_hints [VERIFIED]
- Default STEALTH: `DEFAULT_RATE_PER_SEC=0.7`, `DEFAULT_BURST=3.0`, `DEFAULT_MIN_SPACING_S=1/0.7`, `DEFAULT_JITTER_S=0.25` [VERIFIED pipeline/engine/governor.py:51-54].
- Clase JSON_API: `JSON_API_RATE_PER_SEC=12.0`, `JSON_API_BURST=24.0`, `JSON_API_MIN_SPACING_S=0.03`, `JSON_API_JITTER_S=0.02` [VERIFIED :88-91]; `_JSON_API_PROFILE` dict [VERIFIED :96-101].
- `_HOST_RATE_CLASSES`: mapea **10 hosts ES** a `_JSON_API_PROFILE` (`web.gw.coches.net`, `api.wallapop.com`, `gql.autocasion.com`, `es.renew.auto`, `scs.audi.de`, `kiaokasion.net`, `services.flexicar.es`, `api-carmarket.ayvens.com`, `searchapi.gw.milanuncios.com`) [VERIFIED :102-148]. Lo NO presente hereda STEALTH 0.7 (comentario :94-95 "treated as fragile until proven otherwise").
- **Cicatriz milanuncios STEALTH-por-omision** [VERIFIED :142-147]: `searchapi.gw.milanuncios.com` faltaba en la tabla -> heredaba silenciosamente STEALTH 0.7 r/s (~17x mas lento) pese a que el docstring del wholesale reclamaba la clase; ahora registrado con nota BUGFIX. **Es el arquetipo del modo de fallo de esta faceta.**
- `governor()` construye `_default_governor`: bloque STEALTH via `configure_host` — `www.autoscout24.es` 0.5/burst2/spacing2 [VERIFIED :376], `autoscout24.es` :377, `www.coches.com` 1.0 :383, `www.dasweltauto.es` 1.0 :390, `www.autocasion.com` 4.0 :407, `carmarket.ayvens.com` 1.0 :417, `www.ocasionplus.com` 1.0 :424, `www.carandclassic.com` 1.0 :433, `www.miclasico.com` 2.0 :441 — y luego `:448-449` un bucle aplica `_JSON_API_PROFILE` a cada host de `_HOST_RATE_CLASSES` [VERIFIED].
- `configure_host` escribe `_overrides[host.lower()]` [VERIFIED :248-257]; `_profile` resuelve `(rate,burst,spacing,jitter)` con fallback `or` a defaults [VERIFIED :259-270].
- `migrations/0016_tiering_groups.sql:6-12` ENUM `defense_tier` = `t0_open / t1_soft / t2_js_challenge / t3_hard_sensor / t4_spend_gated` [VERIFIED]; `PlatformSpec.defense_tier: str|None` existe [VERIFIED pipeline/platform/_core/contract.py:40].
- **EL PUENTE ES INEXISTENTE [VERIFIED]:** `grep defense_tier pipeline/engine/governor.py` devuelve **solo lineas de comentario** (112,117,124,130,144,387,415,421,428,436); **no hay codigo** que mapee `defense_tier -> rate-class`. La etiqueta `defense_tier=t0_open` vive solo como prosa justificativa en los comentarios per-host.

#### (b) El mecanismo al atomo
La rate-class se keyea a **lo que el host ES** (STEALTH vs JSON_API), no a un default global (docstring :57-82): un JSON gateway de primera-parte tolera 12-20 r/s; una superficie HTML/stealth tras WAF activo gana un ban al pasar la cadencia humana. La clase se elige **a mano**: una linea en `_HOST_RATE_CLASSES` (gateway) o un `configure_host()` (bespoke). `_profile` resuelve override-or-default; el `_Bucket` (faceta 8) consume el perfil resuelto. La doctrina de la cicatriz AS24 (0.5 r/s, **por debajo** del rate que gano el ban) esta codificada contra `www.autoscout24.es` especificamente.

#### (c) Costura ES->generico + fix exacto
`_HOST_RATE_CLASSES` (10 hosts) y el bloque `configure_host` (9 overrides STEALTH) son **todos hosts/TLD ES** escritos a mano en `governor()`. La doctrina del scar se ata al host `.es`, no a la PLATAFORMA. **Costura doble:** (1) un pais nuevo NO tiene sus hosts en la tabla -> todos caen a STEALTH 0.7 (seguro pero estrangula los gateways JSON a 1/17 de su techo); (2) `PlatformSpec.defense_tier` (la fragilidad por-plataforma, migracion 0016) **no conduce** la rate-class -> `autoscout24.de` hereda STEALTH 0.7 (default de host desconocido) en vez del 0.5 que la **misma marca** gano con un ban en `.es`. **Fix exacto:** (1) el onboarding declara `host_rate_classes:[(host,profile)]` como dato del `CountryScrapePack` (faceta 14) y el bucle `:448` ya-existente lo consume; (2) construir el puente `PlatformSpec.defense_tier -> rate-class` (`t0_open`/`t1_soft` gateway JSON -> JSON_API; HTML/stealth o `t2+` -> STEALTH) para que la fragilidad viaje por plataforma en TODOS sus TLD; (3) consumir `entity.defense_tier` (ya en DB) al construir el governor para arrancar barato y heredar el pace ganado-con-ban.

#### (d) Riesgo adversarial concreto
- **`autoscout24.de` ausente** -> hereda STEALTH 0.7 > el 0.5 que la marca gano con un ban -> **re-gana el ban**.
- **JSON_API de pais nuevo ausente** -> corre a 0.7 en vez de 12 (**1/17** del techo) -> estrangula la cosecha.
- **Tabla manual sin bridge desde `defense_tier`** -> cada TLD nuevo de una plataforma fragil conocida re-gana el ban.
- **DE/FR/IT/PT:** los hosts de cada pais estan ausentes -> todos default STEALTH; los gateways JSON nativos corren 17x lentos.
- **no-UE:** idem; ademas un gateway de alta-traffic mal-clasificado como STEALTH desperdicia la ventana abierta.
- **Ruido:** un host metido en la clase equivocada (JSON_API sobre una superficie HTML fragil) -> ban; las clases lo mantienen auditable pero un humano puede mis-clasificar — el bridge desde `defense_tier` elimina ese juicio manual.

#### (e) Criterio de sellado + verificacion multi-via
Sello = **todo host del roster del pais clasificado** y una plataforma fragil conocida conserva su pace ganado-con-ban en TODOS sus TLD. Multi-via: (a) test: ningun host del roster hereda STEALTH silenciosamente cuando es un gateway JSON; `autoscout24.de` hereda 0.5 via `defense_tier`, no 0.7. (b) adversarial: 4 procesos concurrentes contra un host -> el rate **agregado** respeta el techo (acoplado a la faceta 10, distribuido). (c) via independiente: medir el spacing real de requests en el log de un host-echo y compararlo contra la clase declarada -> el pacing observado == el configurado.

#### (f) Herramienta que la eleva a nivel inalcanzable
**PyrateLimiter** (MIT, EUR0) — https://github.com/vutran1710/PyrateLimiter [VERIFIED NEXT-LEVEL.md:304 "defense-tier-preselect + distributed-pacing"]. Cubre EXACTAMENTE las dos necesidades acopladas de esta faceta: (1) consumir `entity.defense_tier` (migrations/0016) para **atar la rate-class a `PlatformSpec.defense_tier`, no al host-TLD** -> AS24 `.de` hereda 0.5 (cierra la fuga HIGH governor.py:376), y arrancar en el engine mas barato viable saltando probes Tier-0 inutiles en hosts t2+/t3; (2) respaldar el token-bucket in-memory con `PostgresBucket`/`RedisBucket` (reusa el PG existente) para cosechar multi-proceso sin re-ganar el ban (su Redis-GCRA seam, governor.py:26,220). `PostgresBucket` = cero infra nueva, EUR0. Alternativa para GCRA exacto: redis-cell (modulo Redis MIT, `CL.THROTTLE`) — el algoritmo exacto del seam.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f10"></a>
### Faceta 10 · Estado de rate distribuido multi-proceso (PG / Redis)

> **Grupo:** Transporte por tiers & pacing  ·  **Resuelve:** mecanismo / infra  ·  **Estado:** MECANISMO/INFRA
>
> **Costura —** Backend distribuido implementado (ratelimit_pg.py plpgsql atomico) y cableado por el seam governor.py:241/:290, pero el default es _backend=None -> in-memory single-proceso [VERIFIED governor.py:241,290]; el scar de ban vive en RAM y un restart lo borra [VERIFIED governor.py:245,315]; la impl PG es token-bucket, no GCRA estricto [VERIFIED ratelimit_pg.py:66-90].
>
> **Fix —** Cablear RateGovernor(backend=PostgresRateLimiter(dsn)) + ensure_schema() en el bootstrap de drain multi-maquina (la API publica acquire/slot/wrap_fetch_text no cambia); versionar el schema; si se exige spacing duro, sustituir el bucket por GCRA exacto (redis-cell CL.THROTTLE).
>
> **Adversarial —** Sin backend, N maquinas arrancan con bucket lleno + scar vacio y re-ganan el ban (cicatriz AS24 138 dealers / 4x); con backend mezclar relojes Redis+PG diverge el 'now'; el token-bucket deja colar un burst que GCRA negaria; un host fragil .es sin bridge defense_tier hereda en .de/.it un techo equivocado que el backend respeta fielmente.
>
> **Sellado —** (a) 4 procesos concurrentes -> rate agregado respeta el techo y un ban lo ven todos; (b) medir spacing real en log host-echo == clase declarada; (c) matar worker mid-flight y confirmar banned_until persiste en la fila (no como el scar RAM).
>
> **Herramienta NEXT-LEVEL —** PyrateLimiter (RedisBucket/PostgresBucket/MultiprocessBucket) (MIT, EUR0) https://github.com/vutran1710/PyrateLimiter [VERIFIED NEXT-LEVEL.md:304] — PostgresBucket reusa el PG existente, cero infra; redis-cell (MIT, CL.THROTTLE) [VERIFIED NEXT-LEVEL.md:305] para GCRA exacto self-host EUR0.

#### (a) code_hints [VERIFIED]
- [VERIFIED ratelimit_pg.py:41] `engine_ratelimit_acquire(p_host, p_rate, p_burst, p_min_spacing) RETURNS TABLE(granted boolean, wait_seconds double)` plpgsql. Orden ATOMICO bajo el row-lock que el UPDATE ya toma: INSERT...ON CONFLICT (:56-59) -> SELECT...FOR UPDATE (:61-63) -> refill (:66-70) -> ban-scar (:73-78) -> spacing-floor (:81-82) -> spend (:84-90) -> denied: persist refill + reporta el wait minimo (:93-96).
- [VERIFIED ratelimit_pg.py:102] `PostgresRateLimiter`; [VERIFIED :129] `acquire` (loop try_acquire -> sleep(wait+jitter)); [VERIFIED :151] `record_ban` (INSERT...ON CONFLICT banned_until = clock_timestamp() + cooldown).
- [VERIFIED governor.py:22-28] doc seam: el upgrade hook multi-proceso esta documentado; el texto nombra 'Redis-backed GCRA/token-bucket Lua', la API publica (acquire/slot/wrap_fetch_text) NO cambia con el swap.
- [VERIFIED governor.py:241] `self._backend = backend`; [VERIFIED governor.py:290-293] `if self._backend is not None: return await self._backend.acquire(host, rate=..., burst=..., min_spacing=..., jitter=...)`.
- [VERIFIED governor.py:245,315] el scar de ban in-memory vive en RAM (`self._ban_until`); un restart lo borra — exactamente el gap que el backend distribuido cierra.
- MATIZ TECNICO [VERIFIED ratelimit_pg.py:66-90]: la implementacion es un TOKEN-BUCKET (refill continuo + spacing-floor + spend), NO GCRA estricto. El nombre de la faceta dice 'GCRA' pero el algoritmo realmente codificado es bucket con reloj `clock_timestamp()` compartido.

#### (b) Mecanismo al atomo
El governor expone un seam estable: `acquire(host)` rutea al `_backend` cuando existe, si no al `_Bucket` in-memory por host. El backend PG mueve TODA la matematica (refill + ban-check + spacing + spend) a UNA llamada plpgsql que toma el row-lock que el UPDATE ya necesita -> read-modify-write atomico cross-proceso, imposible de razear entre workers. El reloj es `clock_timestamp()` del servidor DB = un UNICO 'now' compartido. El lado Python solo hace loop: granted -> return waited; else sleep(wait+jitter) -> retry — exactamente la forma de `_Bucket.acquire`, asi el swap in-memory->distribuido es INVISIBLE a los callers (wrap_fetch_text, slot, acquire no cambian una linea). El `banned_until` persiste en la misma fila: un ban que un worker observa throttlea a TODOS hasta que expira (equivalente distribuido de la cicatriz AS24).

#### (c) Costura ES->generico + fix
Esta faceta es MECANISMO PURO country-blind: no tiene costura de DATO ES (lo que viaja por pack es la rate-class, faceta 9, no el backend). Su 'costura' es de INFRA-arranque: el backend (1) debe instanciarse y pasarse `RateGovernor(backend=PostgresRateLimiter(dsn))` en el bootstrap de produccion multi-maquina, y (2) `ensure_schema()` debe correr (crea tabla + funcion, idempotente CREATE OR REPLACE). Fix: cablear el backend en el bootstrap del drain (hoy `_backend` defaultea None -> in-memory single-proceso) y versionar el schema. La superficie publica del governor NO cambia.

#### (d) Riesgo adversarial concreto (escala real multi-maquina)
SIN backend (default None): N maquinas arrancan cada una con bucket lleno + scar VACIO -> martillan el host agregado y re-ganan el ban exacto que el governor existe para evitar (la cicatriz: 138 dealers cayeron por throttling AS24 4x). CON backend PG/Redis self-host EUR0 hay que garantizar: (1) atomicidad real a alta concurrencia — el FOR UPDATE serializa la fila, correcto; (2) consistencia de reloj — `clock_timestamp()` es server-side, correcto, PERO si se mezclan Redis y PG sus relojes divergen; (3) si se exige spacing DURO, el bucket actual deja colar un burst que un GCRA puro negaria. Adversarial cross-pais: un host fragil conocido en .es debe heredar su pace ganado-con-ban en .de/.it (bridge defense_tier, faceta 9), o el backend distribuido respeta fielmente un techo EQUIVOCADO.

#### (e) Sellado + verificacion multi-via
- (a) test: 4 procesos concurrentes contra un host -> el rate AGREGADO respeta el techo (el bucket distribuido no deja pasar el burst que el in-memory single-proc permitiria); un worker que registra un ban -> TODO worker hace backoff (scar compartida observable).
- (b) adversarial: medir el spacing REAL de requests en el log de un host-echo y compararlo con la clase declarada -> el pacing observado == el pacing configurado.
- (c) via independiente: matar un worker mid-flight y confirmar que `banned_until` PERSISTE en la fila (a diferencia del scar RAM que un restart borra) — todo worker nuevo lo ve.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
[VERIFIED NEXT-LEVEL.md:304] `PyrateLimiter` (RedisBucket/PostgresBucket/MultiprocessBucket) (MIT, EUR0) — https://github.com/vutran1710/PyrateLimiter. Trae el backend distribuido battle-tested SIN escribir un limiter desde cero; el PostgresBucket REUSA el Postgres que el proyecto YA corre (cero infra nueva, EUR0). Si se exige GCRA EXACTO (el 'algoritmo exacto del seam'), [VERIFIED NEXT-LEVEL.md:305] `redis-cell` (modulo Redis, comando CL.THROTTLE) es MIT self-host EUR0. Esta es la mejora 'defense-tier-preselect + distributed-pacing', que referencia explicitamente el seam governor.py:26,220 y acopla el arranque-barato-por-defense_tier con el pacing multi-proceso.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f11"></a>
### Faceta 11 · Capa de IP de egress: pool sticky por-drain & residencial

> **Grupo:** Egress & resiliencia de IP  ·  **Resuelve:** B2 / MP2  ·  **Estado:** PARCIAL (residencial OPEN/GASTO)
>
> **Costura —** El mecanismo de egress es country-blind (cicla URLs dadas) pero el harvester por DEFECTO (proxies.py:113 -> free_proxies _COUNTRY='ES') y la costura PENDING-CREDENTIAL (browser.py:61 'residential ES sticky') asumen geo ES; la key sticky engine:{id} ya es generica.
>
> **Fix —** Anadir pack.proxy_country consumido por el filtro del harvester + el selector de credencial residencial; env por pais CARDEEP_PROXIES_{CC}; open_session(pack=) selecciona la geo; mantener la key sticky engine:{id} y el fallback host-IP €0 como piso universal.
>
> **Adversarial —** IPs datacenter queman cookies IP-bound a volumen (sin discriminador ASN/residencial); pais #2 heredando el harvester ES sale por IPs espanolas -> dealer DE/FR/IT sobre IP ES = tell geo -> geo-redirect a vista ES sellada FALSO; no-UE necesita egress in-country; sticky-dict in-proceso no compartido entre restarts/maquinas.
>
> **Sellado —** test: sticky_for estable por engine + pool vacio->host IP (ES byte-identico); adversarial: echo externo aserta geo egress==pack.proxy_country Y cookie minteada en IP-A rechazada desde IP-B; independiente: gate de leak CreepJS (cero WebRTC/DNS, tz<->IP<->locale coherente); PENDING-CREDENTIAL sellado honesto (host-IP, sin falsa cobertura residencial).
>
> **Herramienta NEXT-LEVEL —** NINGUNA directa en NEXT-LEVEL (proxies residenciales son GASTO-gated, fuera del scope €0) [VERIFIED por grep]; lo mas cercano: camoufox geoip-coherence (NEXT-LEVEL.md:209) deriva locale/tz/geo del browser desde la region del proxy; CreepJS (MIT, https://github.com/abrahamjuliot/creepjs) [VERIFIED NEXT-LEVEL.md:248] como gate CI de certificacion de leak.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/engine/proxies.py:24` `class ProxyPool` lee env `CARDEEP_PROXIES` (`:21 _ENV_VAR`), split por comas (`:27-28`) [VERIFIED].
- `:35` `populate` (reemplaza pool, limpia sticky), `:44` `is_stale`, `:49` `ensure_fresh(ttl=600, harvester)` re-cosecha si vacio/stale (`:57`), harvester best-effort nunca fatal (`:61`) [VERIFIED].
- `:79` `next()` round-robin o None (host IP), `:86` `sticky_for(key)` pinea 1 proxy por key de por vida (`:91-93`) [VERIFIED].
- `:100` `default_pool()` singleton proceso, `:113` `free_proxy_harvester` (via #2, lazy import `free_proxies`), `:121` `auto_refresh_default` [VERIFIED].
- `pipeline/engine/fetch.py:142` `_lease_proxy` -> si `not _use_proxy_pool`:None; gate `pool.enabled`; `:150` `pool.sticky_for(f"engine:{id(self)}")` = un engine == una IP sticky para todo el drain (invariante de cookie-reuse) [VERIFIED]; `:156` `_new_session` inyecta `proxies` en la Session curl_cffi [VERIFIED].
- `pipeline/engine/tier1/browser.py:33-36` docstring PROXY (residential ES sticky = requisito transversal, clearance atada a la IP que resuelve), `:61` const `PENDING_CREDENTIAL_PROXY`, `:69` `solve_challenge(proxy=None default)`, `:76` "Pass None for cost-zero host-IP solving; pass http://user:pass@host:port once residential ES proxy wired" [VERIFIED].

#### (b) El mecanismo al atomo
Egress de dos capas. **Capa 1 (Tier-0, curl_cffi)**: cada `FetchEngine` llama `_lease_proxy()` UNA vez y obtiene un proxy sticky keyed por `engine:{id(self)}` -> todo el drain de un dealer sale por UNA IP. Esa stickiness no es cosmetica: la cookie de clearance Tier-1 esta atada a (UA, JA3, IP); reusarla desde otra IP la invalida al primer reuso (`browser.py:6-9`). **Capa 2 (Tier-1 browser)**: `solve_challenge` toma `proxy` explicito; sin credencial es None -> resuelve sobre host IP, marcado `PENDING_CREDENTIAL_PROXY`. El pool es env-driven (`CARDEEP_PROXIES`) -> vacio por defecto -> `next()/sticky_for` devuelven None -> todo fetch sale por host IP = €0, cero cambio de comportamiento. `ensure_fresh` + `free_proxy_harvester` autopueblan desde fuentes libres (via #2) por TTL cuando no hay creds. Sticky-dict + cycle viven en-proceso bajo `threading.Lock`.

#### (c) Costura ES->generico
El pool ya es country-blind en MECANISMO (cicla las URLs que reciba). El acople ES es: (1) el harvester por defecto `free_proxy_harvester` -> modulo `free_proxies` con `_COUNTRY='ES'` soldado (costura de faceta 12, pero es el default cableado aqui en `proxies.py:113-118`); (2) la costura PENDING-CREDENTIAL en `browser.py:61` nombra "residential **ES** sticky proxy" — TODO el diseno asume egress ES. Para el pais #2 el egress debe salir de SU geo, no ES, por coherencia locale<->IP (faceta 3). **Fix**: el pais de egress pasa a campo de pack `proxy_country` consumido por (a) el filtro del harvester y (b) el selector de credencial residencial; la key sticky queda `engine:{id}` (mecanismo intacto); `open_session(pack=)` selecciona `proxy_country`. El fallback host-IP €0 se preserva como piso universal. Convencion env por pais: `CARDEEP_PROXIES_{CC}` para que creds DE/FR caigan sin tocar ES.

#### (d) Riesgo adversarial concreto
- Sobre **IP datacenter** las cookies IP-bound se queman a volumen; un target DataDome/Akamai live flaggea el ASN y la IP sticky se cicatriza rapido; el pool no tiene discriminador residencial/ASN -> un proxy datacenter cosechado envenena todo el drain al que esta pegado.
- El **residential-ES-sticky** es el gap real (`browser.py:36` "no paid credential wired yet").
- **Cross-country**: pais #2 heredando el harvester ES cosecha IPs espanolas -> un dealer DE drenado sobre IP residencial ES = tell geo/locale (navegador ya es-ES + ahora IP ES sobre host .de) -> soft-block o geo-redirect a una vista ES que parsea limpio y sella FALSO (el fallo de faceta 3 disparado aqui por el egress equivocado).
- **no-UE**: target JP/MX necesita egress in-country; un proxy UE es mismatch ASN-geo duro.
- Sticky-dict in-proceso: un restart re-lease IPs frescas (pierde la identidad calentada) y N maquinas tienen mapas sticky independientes -> cero coordinacion cross-proceso.

#### (e) Sellado + verificacion multi-via
**Criterio**: 1 drain == 1 IP de egress estable de la geo del pack, y el fallback host-IP €0 nunca cambia el comportamiento ES. **Multi-via**: (1) **test** — `sticky_for` devuelve el MISMO proxy en N llamadas para una key de engine; pool vacio -> None -> host IP (path ES byte-identico); (2) **adversarial** — asertar via echo externo (ip-api/ipinfo) que la geo de egress == `pack.proxy_country` antes de un solve Tier-1, Y que una cookie minteada en IP-A es RECHAZADA al reusarla desde IP-B (binding cookie-IP probado, no asumido); (3) **eje independiente** — harness de leak (CreepJS) aserta cero leak WebRTC/DNS de la IP host real tras el proxy y que timezone<->IP<->locale son mutuamente coherentes (la coherencia que faceta 3 necesita, verificada aqui en la capa de egress). El estado PENDING-CREDENTIAL se SELLA como honestamente-pendiente: un test aserta que sin credencial se corre sobre host IP y nunca se reclama cobertura residencial inexistente.

#### (f) Herramienta NEXT-LEVEL (eleva a inalcanzable)
**HALLAZGO HONESTO**: NEXT-LEVEL.md NO tiene herramienta de egress-IP / adquisicion de proxy — los proxies residenciales de pago caen tras el gate GASTO, fuera del scope €0-cimiento que la biblia mina. [VERIFIED: grep de NEXT-LEVEL.md por proxy/egress/residential/ASN da solo `:209` "camoufox geoip-coherence (calcula locale/timezone/geo desde la region del proxy)" como alternativa dentro de la seccion browserforge, y `:436` "zero extra egress".] La ELEVACION aplicable es por tanto indirecta: (1) **camoufox geoip-coherence** (NEXT-LEVEL.md:209) — derivar locale/timezone/geo del browser Tier-1 DESDE la region del proxy para que egress e identidad presentada sean auto-coherentes (mata mecanicamente el tell es-ES-sobre-.de); (2) **CreepJS** antidetect-validation-harness (MIT, https://github.com/abrahamjuliot/creepjs [VERIFIED NEXT-LEVEL.md:248]) como gate CI de leak certificando cero leak IP/WebRTC/timezone tras el proxy. No existe herramienta de proxy residencial €0 que recomendar; la credencial residencial sigue siendo decision GASTO-gated del owner, correctamente dejada PENDING.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f12"></a>
### Faceta 12 · Cosecha & health-scoring de proxies libres (coste-cero)

> **Grupo:** Egress & resiliencia de IP  ·  **Resuelve:** B2 / MP2  ·  **Estado:** CERRABLE (+residencial OPEN)
>
> **Costura —** _COUNTRY='ES' es constante de modulo soldada en 3 URLs de fuente [VERIFIED free_proxies.py:27,:34,:39,:43]; comentario que lo justifica como coherencia con es-ES [VERIFIED :26]. tier1_url ya es parametro (input de pack) [VERIFIED :121,:160].
>
> **Fix —** Parametrizar country en fetch_candidates(country=...) y harvest_alive(country=...) alimentado por pack.proxy_country; construir las URLs proxyscrape/geonode con f-string sobre ese parametro [VERIFIED :31-44]. Default country='ES' -> byte-identico. Verificar la geo REAL del egress_ip capturado [VERIFIED :138-142], no fiarse del filtro &country= de la fuente.
>
> **Adversarial —** Pais #2 cosecha IPs espanolas (incoherentes con su locale -> tell geo) [VERIFIED adversarial_risk]; proxyscrape/geonode pueden tener 0 IPs de un pais pequeno (DE/PT/JP) -> harvester devuelve [] y la via #2 muere; listas GitHub country-mixed sin filtro real [VERIFIED :45-46] -> proxy 'vivo' en geo arbitraria que pasa ipify pero es incoherente con el target.
>
> **Sellado —** Pool solo con proxies alive (ipify 200) Y tier1_ok contra target real del pais [VERIFIED :144-153]. Multi-via: (1) muerto->score 0 excluido, vivo-baneado ordena bajo tier1_ok [VERIFIED :62-69,:179]; (2) geolocalizar egress_ip y exigir == pack.proxy_country (geo REAL, no el filtro de fuente); (3) pack.country='DE' -> URLs piden &country=DE, 0 proxy ES en pool DE, ES byte-identico.
>
> **Herramienta NEXT-LEVEL —** HONESTO: NEXT-LEVEL.md NO mina herramienta dedicada de harvest/health-scoring de free-proxies (mecanismo propio EUR0, fuentes publicas sin key) [ASSESSED cluster extraction-scrape + tabla completos]. Palanca de COHERENCIA aplicable: browserforge (Apache-2.0, EUR0) https://github.com/daijro/browserforge [VERIFIED NEXT-LEVEL.md:208] + camoufox geoip-coherence [VERIFIED :209] -- perfil coherente con la geo del proxy parametrizado por pack, cierra el tell egress<->locale. Sellado del tier1_ok: CreepJS (MIT) [VERIFIED :248].

#### (a)+(b) Mecanismo VERIFICADO al átomo
- Capa de RESILIENCIA, no de cimiento: la vía #1 (browser headful sobre la IP residencial del host) ya gana coches.net; los free proxies son la vía #2 para cuando la IP del host se quema a volumen [VERIFIED pipeline/engine/free_proxies.py:1-11]. Confiesa honestamente que son efímeros/flaky [VERIFIED :9-11].
- País SOLDADO: `_COUNTRY = "ES"` [VERIFIED :27] inyectado literalmente en las URLs de las 3 fuentes API: `_PROXYSCRAPE ...&country={_COUNTRY}` [VERIFIED :31-35], `_PROXYSCRAPE_SOCKS` [VERIFIED :36-40], `_GEONODE ...&country={_COUNTRY}` [VERIFIED :41-44]. Comentario explícito de intención: "egress should look ES for coherence with es-ES headers" [VERIFIED :26].
- `_GITHUB_RAW` = 3 listas country-mixed (TheSpeedX, monosans, proxifly) [VERIFIED :47-51] para dar VOLUMEN al health-check ES.
- `fetch_candidates()` [VERIFIED :72]: GET a cada fuente con `impersonate="chrome131"` [VERIFIED :76,:87,:96,:108], parseo tolerante (text/JSON), normaliza a `proto://ip:port`, dedup preservando orden [VERIFIED :116-118]. Cada fuente caída es no-fatal (try/except BLE001) [VERIFIED :84-85,:93-94,:104-105,:114-115].
- `health_check(proxy, *, test_url=ipify, tier1_url=None)` [VERIFIED :121]: GET ipify a través del proxy [VERIFIED :134-135]; si !=200 → dead [VERIFIED :136-137]; captura egress_ip + latency [VERIFIED :138-143]. Si `tier1_url` dado, ADEMÁS fetch de un target Tier-1 REAL y `tier1_ok = (status==200 ∧ ban_detector.classify()==Verdict.OK)` [VERIFIED :144-153] — señal mucho más fuerte que ipify (un proxy vivo que el WAF ya banea es inútil) [VERIFIED :126-129].
- `ProxyHealth.score` [VERIFIED :62-69]: dead=0; vivo = (1 - min(lat,10000)/10000) ∈ [0,1] + bonus 1.0 si tier1_ok → el pase Tier-1 DOMINA sobre la latencia [VERIFIED :69].
- `harvest_alive(max_candidates=60, max_workers=20, tier1_url=None)` [VERIFIED :160]: fetch + health-check paralelo (ThreadPoolExecutor) [VERIFIED :172-178], filtra alive, ordena por score desc (best-first) [VERIFIED :179]. `refresh_pool_urls` devuelve solo las URLs vivas [VERIFIED :183-185]. ALIMENTA el pool (distinto de consumirlo: faceta 11).

#### (b) Costura ES→genérico (fix exacto)
`_COUNTRY="ES"` es una CONSTANTE DE MÓDULO soldada en 3 URLs [VERIFIED :27,:34,:39,:43]. Fix: pasar `country` como parámetro de `fetch_candidates(country=...)` y `harvest_alive(country=...)`, alimentado por `pack.proxy_country`; construir las URLs proxyscrape/geonode con f-string sobre ese parámetro. Default `country="ES"` → byte-idéntico. `tier1_url` ya es parámetro (input de pack: un target Tier-1 del roster del país). `_HEALTH_URL`=ipify es country-blind, no toca.

#### (c) Riesgo adversarial concreto
- **Incoherencia geo→locale** (raíz): con `_COUNTRY` soldado a ES, el país #2 cosecha IPs ESPAÑOLAS [VERIFIED adversarial_risk] → egress .es bajo navegador de-DE/fr-FR = tell de geo/locale → el WAF sirve vista ES o soft-block (cruza con faceta 3).
- **Efímeros/flaky**: el propio módulo lo admite [VERIFIED :9]; con max 60 candidatos puede no hallar uno vivo Y tier1_ok contra un target duro.
- **DE/FR/IT/PT/JP**: proxyscrape/geonode pueden tener pocas o cero IPs de un país pequeño; sin fallback el harvester devuelve `[]` y la vía #2 queda muerta para ese país.
- **Ruido**: las listas GitHub son country-mixed sin filtro real de país [VERIFIED :45-46] → un proxy "vivo" puede estar en cualquier geo, incoherente con el locale objetivo aunque pase ipify.

#### (d) Sellado + verificación multi-vía
- **Sello**: el pool entregado solo contiene proxies (1) alive (ipify 200) Y (2) tier1_ok contra un target REAL del país (no solo ipify) — el `tier1_url` probe es el gate de "no-baneado por el WAF objetivo" [VERIFIED :144-153].
- **Vía 1 (test)**: un proxy muerto conocido → score 0, excluido; un proxy vivo-pero-baneado (tier1_ok=False) ordena por debajo de uno tier1_ok [VERIFIED :62-69,:179].
- **Vía 2 (independiente, geo)**: el `egress_ip` capturado [VERIFIED :138-142] se geolocaliza y debe coincidir con `pack.proxy_country` — verificar la geo REAL de la IP saliente, no fiarse del filtro `&country=` de la fuente.
- **Vía 3 (adversarial)**: con `pack.country="DE"`, afirmar que las URLs piden `&country=DE` y que ningún proxy ES entra al pool DE; ES sigue byte-idéntico.

#### (e) Herramienta NEXT-LEVEL (honestidad: no hay reemplazo directo del harvester)
NEXT-LEVEL.md NO mina una herramienta dedicada al HARVESTING / health-scoring de free-proxies — es un mecanismo propio €0 (proxyscrape/geonode/github-raw son fuentes públicas sin key) sin sustituto battle-tested en el set minado [ASSESSED: revisado el cluster extraction-scrape completo + tabla resumen]. La palanca aplicable es de COHERENCIA, co-igual a la faceta 3:
- **browserforge (Apache-2.0, €0)** — https://github.com/daijro/browserforge [VERIFIED NEXT-LEVEL.md:208]. Generador de huellas country-keyed: una vez `pack.proxy_country` parametriza el harvester, browserforge produce un perfil (Accept-Language+UA+Sec-CH-UA+screen) coherente con ESA geo, cerrando el tell egress↔locale que el `_COUNTRY` soldado abre. La alternativa nombrada "camoufox geoip-coherence (calcula locale/timezone/geo desde la región del proxy)" [VERIFIED NEXT-LEVEL.md:209] es exactamente lo que hace coherente un proxy de geo X.
- Co-palanca de sellado del `tier1_ok`: **CreepJS (MIT, €0)** [VERIFIED NEXT-LEVEL.md:248] eleva el probe de "devuelve OK" a "egress fingerprint-limpio a través de este proxy".
Lo inalcanzable no es cosechar (mecanismo propio) sino la COHERENCIA geo-fingerprint sobre el proxy parametrizado por pack.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f13"></a>
### Faceta 13 · Route-around por entidad (fallback own-site-first)

> **Grupo:** Egress & resiliencia de IP  ·  **Resuelve:** MP9 (fallback)  ·  **Estado:** CERRABLE
>
> **Costura —** DEFAULT_PRIORITIES (source_fallback.py:75-86 [VERIFIED]) esta soldado a ES: 8 claves = own_site + 7 marketplaces espanoles (autocasion/coches_com/motor_es/wallapop/coches_net/autoscout24/milanuncios), con la DUREZA (tier=1 si prio>=90) tambien del roster ES. El unico invariante country-blind es own_site=10 (un dealer siempre tiene su web primero). build_candidates (:89-96) usa .get(key, 60) -> toda fuente no-ES cae a secundario-blando por defecto.
>
> **Fix —** Mover priorities+hardness a CountryScrapePack.fallback_priorities (faceta 14 keystone); dejar own_site=10 como constante country-blind; build_candidates lee pack.fallback_priorities con own_site default. El pack ES reproduce el dict actual byte-identico (golden coexistencia). El motor (order_candidates/fetch_first_available) no cambia: es country-blind y ya enruta cada candidato por el FetchEngine inyectado (tier=1 per-candidato).
>
> **Adversarial —** Roster ajeno: DE=mobile.de/autoscout24.de, FR=lacentrale/leboncoin(DataDome), IT=subito.it/automobile.it, PT=standvirtual/olx.pt. Con .get(key,60) el marketplace duro nacional cae a blando -> se intenta Tier-0 sin escalar, se quema, y el dealer puede quedar sin cobertura. Inversion de dureza: en DE mobile.de es mas duro que autoscout24.de, el orden ES manda al WAF equivocado primero. Sin el ledger attempts, own_site con FetchError se confunde con 'sin inventario'.
>
> **Sellado —** Multi-via: (1) golden — build_candidates con pack ES reproduce DEFAULT_PRIORITIES byte-identico, pack DE produce orden+dureza DE; (2) adversarial never-stop — dealer con unica fuente own_site se resuelve, dealer con todas-FetchError retorna ok==False con ledger completo (nunca vacio silencioso); (3) ledger ortogonal — resolved_source es el menor priority que dio contenido y own_site siempre primero, asserto sobre attempts no sobre el parser.
>
> **Herramienta NEXT-LEVEL —** primp (MIT) — https://github.com/deedy5/primp — [VERIFIED en NEXT-LEVEL.md:293-299, lic MIT :296]. tls-impersonation-breadth: impersona Safari/Firefox/Edge/Opera (JA3/JA4+HTTP2, Rust) para resolver candidatos del route-around en Tier-0 antes de escalar a Tier-1 que quema-IP — NEXT-LEVEL lo ata explicitamente a 'route-around'. Complemento de descubrimiento de own_site: censo schema.org/AutoDealer desde Common Crawl (CC BY 4.0, NEXT-LEVEL.md:180-186) puebla el ref own_site que la tabla prioriza primero en cualquier pais.

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/engine/source_fallback.py:25-31`** [VERIFIED]: `@dataclass(frozen=True) class SourceCandidate` con campos `source_key: str`, `url: str`, `tier: int = 0` (`Tier-1 escalation per candidate when needed`), `priority: int = 100` (`lower = tried first`).
- **`:45-47`** [VERIFIED]: `order_candidates(candidates) -> sorted(candidates, key=lambda c: c.priority)` — `Own site first, hard marketplaces last (stable by priority then order)`.
- **`:50-70`** [VERIFIED]: `fetch_first_available(candidates, *, fetch_text)` itera en orden de prioridad; `:61` `html = fetch_text(cand.url, tier=cand.tier)`; un `FetchError` (`:62-64`) se REGISTRA en `result.attempts` y se salta (`continue`) — `we go around it to the next source, never stop`; el primer candidato con contenido (`:65-69`) fija `resolved_source/url/html` y retorna. Si todos fallan, retorna `result` con `ok == False` (`:70`).
- **`:73-86` `DEFAULT_PRIORITIES`** [VERIFIED]: dict con `own_site: 10`, `autocasion: 20`, `coches_com: 25`, `motor_es: 30`, `wallapop: 40`, `coches_net: 90` (`hard (DataDome) — last, with tier=1`), `autoscout24: 90` (`hard (DataDome) — won live, but still last`), `milanuncios: 95` (`HARDEST (PerimeterX press-and-hold): free browser vías exhausted (nodriver+camoufox+CDP hold all blocked) — route AROUND it`). **Todas las claves son slugs de marketplaces ES.**
- **`:89-96` `build_candidates(refs)`** [VERIFIED]: por cada `(source_key, url)` toma `prio = DEFAULT_PRIORITIES.get(source_key, 60)` (default 60 para fuente desconocida) y `tier = 1 if prio >= 90 else 0` — los marketplaces duros (>=90) escalan a Tier-1 automaticamente.
- **`:22`** [VERIFIED]: `from pipeline.engine.fetch import FetchError` — el modulo se acopla al motor por la excepcion; el `fetch_text` se **inyecta** (`:51` docstring: `a FetchEngine.fetch_text or the module-level fetch_text`), de modo que **cada candidato pasa por el FetchEngine** (Tier-1 aplica por candidato, `:12-13`).

#### (b) El mecanismo al atomo
Route-around es la **red de seguridad de cobertura por-dealer**: garantiza que ningun concesionario quede sin indexar por depender de UNA fuente dura. Atomo a atomo:
1. **Modelo de candidato** (`SourceCandidate`, frozen): un dealer conocido por N refs `{source_key: url}` se expande a N candidatos, cada uno con su dureza (`tier`) y prioridad heredadas de la tabla.
2. **Orden own-site-first** (`order_candidates`): `own_site=10` es el numero mas bajo -> siempre primero. Es el mas barato (sin WAF de marketplace), el mas autoritativo y el mas completo (el dealer publica su stock entero en su propia web). Los marketplaces duros (DataDome/PerimeterX) van ultimos con `tier=1`.
3. **Lazo never-stop** (`fetch_first_available`): el primer candidato con contenido genuino gana y corta; cada fallo se registra como `(source_key, "error:...")` y se salta. El registro `attempts` es la **observabilidad**: se ve por que fuente se resolvio y cuales fallaron. No hay parada silenciosa: si todo falla, `ok==False` es explicito.
4. **Escalado per-candidato** (`build_candidates`, `tier=1 if prio>=90`): solo los marketplaces duros pagan el coste Tier-1 (navegador headful, quema-IP); own_site y secundarios se resuelven barato en Tier-0.

#### (c) La costura ES->generico
`DEFAULT_PRIORITIES` (`:75-86`) esta **soldado a ES**: las 8 claves son `own_site` + 7 marketplaces espanoles (autocasion, coches_com, motor_es, wallapop, coches_net, autoscout24, milanuncios). Tanto las CLAVES como la DUREZA (que fuente lleva `tier=1`) son del roster ES. La costura: mover `priorities` + `hardness` al `CountryScrapePack.fallback_priorities` (faceta 14, el keystone). El UNICO invariante country-blind es `own_site=10` (un dealer siempre tiene su web primero, en cualquier pais) — ese se queda como constante. `build_candidates` lee `pack.fallback_priorities` con `own_site` default; el pack ES reproduce el dict actual byte-identico (golden de coexistencia).

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **Roster ajeno:** DE no tiene coches.net ni milanuncios; tiene **mobile.de** y **autoscout24.de**. FR tiene **lacentrale.fr** y **leboncoin.fr** (DataDome). IT tiene **subito.it** y **automobile.it**. PT tiene **standvirtual.com** y **olx.pt**. Con `DEFAULT_PRIORITIES.get(key, 60)` toda fuente no-ES cae al default 60 -> se trata como secundario blando, aunque sea el marketplace duro nacional. Resultado: el WAF duro local se intenta a Tier-0 (sin `tier=1`), se quema, y nunca escala -> el dealer puede quedar sin cobertura.
- **Inversion de dureza:** en DE, mobile.de suele ser MAS duro que autoscout24.de; el orden ES (autoscout24 ultimo, =90) manda al WAF equivocado primero o trata el mas duro como blando.
- **Ruido / parada silenciosa:** sin el registro `attempts`, un dealer cuya unica fuente viva es own_site pero cuyo own_site dio FetchError se confundiria con "sin inventario". El `result.ok==False` explicito + ledger lo previene (cobertura honesta).

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (golden de coexistencia):** `build_candidates` con el pack ES reproduce EXACTO el `DEFAULT_PRIORITIES` actual (own_site=10..milanuncios=95) byte-identico; un pack DE con mobile.de/autoscout24.de produce el orden DE correcto y su dureza (tier=1) propia.
- **Via 2 (adversarial never-stop):** un dealer cuya unica fuente reachable es own_site se resuelve igual; un dealer con TODAS las fuentes en FetchError retorna `ok==False` con el ledger `attempts` completo (nunca un vacio silencioso).
- **Via 3 (ledger ortogonal):** el `resolved_source` es siempre el candidato de menor numero de prioridad que dio contenido, y `own_site` se intenta primero independientemente del pais — se asserta sobre el ledger, no sobre el parser. Sellado = las 3 vias verdes + `fallback_priorities` viviendo en el pack.

#### (f) Herramienta NEXT-LEVEL que lo eleva a nivel inalcanzable
La logica de ORDEN/fallback en si es ~10 lineas de sort por prioridad — no necesita libreria (seria sobre-ingenieria). Lo que eleva la faceta es hacer que **cada candidato se resuelva barato antes de escalar a Tier-1 que quema-IP**, y ahi NEXT-LEVEL.md es explicito: **primp** (MIT, `tls-impersonation-breadth`, NEXT-LEVEL.md:293-299 [VERIFIED]) `amplia el Tier-0 mas alla del pool Chrome de curl_cffi ... para route-around antes de escalar a Tier-1 navegador (mas caro y quema-IP)`. primp impersona Safari/Firefox/Edge/Opera recientes (JA3/JA4 + HTTP2 coherentes, nucleo Rust): un marketplace que perfila forma NO-Chrome (frecuente en FR/IT) se resuelve como candidato Tier-0 con forma Safari/Firefox en vez de escalar a navegador. URL: https://github.com/deedy5/primp — MIT [VERIFIED en NEXT-LEVEL.md:296 y tabla :35]. **Complemento de descubrimiento** (para POBLAR los refs `own_site` que la tabla prioriza): el censo schema.org/AutoDealer desde **Common Crawl** (NEXT-LEVEL.md:180-186, indice CC BY 4.0) mina el own_site auto-declarado de cada dealer — la senal que hace que `own_site=10` tenga una URL que poner primero en CUALQUIER pais.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f14"></a>
### Faceta 14 · Contrato CountryScrapePack & inyeccion en el motor (keystone)

> **Grupo:** Pack keystone (inyeccion)  ·  **Resuelve:** KEYSTONE (B1/B4/B6/B7/B9/B10 + MP1-MP10)  ·  **Estado:** KEYSTONE-CERRABLE
>
> **Costura —** Hoy cada costura esta soldada en su modulo (es-ES en 3 header factories, hosts ES en _HOST_RATE_CLASSES governor.py:102-148, keywords ES, € en parsing, provincia INE-2-digit, block-strings ES). El pack las LEVANTA a un dato declarativo countries/<CC>/_pack.py leido por open_session(pack=). Clave: el bucle de consumo governor.py:448 (configure_host) YA EXISTE; el pack es definir la dataclass + anadir pack= a open_session (api.py:51) + sustituir cada constante soldada por lookup con default=ES. CountryScrapePack/generic_design [VERIFIED AUSENTE en codigo, solo en docs].
>
> **Fix —** (1) Crear pipeline/engine/pack.py con @dataclass(frozen=True) CountryScrapePack (10 campos + engine_api_version). (2) Anadir pack: CountryScrapePack|None=None a open_session (api.py:51) y threadearlo a FetchEngine; None->cargar countries/ES/_pack.py (default ES byte-identico). (3) En governor() sustituir _HOST_RATE_CLASSES+overrides ES hardcoded por pack.host_rate_classes via el bucle existente governor.py:448. (4) Version-gate: assert pack.engine_api_version compatible con ENGINE_API_VERSION (api.py:37) en construccion -> pack viejo falla LOUD. (5) Guard de completitud: faltar cualquiera de los 10 campos -> construccion raise (no pais a-medias).
>
> **Adversarial —** Omitir UNA costura del pack (block_strings o currency) onboarda el pais a-medias y corrompe en SILENCIO: drain DE con block_strings ES mis-clasifica interstitial aleman como OK (faceta 4); con currency=€ mis-parsea precios DE (faceta 28). Sin version-pin un pack contra ENGINE_API_VERSION viejo carga contra motor nuevo y una costura renombrada queda default-ES en silencio. Single point of failure: error en el pack -> TODA costura aguas-abajo hereda el error. JP estresa el maximo de campos a la vez.
>
> **Sellado —** Sellado cuando: (a) golden coexistencia ES -pack=None vs countries/ES/_pack.py produce FingerprintPool/tabla governor/orden fallback/keywords/currency/provincia byte-identicos, cero drift ES-; (b) pack sin cualquiera de los 10 campos FALLA construccion (completitud mecanica); (c) pack con engine_api_version incompatible FALLA loud (version-pin); (d) pack DE drena host DE con accept-language+proxy_country+rate-class DE sin tocar el motor. Multi-via: unit (presencia de campos), golden (ES byte-identico), integracion (DE e2e), adversarial (omitir costura -> rojo).
>
> **Herramienta NEXT-LEVEL —** DOS directas. Primaria: Country-pack como CONTRATO frictionless Table Schema [VERIFIED NEXT-LEVEL.md:334-340, Frictionless MIT, https://github.com/frictionlessdata/frictionless-py] -valida tipos+regex+ancho-byte per-pais en bootstrap antes del primer INSERT. Secundaria: Pydantic [VERIFIED NEXT-LEVEL.md:584-589, MIT, https://github.com/pydantic/pydantic] -BaseModel con validators cross-field + test CI de biyeccion source_health<->registry<->lock_key (0 UNMAPPED/0 ORPHAN). Pydantic=guard completitud/version in-proceso; frictionless=contrato de ancho de assets tabulares. Ambas EUR0.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/engine/api.py:37` `ENGINE_API_VERSION = "1.0.0"` [VERIFIED]; docstring 1-30 declara esta la **superficie publica ESTABLE** y que la version se bumpea ante cambio rompedor (`:8-9`).
- `open_session(*, tier1, headful, impersonate, tier1_engines, proxy, auto_proxy_refresh, polite_min=0.7, polite_max=1.4) -> FetchEngine` (`:51-73`). **NO existe parametro `pack=` hoy** [VERIFIED api.py:51-55]; es el punto de inyeccion documentado.
- `pipeline/engine/governor.py:448-449`: el bucle de consumo **YA EXISTE** -> `for host, profile in _HOST_RATE_CLASSES.items(): g.configure_host(host, **profile)` [VERIFIED]; `_HOST_RATE_CLASSES` es tabla de hosts ES (`:102-148`); `governor()` arma el default proceso-wide con overrides STEALTH ES (`:372-441`) + el bucle JSON_API.
- **`CountryScrapePack` / `generic_design`: [VERIFIED AUSENTE en codigo]** — grep los halla SOLO bajo `docs/generic-engine-bible/*` (NEXT-LEVEL.md, INSTITUTIONAL-BACKLOG.md, COUNTRY-PACK-CONTRACT.md, stages/02-scrape.md, stages/03-extract.md), **jamas** en `pipeline/` ni `services/`. Existe el doc-spec `COUNTRY-PACK-CONTRACT.md` pero cero lineas de codigo.

#### (b) Mecanismo al atomo
El pack es la **UNICA dataclass commiteada** bajo `countries/<CC>/_pack.py` que ata cada costura de pais en un solo dato leido en construccion. Forma propuesta: `{country_code, accept_language, proxy_country, host_rate_classes:[(host,profile)], platform_roster, fallback_priorities, web_lang_keywords:{stock,count,marketplaces}, currency, province_resolver, block_strings}`. La propagacion entra por `open_session(pack=)` (seam estable, `api.py:51`) y reparte: `accept_language`->FingerprintPool (faceta 3); `proxy_country`->ProxyPool/free_proxies (facetas 11/12); `host_rate_classes`->governor via el **bucle ya-existente** `configure_host` (`governor.py:448`); `fallback_priorities`->source_fallback (faceta 13); `web_lang_keywords`->extractor web (faceta 21); `currency`->parse_money (faceta 28); `province_resolver`->mint (faceta 25); `block_strings`->ban_detector (faceta 4). **Default=ES byte-identico**: con `pack=None` o `country_code=="ES"` cada valor iguala la constante ES soldada de hoy, probado por golden/coexistencia.

#### (c) Costura ES->generico
Hoy CADA costura esta soldada en su modulo: es-ES en 3 factories de headers, hosts ES en `_HOST_RATE_CLASSES`, keywords ES en `_STOCK_HINT`, € en parsing, provincia INE-2-digit, block-strings ES. El pack es la abstraccion que **LEVANTA todas** a un dato declarativo para que un pais nuevo no toque codigo del motor. Insight keystone: la maquinaria de propagacion **ya existe parcialmente** (`governor.py:448` es exactamente el patron de consumo que el pack necesita), asi que el pack es sobre todo (a) definir la dataclass, (b) anadir `pack=` a `open_session`, (c) sustituir cada constante soldada por un lookup del pack con default = valor ES.

#### (d) Riesgo adversarial
- Si UNA costura se omite del pack (p.ej. `block_strings` o `currency`) el pais se onboarda **a medias y corrompe en SILENCIO**: un drain DE con block_strings ES mis-clasifica un interstitial aleman localizado como OK (faceta 4), o con `currency=€` mis-parsea precios DE (faceta 28).
- **Sin version-pin**: un pack escrito contra un `ENGINE_API_VERSION` viejo (`api.py:37`) carga contra un motor nuevo y una costura renombrada/anadida queda default-ES en silencio en vez de fallar ruidoso.
- El pack es **single point of failure**: error en el pack -> TODA costura aguas-abajo hereda el error. No-UE (JP) estresa el maximo de campos a la vez (script, currency, ancho de provincia, proxy geofenceado).

#### (e) Sellado + verificacion multi-via
- **Sellado cuando**: (a) golden de coexistencia ES — construir con `pack=None` y con `countries/ES/_pack.py` da headers FingerprintPool, tabla governor, orden fallback, keywords, currency y provincia **byte-identicos** (cero drift ES); (b) un pack al que le falta cualquiera de los 10 campos **FALLA construccion** (guard de completitud mecanico); (c) un pack con `engine_api_version` incompatible **FALLA ruidoso** (version-pin); (d) un pack DE drena un host DE con accept-language DE + proxy_country DE + rate-class DE **SIN tocar codigo del motor**.
- **Multi-via**: unit (presencia de los 10 campos), golden (ES byte-identico), integracion (pack DE end-to-end), adversarial (omitir una costura -> build rojo).

#### (f) Herramienta NEXT-LEVEL
**DOS directamente aplicables.** PRIMARIA: **Country-pack como CONTRATO de datos auto-verificado (frictionless Table Schema)** [VERIFIED NEXT-LEVEL.md:334-340, Frictionless Framework MIT, https://github.com/frictionlessdata/frictionless-py] — declarar cada dataset del pack como Table Schema con tipos, regex de forma de codigo y **ancho en bytes per-pais**, validado en el bootstrap del pais ANTES de cargar una sola fila/costura; un pack malformado falla con mensaje claro en vez del tardio Postgres `value too long`. SECUNDARIA: **Guard de drift como CONTRATO TIPADO Pydantic** [VERIFIED NEXT-LEVEL.md:584-589, Pydantic MIT, https://github.com/pydantic/pydantic] — modelar el pack como `BaseModel` con validators cross-field + test CI que asevera la biyeccion source_health<->registry<->lock_key (0 UNMAPPED / 0 ORPHAN), convirtiendo el hueco silencioso de onboarding en build ROJO. Pydantic impone el guard de completitud/version in-proceso; frictionless impone el contrato de ancho de los assets tabulares del pack. Ambas EUR0, pure-Python.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f15"></a>
### Faceta 15 · Esquema de receta v2 & persistencia round-trip

> **Grupo:** Receta como activo & cobertura  ·  **Resuelve:** SH5  ·  **Estado:** CERRABLE (+hardening)
>
> **Costura —** El SCHEMA es country-agnostico (Transport/Pagination/Parsing sin literal ES). La costura esta en persistencia: AS24_RECIPE (recipe.py:20, version:1 ES-shaped) es el DEFAULT de write_recipe(recipe=None) via :59, acoplando el modulo a una plataforma ES; y country_of_cdp(:69) defaultea ES.
>
> **Fix —** 1) Sacar AS24_RECIPE a la fuente autoscout24; write_recipe exige receta explicita (sin default ES). 2) country_of_cdp(:69) debe RAISE ante CC no reconocido en vez de defaultear ES. 3) Recipe.to_dict()(:118) unico productor; deprecar el dict v1 desnudo.
>
> **Adversarial —** country_of_cdp default-ES (recipe.py:69): mint-bug de pais #2 vuelca recetas DE en countries/ES/ SIN error. Clobber R3 solo log.warning(:89), no bloquea -> last-writer-wins silencioso. AS24_RECIPE version:1 junto a SCHEMA_VERSION=2: default v1 sin campos VAM de v2. CC JP/CJK no parseado rutea a ES.
>
> **Sellado —** Round-trip golden (campo->to_dict->YAML->from_dict byte-identico, R2 ya lo fuerza) + ruteo (CDP-DE-... aterriza en countries/DE/, malformado RAISE) + adversarial (clobber cross-country diferente BLOQUEA, no logea). Sello: receta auto-suficiente, country-agnostica en schema, arbol correcto o fail-loud.
>
> **Herramienta NEXT-LEVEL —** parsel (BSD-3, EUR0) https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:31,264] — field_map como DSL ejecutable (replay 100% YAML, cero Python por fuente); + in-toto (Apache-2.0, :37,312) provenance tamper-evident del sello; + Hypothesis (MPL-2.0, :38,320) fuzzing de locale.

#### (a) code_hints verificados
- [VERIFIED pipeline/recipe_schema.py:27] `SCHEMA_VERSION = 2`.
- [VERIFIED recipe_schema.py:36-110] dataclasses: `Transport`(:36), `Fingerprint`(:45), `Pagination`(:53), `Parsing`(:63), `Evidence`(:72), `Recipe`(:96).
- [VERIFIED recipe_schema.py:30-33] vocabulario CERRADO DRAFT/VERIFIED/FAILED; [VERIFIED :112-115] `__post_init__` rechaza un status no valido; [VERIFIED :89-93] `Evidence.parse_loss = fetched - parsed`.
- [VERIFIED recipe_schema.py:118] `to_dict` con orden de claves deliberado (:126-139); [VERIFIED :142] `from_dict` defensivo (ignora claves extra, :150-152).
- [VERIFIED pipeline/recipe.py:43] `write_recipe(cdp_code, recipe=None)`; [VERIFIED :69] `recipes_flat_dir(country_of_cdp(cdp_code), root=ROOT)`; [VERIFIED :76] R2 round-trip `if yaml.safe_load(body) != recipe: raise`; [VERIFIED :83-91] R3 clobber -> solo `log.warning` (:89); [VERIFIED :20] `AS24_RECIPE` (version:1, ES-shaped: source autoscout24, /profesionales/{slug}).

#### (b) Mecanismo al atomo
La `Recipe` es el activo durable y reproducible por-dealer que permite re-scrapear SIN retener el crudo (docstring :3-5). Cinco dataclasses capturan cada dimension de replay: transport(engine/base_url/impersonate), fingerprint(UA/JA3), pagination(strategy/url_template/declared_path), parsing(engine/container_path/field_map), evidence(prueba VAM). Status es vocabulario cerrado para que un lector nunca adivine (:18-20); `__post_init__` falla loud ante un estado sin nombre. La (de)serializacion round-trippea con orden de claves deliberado (top-matter legible primero). Persistencia: `write_recipe` deriva el pais del cdp_code (`country_of_cdp`, :69) y aterriza el YAML bajo `countries/<CC>/recipes/<cdp>.yaml` — sin DB lookup. Guard R2: el YAML se round-trippea al ESCRIBIR (:76) para que un defecto de serializacion falle al write, no en silencio al read. R3: una receta DIFERENTE bajo el mismo cdp_code se detecta semanticamente y se logea (:88-91).

#### (c) Costura ES->generico + fix exacto
El SCHEMA es country-agnostico por diseno (Transport/Pagination/Parsing no portan literal ES). La costura esta en la PERSISTENCIA: [VERIFIED recipe.py:20] `AS24_RECIPE` es un dict v1 (version:1) ES-shaped y es el DEFAULT cuando `write_recipe` se llama con `recipe=None` (:59 `recipe = recipe or AS24_RECIPE`), acoplando el modulo de persistencia a una plataforma ES. **Fix:** (1) sacar `AS24_RECIPE` de recipe.py al modulo de la fuente autoscout24; `write_recipe` debe exigir receta explicita (sin default ES). (2) `country_of_cdp` [:69] defaultea ES ante codigo malformado -> un mint-bug de pais #2 vuelca recetas DE en countries/ES/; hacer que RAISE ante CC no reconocido (territorio faceta 30, raiz aqui). (3) coexistencia dict-v1 <-> dataclass-v2: `write_recipe` toma un dict plano, asi que `Recipe.to_dict()` (:118) debe ser el unico productor; deprecar el path de dict desnudo.

#### (d) Riesgo adversarial concreto
[VERIFIED] `country_of_cdp` default-ES (recipe.py:69) -> un mint-bug de pais #2 escribe recetas DE en countries/ES/recipes/ SIN error (corrupcion cross-country silenciosa). El clobber R3 solo LOGea (:89 `log.warning`), no BLOQUEA — dos modulos escribiendo el mismo cdp_code es last-writer-wins con un warning que nadie lee. `AS24_RECIPE` (version:1) vive junto a `SCHEMA_VERSION=2`: un loader que confia en `schema_version` ve un default v1 que carece de los campos evidence/VAM de v2. No-UE: un segmento de cdp_code JP/CJK que `country_of_cdp` no parsea rutea en silencio a ES.

#### (e) Sellado + verificacion multi-via
1. **Round-trip golden**: cada campo de dataclass sobrevive to_dict->YAML->safe_load->from_dict byte-identico (R2 ya lo fuerza al write).
2. **Ruteo**: afirmar que `write_recipe(CDP-DE-...)` aterriza bajo countries/DE/recipes/ y NUNCA countries/ES/ (un codigo malformado debe RAISE, no defaultear).
3. **Adversarial**: un clobber con receta diferente bajo el mismo cdp_code debe BLOQUEAR (no solo logear) cuando las dos difieren cross-country. Sello = "la receta es config auto-suficiente, country-agnostica en schema, y aterriza en el arbol de pais correcto o falla loud".

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**parsel** (BSD-3-Clause, EUR0) — https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:31,264 lic BSD-3]. *executable-field-map-interpreter*: convertir `field_map` de prosa descriptiva a un mini-DSL CERRADO interpretado puramente desde el YAML (CSS/XPath via parsel, JSON via jsonpath-ng, HTML rapido via selectolax). El enum `Parsing.engine` {next_data,jsonld,css,llm_local} mapea cada uno a un Selector que implementa `locate(bytes,container_path,field_map)->list[dict]` — la receta se vuelve activo auto-suficiente real y un pais/fuente nuevo sobre engine conocido es 100% pack YAML, cero Python. Empareja con **in-toto** (Apache-2.0, https://github.com/in-toto/in-toto [VERIFIED :37,312]) para *certifiable-recipe-provenance* (veredicto+parse_loss+hash-golden sellado tamper-evident, compatible con sample-verify-delete) y **Hypothesis** (MPL-2.0, https://github.com/HypothesisWorks/hypothesis [VERIFIED :38,320]) para fuzzear los casos-borde de locale que el golden ES no ve.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f16"></a>
### Faceta 16 · Harness sample-verify-delete & decide_status

> **Grupo:** Verificacion cero-confianza & sello  ·  **Resuelve:** SH1 / SH3  ·  **Estado:** REWORK-SELLO
>
> **Costura —** El harness ya es source-agnostico/country-blind; la costura es lo que decide_status NO aserta: solo integridad de cuenta (parse_loss/target/REFUTED), sin coherencia de locale/geo/moneda/pais [VERIFIED recipe_harness.py:94-117]. Ademas el quorum VAM degrada fuera de ES porque declared=None (faceta 21/18).
>
> **Fix —** Mantener decide_status como nucleo de cuenta y anadir un contrato de datos pre-sello (fill-rate make/model/price/year, enum fuel/transmission, price currency-tagged) que falle CERRADO para atrapar el block-page con schema.org rancio (fetched==parsed pero basura). Restaurar la 2a familia VAM con el oraculo registral (faceta 18) + measured_by_observation para EXACT_ZERO.
>
> **Adversarial —** El guard vacio solo salva fetched==0; una pagina de bloqueo localizada con schema.org rancio da fetched==parsed -> FALSE-VERIFIED; fuera de ES declared=None deja 2-path {fetched,parsed} subconjuntos de los mismos bytes -> ortogonalidad debil -> UNVERIFIED; _COUNT_HINT ES pierde el 3er path en DE/FR/IT/PT/JP; campos CJK parsean a vacio pero cuentan bien.
>
> **Sellado —** VERIFIED iff parse_loss==0 AND parsed>=min(target,k) AND VAM!=REFUTED, cero crudo retenido (sample.parsed.clear() :189). Multi-via: tests puros de decide_status + sello record_count_verdict con families>=2/origins>=2 (verify.py:117-119) + property-based fuzzing de invariantes sobre muestras generadas.
>
> **Herramienta NEXT-LEVEL —** Hypothesis (MPL-2.0, EUR0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320] property-based fuzzing que caza el caso de locale raro y minimiza el contraejemplo; + pandera (MIT) como contrato de datos que falla CERRADO [VERIFIED :164,:318]. Ambos CPU puro, CI local, EUR0.

#### (a) Verificacion de code_hints [VERIFIED]
- Docstring del ciclo canonico EXTRACT(k~3-5)->PERSIST->VERIFY(VAM)->DELETE + doctrina recipe-first/sample-verify-delete/VAM/no-silent-failure [VERIFIED pipeline/recipe_harness.py:1-21].
- `Sample` dataclass `{declared:int|None, fetched:int, parsed:list[dict], full_dealer:bool}`; `full_dealer` iff la muestra cubre el inventario ENTERO (`declared<=k`) — **solo entonces** `declared` entra al quorum VAM (un subset deliberado refutaria en falso) [VERIFIED :49-62].
- `Extractor` Protocol `{source, recipe_template(dealer_ref)->Recipe DRAFT, sample(dealer_ref,k)->Sample}` [VERIFIED :65-74].
- `sample_paths(s)`: `{"fetched":s.fetched, "parsed":len(s.parsed)}`; anade `"source_declared"` **solo** si `full_dealer and declared is not None` [VERIFIED :80-91].
- `decide_status(s,k,verdict)` [VERIFIED :94-117]: `target = declared if (full_dealer and declared!=None) else k`; `loss = fetched - parsed_n`; **FAILED** si `fetched==0 or parsed_n==0` (":108-109 empty sample"); **FAILED** si `loss!=0` (:110-111); **FAILED** si `parsed_n < min(target,k) and not full_dealer` (:112-113); **FAILED** si `verdict=="REFUTED"` (:114-115); si no **VERIFIED** (:116-117).
- `RecipeHarness.run` [VERIFIED :150-194]: 1) `sample = ex.sample` (los UNICOS bytes); 2) VERIFY via `record_count_verdict(subject_type='recipe_sample', tolerance=0.0, claim_kind='count')` si hay conn, si no `_offline_verdict` (:156-163); 3) `decide_status` (:165); 4) `Evidence(verified_at=self._now` **timestamp inyectado** `, sample_k, declared, fetched, parsed, vam_verdict, vam_paths)` (:172-175); 5) `write_recipe` (:180); 6) `sample.parsed.clear()` — **el DELETE: soltar la referencia, ningun crudo a disco** (:186-189).
- `_offline_verdict`: TRUSTWORTHY iff todos los paths iguales, REFUTED si discrepan, si no UNVERIFIED [VERIFIED :196-207].
- **Anclaje VAM** [VERIFIED pipeline/verify.py]: `record_count_verdict` :53; `has_independence = len(families)>=2 AND len(origins)>=2` :117-119; `zero_certifiable = top_val != 0 or measured_by_observation` :155; TRUSTWORTHY solo con `modal_ok AND has_independence AND zero_certifiable`, si no UNVERIFIED, REFUTED ante discrepancia :156-166.

#### (b) El mecanismo al atomo
**VERIFIED = `parse_loss==0` AND `parsed >= min(target,k)` AND `VAM != REFUTED`.** `decide_status` es **puro** (offline-testable, sin DB/red), lo que lo hace el atomo verificable del eje "consistencia interna". El DELETE es **estructural**: la muestra vive solo en memoria local; `sample.parsed.clear()` suelta la referencia; el harness **no escribe ningun fichero crudo** (:186-189) -> nada que fugar en disco (mandato sample-verify-delete, biblia §10). El timestamp se **inyecta** (`self._now`, :148) para prohibir nondeterminismo estilo `Date.now()`. El VAM **reusa** `record_count_verdict` (jamas un check hand-rolled, docstring :14). UNVERIFIED **pasa** (significa "no puedo certificar un quorum", p.ej. acuerdo 2-path same-family), no es desacuerdo.

#### (c) Costura ES->generico + fix exacto
El harness **ya es source-agnostico y country-blind en mecanismo** (conduce cualquier `Extractor`). La costura NO esta en el harness sino en lo que `decide_status` **no puede** asertar: comprueba solo integridad de cuenta (`parse_loss`, `target`, `REFUTED`). **No** aserta coherencia de locale/geo/moneda/pais -> un sitio DE servido en es-ES que parsea limpio (`fetched==parsed`, schema.org presente) sella VERIFIED de la **vista equivocada**. Es el puente a la faceta 30 (sellado country-aware). **Fix exacto:** mantener `decide_status` como nucleo de integridad-de-cuenta y ANADIR un **contrato de datos pre-sello** (fill-rate de make/model/price/year, enum de fuel/transmission, price currency-tagged) que **falle CERRADO** — asi una pagina de bloqueo localizada con schema.org rancio (`fetched==parsed` pero campos basura) se atrapa. El quorum VAM ya degrada fuera de ES (`declared=None` -> 2-path `{fetched,parsed}` que son subconjuntos de los MISMOS bytes -> ortogonalidad debil -> a lo sumo UNVERIFIED); el complemento es el oraculo registral (faceta 18) para restaurar una 2a familia real + el flag `measured_by_observation` para EXACT_ZERO.

#### (d) Riesgo adversarial concreto
- El guard de muestra-vacia solo salva `fetched==0` (:108). Una **pagina de bloqueo localizada con schema.org rancio** da `fetched==parsed` -> **FALSE-VERIFIED** (`parse_loss==0`, la cuenta pasa, pero es un interstitial).
- Fuera de ES `declared=None` -> `sample_paths` devuelve solo `{fetched,parsed}` -> el VAM ve 2 paths de los MISMOS bytes (`parsed ⊂ fetched`) -> ortogonalidad debil -> degrada a 2-path same-family -> UNVERIFIED en el mejor caso.
- **DE/FR/IT/PT:** `_COUNT_HINT` es ES (faceta 21) -> `declared=None` casi siempre fuera de ES -> se pierde el 3er path de cuenta en todas partes.
- **no-UE/JP:** idem; ademas campos CJK pueden parsear a string vacio pero contar bien (la cuenta pasa, el dato esta roto).
- **Ruido:** un subset deliberado (`declared>k`, `full_dealer=False`) excluye correctamente `declared` (:89,:112) y NO refuta en falso — correcto, pero implica que la mayoria de dealers reales (grandes) verifican solo sobre el 2-path debil.

#### (e) Criterio de sellado + verificacion multi-via
Sello = **fiel a los bytes** (`parse_loss==0`) Y produjo coches (`parsed>=min(target,k)`) Y `VAM!=REFUTED`, **sin retener crudo** (`sample.parsed.clear()` :189). Multi-via: (a) tests unitarios de `decide_status` (offline, puros); (b) sello `record_count_verdict` en `verification_verdict` (`subject_type='recipe_sample'`) con independencia `families>=2`/`origins>=2` (verify.py:117-119); (c) property-based fuzzing de los invariantes de `decide_status` sobre muestras generadas (los casos-borde de locale que el golden no ve).

#### (f) Herramienta que la eleva a nivel inalcanzable
**Hypothesis** (MPL-2.0, EUR0) — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320 "property-based-recipe-fuzzing"]. Genera muestras adversariales (separadores mixtos, postcodes no-INE, titulos CJK, precios JPY sobre el techo EUR) — exactamente los modos de fallo CRITICAL/HIGH que los 11 tests golden (que certifican ES) no ven; **minimiza** al contraejemplo mas simple y bloquea el merge; los contraejemplos se congelan como regression-fixtures. Se empareja con **pandera** (MIT) como el **contrato de datos que falla CERRADO** (el gate de fill-rate/enum/range que el sello debe anadir) [VERIFIED NEXT-LEVEL.md:164 "Great Expectations / Pandera", :318]. Ambos CPU puro, CI local, EUR0; pandera auto-deriva estrategias Hypothesis desde el schema del Vehicle.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f17"></a>
### Faceta 17 · RecipeRunner replay (prueba de auto-suficiencia)

> **Grupo:** Receta como activo & cobertura  ·  **Resuelve:** DEUDA replay (5/42)  ·  **Estado:** DEUDA -> CERRABLE
>
> **Costura —** RecipeRunner.replay re-ejecuta CODIGO PYTHON por fuente (EXTRACTORS[recipe.source]().sample) en vez de interpretar el YAML [VERIFIED recipe_harness.py:248]; el propio docstring lo declara 'deliberately NOT claimed' [VERIFIED recipe_harness.py:228-231]; field_map es prosa no ejecutable [VERIFIED recipe_extractors.py:62-73]; el extractor AS24 re-invoca as24._BASE ES soldado [VERIFIED recipe_extractors.py:49,80]; solo 5/42 fuentes tienen Extractor.
>
> **Fix —** Convertir field_map en un mini-DSL cerrado interpretado desde el YAML (enum Parsing.engine {next_data,json_api,jsonld,microdata,css,regex_hydrate} -> Selector.locate(bytes,container_path,field_map)->list[dict] via parsel/jsonpath-ng/selectolax); replay INTERPRETA el YAML, no re-ejecuta Python -> receta auto-suficiente y fuente nueva = 100% pack YAML, cero Python.
>
> **Adversarial —** 37/42 fuentes sin Extractor no tienen replay; un drift de fuente deja replay roto sin deteccion ni reparacion (frescura 24h ~52%); replay solo ve rotura dura (parse_loss>0), no la degradacion silenciosa (campos a NULL, mis-count) -> pagina que aun parsea pero cuenta mal pasa replay verde; pagina de bloqueo con schema.org rancio da reproduced=True falso.
>
> **Sellado —** (a) paridad golden byte-identica: 5 extractores ES como field_map interpretado == Vehicle del Python actual (cero regresion ES); (b) field_map con path inexistente falla al CARGAR (validacion DSL), no al ejecutar; (c) replay en proceso limpio interpreta el YAML sin importar el modulo Python de la fuente, cruzado con el VAM ortogonal.
>
> **Herramienta NEXT-LEVEL —** parsel (CSS+XPath+JMESPath+regex) (BSD-3-Clause, EUR0) https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:264] — sustrato del executable-field-map-interpreter (nucleo de Scrapy); + selectolax (Lexbor ~25x) y jsonpath-ng [VERIFIED NEXT-LEVEL.md:265]; cierra la honestidad recipe_harness.py:228-231. Drift: datasketch MinHash [VERIFIED NEXT-LEVEL.md:232] + Crawl4AI generate_schema [VERIFIED NEXT-LEVEL.md:240] para auto-resintesis.

#### (a) code_hints [VERIFIED]
- [VERIFIED recipe_harness.py:210] `@dataclass class ReplayResult(dealer_ref, source, reproduced, parsed, parse_loss, note)`.
- [VERIFIED recipe_harness.py:220] `class RecipeRunner`; [VERIFIED :237] `def replay(self, recipe_path, k=5)`.
- [VERIFIED recipe_harness.py:243-244] `Recipe.from_dict(yaml.safe_load(fh))` — carga SOLO el YAML; [VERIFIED :245-247] si `recipe.source` no esta en EXTRACTORS devuelve ReplayResult(reproduced=False) con nota.
- [VERIFIED recipe_harness.py:248] `sample = EXTRACTORS[recipe.source]().sample(recipe.dealer_ref, k)` — RE-INVOCA el extractor PYTHON (no interpreta el YAML).
- [VERIFIED recipe_harness.py:249-250] `loss = sample.fetched - len(sample.parsed)`; `reproduced = len(sample.parsed) > 0 and loss == 0`.
- [VERIFIED recipe_harness.py:228-231] docstring de HONESTIDAD: 'a fully field-map-driven interpreter ... is deliberately NOT claimed here -- the extractor still owns the parse code'. El propio codigo declara la grieta.
- [VERIFIED recipe_extractors.py:22-27] EXTRACTORS importa solo 5 fuentes (autoscout24/coches_com/coches_net/autocasion/web_generic); [VERIFIED recipe_extractors.py:49,80] AutoScout24Extractor.sample llama `as24.fetch_page` que usa `as24._BASE` (ES soldado) -> replay de una receta AS24 re-ejecuta el modulo ES.

#### (b) Mecanismo al atomo
El replay es el eje 'reproducibilidad' del sello tri-ortogonal que el propio diseno declara independiente: consistencia interna (harness sample-verify-delete, faceta 16), reproducibilidad (este replay, faceta 17) y cuenta (VAM, faceta 18). Lee el YAML commiteado, selecciona el extractor por `recipe.source`, re-localiza el dealer por `recipe.dealer_ref` y re-extrae k listings. `reproduced` es True iff parse_loss==0 y parsed>0. Es la PRUEBA de que el YAML basta para re-cosechar SIN crudo retenido (mandato sample-verify-delete: el crudo ya se borro; si la receta no reproduce desde el YAML, no es asset auto-suficiente, es un puntero a codigo).

#### (c) Costura ES->generico + fix exacto
La grieta la declara el propio codigo (recipe_harness.py:228-231): `EXTRACTORS[recipe.source]().sample()` re-ejecuta CODIGO PYTHON por fuente, no INTERPRETA el YAML. Para AS24 ese codigo es `as24._BASE = 'https://www.autoscout24.es'` (ES soldado, faceta 20) -> replay de una receta AS24 re-invoca el modulo ES aunque el dealer fuera DE. El `field_map` del Recipe [VERIFIED recipe_extractors.py:62-73] es PROSA descriptiva ('host + listing.url', 'listing.id'), no ejecutable. Fix exacto: convertir field_map en un mini-DSL CERRADO interpretado desde el YAML (selectores CSS/XPath/JSONPath), con un enum cerrado Parsing.engine {next_data,json_api,jsonld,microdata,css,regex_hydrate} que mapea cada uno a un Selector `locate(bytes, container_path, field_map) -> list[dict]`. Asi replay INTERPRETA el field_map en vez de re-ejecutar Python -> la receta pasa de 'config' a 'programa' y un pais/fuente nuevo sobre engine conocido es 100% pack YAML, cero Python.

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
Solo 5/42 fuentes implementan el protocolo Extractor; las 37 wholesale restantes NO tienen replay (faceta 19) -> una receta de un dealer extranjero solo replaya si existe un extractor Python para su fuente. Un drift de fuente (el sitio muta su HTML) deja replay roto SIN deteccion ni reparacion automatica -> la frescura 24h cae (~52% segun recon). Peor: el replay solo detecta rotura DURA (parse_loss>0), NO la degradacion silenciosa (campos que pasan a NULL, estructura que muta pero aun 'parsea', mis-count) -> una pagina que aun parsea pero cuenta mal pasa replay VERDE y miente. Ruido: una pagina de bloqueo localizada con schema.org rancio puede dar fetched==parsed y reproduced=True falso.

#### (e) Sellado + verificacion multi-via
- (a) test: paridad golden byte-identica — los 5 extractores ES reescritos como field_map interpretado producen EXACTAMENTE el mismo Vehicle que el Python actual (cero regresion ES).
- (b) adversarial: una receta con field_map que referencia un path inexistente debe fallar al CARGAR (validacion de DSL), no al ejecutar.
- (c) via independiente: RecipeRunner.replay en un PROCESO LIMPIO interpreta el YAML y reproduce el sample SIN importar el modulo Python de la fuente — prueba la auto-suficiencia que el diseno hoy solo AFIRMA. Cruzar con el VAM ortogonal (declared vs fetched vs parsed): el replay no se auto-aprueba con su propio parser.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
[VERIFIED NEXT-LEVEL.md:264] `parsel` (CSS+XPath+JMESPath+regex) (BSD-3-Clause, EUR0) — https://github.com/scrapy/parsel. Es el sustrato del 'executable-field-map-interpreter': cada valor del enum cerrado Parsing.engine mapea a un Selector que implementa `locate(bytes, container_path, field_map) -> list[dict]`; parsel es el nucleo de Scrapy. Complementos [VERIFIED NEXT-LEVEL.md:265]: `selectolax` (parser Lexbor, ~25x BeautifulSoup) y `jsonpath-ng` (JSONPath para next_data/json_api). Esto cierra EXACTAMENTE la honestidad declarada en recipe_harness.py:228-231 (el interprete field-map 'deliberately NOT claimed'): replay pasa de re-ejecutar Python a INTERPRETAR el YAML. Para el drift que rompe replay sin deteccion: [VERIFIED NEXT-LEVEL.md:232] `datasketch` MinHash/LSH (firma estructural sellada en la receta -> detecta drift) + [VERIFIED NEXT-LEVEL.md:240] Crawl4AI `generate_schema` (auto-resintesis del field_map en 1 disparo, replay determinista) — la corona self-healing.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f18"></a>
### Faceta 18 · VAM count-quorum & oraculo registral por pais

> **Grupo:** Verificacion cero-confianza & sello  ·  **Resuelve:** MP11 / SH2 / SH3  ·  **Estado:** OPEN (registral/LEGAL)
>
> **Costura —** La rama 'registral' de _path_family (verify.py:48) esta keyed sobre tokens ES dgt/cnae/faconauto/borme/census; ningun registrador no-ES clasifica como registral -> el quorum degrada a {http,source} sobre los mismos bytes.
>
> **Fix —** pack.registral_oracle_tokens + adaptador registral por pais (DE KBA/Handelsregister, FR SIV/Infogreffe, IT Motorizzazione, PT IMT/IRN) que aporta un path de cuenta independiente; _path_family lee los tokens del pack (default ES byte-identico); DECLARAR el veredicto sin-oraculo como UNVERIFIED-no-orthogonal-oracle explicito, nunca un pase silencioso.
>
> **Adversarial —** no-ES declared=None -> valores {fetched,parsed} son subconjuntos de un fetch (ortogonalidad debil) -> techo UNVERIFIED, intervalo 100% nunca estrecha; mapa de familias gameable por NOMBRADO de path (un par 'page'+'total' de un solo fetch parece 2-familias); JP/MX sin token registral alguno.
>
> **Sellado —** golden sobre las 7 ramas de familia incl. tokens registrales del pack (ES byte-identico); adversarial {source,http}-misma-pagina -> <=UNVERIFIED y declared=None -> UNVERIFIED-no-oracle explicito; independiente: CHECK DB chk_trustworthy_needs_quorum (0026) doble-cierra quorum_n/family_n/origin_n>=2 en el INSERT; SparseMSE/dga para intervalos de solapamiento-fino.
>
> **Herramienta NEXT-LEVEL —** GLEIF LEI Golden Copy (CC0 1.0, https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy) [VERIFIED NEXT-LEVEL.md:175] — path registral cross-border dia-uno para DE/FR/IT/PT/MX/JP, la familia ortogonal que _path_family no puede poblar fuera de ES; companeros SparseMSE (GPL>=2, NEXT-LEVEL.md:119) + dga (GPL>=2, NEXT-LEVEL.md:127).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/verify.py:31` `_path_family(path_name)` mapea cada path VAM a su FAMILIA de colector: `:42` "db" (db/ingest/persist/land/stored/cdp/distinct/join), `:44` "http" (fetch/harvest/scrape/http/api/live/cage/pair/page), `:46` "source" (declar/source/oracle/header/total/numberofresults/remaining), `:48` "registral" (registr/official/**dgt/cnae/faconauto/borme/census**) <- registradores ES soldados, `:50` "other" fallback [VERIFIED].
- `:53` `record_count_verdict(... paths:dict[str,int], tolerance, claim_kind='count', measured_by_observation)` [VERIFIED].
- `:117-119` `families={_path_family(k)}`, `origins={k}`, `has_independence = len(families)>=2 and len(origins)>=2` [VERIFIED]; `:120` `verifier_paths_json=[{family,origin}]`.
- `:125` `len(values)<2`->UNVERIFIED; `:128` Counter; `:130` rivals; `:136` `primary_agrees` (el path primario/landed debe coincidir con >=1 otro); `:137` `modal_ok = top_n>=2 ∧ ¬rivals ∧ primary_agrees`; `:148` `drift_ok = len>=2 ∧ divergence<=tolerance`; `:155` `zero_certifiable = top_val!=0 ∨ measured_by_observation` [VERIFIED].
- `:156` `modal_ok ∧ has_independence ∧ zero_certifiable`->TRUSTWORTHY; `:160` `modal_ok ∨ drift_ok`->UNVERIFIED; `:166` else REFUTED [VERIFIED].
- `:111-116` comentario: el CHECK DB `chk_trustworthy_needs_quorum` (deep-ledger 0026) exige `quorum_n>=2 ∧ family_n>=2 ∧ origin_n>=2`; la auditoria cazo 989/991 TRUSTWORTHY con quorum_n=0 desde paths string [VERIFIED]; `:201-210` D-supersession (el veredicto mas nuevo es el unico activo) [VERIFIED].

#### (b) El mecanismo al atomo
Una cuenta es TRUSTWORTHY solo si >=2 vias ORTOGONALES concuerdan. La ortogonalidad se impone en DOS ejes calculados aqui para espejar el CHECK DB: `family_n` (familia gruesa via `_path_family`) y `origin_n` (nombres de path distintos). Escalera del veredicto: <2 valores -> UNVERIFIED; cluster modal (>=2 identicos, sin rival >=2, Y el path primario/landed dentro del cluster para que la perdida silenciosa de ingest no se enmascare) sobre >=2 familias Y >=2 origins Y un cero no-espurio -> TRUSTWORTHY; cluster misma-familia O drift dentro de tolerancia pero no exacto -> UNVERIFIED (honesto "no puedo certificar", NUNCA REFUTED, para que los gates que solo filtran REFUTED procedan); resto REFUTED. Guard EXACT_ZERO: 0==0==0 es ausencia, no conjunto-vacio medido, salvo `measured_by_observation` — evita que "fetched:0" selle TRUSTWORTHY (10 recetas web_generic lo habian hecho). El mapa de familias es el oraculo de ortogonalidad: nombres desconocidos colapsan a 'other' para que la independencia no-probada JAMAS otorgue quorum (Law I: subcertificar antes que certificar un punto-ciego compartido).

#### (c) Costura ES->generico
La familia "registral" en `verify.py:48` esta keyed sobre tokens de registrador ES: `dgt`, `cnae`, `faconauto`, `borme`, `census`. Para un pais no-ES esos tokens nunca aparecen -> ningun path se clasifica 'registral' -> la unica familia ortogonal-por-mecanismo (un oraculo fiscal/registral independiente del scraper) es inalcanzable. El quorum degrada a {http, source/other}, donde 'source' (la cuenta declarada del sitio) y 'http' (lo que fetcheamos/parseamos) derivan de los MISMOS bytes -> ortogonalidad debil -> a lo sumo UNVERIFIED. **Fix**: el set de tokens registrales pasa a campo de pack `registral_oracle_tokens` + un ADAPTADOR registral por pais que aporte una cuenta independiente (DE: KBA/Handelsregister; FR: SIV/Infogreffe; IT: Motorizzazione/Registro Imprese; PT: IMT/IRN). `_path_family` lee los tokens del pack (default ES = set de hoy, byte-identico). La POLITICA de quorum para no-ES debe DECLARARSE, no subcertificar en silencio: si no hay path registral, el veredicto es explicitamente `UNVERIFIED-no-orthogonal-oracle`, aflorado como gap de cobertura, no un pase limpio.

#### (d) Riesgo adversarial concreto
- Fuera de ES, `declared=None` es comun (el regex de count-hint no casa la pagina extranjera) -> los valores colapsan a {fetched, parsed} que son subconjuntos de los MISMOS bytes fetched -> ortogonalidad debil -> techo UNVERIFIED; el intervalo 100% nunca se estrecha, asi que un pais no-ES jamas sella cobertura aun con dato bueno.
- Si una 'source' no-ES y el parse 'http' casualmente concuerdan (ambos sobre la misma pagina rancia), `modal_ok` podria disparar con `family_n=2` ({source,http}) pero el acuerdo es sobre un punto-ciego compartido — Law I solo es tan fuerte como la honestidad del mapa de familias.
- **Ruido**: un nombre de path con 'page' mapea a 'http' y uno con 'total' a 'source' aunque ambos vengan de un solo fetch -> el mapa de familias es gameable por NOMBRADO.
- **no-UE** (JP, MX): cero token registral disponible.

#### (e) Sellado + verificacion multi-via
**Criterio**: una cuenta TRUSTWORTHY NUNCA descansa en el mismo parser que escribio el dato; >=2 familias genuinamente ortogonales con politica DECLARADA para no-ES. **Multi-via**: (1) **test** — golden sobre las 7 ramas de `_path_family` incl. los tokens registrales del pack; set ES byte-identico; un token registral extranjero (ej. 'kba') mapea a 'registral'; (2) **adversarial** — alimentar {source, http} ambos de una pagina rancia y asertar <=UNVERIFIED (nunca TRUSTWORTHY) porque los origins comparten familia; alimentar `declared=None` y asertar el UNVERIFIED-no-oracle DECLARADO, no un pase silencioso; (3) **eje independiente** — el CHECK DB `chk_trustworthy_needs_quorum` (0026) es la 2a imposicion: todo TRUSTWORTHY emitido debe satisfacer `quorum_n>=2 ∧ family_n>=2 ∧ origin_n>=2` en el INSERT o levanta CheckViolation — Python y SQL deben concordar, doble-cerrojo del sello. Companero estadistico para paises de solapamiento-fino: SparseMSE/dga dan intervalo finito donde el log-lineal unico degenera (el analogo nacional de este quorum por-cuenta).

#### (f) Herramienta NEXT-LEVEL (eleva a inalcanzable)
**GLEIF LEI Golden Copy** — CC0 1.0 Universal (dominio publico, comercial OK, sin atribucion) — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:175]. La mejora `Lista ortogonal registral transfronteriza GLEIF/LEI` (NEXT-LEVEL.md:172-178) surte un path de captura REGISTRAL para CUALQUIER pais el dia uno: cada entidad con LEI lleva pais + direccion + (a menudo) un id de registro local; el conjunto de LEIs NACE-automocion por region es una lista registral de mecanismo DISTINTO que EXISTE para DE/FR/IT/PT/MX/JP sin escribir adaptador de registro nacional. Es exactamente la familia 'registral' ortogonal que el `_path_family` de la faceta 18 no puede poblar fuera de ES — GLEIF da el oraculo independiente que falta para que el quorum deje de degradar a {http,source}. Companeros para el eje de sellado-bajo-escasez: **SparseMSE** (GPL>=2, https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]) y **dga** (GPL>=2, https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127]) para intervalos finitos donde el solapamiento es fino.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f19"></a>
### Faceta 19 · Protocolo Extractor & cobertura del registro (5/38 -> roster)

> **Grupo:** Receta como activo & cobertura  ·  **Resuelve:** DEUDA cobertura (5/42)  ·  **Estado:** DEUDA -> CERRABLE
>
> **Costura —** Protocolo Extractor country-blind, pero solo 5/38 wholesale lo implementan [VERIFIED recipe_extractors.py:280-286 = 5 entradas; `ls pipeline/platform/*_wholesale.py` = 38]. Costura de COBERTURA, no de pais: 33 wholesale drenan sin sample-verify-delete+replay+VAM; replay imposible si source no esta en EXTRACTORS [VERIFIED recipe_harness.py:245-247].
>
> **Fix —** Cerrar el protocolo sobre los 33 wholesale restantes: cada *_wholesale.py expone sample()/recipe_template() y se registra en EXTRACTORS. Estructuralmente, sustituir las 33 clases Python por un interprete field-map (parsel) que ejecuta el YAML -> un source nuevo es 100% pack, cero Python; la honesta nota 'extractor owns parse code' [VERIFIED :228-231] se elimina al hacer la receta interpretable.
>
> **Adversarial —** 33/38 connectors sin garantia recipe-first -> 'intervalo 100%' miente por arriba; receta con source no-en-EXTRACTORS es irreproducible (replay imposible) [VERIFIED :245-247] -> drift no detectado, frescura 24h cae sin alarma; pais #2 hereda los 33 ES-shaped y anade sus nativos como mas scripts sueltos -> deuda x pais; 33 clases a mano por pais es el cuello inalcanzable manual.
>
> **Sellado —** Todo source del roster del pais en EXTRACTORS -> receta pasa harness (loss==0 AND parsed>=min(target,k) AND VAM!=REFUTED) [VERIFIED recipe_harness.py:94-117] + replay verde [VERIFIED :248-250]. Multi-via: (1) set(EXTRACTORS) superconjunto del roster del pack o gate rojo; (2) cada receta replay-verde en proceso limpio; (3) VAM ortogonal sella cada sample (>=2 familias, parser no se auto-aprueba).
>
> **Herramienta NEXT-LEVEL —** parsel (BSD-3-Clause, EUR0) https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:264] -- executable-field-map-interpreter: receta como PROGRAMA interpretado desde YAML, colapsa 33 clases Python a YAMLs (cita el gap exacto '5/42 conectores' [VERIFIED :263]). Onboarding masivo: Crawl4AI generate_schema (Apache-2.0) https://github.com/unclecode/crawl4ai [VERIFIED :240]. Rung structured: extruct (BSD-3-Clause) https://github.com/scrapinghub/extruct [VERIFIED :288].

#### (a)+(b) Mecanismo VERIFICADO al átomo
- Contrato mínimo de adaptador: `class Extractor(Protocol)` [VERIFIED pipeline/recipe_harness.py:65] con `source: str`, `recipe_template(dealer_ref) -> Recipe` (DRAFT: transport/pagination/parsing pre-llenos, evidence vacía) [VERIFIED :70-72] y `sample(dealer_ref, k) -> Sample` (extracción acotada) [VERIFIED :74].
- `Sample` [VERIFIED :49-62]: `declared` (oráculo propio de la fuente, puede ser >k) [VERIFIED :59], `fetched` (listings crudos que el transporte consumió) [VERIFIED :60], `parsed: list[dict]` [VERIFIED :61], `full_dealer: bool` (True sii la muestra cubre el inventario ENTERO → solo entonces `declared` entra al quórum VAM, si no un subset deliberado refutaría en falso) [VERIFIED :57,:62].
- Registro: `EXTRACTORS = {autoscout24, web_generic, coches_com, coches_net, autocasion}` — EXACTAMENTE 5 entradas [VERIFIED pipeline/recipe_extractors.py:280-286].
- Roster real medido: 38 módulos `*_wholesale.py` [VERIFIED `ls pipeline/platform/*_wholesale.py` = 38], 46 conectores platform totales. Los ~33 wholesale restantes drenan con lógica propia SIN el protocolo Extractor → sin la garantía sample-verify-delete (faceta 16) + replay (faceta 17) + VAM (faceta 18).
- `RecipeRunner.replay` [VERIFIED :220-255] reproduce SOLO desde el YAML: lee la receta, selecciona `EXTRACTORS[recipe.source]` y re-extrae [VERIFIED :245-248]; `reproduced = parsed>0 ∧ loss==0` [VERIFIED :250]. Si el source NO está en EXTRACTORS → `ReplayResult(reproduced=False, "no extractor registered for source")` [VERIFIED :245-247] — un wholesale sin Extractor es IRREPRODUCIBLE por diseño.
- HONESTIDAD codificada: el intérprete field-map universal está explícitamente NO reclamado; "the extractor still owns the parse code" [VERIFIED :228-231] — replay prueba relocalización+reparse, no interpretación pura del YAML.

#### (b) Costura ES→genérico (fix exacto)
El protocolo Extractor ES country-blind (recibe `dealer_ref` opaco, devuelve `Sample`). La costura es de COBERTURA, no de país: 5/38 wholesale tienen Extractor → el sello recipe-first es PARCIAL. Un país nuevo que reuse estos 33 wholesale hereda drains sin garantía. Fix: cerrar el protocolo sobre los 33 restantes (cada `*_wholesale.py` expone su `sample()`/`recipe_template()` y se registra en EXTRACTORS). Estructuralmente, sustituir las 33 clases Python por un intérprete field-map universal que ejecute el YAML → un source nuevo sobre engine conocido es 100% pack, cero Python; la honesta nota "extractor owns parse code" [VERIFIED :228-231] desaparece.

#### (c) Riesgo adversarial concreto
- **Sello parcial heredado**: 33/38 connectors drenan sin sample-verify-delete ni replay [VERIFIED conteo 38 vs EXTRACTORS=5] → el "intervalo 100%" de un país miente POR ARRIBA (cuenta inventario de fuentes no-selladas como sellado).
- **Irreproducibilidad**: una receta cuyo `source` no está en EXTRACTORS no puede replay [VERIFIED :245-247] → drift de fuente no detectado → frescura 24h cae sin alarma.
- **DE/FR/IT/PT**: el país #2 hereda los 33 wholesale ES-shaped; sus equivalentes nativos (un PerimeterX-protected DE, un classifieds IT) se construyen como MÁS scripts sueltos sin Extractor → la deuda se multiplica por país.
- **Escala humana**: escribir 33+ clases Extractor a mano por país es el cuello que hace inalcanzable el roster completo manualmente.

#### (d) Sellado + verificación multi-vía
- **Sello**: TODA plataforma del roster tiene un Extractor registrado → su receta pasa harness (`parse_loss==0 ∧ parsed≥min(target,k) ∧ VAM≠REFUTED`) [VERIFIED :94-117] + replay verde (loss==0 desde YAML) [VERIFIED :248-250].
- **Vía 1 (test)**: `set(EXTRACTORS) ⊇ {todo source del roster del país}` — gate que falla si un wholesale del pack no tiene Extractor.
- **Vía 2 (replay)**: cada receta commiteada del país replay-verde en proceso limpio (relocaliza + reparse, loss==0).
- **Vía 3 (VAM ortogonal)**: el sample de cada Extractor sella por `record_count_verdict` (declared/fetched/parsed, ≥2 familias) — el parser NO se auto-aprueba.

#### (e) Herramienta NEXT-LEVEL (eleva a nivel inalcanzable)
ESTE es el facet que el cluster extraction-scrape ataca de frente:
- **parsel (BSD-3-Clause, €0)** — https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:264]. El "executable-field-map-interpreter": convierte field_map de prosa a un mini-DSL CERRADO interpretado puramente desde YAML (CSS+XPath+JMESPath+regex; núcleo de Scrapy). `RecipeRunner.replay` pasa de re-ejecutar `extractor.sample()` Python a INTERPRETAR el field_map → un país/fuente nuevo sobre engine conocido es 100% pack YAML, CERO Python. Cita textual del gap de ESTA faceta: "solo 5/42 conectores implementan el protocolo Extractor" [VERIFIED NEXT-LEVEL.md:263]. Es el salto "receta como config → receta como programa" que colapsa 33 clases Python a 33 YAMLs.
- **Crawl4AI generate_schema (Apache-2.0, €0)** — https://github.com/unclecode/crawl4ai [VERIFIED NEXT-LEVEL.md:240]. Auto-síntesis del field_map en 1 disparo (LLM emite schema CSS/XPath reusable one-time; extracción determinista €0 en runtime) → onboardar los 33 wholesale restantes sin escribir parse a mano; re-verifica con el harness existente.
- **extruct (BSD-3-Clause, €0)** — https://github.com/scrapinghub/extruct [VERIFIED NEXT-LEVEL.md:288]. Sube el rung structured €0 (JSON-LD+Microdata+RDFa+OpenGraph+Microformats+DublinCore) para los wholesale que dependen de schema.org.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f20"></a>
### Faceta 20 · Exemplar cross-pais AutoScout24 (parser-invariante / country-anchor)

> **Grupo:** Receta como activo & cobertura  ·  **Resuelve:** B3 / MP9  ·  **Estado:** REWORK (cableado exemplar)
>
> **Costura —** El ancla ES esta soldada en TRES sitios y la receta LEE de la fuente (no al reves): autoscout24.py:21 _BASE='https://www.autoscout24.es', :67 path '/profesionales/{slug}' (DE usa /haendler/), :72-73 transporte urllib crudo SIN antideteccion; recipe_extractors.py:49 Transport(base_url=as24._BASE) y :80 sample llama as24.fetch_page() que arma _BASE+/profesionales/ internamente sin override [todo VERIFIED]. El parser __NEXT_DATA__ (parse_listing_vehicle :172-218) es invariante .es/.de (cero strings ES) — la tesis es correcta, el acoplamiento la refuta.
>
> **Fix —** 1) fetch_page acepta base_url+path_template como parametros (default ES byte-identico); recipe_template los graba desde el pack/Transport y sample los pasa -> dominio/path viven en el YAML. 2) Sustituir urllib.request (:72-73) por FetchEngine.fetch_text(url, tier=) -> fingerprint rotation + ban_detector + Tier-1 (invariante de pais). 3) RecipeRunner.replay interpreta el field_map (parsel/jsonpath-ng) en vez de re-invocar as24.sample() -> AS24.de drena cambiando SOLO base_url+path+rate-class en el pack; ES byte-identico (golden).
>
> **Adversarial —** AS24.de HOY exige reescribir la fuente (path /haendler/ != /profesionales/, _BASE ES soldado, urllib sin override) -> copiar-pegar el modulo = drift; la plataforma que debia probar la tesis la refuta. urllib sin antideteccion: un 200 soft-block DE se parsea como __NEXT_DATA__ ausente -> 0 listings -> 'dealer vacio' falso en vez de 'bloqueado'. replay de receta DE re-invoca fetch_page que arma autoscout24.es/profesionales/ -> reproduce la vista ESPANOLA de un dealer aleman o 404; el sello de auto-suficiencia miente.
>
> **Sellado —** Multi-via: (1) golden ES — receta AS24.es replay byte-identico (parse_loss==0) tras parametrizar base_url/path, Vehicle exacto al actual; (2) adversarial DE — pack autoscout24.de (path /haendler/, rate 0.5) drena dealer DE con el MISMO parser, replay verde, y el swap urllib->FetchEngine hace que un challenge DE escale en vez de servir interstitial; (3) auto-suficiencia — RecipeRunner.replay en proceso limpio interpreta el field_map YAML sin importar pipeline.sources.autoscout24.
>
> **Herramienta NEXT-LEVEL —** parsel (BSD-3-Clause) — https://github.com/scrapy/parsel — [VERIFIED en NEXT-LEVEL.md:261-267, lic BSD-3-Clause :264]. executable-field-map-interpreter: el field_map AS24 ya es JSON-path-shaped (recipe_extractors.py:62-73), jsonpath-ng/JMESPath sobre __NEXT_DATA__ reemplaza el parser Python -> replay interpreta el YAML sin re-invocar codigo ES ('holds sin tocar codigo', cero Python por fuente). Complemento: primp (MIT, :293-299) para AS24.de si el WAF perfila forma no-Chrome.

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/sources/autoscout24.py:21`** [VERIFIED]: `_BASE = "https://www.autoscout24.es"` — dominio ES soldado como constante de modulo.
- **`:64-67`** [VERIFIED]: `fetch_page(slug, page, ...)` construye `url = f"{_BASE}/profesionales/{slug}?atype=C&sort=price&desc=1&page={page}"`. El segmento **`/profesionales/`** es el path ES (AS24 .de usa `/haendler/` [ASSUMED — convencion conocida de AS24.de, no verificable en este repo]).
- **`:72-73`** [VERIFIED]: transporte = **urllib crudo**: `req = urllib.request.Request(url, headers={"User-Agent": _UA})` + `with urllib.request.urlopen(req, timeout=40) as r:` — **sin antideteccion** (sin fingerprint rotation, sin ban_detector, sin Tier-1). El `_UA` (`:22-23`) es un Chrome 137 estatico soldado.
- **Parser INVARIANTE** [VERIFIED]: `_next_data` (`:87-89`) extrae `__NEXT_DATA__` via regex `:24`; `parse_listing_vehicle` (`:172-218`) navega claves JSON estructurales (`raw.get("vehicle")`, `prices.public.priceRaw`, `firstRegistrationDate`, `mileageInKm`...) — **cero strings ES en la logica de parseo**; opera sobre el shape del `__NEXT_DATA__`, identico en `.es`/`.de`. Esta es LA tesis: el parser es country-agnostico, solo el ancla (dominio/path) es ES.
- **`recipe_extractors.py:42-74`** [VERIFIED]: `AutoScout24Extractor.recipe_template` graba `Transport(engine="http", base_url=as24._BASE, ...)` (`:49`) y `Pagination(url_template="/profesionales/{slug}?...")` (`:55`) — **la receta hereda el ancla ES del modulo fuente**, no al reves. El `field_map` (`:62-73`) ya es prosa JSON-path-shaped (`"make": "listing.vehicle.make"`, `"price": "listing.prices.public.priceRaw|tracking.price"`).
- **`:76-92` `sample(dealer_ref, k)`** [VERIFIED]: `:80` `html = as24.fetch_page(dealer_ref, 1)` — el sample llama `fetch_page` que arma `_BASE + /profesionales/` **internamente, sin parametro de override**. Por tanto `RecipeRunner.replay` (que invoca `EXTRACTORS[source].sample`) re-ejecuta el codigo ES: el dominio/path no salen del YAML sino del modulo Python.

#### (b) El mecanismo al atomo
AS24 es **el country-anchor**: la plataforma elegida para PROBAR la tesis "parser reusable, solo la receta es pack". El mecanismo:
1. **SSR `__NEXT_DATA__`**: AS24 sirve server-side render con un blob JSON que lleva cada listing (vehiculo + seller/dealer + location). `harvest_dealer` (`:286-317`) drena pagina a pagina hasta alcanzar `numberOfResults` (declared count) o pagina vacia; `parse_page_dealer` (`:221-243`) saca la identidad del dealer de `dealerInfoPage`.
2. **El parser no toca idioma**: navega claves de objeto (`vehicle.make`, `prices.public.priceRaw`). Por construccion, AS24.de devuelve el MISMO shape -> el mismo parser produce los mismos `Vehicle`. La unica diferencia .es/.de es el ANCLA: `base_url` (`autoscout24.es` vs `.de`), `path` (`/profesionales/` vs `/haendler/`) y la `rate-class` del host.
3. **El acoplamiento que rompe la tesis**: hoy el ancla esta soldada en TRES sitios — la constante `_BASE` (`:21`), el f-string de `fetch_page` (`:67`), y el transporte urllib (`:72-73`). Y la receta LEE de la fuente (`recipe_extractors.py:49` `base_url=as24._BASE`), no al reves -> `replay` re-invoca codigo ES. La plataforma que debia probar "holds sin tocar codigo" hoy EXIGE reescribir la fuente por pais.

#### (c) La costura ES->generico
Tres fixes atomicos invierten el acoplamiento:
1. **Ancla desde la receta, no desde el modulo:** `fetch_page` debe aceptar `base_url` + `path_template` como parametros (default ES byte-identico); el `recipe_template` los graba desde el `pack`/`Transport`, y `sample` los pasa a `fetch_page`. Asi el dominio/path viven en el YAML.
2. **Transporte por el FetchEngine, no urllib:** sustituir `urllib.request` (`:72-73`) por `FetchEngine.fetch_text(url, tier=...)` -> gana fingerprint rotation + ban_detector (un 200-interstitial DE deja de servirse como contenido) + escalado Tier-1. Esto es invariante de pais.
3. **Replay que re-ancla desde YAML:** que `RecipeRunner.replay` interprete el `field_map` (via parsel/jsonpath-ng) en vez de re-invocar `as24.sample()` Python -> la receta se vuelve auto-suficiente y AS24.de drena cambiando SOLO `base_url`+`path`+`rate-class` en el pack. ES queda byte-identico (golden).

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **AS24 .de exige reescribir la fuente HOY:** path `/haendler/` != `/profesionales/`, `_BASE` ES soldado, urllib sin override -> sin los 3 fixes, onboardar AS24.de es copiar-pegar el modulo (drift). **La plataforma que debia probar la tesis la REFUTA.**
- **urllib sin antideteccion = interstitial servido como inventario:** un WAF DE que devuelve un 200 soft-block (`:73` urlopen no clasifica) se parsea como `__NEXT_DATA__` ausente -> `{}` -> 0 listings -> se confunde con "dealer vacio" en vez de "bloqueado". El FetchEngine+ban_detector lo haria fail-loud.
- **replay acoplado al codigo ES:** `recipe_extractors.py:80` fija host+path ES; un `replay` de una receta DE re-invocaria `fetch_page` que arma `autoscout24.es/profesionales/` -> reproduce la vista ESPANOLA de un dealer aleman, o 404. El sello de auto-suficiencia miente.
- **AS24 multi-pais (cross-border):** AS24 opera el MISMO dealer en varios paises; sin un ancla por pais limpia, la identidad cross-border es inestable (conecta con faceta 24/26).

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (golden ES, cero regresion):** la receta AS24 .es replay byte-identico (`parse_loss==0`) tras mover `base_url`/`path` a parametros — el `Vehicle` producido es EXACTO al actual.
- **Via 2 (adversarial DE holds-sin-tocar-codigo):** un pack AS24.de (`base_url=autoscout24.de`, `path=/haendler/{slug}`, rate-class 0.5) drena un dealer DE con el MISMO parser y replay verde; el swap urllib->FetchEngine hace que un challenge DE escale/raise en vez de devolver interstitial.
- **Via 3 (auto-suficiencia independiente):** `RecipeRunner.replay` en proceso limpio interpreta el `field_map` del YAML (parsel/jsonpath) y reproduce el sample **sin importar `pipeline.sources.autoscout24`** — prueba la auto-suficiencia que el diseno solo afirmaba. Sellado = 3 vias verdes.

#### (f) Herramienta NEXT-LEVEL que lo eleva a nivel inalcanzable
**parsel** (BSD-3-Clause) — `executable-field-map-interpreter` (NEXT-LEVEL.md:261-267 [VERIFIED]): convierte el `field_map` de prosa descriptiva a un mini-DSL CERRADO interpretado puramente desde el YAML (CSS/XPath + **JMESPath para JSON** + regex; parsel es el nucleo de Scrapy). AS24 es el caso ideal: su `field_map` ya es JSON-path-shaped (`listing.vehicle.make`, `listing.prices.public.priceRaw` — `recipe_extractors.py:62-73`), de modo que jsonpath-ng/JMESPath sobre el `__NEXT_DATA__` reemplaza `parse_listing_vehicle` Python. Asi `RecipeRunner.replay` `pasa de re-ejecutar extractor.sample() (Python) a INTERPRETAR el field_map -> la receta es un activo auto-suficiente real y un pais/fuente nuevo sobre engine conocido es 100% pack YAML, cero Python` — exactamente "holds sin tocar codigo". Verificacion (a) del doc: `paridad golden byte-identica — los 5 extractores ES actuales reescritos como field_map interpretado producen EXACTAMENTE el mismo Vehicle`. URL: https://github.com/scrapy/parsel — BSD-3-Clause [VERIFIED en NEXT-LEVEL.md:264 y tabla :31]. Complemento: **primp** (MIT, :293-299) amplia la breadth TLS para AS24.de si su WAF perfila forma no-Chrome.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f21"></a>
### Faceta 21 · Extractor web generico de cola-larga & pack de keywords de idioma

> **Grupo:** Receta como activo & cobertura  ·  **Resuelve:** B4 / MP4 / SH2  ·  **Estado:** CERRABLE
>
> **Costura —** TRES constantes soldadas a ES, todas en recipe_extract_web.py: _STOCK_HINT (:28-30) slugs ES, _COUNT_HINT (:32) palabras ES, _MARKETPLACES (:33) set ES. El parser JSON-LD/microdata (:53-109) es country-blind. Costura: levantar {stock_hints,count_hints,marketplaces} al web_lang_keywords del pack (faceta 14), default=regex ES de hoy byte-identicos. Es un pack de keywords, NO un rewrite del parser.
>
> **Fix —** (1) Parametrizar _STOCK_HINT/_COUNT_HINT/_MARKETPLACES desde pack.web_lang_keywords; ES pack=regex actuales byte-identicos; DE anade fahrzeuge|gebrauchtwagen|fahrzeugbestand, FR vehicules|occasion, IT usato|veicoli, JP 在庫|中古車. (2) _COUNT_HINT debe manejar separador de millares del locale (hoy \d{1,5} lee '1.234'->234) routeando por el parser numerico de faceta 28. (3) Capturar priceCurrency de offers (recipe_extract_web.py:79 hoy lo descarta) -> dimension moneda poblada (acopla faceta 28). (4) Subir el recall estructurado mas alla de JSON-LD+microdata hand-rolled para que menos sitios de cola-larga caigan a FAILED.
>
> **Adversarial —** _STOCK_HINT casa slugs ES ONLY -> en DE (/fahrzeuge,/gebrauchtwagen), FR (/vehicules,/occasion), IT (/usato), JP (在庫,中古車) find_stock_url=None -> cae al home -> sample vacio -> FAILED: TODA la cola-larga del pais #2 falla descubrimiento en silencio. _COUNT_HINT ES -> declared=None no-ES -> VAM degrada (faceta 18); \d{1,5} lee '1.234 Fahrzeuge'->234 (off-by-1000). Pagina de error estilizada con schema.org rancio -> fetched==parsed -> FALSE-VERIFIED (facetas 16/4). Ruido: link de marketplace fuera del set ES seguido como stock propio.
>
> **Sellado —** Sellado cuando: (a) parser JSON-LD/microdata da vehiculos byte-identicos sobre fixtures ES (cero regresion); (b) fixture DE/FR/IT/JP con slugs localizados es DESCUBIERTO (find_stock_url non-None) y parseado via pack de keywords; (c) sitio JS-only sigue dando vacio -> FAILED honesto; (d) conteo declarado parsea bajo separador de millares. Multi-via: golden (paridad ES), integracion (descubrimiento por-idioma), adversarial (error estilizado con schema.org rancio cazado por contrato fill-rate, no sellado), via independiente (conteo via extraccion estructurada cruzado vs _COUNT_HINT: metadato vs texto).
>
> **Herramienta NEXT-LEVEL —** Primaria: extruct (6 sintaxis) + trafilatura [VERIFIED NEXT-LEVEL.md:285-291, extruct BSD-3-Clause, https://github.com/scrapinghub/extruct] sustituye vehicles_from_jsonld/microdata hand-rolled (recipe_extract_web.py:53-109) y anade RDFa/OpenGraph/microformats + cola-larga sin schema.org, subiendo recall EUR0 antes del LLM. Corona: datasketch MinHash DRIFT [VERIFIED :229-235, MIT, https://github.com/ekzhu/datasketch] + Crawl4AI generate_schema AUTO-RESYNTHESIS [VERIFIED :237-243, Apache-2.0, https://github.com/unclecode/crawl4ai] + parsel field_map ejecutable [VERIFIED :261-266, BSD-3-Clause, https://github.com/scrapy/parsel].

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/recipe_extract_web.py:27` `_VEHICLE_TYPES = ("Car","Vehicle","MotorizedVehicle","Motorcycle","Product")`.
- `:28-30` `_STOCK_HINT` regex con **slugs ES**: `coches|vehiculos|veh%C3|stock|ocasion|inventario|segunda-mano|nuestros-coches|vehiculos-ocasion|km0|kilometro-0` [VERIFIED].
- `:32` `_COUNT_HINT = r'(\d{1,5})\s*(?:veh[ií]culos|coches)\b'` — **palabras ES** y `\d{1,5}` **no maneja separador de millares** [VERIFIED].
- `:33-34` `_MARKETPLACES` set ES (paginasamarillas/wallapop/coches.net/autoscout/milanuncios...).
- `find_stock_url(home_html, base)` (`:37-50`): itera matches de `_STOCK_HINT`, salta marketplaces, devuelve el primero.
- `vehicles_from_jsonld(html)` (`:53-87`): recorre recursivo cada bloque JSON-LD; cuenta nodo como vehiculo iff `@type in _VEHICLE_TYPES AND node.get("name")` (`:75`); saca `offers.price` (`:79-81`) pero **DESCARTA `priceCurrency`** [VERIFIED: solo `.get("price")`].
- `vehicles_from_microdata(html)` (`:95-109`); `_valid` = name + (price o url) (`:112-114`).
- `GenericWebExtractor` (`:117-165`): `source="web_generic"`; `sample(dealer_ref,k)` (`:139-165`): fetch home (tier=0), `find_stock_url`, fallback al home, jsonld->microdata, `_COUNT_HINT` para `declared` (`:158-159`), slice k, parsed=validos, `full = declared<=len(sliced)`.

#### (b) Mecanismo al atomo
Es el rung **coste-0 universal** y el MAS reusado de la cola-larga. Flujo: fetch del home del dealer (tier=0, por el engine antideteccion compartido) -> descubrir la pagina de stock via `_STOCK_HINT` (saltando links de marketplace para quedarse en la web PROPIA del dealer) -> extraer schema.org JSON-LD (Car/Vehicle/Product/Motorcycle), con fallback a microdata si no hay JSON-LD. Un nodo es vehiculo iff `@type` casa Y tiene `name` (identidad minima); price/url lo hacen accionable. `declared` viene del scrape de texto `_COUNT_HINT` para el VAM. Web JS-rendered -> sample vacio -> el harness marca **FAILED honesto** (nunca exito falso). El **parser (JSON-LD walk) es INVARIANTE** entre idiomas; solo los hints de descubrimiento y las palabras de conteo son por-idioma.

#### (c) Costura ES->generico
TRES constantes soldadas a ES, todas en `recipe_extract_web.py`: `_STOCK_HINT` (`:28-30`) solo casa slugs ES; `_COUNT_HINT` (`:32`) solo casa "vehiculos/coches"; `_MARKETPLACES` (`:33`) es el set de marketplaces ES. El parser JSON-LD/microdata (`:53-109`) es genuinamente country-blind. Costura: **levantar `{stock_hints, count_hints, marketplaces}` al `web_lang_keywords` del pack** (faceta 14), default = los regex ES de hoy byte-identicos. El fix es un **pack de keywords**, NO un rewrite del parser — el parser ya generaliza.

#### (d) Riesgo adversarial
- `_STOCK_HINT` casa slugs ES ONLY -> en DE (`/fahrzeuge`, `/gebrauchtwagen`), FR (`/vehicules`, `/occasion`), IT (`/usato`), JP (在庫, 中古車) `find_stock_url` devuelve None -> cae al home -> sample vacio -> **FAILED**, asi que TODA la cola-larga del pais #2 falla el descubrimiento en silencio.
- `_COUNT_HINT` palabras ES -> `declared=None` para no-ES -> el VAM degrada a menos familias ortogonales (acopla faceta 18). `\d{1,5}` mis-lee "1.234 Fahrzeuge" como **234** (off-by-1000 en el declared).
- Una pagina de error estilizada con schema.org rancio da `fetched==parsed` -> **FALSE-VERIFIED** (acopla facetas 16/4).
- Ruido: un link de marketplace **no** en el `_MARKETPLACES` ES (p.ej. un classifieds local DE) se sigue como si fuera el stock propio del dealer.

#### (e) Sellado + verificacion multi-via
- **Sellado cuando**: (a) el parser JSON-LD/microdata produce vehiculos **byte-identicos** sobre fixtures ES (cero regresion); (b) un fixture DE/FR/IT/JP con slugs localizados es DESCUBIERTO (`find_stock_url` non-None) y parseado via el pack de keywords; (c) un sitio JS-only sigue dando vacio -> FAILED honesto; (d) el conteo declarado parsea correcto bajo separador de millares del locale.
- **Multi-via**: golden (paridad ES), integracion (descubrimiento por-idioma), adversarial (pagina de error estilizada con schema.org rancio cazada por un contrato de fill-rate, no sellada), via independiente (conteo de vehiculos via extraccion estructurada cruzado contra `_COUNT_HINT` -> dos familias: metadato vs texto visible).

#### (f) Herramienta NEXT-LEVEL
PRIMARIA: **deterministic-structured-extraction-upgrade — extruct (6 sintaxis) + trafilatura** [VERIFIED NEXT-LEVEL.md:285-291, extruct BSD-3-Clause, https://github.com/scrapinghub/extruct] — sustituir el `vehicles_from_jsonld`/`vehicles_from_microdata` hand-rolled (`recipe_extract_web.py:53-109`) por extruct (JSON-LD + Microdata + RDFa + OpenGraph + Microformats + Dublin Core en un motor battle-tested) y anadir **trafilatura** para la cola-larga sin schema.org, subiendo el recall del rung estructurado EUR0 ANTES de gastar un token de LLM. CORONA complementaria: **self-healing recipe-rot · DRIFT DETECTION (datasketch MinHash)** [VERIFIED NEXT-LEVEL.md:229-235, datasketch MIT, https://github.com/ekzhu/datasketch] **+ AUTO-RESYNTHESIS (Crawl4AI generate_schema)** [VERIFIED NEXT-LEVEL.md:237-243, Crawl4AI Apache-2.0, https://github.com/unclecode/crawl4ai] — ante drift o sitio JS-only, regenerar un field_map CSS/XPath reusable UNA vez (LLM one-time, runtime determinista EUR0) y re-verificar por el harness existente; **executable-field-map-interpreter — parsel** [VERIFIED NEXT-LEVEL.md:261-266, parsel BSD-3-Clause, https://github.com/scrapy/parsel] hace ese field_map un programa YAML replayable. extruct es el lift inmediato de recall; Crawl4AI+parsel es la corona self-healing de la cola-larga.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f22"></a>
### Faceta 22 · Contrato strangler de connector & roster de plataformas (_core)

> **Grupo:** Identidad de entidad, geo & cross-border  ·  **Resuelve:** MP-plataforma (-> 23)  ·  **Estado:** CERRABLE
>
> **Costura —** PlatformSpec (contract.py:14) NO lleva country_code [VERIFIED ausencia]: su cdp_code(:24) es precomputado/pasado-in, no puede enrutar el mint por pais (faceta 23). El roster esta hoy implicito en codigo de connector, no como dato del pack. El body SQL (persistence.py) ya es country-blind (province_code NULL :30).
>
> **Fix —** Anadir country_code:str a PlatformSpec e hilarlo a mint_code(...,country_code=CC) upstream. Roster como dato del pack: countries/<CC>/_pack.py declara platform_roster; cada connector reusa _core.ensure_platform_entity con su country_code. El SQL no cambia un byte.
>
> **Adversarial —** Sin country_code, un pais #2 que no reuse _core re-introduce el drift de 29 copias; y el cdp_code del spec defaultea a CDP-ES- para plataformas extranjeras (corrupcion de identidad). Pan-EU cross-market con canonical_key country-blind (faceta 24) -> mismo base32, prefijo {cc} divergente -> 2 codigos por entidad.
>
> **Sellado —** Forma-unica (cada connector escribe filas identicas a su copia legacy, golden row-diff) + inyeccion (conflict_refresh no-allowlisted RAISE en _entity_sql:52) + pais (country_code=DE rutea a CDP-DE-, ES byte-identico). Sello: una forma SQL para N plataformas, roster=dato del pack, cada connector con su country_code, cero drift.
>
> **Herramienta NEXT-LEVEL —** Pydantic (MIT, EUR0) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:71,587] — country-pack (roster+PlatformSpec set) como esquema tipado con validators (country_code requerido, defense_tier/source_group in ENUMs 0016) + test CI de biyeccion 0 UNMAPPED/0 ORPHAN: onboarding incompleto = build ROJO.

#### (a) code_hints verificados
- [VERIFIED pipeline/platform/_core/contract.py:14-15] `@dataclass(frozen=True) class PlatformSpec` — absorbe las constantes per-modulo que 29 copias hand-rolled de `ensure_platform_entity` hardcodeaban (docstring :3-6).
- [VERIFIED contract.py:24] `cdp_code: str` (precomputado, determinista — pasado IN, NO minteado aqui); [VERIFIED :40] `defense_tier: str|None=None`; [:41] `source_group`; [:42] `role`; [:43] `family`; [:47] `conflict_refresh: tuple[str,...]=()`.
- [VERIFIED AUSENCIA contract.py:14-48] NO existe campo `country_code` en ningun punto de PlatformSpec (lei las 48 lineas).
- [VERIFIED _core/persistence.py:20] `_ALLOWED_REFRESH = ("is_tier1","website_waf","defense_tier","source_group","role","kind","legal_name")`.
- [VERIFIED persistence.py:26] `_ENTITY_INSERT` superset-INSERT lista toda columna opcional, NULL-bound cuando el spec la omite (:24-25,:30); [VERIFIED :48-54] `_entity_sql` valida `conflict_refresh` contra el allowlist (injection-safe); [VERIFIED :57] `ensure_platform_entity`.
- [VERIFIED migrations/0016_tiering_groups.sql:6-12] `defense_tier` ENUM t0_open..t4_spend_gated; [:17-29] `source_group` ENUM (11 valores); [:34] `entity_role` ENUM.

#### (b) Mecanismo al atomo
`PlatformSpec` parametriza el UNICO `ensure_platform_entity` — un spec por plataforma alimenta un solo body, matando el drift de 29 copias que la auditoria P05 marco (docstring :3-6). Los campos mapean 1:1 a las columnas que las copias legacy escribian (entity/entity_source/platform_meta). El superset-INSERT lista toda columna de clasificacion opcional y bindea NULL cuando el spec la omite (persistence :24-25) -> byte-for-byte la fila que la copia legacy escribia. Dos valores que las copias hardcodeaban como literales SQL (is_tier1, data_surface) pasan a bind params spec-driven para que un body sirva a toda plataforma (:5-7). El ON CONFLICT SET es per-spec via `conflict_refresh`, validado contra `_ALLOWED_REFRESH` antes de interpolar (:48-54) — el SET dinamico no puede inyectar. La taxonomia multi-eje (defense_tier/source_group/role/family, 0016) reemplaza el booleano plano is_tier1 por estructura real.

#### (c) Costura ES->generico + fix exacto
[VERIFIED AUSENCIA] `PlatformSpec` NO lleva `country_code` — su `cdp_code` (:24) esta precomputado y se pasa IN, asi que el spec no puede enrutar su mint por pais (ese mint vive en la faceta 23, los 31 hardcodes 'CDP-ES-'). **Fix:** anadir `country_code: str` a PlatformSpec e hilarlo al `mint_code(province_code, digest, country_code=CC)` upstream para que la identidad de plataforma rutee por pais. El roster (que formas conocidas operan + las nativas del pais sin equivalente ES) se vuelve DATO del pack (faceta 14): `countries/<CC>/_pack.py` declara `platform_roster`, y cada connector reusa `_core.ensure_platform_entity` con su country_code. El body SQL (persistence.py) no cambia un byte — ya es country-blind (`province_code` NULL-bound :30, el pais deriva del cdp_code).

#### (d) Riesgo adversarial concreto
[VERIFIED] PlatformSpec sin country_code -> un pais #2 que construya sus plataformas nativas SIN reusar _core re-introduce exactamente el drift de 29 copias que el strangler mato; y aun reusando _core, el `cdp_code` del spec debe minteerse upstream con el CC correcto (faceta 23) — ausente el campo, el mint defaultea a CDP-ES- para plataformas extranjeras (corrupcion silenciosa de identidad). DE/FR/IT/PT: un backend pan-EU (faceta 26) reusado cross-market con un canonical_key country-blind (faceta 24) produce el mismo base32 con prefijo {cc} divergente -> dos cdp_codes para una entidad canonica, rompiendo el invariante de codigo inmutable. Ruido: una entrada de roster `is_platform_like` pero no `sells_cars` (:37 NULL default) no debe mintarse como POS.

#### (e) Sellado + verificacion multi-via
1. **Forma unica**: cada `ensure_platform_entity` de un connector escribe filas identicas a su copia legacy (golden row-diff por spec).
2. **Inyeccion**: un `conflict_refresh` con columna no-allowlisted RAISE en `_entity_sql` (:52) — probado por test rojo.
3. **Pais**: afirmar que un PlatformSpec con country_code=DE rutea su mint a CDP-DE- y la entidad aterriza con el DE derivable del cdp_code; ES byte-identico. Sello = "una forma SQL para N plataformas, el roster es dato del pack, cada connector reusa _core con su country_code, cero drift".

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Pydantic** (MIT, EUR0) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:71,587 lic MIT]. *Guard de drift de registry/semilla como CONTRATO TIPADO*: modelar el country-pack (roster + registry + lock_key + el set de PlatformSpec) como un esquema Pydantic con validators cross-field (country_code requerido, defense_tier in el ENUM de 0016, source_group in ENUM, cdp_code casa CDP-<CC>-) y un test CI que asevera la biyeccion source_health<->registry<->roster (0 UNMAPPED / 0 ORPHAN) por pais activo — convirtiendo un hueco silencioso de onboarding en un build ROJO mecanico. Hoy el gap solo se ve en un --dry-run manual (scheduler.py:394); Pydantic hace del frozen-dataclass PlatformSpec un contrato validado y country-completo. Alternativas: jsonschema, Cerberus.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f23"></a>
### Faceta 23 · mint_code routing & los 31 hardcodes CDP-ES-

> **Grupo:** Identidad de entidad, geo & cross-border  ·  **Resuelve:** costura #1 / RIESGO 31 CDP-ES-  ·  **Estado:** CERRABLE
>
> **Costura —** El UNICO hogar del prefijo (mint_code, codes.py:44,53) ya es country-parametrico (default ES), pero 31 conectores *_wholesale hornean el literal f"CDP-ES-..." en vez de delegar en el helper [VERIFIED 31 mints, 0 usan mint_code]; y PlatformSpec NO lleva country_code [VERIFIED contract.py:14-48] -> el path de plataforma no puede enrutar su mint por pais.
>
> **Fix —** Importar mint_code en cada conector y reemplazar el f-string por mint_code(province_code=..., digest=digest, country_code=CC) (digest/_base32 identicos -> ES byte-identico, test_country_golden.py:173); anadir country_code:str a PlatformSpec (faceta 22) e hilarlo upstream; CC viaja en el CountryScrapePack (faceta 14). El SQL de persistence.py no cambia.
>
> **Adversarial —** Pais #2 que reusa los 31 conectores sin cablear mint_code mintaria CDP-ES- para SUS plataformas -> corrupcion silenciosa de identidad (entidad extranjera con prefijo ES). Cross-border: canonical_key country-blind (faceta 24) da el mismo base32 con prefijo {cc} divergente -> 2 cdp_codes por entidad (juntura faceta 26). El path por-dealer es seguro; el de plataforma NO.
>
> **Sellado —** grep-guard 0 ocurrencias de CDP-ES- literal en conectores (CI rojo ante f-string ES) + golden test_country_golden.py:173 verde (ES byte-identico, sin re-key de 431k) + pais (PlatformSpec country_code=DE rutea a CDP-DE-). Sello: canal de mint unico y parametrico, cero literal ES, ES byte-identico.
>
> **Herramienta NEXT-LEVEL —** Pydantic (MIT, EUR0) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:71,587] — PlatformSpec/CountryScrapePack como esquema tipado (country_code requerido, cdp_code casa ^CDP-<CC>-, ENUMs de 0016) + test CI grep-guard que falla rojo ante un f-string CDP-ES- literal: onboarding incompleto = build ROJO.

> **Procedencia honesta.** El lote de deep-dives `g*` colisiono `canonical_key` en este slot (23) con la faceta 24 (mismo `facet_name`, contenido casi identico). Las referencias cruzadas de la **faceta 22** asignan inequivocamente el slot 23 a *"el mint ... los 31 hardcodes `CDP-ES-`"*. Esta subseccion se **reconstruye desde la costura #1 [VERIFIED]** del cuerpo v1 + los anclajes `codes.py` que comparten las facetas 22/24/25 — contenido verificado, **no placeholder**.

#### (a) code_hints verificados
- [VERIFIED services/api/codes.py:44] `mint_code(*, province_code, digest, country_code="ES")` — el **UNICO hogar** del literal del prefijo.
- [VERIFIED codes.py:53] `return f"CDP-{country_code}-{province_code}-{_base32(digest)}"` — ya **country-parametrico** (default ES).
- [VERIFIED codes.py:62-65] `canonical_key` es country-blind: el pais NO entra al pre-image (no re-keya las 431k entidades).
- [VERIFIED pipeline/platform/*_wholesale.py (31 mints)] 31 lineas `return f"CDP-ES-{PROVINCE_SENTINEL}-{_base32(digest)}"`; **0** conectores importan/usan `mint_code` (importan `_base32`+`cdp_code` pero NO el helper).
- [VERIFIED tests/test_country_golden.py:173] `mint_code` default == ES literal byte-identico.
- [VERIFIED pipeline/platform/_core/contract.py:14-48] `PlatformSpec` **NO** lleva campo `country_code` (lei las 48 lineas) -> su `cdp_code` (:24) es precomputado/pasado-in, no puede enrutar el mint por pais.

#### (b) El mecanismo al atomo
`mint_code` compone el unico prefijo `CDP-{cc}-{prov}-{base32}`; el `digest`/`_base32` (Crockford) son **country-blind**, y el `country_code` ya viaja como parametro con default ES — la pieza CENTRAL es generica por diseno. La rotura esta **fuera** de `mint_code`: los **31 conectores de plataforma** no delegan en el helper, sino que **hornean el f-string literal `CDP-ES-`** cada uno. La identidad de una plataforma (su `cdp_code`) se computa upstream y se pasa al `PlatformSpec.cdp_code` ya-resuelto; sin `country_code` en el spec, no existe canal para enrutar ese mint por pais. El path **por-dealer** (que SI llama `mint_code`) es seguro; el path **de plataforma** no.

#### (c) Costura ES->generico + fix exacto
La costura es la **duplicacion del prefijo ES en 31 sitios** en vez de un unico canal parametrico. **Fix exacto:** (1) importar `mint_code` en cada conector y reemplazar el f-string por `mint_code(province_code=..., digest=digest, country_code=CC)`; el `digest`/`_base32` son identicos -> **ES byte-identico** (lo prueba `test_country_golden.py:173`). (2) Anadir `country_code: str` a `PlatformSpec` (faceta 22) e hilarlo al `mint_code(...)` upstream para que el `cdp_code` del spec rute por pais. (3) `CC` viaja en el `CountryScrapePack` (faceta 14)/`PlatformSpec`. El body SQL de `_core/persistence.py` no cambia un byte (`province_code` NULL-bound, el pais deriva del `cdp_code`).

#### (d) Riesgo adversarial concreto
Pais #2 que reusa estos 31 conectores **sin** cablear `mint_code` mintaria `CDP-ES-` para SUS plataformas -> **corrupcion silenciosa de identidad** (toda entidad extranjera con prefijo ES, indetectable hasta auditar). Cross-border: una entidad pan-EU con `canonical_key` country-blind (faceta 24) produce el **mismo `base32`** con prefijo `{cc}` divergente -> **2 `cdp_codes`** para una entidad canonica (juntura con la faceta 26 de gateways pan-EU). El path por-dealer es seguro; el de plataforma **NO**, y es exactamente el que un pais nuevo hereda.

#### (e) Sellado + verificacion multi-via
1. **grep-guard**: **0** ocurrencias del literal `CDP-ES-` en los conectores tras el fix (todos via `mint_code`), gate de CI que falla rojo ante un f-string ES desnudo.
2. **golden**: `test_country_golden.py:173` sigue verde (ES byte-identico) -> el fix no re-keya ninguna de las 431k entidades vivas.
3. **pais**: un `PlatformSpec` con `country_code=DE` rutea su mint a `CDP-DE-` y la entidad aterriza con el DE derivable del `cdp_code`. Sello = *"un unico canal de mint parametrico, cero literal ES en conectores, ES byte-identico"*.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Pydantic** (MIT, EUR0) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:71,587]. Modelar `PlatformSpec`/`CountryScrapePack` como esquema tipado con validators cross-field (`country_code` **requerido**, `cdp_code` casa `^CDP-<CC>-`, `defense_tier`/`source_group` en los ENUMs de `migrations/0016`) + un test CI grep-guard que falla el build si cualquier conector emite un f-string `CDP-ES-` literal -> **onboarding incompleto = build ROJO mecanico** en vez de corrupcion silenciosa. Es el mismo contrato tipado que eleva la faceta 22; aqui ata la **identidad de plataforma** a un canal verificado.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f24"></a>
### Faceta 24 · Identidad canonical_key: transliteracion & estabilidad cross-border

> **Grupo:** Identidad de entidad, geo & cross-border  ·  **Resuelve:** B5 / B8 / MP6 / MP8  ·  **Estado:** OPEN (identidad/transliteracion)
>
> **Costura —** codes.py:30 _normalize hace unicodedata.normalize('NFKD',t).encode('ascii','ignore') -> DESCARTA todo no-ASCII [VERIFIED codes.py:29-32]; canonical_key es country-blind por diseno (country no entra al pre-image) [VERIFIED codes.py:62-65]; el golden solo cubre 7 filas ASCII y nunca estresa no-ASCII [VERIFIED test_country_golden.py:54-69]; el mismo fold roto esta en codes.py:_normalize y pipeline/geo.py:_norm.
>
> **Fix —** Insertar transliteracion country-scoped (pack.normalize_policy) ANTES del fold: latino conserva el fold (byte-identico ES), no-latino via anyascii; orden romaji-de-fuente-primero (GeoNames asciiname/alternateNames) y solo si falta, anyascii algoritmico (evita Pinyin-sobre-japones, identidad inmutable); aplicar en codes.py:_normalize Y pipeline/geo.py:_norm.
>
> **Adversarial —** JP: 2 dealers name-only CJK distintos en un muni -> _normalize=='' -> key 'name:|{muni}' identica -> MASS FALSE DEDUP irreversible (1 cdp_code, entidad perdida); DE eszett 'Strasse' vs forma-eszett divergen y NO deduplican; pan-EU mismo-dominio en 2 paises -> mismo base32 con prefijo {cc} divergente -> 2 cdp_codes para 1 entidad (rompe invariante inmutable de gateways).
>
> **Sellado —** (a) palabra CJK y su half-width -> MISMO key; key(eszett)==key('Strasse'); ASCII ES byte-identico sobre 431k codes; (b) 2 dealers JP distintos name-only mismo muni -> keys DISTINTAS; (c) bucket union-find con vs sin transliteracion sobre muestra DE/JP -> conteo de entidades distintas SUBE (rompe el falso merge), contra oraculo de nombres crudos del test.
>
> **Herramienta NEXT-LEVEL —** anyascii (ISC, EUR0) https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:224] — transliteracion CPU pura, ISC (limpia, no GPL como unidecode); + GeoNames asciiname/alternateNames (CC-BY) romaji-de-fuente-primero [VERIFIED NEXT-LEVEL.md:327] para evitar Pinyin-sobre-japones; blocking language-neutral: datasketch MinHash-LSH+RapidFuzz [VERIFIED NEXT-LEVEL.md:535] y Splink Fellegi-Sunter [VERIFIED NEXT-LEVEL.md:401] como 2a via.

#### (a) code_hints [VERIFIED]
- [VERIFIED codes.py:29-32] `_normalize(text)`: `unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode('ascii')` seguido de `re.sub('[^a-z0-9]+', '', text.lower())`. El encode ascii-ignore DESCARTA todo caracter no-ASCII.
- [VERIFIED codes.py:56] `canonical_key(...)`; [VERIFIED codes.py:62-65] `country_code` se acepta pero DELIBERADAMENTE NO entra al pre-image (mezclarlo cambiaria cada sha256 y re-keyaria los 431k entities); [VERIFIED :72-75] rama particular (`particular:{plat}:{sid}`); [VERIFIED :76-87] rama domain (bare-host: strip scheme/www/path -> `domain:{host}` SOLO si host sin path); [VERIFIED :88-89] rama cif; [VERIFIED :92-96] rama name (`name:{norm}|{muni}{addr}` o `name:{norm}|p{prov}{addr}`).
- [VERIFIED test_country_golden.py:54-69] `_ES_GOLDEN` cubre las 7 ramas; [VERIFIED :103-119] test_canonical_key_is_country_blind prueba que el country no entra al pre-image. PERO las 7 filas son TODAS ASCII ('Talleres X', 'Garaje Y', 'ford.es', 'B12345678') -> el golden NUNCA estresa no-ASCII: la doble-falla CJK/sz es invisible al sello actual.

#### (b) Mecanismo al atomo
canonical_key es el pre-image INMUTABLE del dedup, deliberadamente country-blind (el country vive solo en el prefijo humano de mint_code, no en el hash) para NO re-keyar los 431k cdp_code vivos. Prioridad: particular > domain > cif > name|muni. `_normalize` es el UNICO punto que toca texto libre (name, address). El fold ASCII (`encode('ascii','ignore')`) es una linea que funciono para ES (Latin-1) porque ES fue el unico tenant y nunca se estreso con datos no-Latinos; NFKD descompone diacriticos latinos (a-acento -> a) que sobreviven como ASCII -> ES byte-identico. La falla es matematicamente IRREVERSIBLE: descartar bytes no se revierte, y el cdp_code resultante es INMUTABLE (sample-verify-delete no lo deshace).

#### (c) Costura ES->generico + fix exacto
La costura es codes.py:30. Fix: insertar transliteracion ANTES del fold, country-scoped via `pack.normalize_policy`: latino-con-diacriticos (ES/DE/FR/IT/PT) conserva el fold actual -> byte-identico; no-latino (JP/CJK, EL, BG/RU) transliteran via anyascii. MATIZ CRITICO (cross-link geo [VERIFIED NEXT-LEVEL.md:327]): el orden correcto es romaji-de-la-FUENTE primero (columna asciiname y alternateNames isolang=en de GeoNames), y SOLO si falta, transliteracion algoritmica anyascii — porque anyascii/ICU romanizan Han via Pinyin CHINO, lo cual es INCORRECTO para toponimos/nombres japoneses; mintear identidad japonesa mal-romanizada es inmutable. El mismo fix debe aplicarse en los DOS sitios que hoy hacen encode ascii-ignore: codes.py:_normalize (identity-path) y pipeline/geo.py:_norm (resolver).

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- JP/CJK: dos dealers name-only DISTINTOS en el mismo municipio, ambos con nombre 100% CJK -> `_normalize` devuelve '' para ambos -> key IDENTICA `name:|{muni}` -> MASS FALSE DEDUP: se funden en UN cdp_code, perdida silenciosa de una entidad real, irreversible.
- DE: 'Strasse' -> 'strasse' vs 'Strasze' (con eszett) -> 'strae' DIVERGEN -> NO deduplican (dos codigos para una entidad).
- Cross-border pan-EU: una entidad mismo-dominio descubierta en 2 paises produce el MISMO base32 (canonical_key country-blind) con prefijo {cc} divergente -> 2 cdp_codes para 1 entidad canonica -> rompe el invariante de codigo inmutable de los gateways pan-EU (faceta 26).
- Ruido: nombres mixtos latino+CJK colapsan parcialmente, generando keys casi-iguales que ni funden ni separan limpio.

#### (e) Sellado + verificacion multi-via
- (a) test: una palabra CJK y su forma half-width transliteran al MISMO key; key(eszett) == key('Strasse'); ASCII ES inalterado (golden byte-identico sobre los 431k cdp_code vivos).
- (b) adversarial: dataset de 2 dealers JP DISTINTOS name-only en el mismo muni -> deben producir keys DISTINTAS (no colapsar a una).
- (c) via independiente: comparar el bucket union-find resultante CON y SIN transliteracion sobre una muestra DE/JP — el conteo de entidades DISTINTAS debe SUBIR (se rompe el falso merge), verificado contra el oraculo de nombres crudos retenido solo en el test.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
[VERIFIED NEXT-LEVEL.md:224] `anyascii` (ISC, EUR0) — https://github.com/anyascii/anyascii. CPU puro, sin dependencias, ~200-500KB de tablas embebidas; ISC es comercial-limpia, MEJOR que unidecode (GPL, que contaminaria el servicio API publico). `_normalize` llama anyascii() bajo la rama de script seleccionada por pack.normalize_policy; ES byte-identico (ASCII pasa igual). MATIZ obligatorio [VERIFIED NEXT-LEVEL.md:327]: combinar con GeoNames asciiname/alternateNames (CC-BY) para romaji-de-fuente-PRIMERO en el identity-path, evitando el Pinyin-sobre-japones (identidad inmutable mal-romanizada). Para el blocking de dedup language-neutral que esta capa habilita: [VERIFIED NEXT-LEVEL.md:535] `datasketch` MinHash-LSH + RapidFuzz (retira el levenshtein SQL O(n^2)) y [VERIFIED NEXT-LEVEL.md:401] `Splink` (record linkage Fellegi-Sunter, MIT) como 2a via certificable.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f25"></a>
### Faceta 25 · Resolutor de provincia/region para el segmento {prov} del cdp_code

> **Grupo:** Identidad de entidad, geo & cross-border  ·  **Resuelve:** B9 / MP7  ·  **Estado:** CERRABLE (cross-ref Geo)
>
> **Costura —** No existe resolutor zip->region; una coincidencia ES (CP[:2]==provincia INE, recipe.py:38) hace de resolutor. Tres asunciones ES soldadas: zip[:2]==province, region es [0-9]{2} (_CDP_CODE_RE complete.py:89), set valido 01-52 (_PROVINCE_RE complete.py:73).
>
> **Fix —** pack.province_resolver (zip->subdivision primer-nivel: DE Bundesland/FR departement/IT sigla/PT distrito/JP prefecture) + pack.region_code_pattern + pack.valid_regions; ensanchar el segmento de provincia de _CDP_CODE_RE [0-9]{2}->clase de pack como SUPERSET ESTRICTO (ES [0-9]{2} byte-identico); _PROVINCE_RE->pack.valid_regions; mantener el sentinel nacional '00'; auditar el ancho del slot de 2-char por manifest.
>
> **Adversarial —** Bloqueo G1 duro para no-ES: Bundesland DE de 2-LETRAS (BW/BY) -> mint CDP-DE-BW-... rechazado por _CDP_CODE_RE [0-9]{2} -> toda entidad DE falla identidad; Corse FR 2A/2B rechazado; JP 7-digit/47 prefecturas sin mapeo 2-digit; un zip foraneo que aliase a un prefijo real 01-52 pasa por suerte -> dealer ES mal-ubicado sellado.
>
> **Sellado —** golden ES: zip[:2] resolver + regex ensanchado reproducen 431k codigos byte-identico; sanidad por pais: conteos/anchos casan autoridad ISO (DE16/FR101/IT107/JP47) + muestra de zips foraneos cruzada con 2a fuente; adversarial: alias-espurio-01-52 rechazado, region 2-letras/alfanumerica round-trip mientras ES [0-9]{2} sigue valido; manifest derivado de dato estandar, no a mano.
>
> **Herramienta NEXT-LEVEL —** pycountry (ISO 3166-1/-2 + ISO 4217, LGPL-2.1, https://github.com/pycountry/pycountry) [VERIFIED NEXT-LEVEL.md:530] — conteo/ancho de subdivisiones como dato -> manifest de sello por-pais, retira los sentinels [0-9]{2}/01-52 y el problema CHAR(2); alt iso3166 (MIT, NEXT-LEVEL.md:531); backbone zip->region de GeoNames admin1/2 (CC-BY 4.0, https://download.geonames.org/export/dump/) [VERIFIED NEXT-LEVEL.md:377].

#### (a) Verificacion de code_hints [VERIFIED]
- `services/api/codes.py:44` `mint_code(*, province_code, digest, country_code='ES')` -> `:53` `f"CDP-{country_code}-{province_code}-{_base32(digest)}"` — acepta CUALQUIER string `province_code`, SIN validacion, columna NOT NULL [VERIFIED].
- `pipeline/recipe.py:38` `"location": "listing.location {zip->province, city, street}"` — el field-map AS24 deriva provincia del zip [VERIFIED].
- `pipeline/complete.py:73` `_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")` — SOLO 01-52 (provincias INE espanolas) [VERIFIED].
- `pipeline/complete.py:83` `_NATIONAL_KINDS = frozenset({subasta,plataforma,oem_vo_portal,importador})` — entidades nacionales con province NULL + sentinel '00' en el codigo [VERIFIED].
- `pipeline/complete.py:89` `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — segmento de provincia `[0-9]{2}` DOS DIGITOS, ES soldado [VERIFIED].
- `pipeline/complete.py:142` `check_g1`: no-nacional ∧ (prov None ∨ ¬`_PROVINCE_RE`.match) -> `invalid_province_code`; `:145` ¬`_CDP_CODE_RE`.match -> `cdp_code_format_invalid` [VERIFIED].

#### (b) El mecanismo al atomo
`mint_code` exige un `province_code` de 2-char y lo hornea literal en el cdp_code. Hoy el valor sale GRATIS de una COINCIDENCIA ESPANOLA: los 2 primeros digitos del CP espanol == codigo INE de provincia (01-52). Asi `zip[:2]` ES el segmento de provincia — sin resolutor para ES. El gate G1 lo impone DOS veces: `_PROVINCE_RE` (solo 01-52) sobre la columna, y `_CDP_CODE_RE` (`[0-9]{2}`) sobre el string del codigo. Los kinds nacionales bypassean via el sentinel '00'. Toda la cadena — derivar, mintar, validar — asume en silencio el esquema INE de 2-digitos.

#### (c) Costura ES->generico
NO hay resolutor zip->region; hay una COINCIDENCIA ES haciendo de resolutor. Tres asunciones ES soldadas: (1) `zip[:2]==province` (derivacion `recipe.py:38`); (2) el codigo de region es exactamente 2 DIGITOS (`_CDP_CODE_RE [0-9]{2}`); (3) el set valido es 01-52 (`_PROVINCE_RE`). **Fix**: introducir un adaptador de pack `province_resolver: zip->region2` (DE PLZ->Bundesland, FR CP->departement, IT CAP->sigla provincia, PT->distrito, JP 〒->prefecture) y un pack `region_code_pattern` + `valid_regions`; ensanchar el segmento de provincia de `_CDP_CODE_RE` de `[0-9]{2}` a una clase suministrada por pack (ej. `[0-9A-Z]{2}`) como SUPERSET ESTRICTO para que ES `[0-9]{2}` quede byte-identico y golden-probado; `_PROVINCE_RE` pasa a `pack.valid_regions`. El sentinel nacional '00' queda universal. Critico: el ANCHO de 2-CHAR del slot debe auditarse — DE Kreis es 5-digit, JP postal 7-digit, FR ultramar '971'-'976' (3-digit) — 2 chars puede ser demasiado estrecho, asi que el resolutor mapea a la subdivision de PRIMER NIVEL (Bundesland/region/regione/distrito), no al prefijo postal crudo, y el manifest declara el ancho.

#### (d) Riesgo adversarial concreto
Esta faceta BLOQUEA DURO en G1 para todo pais no-ES:
- **DE**: los Bundeslander son codigos de 2-LETRAS (BW, BY, NW) -> `mint_code` emite `CDP-DE-BW-...` que `_CDP_CODE_RE [0-9]{2}` RECHAZA -> `cdp_code_format_invalid`, toda entidad alemana falla identidad.
- **FR**: Corse es 2A/2B (alfanumerico) -> mismo rechazo aunque FR mayormente cabe en departamentos 2-digit.
- **JP**: 7-digit 〒NNN-NNNN con 47 prefecturas sin mapeo a prefijo postal de 2-digit -> ningun segmento valido derivable.
- **IT**: el CAP no mapea a la sigla de provincia de 2-letras.
- Sin resolutor el scraper no puede emitir un {prov} valido y el drain se atasca en G1 (la clase "6o blocker oculto").
- **Ruido**: un zip extranjero malformado produce en silencio un prefijo 2-char erroneo que PASA `_PROVINCE_RE` por suerte (ej. '08' de un codigo foraneo) -> entidad mal-ubicada sellada como dealer valido de Barcelona.

#### (e) Sellado + verificacion multi-via
**Criterio**: cada pais emite un codigo de region de PRIMER NIVEL VALIDO en {prov} via un resolutor explicito, sin asuncion INE de 2-digitos, y ES queda byte-identico. **Multi-via**: (1) **test** — golden ES: `zip[:2]` resolver + `_PROVINCE_RE` + `_CDP_CODE_RE` reproducen los 431k codigos vivos byte-por-byte; el regex ensanchado sigue aceptando todo codigo ES vivo; (2) **sanidad por pais** — los CONTEOS de subdivisiones y los ANCHOS de codigo DE/FR/IT/PT/JP casan una autoridad independiente (16/101/107/set distrito/47), y una muestra de zips foraneos reales resuelve a la subdivision correcta cruzada con una 2a fuente; (3) **adversarial** — un zip foraneo que aliase a un prefijo espurio 01-52 debe ser RECHAZADO por el resolutor (no pasar por coincidencia), y una region de 2-letras/alfanumerica debe round-trip por el `_CDP_CODE_RE` ensanchado mientras los codigos ES `[0-9]{2}` siguen validos. El manifest de sello (geo_unit_level, ancho, set valido) se deriva del dataset estandar, no a mano.

#### (f) Herramienta NEXT-LEVEL (eleva a inalcanzable)
**pycountry (ISO 3166-1/-2 + ISO 4217 currency data)** — LGPL-2.1 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]. La mejora `ISO 3166-2 subdivision authority for the geo_unit grain, width, and per-country over-merge caps` (NEXT-LEVEL.md:527-533) vuelve DATA el conteo y el ancho-de-codigo de las subdivisiones de primer nivel de cada pais, alimentando un manifest de sello por-pais (geo_unit_level, geo_unit_width, set valido) — retirando directamente los sentinels ES `[0-9]{2}`/01-52 y el problema CHAR(2) (nombra explicitamente "DE Kreis 5-digit, FR overseas '971'-'976'"). Uso solo en build/config-time (no hot-path) -> LGPL es non-issue; alternativa estricta-permisiva `iso3166` (MIT) + JSON crudo Debian iso-codes (NEXT-LEVEL.md:531). El BACKBONE del mapeo zip->region (el lookup que corre el resolutor) se carga de **GeoNames** (admin1/admin2 codes + postal, CC-BY 4.0, https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377]) — pycountry valida/dimensiona el slot, GeoNames aporta el dato zip->subdivision. Juntos hacen el resolutor country-proof y auto-pineado.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f26"></a>
### Faceta 26 · Parametrizacion de market/tenant de gateways pan-EU (OEM)

> **Grupo:** Identidad de entidad, geo & cross-border  ·  **Resuelve:** B8 / MP8  ·  **Estado:** OPEN (cross-border identidad)
>
> **Costura —** Mercado clavado a ES por 3 mecanismos en gateways pan-EU sin cambiar de host: path /es/es [VERIFIED oem_toyota_lexus_wholesale.py:117-118], query market=ES + _MARKET_CONFIG country:ES [VERIFIED oem_nissan_mazda_honda_wholesale.py:146,:186], header x-country:es/x-tenant:ald [VERIFIED group_subastas_wholesale.py:40-41], hq_province INE soldado [VERIFIED group_rentacar_vo_wholesale.py:540,:739-788].
>
> **Fix —** Lift a pack: Toyota LIST_PATH+Accept-Language<-pack.api_locale (/de/de); Nissan market/country/language<-pack.market+pack.api_locale; Ayvens x-tenant/x-country<-pack.tenant/pack.market; rentacar hq_province<-adaptador zip->region (faceta 25), no INE soldado. Default ES byte-identico; el mismo gateway pan-EU sirve N mercados. PRE-REQUISITO: reparar canonical_key (faceta 24) para que la entidad cross-border colapse a 1 cdp_code estable antes de re-apuntar.
>
> **Adversarial —** Mismo dealer pan-EU via tenant ES y DE -> canonical_key country-blind da base32 igual con prefijo {cc} divergente -> 2 cdp_codes para 1 entidad, rompe inmutabilidad; doble conteo cross-tenant si opera en 2 mercados; Ayvens x-country:es = catalogo del OPERADOR (3.977) != 461 fisicos en ES [VERIFIED group_subastas:56-60] -> re-apuntar debe preservar semantica de tenant; gateway solo-UE no sirve a pais no-UE -> route-around a fuente local.
>
> **Sellado —** Gateway re-apuntado drena el mercado objetivo Y cada entidad pan-EU en >=2 mercados resuelve a 1 cdp_code estable. Multi-via: (1) pack.market='DE' -> Toyota /de/de, Nissan market=DE, Ayvens x-country:de, ES byte-identico; (2) mismo dealer via tenant ES+DE colapsa a 1 entidad (no 2 codigos); (3) aggregates.count por tenant [VERIFIED group_subastas:43-44] cuadra con VAM declared, doble conteo = REFUTED.
>
> **Herramienta NEXT-LEVEL —** Splink (MIT, EUR0) https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:401] -- probabilistic record linkage (Fellegi-Sunter) como 2a via certificable que colapsa una entidad pan-EU multi-tenant a 1 cdp_code estable; corre sobre el Postgres/DuckDB existente, sin GPU [VERIFIED :403]. Sello 2-via ortogonal: pyJedAI (Apache-2.0) [VERIFIED nombre/lic NEXT-LEVEL.md:66 tabla] como segundo motor ER independiente. La parametrizacion del tenant es config de connector; lo inalcanzable es la garantia de identidad cross-border.

#### (a)+(b) Mecanismo VERIFICADO al átomo
Backends pan-EU YA en el roster cuyo parámetro de mercado está clavado a ES por TRES mecanismos distintos (todos verificados), sin cambiar de host:
- **Path-embedded locale (Toyota/Lexus)**: `_BASE = "https://usc-webcomponents.toyota-europe.com"` [VERIFIED pipeline/platform/oem_toyota_lexus_wholesale.py:117] + `LIST_PATH = "/v1/api/usedcars/results/es/es"` [VERIFIED :118] — el segmento `/es/es` (país/locale) está soldado DENTRO del path; el backend es pan-EU (toyota-europe.com) pero el path fija ES. `Accept-Language: es-ES,es;q=0.9` [VERIFIED :141]. Endpoint declarado: `POST .../results/es/es?brand={toyota|lexus}` [VERIFIED :460].
- **Query-param market (Nissan)**: `TOKEN_URL = "...public-access-token?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm"` [VERIFIED oem_nissan_mazda_honda_wholesale.py:145-146] — `market=ES` es query param; `_MARKET_CONFIG = {"brand":"NISSAN","country":"ES","language":"es", ...}` [VERIFIED :186] viaja como variable GraphQL `marketConfig` [VERIFIED :166-180,:460,:467]. Gateway pan-EU: `apigateway-eu-prod.nissanpace.com` / `gq-eu-prod.nissanpace.com` [VERIFIED :145,:147]. Modelo de tenant MÁS puro: cambiar `market=ES`→`market=DE` y `country:"ES"`→`"DE"`.
- **Header tenant (Ayvens/subastas)**: `x-tenant: ald` + `x-country: es` [VERIFIED group_subastas_wholesale.py:40-41]; "x-country: es es el SPANISH Ayvens REMARKETING TENANT — its WHOLE catalog" [VERIFIED :41,:56]; gateway `api-carmarket.ayvens.com/graphql/saleevents` [VERIFIED :37], clasificado JSON_API en el governor [VERIFIED pipeline/engine/governor.py:140]. Scope tenant deliberado: x-country:es = catálogo completo del operador español (3.977 lots), NO un filtro per-lot saleEventCountry (~461 físicos) [VERIFIED :56-60].
- **HQ-province INE (rentacar_vo)**: `hq_province: str  # INE province of the registered HQ` [VERIFIED group_rentacar_vo_wholesale.py:540], con códigos INE hardcodeados (08/07/03/12/28...) [VERIFIED :739-788] y paths `/es/` (athlon, northgate) [VERIFIED :460,:666,:788].

#### (b) Costura ES→genérico (fix exacto)
A diferencia de AS24 (faceta 20, swap de DOMINIO), aquí el mercado se re-apunta por PARÁMETRO sin cambiar de host. Fix por mecanismo, lift a pack: Toyota `LIST_PATH`+`Accept-Language`←`pack.api_locale` → `/{lang}/{country}` (`/de/de`); Nissan `market`/`country`/`language` de `_MARKET_CONFIG`/`TOKEN_URL`←`pack.market`+`pack.api_locale`; Ayvens `x-tenant`/`x-country`←`pack.tenant`/`pack.market`; rentacar `hq_province`←adaptador zip→region del país (faceta 25), no INE soldado. Default ES byte-idéntico cuando el pack es ES; el host pan-EU NO cambia → el mismo gateway sirve N mercados. PRE-REQUISITO: reparar `canonical_key` (faceta 24) para que la entidad cross-border colapse a 1 cdp_code estable antes de re-apuntar.

#### (c) Riesgo adversarial concreto
- **Identidad cross-border inestable (riesgo central)**: el MISMO dealer pan-EU descubierto vía dos tenants (Toyota `/es/es` Y `/de/de`, o Nissan `market=ES` Y `market=DE`) es UNA entidad física, pero `canonical_key` es country-blind (faceta 24) → mismo base32 con prefijo `{cc}` divergente → 2 cdp_codes para 1 entidad canónica [VERIFIED adversarial_risk facet], rompiendo el invariante de código inmutable de los gateways pan-EU.
- **Doble conteo**: un gateway drenado con x-country:es Y x-country:de para un dealer que opera en ambos mercados cuenta su stock dos veces salvo dedup cross-tenant.
- **Scope tenant vs físico**: Ayvens documenta x-country:es = catálogo del OPERADOR español (3.977) ≠ ~461 coches físicamente en España [VERIFIED group_subastas:56-60]; re-apuntar a DE debe preservar la semántica de TENANT, no de geo física, o el denominador del país se desalinea.
- **No-UE**: un gateway que solo expone mercados UE (toyota-europe) no sirve a un país no-UE → el route-around (faceta 13) debe saltar a la fuente local.

#### (d) Sellado + verificación multi-vía
- **Sello**: el gateway re-apuntado drena el mercado del país OBJETIVO con su tenant param Y cada entidad pan-EU descubierta en ≥2 mercados resuelve a UN cdp_code estable.
- **Vía 1 (test)**: con `pack.market="DE"`, afirmar que Toyota pide `/de/de`, Nissan `market=DE`, Ayvens `x-country:de`; ES byte-idéntico.
- **Vía 2 (cross-border identity)**: inyectar el mismo dealer pan-EU vía tenant ES y tenant DE → debe colapsar a 1 entidad canónica (no 2 cdp_codes divergentes).
- **Vía 3 (denominador)**: el `aggregates.count` del gateway (Ayvens `LoadLots { aggregates{count} }` [VERIFIED group_subastas:43-44]) por tenant cuadra con el VAM declared; doble conteo cross-tenant = REFUTED.

#### (e) Herramienta NEXT-LEVEL (eleva a nivel inalcanzable)
El núcleo inalcanzable de esta faceta es la ESTABILIDAD DE IDENTIDAD cross-border de una entidad vista por N tenants (la parametrización del tenant en sí es config de connector, no requiere lib):
- **Splink (MIT, €0)** — https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:401]. Probabilistic record linkage (Fellegi-Sunter aprendido) como la 2a vía CERTIFICABLE que reconoce "este dealer Toyota-ES y este Toyota-DE son la MISMA entidad cross-border" y la colapsa a un cdp_code estable. Corre sobre el Postgres existente o DuckDB (1M registros/min en portátil), sin GPU [VERIFIED NEXT-LEVEL.md:403]. Es el rigor que ningún union-find determinista con block-keys exactas alcanza para entidades pan-EU multi-mercado.
- **pyJedAI (Apache-2.0, €0)** — [VERIFIED nombre+licencia NEXT-LEVEL.md:66 tabla resumen] como "independent second ER path for 2-via seal cert": el sello "1 entidad, 1 código" se certifica por DOS motores ER ortogonales, no por uno. (URL en la sección de detalle identity-vehicle, no transcrita aquí — no fabricada.)
Lo inalcanzable: garantizar estadísticamente que el re-apuntado multi-mercado no fragmenta ni funde identidades — Splink (+pyJedAI como 2a vía) es esa garantía.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f27"></a>
### Faceta 27 · Normalizacion de recetas runtime Tier-1 (milanuncios -> harness)

> **Grupo:** Receta como activo & cobertura  ·  **Resuelve:** B10 / B11 / RIESGO runtime  ·  **Estado:** CERRABLE (higiene)
>
> **Costura —** milanuncios_camoufox.py es un script suelto asyncio.run(main()) (:42 [VERIFIED]) FUERA del esquema Recipe/harness, con locale='es-ES'+os='windows' soldados (:5), dominio www.milanuncios.com (:7), selectores ES article.ma-AdCardV2 (:19) y slug coches-de-segunda-mano (:11), regex precio '([\d.]+)\s*€' con € soldado (:28) y combustible ES (:31), y json.dump a 'mn_cars_final.json' (:37) que VIOLA sample-verify-delete. No pasa por decide_status/VAM ni RecipeRunner.replay.
>
> **Fix —** Convertir el script en Recipe v2 bajo countries/<CC>/_recipes_runtime/: 1) Transport(engine=camoufox|patchright, base_url/locale del pack); 2) Parsing(engine=rendered_dom|css, field_map) con selectores declarativos y moneda/separadores del pack de moneda (faceta 28); 3) correr por RecipeHarness (sample-verify-delete) en vez de json.dump -> muestra verificada por VAM y dropeada, cero fichero local; 4) generalizar el patron para que el PerimeterX de otro pais sea receta pack-declarada, no script nuevo.
>
> **Adversarial —** El equivalente PerimeterX de DE viviria como otro script ES-shaped con locale='es-ES' -> navegador espanol sobre host aleman (tell de geo/locale). json.dump (:37) persiste crudo -> a escala el disco se llena y el mandato no-retencion se rompe en silencio. Selectores/regex ES (coches-de-segunda-mano, article.ma-AdCardV2, [\d.]+€, diesel|gasolina) no casan otro DOM/idioma -> 0 cards -> muestra vacia. Sin replay/VAM una pagina de bloqueo PerimeterX a 0 cards se confunde con dealer vacio. milanuncios HOY esta bloqueado (source_fallback.py:83-85): la receta debe escalar a patchright o quedar FAILED honesto, nunca sellar basura.
>
> **Sellado —** Multi-via: (1) replay+delete — la receta bajo schema replay desde YAML y pasa sample-verify-delete (parse_loss==0, VAM no-REFUTED) con CERO fichero local (assert mn_cars_final.json nunca creado); (2) adversarial generico — locale/os/selectores en el pack, sitio PerimeterX no-ES es receta pack-declarada no script, gate antidetect CreepJS certifica la huella antes de sellar; (3) VAM ortogonal — el harness sella la receta runtime por el mismo quorum declared/fetched/parsed que las Tier-0, la ruta runtime no esta exenta del oraculo de conteo.
>
> **Herramienta NEXT-LEVEL —** Crawl4AI JsonCssExtractionStrategy.generate_schema (Apache-2.0) — https://github.com/unclecode/crawl4ai — [VERIFIED en NEXT-LEVEL.md:237-243, lic Apache-2.0 :240]. AUTO-RESYNTHESIS: regenera el field_map una vez desde un sample fresco (LLM one-time, extraccion runtime determinista sin LLM), re-verifica con el harness y re-commitea -> convierte el script hand-rolled con selectores inline en receta schema-driven regenerable en drift. Complementos: parsel (BSD-3-Clause, :261-267) interpreta el field_map como DSL; patchright-python (Apache-2.0, :253-259) mina la clearance de milanuncios donde camoufox/nodriver cayeron, con licencia limpia.

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/platform/_recipes_runtime/milanuncios_camoufox.py`** [VERIFIED leido entero, 43 lineas]: es un **script suelto** `asyncio.run(main())` (`:42`), NO un asset bajo `Recipe`/`harness`. No importa `pipeline.recipe_schema` ni `recipe_harness`.
- **`:5`** [VERIFIED]: `async with AsyncCamoufox(headless=True, os="windows", locale="es-ES", geoip=False, humanize=True)` — **locale ES + os soldados**.
- **`:7`** [VERIFIED]: `await page.goto("https://www.milanuncios.com/", ...)` — dominio ES soldado.
- **`:11`** [VERIFIED]: selector ES `'a[href*="coches-de-segunda-mano"]'` (el slug de stock espanol).
- **`:19,:22-36`** [VERIFIED]: `page.evaluate` con selectores ES soldados `article.ma-AdCardV2`, regex de precio `([\d.]+)\s*€` (`:28`, **simbolo € y campo soldados**), regex de combustible ES `diesel|gasolina|h[íi]brido|el[ée]ctrico|gas` (`:31`).
- **`:37`** [VERIFIED]: `json.dump(cars, open("mn_cars_final.json","w",encoding="utf-8"), ...)` — **escribe crudo a un archivo local**, lo que **VIOLA el mandato sample-verify-delete** (ningun crudo debe persistir a disco; faceta 16). No pasa por `decide_status`/VAM ni por `RecipeRunner.replay`.
- **Contexto cross-faceta** [VERIFIED]: `source_fallback.py:83-85` marca milanuncios como `HARDEST (PerimeterX press-and-hold): free browser vías exhausted (nodriver+camoufox+CDP hold all blocked) — route AROUND it` — es decir, este script runtime **hoy esta bloqueado** y la cobertura se cierra por route-around (faceta 13).

#### (b) El mecanismo al atomo
La faceta trae las **recetas runtime sueltas** (scripts camoufox por-plataforma que resuelven en navegador real y extraen en-DOM) bajo el contrato `Recipe v2 + harness`. Atomo a atomo del script actual:
1. **Transporte Tier-1**: `AsyncCamoufox(headless, os, locale, geoip, humanize)` + navegacion + `wait_for_timeout` + scroll-loop para cargar todas las cards (`:16-21`). Esto es la mitad-transporte de una receta (engine camoufox, params de humanizacion).
2. **Extraccion en-DOM**: `page.evaluate` devuelve cards parseadas con selectores+regex inline (`:22-36`). Esto es la mitad-parsing (un `field_map` sobre el DOM renderizado).
3. **Persistencia**: `json.dump` a fichero local (`:37`). Esto DEBE ser sample-verify-delete: extraer k~3-5, verificar por VAM, **dropear la muestra** (sin crudo a disco).
El problema: las tres mitades estan hard-coded ES y sueltas; ninguna es declarativa, sellable ni replayable. El equivalente PerimeterX de OTRO pais hoy seria **otro script ES-shaped** copiado.

#### (c) La costura ES->generico
Convertir el script en un `Recipe v2` bajo `countries/<CC>/_recipes_runtime/`:
1. **Transport declarativo**: `Transport(engine="camoufox"|"patchright", base_url=pack.base_url, locale=pack.accept_language, humanize=...)` — locale/os/dominio salen del pack, no soldados.
2. **Parsing declarativo**: los selectores `article.ma-AdCardV2` + regex de precio/combustible pasan a un `Parsing(engine="rendered_dom"|"css", field_map={...})` interpretable; el simbolo de moneda € + separadores salen del pack de moneda (faceta 28), no `[\d.]+\s*€` soldado.
3. **Harness en vez de json.dump**: correr por `RecipeHarness` (sample-verify-delete) — la muestra se verifica por VAM y se **dropea**; cero `mn_cars_final.json`. La receta se vuelve sellable (`decide_status`) y replayable (`RecipeRunner.replay`).
4. **Relocalizacion + generalizacion**: vive en `countries/ES/_recipes_runtime/`; el patron se generaliza para que el PerimeterX de DE/FR sea una receta declarada en SU pack, no un script nuevo.

#### (d) Riesgo adversarial concreto (DE/FR/IT/PT/no-UE/ruido)
- **Parche no generalizado**: el equivalente PerimeterX de DE (p.ej. mobile.de si virara a press-and-hold) viviria como OTRO script ES-shaped con `locale='es-ES'` -> anuncia navegador espanol sobre host aleman (tell de geo/locale, conecta con faceta 3).
- **Viola sample-verify-delete**: `json.dump` a `mn_cars_final.json` (`:37`) persiste crudo; a escala multi-pais x multi-plataforma, el disco se llena y el mandato de no-retencion se rompe en silencio.
- **Selectores/regex ES soldados**: `coches-de-segunda-mano` (`:11`), `article.ma-AdCardV2` (`:19`), `([\d.]+)\s*€` (`:28`), `diesel|gasolina|...` (`:31`) no casan el DOM/idioma de otro pais -> 0 cards -> muestra vacia.
- **Sin replay/VAM**: una pagina de bloqueo PerimeterX localizada que el script "parsee" a 0 cards no se distingue de un dealer vacio; sin VAM ortogonal no hay sello honesto.
- **Ruido cross-faceta**: milanuncios HOY esta bloqueado (`source_fallback.py:83-85`) — la receta runtime debe poder ESCALAR a patchright (Chrome-shaped) o quedar en FAILED honesto + route-around, nunca sellar basura.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (replay + delete):** la receta milanuncios, ya bajo schema, replay desde YAML y pasa sample-verify-delete (`parse_loss==0`, VAM no-REFUTED) con **CERO fichero local** (assert: `mn_cars_final.json` nunca se crea).
- **Via 2 (adversarial generico):** locale/os/selectores movidos al pack; un sitio PerimeterX no-ES es una receta pack-declarada, no un script nuevo; el gate antidetect (CreepJS) certifica la huella camoufox/patchright antes de sellar.
- **Via 3 (VAM ortogonal):** el harness sella la receta runtime por el MISMO quorum `declared/fetched/parsed` que las recetas Tier-0 — la ruta runtime no esta exenta del oraculo de conteo independiente. Sellado = 3 vias verdes + la receta viviendo en `countries/<CC>/_recipes_runtime/`.

#### (f) Herramienta NEXT-LEVEL que lo eleva a nivel inalcanzable
**Crawl4AI `JsonCssExtractionStrategy.generate_schema`** (Apache-2.0) — `self-healing recipe-rot · AUTO-RESYNTHESIS` (NEXT-LEVEL.md:237-243 [VERIFIED]): regenera el `field_map` UNA vez desde un sample fresco (un LLM emite un schema CSS/XPath **reusable**; coste LLM one-time, **extraccion deterministica en runtime SIN LLM**), re-verifica con el harness sample-verify-delete existente y re-commitea la receta. Es exactamente lo que convierte el script milanuncios hand-rolled (selectores `article.ma-AdCardV2` inline) en una receta schema-driven, regenerable cuando milanuncios rota su DOM, sin reescribir el script a mano. `Escala a Claude (capa-3) SOLO si la re-sintesis no alcanza parse_loss==0`. URL: https://github.com/unclecode/crawl4ai — Apache-2.0 [VERIFIED en NEXT-LEVEL.md:240 y tabla :28]. **Complementos:** (1) **parsel** (BSD-3-Clause, :261-267) interpreta el field_map resultante como DSL sobre el DOM renderizado (cero Python por fuente); (2) **patchright-python** (Apache-2.0, :253-259) es el engine Chrome-shaped que puede minar la clearance de milanuncios donde camoufox/nodriver cayeron (`source_fallback.py:83-85`), bajo licencia limpia.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f28"></a>
### Faceta 28 · Pack de moneda & formato numerico de parsing

> **Grupo:** Moneda & formato numerico  ·  **Resuelve:** B10 / MP10  ·  **Estado:** CERRABLE
>
> **Costura —** La costura cruza 4+ sitios divergentes: (1) milanuncios_camoufox.py:28 € + [\d.] soldados; (2) recipe_extract_web.py:32 _COUNT_HINT sin-millares; (3) recipe_extract_web.py:79 descarta priceCurrency; (4) price_sanity.py:49 PRICE_MAX EUR-calibrado. recipe_schema.py no tiene campo currency [VERIFIED 0 matches]. Fix: centralizar parseo en parse_money(text, LocaleProfile) guiado por moneda+formato del pack, anadir currency_code al contrato de vehiculo, PRICE_MAX per-currency. Default ES = € + techo EUR byte-identico. Distinto de faceta 21: aquello es URLs, esto es VALORES.
>
> **Fix —** (1) Introducir parse_money(text, locale_profile)->(amount, currency_code); rutear el rung web/microdata (recipe_extract_web.py:104/79) y los runtime recipes (milanuncios_camoufox.py:28) por el; borrar el regex € ad-hoc y los _to_float divergentes. (2) Anadir currency_code al contrato CanonicalVehicle/Recipe (hoy price float pelado [VERIFIED recipe_schema.py sin campo currency]); capturarlo del priceCurrency JSON-LD (recipe_extract_web.py:79). (3) Sustituir _COUNT_HINT \d{1,5} (recipe_extract_web.py:32) por parse numerico locale-aware: '1.234 Fahrzeuge'->1234 no 234. (4) PRICE_MAX per-currency en el pack (price_sanity.py:49) -> un coche JPY normal no cae por el techo EUR. (5) Parametrizar el regex de fuel (milanuncios_camoufox.py:31) por pack de idioma.
>
> **Adversarial —** 'DE 1.234 Fahrzeuge': o no casa palabras ES o \d{1,5} lee 234 (mis-count declared -> VAM faceta 18). 'ES/DE 1.234,56' por [\d.] (milanuncios:28) -> '1.234' ambiguo; FR '1 234,56' NBSP no casa nada. MXN '1,234.56' por parser coma-millares -> 1.23456 (~1000x corrupcion) que pasa sanity como float valido: SILENCIOSO. ¥/MXN como € corrompe price_sanity: coche JPY normal excede PRICE_MAX=5_000_000 EUR y se descarta (B3 CRITICAL). Fuel ES (milanuncios:31) no casa otro idioma. No-UE peor: JP/MX invierten separador + cambian simbolo + magnitud.
>
> **Sellado —** Sellado cuando: (a) golden 'MX 1,234.56'==1234.56, 'ES 1.234,56'==1234.56, 'FR 1 234,56'==1234.56, 'JP ¥1,234,000'==1234000 con currency_code capturado; (b) conteo declarado parsea bajo cada separador de millares; (c) precio JPY normal sobrevive sanitize_price bajo techo JPY mientras junk EUR sigue rechazado (ES byte-identico); (d) ningun precio fluye sin currency_code. Multi-via: golden per-locale; adversarial (property-based: parse_money idempotente, nunca off-by-1000); via independiente (monto vs priceCurrency JSON-LD que recipe_extract_web.py:79 descarta -> texto visible vs metadato -> REFUTED ante mismatch).
>
> **Herramienta NEXT-LEVEL —** Directa: locale-money-correctness price-parser CLDR [VERIFIED NEXT-LEVEL.md:213-219, price-parser BSD-3-Clause, https://github.com/scrapinghub/price-parser] -parse_money(text,LocaleProfile) sobre price-parser + Babel (CLDR), anade currency_code, rutea recipe_extract_web.py:104, borra _to_float divergentes. Re-afirmada: Currency-correct pricing price-parser + Babel/py-moneyed [VERIFIED :503-509] -PRICE_MAX per-currency, moneda en block-key Signal-B, assert same-currency antes del ±2%. Adversarial: Hypothesis [VERIFIED :317-322, MPL-2.0, https://github.com/HypothesisWorks/hypothesis] minimiza al menor precio MX que corrompe 1000x. EUR0 pure-Python offline (CLDR en Babel, sin FX, comparaciones intra-moneda).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/platform/_recipes_runtime/milanuncios_camoufox.py:28` `price_eur:(t.match(/([\d.]+)\s*€/)||[])[1]||null,` — **simbolo € Y nombre de campo `price_eur` soldados**, y la clase `[\d.]` **no maneja coma-decimal** [VERIFIED]; fuel ES `:31` `/\b(diesel|gasolina|h[íi]brido|el[ée]ctrico|gas)\b/i`; ademas `json.dump` a archivo local (`:37`) — viola sample-verify-delete (toca faceta 27).
- `pipeline/recipe_extract_web.py:32` `_COUNT_HINT = r'(\d{1,5})...'` — `\d{1,5}` **no maneja millares**: "1.234"->casa "234" [VERIFIED].
- `pipeline/price_sanity.py:49` `PRICE_MAX = 5_000_000`, **EUR-calibrado explicito** (docstring 4-13: "real used-market max ~€3.6M Bugatti Chiron"); `sanitize_price` (`:56-66`) -> None si `<=0 or >PRICE_MAX`; KM_MAX/YEAR_MIN tambien. Todo el modulo es EUR-shaped.
- `pipeline/recipe_schema.py`: grep `currency|currency_code|price_eur` -> **0 matches [VERIFIED]** — el schema de receta **no tiene dimension de moneda**; el precio es float pelado.
- `recipe_extract_web.py:79/81`: `offers.get("price")` extraido, `priceCurrency` **DESCARTADO** [VERIFIED].

#### (b) Mecanismo al atomo
Parsing del VALOR numerico por pais: simbolo+campo de moneda (€/`price_eur` -> ¥/MXN/£) y separadores de millar/decimal (ES/DE `1.234,56` vs FR `1 234,56` vs JP/US `1,234.56`) tanto en el precio como en el conteo declarado. **Distinto de faceta 21** (keywords de descubrimiento): aquello interpreta URLs; esto interpreta VALORES. Hoy la extraccion de precio es un regex por-fuente (`([\d.]+)\s*€`, `milanuncios_camoufox.py:28`) que hardcodea el simbolo € y la clase `[\d.]` (sin coma-decimal), el regex de conteo (`\d{1,5}`) ignora millares, el techo de sanity (`PRICE_MAX=5_000_000`) es magnitud-EUR, y el schema de receta no lleva moneda (precio = float pelado).

#### (c) Costura ES->generico
La costura cruza 4+ sitios divergentes: (1) `milanuncios_camoufox.py:28` € + `[\d.]` soldados; (2) `recipe_extract_web.py:32` `_COUNT_HINT` sin-millares; (3) `recipe_extract_web.py:79` descarta `priceCurrency`; (4) `price_sanity.py:49` `PRICE_MAX` EUR-calibrado. Fix: **centralizar TODO parseo de precio/numero en un `parse_money(text, LocaleProfile)`** guiado por la moneda + formato-numerico del pack, **anadir `currency_code` al contrato de vehiculo**, y hacer `PRICE_MAX` per-currency. Default ES = € + techo EUR de hoy, byte-identico.

#### (d) Riesgo adversarial
- "DE 1.234 Fahrzeuge" o no casa las palabras ES o `\d{1,5}` lee **234** (mis-count del declared -> VAM degrada, faceta 18).
- Precio DE/ES "1.234,56" por el regex `[\d.]` (`milanuncios:28`) -> "1.234" -> 1.234 o 1234 ambiguo; FR "1 234,56" (NBSP millares) **no casa nada**.
- MXN "1,234.56" por un parser que asume coma-millares -> **1.23456 (~1000x corrupcion)** que aun pasa sanity como float valido — **SILENCIOSO**, indetectable por los gates actuales.
- ¥/MXN parseado como € corrompe `price_sanity`: un coche JPY normal **excede `PRICE_MAX=5_000_000` EUR y se descarta** (B3 CRITICAL); un precio MXN lee como junk EUR 1000x. El regex de fuel ES (`milanuncios:31`) no casa ningun otro idioma. No-UE es lo peor: JP/MX **invierten** la convencion de separador Y cambian simbolo Y magnitud.

#### (e) Sellado + verificacion multi-via
- **Sellado cuando**: (a) golden — `'MX 1,234.56'==1234.56`, `'ES 1.234,56'==1234.56`, `'FR 1 234,56'==1234.56`, `'JP ¥1,234,000'==1234000`, cada uno con `currency_code` capturado; (b) el conteo declarado parsea correcto bajo el separador de millares de cada locale; (c) un precio JPY normal **sobrevive** `sanitize_price` bajo un techo JPY mientras el junk EUR sigue rechazado (ES byte-identico); (d) ningun precio fluye sin `currency_code`.
- **Multi-via**: golden per-locale; adversarial (property-based: un generador sintetiza separadores mixtos/ambiguos y afirma que `parse_money` es idempotente y nunca off-by-1000); via independiente (el monto parseado cruzado contra el `priceCurrency` del JSON-LD que `recipe_extract_web.py:79` hoy DESCARTA -> dos familias: texto visible vs metadato schema.org -> REFUTED ante mismatch).

#### (f) Herramienta NEXT-LEVEL
DIRECTA: **locale-money-correctness — parser de precio+moneda CLDR (price-parser)** [VERIFIED NEXT-LEVEL.md:213-219, price-parser BSD-3-Clause, https://github.com/scrapinghub/price-parser] — centralizar todo parseo en `parse_money(text, LocaleProfile)` sobre price-parser (extrae monto + simbolo/codigo de divisa de texto crudo, maneja millar/decimal por locale) respaldado por **Babel** (CLDR); anadir `currency_code` al contrato; rutear el rung web (`recipe_extract_web.py:104`) y borrar los `_to_float` divergentes. RE-AFIRMADA para el techo: **Currency-correct pricing: price-parser at the boundary + Babel/py-moneyed for per-currency ceilings** [VERIFIED NEXT-LEVEL.md:503-509, price-parser BSD-3-Clause + Babel + py-moneyed] — `PRICE_MAX` per-currency en el CountryProfile, moneda en la clave de bloque Signal-B, assert same-currency antes del ±2%. Cobertura adversarial: **property-based-recipe-fuzzing — Hypothesis** [VERIFIED NEXT-LEVEL.md:317-322, Hypothesis MPL-2.0, https://github.com/HypothesisWorks/hypothesis] minimiza al menor precio MX que se corrompe 1000x y lo congela como regression-fixture. Todo EUR0, pure-Python, offline (CLDR viene con Babel — sin servicio FX, las comparaciones son intra-moneda por construccion).

[↑ Indice de facetas](#indice-facetas)

---

<a id="f29"></a>
### Faceta 29 · Orquestacion del drain, governed-fetch & observabilidad

> **Grupo:** Transporte por tiers & pacing  ·  **Resuelve:** observabilidad de drain  ·  **Estado:** CERRABLE
>
> **Costura —** TRES solders ES [VERIFIED]: scrape_dealer clavado a autoscout24 (import :23), build_origin literal 'as24' (:45,53,71,85), data_root('ES') (:61). Y el hueco critico: harvest_dealer llama scrape_dealer(slug) DIRECTO (:43), NO por governed_fetch_text(governor.py:460) — el choke-point existe pero el orquestador lo bypassa.
>
> **Fix —** 1) Parametrizar fuente: (source_key, scrape_callable) del platform_roster del pack en vez del import AS24; build_origin usa source_key. 2) data_root(pack.country_code) no 'ES'. 3) Cablear scrape por governed_fetch_text(engine=...) para que cada drain pase el bucket del host (el sentido de la faceta 8).
>
> **Adversarial —** scrape_dealer pinneado AS24 + data_root('ES'): un drain de pais #2 mis-etiqueta todo fallo como 'as24'/ES. El raw dump (:61-65) FUGA si el delete no corre tras crash — el re-raise (:88) sale antes de limpiar (viola sample-verify-delete). Drain no-ES que bypassa governed_fetch(:43) martillea el host sin bucket -> ban clase-AS24.
>
> **Sellado —** Choke-point (instrumentar acquire: count==fetch count, todo fetch pasa el governor) + origen (fallo de pais #2 alerta con SU source_key+pais, no 'as24'/ES) + adversarial (matar proceso a mitad de drain -> no persiste crudo, delete-on-exit aun en re-raise). Sello: cada drain pasa el choke-point, fail-loud con origen exacto, cero crudo, generico por source.
>
> **Herramienta NEXT-LEVEL —** Procrastinate (MIT, EUR0) https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:67,555] — drains como tareas durables PG (claim idempotente, retry backoff, reanudacion tras crash; cierra el raw-leak); + Apprise (BSD-2, :86,707) alerta country-routed out-of-band; + Healthchecks (BSD-3, :68,563) dead-man externo.

#### (a) code_hints verificados
- [VERIFIED pipeline/harvest_dealer.py:29] `async def run(slug)` — orquestador E2E por-dealer SCRAPEAR->RECETA->INGEST->VERIFICAR (docstring :1).
- [VERIFIED harvest_dealer.py:23] `from pipeline.sources.autoscout24 import harvest_dealer as scrape_dealer` — scrape CLAVADO a AS24.
- [VERIFIED harvest_dealer.py:42-48] `try: scrape_dealer(slug)` -> en Exception: `fire_alert(build_origin("as24","scrape",slug), severity="error")` + return (outcome operacional ESPERADO, no crash; comentario :30-35 explica fire_alert per-dealer vs record_run source-level).
- [VERIFIED harvest_dealer.py:61] `raw_dir = data_root("ES", root=ROOT) / slug / "raw"` — dump crudo ES-hardcoded; [:63-65] escribe harvest.json (efimero, gitignored docstring :4-5).
- [VERIFIED harvest_dealer.py:83-88] except externo -> `fire_alert(build_origin("as24","harvest",slug))` + `raise` (re-raise un bug con origen exacto, nunca tragado).
- [VERIFIED pipeline/engine/governor.py:460] `governed_fetch_text(*, engine)` — el choke-point (wrap del governor process-wide).

#### (b) Mecanismo al atomo
El orquestador encadena las fases de inventario de un dealer: scrape (drena todas las paginas) -> receta (persiste) -> ingest+delta+VAM -> verdict. La semantica de fallo es de dos niveles y load-bearing: un fallo de SCRAPE es outcome operacional ESPERADO (sitio caido/bloqueado) -> `fire_alert` a granularidad per-dealer (NO `record_run`, que es source-level y tripearia falsamente el breaker de TODA la fuente, comentario :30-35) + skip; un error INESPERADO (un bug) -> `fire_alert` con origen exacto (source/fase/slug) y luego RE-RAISE para que aflore (:83-88). Cada alerta lleva `build_origin("as24", fase, slug)`. El harvest crudo se vuelca a data/ES/<slug>/raw (efimero, gitignored) y debe borrarse. El choke-point del governor (`governed_fetch_text`, :460) es el camino unico por el que TODO fetch debe pacearse.

#### (c) Costura ES->generico + fix exacto
TRES solders ES [VERIFIED]. (1) `scrape_dealer` clavado a autoscout24 (import :23) — el orquestador drena SOLO AS24; cada `build_origin` es literal "as24" (:45,:53,:71,:85). (2) `data_root("ES",...)` ES-literal (:61). (3) **El hueco CRITICO**: harvest_dealer.py llama `scrape_dealer(slug)` DIRECTAMENTE (:43) — NO rutea por `governed_fetch_text` (governor.py:460); el choke-point existe pero ESTE orquestador lo bypassa. **Fix:** (1) parametrizar la fuente — aceptar un `(source_key, scrape_callable)` del `platform_roster` del pack (faceta 14) en vez del import AS24; los tags `build_origin` pasan a ser el source_key. (2) `data_root(pack.country_code)` no "ES". (3) Cablear el scrape por `governed_fetch_text(engine=...)` para que cada drain sea paceado por el bucket del host (el sentido entero de la faceta 8) — hoy el pacing esta bypasseado para el drain del dealer.

#### (d) Riesgo adversarial concreto
[VERIFIED] `scrape_dealer` pinneado a AS24 + `data_root("ES")` -> un dealer-drain de pais #2 no puede enrutar su source/pais en la alerta (todo fallo se mis-etiqueta "as24"/ES). El raw dump (data/ES/<slug>/raw, :61-65) puede FUGAR si el delete no corre tras un crash — el path de re-raise (:88) sale antes de cualquier limpieza, dejando crudo en disco (viola el mandato sample-verify-delete del contrato de receta). DE/FR/IT/PT: un drain no-ES que bypassa `governed_fetch_text` (:43) martillea el host sin bucket per-host -> re-gana el ban clase-AS24. Ruido: un blip transitorio de red aflora como bug re-raised (:88) en vez de outcome retryable, porque el orquestador no tiene tier de retry propio (ese vive en fetch.py faceta 1, tambien bypasseado aqui).

#### (e) Sellado + verificacion multi-via
1. **Choke-point**: afirmar que TODO fetch de un drain pasa por el governor (instrumentar `acquire` y contar == fetch count).
2. **Origen**: un fallo de scrape de pais #2 produce una alerta etiquetada con SU source_key y pais, nunca "as24"/ES.
3. **Adversarial**: matar el proceso a mitad de drain y afirmar que no persiste crudo (delete-on-exit honrado aun en re-raise). Sello = "cada drain pasa el choke-point, falla loud con origen exacto, no deja crudo persistido, generico por source no AS24-only".

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Procrastinate** (MIT, EUR0) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:67,555 lic MIT]. Drains como TAREAS DURABLES sobre el Postgres existente: claim idempotente (FOR UPDATE SKIP LOCKED), retry backoff-exponencial por tipo, deferral, y un worker que reanuda a mitad de vuelo tras crash — modelando el drain como PENDING->CLAIMED->DONE con exactly-once gratis, de modo que un drain matado reanuda sin perder un dealer y un fallo transitorio de fuente reintenta con backoff en vez de quemar el breaker (cierra el hueco raw-leak-on-crash haciendo la unidad de trabajo reanudable). Empareja con **Apprise** (BSD-2-Clause, https://github.com/caronc/apprise [VERIFIED :86,707]) para fan-out de alerta country-routed fuera-de-banda (fire_alert hoy solo escribe una fila in-DB que nadie mira con el stack caido) y **Healthchecks** (BSD-3-Clause, https://github.com/healthchecks/healthchecks [VERIFIED :68,563]) como dead-man switch EXTERNO (un watchdog in-process no puede detectar su propia muerte de proceso). Alternativas: pgqueuer, DBOS Transact.

[↑ Indice de facetas](#indice-facetas)

---

<a id="f30"></a>
### Faceta 30 · Criterio de sellado country-aware & rollback atomico por pais

> **Grupo:** Verificacion cero-confianza & sello  ·  **Resuelve:** SH1 / SH5 / SH6 + G1 (complete.py:89)  ·  **Estado:** REWORK-SELLO
>
> **Costura —** Cuatro huecos: (1) decide_status sella sobre la cuenta sola sin assert pais/locale/geo/moneda [recipe_harness.py:94]; (2) country_of_cdp defaultea a ES ante codigo malformado -> mint-bug vuelca recetas DE en countries/ES/ [paths.py:62-63]; (3) R3 clobber solo log.warning, no bloquea [recipe.py:88-91]; (4) _CDP_CODE_RE hard-codea ^CDP-ES- rechazando entidades extranjeras [complete.py:89, xfail].
>
> **Fix —** (1) Extender el sello para asertar coherencia pais/locale/moneda/geo y country_of_cdp(receta)==pais-objetivo; (2) country_of_cdp fail-loud cuando target!=parseado en vez de default ES; (3) R3 clobber BLOQUEA cuando los paises difieren; (4) ensanchar _CDP_CODE_RE a ^CDP-([A-Z]{2})- y quitar el xfail; (5) unidad de rollback country-scoped que borra countries/<CC>/ + entrada de _pack.py atomico sin tocar motor ni ES.
>
> **Adversarial —** Sitio DE servido en es-ES parsea limpio -> VERIFIED de la vista equivocada; mint-bug vuelca recetas DE en countries/ES/ sin error ni deteccion; sin granularidad de revert por pais; clobber cross-country silent last-writer-wins (solo log); G1 _CDP_CODE_RE rechaza DE/FR/IT/PT hasta el widening; no-UE incoherencia currency/locale no detectada.
>
> **Sellado —** VERIFIED implica coherencia de pais Y pais revertible atomico (countries/<CC>/ + pack) sin tocar motor ni ES. Multi-via: (a) drain pack=DE con receta.country!=DE falla el sello; (b) editar country post-sello -> la cadena detecta el tamper y el clobber cross-country se BLOQUEA; (c) in-toto-verify re-deriva el sello desde el fixture sin confiar en el emisor.
>
> **Herramienta NEXT-LEVEL —** in-toto (Apache-2.0, EUR0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:312] recibo de procedencia firmado/hash-chained/tamper-evident reteniendo cero crudo; soporte DVC (content-addressed, build_run_id reconstruible -> rollback por-pais) [VERIFIED :148] y pandera (contrato de coherencia locale/geo/currency que falla CERRADO) [VERIFIED :164].

#### (a) Verificacion de code_hints [VERIFIED]
- `country_of_cdp`: `_CDP_COUNTRY_RE.match(cdp_code)` -> `group(1)` si matchea, si no `DEFAULT_COUNTRY` (`"ES"`) [VERIFIED pipeline/paths.py:55-63]; regex `_CDP_COUNTRY_RE = r"^CDP-([A-Z]{2})-"` [VERIFIED :30]. **Un codigo malformado / mint-bug defaultea a ES** -> vuelca recetas DE en `countries/ES/`.
- `write_recipe`: `out_dir = recipes_flat_dir(country_of_cdp(cdp_code), root=ROOT)` -> rutea por el pais derivado del codigo [VERIFIED pipeline/recipe.py:69]; **R2** round-trip self-check al ESCRIBIR (raise si no round-trip) [VERIFIED :76-79]; **R3 clobber**: si `path.exists()` y `old_recipe != recipe` -> **solo `log.warning`** (NO bloquea) [VERIFIED :83-91].
- `decide_status` comprueba SOLO `parse_loss`/empty/under-target/REFUTED — **sin assert de locale/geo/currency/pais** [VERIFIED pipeline/recipe_harness.py:94-117].
- `_CDP_CODE_RE = r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$"` — **aun hard-codea `CDP-ES-`** (el 6o blocker oculto) [VERIFIED pipeline/complete.py:89]; usado en `if not _CDP_CODE_RE.match(cdp_code)` [VERIFIED :145]; `_NATIONAL_KINDS` frozenset (sentinel nacional, `prov_str is None`) [VERIFIED :83]. El golden lo vigila con `xfail(strict)` documentando que G1 "silently reject every foreign-country entity" [VERIFIED tests/test_country_golden.py:278-291].

#### (b) El mecanismo al atomo
Esta faceta es el **meta-criterio sobre las facetas 16/17/18** (los 3 sellos ortogonales: consistencia, replay, VAM). Hoy VERIFIED significa solo `fetched==parsed` (integridad de cuenta, `decide_status`). El ruteo de pais es por `country_of_cdp(cdp_code)` parseando el segmento `CDP-XX-`, **defaulteando a ES ante basura**. El guard de clobber (R3) **solo LOGea**. El validador G1 (`_CDP_CODE_RE`) sigue ES-hardcodeado. No existe unidad de sello/rollback country-scoped.

#### (c) Costura ES->generico + fix exacto
Cuatro huecos load-bearing: **(1)** `decide_status` (recipe_harness.py:94) sella sobre la cuenta sola — sin assert de coherencia pais/locale/geo/moneda. **(2)** `country_of_cdp` (paths.py:62-63) defaultea un codigo malformado a ES -> un mint-bug de pais #2 vuelca recetas DE en `countries/ES/` **sin error**. **(3)** R3 clobber (recipe.py:88-91) solo `log.warning` -> un clobber cross-country no se bloquea. **(4)** `_CDP_CODE_RE` (complete.py:89) hard-codea `^CDP-ES-` -> rechaza toda entidad extranjera (el 6o blocker vigilado por xfail). **Fix exacto:** (1) extender el sello: `decide_status` (o un wrapper) debe ADEMAS asertar coherencia pais/locale/moneda/geo (el locale<->IP de la faceta 3, currency<->pack de la faceta 28, y `country_of_cdp(receta)==pais-objetivo-del-drain`); (2) `country_of_cdp` NO debe defaultear silenciosamente a ES para un drain cuyo pais-objetivo != pais parseado -> fail-loud; (3) R3 clobber debe **BLOQUEAR** cuando los paises difieren (no `log.warning`); (4) ensanchar `_CDP_CODE_RE` a `^CDP-([A-Z]{2})-` (quitar el xfail); (5) una **unidad de rollback country-scoped**: revertir "todas las recetas DE" atomico borrando `countries/<CC>/` + su entrada de `_pack.py`, sin tocar el motor ni ES.

#### (d) Riesgo adversarial concreto
- Un **sitio DE servido en es-ES** parsea limpio -> **VERIFIED de la vista equivocada** (decide_status no puede distinguirlo).
- Un **mint-bug vuelca recetas DE en `countries/ES/`** (country_of_cdp defaultea ES) y ni el sello ni el rollback lo detectan.
- **Sin granularidad de revert por pais**: no se puede deshacer atomico el pais #2 sin arriesgar ES.
- **Sin bloqueo de clobber cross-country**: dos paises escribiendo el mismo `cdp_code` (colision canonica, faceta 24) -> silent last-writer-wins con solo un log.
- **DE/FR/IT/PT:** G1 `_CDP_CODE_RE` rechaza todas sus entidades hasta el widening.
- **no-UE:** idem + incoherencia de currency/locale no detectada.
- **Ruido:** un `cdp_code` basura -> arbol ES (por diseno para legacy, pero enmascara mint-bugs reales).

#### (e) Criterio de sellado + verificacion multi-via
Sello = VERIFIED implica TAMBIEN coherencia de pais Y un pais es **revertible atomico** (`countries/<CC>/` + entrada de pack) sin tocar el motor ni ES. Multi-via: (a) test: un drain con pack=DE cuya `receta.country != 'DE'` falla el sello; `country_of_cdp` de un drain target-DE que produce un codigo ES falla loud. (b) adversarial: editar el `country` de una receta sellada post-sello -> la verificacion de la cadena **detecta la manipulacion**; un clobber cross-country se **BLOQUEA**, no se logea. (c) via independiente: `in-toto-verify` re-deriva el sello desde el fixture y confirma la procedencia **sin confiar en quien la emitio**.

#### (f) Herramienta que la eleva a nivel inalcanzable
**in-toto** (Apache-2.0, EUR0) — https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:312 "certifiable-recipe-provenance"]. Eleva sample-verify-delete de "borro el crudo" a un **recibo de procedencia firmado, hash-chained y tamper-evident** (quien/que/cuando + `parse_loss` + quorum VAM + hash del golden + firma de la huella antidetect) — cierra el sealing-hole "consistencia interna pero no certificable externamente" con cadena de custodia SLSA-grade, EUR0, reteniendo cero crudo (se firma el VEREDICTO + hashes, no el crudo). **Soporte:** DVC (Apache-2.0) [VERIFIED NEXT-LEVEL.md:148 "Versionado content-addressed de inputs del sello"] para un `build_run_id` reconstruible bit-a-bit -> el sustrato del rollback atomico por-pais; y **pandera** (MIT) [VERIFIED NEXT-LEVEL.md:164 "Contrato de datos PRE-sello"] como el contrato de coherencia (locale/geo/currency) que el sello debe anadir y que falla CERRADO.

[↑ Indice de facetas](#indice-facetas)

---

## Mejoras a nivel inalcanzable (€0, priorizadas)
Programa de Ola 3 — todas €0, ordenadas por ratio impacto/esfuerzo:

1. **[S] Preselección de tier por `defense_tier`.** Leer `entity.defense_tier` (`migrations/0016`) para arrancar en el engine más barato viable y **saltar probes Tier-0 inútiles** en hosts `t2+/t3` (ahorra latencia, reduce huella de ban). Hoy `fetch.py` siempre intenta Tier-0 y escala reactivo.
2. **[M] Herencia de receta cross-país.** El parser de una plataforma multi-país (AS24) se hereda `.es→.de` por **swap de dominio**, y el harness **auto-verifica** la herencia. Una sola definición de parser sirve N países (hoy el piloto DE fue manual).
3. **[M] Patchright (Apache-2.0) como Tier-1 por defecto** para WAFs Chrome-shaped, retirando la dependencia de `nodriver` (AGPL-3.0). Declarado como upgrade staged en `tier1/browser.py:30`. Superior contra WAFs forma-Chrome **y** elimina el riesgo legal AGPL sin coste.
4. **[M] Governor distribuido Redis GCRA.** El hook multi-proceso ya está documentado (`governor.py:26,220`) con API estable. Self-host Redis €0 permite cosechar desde N procesos/máquinas sin martillar un host (hoy el bucket es in-memory single-proceso).
5. **[L] Capa-2 IA-local: síntesis de `field_map` para webs JS-rendered.** Cuando `GenericWebExtractor` devuelve muestra vacía (recipe `FAILED`), un LLM local lee el DOM renderizado y emite `Parsing(engine='css', field_map=…)` — el rung `llm_local` declarado con 0 en código (`recipe_extract_web.py:9`). Es el cuello de la cola larga de dealers. Salida por gramática (ANTI-DRIFT §1).
6. **[L] Auto-reparación de receta por drift.** Cuando `RecipeRunner.replay` detecta `parse_loss>0` (la fuente cambió), regenerar el `field_map` desde muestra fresca vía LLM local, re-verificar con el harness y re-commitear. Cierra el lazo `sample-verify-delete → repair → re-verify`. Sin esto la frescura 24 h cae (~52 % según recon — punto-en-el-tiempo).
7. **[XL] Intérprete de receta dirigido por YAML puro.** Ejecutar el `Parsing` (incl. `css`/`llm_local`) SOLO desde el `field_map` del YAML, sin que el `Extractor` posea el código de parseo (hoy `recipe_harness.py:225` lo declina). El salto de "receta como config" a "receta como programa".

---

## Riesgos / open items
Estado crudo. Lo que NO está cerrado, con causa y gate:

- **OPEN/GASTO — egress residencial sticky por país.** El supuesto "sin-proxies" es frágil sobre IP datacenter: free proxies son efímeros/flaky (`free_proxies.py:9-11` lo admite) y la cookie Tier-1 se liga a la IP que la minó (`browser.py:7`). A volumen, la IP del host **se quema**; el residencial sticky es `PENDING-CREDENTIAL` (`browser.py:61`). Gap real de resiliencia. Gate: **GASTO** + firma owner.
- **OPEN/LEGAL — familia VAM `registral` fuera de ES (MP11).** `verify.py:48` (DGT/CNAE/BORME/FacoNauto) y `axesor_cnae.py` son **ES-only**. Sin equivalente (KBA/SIV/Motorizzazione/IMT) el sello **no alcanza quórum registral** fuera de ES → el intervalo 100 % no estrecha. Gate: disponibilidad de fuente + **LEGAL** (ToS/RGPD-equiv). Cross-ref Etapa 7.
- **OPEN — cross-border identity (B8/MP8).** La espina dorsal: `canonical_key` country-blind colapsa entidades pan-EU multi-market. Requiere decisión de identidad (market entra en la clave **o** POS-por-país) **antes** de reapuntar gateways `toyota-europe`/`nissanpace`/`ayvens`/`codeweavers` a DE/IT. Cross-ref Etapa 4.
- **OPEN — transliteración / mass-dedup (B5/MP6).** `_normalize` descarta no-ASCII → false-merge JP y divergencia DE `ß`. `pack.normalize_policy` country-scoped lo cierra **sin** re-keyar ES; gate: golden verde. Cross-ref Etapa 4.
- **DEUDA — cobertura del sello recipe-first parcial.** Solo **5/42** conectores implementan el protocolo `Extractor` del harness (`recipe_extractors.py:280`): `sample-verify-delete` + replay + VAM cubren 5 fuentes; los ~37 `wholesale` restantes drenan con lógica propia **sin** la garantía recipe-first. La cobertura del sello es parcial.
- **RIESGO — 31 conectores hardcodean `CDP-ES-`** (costura #1): país #2 mintaría códigos ES para sus plataformas → corrupción de identidad silenciosa hasta cablear `mint_code`. El path por-dealer es seguro; el de plataforma **NO**.
- **RIESGO — firmas WAF estáticas sin telemetría de drift.** `ban_detector.py` es lista estática: cuando un vendor rota su interstitial, un challenge se clasifica `OK` en silencio y se sirve basura como inventario. Mitiga: mejora #6 (auto-reparación) + telemetría de drift de firmas.
- **RIESGO — `nodriver` es AGPL-3.0** (copyleft de red): si se cablea por defecto o dentro del servicio API público puede forzar divulgación de fuente. Mitigado HOY (`camoufox` MPL-2.0 default, nodriver solo opt-in con caja de licencia en `browser.py:19-26`), pero las 14 recetas `_tier1` podrían referenciarlo — **auditar antes de exponer API**. Cierra con mejora #3 (Patchright Apache-2.0).
- **RIESGO — `_HOST_RATE_CLASSES` de mantenimiento manual.** Un host ausente hereda `STEALTH` (dirección segura), pero un `JSON_API` ausente corre **17× lento** (el bug real milanuncios, `governor.py:144-147`). El onboarding **debe** poblar la tabla o estrangula la cosecha (paso 10).
- **RIESGO — receta runtime Tier-1 fuera del esquema.** `milanuncios_camoufox.py` vive como script suelto fuera de `Recipe v2` y del harness: no pasa `sample-verify-delete` ni replay, escribe a archivo local (`json.dump`, `:37`) → **viola** `sample-verify-delete`. Parche por-plataforma no generalizado.

> **Cierre honesto (00-MASTER §"antes confesar un hueco que vender una mentira"):** el motor de scrape es genérico **en mecanismo** y reversible **en su totalidad** (aditivo, default ES, rollback por `git revert`). Pero `holds=false` es correcto: 11 roturas, 11 packs ausentes y 6 agujeros de sellado están **VERIFICADOS en código**. De ellos, **la mayoría son cerrables** por inyección de pack + el `CountryScrapePack` enriquecido; **4 son OPEN ITEM** con causa y gate declarados (residencial/GASTO, registral/LEGAL, cross-border/identidad, transliteración/identidad) y **2 exigen rework de la definición de sello** (SH3 ortogonalidad débil, SH5 default-ES peligroso). El motor **NO es genérico aún por debajo del esquema** — esta etapa es la hoja de ruta que lo cierra.
