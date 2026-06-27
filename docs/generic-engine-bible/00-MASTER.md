# CARDEEP — BIBLIA DEL MOTOR GENÉRICO DE COBERTURA DE PAÍS
> Carta de campaña · Director Soberano (CEO-orquestador) · 2026-06-27 · estado: EN CONSTRUCCIÓN (Ola 1 lanzada)

## Norte
No "cubrir España". Construir un **motor genérico de cobertura de país** donde España es la **primera ejecución** (el banco de pruebas que lo endurece), no el producto. País nuevo = **otra ejecución**, no un rewrite. Scope = **huella DIGITAL** del 100% de los puntos de venta (sin web ≠ inventario). Coste **€0** de cimiento.

## Decisiones bloqueadas (CEO — no se re-litigan sin instrucción)
1. **Extracción in-place**, NO greenfield. El motor genérico se forja endureciendo el sistema 8/10 probado (la `0052/0053` + piloto DE byte-idéntico ya demostraron que el esquema es paramétrico por país). Tirar 2,3M de coches + el MSE probado está descartado.
2. **€0 de cimiento.** GPU / IA-local = palanca que se activa solo con caso de uso PROBADO + firma del owner. El motor no nace dependiendo de la cartera.
3. **Geo por adaptadores** sobre el esquema `(country_code, code)` existente. España sigue con INE; cada país entra con su árbol administrativo sin reescribir lo probado.

## Modelo de ejecución (3 capas — "IA local ejecuta, Claude orquesta siempre")
- **Capa 1 — Músculo determinista (24/7, autónomo):** schedulers, conectores, delta, MSE, eviction. Corre sin nadie. ≈ coste servidor.
- **Capa 2 — IA local (obrera barata):** solo el subconjunto irreducible (campos sucios, clasificación ambigua). Salida forzada por gramática. La llama el músculo; no decide nada estratégico. HOY = 0 en código; se enciende donde se demuestre que el determinismo falla.
- **Capa 3 — Claude (cerebro permanente):** el ÚNICO decididor/orquestador. Caza recetas Tier-1, resuelve ambigüedades, dirige campañas por país vía workflows, decide arquitectura. Actúa en ráfagas (programadas o disparadas por la cola de decisiones), no dentro del bucle caliente.

## Doctrina de onboarding (mandato owner 2026-06-27)
- **España se preserva.** Tomar lo que funciona y está **VERIFICADO** → generalizar → luego mejorar. Cero pérdida de lo construido.
- **Genérico ≠ uniforme.** El **motor** (maquinaria: union-find, MSE, delta, API, schedulers, y el propio proceso `cover(CC)`) es invariante. Pero al desplegar un país, **TODAS las etapas quedan personalizadas exclusivamente al 100% a ese país** — el pack es **PROFUNDO y a medida**, no config fina.
- **Conocer el país ANTES de proceder.** `cover(CC)` arranca SIEMPRE con una fase de **inteligencia de país/mercado** (orquestada por Claude): árbol administrativo, estructura del mercado de venta de coches (qué plataformas/marketplaces/portales OEM/asociaciones/registros dominan), marco legal (RGPD-equivalente, ToS), idioma(s), fuentes de denominador, formatos de teléfono/dirección/moneda. De esa inteligencia se **DERIVA** el pack 100%-personalizado de las 9 etapas; solo entonces se ejecuta.
- **Estados `cover(CC)`:** `REGISTERED → KNOW_COUNTRY (inteligencia de mercado) → BOOTSTRAPPED (pack derivado) → IN_COVERAGE → SEALED`. La genericidad vive en la maquinaria y en el método de investigar-y-personalizar cualquier país.

## Las 10 etapas (motor invariante vs pack por país)
| # | Etapa | Motor (invariante) | Pack (por país) |
|---|---|---|---|
| 1 | Descubrir | Framework de adaptadores + contrato DiscoveredEntity + mint cdp + cuórum VAM + MSE | Qué adaptadores/fuentes aplican (registro mercantil, mapas, dorks) |
| 2 | Scrapear | Motor por tiers + anti-detección + recetas v2 + harness | Roster de plataformas + recetas |
| 3 | Extraer/Normalizar | Selectores deterministas + (enganche IA local) | Locale (precio/fecha/idioma) |
| 4 | Identidad | Union-find B1 + cadena dedup + red anti-over-merge | Autoridad de teléfono/dirección |
| 5 | Vehículo | Resolver det-v1 + delta 5 tipos + pHash | ~nada (universal) |
| 6 | Geo | Cascada de resolución + esquema (country_code,code) | El árbol administrativo + centroides + alias |
| 7 | Calidad/Sello | Motor MSE + sellos + definición punto-venta | Ancla externa (censo/registro) + listas ortogonales |
| 8 | Servir | FastAPI + envelope + auth + cache + delta | ~nada (país = dimensión) |
| 9 | Orquestar/Observar | Scheduler + locks + health + breaker + lease | REGISTRY de fuentes |
| 10 | Cerebro/Automatización | Bus de decisiones + cover(CC) state machine + orquestación Claude | — |

## Invariantes (la "física" del motor — no negociables)
cdp_code = `CDP-{CC}-…` (paramétrico) · VAM = cero confianza (ningún número sin quórum ≥2 vías ortogonales, impuesto por triggers DB) · append-only + 5-gates COMPLETED · sample-verify-delete (la receta es el activo, el crudo se evicta con tombstone) · main = única verdad · dry-run(:5434)→golden→Ferrari→CI antes de tocar lo servido · "antes confesar un hueco que vender una mentira" · **BLINDAJE** anti-alucinación + anti-desvío + contexto total → `ANTI-DRIFT-HARDENING.md` (nada se inventa, nada se sale de vía, todo sabe qué hacer con contexto total; prohibido adivinar — la duda escala, no improvisa).

## Gates PENDING-OWNER (nunca paran el loop)
GASTO (€>0) · ESCRITURA EN PROD/serving-of-record · LEGAL (RGPD/ToS). Prohibido declarar 100% con residual gateado abierto.

## Operación (mandato owner 2026-06-27)
- **Cada punto = proyecto paralelo.** Cada etapa/sub-punto se exprime al máximo como proyecto independiente, en paralelo, orquestado — máximo jugo, inteligentemente.
- **Autoridad total para conseguir herramientas.** Ante cualquier dificultad: buscar, investigar y **auditar repos / GitHub / foros / plataformas sociales** para extraer info o herramientas battle-tested que el proyecto necesite (reuse > reinventar). **No se acepta un "no"** mientras quede una vía sin probar.
- **Desconfianza total — verificación multi-vía = única fuente de confianza.** Ningún resultado, número o afirmación se da por bueno sin **≥2 vías independientes y ortogonales**; verificación adversarial co-igual; nada se declara hecho sin estar **PROBADO y FUNCIONAL**.
- **Funnel impecable.** Entrada única (`README.md`): cualquier IA o persona ve el funnel —de "cubrir un país" a "sellado"— sin perderse. Carpetas y nombres con lógica total; cero artefacto huérfano.

## Estructura de la biblia
- `00-MASTER.md` (este) — carta de campaña + invariantes.
- `stages/01-discover.md` … `10-automation.md` — una etapa por archivo: revisión átomo (lo que existe, verificado) → motor vs pack → diseño genérico → pasos de onboarding → criterio de sellado+verificación+rollback → mejoras "nivel inalcanzable".
- `COUNTRY-PACK-CONTRACT.md` — el contrato consolidado: las 8 cosas que un país debe aportar.
- `COVER-NEW-COUNTRY.md` — la biblia operativa: campaña end-to-end `cover(country_code)`.
- `NEXT-LEVEL.md` — el programa de mejora a nivel inalcanzable.

## Capa LLM — enrutado por tarea (mandato owner 2026-06-27)
Maximizar cobertura LLM **solo donde sube calidad O eficiencia**; lo determinista se queda donde ya gana (hashing, dedup exacto, geo exacto). Para cada sub-punto LLM-amenable del motor: **el modelo exacto** que lo lleva (investigado, el mejor de cada cosa), su **recorrido A→Z** (input→modelo→salida→verificación→commit), su **guardrail de calidad** (decodificación por gramática + 2ª vía de verificación + fallback a determinista/Claude — nunca se pierde calidad), su perfil de **eficiencia/coste**, y **cuándo escala a Claude** (capa-3). Reglas: open-weight local-first **€0** preferente; modelo capaz al problema correcto; el GPU (que da el local-LLM masivo) es la **palanca €>0** que se activa con caso de uso probado + firma. **Auto-despliegue:** la campaña `cover(country_code)` instala la config de enrutado (modelos+endpoints+gramáticas+prompts por tarea) como parte del bootstrap del país. Entregable: `LLM-ROUTING-MATRIX.md`.

## Cadencia de campaña
- **Ola 1 (lanzada):** revisión átomo de las 10 etapas → diseño genérico + capítulo de biblia, cada una con pasada adversarial (DE/FR/IT/PT/no-UE). Verificación co-igual: nada se da por bueno sin romperlo primero.
- **Ola 1.5 (lanzada, paralela):** investigación del mejor modelo por categoría de tarea LLM → matriz de asignación + recorrido A→Z por modelo + guardrail de calidad + auto-despliegue por país.
- **Ola 2:** síntesis → contrato de country-pack + biblia `cover(CC)` + matriz LLM + invariantes consolidados.
- **Ola 3:** mejora a nivel inalcanzable (adversarial + visionario, €0, priorizado).
