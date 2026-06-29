# CARDEEP — CAMINO AL 13/10
> Programa institucional derivado de un panel adversarial de 7 lentes (2026-06-29).
> Mandato owner: "Quiero el puto 13/10". Doctrina: €0, gana el código, causa raíz, :5433 intocable, gates PENDIENTE-OWNER no detienen.

## QUÉ ES "13/10" (la barra medible, no un número)
Casi todo lo que el proyecto presume vive en estado **sintético / dry-run / manual / apagado / dormante**.
El 13/10 = convertir cada uno en **real / vivo / automático / mecánico**, medible:
1. País #2 REAL E2E servido en vivo (no el run_campaign sintético "XX" que hace rollback).
2. Cobertura reproducible por un TERCERO desde un snapshot, R encendido por defecto.
3. ES corriendo ≥14 días 100% desatendido con cosecha fresca continua + country-proof chequeado vs :5433 cada tick.
4. vam_verified mecanizado (trigger, no script humano).
5. Producto que lo prueba en vivo (web consumiendo la API viva).
> Verdad incómoda: >80% nacional certificado NO es alcanzable a €0 para compraventa (sin ancla, cola mono-canal).
> El 13/10 de cobertura = banda-por-segmento triangulada + `dvc repro` byte-idéntico. Vender el 80% sería fallar.

## NOTA HONESTA DE PARTIDA: ~7,5/10 (el panel rebajó el 8,5 con evidencia file:line)
Lo top-decil real (confirmado): append-only triggers, hash-chain tamper-evident, COMPLETED 5-gates, honestidad de seal.py.
Lo sobre-vendido (refutado): "invariantes mecánicos VAM" — vam_verified es BOOLEAN MANUAL sin trigger; country-proof es VISTA detectora inerte en :5433; ops sin backups/entrega-de-alertas; cobertura 37,72% = muñón identificable, no España.

---

## LOS 6 TIERS (cada movimiento: qué · herramienta+licencia €0 · seam · criterio verificable · esfuerzo · riesgo)

### TIER 0 — DETENER LA HEMORRAGIA (hoy, bloqueante, frontend puro, reversible)
- **T0.1** Desactivar la bomba RIVR (landing de otro producto DeFi con 5 cifras fabricadas) → landing CARDEEP que lee /stats vivo o muestra '—'. S, nulo.
- **T0.2** Endurecer guardrail test_web_no_fabricated_data.py a la CLASE (strings-métrica $2.4B/8.5%/140K+ + vocabulario fuera de dominio). S, nulo.
- **T0.3** Higiene: purgar countries/ES/recipes/{r1,r3,llm_local}__d.yaml + .pyc huérfanos test_country2_* + gate CI. XS.

### TIER 1 — MECANIZAR LO MANUAL (sube el eje sobre-vendido a real)
- **T1.1** Mecanizar vam_verified: trigger que prohíba TRUE sin verdict TRUSTWORTHY quorum_n>=2 (clonar 0036). Resolver 989 grandfathered. VALIDATE el CHECK. M, medio. [requiere DB]
- **T1.2** Cinturón country-proof mecánico uniforme: country_set en cross_source_dedup + constraint DB en clusters. S-M. [requiere DB]
- **T1.3** Property-based testing (Hypothesis MPL-2.0): de goldens-ejemplo a propiedades (∀ aristas→clusters monopaís; dedup idempotente; cdp_pair inyectivo; state machine legal). M, bajo. [PURO]

### TIER 2 — ENCENDER LO APAGADO (€0, ya instalado/codificado)
- **T2.1** CIF/NIF como arista dura de dedup (señal más fuerte, cargada y SIN USAR; exact-match, no sobre-mergea). S-M, bajo. PALANCA MÁXIMA dedup. [requiere DB]
- **T2.2** Splink en el build (codificado, deps no declaradas → fallback silencioso). Declarar deps, --unit splink default tras auditar precisión ≥0,95. Bajo, medio. [requiere DB]
- **T2.3** Activar R §2.3 (r_crosscheck=True; R-portable YA instalado) + Chao puro-Python + LCMCR/dga. Trivial+bajo. [parcial-PURO]
- **T2.4** Estimador jerárquico (partial pooling) para los estratos sparse. Alto, medio-alto. [requiere DB+R]

### TIER 3 — HACERLO CORRER SOLO 24/7 (la dimensión más débil, €0)
- **T3.1** Backups + restore probado (pg_dump timer + WAL/PITR). PALANCA #1 ops. M, bajo. [requiere DB]
- **T3.2** Supervisores VIVOS (NSSM/systemd) + dead-man's-switch externo (lee scheduler_lease). S+S. [owner instala]
- **T3.3** Cablear ENTREGA de alertas (ntfy Apache-2.0 / Apprise BSD-2 / Telegram €0) desde fire_alert. S, bajo.
- **T3.4** Fix lock-loss en PG restart (re-acquire en caliente o SystemExit). S-M, medio.
- **T3.5** Observabilidad: /metrics Prometheus (prometheus-client) + structlog + SLOs. M, bajo.

### TIER 4 — BLINDAR EL CRACKER Y DISPARARLO VIVO (santo grial del scope)
- **T4.1** ✅ HECHO — try/except por rung (un FetchError vivo ya no aborta el ladder). XS. [PURO]
- **T4.2** Auto-discovery de API interna como rung 0 (XHR/__NEXT_DATA__/GraphQL; mitmproxy2swagger MIT). M, bajo-medio.
- **T4.3** VAM real del cracker (oráculo independiente, no fetched==parsed). M, bajo. [parcial-PURO]
- **T4.4** Encender rung LLM local + GBNF (Ollama qwen2.5 + llama.cpp/outlines/xgrammar). M, bajo. [owner: daemon]
- **T4.5** Cerrar loop crack→verify→delta→re-rank vivo (dry_run=False tras crack, :5434 primero). S, medio. [requiere DB]
- **T4.6** Egress residencial = ÚNICO gate NO-€0 → PENDIENTE-OWNER. Captcha: evitar (camoufox+humanize).

### TIER 5 — EL PRODUCTO QUE LO PRUEBA (frontend conectado al censo vivo)
- **T5.1** Resucitar cardeep.ts como capa de datos (ya tipa los 18 endpoints). S.
- **T5.2** Cobertura honesta visualizada (Observable Plot ISC; suelo coverage_lower, GAP en rojo). S-M.
- **T5.3** Mapa coroplético vivo (MapLibre BSD-3 + deck.gl MIT; NO three.js muerto). M-L.
- **T5.4** Ficha dealer/coche + delta en vivo. M.
- **T5.5** Buscador instantáneo (Meilisearch MIT) sobre servable_vehicle. REQUIERE /search nuevo. L, alto. [requiere DB]
- **T5.6** Clasificador kind (dejar de hardcodear "compraventa"; cierra classifier_drift STUB). M.

### TIER 6 — EL TECHO (demostrar, no afirmar)
- **T6.1** País #2 REAL E2E vivo (sellar 5 acoplamientos ES: ingest.py:49, geo default, phone_es...). [requiere DB+datos]
- **T6.2** Reproducibilidad por terceros (DVC + Great Expectations + OpenLineage, OSS €0).
- **T6.3** Reformular cobertura a banda-por-segmento (desguace anclado / venta registral / compraventa banda).
- **T6.4** Spec formal (TLA+/Alloy) del state machine + no-cross-merge. 14/10.

## SECUENCIA
T0 → T1.1+T1.2+T1.3 → T2.1+T2.2+T2.3 → T3.1+T3.2+T3.3 → T4.* → T5.1+T5.2 → T6.
Con T0-T3 el artefacto pasa de ~7,5 a ~9,5 honesto; T4-T6 = fuera de escala.

## ANTI-HUMO (victorias falsas a rechazar)
Ver scratchpad/cardeep-CAMINO-AL-13-2026-06-29.md §ANTI-HUMO MAESTRO. Resumen: no commitear RIVR; "N tests más" ≠ verdad;
"CI verde" excluye suite censo; "SEALED sintético" no es onboarding; "vam_verified=TRUE manual" no es invariante;
">80% cobertura" = humo sin ancla; "pHash implementado" sin deps en requirements = código muerto.
