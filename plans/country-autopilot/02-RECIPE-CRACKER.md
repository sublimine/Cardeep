# 02 — RECIPE-CRACKER autónomo (diseño)
> Owner 2026-06-28 (CENTRAL, no marginal): un equipo/harness que para CADA objetivo (dealer/plataforma)
> prueba TODAS las alternativas de scraping coherentemente (escalera) hasta VERIFICAR, y guarda la
> **receta ganadora + delta** (sample-verify-delete + VAM, cero crudo). Síntesis del recon `a33d79bd`.
> Construye SOBRE lo existente — NO reinventa.

## La ESCALERA (barata→cara) [recon, anclada al enum `recipe_schema.Parsing.engine`]
| # | transporte + parse | engine | herramienta €0 | estado |
|---|---|---|---|---|
| 0 | curl_cffi + JSON/GraphQL API interna | `json_api` | curl_cffi | ✅ existe |
| 1 | curl_cffi + `__NEXT_DATA__`/SSR | `next_data` | curl_cffi+selectolax | ✅ existe |
| 2 | curl_cffi + JSON-LD/microdata | `jsonld` | **extruct** | ⚠ regex propio; extruct no instalado |
| 3 | curl_cffi + sitemap-walk + SSR cards | (css slot) | **dealerprobe** classifiers | ⚠ existe en connector, no como rung |
| 4 | curl_cffi + CSS-selector adaptativo | `css` | **scrapling** | ❌ NO construido |
| 5 | stealth browser (render-to-unlock) | `browser` | **patchright**(vía scrapling)→**camoufox** | ⚠ codificado, dep comentada |
| 6 | browser CDP puro | `browser` | **nodriver/zendriver** | ⚠ codificado opt-in (AGPL), no instalado |
| 7 | browser + LLM-selector local | `llm_local` | **crawl4ai + Ollama** | ❌ NO construido |
| 8 | Tier-2 heavy (sensor-gen + residential) | — | Hyper/Decodo/2Captcha | ❌ **cruza puerta €>0** |

## El ORQUESTADOR (el núcleo ausente)
`crack_recipe(target, *, fetch_fn, ladder) -> CrackResult`: recorre la escalera de barata→cara; por rung
`sample = rung.extract(target, fetch_fn)`; si `decide_status(sample)==VERIFIED` (cero parse-loss ∧ coches≥target ∧ VAM no-REFUTED) → **persiste la receta con el rung ganador grabado** + break; si ninguno → FAILED **con razón por rung** (qué probó, por qué falló cada uno — sin fallo silencioso). REUSA `RecipeHarness.decide_status` + `record_count_verdict` (VAM) + el protocolo `Extractor` tal cual. `fetch_fn` INYECTABLE → fixtures en test, fetch real en runtime (egress-gated).

## Piezas nuevas a construir (€0, dry-run/fixtures)
1. **Orquestador try-all** + **ranking feedback** (§9.4): graba el rung ganador en la receta → próximo run warm-starts en ese peldaño.
2. **Rung `css`** (4): extractor CSS-selector adaptativo (auto-deriva selectores listing/PDP), scrapling-style.
3. **Rung `llm_local`** (7): extractor LLM-selector (infiere field-map de HTML arbitrario). FRAMEWORK mockable (reviewer_fn/llm_fn inyectable) → real = Ollama €0 local / Gemini-flash en runtime.
4. **Investigación/integración de herramientas**: registro extensible de rungs (`RUNG_REGISTRY`) — añadir una herramienta nueva = registrar un `Extractor`, sin tocar el orquestador.
5. **Recipe→delta tie**: puente harness→ingest→delta (hoy paths separados).

## Las PUERTAS (PENDIENTE-OWNER, aparcan no detienen) [gates.py]
- **EGRESS** (fetch real contra un target vivo) · **LEGAL/ToS** (scrape de país real) · **GASTO €>0** (GPU/LLM de pago, proxies residenciales, solvers = rung 8) · **PROD** (:5433).
- **Provisión de deps** (camoufox/scrapling/patchright/nodriver, comentadas en `requirements.txt:35-37`) = decisión owner (instalar). El código Tier-1 ya existe (`engine/tier1/browser.py`).
- ⇒ El orquestador + los rungs se **construyen y verifican contra FIXTURES sintéticos** (HTML/JSON de prueba) hasta las puertas; "arrancar fetch real contra país vivo" es estructuralmente del owner (doctrina frontera honesta).

## Build order
**(A)** orquestador try-all + ranking + RUNG_REGISTRY · **(B)** rung css · **(C)** rung llm_local (framework) · **(D)** recipe→delta tie · **(E)** provisión deps + extruct (owner-gated install).
